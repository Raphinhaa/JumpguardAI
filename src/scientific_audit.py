"""Read-only scientific audit utilities for biomechanical measurements.

Prompt 14 audit code consumes existing pipeline artifacts and exports
traceability documentation. It does not change pose estimation, feature
extraction, evidence interpretation, reports, dashboards, or JSON schemas.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any

import json

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .feature_extraction import ANGLE_SIGNAL_MAP, FeatureExtractor as LandmarkFeatureExtractor
from .feature_engineering import FeatureExtractor as DatasetFeatureExtractor
from .features.biomechanics import PRIMARY_JOINT_PAIRS, PRIMARY_JOINT_SIGNALS
from .features.statistical import DESCRIPTORS
from .pose_estimation import annotate_frame
from .video_processing import Video


ANGLE_SOURCE_LOCATION = "src/feature_extraction.py:ANGLE_SIGNAL_MAP,_angle_for_points,_angle_between"
FEATURE_SOURCE_LOCATION = "src/feature_extraction.py:FeatureExtractor.calculate_temporal_features,_feature_row"
DATASET_FEATURE_SOURCE_LOCATION = "src/feature_engineering.py:FeatureExtractor.extract,_build_feature_definitions"
SYMMETRY_SOURCE_LOCATION = "src/features/symmetry.py:absolute_difference,percent_difference,symmetry_index"


@dataclass(frozen=True)
class ScientificAuditPaths:
    """Paths written by the Prompt 14 audit exporter."""

    angle_audit: Path
    feature_audit: Path
    dependency_graph: Path
    code_traceability: Path
    frame_provenance: Path
    measurement_timeline: Path
    measurement_audit_index: Path
    measurement_images: list[Path]


def generate_scientific_audit(
    run_dir: str | Path = "reports/run_prompt13_evidence",
    *,
    docs_dir: str | Path = "docs",
) -> ScientificAuditPaths:
    """Generate Prompt 14 documentation and run-local audit artifacts."""

    run_path = Path(run_dir)
    docs_path = Path(docs_dir)
    docs_path.mkdir(parents=True, exist_ok=True)
    landmarks = pd.read_csv(run_path / "landmarks" / "landmarks.csv")
    feature_table = pd.read_csv(run_path / "features" / "feature_table.csv")
    metadata = json.loads((run_path / "metadata.json").read_text(encoding="utf-8"))
    video = Video(metadata["video"]["path"])
    extractor = LandmarkFeatureExtractor()
    joint_angles = extractor.calculate_joint_angles(landmarks)
    provenance = build_frame_provenance(joint_angles, feature_table)
    timeline = build_measurement_timeline(joint_angles, provenance)
    audit_dir = run_path / "measurement_audit"
    images = export_measurement_audit_images(video, landmarks, joint_angles, feature_table, audit_dir)

    angle_path = docs_path / "ANGLE_DEFINITION_AUDIT.md"
    feature_path = docs_path / "FEATURE_DEFINITION_AUDIT.md"
    dependency_path = docs_path / "PIPELINE_DEPENDENCY_GRAPH.md"
    traceability_path = docs_path / "CODE_TRACEABILITY.md"
    provenance_path = run_path / "frame_provenance.json"
    timeline_path = run_path / "measurement_timeline.csv"
    index_path = audit_dir / "index.html"

    angle_path.write_text(render_angle_definition_audit(), encoding="utf-8")
    feature_path.write_text(render_feature_definition_audit(), encoding="utf-8")
    dependency_path.write_text(render_dependency_graph(), encoding="utf-8")
    traceability_path.write_text(render_code_traceability(), encoding="utf-8")
    provenance_path.write_text(json.dumps(_json_ready(provenance), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    pd.DataFrame(timeline).to_csv(timeline_path, index=False, float_format="%.10g")
    index_path.write_text(render_measurement_audit_index(images), encoding="utf-8")
    return ScientificAuditPaths(
        angle_audit=angle_path,
        feature_audit=feature_path,
        dependency_graph=dependency_path,
        code_traceability=traceability_path,
        frame_provenance=provenance_path,
        measurement_timeline=timeline_path,
        measurement_audit_index=index_path,
        measurement_images=images,
    )


def build_frame_provenance(
    joint_angles: pd.DataFrame,
    feature_table: pd.DataFrame,
) -> list[dict[str, Any]]:
    """Return frame-level traceability records for every Prompt-11 feature."""

    row = feature_table.iloc[0]
    records: list[dict[str, Any]] = []
    for signal in PRIMARY_JOINT_SIGNALS:
        values = joint_angles[signal.key].to_numpy(float)
        timestamps = joint_angles["timestamp"].to_numpy(float)
        frames = joint_angles["frame_number"].astype(int).to_numpy()
        valid_mask = np.isfinite(values)
        valid_frames = frames[valid_mask].astype(int).tolist()
        valid_timestamps = timestamps[valid_mask].astype(float).tolist()
        for descriptor in (*DESCRIPTORS, "time_to_peak"):
            feature = f"{signal.key}_{descriptor}"
            source = _descriptor_source(descriptor, values, timestamps, frames)
            records.append(
                {
                    "feature": feature,
                    "feature_value": _maybe_float(row.get(feature)),
                    "source_signal": signal.key,
                    "source_angle_columns": [signal.key],
                    "landmarks_used": list(ANGLE_SIGNAL_MAP[signal.key]),
                    "aggregation_method": _descriptor_method(descriptor),
                    "aggregation_window": "full processed recording; all finite frames for the source signal",
                    "event_label": "none; no landing phase detector is defined",
                    "representative_frame_index": source["representative_frame_index"],
                    "representative_timestamp": source["representative_timestamp"],
                    "source_frame_indices": valid_frames,
                    "source_timestamps": valid_timestamps,
                    "source_code": FEATURE_SOURCE_LOCATION,
                    "notes": source["notes"],
                }
            )
    for pair in PRIMARY_JOINT_PAIRS:
        left_key = _label_to_key(pair.left_label)
        right_key = _label_to_key(pair.right_label)
        left_source = _rom_source(joint_angles, left_key)
        right_source = _rom_source(joint_angles, right_key)
        combined_frames = sorted(set(left_source["source_frame_indices"] + right_source["source_frame_indices"]))
        for metric in ("rom_absolute_difference", "rom_percent_difference", "rom_symmetry_index"):
            feature = f"{pair.key}_{metric}"
            records.append(
                {
                    "feature": feature,
                    "feature_value": _maybe_float(row.get(feature)),
                    "source_signal": pair.key,
                    "source_angle_columns": [left_key, right_key],
                    "landmarks_used": list(ANGLE_SIGNAL_MAP[left_key] + ANGLE_SIGNAL_MAP[right_key]),
                    "aggregation_method": _symmetry_method(metric),
                    "aggregation_window": "full processed recording; left and right ROM values computed from finite frames",
                    "event_label": "none; no landing phase detector is defined",
                    "representative_frame_index": combined_frames[0] if combined_frames else None,
                    "representative_timestamp": _timestamp_for_frame(joint_angles, combined_frames[0]) if combined_frames else None,
                    "source_frame_indices": combined_frames,
                    "source_timestamps": [_timestamp_for_frame(joint_angles, frame) for frame in combined_frames],
                    "source_code": SYMMETRY_SOURCE_LOCATION,
                    "notes": "Bilateral feature derived from left/right ROM extrema; no single anatomical angle equals this scalar.",
                }
            )
    return records


def build_measurement_timeline(
    joint_angles: pd.DataFrame,
    provenance: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Build a transparent event timeline from existing computed measurements."""

    rows: list[dict[str, Any]] = [
        {
            "event": "initial_contact",
            "frame_number": None,
            "timestamp": None,
            "source_feature": None,
            "value": None,
            "status": "unavailable",
            "method": "No documented initial-contact detector exists in the current pipeline.",
        },
        {
            "event": "peak_landing",
            "frame_number": None,
            "timestamp": None,
            "source_feature": None,
            "value": None,
            "status": "unavailable",
            "method": "No documented landing-phase or peak-landing detector exists in the current pipeline.",
        },
    ]
    for family, label in (
        ("knee_flexion", "maximum_knee_flexion"),
        ("hip_flexion", "maximum_hip_flexion"),
        ("ankle_angle", "maximum_ankle_angle"),
    ):
        candidates = [record for record in provenance if record["feature"].startswith(family) and record["feature"].endswith("maximum")]
        for record in candidates:
            rows.append(
                {
                    "event": label,
                    "frame_number": record["representative_frame_index"],
                    "timestamp": record["representative_timestamp"],
                    "source_feature": record["feature"],
                    "value": record["feature_value"],
                    "status": "computed",
                    "method": "Frame of first finite maximum for this joint-angle signal.",
                }
            )
    knee_columns = [column for column in joint_angles.columns if column.startswith("knee_flexion")]
    if knee_columns:
        mean_signal = joint_angles[knee_columns].mean(axis=1, skipna=True)
        if not mean_signal.isna().all():
            idx = int(mean_signal.idxmax())
            rows.append(
                {
                    "event": "peak_mean_knee_flexion_frame",
                    "frame_number": int(joint_angles.loc[idx, "frame_number"]),
                    "timestamp": float(joint_angles.loc[idx, "timestamp"]),
                    "source_feature": "mean(knee_flexion_left,knee_flexion_right)",
                    "value": float(mean_signal.loc[idx]),
                    "status": "computed",
                    "method": "Existing landing_events peak_flexion_frame logic: maximum row-wise mean of knee flexion columns.",
                }
            )
    return rows


