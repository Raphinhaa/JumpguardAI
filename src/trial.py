"""Clean trial-level domain objects for JumpGuard AI."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Mapping

import numpy as np
from numpy.typing import NDArray

if TYPE_CHECKING:
    from .feature_engineering import FeatureExtractor


class EmptyTrialError(ValueError):
    """Raised when numeric data is requested from an empty trial."""


@dataclass(frozen=True)
class Trial:
    """A single Drop Jump trial detached from the raw MATLAB representation.

    Args:
        participant_id: Metadata subject identifier.
        slot: One-based trial slot from 1 through 6.
        name: Source trial name, such as ``DJ_t1``.
        condition: Either ``nonfatigued`` or ``fatigued``.
        joint_angles: Frame-by-column inverse-kinematics matrix.
        joint_angle_labels: Semantic labels for the matrix columns.
        events: Named one-based event frame indices from MATLAB.
        com_velocity: Center-of-mass velocity with shape ``(frames, 3)``.
        com_position: Center-of-mass position with shape ``(frames, 3)``.
        com_acceleration: Center-of-mass acceleration with shape ``(frames, 3)``.
        markers: Marker names mapped to numeric coordinate arrays.
        metadata: Trial-level source metadata.
        missing_reason: Documented reason when the trial is empty.

    Examples:
        >>> trial.get_joint_angle("knee_angle_r").ndim
        1
        >>> trial.summary()["participant_id"]
        1
    """

    participant_id: int
    slot: int
    name: str
    condition: str
    joint_angles: NDArray[np.float64] | None
    joint_angle_labels: tuple[str, ...]
    events: Mapping[str, int] = field(default_factory=dict)
    com_velocity: NDArray[np.float64] | None = None
    com_position: NDArray[np.float64] | None = None
    com_acceleration: NDArray[np.float64] | None = None
    markers: Mapping[str, NDArray[np.float64]] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    missing_reason: str | None = None
    _label_to_index: Mapping[str, int] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Create immutable mappings and the semantic label lookup."""
        object.__setattr__(self, "events", MappingProxyType(dict(self.events)))
        object.__setattr__(self, "markers", MappingProxyType(dict(self.markers)))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))
        object.__setattr__(
            self,
            "_label_to_index",
            MappingProxyType({label: index for index, label in enumerate(self.joint_angle_labels)}),
        )

    @property
    def is_empty(self) -> bool:
        """Return whether this trial has no joint-angle matrix.

        Examples:
            >>> empty_trial.is_empty
            True
        """
        return self.joint_angles is None

    @property
    def frame_count(self) -> int:
        """Return the number of frames, or zero for an empty trial.

        Examples:
            >>> trial.frame_count > 0
            True
        """
        return 0 if self.joint_angles is None else int(self.joint_angles.shape[0])

    def get_joint_angle(self, name: str) -> NDArray[np.float64]:
        """Return one joint-angle column by semantic label.

        Args:
            name: Exact label from ``IK_column_labels.xlsx``.

        Returns:
            A one-dimensional view with one value per frame.

        Raises:
            EmptyTrialError: If this trial has no data.
            KeyError: If ``name`` is not an available semantic label.

        Examples:
            >>> knee = trial.get_joint_angle("knee_angle_r")
            >>> knee.shape == (trial.frame_count,)
            True
        """
        if self.joint_angles is None:
            raise EmptyTrialError(
                f"Participant {self.participant_id} trial slot {self.slot} is empty"
                + (f": {self.missing_reason}" if self.missing_reason else ".")
            )
        if name not in self._label_to_index:
            suggestions = ", ".join(
                label for label in self.joint_angle_labels if name.lower() in label.lower()
            )
            suffix = f" Similar labels: {suggestions}." if suggestions else ""
            raise KeyError(f"Unknown joint-angle label {name!r}.{suffix}")
        return self.joint_angles[:, self._label_to_index[name]]

    def summary(self) -> dict[str, Any]:
        """Return a serializable trial summary.

        Returns:
            Trial identity, dimensions, event count, and missingness.

        Examples:
            >>> trial.summary()["joint_angle_columns"]
            44
        """
        return {
            "participant_id": self.participant_id,
            "slot": self.slot,
            "name": self.name,
            "condition": self.condition,
            "is_empty": self.is_empty,
            "missing_reason": self.missing_reason,
            "frames": self.frame_count,
            "joint_angle_columns": (
                0 if self.joint_angles is None else int(self.joint_angles.shape[1])
            ),
            "event_count": len(self.events),
            "marker_count": len(self.markers),
        }

    def plot(self, joint_angles: tuple[str, ...] | None = None, **kwargs: Any) -> Any:
        """Plot this trial using the reusable visualization layer.

        Args:
            joint_angles: Optional semantic labels to plot.
            **kwargs: Additional arguments passed to ``plot_trial``.

        Returns:
            A Matplotlib figure and axes pair.

        Examples:
            >>> figure, axes = trial.plot(("knee_angle_r", "knee_angle_l"))
        """
        from .visualization import plot_trial

        return plot_trial(self, joint_angles=joint_angles, **kwargs)

    def extract_features(
        self,
        extractor: "FeatureExtractor | None" = None,
    ) -> dict[str, float]:
        """Extract the configured biomechanical feature vector.

        Args:
            extractor: Optional FeatureExtractor; the default uses ``nan`` handling.

        Returns:
            Ordered mapping of measurable full-recording features.

        Examples:
            >>> features = trial.extract_features()
            >>> "knee_flexion_right_rom" in features
            True
        """
        if extractor is None:
            from .feature_engineering import FeatureExtractor

            extractor = FeatureExtractor()
        return extractor.extract(self)
