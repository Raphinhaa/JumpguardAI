"""Tests for the public Dataset API."""

import pytest

from src.dataset import Dataset


def test_dataset_summary_matches_documented_counts(dataset: Dataset) -> None:
    summary = dataset.summary()
    assert summary["participants"] == 43
    assert summary["total_trial_slots"] == 258
    assert summary["valid_trials"] == 249
    assert summary["empty_trials"] == 9
    assert summary["frame_min"] == 842
    assert summary["frame_max"] == 2280


def test_dataset_accepts_integer_and_sub_identifiers(dataset: Dataset) -> None:
    assert dataset.get_participant(1) is dataset.get_participant("sub01")
    assert 5 not in dataset.list_participants()
    assert 44 in dataset.list_participants()


def test_dataset_reports_unknown_participant(dataset: Dataset) -> None:
    with pytest.raises(KeyError, match="Available IDs"):
        dataset.get_participant(5)


def test_trial_iteration_can_include_empty_slots(dataset: Dataset) -> None:
    assert sum(1 for _ in dataset.iter_trials()) == 249
    assert sum(1 for _ in dataset.iter_trials(include_empty=True)) == 258
