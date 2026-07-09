"""Reusable numeric preprocessing helpers without biomechanical feature logic."""

from __future__ import annotations

from typing import Literal

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy import signal


def interpolate_missing(values: ArrayLike, axis: int = 0) -> NDArray[np.float64]:
    """Linearly interpolate NaN values along one axis.

    Args:
        values: Numeric array containing optional NaNs.
        axis: Axis representing ordered samples.

    Returns:
        A float array with interior gaps interpolated and edge gaps extended.

    Raises:
        ValueError: If an entire one-dimensional slice is missing.

    Examples:
        >>> interpolate_missing([1.0, np.nan, 3.0]).tolist()
        [1.0, 2.0, 3.0]
    """
    array = np.asarray(values, dtype=float)
    moved = np.moveaxis(array, axis, 0).copy()
    flat = moved.reshape(moved.shape[0], -1)
    indices = np.arange(flat.shape[0])
    for column in range(flat.shape[1]):
        valid = np.isfinite(flat[:, column])
        if not valid.any():
            raise ValueError(f"Cannot interpolate slice {column}: every value is missing.")
        flat[:, column] = np.interp(indices, indices[valid], flat[valid, column])
    return np.moveaxis(flat.reshape(moved.shape), 0, axis)


def normalize(
    values: ArrayLike,
    method: Literal["zscore", "minmax"] = "zscore",
    axis: int = 0,
) -> NDArray[np.float64]:
    """Normalize numeric values without mutating the input.

    Args:
        values: Numeric array.
        method: ``zscore`` or ``minmax``.
        axis: Axis along which statistics are computed.

    Returns:
        Normalized float array; constant slices become zeros.

    Raises:
        ValueError: If ``method`` is unsupported.

    Examples:
        >>> normalize([1.0, 2.0, 3.0], method="minmax").tolist()
        [0.0, 0.5, 1.0]
    """
    array = np.asarray(values, dtype=float)
    if method == "zscore":
        center = np.nanmean(array, axis=axis, keepdims=True)
        scale = np.nanstd(array, axis=axis, keepdims=True)
    elif method == "minmax":
        minimum = np.nanmin(array, axis=axis, keepdims=True)
        center = minimum
        scale = np.nanmax(array, axis=axis, keepdims=True) - minimum
    else:
        raise ValueError(f"Unsupported normalization method {method!r}.")
    safe_scale = np.where(scale == 0, 1.0, scale)
    return (array - center) / safe_scale


def trim_frames(values: ArrayLike, start: int = 0, stop: int | None = None) -> np.ndarray:
    """Return a validated frame slice.

    Args:
        values: Array whose first axis represents frames.
        start: Inclusive zero-based frame.
        stop: Exclusive zero-based frame, or the array end.

    Returns:
        A copied frame slice.

    Raises:
        ValueError: If bounds are invalid.

    Examples:
        >>> trim_frames(np.arange(5), 1, 4).tolist()
        [1, 2, 3]
    """
    array = np.asarray(values)
    final = len(array) if stop is None else stop
    if start < 0 or final < start or final > len(array):
        raise ValueError(f"Invalid frame bounds [{start}:{final}] for {len(array)} frames.")
    return array[start:final].copy()


def handle_missing(
    values: ArrayLike,
    strategy: Literal["raise", "interpolate", "fill", "drop"] = "raise",
    *,
    fill_value: float = 0.0,
    axis: int = 0,
) -> NDArray[np.float64]:
    """Apply an explicit missing-value policy.

    Args:
        values: Numeric array containing optional NaNs.
        strategy: ``raise``, ``interpolate``, ``fill``, or ``drop``.
        fill_value: Replacement used by ``fill``.
        axis: Sample axis for interpolation or dropping.

    Returns:
        Processed float array.

    Raises:
        ValueError: If missing values exist under ``raise`` or strategy is unknown.

    Examples:
        >>> handle_missing([1.0, np.nan], "fill", fill_value=-1).tolist()
        [1.0, -1.0]
    """
    array = np.asarray(values, dtype=float)
    if not np.isnan(array).any():
        return array.copy()
    if strategy == "raise":
        raise ValueError(f"Array contains {int(np.isnan(array).sum())} missing value(s).")
    if strategy == "interpolate":
        return interpolate_missing(array, axis=axis)
    if strategy == "fill":
        return np.nan_to_num(array, nan=fill_value)
    if strategy == "drop":
        other_axes = tuple(index for index in range(array.ndim) if index != axis)
        keep = ~np.isnan(array).any(axis=other_axes) if other_axes else ~np.isnan(array)
        return np.compress(keep, array, axis=axis)
    raise ValueError(f"Unsupported missing-value strategy {strategy!r}.")


def lowpass_filter(
    values: ArrayLike,
    cutoff_hz: float,
    sampling_hz: float,
    *,
    order: int = 4,
    axis: int = 0,
) -> NDArray[np.float64]:
    """Apply a zero-phase Butterworth low-pass filter.

    Args:
        values: Numeric samples.
        cutoff_hz: Cutoff frequency in hertz.
        sampling_hz: Sampling frequency in hertz.
        order: Butterworth filter order.
        axis: Time/sample axis.

    Returns:
        Filtered float array with unchanged shape.

    Raises:
        ValueError: If frequencies, order, or sample count are invalid.

    Examples:
        >>> filtered = lowpass_filter(signal_values, 15.0, 250.0)
        >>> filtered.shape == signal_values.shape
        True
    """
    if sampling_hz <= 0 or cutoff_hz <= 0 or cutoff_hz >= sampling_hz / 2:
        raise ValueError("cutoff_hz must be positive and below the Nyquist frequency.")
    if order < 1:
        raise ValueError("Filter order must be at least 1.")
    array = np.asarray(values, dtype=float)
    sos = signal.butter(order, cutoff_hz, fs=sampling_hz, btype="low", output="sos")
    try:
        return signal.sosfiltfilt(sos, array, axis=axis)
    except ValueError as exc:
        raise ValueError(
            "Signal is too short for zero-phase filtering; use more frames or a lower order."
        ) from exc
