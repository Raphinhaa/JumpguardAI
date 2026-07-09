"""Tests for Prompt 9 video processing layer."""

from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pytest

from src.video_processing import (
    Video,
    VideoPreprocessingConfig,
    VideoProcessingError,
    first_frame_preview,
    frame_timeline,
    last_frame_preview,
    playback_preview,
    save_frames,
)


@pytest.fixture()
def sample_video(tmp_path: Path) -> Path:
    path = tmp_path / "sample.avi"
    writer = cv2.VideoWriter(
        str(path),
        cv2.VideoWriter_fourcc(*"MJPG"),
        10.0,
        (32, 24),
    )
    assert writer.isOpened()
    for index in range(12):
        frame = np.zeros((24, 32, 3), dtype=np.uint8)
        frame[:, :, 0] = index * 10
        frame[:, :, 1] = 50
        frame[:, :, 2] = 100
        writer.write(frame)
    writer.release()
    return path


def test_video_metadata_and_properties(sample_video: Path) -> None:
    video = Video(sample_video)

    assert video.filename == "sample.avi"
    assert video.frame_count == 12
    assert video.fps == pytest.approx(10.0)
    assert video.duration == pytest.approx(1.2)
    assert video.width == 32
    assert video.height == 24
    assert video.metadata.codec


def test_frame_access_iteration_and_timestamp(sample_video: Path) -> None:
    video = Video(sample_video)
    first = video.get_frame(0)
    timestamp = video.get_frame_at_timestamp(0.5)
    frames = list(video)

    assert first.shape == (24, 32, 3)
    assert timestamp.shape == (24, 32, 3)
    assert len(frames) == video.frame_count
    np.testing.assert_array_equal(first, video.get_frame(0))


def test_preprocessing_is_non_destructive_and_deterministic(sample_video: Path) -> None:
    video = Video(sample_video)
    original = video.get_frame(0)
    config = VideoPreprocessingConfig(resize=(16, 12), grayscale=True, normalize=True)

    first = video.extract_frames([0, 1], config)
    second = video.extract_frames([0, 1], config)

    assert first[0].shape == (12, 16)
    assert first[0].dtype == np.float32
    assert float(first[0].min()) >= 0.0
    assert float(first[0].max()) <= 1.0
    np.testing.assert_array_equal(first[0], second[0])
    np.testing.assert_array_equal(original, video.get_frame(0))


def test_sampling_and_clip_selection(sample_video: Path) -> None:
    video = Video(sample_video)
    sampled = list(video.iter_frames(VideoPreprocessingConfig(sample_every_n=3)))
    frame_clip = video.select_clip_by_frames(2, 5)
    time_clip = video.select_clip_by_timestamps(0.2, 0.5)

    assert len(sampled) == 4
    assert len(frame_clip) == 4
    assert len(time_clip) == 4


def test_invalid_inputs_and_bounds(tmp_path: Path, sample_video: Path) -> None:
    with pytest.raises(FileNotFoundError):
        Video(tmp_path / "missing.avi")

    unsupported = tmp_path / "sample.webm"
    unsupported.write_bytes(b"not a supported video")
    with pytest.raises(VideoProcessingError, match="Unsupported"):
        Video(unsupported)

    invalid = tmp_path / "invalid.avi"
    invalid.write_text("not a video", encoding="utf-8")
    with pytest.raises(VideoProcessingError):
        Video(invalid)

    video = Video(sample_video)
    with pytest.raises(IndexError):
        video.get_frame(video.frame_count)
    with pytest.raises(IndexError):
        video.get_frame_at_timestamp(video.duration + 1)
    with pytest.raises(IndexError):
        video.select_clip_by_frames(5, 2)


def test_save_frames_and_visualizations(tmp_path: Path, sample_video: Path) -> None:
    video = Video(sample_video)
    frames = video.extract_frames([0, 1])
    paths = save_frames(frames, tmp_path / "frames")

    assert len(paths) == 2
    assert all(path.exists() for path in paths)
    assert first_frame_preview(video)[0] is not None
    assert last_frame_preview(video)[0] is not None
    assert playback_preview(video, max_frames=3)[0] is not None
    assert frame_timeline(video)[0] is not None
    plt.close("all")
