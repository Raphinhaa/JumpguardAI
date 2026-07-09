"""Reusable publication-quality plots for JumpGuard AI domain objects."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .dataset import Dataset
from .participant import Participant
from .trial import EmptyTrialError, Trial


def plot_joint_angle(
    trial: Trial,
    name: str,
    *,
    ax: Axes | None = None,
    color: str = "#2166AC",
    label: str | None = None,
) -> tuple[Figure, Axes]:
    """Plot one semantically named joint-angle series.

    Args:
        trial: Non-empty Trial.
        name: Exact IK semantic label.
        ax: Optional Matplotlib axes.
        color: Line color.
        label: Optional legend label.

    Returns:
        Figure and axes containing the plot.

    Examples:
        >>> figure, axes = plot_joint_angle(trial, "knee_angle_r")
    """
    values = trial.get_joint_angle(name)
    figure, axes = _figure_and_axes(ax)
    axes.plot(_time_axis(trial), values, color=color, linewidth=1.6, label=label or name)
    axes.set(xlabel="Time (s)", ylabel=_axis_label(name), title=_trial_title(trial))
    axes.legend(frameon=False)
    _style_axes(axes)
    figure.tight_layout()
    return figure, axes


def plot_trial(
    trial: Trial,
    joint_angles: Sequence[str] | None = None,
    *,
    ax: Axes | None = None,
) -> tuple[Figure, Axes]:
    """Plot selected semantic joint angles for one trial.

    Args:
        trial: Non-empty Trial.
        joint_angles: Labels to plot; defaults to bilateral knee angles.
        ax: Optional Matplotlib axes.

    Returns:
        Figure and axes containing all selected series.

    Raises:
        EmptyTrialError: If the trial contains no numeric data.

    Examples:
        >>> figure, axes = plot_trial(trial, ("hip_flexion_r", "hip_flexion_l"))
    """
    if trial.is_empty:
        raise EmptyTrialError(
            f"Cannot plot empty participant {trial.participant_id} trial {trial.slot}."
        )
    names = tuple(joint_angles or ("knee_angle_r", "knee_angle_l"))
    figure, axes = _figure_and_axes(ax)
    for name in names:
        axes.plot(_time_axis(trial), trial.get_joint_angle(name), linewidth=1.5, label=name)
    axes.set(xlabel="Time (s)", ylabel="Angle (degrees)", title=_trial_title(trial))
    axes.legend(frameon=False, ncols=min(2, len(names)))
    _style_axes(axes)
    figure.tight_layout()
    return figure, axes


def plot_participant(
    participant: Participant,
    joint_angle: str = "knee_angle_r",
    *,
    condition: str | None = None,
) -> tuple[Figure, Axes]:
    """Compare one joint angle across a participant's valid trials.

    Args:
        participant: Participant to visualize.
        joint_angle: Semantic IK label.
        condition: Optional ``nonfatigued`` or ``fatigued`` filter.

    Returns:
        Figure and axes containing one line per matching trial.

    Examples:
        >>> figure, axes = plot_participant(participant, "knee_angle_r")
    """
    trials = [
        trial
        for trial in participant.list_trials()
        if condition is None or trial.condition == condition
    ]
    if not trials:
        raise ValueError(
            f"Participant {participant.participant_id} has no valid trials"
            + (f" for condition {condition!r}." if condition else ".")
        )
    figure, axes = plt.subplots(figsize=(8.0, 4.8))
    for trial in trials:
        axes.plot(
            _time_axis(trial),
            trial.get_joint_angle(joint_angle),
            linewidth=1.2,
            alpha=0.85,
            label=trial.name,
        )
    axes.set(
        xlabel="Time (s)",
        ylabel=_axis_label(joint_angle),
        title=f"Participant {participant.participant_id}: {joint_angle}",
    )
    axes.legend(frameon=False, ncols=2)
    _style_axes(axes)
    figure.tight_layout()
    return figure, axes


def plot_dataset_summary(dataset: Dataset) -> tuple[Figure, np.ndarray]:
    """Plot dataset frame-count and trial-availability summaries.

    Args:
        dataset: Dataset to summarize.

    Returns:
        Figure and a two-element axes array.

    Examples:
        >>> figure, axes = plot_dataset_summary(dataset)
        >>> len(axes)
        2
    """
    valid_trials = list(dataset.iter_trials())
    participants = [dataset.get_participant(value) for value in dataset.list_participants()]
    figure, axes = plt.subplots(1, 2, figsize=(11.0, 4.4))
    axes[0].hist(
        [trial.frame_count for trial in valid_trials],
        bins=20,
        color="#2166AC",
        edgecolor="white",
    )
    axes[0].set(xlabel="Frames", ylabel="Trial count", title="Trial frame distribution")
    ids = [participant.participant_id for participant in participants]
    counts = [len(participant.list_trials()) for participant in participants]
    axes[1].bar(ids, counts, color="#4D9221", width=0.8)
    axes[1].set(
        xlabel="Participant ID",
        ylabel="Valid trials",
        title="Valid trials by participant",
        ylim=(0, 6.5),
    )
    for axis in axes:
        _style_axes(axis)
    figure.tight_layout()
    return figure, axes


def _figure_and_axes(ax: Axes | None) -> tuple[Figure, Axes]:
    if ax is not None:
        return ax.figure, ax
    return plt.subplots(figsize=(8.0, 4.8))


def _time_axis(trial: Trial) -> np.ndarray:
    if "time" in trial.joint_angle_labels:
        return trial.get_joint_angle("time")
    return np.arange(trial.frame_count)


def _axis_label(name: str) -> str:
    return "Time (s)" if name == "time" else "Angle (degrees)"


def _trial_title(trial: Trial) -> str:
    return f"Participant {trial.participant_id} - {trial.name}"


def _style_axes(ax: Axes) -> None:
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.7, alpha=0.75)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=9)
