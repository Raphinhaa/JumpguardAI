"""Landmark-derived biomechanical feature extraction for uploaded videos."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .feature_engineering import (
    FeatureExtractor as Prompt3FeatureExtractor,
    IDENTIFIER_COLUMNS,
    validate_feature_table,
)
from .features.biomechanics import PRIMARY_JOINT_PAIRS, PRIMARY_JOINT_SIGNALS
from .features.statistical import DESCRIPTORS
from .features.symmetry import absolute_difference, percent_difference, symmetry_index
from .pose_estimation import PoseEstimationResult
from .video_processing import Video


ANGLE_SIGNAL_MAP: dict[str, tuple[str, str, str]] = {
    "hip_flexion_right": ("right_shoulder", "right_hip", "right_knee"),
    "hip_flexion_left": ("left_shoulder", "left_hip", "left_knee"),
    "knee_flexion_right": ("right_hip", "right_knee", "right_ankle"),
    "knee_flexion_left": ("left_hip", "left_knee", "left_ankle"),
    "ankle_angle_right": ("right_knee", "right_ankle", "right_foot_index"),
    "ankle_angle_left": ("left_knee", "left_ankle", "left_foot_index"),
}


@dataclass(frozen=True)
class ExtractionMetadata:
    """Identifier metadata for one uploaded-video feature row."""

    participant_id: int | float = np.nan
    trial_slot: int | float = 1
    trial_name: str = "uploaded_video"
    condition: str = "uploaded"
    is_empty: bool = False


@dataclass(frozen=True)
class LandmarkFeatureResult:
    """Outputs from Prompt 11 landmark-derived feature extraction."""

    feature_table: pd.DataFrame
    joint_angles: pd.DataFrame
    feature_statistics: dict[str, Any]
    symmetry_summary: dict[str, Any]
    landing_events: dict[str, Any]
    trajectory_features: dict[str, Any]


class FeatureExtractionError(ValueError):
    """Raised when landmark-derived feature extraction output is invalid."""


class FeatureExtractor:
    """Extract Prompt-3-compatible features from Prompt 10 landmark outputs.

    The geometric angles are deterministic MediaPipe-derived approximations.
    They are not equivalent to laboratory inverse-kinematics joint angles.
    """

    def __init__(self) -> None:
        self.feature_names = Prompt3FeatureExtractor().feature_names

    def extract(
        self,
        landmark_csv: str | Path,
        *,
        metadata: ExtractionMetadata | None = None,
    ) -> LandmarkFeatureResult:
        """Extract one Prompt-3-compatible feature row from a landmark CSV."""

        landmarks = pd.read_csv(landmark_csv)
        return self.extract_landmarks(landmarks, metadata=metadata)

    def extract_json(
        self,
        landmark_json: str | Path,
        *,
        metadata: ExtractionMetadata | None = None,
    ) -> LandmarkFeatureResult:
        """Extract one feature row from a Prompt 10 landmark JSON file."""

        payload = json.loads(Path(landmark_json).read_text(encoding="utf-8"))
        landmarks = pd.DataFrame(payload["landmarks"])
        return self.extract_landmarks(landmarks, metadata=metadata)

    def extract_video(
        self,
        video: Video,
        *,
        pose_result: PoseEstimationResult | None = None,
        metadata: ExtractionMetadata | None = None,
    ) -> LandmarkFeatureResult:
        """Extract features for a video using an existing Prompt 10 pose result.

        Args:
            video: Prompt 9 Video object, used only for source metadata.
            pose_result: Existing Prompt 10 pose output. This method does not run
                pose estimation itself.
            metadata: Optional output row identifiers.

        Raises:
            FeatureExtractionError: If ``pose_result`` is not supplied.
        """

        if pose_result is None:
            raise FeatureExtractionError(
                "extract_video requires an existing Prompt 10 PoseEstimationResult; "
                "Prompt 11 does not run pose estimation."
            )
        row_metadata = metadata or ExtractionMetadata(trial_name=video.filename)
        return self.extract_landmarks(pose_result.landmarks, metadata=row_metadata)

    def extract_landmarks(
        self,
        landmarks: pd.DataFrame,
        *,
        metadata: ExtractionMetadata | None = None,
    ) -> LandmarkFeatureResult:
        """Extract Prompt-3-compatible features from a landmark DataFrame."""

        _validate_landmarks(landmarks)
        row_metadata = metadata or ExtractionMetadata()
        joint_angles = self.calculate_joint_angles(landmarks)
        temporal = self.calculate_temporal_features(joint_angles)
        symmetry = self.calculate_symmetry(temporal)
        feature_row = self._feature_row(row_metadata, temporal, symmetry)
        feature_table = pd.DataFrame([feature_row], columns=(*IDENTIFIER_COLUMNS, *self.feature_names))
        validate_feature_table(feature_table, self.feature_names)
        landing_events = self._landing_events(joint_angles)
        trajectory = self.calculate_trajectory_features(joint_angles)
        return LandmarkFeatureResult(
            feature_table=feature_table,
            joint_angles=joint_angles,
            feature_statistics=temporal,
            symmetry_summary=symmetry,
            landing_events=landing_events,
            trajectory_features=trajectory,
        )

    def calculate_joint_angles(self, landmarks: pd.DataFrame) -> pd.DataFrame:
        """Calculate deterministic 3D vector-geometry joint angles."""

        _validate_landmarks(landmarks)
        frames = sorted(landmarks["frame_number"].dropna().astype(int).unique())
        rows: list[dict[str, float]] = []
        for frame_number in frames:
            frame = landmarks[landmarks["frame_number"].astype(int).eq(frame_number)]
            timestamp = float(frame["timestamp"].iloc[0])
            row: dict[str, float] = {"frame_number": frame_number, "timestamp": timestamp}
            for signal_key, points in ANGLE_SIGNAL_MAP.items():
                row[signal_key] = _angle_for_points(frame, points)
            rows.append(row)
        return pd.DataFrame(rows)

    def calculate_rom(self, joint_angles: pd.DataFrame) -> dict[str, float]:
        """Calculate range of motion for each angle signal."""

        return {
            signal.key: _finite_descriptor(joint_angles[signal.key].to_numpy(float), "rom")
            for signal in PRIMARY_JOINT_SIGNALS
        }

    def calculate_temporal_features(self, joint_angles: pd.DataFrame) -> dict[str, Any]:
        """Calculate descriptors and time-to-peak for every Prompt 3 signal."""

        statistics: dict[str, Any] = {}
        timestamps = joint_angles["timestamp"].to_numpy(float)
        for signal in PRIMARY_JOINT_SIGNALS:
            values = joint_angles[signal.key].to_numpy(float)
            signal_stats: dict[str, float] = {}
            for descriptor in DESCRIPTORS:
                signal_stats[descriptor] = _finite_descriptor(values, descriptor)
            signal_stats["time_to_peak"] = _time_to_peak(values, timestamps)
            statistics[signal.key] = signal_stats
        return statistics

    def calculate_symmetry(self, feature_statistics: dict[str, Any]) -> dict[str, Any]:
        """Calculate Prompt 3 ROM symmetry features."""

        summary: dict[str, Any] = {}
        label_to_key = {signal.label: signal.key for signal in PRIMARY_JOINT_SIGNALS}
        for pair in PRIMARY_JOINT_PAIRS:
            left_rom = feature_statistics[label_to_key[pair.left_label]]["rom"]
            right_rom = feature_statistics[label_to_key[pair.right_label]]["rom"]
            summary[pair.key] = {
                "rom_absolute_difference": _binary_or_nan(absolute_difference, left_rom, right_rom),
                "rom_percent_difference": _binary_or_nan(percent_difference, left_rom, right_rom),
                "rom_symmetry_index": _binary_or_nan(symmetry_index, left_rom, right_rom),
            }
        return summary

    def calculate_trajectory_features(self, joint_angles: pd.DataFrame) -> dict[str, Any]:
        """Calculate trajectory descriptors without adding Prompt 3 columns."""

        trajectory: dict[str, Any] = {}
        timestamps = joint_angles["timestamp"].to_numpy(float)
        for signal in PRIMARY_JOINT_SIGNALS:
            values = joint_angles[signal.key].to_numpy(float)
            displacement = _safe_displacement(values)
            velocity = _safe_velocity(values, timestamps)
            trajectory[signal.key] = {
                "joint_displacement": displacement,
                "mean_velocity": _nanmean(velocity),
                "max_velocity": _nanmax(velocity),
                "total_path_length": _total_path_length(values),
                "frame_to_frame_movement": _nan_list(np.abs(np.diff(values))),
            }
        return trajectory

    def export(
        self,
        result: LandmarkFeatureResult,
        output_dir: str | Path = "reports/feature_extraction",
    ) -> dict[str, Path]:
        """Export feature table, summaries, landing events, and plots."""

        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        paths = {
            "feature_table_csv": destination / "feature_table.csv",
            "feature_table_json": destination / "feature_table.json",
            "feature_statistics": destination / "feature_statistics.json",
            "symmetry_summary": destination / "symmetry_summary.json",
            "landing_events": destination / "landing_events.json",
            "trajectory_features": destination / "trajectory_features.json",
        }
        result.feature_table.to_csv(paths["feature_table_csv"], index=False, float_format="%.10g")
        paths["feature_table_json"].write_text(
            json.dumps(_json_records(result.feature_table), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        _write_json(paths["feature_statistics"], result.feature_statistics)
        _write_json(paths["symmetry_summary"], result.symmetry_summary)
        _write_json(paths["landing_events"], result.landing_events)
        _write_json(paths["trajectory_features"], result.trajectory_features)
        plot_paths = export_feature_plots(result, destination / "plots")
        paths.update({f"plot_{index}": path for index, path in enumerate(plot_paths)})
        return paths

    def _feature_row(
        self,
        metadata: ExtractionMetadata,
        statistics: dict[str, Any],
        symmetry: dict[str, Any],
    ) -> dict[str, Any]:
        row: dict[str, Any] = {
            "participant_id": metadata.participant_id,
            "trial_slot": metadata.trial_slot,
            "trial_name": metadata.trial_name,
            "condition": metadata.condition,
            "is_empty": metadata.is_empty,
        }
        for signal in PRIMARY_JOINT_SIGNALS:
            for descriptor in (*DESCRIPTORS, "time_to_peak"):
                row[f"{signal.key}_{descriptor}"] = statistics[signal.key][descriptor]
        for pair in PRIMARY_JOINT_PAIRS:
            for metric in (
                "rom_absolute_difference",
                "rom_percent_difference",
                "rom_symmetry_index",
            ):
                row[f"{pair.key}_{metric}"] = symmetry[pair.key][metric]
        return row

    def _landing_events(self, joint_angles: pd.DataFrame) -> dict[str, Any]:
        return {
            "beginning_frame": None,
            "end_frame": None,
            "landing_duration": None,
            "peak_flexion_frame": _peak_flexion_frame(joint_angles),
            "method": (
                "No robust landing event detector is defined for Prompt 11 landmarks. "
                "Beginning, end, and duration are preserved as missing."
            ),
        }


def export_feature_plots(
    result: LandmarkFeatureResult,
    output_dir: str | Path,
) -> list[Path]:
    """Export preview, joint-angle, ROM, and symmetry plots."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    plotters = {
        "joint_angles.png": lambda: plot_joint_angles(result.joint_angles),
        "rom.png": lambda: plot_rom(result.feature_statistics),
        "symmetry.png": lambda: plot_symmetry(result.symmetry_summary),
        "feature_preview.png": lambda: plot_feature_preview(result.feature_table),
    }
    paths: list[Path] = []
    for filename, plotter in plotters.items():
        figure, _ = plotter()
        path = destination / filename
        figure.savefig(path, dpi=140, bbox_inches="tight", metadata={"Software": "JumpGuardAI"})
        plt.close(figure)
        paths.append(path)
    return paths


