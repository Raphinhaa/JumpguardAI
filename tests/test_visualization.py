"""Smoke tests for reusable plotting functions."""

import matplotlib.pyplot as plt

from src.dataset import Dataset
from src.visualization import (
    plot_dataset_summary,
    plot_joint_angle,
    plot_participant,
    plot_trial,
)


def test_all_public_plotters_return_figures(dataset: Dataset) -> None:
    participant = dataset.get_participant(1)
    trial = participant.get_trial(1)
    results = [
        plot_joint_angle(trial, "knee_angle_r"),
        plot_trial(trial),
        plot_participant(participant),
        plot_dataset_summary(dataset),
    ]
    assert all(figure is not None and axes is not None for figure, axes in results)
    plt.close("all")