def export_measurement_audit_images(
    video: Video,
    landmarks: pd.DataFrame,
    joint_angles: pd.DataFrame,
    feature_table: pd.DataFrame,
    output_dir: str | Path,
) -> list[Path]:
    """Export source-frame overlays for frame-specific angle extrema."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    row = feature_table.iloc[0]
    paths: list[Path] = []
    for signal in PRIMARY_JOINT_SIGNALS:
        for descriptor in ("maximum", "minimum"):
            feature = f"{signal.key}_{descriptor}"
            source = _descriptor_source(
                descriptor,
                joint_angles[signal.key].to_numpy(float),
                joint_angles["timestamp"].to_numpy(float),
                joint_angles["frame_number"].astype(int).to_numpy(),
            )
            frame_index = source["representative_frame_index"]
            if frame_index is None:
                continue
            feature_value = float(row[feature])
            frame = video.get_frame(int(frame_index))
            frame_landmarks = landmarks[landmarks["frame_number"].astype(int).eq(int(frame_index))]
            annotated = _measurement_overlay(
                frame,
                frame_landmarks,
                signal.key,
                feature,
                feature_value,
                float(source["representative_timestamp"]),
            )
            path = destination / f"{feature}_frame_{int(frame_index):04d}.png"
            if not cv2.imwrite(str(path), annotated):
                raise RuntimeError(f"Could not write measurement audit image: {path}")
            paths.append(path)
    return paths


def render_angle_definition_audit() -> str:
    """Render docs/ANGLE_DEFINITION_AUDIT.md."""

    rows = [
        "# Angle Definition Audit",
        "",
        "This audit documents the existing uploaded-video angle implementation. These angles are MediaPipe-derived geometric approximations from normalized 3D landmark coordinates `(x, y, z)`. They are not laboratory inverse-kinematics joint angles.",
        "",
        "## Shared Calculation",
        "",
        "- Source code: `src/feature_extraction.py`, `ANGLE_SIGNAL_MAP`, `_angle_for_points`, `_angle_between`.",
        "- Coordinate system: MediaPipe normalized image/world-like landmark coordinates exported by Prompt 10: `x`, `y`, `z`; overlay drawing uses `x` and `y` scaled to video pixels only for visualization.",
        "- Units: degrees.",
        "- Formula: `degrees(arccos(clip(dot(a,b) / (||a|| ||b||), -1, 1)))`.",
        "- Valid numeric range from arccos: 0 to 180 degrees.",
        "- Missing behavior: if any required landmark is missing, nonfinite, or a vector has zero norm, the angle is `NaN`.",
        "- Landing phase: no landing phase is detected; angles are computed for every processed frame.",
        "",
        "## Joint Definitions",
        "",
        "| Signal | Side | Joint | Landmarks | Vectors Used | Convention | Transformations | Source |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for signal in PRIMARY_JOINT_SIGNALS:
        first, middle, last = ANGLE_SIGNAL_MAP[signal.key]
        if first.endswith("shoulder") or last.endswith("foot_index"):
            vectors = f"{middle} - {first}; {last} - {middle}"
        else:
            vectors = f"{first} - {middle}; {last} - {middle}"
        rows.append(
            f"| `{signal.key}` | {signal.side} | {signal.joint} | `{first}` -> `{middle}` -> `{last}` | `{vectors}` | Internal geometric angle between the two vectors listed | None; no `180 - angle` transform is applied | `{ANGLE_SOURCE_LOCATION}` |"
        )
    rows.extend(
        [
            "",
            "## Validation Notes",
            "",
            "The code does not apply clinical sign conventions, anatomical coordinate transformations, inverse-kinematics model constraints, or event segmentation. Therefore these measurements should be interpreted as deterministic MediaPipe landmark geometry only.",
        ]
    )
    return "\n".join(rows) + "\n"


def render_feature_definition_audit() -> str:
    """Render docs/FEATURE_DEFINITION_AUDIT.md."""

    definitions = DatasetFeatureExtractor().definitions
    rows = [
        "# Feature Definition Audit",
        "",
        "All Prompt 3 and Prompt 11 feature names are preserved exactly. Uploaded-video Prompt 11 features reuse the same names as the dataset feature framework but source the six primary signals from MediaPipe-derived geometric angles.",
        "",
        "Landing phase: the current implementation computes all descriptors over the full processed recording. `landing_events.json` preserves beginning/end/duration as missing because no robust landing event detector is defined.",
        "",
        "| Feature | Human-readable description | Mathematical definition | Source angles | Aggregation method | Landing phase | Units | Expected range | Source code |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for definition in definitions:
        source_angles = _source_angles_for_feature(definition.name)
        rows.append(
            "| "
            f"`{_md_cell(definition.name)}` | {_md_cell(definition.description)} | `{_md_cell(definition.formula)}` | {_md_cell(source_angles)} | {_md_cell(_aggregation_for_feature(definition.name))} | Full processed recording | {_md_cell(definition.units)} | {_md_cell(_expected_range(definition.name, definition.units))} | `{_md_cell(_source_for_feature(definition.name))}` |"
        )
    rows.extend(
        [
            "",
            "## Missing Values",
            "",
            "Empty trials, unavailable labels, missing landmarks, nonfinite angle values, or zero-length vectors propagate to `NaN`. Symmetry percent metrics are also `NaN` when both side magnitudes are zero.",
        ]
    )
    return "\n".join(rows) + "\n"


def render_dependency_graph() -> str:
    """Render docs/PIPELINE_DEPENDENCY_GRAPH.md."""

    return """# Pipeline Dependency Graph

