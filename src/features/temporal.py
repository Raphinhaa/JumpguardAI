"""Temporal features directly supported by the full-recording time column."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike


def time_to_peak(values: ArrayLike, time: ArrayLike) -> float:
    """Return elapsed time from recording start to the signal maximum.

    Args:
        values: One-dimensional finite joint-angle signal.
        time: One-dimensional finite time signal in seconds.

    Returns:
        Seconds from ``time[0]`` to the first maximum value.

    Raises:
        ValueError: If signals are empty, nonfinite, mismatched, or time decreases.

    Examples:
        >>> time_to_peak([1.0, 3.0, 2.0], [0.0, 0.1, 0.2])
        0.1
    """
    signal = np.asarray(values, dtype=float)
    timestamps = np.asarray(time, dtype=float)
    if signal.ndim != 1 or timestamps.ndim != 1 or signal.size == 0:
        raise ValueError("Values and time must be non-empty one-dimensional signals.")
    if signal.shape != timestamps.shape:
        raise ValueError(f"Values shape {signal.shape} does not match time {timestamps.shape}.")
    if not np.isfinite(signal).all() or not np.isfinite(timestamps).all():
        raise ValueError("Time-to-peak requires finite values and timestamps.")
    if np.any(np.diff(timestamps) < 0):
        raise ValueError("Time values must be monotonically nondecreasing.")
    peak_index = int(np.argmax(signal))
    return float(timestamps[peak_index] - timestamps[0])
