"""Validation primitives for clean JumpGuard AI domain objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np

from .dataset import Dataset
from .schema import JOINT_ANGLE_COUNT, MARKER_FIELD_COUNT, TRIALS_PER_PARTICIPANT
from .trial import Trial


@dataclass(frozen=True)
class ValidationIssue:
    """One actionable dataset validation finding.

    Args:
        severity: ``error`` or ``warning``.
        code: Stable machine-readable issue code.
        path: Domain-object path where the issue occurred.
        message: Human-readable description.
        suggested_fix: Concrete remediation guidance.

    Examples:
        >>> issue = ValidationIssue("error", "shape", "trial", "Bad shape", "Reload data")
        >>> issue.severity
        'error'
    """

    severity: str
    code: str
    path: str
    message: str
    suggested_fix: str

    def to_dict(self) -> dict[str, str]:
        """Return a serializable representation.

        Returns:
            All issue fields as a dictionary.

        Examples:
            >>> issue.to_dict()["code"]
            'shape'
        """
        return {
            "severity": self.severity,
            "code": self.code,
            "path": self.path,
            "message": self.message,
            "suggested_fix": self.suggested_fix,
        }


@dataclass(frozen=True)
class ValidationReport:
    """Aggregate validation result for a Dataset.

    Args:
        issues: Ordered validation findings.

    Examples:
        >>> ValidationReport(()).is_valid
        True
    """

    issues: tuple[ValidationIssue, ...]

    @property
    def errors(self) -> tuple[ValidationIssue, ...]:
        """Return error-severity findings.

        Returns:
            Validation errors.
        """
        return tuple(issue for issue in self.issues if issue.severity == "error")

    @property
    def warnings(self) -> tuple[ValidationIssue, ...]:
        """Return warning-severity findings.

        Returns:
            Validation warnings.
        """
        return tuple(issue for issue in self.issues if issue.severity == "warning")

    @property
    def has_errors(self) -> bool:
        """Return whether any validation error exists.

        Returns:
            ``True`` when validation found an error.
        """
        return bool(self.errors)

    @property
    def is_valid(self) -> bool:
        """Return whether validation found no errors.

        Returns:
            ``True`` when the dataset is safe to consume.
        """
        return not self.has_errors

    def to_dict(self) -> dict[str, Any]:
        """Return summary counts and serialized findings.

        Returns:
            A dictionary suitable for notebook display or JSON output.
        """
        return {
            "is_valid": self.is_valid,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "issues": [issue.to_dict() for issue in self.issues],
        }


class DatasetValidationError(ValueError):
    """Raised when automatic Dataset validation finds errors."""

    def __init__(self, report: ValidationReport):
        """Build an informative exception from a validation report."""
        details = "\n".join(
            f"- [{issue.code}] {issue.path}: {issue.message} "
            f"Suggested fix: {issue.suggested_fix}"
            for issue in report.errors
        )
        super().__init__(f"Dataset validation failed with {len(report.errors)} error(s):\n{details}")
        self.report = report


def validate_dataset(dataset: Dataset) -> ValidationReport:
    """Validate labels, participants, trials, arrays, and metadata consistency.

    Args:
        dataset: Clean Dataset to validate.

    Returns:
        A report whose warnings include documented empty trials.

    Examples:
        >>> report = validate_dataset(dataset)
        >>> report.is_valid
        True
    """
    issues: list[ValidationIssue] = []
    labels = dataset.joint_angle_labels
    if not labels:
        issues.append(_error("missing_labels", "dataset.labels", "No IK labels were loaded."))
    if len(labels) != len(set(labels)):
        duplicates = sorted({label for label in labels if labels.count(label) > 1})
        issues.append(
            _error(
                "duplicate_labels",
                "dataset.labels",
                f"Duplicate semantic labels found: {duplicates}.",
                "Correct the authoritative workbook row before loading.",
            )
        )
    if labels and labels[0] != "time":
        issues.append(
            _error(
                "label_order",
                "dataset.labels[0]",
                f"Expected first label 'time', found {labels[0]!r}.",
                "Verify IK_column_labels.xlsx!A12:AR12.",
            )
        )

    for participant_id in dataset.list_participants():
        participant = dataset.get_participant(participant_id)
        if len(participant.trials) != TRIALS_PER_PARTICIPANT:
            issues.append(
                _error(
                    "trial_count",
                    f"participant[{participant_id}]",
                    f"Expected {TRIALS_PER_PARTICIPANT} trial slots, "
                    f"found {len(participant.trials)}.",
                    "Recheck labeling_DJ.xlsx rows and parser slot preservation.",
                )
            )
        for trial in participant.list_trials(include_empty=True):
            issues.extend(validate_trial(trial, expected_label_count=len(labels)))
    return ValidationReport(tuple(issues))


def validate_trial(
    trial: Trial,
    expected_label_count: int = JOINT_ANGLE_COUNT,
) -> tuple[ValidationIssue, ...]:
    """Validate one clean Trial.

    Args:
        trial: Trial to inspect.
        expected_label_count: Required number of joint-angle columns.

    Returns:
        Zero or more actionable findings.

    Examples:
        >>> validate_trial(valid_trial)
        ()
    """
    path = f"participant[{trial.participant_id}].trial[{trial.slot}]"
    issues: list[ValidationIssue] = []
    metadata_missing = int(trial.metadata.get("metadata_missing_flag", 0) or 0)
    if not bool(trial.metadata.get("metadata_condition_matches_slot", True)):
        issues.append(
            _error(
                "condition_mismatch",
                path,
                f"Metadata condition does not match slot condition {trial.condition!r}.",
                "Verify metadata row order and fatigue-condition coding.",
            )
        )
    if trial.is_empty:
        severity = "warning" if metadata_missing == 1 else "error"
        issue = ValidationIssue(
            severity,
            "empty_trial",
            path,
            f"Trial is empty{': ' + trial.missing_reason if trial.missing_reason else '.'}",
            "Preserve the empty slot and exclude it from numeric analysis."
            if metadata_missing == 1
            else "Correct the source file or mark the trial missing in labeling_DJ.xlsx.",
        )
        return (*issues, issue)

    if metadata_missing == 1:
        issues.append(
            _error(
                "metadata_mismatch",
                path,
                "Numeric trial data exists but metadata marks it missing.",
                "Correct the missing-data flag or verify participant/slot mapping.",
            )
        )
    if not bool(trial.metadata.get("source_name_matches_slot", True)):
        issues.append(
            _error(
                "trial_name_mismatch",
                path,
                f"Source trial name {trial.name!r} does not match its slot.",
                "Verify trial ordering before analysis.",
            )
        )

    joint_angles = trial.joint_angles
    assert joint_angles is not None
    if joint_angles.ndim != 2 or joint_angles.shape[1] != expected_label_count:
        issues.append(
            _error(
                "joint_angle_shape",
                f"{path}.joint_angles",
                f"Expected (frames, {expected_label_count}), found {joint_angles.shape}.",
                "Re-export or repair the inverse-kinematics array.",
            )
        )
    issues.extend(_numeric_array_issues(joint_angles, f"{path}.joint_angles"))

    for name in ("com_velocity", "com_position", "com_acceleration"):
        array = getattr(trial, name)
        if array is None or array.shape != (trial.frame_count, 3):
            issues.append(
                _error(
                    "com_shape",
                    f"{path}.{name}",
                    f"Expected ({trial.frame_count}, 3), found "
                    f"{None if array is None else array.shape}.",
                    "Verify frame alignment in the source trial.",
                )
            )
        elif array is not None:
            issues.extend(_numeric_array_issues(array, f"{path}.{name}"))

    for marker_name, array in trial.markers.items():
        expected_shape = (trial.frame_count, 1 if marker_name == "time" else 3)
        if array.shape != expected_shape:
            issues.append(
                _error(
                    "marker_shape",
                    f"{path}.markers[{marker_name!r}]",
                    f"Expected {expected_shape}, found {array.shape}.",
                    "Verify marker export and frame alignment.",
                )
            )
        issues.extend(_numeric_array_issues(array, f"{path}.markers[{marker_name!r}]"))
    if len(trial.markers) != MARKER_FIELD_COUNT:
        issues.append(
            _error(
                "marker_count",
                f"{path}.markers",
                f"Expected {MARKER_FIELD_COUNT} marker fields, found {len(trial.markers)}.",
                "Compare marker names against DATASET_REPORT.md.",
            )
        )
    for event_name, frame_index in trial.events.items():
        if not 1 <= frame_index <= trial.frame_count:
            issues.append(
                _error(
                    "event_range",
                    f"{path}.events[{event_name!r}]",
                    f"One-based event index {frame_index} is outside 1..{trial.frame_count}.",
                    "Correct the source event index before converting to zero-based indexing.",
                )
            )
    for first_name, second_name in (
        ("IC_first_K", "IC_second_K"),
        ("IC_first_A", "IC_second_A"),
    ):
        if (
            first_name in trial.events
            and second_name in trial.events
            and trial.events[first_name] > trial.events[second_name]
        ):
            issues.append(
                _error(
                    "event_order",
                    f"{path}.events",
                    f"{first_name} occurs after {second_name}.",
                    "Correct source contact indices before event-window extraction.",
                )
            )
    return tuple(issues)


def _numeric_array_issues(array: np.ndarray, path: str) -> Iterable[ValidationIssue]:
    if not np.issubdtype(array.dtype, np.number):
        yield _error(
            "non_numeric_array",
            path,
            f"Expected numeric dtype, found {array.dtype}.",
            "Convert or repair the source array.",
        )
        return
    if np.isnan(array).any():
        yield _error(
            "missing_values",
            path,
            f"Array contains {int(np.isnan(array).sum())} NaN value(s).",
            "Use an explicit missing-value strategy from preprocessing.py.",
        )
    if np.isinf(array).any():
        yield _error(
            "infinite_values",
            path,
            f"Array contains {int(np.isinf(array).sum())} infinite value(s).",
            "Repair or exclude corrupted frames.",
        )


def _error(
    code: str,
    path: str,
    message: str,
    suggested_fix: str = "Verify the source files and rerun validation.",
) -> ValidationIssue:
    return ValidationIssue("error", code, path, message, suggested_fix)
