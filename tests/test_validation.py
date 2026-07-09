"""Tests for automatic validation and actionable findings."""

from dataclasses import replace

import numpy as np

from src.dataset import Dataset
from src.trial import Trial
from src.validation import validate_dataset, validate_trial


def test_canonical_dataset_has_only_documented_empty_warnings(dataset: Dataset) -> None:
    report = validate_dataset(dataset)
    assert report.is_valid
    assert len(report.errors) == 0
    assert len(report.warnings) == 9
    assert {issue.code for issue in report.warnings} == {"empty_trial"}


def test_validation_detects_corrupted_joint_array(dataset: Dataset) -> None:
    source = dataset.get_participant(1).get_trial(1)
    corrupted = source.joint_angles.copy()
    corrupted[0, 1] = np.nan
    trial = replace(source, joint_angles=corrupted)
    issues = validate_trial(trial)
    assert "missing_values" in {issue.code for issue in issues}


def test_validation_detects_inconsistent_dimensions(dataset: Dataset) -> None:
    source = dataset.get_participant(1).get_trial(1)
    trial = replace(source, joint_angles=source.joint_angles[:, :-1])
    issues = validate_trial(trial)
    assert "joint_angle_shape" in {issue.code for issue in issues}


def test_validation_detects_metadata_condition_mismatch(dataset: Dataset) -> None:
    source = dataset.get_participant(1).get_trial(1)
    metadata = {**source.metadata, "metadata_condition_matches_slot": False}
    issues = validate_trial(replace(source, metadata=metadata))
    assert "condition_mismatch" in {issue.code for issue in issues}
