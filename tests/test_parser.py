"""Tests for conversion from raw sources to domain objects."""

from src.dataset import Dataset
from src.participant import Participant
from src.trial import Trial


def test_parser_produces_clean_domain_objects(dataset: Dataset) -> None:
    participant = dataset.get_participant(1)
    trial = participant.get_trial(1)
    assert isinstance(participant, Participant)
    assert isinstance(trial, Trial)
    assert trial.joint_angles is not None
    assert trial.joint_angles.shape == (1175, 44)
    assert not hasattr(trial, "_fieldnames")


def test_parser_preserves_metadata_defined_empty_slots(dataset: Dataset) -> None:
    assert dataset.get_participant(32).get_trial(4).is_empty
    assert dataset.get_participant(44).get_trial(1).is_empty
    assert dataset.get_participant(32).get_trial(4).missing_reason == (
        "no c3d file; excessive marker movement"
    )


def test_parser_uses_authoritative_label_range(dataset: Dataset) -> None:
    assert len(dataset.joint_angle_labels) == 44
    assert dataset.joint_angle_labels[:3] == ("time", "pelvis_list", "pelvis_tilt")
    assert dataset.metadata["label_range"] == "A12:AR12"
