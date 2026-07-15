"""Camera-aware measurement confidence diagnostics.

This module adds interpretive confidence metadata from existing landmark
visibility values. It does not alter pose estimation, joint-angle math,
feature extraction, deltas, symmetry, MP4 generation, or synchronization.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from src.feature_extraction import ANGLE_SIGNAL_MAP


CAMERA_SIDE_LANDMARKS: tuple[str, ...] = ("shoulder", "hip", "knee", "ankle", "heel", "foot_index")

CONFIDENCE_THRESHOLDS: dict[str, float] = {
    "high": 0.85,
    "moderate": 0.70,
    "partial": 0.50,
}

CONFIDENCE_LABELS: dict[str, str] = {
    "high": "High Confidence",
    "moderate": "Moderate Confidence",
    "partial": "Partially Occluded",
    "low": "Low Confidence",
}

CONFIDENCE_ICONS: dict[str, str] = {
    "high": "green",
    "moderate": "yellow",
    "partial": "orange",
    "low": "red",
}


def attach_measurement_confidence(frame_database: list[dict[str, Any]]) -> dict[str, Any]:
    """Attach additive camera-aware confidence metadata to existing frames."""

    orientation = camera_orientation(frame_database)
    for frame in frame_database:
        frame["camera_orientation"] = orientation
        frame["measurement_confidence"] = {
            signal: _signal_confidence(frame, signal, landmarks, orientation)
            for signal, landmarks in ANGLE_SIGNAL_MAP.items()
        }
    return orientation


def camera_orientation(frame_database: list[dict[str, Any]]) -> dict[str, Any]:
    """Determine one stable camera-facing side from average side visibility."""

    averages = {side: _side_visibility_average(frame_database, side) for side in ("left", "right")}
    left = averages["left"]
    right = averages["right"]
    if left is None and right is None:
        facing = "unknown"
        opposite = "unknown"
    elif right is None or (left is not None and left >= right):
        facing = "left"
        opposite = "right"
    else:
        facing = "right"
        opposite = "left"
    return {
        "camera_facing_side": facing,
        "opposite_side": opposite,
        "side_visibility_averages": averages,
        "landmarks_used": [f"<side>_{name}" for name in CAMERA_SIDE_LANDMARKS],
        "fixed_for_session": True,
        "method": "Average landmark visibility for shoulder, hip, knee, ankle, heel, and foot_index across processed frames; higher side is fixed as camera-facing for the session.",
    }


def confidence_category(score: float | None) -> dict[str, str]:
    """Return clinician-facing confidence category metadata."""

    if score is None or not np.isfinite(score):
        key = "low"
    elif score >= CONFIDENCE_THRESHOLDS["high"]:
        key = "high"
    elif score >= CONFIDENCE_THRESHOLDS["moderate"]:
        key = "moderate"
    elif score >= CONFIDENCE_THRESHOLDS["partial"]:
        key = "partial"
    else:
        key = "low"
    return {
        "key": key,
        "label": CONFIDENCE_LABELS[key],
        "icon": CONFIDENCE_ICONS[key],
    }


def _side_visibility_average(frame_database: list[dict[str, Any]], side: str) -> float | None:
    values: list[float] = []
    names = {f"{side}_{name}" for name in CAMERA_SIDE_LANDMARKS}
    for frame in frame_database:
        for landmark in frame.get("landmarks", []):
            if str(landmark.get("landmark_name")) not in names:
                continue
            value = _float_or_none(landmark.get("visibility"))
            if value is not None:
                values.append(value)
    return None if not values else float(np.mean(values))


def _signal_confidence(
    frame: dict[str, Any],
    signal: str,
    landmarks: tuple[str, str, str],
    orientation: dict[str, Any],
) -> dict[str, Any]:
    lookup = {str(row.get("landmark_name")): row for row in frame.get("landmarks", [])}
    visibility_values = [_float_or_none(lookup.get(name, {}).get("visibility")) for name in landmarks]
    finite_values = [value for value in visibility_values if value is not None]
    score = None if len(finite_values) != len(landmarks) else float(np.mean(finite_values))
    category = confidence_category(score)
    side = _signal_side(signal)
    facing = orientation.get("camera_facing_side")
    if side is None or facing == "unknown":
        limb_role = "Unknown limb role"
    elif side == facing:
        limb_role = "Camera-Facing Limb"
    else:
        limb_role = "Opposite Limb"
    return {
        "score": score,
        "score_percent": None if score is None else round(score * 100, 1),
        "category": category,
        "side": side,
        "limb_role": limb_role,
        "landmarks_used": list(landmarks),
        "landmark_visibilities": {
            name: visibility
            for name, visibility in zip(landmarks, visibility_values, strict=True)
        },
        "calculation": "Mean visibility of the three landmarks used by this joint-angle measurement; no biomechanical values are changed.",
    }


def _signal_side(signal: str) -> str | None:
    if signal.endswith("_left"):
        return "left"
    if signal.endswith("_right"):
        return "right"
    return None


def _float_or_none(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return None if not np.isfinite(number) else number
