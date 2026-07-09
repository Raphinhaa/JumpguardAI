"""Tests for Participant behavior."""

import pytest

from src.dataset import Dataset


def test_participant_gets_trial_by_slot_and_name(dataset: Dataset) -> None:
    participant = dataset.get_participant(1)
    assert participant.get_trial(1) is participant.get_trial("DJ_t1")
    assert participant.get_trial("f_DJ_t3").slot == 6


def test_participant_lists_valid_or_all_trials(dataset: Dataset) -> None:
    participant = dataset.get_participant(32)
    assert len(participant.list_trials()) == 3
    assert len(participant.list_trials(include_empty=True)) == 6
    assert participant.summary()["empty_trials"] == 3


def test_participant_reports_unknown_trial(dataset: Dataset) -> None:
    with pytest.raises(KeyError, match="Available slots"):
        dataset.get_participant(1).get_trial("unknown")
