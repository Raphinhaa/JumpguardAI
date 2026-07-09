"""Tests for semantic Trial access."""

import numpy as np
import pytest

from src.dataset import Dataset
from src.trial import EmptyTrialError


def test_semantic_joint_angle_access_maps_exact_column(dataset: Dataset) -> None:
    trial = dataset.get_participant(1).get_trial(1)
    knee = trial.get_joint_angle("knee_angle_r")
    assert knee.shape == (trial.frame_count,)
    np.testing.assert_array_equal(knee, trial.joint_angles[:, 10])


def test_unknown_joint_angle_is_informative(dataset: Dataset) -> None:
    trial = dataset.get_participant(1).get_trial(1)
    with pytest.raises(KeyError, match="Unknown joint-angle label"):
        trial.get_joint_angle("not_a_joint")


def test_empty_trial_rejects_numeric_access(dataset: Dataset) -> None:
    trial = dataset.get_participant(44).get_trial(1)
    with pytest.raises(EmptyTrialError, match="pain reported"):
        trial.get_joint_angle("knee_angle_r")