def plot_joint_angles(joint_angles: pd.DataFrame) -> tuple[Figure, Axes]:
    """Plot landmark-derived joint-angle trajectories."""

    figure, axes = plt.subplots(figsize=(9.0, 5.2))
    for signal in PRIMARY_JOINT_SIGNALS:
        axes.plot(joint_angles["timestamp"], joint_angles[signal.key], label=signal.key)
    axes.set(
        title="MediaPipe-derived geometric joint angles",
        xlabel="Time (s)",
        ylabel="Angle (degrees)",
    )
    axes.legend(frameon=False, fontsize=8, ncols=2)
    _style_axes(axes)
    figure.tight_layout()
    return figure, axes


def plot_rom(feature_statistics: dict[str, Any]) -> tuple[Figure, Axes]:
    """Plot ROM values by signal."""

    labels = [signal.key for signal in PRIMARY_JOINT_SIGNALS]
    values = [feature_statistics[label]["rom"] for label in labels]
    figure, axes = plt.subplots(figsize=(8.5, 4.6))
    axes.bar(labels, values, color="#2C7FB8")
    axes.set(title="Range of motion", ylabel="Degrees")
    axes.tick_params(axis="x", rotation=45)
    _style_axes(axes)
    figure.tight_layout()
    return figure, axes


