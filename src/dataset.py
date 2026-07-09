"""Public Dataset API for JumpGuard AI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from collections.abc import Iterator
from typing import Any, Mapping

import numpy as np

from .participant import Participant
from .trial import Trial


@dataclass(frozen=True)
class Dataset:
    """A clean, validated collection of participant and trial objects.

    Args:
        participants: Participant objects keyed by metadata subject ID.
        joint_angle_labels: Ordered semantic labels for joint-angle columns.
        source_path: MAT file used to construct the dataset.
        metadata: Dataset-level provenance and source metadata.

    Examples:
        >>> dataset = Dataset.load("data/sample/DJ.mat")
        >>> dataset.get_participant(1).get_trial(1).name
        'DJ_t1'
    """

    participants: Mapping[int, Participant]
    joint_angle_labels: tuple[str, ...]
    source_path: Path
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        """Freeze public mappings after construction."""
        object.__setattr__(self, "participants", MappingProxyType(dict(self.participants)))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @classmethod
    def load(
        cls,
        path: str | Path,
        *,
        labels_path: str | Path | None = None,
        metadata_path: str | Path | None = None,
        validate: bool = True,
    ) -> "Dataset":
        """Load the complete dataset through the single public API.

        Args:
            path: Path to ``DJ.mat``.
            labels_path: Optional IK label workbook path.
            metadata_path: Optional trial-labeling workbook path.
            validate: Raise when validation finds errors.

        Returns:
            A Dataset containing clean Participant and Trial objects.

        Raises:
            DatasetValidationError: If validation errors are found.
            FileNotFoundError: If a required source file is unavailable.

        Examples:
            >>> dataset = Dataset.load("data/sample/DJ.mat")
            >>> len(dataset.list_participants())
            43
        """
        from .dataset_parser import parse_dataset
        from .load_dataset import load_excel_workbook, load_mat_dataset
        from .utils import METADATA_DIR, require_file
        from .validation import DatasetValidationError, validate_dataset

        mat_path = require_file(path)
        labels = require_file(labels_path or METADATA_DIR / "IK_column_labels.xlsx")
        labeling = require_file(metadata_path or METADATA_DIR / "labeling_DJ.xlsx")
        mat_info, raw_data = load_mat_dataset(mat_path)
        label_workbook = load_excel_workbook(labels)
        metadata_workbook = load_excel_workbook(labeling)
        dataset = parse_dataset(
            raw_data,
            label_workbook,
            metadata_workbook,
            source_path=mat_path,
            source_info={
                "mat_version": mat_info.version,
                "mat_loader": mat_info.loader,
                "labels_path": str(labels),
                "metadata_path": str(labeling),
            },
        )
        report = validate_dataset(dataset)
        object.__setattr__(
            dataset,
            "metadata",
            MappingProxyType({**dataset.metadata, "validation": report.to_dict()}),
        )
        if validate and report.has_errors:
            raise DatasetValidationError(report)
        return dataset

    def get_participant(self, participant_id: int | str) -> Participant:
        """Return a participant by integer or ``subNN`` identifier.

        Args:
            participant_id: Subject ID, for example ``1`` or ``"sub01"``.

        Returns:
            The matching Participant.

        Raises:
            KeyError: If the participant is not represented by metadata.

        Examples:
            >>> dataset.get_participant("sub01").participant_id
            1
        """
        normalized = _normalize_participant_id(participant_id)
        try:
            return self.participants[normalized]
        except KeyError as exc:
            raise KeyError(
                f"Participant {participant_id!r} is unavailable. "
                f"Available IDs: {self.list_participants()}."
            ) from exc

    def list_participants(self) -> list[int]:
        """Return sorted metadata-backed participant IDs.

        Returns:
            Sorted integer subject identifiers.

        Examples:
            >>> dataset.list_participants()[:3]
            [1, 2, 3]
        """
        return sorted(self.participants)

    def iter_trials(self, include_empty: bool = False) -> Iterator[Trial]:
        """Iterate over trials in participant and slot order.

        Args:
            include_empty: Include metadata-defined empty trial slots.

        Yields:
            Trial objects in deterministic order.

        Examples:
            >>> sum(1 for _ in dataset.iter_trials())
            249
        """
        for participant_id in self.list_participants():
            yield from self.participants[participant_id].list_trials(include_empty=include_empty)

    def summary(self) -> dict[str, Any]:
        """Return aggregate dataset dimensions and missingness.

        Returns:
            Counts and frame statistics suitable for documentation or plotting.

        Examples:
            >>> dataset.summary()["valid_trials"]
            249
        """
        all_trials = list(self.iter_trials(include_empty=True))
        valid_trials = [trial for trial in all_trials if not trial.is_empty]
        frames = np.asarray([trial.frame_count for trial in valid_trials], dtype=float)
        return {
            "participants": len(self.participants),
            "participant_ids": self.list_participants(),
            "total_trial_slots": len(all_trials),
            "valid_trials": len(valid_trials),
            "empty_trials": len(all_trials) - len(valid_trials),
            "joint_angle_labels": len(self.joint_angle_labels),
            "frame_min": int(frames.min()) if frames.size else 0,
            "frame_max": int(frames.max()) if frames.size else 0,
            "frame_mean": float(frames.mean()) if frames.size else 0.0,
            "frame_median": float(np.median(frames)) if frames.size else 0.0,
        }


def _normalize_participant_id(participant_id: int | str) -> int:
    """Normalize integer and ``subNN`` identifiers to an integer."""
    if isinstance(participant_id, int):
        return participant_id
    value = participant_id.strip().lower()
    if value.startswith("sub"):
        value = value[3:]
    try:
        return int(value)
    except ValueError as exc:
        raise KeyError(f"Invalid participant identifier: {participant_id!r}.") from exc
