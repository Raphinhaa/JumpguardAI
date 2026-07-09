"""Semantic joint-angle selections for directly measurable features."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class JointSignal:
    """Definition of one semantic joint-angle signal.

    Args:
        key: Compact output feature prefix.
        label: Exact Trial joint-angle label.
        joint: Anatomical joint name.
        side: ``left`` or ``right``.
        plane: Motion-plane description supported by the source label.

    Examples:
        >>> PRIMARY_JOINT_SIGNALS[0].label
        'hip_flexion_r'
    """

    key: str
    label: str
    joint: str
    side: str
    plane: str


@dataclass(frozen=True)
class JointPair:
    """Definition of a left/right signal pair used for symmetry.

    Args:
        key: Compact output feature prefix.
        left_label: Exact left-side Trial label.
        right_label: Exact right-side Trial label.
        joint: Anatomical joint name.

    Examples:
        >>> PRIMARY_JOINT_PAIRS[0].joint
        'hip'
    """

    key: str
    left_label: str
    right_label: str
    joint: str


PRIMARY_JOINT_SIGNALS: tuple[JointSignal, ...] = (
    JointSignal("hip_flexion_right", "hip_flexion_r", "hip", "right", "sagittal"),
    JointSignal("hip_flexion_left", "hip_flexion_l", "hip", "left", "sagittal"),
    JointSignal("knee_flexion_right", "knee_angle_r", "knee", "right", "sagittal"),
    JointSignal("knee_flexion_left", "knee_angle_l", "knee", "left", "sagittal"),
    JointSignal("ankle_angle_right", "ankle_angle_r", "ankle", "right", "sagittal"),
    JointSignal("ankle_angle_left", "ankle_angle_l", "ankle", "left", "sagittal"),
)

PRIMARY_JOINT_PAIRS: tuple[JointPair, ...] = (
    JointPair("hip_flexion", "hip_flexion_l", "hip_flexion_r", "hip"),
    JointPair("knee_flexion", "knee_angle_l", "knee_angle_r", "knee"),
    JointPair("ankle_angle", "ankle_angle_l", "ankle_angle_r", "ankle"),
)