def plot_symmetry(symmetry_summary: dict[str, Any]) -> tuple[Figure, Axes]:
    """Plot ROM absolute-difference symmetry values."""

    labels = list(symmetry_summary)
    values = [symmetry_summary[label]["rom_absolute_difference"] for label in labels]
    figure, axes = plt.subplots(figsize=(7.5, 4.4))
    axes.bar(labels, values, color="#4D9221")
    axes.set(title="ROM symmetry absolute differences", ylabel="Degrees")
    _style_axes(axes)
    figure.tight_layout()
    return figure, axes


def plot_feature_preview(feature_table: pd.DataFrame) -> tuple[Figure, Axes]:
    """Plot first-row non-missing feature values."""

    numeric = feature_table.drop(columns=list(IDENTIFIER_COLUMNS)).iloc[0].dropna()
    figure, axes = plt.subplots(figsize=(9.0, 4.8))
    preview = numeric.head(20)
    axes.bar(preview.index, preview.to_numpy(float), color="#756BB1")
    axes.set(title="Feature preview", ylabel="Value")
    axes.tick_params(axis="x", rotation=75, labelsize=7)
    _style_axes(axes)
    figure.tight_layout()
    return figure, axes


def _validate_landmarks(landmarks: pd.DataFrame) -> None:
    required = {
        "frame_number",
        "timestamp",
        "landmark_name",
        "x",
        "y",
        "z",
    }
    missing = required - set(landmarks.columns)
    if missing:
        raise FeatureExtractionError(f"Landmark table is missing columns: {sorted(missing)}")


