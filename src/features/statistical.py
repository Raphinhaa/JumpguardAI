"""Essential deterministic statistical descriptors for joint-angle signals."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike


DESCRIPTORS: tuple[str, ...] = (
    "mean",
    "median",
    "std",
    "variance",
    "maximum",
    "minimum",
    "rom",
)


def describe_signal(values: ArrayLike) -> dict[str, float]:
    """Compute essential descriptors for one complete angle signal.

    Args:
        values: One-dimensional finite joint-angle signal.

    Returns:
        Mean, median, population standard deviation, population variance,
        maximum, minimum, and range of motion.

    Raises:
        ValueError: If the signal is empty, non-vector, or nonfinite.

    Examples:
        >>> describe_signal([1.0, 2.0, 4.0])["rom"]
        3.0
    """
    array = np.asarray(values, dtype=float)
    if array.ndim != 1 or array.size == 0:
        raise ValueError(f"Expected a non-empty one-dimensional signal, found {array.shape}.")
    if not np.isfinite(array).all():
        raise ValueError("Statistical descriptors require a finite signal.")
    return {
        "mean": float(np.mean(array)),
        "median": float(np.median(array)),
        "std": float(np.std(array, ddof=0)),
        "variance": float(np.var(array, ddof=0)),
        "maximum": float(np.max(array)),
        "minimum": float(np.min(array)),
        "rom": float(np.max(array) - np.min(array)),
    }
