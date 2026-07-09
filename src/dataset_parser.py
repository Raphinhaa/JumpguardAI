"""The sole raw-MATLAB-to-domain-object parser for JumpGuard AI."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd

from .dataset import Dataset
from .participant import Participant
from .schema import (
    DJ_ENTRY_COUNT,
    JOINT_ANGLE_COUNT,
    NONFATIGUED_TRIAL_COUNT,
    TRIALS_PER_PARTICIPANT,
)
from .trial import Trial


TRIAL_NAMES = ("DJ_t1", "DJ_t2", "DJ_t3", "f_DJ_t1", "f_DJ_t2", "f_DJ_t3")
EVENT_FIELDS = ("IC_first_K", "IC_second_K", "IC_first_A", "IC_second_A")


class DatasetParseError(ValueError):
    """Raised when source files do not match the documented hierarchy."""


@dataclass(frozen=True)
class RawArraySummary:
    """Description of one value encountered during raw source inspection.

    Args:
        path: Dot/index path from the inspected root.
        type_name: Python runtime type name.
        shape: Array shape when available.
        dtype: Array dtype when available.
        ndim: Dimension count when available.
    """

    path: str
    type_name: str
    shape: tuple[int, ...] | None
    dtype: str | None
    ndim: int | None


def summarize_raw_structure(
    obj: Any,
    name: str = "root",
    max_depth: int = 5,
    max_object_items: int = 300,
    _depth: int = 0,
) -> list[RawArraySummary]:
    """Recursively summarize a raw MATLAB source structure.

    This function lives in the parser so no other module needs knowledge of
    SciPy's MATLAB ``mat_struct`` representation.

    Args:
        obj: Raw value to inspect.
        name: Root path shown in summaries.
        max_depth: Maximum recursive depth.
        max_object_items: Largest object container expanded element by element.
        _depth: Internal recursion depth.

    Returns:
        Ordered summaries for the root and every expanded descendant.

    Examples:
        >>> summaries = summarize_raw_structure({"value": np.zeros((2, 3))})
        >>> summaries[-1].shape
        (2, 3)
    """
    type_name = type(obj).__name__
    shape = tuple(obj.shape) if hasattr(obj, "shape") else None
    dtype = str(obj.dtype) if hasattr(obj, "dtype") else None
    ndim = int(obj.ndim) if hasattr(obj, "ndim") else None
    summaries = [RawArraySummary(name, type_name, shape, dtype, ndim)]
    if _depth >= max_depth:
        return summaries
    children: Iterable[tuple[str, Any]] = ()
    if isinstance(obj, dict):
        children = ((f".{key}", value) for key, value in obj.items())
    elif hasattr(obj, "_fieldnames"):
        children = (
            (f".{field}", getattr(obj, field))
            for field in obj._fieldnames
        )
    elif isinstance(obj, np.ndarray) and obj.dtype == object and obj.size <= max_object_items:
        children = ((str(index), value) for index, value in np.ndenumerate(obj))
    elif isinstance(obj, (list, tuple)) and len(obj) <= max_object_items:
        children = ((f"[{index}]", value) for index, value in enumerate(obj))
    for suffix, value in children:
        summaries.extend(
            summarize_raw_structure(
                value,
                f"{name}{suffix}",
                max_depth,
                max_object_items,
                _depth + 1,
            )
        )
    return summaries


def parse_dataset(
    raw_data: Mapping[str, Any],
    label_workbook: Mapping[str, pd.DataFrame],
    metadata_workbook: Mapping[str, pd.DataFrame],
    *,
    source_path: str | Path,
    source_info: Mapping[str, Any] | None = None,
) -> Dataset:
    """Parse raw MATLAB and workbook structures into clean domain objects.

    Args:
        raw_data: Result from ``load_mat_dataset``.
        label_workbook: Every sheet from the IK-label workbook.
        metadata_workbook: Every sheet from ``labeling_DJ.xlsx``.
        source_path: MAT-file path recorded as provenance.
        source_info: Additional loader provenance.

    Returns:
        A Dataset containing no raw MATLAB structs.

    Raises:
        DatasetParseError: If required variables, labels, or metadata are absent.

    Examples:
        >>> dataset = parse_dataset(raw, labels, metadata, source_path="DJ.mat")
        >>> dataset.joint_angle_labels[0]
        'time'
    """
    if "DJ" not in raw_data:
        raise DatasetParseError("DJ.mat does not contain the required top-level variable 'DJ'.")
    labels, label_sheet = _parse_joint_angle_labels(label_workbook)
    metadata_frame = _first_sheet(metadata_workbook, "labeling metadata")
    columns = _metadata_columns(metadata_frame)
    participant_ids = sorted(int(value) for value in metadata_frame[columns["subject"]].unique())
    dj = raw_data["DJ"]
    expected_dj_shape = (DJ_ENTRY_COUNT, 1)
    if not isinstance(dj, np.ndarray) or dj.shape != expected_dj_shape:
        raise DatasetParseError(
            f"Expected raw DJ array shape {expected_dj_shape}, "
            f"found {getattr(dj, 'shape', None)}. "
            "Re-run dataset inspection before changing parser assumptions."
        )

    participants: dict[int, Participant] = {}
    for participant_id in participant_ids:
        rows = metadata_frame[metadata_frame[columns["subject"]] == participant_id].reset_index(
            drop=True
        )
        if len(rows) != TRIALS_PER_PARTICIPANT:
            raise DatasetParseError(
                f"Participant {participant_id} has {len(rows)} metadata rows; "
                f"expected {TRIALS_PER_PARTICIPANT}."
            )
        participant_columns = (
            columns["jump"],
            columns["group"],
            columns["gender"],
            columns["leg_dominance"],
            columns["fatigued_leg"],
            columns["acl_injured_leg"],
        )
        inconsistent = [
            column for column in participant_columns if rows[column].nunique(dropna=False) != 1
        ]
        if inconsistent:
            raise DatasetParseError(
                f"Participant {participant_id} has inconsistent participant metadata "
                f"across trial rows: {inconsistent}."
            )
        raw_entry = _unwrap(dj[participant_id - 1, 0])
        raw_trials = None if _is_empty(raw_entry) else _participant_trials(raw_entry)
        trials = tuple(
            _parse_trial(
                participant_id,
                slot,
                None if raw_trials is None else raw_trials[slot - 1, 0],
                labels,
                rows.iloc[slot - 1],
                columns,
            )
            for slot in range(1, TRIALS_PER_PARTICIPANT + 1)
        )
        participant_metadata = {
            key: _python_scalar(rows.iloc[0][column])
            for key, column in columns.items()
            if key not in {"missing", "notes", "condition"}
        }
        participants[participant_id] = Participant(
            participant_id=participant_id,
            trials=trials,
            metadata=participant_metadata,
        )

    return Dataset(
        participants=participants,
        joint_angle_labels=labels,
        source_path=Path(source_path).resolve(),
        metadata={
            **dict(source_info or {}),
            "label_sheet": label_sheet,
            "label_range": "A12:AR12",
            "metadata_rows": len(metadata_frame),
        },
    )


def _parse_joint_angle_labels(
    workbook: Mapping[str, pd.DataFrame],
) -> tuple[tuple[str, ...], str]:
    candidates: list[tuple[str, tuple[str, ...]]] = []
    for sheet_name, frame in workbook.items():
        values = frame.to_numpy()
        for row_index, row in enumerate(values):
            labels = tuple(str(value).strip() for value in row if pd.notna(value))
            if len(labels) == JOINT_ANGLE_COUNT and labels[0] == "time":
                preceding = values[row_index - 1] if row_index else ()
                indices = [int(value) for value in preceding if pd.notna(value)]
                if indices == list(range(1, JOINT_ANGLE_COUNT + 1)):
                    candidates.append((sheet_name, labels))
    if len(candidates) != 1:
        raise DatasetParseError(
            f"Expected one authoritative {JOINT_ANGLE_COUNT}-label row preceded by "
            f"indices 1-{JOINT_ANGLE_COUNT}; "
            f"found {len(candidates)} candidates."
        )
    sheet_name, labels = candidates[0]
    return labels, sheet_name


def _first_sheet(workbook: Mapping[str, pd.DataFrame], description: str) -> pd.DataFrame:
    if len(workbook) != 1:
        raise DatasetParseError(
            f"Expected exactly one worksheet for {description}; found {list(workbook)}."
        )
    return next(iter(workbook.values()))


def _metadata_columns(frame: pd.DataFrame) -> dict[str, str]:
    normalized = {str(column).strip(): str(column) for column in frame.columns}

    def _match(prefix: str) -> str:
        matches = [original for clean, original in normalized.items() if clean.startswith(prefix)]
        if len(matches) != 1:
            raise DatasetParseError(
                f"Expected one metadata column beginning {prefix!r}; found {matches}."
            )
        return matches[0]

    return {
        "jump": _match("jump"),
        "subject": _match("sub"),
        "group": _match("group"),
        "gender": _match("gender"),
        "condition": _match("trial"),
        "leg_dominance": _match("Leg dominance"),
        "fatigued_leg": _match("Fatigued leg"),
        "acl_injured_leg": _match("ACL injured leg"),
        "missing": _match("Missing data"),
        "notes": _match("notes"),
    }


def _participant_trials(raw_entry: Any) -> np.ndarray:
    entry = _unwrap(raw_entry)
    if not hasattr(entry, "DJ_bil"):
        raise DatasetParseError("Populated participant entry has no DJ_bil field.")
    bilateral = _unwrap(entry.DJ_bil)
    if not hasattr(bilateral, "sub_data"):
        raise DatasetParseError("DJ_bil struct has no sub_data field.")
    trials = bilateral.sub_data
    expected_shape = (TRIALS_PER_PARTICIPANT, 1)
    if not isinstance(trials, np.ndarray) or trials.shape != expected_shape:
        raise DatasetParseError(f"Expected sub_data shape {expected_shape}, found {trials.shape}.")
    return trials


def _parse_trial(
    participant_id: int,
    slot: int,
    raw_trial: Any | None,
    labels: tuple[str, ...],
    metadata_row: pd.Series,
    columns: Mapping[str, str],
) -> Trial:
    expected_name = TRIAL_NAMES[slot - 1]
    expected_condition = (
        "nonfatigued" if slot <= NONFATIGUED_TRIAL_COUNT else "fatigued"
    )
    metadata = {
        key: _python_scalar(metadata_row[column])
        for key, column in columns.items()
        if key not in {"subject"}
    }
    missing_flag = int(metadata_row[columns["missing"]])
    condition_code = int(metadata_row[columns["condition"]])
    note = metadata_row[columns["notes"]]
    missing_reason = None if pd.isna(note) else str(note).strip()

    if raw_trial is None:
        return _empty_trial(
            participant_id, slot, expected_name, expected_condition, labels, metadata, missing_reason
        )
    trial = _unwrap(raw_trial)
    if not hasattr(trial, "Joint_Angles"):
        raise DatasetParseError(
            f"Participant {participant_id} slot {slot} is not a valid trial struct."
        )
    if _is_empty(trial.Joint_Angles):
        return _empty_trial(
            participant_id, slot, expected_name, expected_condition, labels, metadata, missing_reason
        )

    name = _matlab_string(trial.File)
    joint_angles = np.asarray(trial.Joint_Angles, dtype=float)
    markers_raw = _unwrap(trial.marker)
    markers = {
        field: np.asarray(getattr(markers_raw, field), dtype=float)
        for field in markers_raw._fieldnames
    }
    events = {
        field: int(np.asarray(getattr(trial, field)).reshape(-1)[0])
        for field in EVENT_FIELDS
    }
    metadata["source_name_matches_slot"] = name == expected_name
    metadata["metadata_missing_flag"] = missing_flag
    metadata["metadata_condition_matches_slot"] = condition_code == (
        0 if expected_condition == "nonfatigued" else 1
    )
    return Trial(
        participant_id=participant_id,
        slot=slot,
        name=name,
        condition=expected_condition,
        joint_angles=joint_angles,
        joint_angle_labels=labels,
        events=events,
        com_velocity=np.asarray(trial.COM_velocity, dtype=float),
        com_position=np.asarray(trial.COM_position, dtype=float),
        com_acceleration=np.asarray(trial.COM_acceleration, dtype=float),
        markers=markers,
        metadata=metadata,
    )


def _empty_trial(
    participant_id: int,
    slot: int,
    name: str,
    condition: str,
    labels: tuple[str, ...],
    metadata: Mapping[str, Any],
    missing_reason: str | None,
) -> Trial:
    return Trial(
        participant_id=participant_id,
        slot=slot,
        name=name,
        condition=condition,
        joint_angles=None,
        joint_angle_labels=labels,
        metadata={
            **metadata,
            "metadata_missing_flag": int(metadata["missing"]),
            "source_name_matches_slot": True,
            "metadata_condition_matches_slot": int(metadata["condition"])
            == (0 if condition == "nonfatigued" else 1),
        },
        missing_reason=missing_reason,
    )


def _unwrap(value: Any) -> Any:
    current = value
    while isinstance(current, np.ndarray) and current.dtype == object and current.size == 1:
        current = current.item()
    return current


def _is_empty(value: Any) -> bool:
    return isinstance(value, np.ndarray) and value.size == 0


def _matlab_string(value: Any) -> str:
    array = np.asarray(value)
    if array.size != 1:
        raise DatasetParseError(f"Expected one MATLAB string value, found shape {array.shape}.")
    return str(array.reshape(-1)[0])


def _python_scalar(value: Any) -> Any:
    if pd.isna(value):
        return None
    return value.item() if hasattr(value, "item") else value