def _angle_for_points(frame: pd.DataFrame, points: tuple[str, str, str]) -> float:
    first, middle, last = (_point(frame, name) for name in points)
    if any(point is None for point in (first, middle, last)):
        return float("nan")
    assert first is not None and middle is not None and last is not None
    if points[0].endswith("shoulder"):
        vector_a = middle - first
        vector_b = last - middle
    elif points[2].endswith("foot_index"):
        vector_a = middle - first
        vector_b = last - middle
    else:
        vector_a = first - middle
        vector_b = last - middle
    return _angle_between(vector_a, vector_b)


def _point(frame: pd.DataFrame, name: str) -> np.ndarray | None:
    row = frame[frame["landmark_name"].eq(name)]
    if row.empty:
        return None
    values = row.iloc[0][["x", "y", "z"]].to_numpy(dtype=float)
    return None if not np.isfinite(values).all() else values


def _angle_between(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    norm = float(np.linalg.norm(vector_a) * np.linalg.norm(vector_b))
    if norm == 0.0 or not np.isfinite(norm):
        return float("nan")
    cosine = float(np.dot(vector_a, vector_b) / norm)
    return float(np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0))))


def _finite_descriptor(values: np.ndarray, descriptor: str) -> float:
    valid = values[np.isfinite(values)]
    if valid.size == 0:
        return float("nan")
    if descriptor == "mean":
        return float(np.mean(valid))
    if descriptor == "median":
        return float(np.median(valid))
    if descriptor == "std":
        return float(np.std(valid, ddof=0))
    if descriptor == "variance":
        return float(np.var(valid, ddof=0))
    if descriptor == "maximum":
        return float(np.max(valid))
    if descriptor == "minimum":
        return float(np.min(valid))
    if descriptor == "rom":
        return float(np.max(valid) - np.min(valid))
    raise ValueError(f"Unknown descriptor: {descriptor}")


