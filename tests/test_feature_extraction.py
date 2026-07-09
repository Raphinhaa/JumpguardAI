"""Tests for Prompt 11 landmark-derived biomechanical feature extraction."""

from pathlib import Path
import json

import numpy as np
import pandas as pd
import pytest

from src.feature_engineering import FeatureExtractor as Prompt3FeatureExtractor
from src.feature_extraction import (
    ExtractionMetadata,
    FeatureExtractionError,
    FeatureExtractor,
    export_feature_plots,
)
from src.pose_estimation import MEDIAPIPE_POSE_LANDMARKS, PoseEstimationResult
from src.video_processing import Video


def synthetic_landmarks(missing_left_knee: bool = False) -> pd.DataFrame:
    rows = []
    for frame_number, knee_offset in enumerate((0.0, 0.2, 0.4)):
        timestamp = frame_number * 0.1
        points = {
            "right_shoulder": (0.0, 2.0, 0.0),
            "right_hip": (0.0, 1.0, 0.0),
            "right_knee": (0.2 + knee_offset, 0.0, 0.0),
            "right_ankle": (0.0, -1.0, 0.0),
            "right_foot_index": (0.6, -1.0, 0.0),
            "left_shoulder": (1.0, 2.0, 0.0),
            "left_hip": (1.0, 1.0, 0.0),
            "left_knee": (1.2 + knee_offset, 0.0, 0.0),
            "left_ankle": (1.0, -1.0, 0.0),
            "left_foot_index": (1.6, -1.0, 0.0),
        }
        for index, name in enumerate(MEDIAPIPE_POSE_LANDMARKS):
            x, y, z = points.get(name, (np.nan, np.nan, np.nan))
            if missing_left_knee and name == "left_knee":
                x, y, z = np.nan, np.nan, np.nan
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


def test_feature_schema_matches_prompt3() -> None:
    extractor = FeatureExtractor()

    assert extractor.feature_names == Prompt3FeatureExtractor().feature_names
    assert len(extractor.feature_names) == 57


def test_joint_angle_geometry_and_prompt3_table() -> None:
    extractor = FeatureExtractor()
    result = extractor.extract_landmarks(
        synthetic_landmarks(),
        metadata=ExtractionMetadata(participant_id=999, trial_slot=1, trial_name="synthetic"),
    )

    table = result.feature_table
    assert table.shape == (1, 62)
    assert tuple(table.columns[5:]) == extractor.feature_names
    assert table.loc[0, "participant_id"] == 999
    assert table.loc[0, "knee_flexion_right_mean"] > 0
    assert table.loc[0, "knee_flexion_right_rom"] >= 0
    assert "knee_flexion" in result.symmetry_summary
    assert result.landing_events["beginning_frame"] is None
    assert result.landing_events["peak_flexion_frame"] is not None


def test_missing_landmarks_preserve_nan() -> None:
    extractor = FeatureExtractor()
    result = extractor.extract_landmarks(synthetic_landmarks(missing_left_knee=True))

    assert result.joint_angles["knee_flexion_left"].isna().all()
    assert np.isnan(result.feature_table.loc[0, "knee_flexion_left_mean"])
    assert np.isnan(result.feature_table.loc[0, "knee_flexion_rom_absolute_difference"])


def test_extract_csv_json_and_export_are_deterministic(tmp_path: Path) -> None:
    landmarks = synthetic_landmarks()
    csv_path = tmp_path / "landmarks.csv"
    json_path = tmp_path / "landmarks.json"
    landmarks.to_csv(csv_path, index=False)
    json_path.write_text(
        json.dumps({"landmarks": landmarks.to_dict(orient="records")}),
        encoding="utf-8",
    )
    extractor = FeatureExtractor()
    csv_result = extractor.extract(csv_path)
    json_result = extractor.extract_json(json_path)

    pd.testing.assert_frame_equal(csv_result.feature_table, json_result.feature_table)
    paths = extractor.export(csv_result, tmp_path / "exports")
    first = (tmp_path / "exports" / "feature_table.csv").read_text(encoding="utf-8")
    extractor.export(csv_result, tmp_path / "exports")
    second = (tmp_path / "exports" / "feature_table.csv").read_text(encoding="utf-8")

    assert first == second
    assert paths["feature_table_csv"].exists()
    assert paths["landing_events"].exists()
    assert (tmp_path / "exports" / "plots" / "joint_angles.png").exists()


def test_extract_video_requires_existing_pose_result(tmp_path: Path) -> None:
    extractor = FeatureExtractor()
    video = Video("reports/video_processing/sample_video.avi")

    with pytest.raises(FeatureExtractionError):
        extractor.extract_video(video)

    pose_result = PoseEstimationResult(
        video_path=str(video.path),
        backend="test",
        frame_count=3,
        fps=10.0,
        landmarks=synthetic_landmarks(),
    )
    result = extractor.extract_video(video, pose_result=pose_result)
    assert result.feature_table.loc[0, "trial_name"] == video.filename


def test_invalid_landmark_schema_raises() -> None:
    with pytest.raises(FeatureExtractionError):
        FeatureExtractor().extract_landmarks(pd.DataFrame({"frame_number": [0]}))


def test_plot_export_smoke(tmp_path: Path) -> None:
    result = FeatureExtractor().extract_landmarks(synthetic_landmarks())
    paths = export_feature_plots(result, tmp_path)

    assert len(paths) == 4
    assert all(path.exists() for path in paths)
