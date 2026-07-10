"""Tests for Prompt 12 end-to-end pipeline orchestration."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import json

import numpy as np
import pandas as pd
import pytest

from src.feature_extraction import FeatureExtractor
from src.pipeline import JumpGuardPipeline, PipelineExecutionError
from src.pose_estimation import MEDIAPIPE_POSE_LANDMARKS, PoseEstimationResult, PoseEstimator
from src.video_processing import Video


class DeterministicPoseEstimator(PoseEstimator):
    """Small test double that preserves the Prompt 10 estimator contract."""

    def load_model(self) -> None:
        return None

    def estimate(
        self,
        video: Video,
        *,
        frame_skip: int = 1,
        confidence_threshold: float | None = None,
    ) -> PoseEstimationResult:
        del confidence_threshold
        frames = range(0, video.frame_count, frame_skip)
        return PoseEstimationResult(
            video_path=str(video.path),
            backend="deterministic_test",
            frame_count=video.frame_count,
            fps=video.fps,
            landmarks=_synthetic_landmarks(frames, video.fps),
        )

    def estimate_frame(
        self,
        frame: np.ndarray,
        *,
        frame_number: int = 0,
        timestamp: float = 0.0,
        confidence_threshold: float | None = None,
    ) -> pd.DataFrame:
        del frame, confidence_threshold
        return _synthetic_landmarks((frame_number,), fps=1.0, fixed_timestamp=timestamp)


def _synthetic_landmarks(
    frames: range | tuple[int, ...],
    fps: float,
    *,
    fixed_timestamp: float | None = None,
) -> pd.DataFrame:
    rows = []
    for ordinal, frame_number in enumerate(frames):
        timestamp = fixed_timestamp if fixed_timestamp is not None else frame_number / fps
        knee_offset = 0.05 * ordinal
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


def _pipeline() -> JumpGuardPipeline:
    return JumpGuardPipeline(
        pose_estimator=DeterministicPoseEstimator(),
        feature_extractor=FeatureExtractor(),
    )


def test_process_video_creates_complete_run_package(tmp_path: Path) -> None:
    result = _pipeline().process_video(
        "reports/video_processing/sample_video.avi",
        tmp_path,
        run_id="run_test",
        frame_skip=6,
        timestamp=datetime(2026, 7, 9, tzinfo=UTC),
    )

    run_dir = tmp_path / "run_test"
    assert result.run_directory == run_dir
    assert result.metadata["status"] == "success"
    assert result.metadata["frame_count"] == 24
    assert result.metadata["feature_count"] == 57
    assert result.metadata["predictions_generated"] is False
    for key in (
        "video",
        "landmarks_csv",
        "landmarks_json",
        "features_feature_table_csv",
        "features_feature_table_json",
        "athlete_report_json",
        "athlete_report_markdown",
        "athlete_report_html",
        "dashboard_json",
        "dashboard_html",
        "metadata",
    ):
        assert Path(result.generated_files[key]).exists(), key

    feature_table = pd.read_csv(run_dir / "features" / "feature_table.csv")
    assert feature_table.shape == (1, 62)
    assert feature_table.loc[0, "trial_name"] == "sample_video.avi"
    dashboard_text = (run_dir / "dashboard" / "index.html").read_text(encoding="utf-8").lower()
    assert "risk score" not in dashboard_text
    assert "no clinical interpretations" in dashboard_text


def test_pipeline_artifacts_are_deterministic_for_same_inputs(tmp_path: Path) -> None:
    pipeline = _pipeline()
    first = pipeline.process_video(
        "reports/video_processing/sample_video.avi",
        tmp_path / "first",
        run_id="run_same",
        frame_skip=8,
        timestamp=datetime(2026, 7, 9, tzinfo=UTC),
    )
    second = pipeline.process_video(
        "reports/video_processing/sample_video.avi",
        tmp_path / "second",
        run_id="run_same",
        frame_skip=8,
        timestamp=datetime(2026, 7, 9, tzinfo=UTC),
    )

    assert Path(first.generated_files["landmarks_csv"]).read_text(encoding="utf-8") == Path(
        second.generated_files["landmarks_csv"]
    ).read_text(encoding="utf-8")
    assert Path(first.generated_files["features_feature_table_csv"]).read_text(encoding="utf-8") == Path(
        second.generated_files["features_feature_table_csv"]
    ).read_text(encoding="utf-8")


def test_process_video_failure_writes_metadata(tmp_path: Path) -> None:
    bad_video = tmp_path / "not_a_video.webm"
    bad_video.write_bytes(b"not a video")

    with pytest.raises(PipelineExecutionError) as exc_info:
        _pipeline().process_video(bad_video, tmp_path, run_id="run_bad")

    metadata_path = tmp_path / "run_bad" / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["status"] == "failed"
    assert metadata["video"] is None
    assert metadata["frame_count"] is None
    assert "unsupported video format" in metadata["error"].lower()
    assert exc_info.value.result.generated_files["metadata"] == str(metadata_path)
