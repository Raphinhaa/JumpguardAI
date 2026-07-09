"""Tests for reusable preprocessing helpers."""

import numpy as np
import pytest

from src.preprocessing import (
    handle_missing,
    interpolate_missing,
    lowpass_filter,
    normalize,
    trim_frames,
)


def test_interpolation_and_missing_policies() -> None:
    values = np.array([1.0, np.nan, 3.0])
    np.testing.assert_allclose(interpolate_missing(values), [1.0, 2.0, 3.0])
    np.testing.assert_allclose(handle_missing(values, "fill", fill_value=0), [1, 0, 3])
    with pytest.raises(ValueError, match="missing"):
        handle_missing(values)


def test_normalization_and_trimming() -> None:
    np.testing.assert_allclose(normalize([1, 2, 3], "minmax"), [0, 0.5, 1])
    np.testing.assert_array_equal(trim_frames(np.arange(8), 2, 5), [2, 3, 4])
    with pytest.raises(ValueError, match="bounds"):
        trim_frames(np.arange(3), 2, 4)


def test_filter_preserves_shape() -> None:
    time = np.arange(500) / 250
    values = np.sin(2 * np.pi * 3 * time) + 0.2 * np.sin(2 * np.pi * 60 * time)
    assert lowpass_filter(values, 15, 250).shape == values.shape
