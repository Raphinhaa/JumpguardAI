"""Transparent bilateral symmetry formulas for scalar joint measurements."""

from __future__ import annotations

import math


def absolute_difference(left: float, right: float) -> float:
    """Return the unsigned left/right difference.

    Args:
        left: Left-side scalar measurement.
        right: Right-side scalar measurement.

    Returns:
        ``abs(left - right)``.

    Examples:
        >>> absolute_difference(10.0, 8.0)
        2.0
    """
    return abs(float(left) - float(right))


def percent_difference(left: float, right: float) -> float:
    """Return absolute difference relative to mean side magnitude.

    Formula: ``100 * |L - R| / ((|L| + |R|) / 2)``.

    Args:
        left: Left-side scalar measurement.
        right: Right-side scalar measurement.

    Returns:
        Percent difference, or NaN when both magnitudes are zero.

    Examples:
        >>> percent_difference(12.0, 8.0)
        40.0
    """
    denominator = (abs(float(left)) + abs(float(right))) / 2.0
    return math.nan if denominator == 0.0 else 100.0 * absolute_difference(left, right) / denominator


def symmetry_index(left: float, right: float) -> float:
    """Return the signed bilateral symmetry index.

    Formula: ``100 * (L - R) / ((|L| + |R|) / 2)``. Positive values indicate
    a larger left-side measurement. Magnitudes are used in the denominator so
    signed angle conventions cannot cause denominator cancellation.

    Args:
        left: Left-side scalar measurement.
        right: Right-side scalar measurement.

    Returns:
        Signed symmetry index in percent, or NaN when both magnitudes are zero.

    Examples:
        >>> symmetry_index(12.0, 8.0)
        40.0
    """
    denominator = (abs(float(left)) + abs(float(right))) / 2.0
    return math.nan if denominator == 0.0 else 100.0 * (float(left) - float(right)) / denominator
