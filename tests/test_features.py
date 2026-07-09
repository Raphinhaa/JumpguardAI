"""Tests for biomechanical feature primitives."""

import math

import numpy as np
import pytest

from src.features.statistical import describe_signal
from src.features.symmetry import absolute_difference, percent_difference, symmetry_index
from src.features.temporal import time_to_peak


def test_statistical_descriptors_are_direct_measurements() -> None:
    result = describe_signal([1.0, 2.0, 4.0])
    assert result["mean"] == pytest.approx(7 / 3)
    assert result["median"] == 2.0
    assert result["maximum"] == 4.0
    assert result["minimum"] == 1.0
    assert result["rom"] == 3.0
    assert result["variance"] == pytest.approx(np.var([1.0, 2.0, 4.0]))


def test_time_to_peak_uses_first_maximum_and_real_time() -> None:
    assert time_to_peak([1, 4, 4, 2], [0.2, 0.3, 0.4, 0.5]) == pytest.approx(0.1)


def test_symmetry_formulas() -> None:
    assert absolute_difference(12, 8) == 4
    assert percent_difference(12, 8) == 40
    assert symmetry_index(12, 8) == 40
    assert symmetry_index(8, 12) == -40
    assert math.isnan(percent_difference(0, 0))
    assert math.isnan(symmetry_index(0, 0))


def test_nonfinite_signal_is_rejected() -> None:
    with pytest.raises(ValueError, match="finite"):
        describe_signal([1.0, np.nan])