```text
Video file
  -> src.video_processing.Video
     validates extension, metadata, fps, frame count, frame access
  -> src.pose_estimation.MediaPipePoseEstimator
     converts each BGR frame to RGB and exports 33 MediaPipe pose landmarks per processed frame
  -> landmarks.csv / landmarks.json
     frame_number, timestamp, landmark_index, landmark_name, x, y, z, visibility, confidence
  -> src.feature_extraction.FeatureExtractor.calculate_joint_angles
     computes six MediaPipe-derived geometric angle trajectories from documented landmark triplets
  -> src.feature_extraction.FeatureExtractor.calculate_temporal_features
     computes full-recording descriptors and time-to-peak for each angle trajectory
  -> src.feature_extraction.FeatureExtractor.calculate_symmetry
     computes bilateral ROM absolute difference, percent difference, and symmetry index
  -> feature_table.csv / feature_table.json
     one Prompt-3-compatible row for the uploaded video
  -> src.evidence_interpretation.load_reference_feature_table
     loads data/processed/features.csv as the reference feature table when present
  -> src.evidence_interpretation.EvidenceBasedInterpreter
     computes dataset-relative percentiles, z-scores, p05/p95, and evidence-backed non-diagnostic observations
  -> athlete_report / dashboard
     renders existing pipeline outputs without changing measurements
```

