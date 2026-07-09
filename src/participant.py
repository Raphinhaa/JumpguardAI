"""Participant-level domain objects for JumpGuard AI."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Mapping

from .trial import Trial

if TYPE_CHECKING:
    import pandas as pd

    from .feature_engineering import FeatureExtractor


@dataclass(frozen=True)
class Participant:
    """A metadata-backed participant and their six Drop Jump trial slots.

    Args:
        participant_id: Subject identifier from ``labeling_DJ.xlsx``.
        trials: Trial objects ordered by one-based slot.
        metadata: Participant-level metadata copied from the labeling workbook.

    Examples:
        >>> participant.list_trials()[0].participant_id == participant.participant_id
        True
    """

    participant_id: int
    trials: tuple[Trial, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Freeze metadata and enforce unique trial slots."""
        slots = [trial.slot for trial in self.trials]
        if len(slots) != len(set(slots)):
            raise ValueError(f"Participant {self.participant_id} has duplicate trial slots.")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def get_trial(self, identifier: int | str = 1) -> Trial:
        """Return a trial by one-based slot or source name.

        Args:
            identifier: Trial slot such as ``1`` or name such as ``DJ_t1``.

        Returns:
            The matching Trial, including an empty Trial when metadata marks it missing.

        Raises:
            KeyError: If no trial matches the identifier.

        Examples:
            >>> participant.get_trial(1).name
            'DJ_t1'
            >>> participant.get_trial("f_DJ_t1").slot
            4
        """
        for trial in self.trials:
            if trial.slot == identifier or trial.name == identifier:
                return trial
        raise KeyError(
            f"Participant {self.participant_id} has no trial {identifier!r}. "
            f"Available slots: {[trial.slot for trial in self.trials]}."
        )

    def list_trials(self, include_empty: bool = False) -> list[Trial]:
        """List trials in slot order.

        Args:
            include_empty: Include metadata-defined slots without numeric data.

        Returns:
            A new list of matching Trial objects.

        Examples:
            >>> len(participant.list_trials(include_empty=True))
            6
        """
        return [
            trial
            for trial in sorted(self.trials, key=lambda item: item.slot)
            if include_empty or not trial.is_empty
        ]

    def summary(self) -> dict[str, Any]:
        """Return a serializable participant summary.

        Returns:
            Participant identity and valid/empty trial counts.

        Examples:
            >>> participant.summary()["total_trial_slots"]
            6
        """
        valid_trials = self.list_trials()
        return {
            "participant_id": self.participant_id,
            "total_trial_slots": len(self.trials),
            "valid_trials": len(valid_trials),
            "empty_trials": len(self.trials) - len(valid_trials),
            "frame_count": sum(trial.frame_count for trial in valid_trials),
            "metadata": dict(self.metadata),
        }

    def extract_features(
        self,
        extractor: "FeatureExtractor | None" = None,
    ) -> "pd.DataFrame":
        """Extract one feature-table row per metadata-defined trial slot.

        Args:
            extractor: Optional FeatureExtractor; the default uses ``nan`` handling.

        Returns:
            Six-row pandas DataFrame.

        Examples:
            >>> participant.extract_features().shape[0]
            6
        """
        if extractor is None:
            from .feature_engineering import FeatureExtractor

            extractor = FeatureExtractor()
        return extractor.extract_participant(self)