def _time_to_peak(values: np.ndarray, timestamps: np.ndarray) -> float:
    valid = np.isfinite(values) & np.isfinite(timestamps)
    if not valid.any():
        return float("nan")
    valid_values = values[valid]
    valid_timestamps = timestamps[valid]
    peak_index = int(np.argmax(valid_values))
    return float(valid_timestamps[peak_index] - valid_timestamps[0])


def _binary_or_nan(function: Any, left: float, right: float) -> float:
    if not np.isfinite(left) or not np.isfinite(right):
        return float("nan")
    return float(function(left, right))


def _safe_displacement(values: np.ndarray) -> float:
    valid = values[np.isfinite(values)]
    return float(valid[-1] - valid[0]) if valid.size >= 2 else float("nan")


def _safe_velocity(values: np.ndarray, timestamps: np.ndarray) -> np.ndarray:
    if values.size < 2:
        return np.asarray([], dtype=float)
    delta_t = np.diff(timestamps)
    delta_v = np.diff(values)
    with np.errstate(divide="ignore", invalid="ignore"):
        velocity = delta_v / delta_t
    velocity[~np.isfinite(velocity)] = np.nan
    return velocity


def _total_path_length(values: np.ndarray) -> float:
    movement = np.abs(np.diff(values))
    movement = movement[np.isfinite(movement)]
    return float(np.sum(movement)) if movement.size else float("nan")


def _nanmean(values: np.ndarray) -> float:
    return float(np.nanmean(values)) if np.isfinite(values).any() else float("nan")


def _nanmax(values: np.ndarray) -> float:
    return float(np.nanmax(values)) if np.isfinite(values).any() else float("nan")


def _nan_list(values: np.ndarray) -> list[float | None]:
    return [None if not np.isfinite(value) else float(value) for value in values]


def _peak_flexion_frame(joint_angles: pd.DataFrame) -> int | None:
    candidates = [column for column in joint_angles.columns if column.startswith("knee_flexion")]
    if not candidates:
        return None
    mean_signal = joint_angles[candidates].mean(axis=1, skipna=True)
    if mean_signal.isna().all():
        return None
    return int(joint_angles.loc[mean_signal.idxmax(), "frame_number"])


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _json_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return _json_ready(frame.to_dict(orient="records"))


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return None if np.isnan(value) else float(value)
    if isinstance(value, float) and np.isnan(value):
        return None
    return value


def _style_axes(ax: Axes) -> None:
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.7, alpha=0.75)
    ax.spines[["top", "right"]].set_visible(False)
