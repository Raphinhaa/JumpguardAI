"""Tests for Prompt 10 pose estimation layer."""

from pathlib import Path
import json

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

from src.pose_estimation import (
    MEDIAPIPE_POSE_LANDMARKS,
    MediaPipePoseEstimator,
    PoseEstimationError,
    PoseEstimationResult,
    annotate_frame,
    export_annotated_frames,
    export_landmarks,
    landmark_preview,
)
from src.video_processing import Video


@pytest.fixture(scope="module")
def demo_video() -> Video:
    return Video("reports/video_processing/sample_video.avi")


@pytest.fixture(scope="module")
def estimator() -> MediaPipePoseEstimator:
    return MediaPipePoseEstimator("models/pose_landmarker_lite.task")


def test_mediapipe_backend_loads(estimator: MediaPipePoseEstimator) -> None:
    estimator.load_model()

    assert estimator.backend_name in {"mediapipe_tasks", "mediapipe_solutions"}


def test_estimate_video_landmark_dimensions(
    estimator: MediaPipePoseEstimator,
    demo_video: Video,
) -> None:
    result = estimator.estimate(demo_video, frame_skip=12)

    assert isinstance(result, PoseEstimationResult)
    assert result.landmarks.shape == (66, 9)
    assert result.landmarks.groupby("frame_number").size().eq(33).all()
    assert tuple(result.landmarks["landmark_name"].head(33)) == MEDIAPIPE_POSE_LANDMARKS


def test_estimate_frame_missing_landmarks_are_preserved(
    estimator: MediaPipePoseEstimator,
    demo_video: Video,
) -> None:
    frame = demo_video.get_frame(0)
    landmarks = estimator.estimate_frame(frame, frame_number=0, timestamp=0.0)

    assert landmarks.shape == (33, 9)
    assert landmarks["x"].isna().all()
    assert landmarks["visibility"].isna().all()
    assert landmarks["landmark_name"].tolist() == list(MEDIAPIPE_POSE_LANDMARKS)


def test_confidence_filter_preserves_schema(
    estimator: MediaPipePoseEstimator,
    demo_video: Video,
) -> None:
    result = estimator.estimate(demo_video, frame_skip=24, confidence_threshold=1.0)

    assert result.landmarks.shape == (33, 9)
    estimator.validate_output(result)


def test_exports_are_deterministic(
    tmp_path: Path,
    estimator: MediaPipePoseEstimator,
    demo_video: Video,
) -> None:
    result = estimator.estimate(demo_video, frame_skip=12)
    csv_path, json_path = estimator.export_landmarks(
        result,
        tmp_path / "landmarks.csv",
        tmp_path / "landmarks.json",
    )
    first_csv = csv_path.read_text(encoding="utf-8")
    first_json = json_path.read_text(encoding="utf-8")
    export_landmarks(result, csv_path, json_path)

    assert csv_path.read_text(encoding="utf-8") == first_csv
    assert json_path.read_text(encoding="utf-8") == first_json
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert len(payload["landmarks"]) == 66


def test_validation_rejects_invalid_output(estimator: MediaPipePoseEstimator) -> None:
    bad = PoseEstimationResult(
        video_path="x",
        backend="test",
        frame_count=1,
        fps=1.0,
        landmarks=pd.DataFrame({"frame_number": [0]}),
    )

    with pytest.raises(PoseEstimationError):
        estimator.validate_output(bad)


def test_visualization_utilities(
    tmp_path: Path,
    estimator: MediaPipePoseEstimator,
    demo_video: Video,
) -> None:
    result = estimator.estimate(demo_video, frame_skip=12)
    frame = demo_video.get_frame(0)
    rows = result.landmarks[result.landmarks["frame_number"].eq(0)]
    annotated = annotate_frame(frame, rows)
    figure, _ = landmark_preview(frame, rows)
    paths = export_annotated_frames(demo_video, result, tmp_path, max_frames=1)

    assert annotated.shape == frame.shape
    assert figure is not None
    assert len(paths) == 1
    assert paths[0].exists()
    plt.close("all")


def test_missing_model_file_raises(tmp_path: Path) -> None:
    estimator = MediaPipePoseEstimator(tmp_path / "missing.task")

    with pytest.raises(PoseEstimationError, match="model file"):
        estimator.load_model()
