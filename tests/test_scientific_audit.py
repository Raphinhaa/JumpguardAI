"""Tests for Prompt 14 scientific audit utilities."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.feature_extraction import ExtractionMetadata, FeatureExtractor
from src.pose_estimation import MEDIAPIPE_POSE_LANDMARKS
from src.scientific_audit import generate_scientific_audit


def test_scientific_audit_exports_traceability_artifacts(tmp_path: Path) -> None:
    run_dir = tmp_path / "run_audit"
    (run_dir / "landmarks").mkdir(parents=True)
    (run_dir / "features").mkdir(parents=True)
    landmarks = _synthetic_landmarks()
    result = FeatureExtractor().extract_landmarks(
        landmarks,
        metadata=ExtractionMetadata(participant_id=1, trial_name="sample_video.avi"),
    )
    landmarks.to_csv(run_dir / "landmarks" / "landmarks.csv", index=False)
    result.feature_table.to_csv(run_dir / "features" / "feature_table.csv", index=False)
    metadata = {
        "video": {
            "path": "reports/video_processing/sample_video.avi",
            "fps": 30.0,
            "frame_count": 24,
        }
    }
    (run_dir / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")

    paths = generate_scientific_audit(run_dir, docs_dir=tmp_path / "docs")

    provenance = json.loads(paths.frame_provenance.read_text(encoding="utf-8"))
    assert len(provenance) == 57
    assert {record["feature"] for record in provenance} == set(result.feature_table.columns[5:])
    assert paths.angle_audit.exists()
    assert paths.feature_audit.exists()
    assert paths.dependency_graph.exists()
    assert paths.code_traceability.exists()
    assert paths.measurement_timeline.exists()
    assert paths.measurement_audit_index.exists()
    assert len(paths.measurement_images) == 12
    assert all(path.exists() for path in paths.measurement_images)
    assert "No documented initial-contact detector" in paths.measurement_timeline.read_text(
        encoding="utf-8"
    )
    assert "MediaPipe-derived geometric approximations" in paths.angle_audit.read_text(
        encoding="utf-8"
    )
    assert "\\|ROM_L - ROM_R\\|" in paths.feature_audit.read_text(encoding="utf-8")


def _synthetic_landmarks() -> pd.DataFrame:
    rows = []
    for frame_number, knee_offset in enumerate((0.0, 0.2, 0.4)):
        timestamp = frame_number / 30.0
        points = {
            "right_shoulder": (0.10, 0.20, 0.0),
            "right_hip": (0.12, 0.40, 0.0),
            "right_knee": (0.14 + knee_offset * 0.05, 0.62, 0.0),
            "right_ankle": (0.12, 0.82, 0.0),
            "right_foot_index": (0.24, 0.84, 0.0),
            "left_shoulder": (0.50, 0.20, 0.0),
            "left_hip": (0.52, 0.40, 0.0),
            "left_knee": (0.54 + knee_offset * 0.05, 0.62, 0.0),
            "left_ankle": (0.52, 0.82, 0.0),
            "left_foot_index": (0.64, 0.84, 0.0),
        }
        for index, name in enumerate(MEDIAPIPE_POSE_LANDMARKS):
            x, y, z = points.get(name, (np.nan, np.nan, np.nan))
            rows.append(
                {
                    "frame_number": frame_number,
                    "timestamp": timestamp,
                    "landmark_index": index,
                    "landmark_name": name,
                    "x": x,
                    "y": y,
                    "z": z,
                    "visibility": 1.0 if np.isfinite(x) else np.nan,
                    "confidence": 1.0 if np.isfinite(x) else np.nan,
                }
            )
    return pd.DataFrame(rows)