## Dataset Reference Path

```text
DJ.mat + metadata workbooks
  -> Dataset / Participant / Trial abstractions
  -> src.feature_engineering.FeatureExtractor
     extracts the same 57 feature names from laboratory joint-angle labels over full recordings
  -> data/processed/features.csv
  -> src.biomechanical_intelligence
     participant-level means, population statistics, athlete percentiles, descriptive observations
  -> Prompt 13 evidence engine and athlete reporting layers
```

No dependency in this graph performs ACL diagnosis, injury prediction, probability estimation, or clinical scoring.
"""


def render_code_traceability() -> str:
    """Render docs/CODE_TRACEABILITY.md."""

    rows = [
        "# Code Traceability",
        "",
        "## Stage Traceability",
        "",
        "| Stage | Source file/function | Upstream inputs | Downstream outputs | Notes |",
        "|---|---|---|---|---|",
        "| Video loading | `src/video_processing.py:Video` | Source `.mp4`, `.mov`, or `.avi` | Validated metadata and frame access | No event detection or pixel modification in base iterator |",
        "| Pose estimation | `src/pose_estimation.py:MediaPipePoseEstimator.estimate` | `Video` frames | `PoseEstimationResult.landmarks` | Timestamps are `frame_number / video.fps` |",
        "| Landmark export | `src/pose_estimation.py:PoseEstimator.export_landmarks` | `PoseEstimationResult` | `landmarks.csv`, `landmarks.json` | Schema is validated for 33 landmarks per processed frame |",
        "| Angle calculation | `src/feature_extraction.py:FeatureExtractor.calculate_joint_angles` | Landmark table | Six joint-angle trajectories | Uses `ANGLE_SIGNAL_MAP` and `_angle_between` |",
        "| Temporal features | `src/feature_extraction.py:FeatureExtractor.calculate_temporal_features` | Joint-angle trajectories | Mean, median, std, variance, max, min, ROM, time-to-peak | Full processed recording; finite values only |",
        "| Symmetry features | `src/feature_extraction.py:FeatureExtractor.calculate_symmetry`; `src/features/symmetry.py` | Left/right ROM values | Absolute difference, percent difference, symmetry index | No clinical threshold |",
        "| Feature schema validation | `src/feature_engineering.py:validate_feature_table` | Feature table | Validated Prompt-3-compatible columns | Preserves existing names and order |",
        "| Reference loading | `src/evidence_interpretation.py:load_reference_feature_table` | `data/processed/features.csv` | Reference feature table | Used when present for run-local evidence comparisons |",
        "| Evidence comparison | `src/evidence_interpretation.py:EvidenceBasedInterpreter._compare_feature_table` | Uploaded features + reference table | Percentiles, z-scores, mean, std, p05, p95 | Dataset-relative descriptive comparison only |",
        "| Athlete report rendering | `src/reporting.py`; `src/evidence_report_rendering.py` | Existing outputs | Markdown/HTML/JSON reports | Rendering only; no measurement changes |",
        "",
        "## Feature-Level Traceability",
        "",
        "| Feature | Upstream inputs | Computation | Downstream outputs | Source location |",
        "|---|---|---|---|---|",
    ]
    for definition in DatasetFeatureExtractor().definitions:
        rows.append(
            f"| `{_md_cell(definition.name)}` | {_md_cell(_source_angles_for_feature(definition.name))} | `{_md_cell(definition.formula)}` | feature table, evidence comparison, athlete reports, dashboards | `{_md_cell(_source_for_feature(definition.name))}` |"
        )
    rows.extend(
        [
            "",
            "## Duplicate Computation Audit",
            "",
            "The uploaded-video pipeline has one canonical feature extraction path: `src.feature_extraction.FeatureExtractor`. The dataset feature framework in `src.feature_engineering.FeatureExtractor` defines the original Prompt 3 schema and formulas for MATLAB joint-angle trials. Prompt 11 reuses the names and formulas, while changing only the upstream source of the six angle signals to documented MediaPipe landmark geometry. This is intentional compatibility, not a duplicate downstream calculation.",
        ]
    )
    return "\n".join(rows) + "\n"


def render_measurement_audit_index(images: list[Path]) -> str:
    """Render the run-local visual measurement audit index."""

    cards = []
    for path in sorted(images, key=lambda item: item.name):
        cards.append(
            f"<figure><img src=\"{escape(path.name)}\" alt=\"{escape(path.stem)}\"><figcaption>{escape(path.stem)}</figcaption></figure>"
        )
    return (
        "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        "<title>Prompt 14 Measurement Audit</title>"
        "<style>body{font-family:Arial,sans-serif;margin:28px;background:#f7f9fb;color:#1f2933;}"
        "main{max-width:1180px;margin:auto;}figure{background:white;border:1px solid #d9e2ec;border-radius:8px;padding:12px;}"
        "img{max-width:100%;height:auto;display:block;}section{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px;}"
        "figcaption{font-size:13px;color:#52606d;margin-top:8px;}</style></head><body><main>"
        "<h1>Prompt 14 Measurement Audit</h1>"
        "<p>Images show frame-specific maximum/minimum source angles. Aggregate features are traced in frame_provenance.json because no single frame can visually equal an aggregate statistic.</p>"
        "<section>"
        + "".join(cards)
        + "</section></main></body></html>\n"
    )


def _measurement_overlay(
    frame: np.ndarray,
    frame_landmarks: pd.DataFrame,
    signal: str,
    feature: str,
    feature_value: float,
    timestamp: float,
) -> np.ndarray:
    annotated = annotate_frame(frame, frame_landmarks)
    height, width = annotated.shape[:2]
    points = _pixel_points(frame_landmarks, width, height)
    names = ANGLE_SIGNAL_MAP[signal]
    if all(name in points for name in names):
        p1, p2, p3 = (points[name] for name in names)
        cv2.line(annotated, p1, p2, (255, 0, 255), 3)
        cv2.line(annotated, p2, p3, (255, 0, 255), 3)
        for point in (p1, p2, p3):
            cv2.circle(annotated, point, 7, (0, 0, 255), -1)
    frame_number = int(frame_landmarks["frame_number"].iloc[0]) if not frame_landmarks.empty else -1
    lines = [
        feature,
        f"frame={frame_number} time={timestamp:.4f}s",
        f"stored value={feature_value:.4f} deg",
        "MediaPipe geometric approximation",
    ]
    y = 28
    for line in lines:
        cv2.putText(annotated, line, (16, y), cv2.FONT_HERSHEY_SIMPLEX, 0.68, (0, 0, 0), 5, cv2.LINE_AA)
        cv2.putText(annotated, line, (16, y), cv2.FONT_HERSHEY_SIMPLEX, 0.68, (255, 255, 255), 2, cv2.LINE_AA)
        y += 28
    return annotated


def _md_cell(value: Any) -> str:
    return str(value).replace("|", "\\|")


def _pixel_points(frame_landmarks: pd.DataFrame, width: int, height: int) -> dict[str, tuple[int, int]]:
    points: dict[str, tuple[int, int]] = {}
    for _, row in frame_landmarks.dropna(subset=["x", "y"]).iterrows():
        points[str(row["landmark_name"])] = (int(float(row["x"]) * width), int(float(row["y"]) * height))
    return points


def _descriptor_source(
    descriptor: str,
    values: np.ndarray,
    timestamps: np.ndarray,
    frames: np.ndarray,
) -> dict[str, Any]:
    valid = np.isfinite(values) & np.isfinite(timestamps)
    if not valid.any():
        return {"representative_frame_index": None, "representative_timestamp": None, "notes": "No finite source frames."}
    valid_values = values[valid]
    valid_timestamps = timestamps[valid]
    valid_frames = frames[valid]
    if descriptor in {"maximum", "time_to_peak"}:
        idx = int(np.argmax(valid_values))
        note = "First finite maximum frame."
    elif descriptor == "minimum":
        idx = int(np.argmin(valid_values))
        note = "First finite minimum frame."
    elif descriptor == "median":
        median = float(np.median(valid_values))
        idx = int(np.argmin(np.abs(valid_values - median)))
        note = "Representative frame nearest the median; statistic uses all finite frames."
    elif descriptor == "mean":
        mean = float(np.mean(valid_values))
        idx = int(np.argmin(np.abs(valid_values - mean)))
        note = "Representative frame nearest the mean; statistic uses all finite frames."
    else:
        idx = 0
        note = "Aggregate statistic uses all finite frames; representative frame is first finite source frame."
    return {
        "representative_frame_index": int(valid_frames[idx]),
        "representative_timestamp": float(valid_timestamps[idx]),
        "notes": note,
    }


def _rom_source(joint_angles: pd.DataFrame, signal: str) -> dict[str, Any]:
    values = joint_angles[signal].to_numpy(float)
    frames = joint_angles["frame_number"].astype(int).to_numpy()
    valid = np.isfinite(values)
    if not valid.any():
        return {"source_frame_indices": []}
    valid_values = values[valid]
    valid_frames = frames[valid]
    return {"source_frame_indices": sorted({int(valid_frames[int(np.argmax(valid_values))]), int(valid_frames[int(np.argmin(valid_values))])})}


def _descriptor_method(descriptor: str) -> str:
    return {
        "mean": "arithmetic mean of finite source angles",
        "median": "median of finite source angles",
        "std": "population standard deviation of finite source angles, ddof=0",
        "variance": "population variance of finite source angles, ddof=0",
        "maximum": "maximum finite source angle",
        "minimum": "minimum finite source angle",
        "rom": "maximum finite source angle minus minimum finite source angle",
        "time_to_peak": "timestamp of first maximum finite source angle minus first finite timestamp",
    }[descriptor]


def _symmetry_method(metric: str) -> str:
    return {
        "rom_absolute_difference": "abs(left_ROM - right_ROM)",
        "rom_percent_difference": "100 * abs(left_ROM - right_ROM) / ((abs(left_ROM)+abs(right_ROM))/2)",
        "rom_symmetry_index": "100 * (left_ROM - right_ROM) / ((abs(left_ROM)+abs(right_ROM))/2)",
    }[metric]


def _label_to_key(label: str) -> str:
    lookup = {signal.label: signal.key for signal in PRIMARY_JOINT_SIGNALS}
    return lookup[label]


def _timestamp_for_frame(joint_angles: pd.DataFrame, frame: int) -> float | None:
    row = joint_angles[joint_angles["frame_number"].astype(int).eq(int(frame))]
    return None if row.empty else float(row["timestamp"].iloc[0])


def _source_angles_for_feature(feature: str) -> str:
    for signal in PRIMARY_JOINT_SIGNALS:
        if feature.startswith(signal.key):
            return f"`{signal.key}` from `{ANGLE_SIGNAL_MAP[signal.key][0]}` -> `{ANGLE_SIGNAL_MAP[signal.key][1]}` -> `{ANGLE_SIGNAL_MAP[signal.key][2]}`"
    for pair in PRIMARY_JOINT_PAIRS:
        if feature.startswith(pair.key):
            return f"left/right ROM from `{_label_to_key(pair.left_label)}` and `{_label_to_key(pair.right_label)}`"
    return "unknown"


def _aggregation_for_feature(feature: str) -> str:
    for descriptor in (*DESCRIPTORS, "time_to_peak"):
        if feature.endswith(descriptor):
            return _descriptor_method(descriptor)
    for metric in ("rom_absolute_difference", "rom_percent_difference", "rom_symmetry_index"):
        if feature.endswith(metric):
            return _symmetry_method(metric)
    return "unknown"


def _expected_range(feature: str, units: str) -> str:
    if units == "degrees²":
        return ">= 0"
    if feature.endswith("std") or feature.endswith("rom") or feature.endswith("absolute_difference") or feature.endswith("percent_difference"):
        return ">= 0"
    if feature.endswith("symmetry_index"):
        return "signed percent; unbounded by formula"
    if feature.endswith("time_to_peak"):
        return ">= 0 seconds within processed recording"
    return "0 to 180 degrees for source geometric angles; aggregates remain within finite source-angle range except variance/std"


def _source_for_feature(feature: str) -> str:
    if "absolute_difference" in feature or "percent_difference" in feature or "symmetry_index" in feature:
        return SYMMETRY_SOURCE_LOCATION
    return f"{FEATURE_SOURCE_LOCATION}; dataset schema: {DATASET_FEATURE_SOURCE_LOCATION}"


def _maybe_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return None if np.isnan(number) else number


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


if __name__ == "__main__":
    paths = generate_scientific_audit()
    print(json.dumps({key: str(value) for key, value in paths.__dict__.items() if key != "measurement_images"}, indent=2))
    print(f"measurement_images: {len(paths.measurement_images)}")
