"""Video ingestion and frame utilities for future pose-estimation prompts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Literal

import cv2
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure


SUPPORTED_VIDEO_EXTENSIONS: tuple[str, ...] = (".mp4", ".mov", ".avi")


class VideoProcessingError(ValueError):
    """Raised when a video cannot be read or validated."""


@dataclass(frozen=True)
class VideoMetadata:
    """Read-only video metadata.

    Args:
        filename: Source filename.
        path: Source video path.
        duration: Duration in seconds.
        frame_count: Number of frames.
        fps: Frames per second.
        width: Frame width in pixels.
        height: Frame height in pixels.
        codec: FourCC codec string when available.
    """

    filename: str
    path: str
    duration: float
    frame_count: int
    fps: float
    width: int
    height: int
    codec: str


@dataclass(frozen=True)
class VideoPreprocessingConfig:
    """Optional non-destructive frame preprocessing configuration.

    Args:
        resize: Optional output ``(width, height)``.
        grayscale: Convert frames to grayscale.
        normalize: Convert pixel values to float32 in ``[0, 1]``.
        sample_every_n: Keep every nth frame during sampled extraction.
    """

    resize: tuple[int, int] | None = None
    grayscale: bool = False
    normalize: bool = False
    sample_every_n: int = 1

    def __post_init__(self) -> None:
        """Validate preprocessing settings."""

        if self.resize is not None:
            width, height = self.resize
            if width <= 0 or height <= 0:
                raise ValueError("resize dimensions must be positive.")
        if self.sample_every_n < 1:
            raise ValueError("sample_every_n must be at least 1.")


class Video:
    """Validated video wrapper with deterministic frame access.

    Args:
        path: MP4, MOV, or AVI video path.

    Raises:
        FileNotFoundError: If ``path`` does not exist.
        VideoProcessingError: If format, codec, frame count, FPS, or resolution is invalid.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = _validate_path(path)
        self._metadata = _read_metadata(self.path)

    @property
    def metadata(self) -> VideoMetadata:
        """Return immutable video metadata."""

        return self._metadata

    @property
    def filename(self) -> str:
        """Return source filename."""

        return self.metadata.filename

    @property
    def frame_count(self) -> int:
        """Return number of frames."""

        return self.metadata.frame_count

    @property
    def fps(self) -> float:
        """Return frames per second."""

        return self.metadata.fps

    @property
    def duration(self) -> float:
        """Return duration in seconds."""

        return self.metadata.duration

    @property
    def width(self) -> int:
        """Return frame width in pixels."""

        return self.metadata.width

    @property
    def height(self) -> int:
        """Return frame height in pixels."""

        return self.metadata.height

    def __iter__(self) -> Iterator[np.ndarray]:
        """Iterate frames sequentially without modifying pixels."""

        capture = _open_capture(self.path)
        try:
            while True:
                ok, frame = capture.read()
                if not ok:
                    break
                yield frame
        finally:
            capture.release()

    def get_frame(self, index: int) -> np.ndarray:
        """Return a frame by zero-based index."""

        if index < 0 or index >= self.frame_count:
            raise IndexError(f"Frame index {index} is outside 0..{self.frame_count - 1}.")
        capture = _open_capture(self.path)
        try:
            capture.set(cv2.CAP_PROP_POS_FRAMES, int(index))
            ok, frame = capture.read()
            if not ok:
                raise VideoProcessingError(f"Could not read frame {index}.")
            return frame
        finally:
            capture.release()

    def get_frame_at_timestamp(self, timestamp_seconds: float) -> np.ndarray:
        """Return frame nearest to a timestamp in seconds."""

        if timestamp_seconds < 0 or timestamp_seconds > self.duration:
            raise IndexError(
                f"Timestamp {timestamp_seconds} is outside video duration {self.duration:.3f}."
            )
        index = min(int(round(timestamp_seconds * self.fps)), self.frame_count - 1)
        return self.get_frame(index)

    def iter_frames(
        self,
        config: VideoPreprocessingConfig | None = None,
    ) -> Iterator[np.ndarray]:
        """Iterate frames with optional non-destructive preprocessing."""

        preprocessing = config or VideoPreprocessingConfig()
        for index, frame in enumerate(self):
            if index % preprocessing.sample_every_n == 0:
                yield preprocess_frame(frame, preprocessing)

    def extract_frames(
        self,
        indices: list[int] | tuple[int, ...] | None = None,
        config: VideoPreprocessingConfig | None = None,
    ) -> list[np.ndarray]:
        """Extract selected frames deterministically."""

        preprocessing = config or VideoPreprocessingConfig()
        selected = indices if indices is not None else tuple(range(self.frame_count))
        frames = []
        for index in selected:
            frame = self.get_frame(int(index))
            frames.append(preprocess_frame(frame, preprocessing))
        return frames

    def select_clip_by_frames(
        self,
        start_frame: int,
        end_frame: int,
        config: VideoPreprocessingConfig | None = None,
    ) -> list[np.ndarray]:
        """Select a clip using inclusive frame indices.

        No event detection is performed.
        """

        if start_frame < 0 or end_frame < start_frame or end_frame >= self.frame_count:
            raise IndexError("Frame clip bounds are invalid.")
        return self.extract_frames(tuple(range(start_frame, end_frame + 1)), config)

    def select_clip_by_timestamps(
        self,
        start_seconds: float,
        end_seconds: float,
        config: VideoPreprocessingConfig | None = None,
    ) -> list[np.ndarray]:
        """Select a clip using timestamp bounds.

        No landing or movement events are inferred.
        """

        if start_seconds < 0 or end_seconds < start_seconds or end_seconds > self.duration:
            raise IndexError("Timestamp clip bounds are invalid.")
        start_frame = int(round(start_seconds * self.fps))
        end_frame = min(int(round(end_seconds * self.fps)), self.frame_count - 1)
        return self.select_clip_by_frames(start_frame, end_frame, config)


def preprocess_frame(frame: np.ndarray, config: VideoPreprocessingConfig) -> np.ndarray:
    """Apply optional resize, grayscale, and normalization to a frame copy."""

    processed = frame.copy()
    if config.resize is not None:
        processed = cv2.resize(processed, config.resize, interpolation=cv2.INTER_AREA)
    if config.grayscale:
        processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
    if config.normalize:
        processed = processed.astype(np.float32) / 255.0
    return processed


def save_frames(
    frames: list[np.ndarray] | tuple[np.ndarray, ...],
    output_dir: str | Path,
    *,
    prefix: str = "frame",
    image_format: Literal["png", "jpg"] = "png",
) -> list[Path]:
    """Save frames as images without changing source video data."""

    if image_format not in {"png", "jpg"}:
        raise ValueError("image_format must be 'png' or 'jpg'.")
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    paths = []
    for index, frame in enumerate(frames):
        path = destination / f"{prefix}_{index:04d}.{image_format}"
        output = _image_for_write(frame)
        if not cv2.imwrite(str(path), output):
            raise VideoProcessingError(f"Could not write frame image: {path}")
        paths.append(path)
    return paths


def first_frame_preview(video: Video) -> tuple[Figure, Axes]:
    """Create a first-frame preview."""

    return _frame_preview(video.get_frame(0), f"{video.filename} first frame")


def last_frame_preview(video: Video) -> tuple[Figure, Axes]:
    """Create a last-frame preview."""

    return _frame_preview(video.get_frame(video.frame_count - 1), f"{video.filename} last frame")


def playback_preview(
    video: Video,
    *,
    max_frames: int = 6,
) -> tuple[Figure, np.ndarray]:
    """Create a deterministic storyboard-style playback preview."""

    if max_frames < 1:
        raise ValueError("max_frames must be at least 1.")
    count = min(max_frames, video.frame_count)
    indices = np.linspace(0, video.frame_count - 1, count, dtype=int)
    figure, axes = plt.subplots(1, count, figsize=(2.6 * count, 2.4))
    axes_array = np.atleast_1d(axes)
    for axis, index in zip(axes_array, indices):
        axis.imshow(_rgb(video.get_frame(int(index))))
        axis.set_title(f"Frame {int(index)}", fontsize=9)
        axis.axis("off")
    figure.tight_layout()
    return figure, axes_array


def frame_timeline(video: Video) -> tuple[Figure, Axes]:
    """Plot frame index against timestamp."""

    frame_indices = np.arange(video.frame_count)
    timestamps = frame_indices / video.fps
    figure, axes = plt.subplots(figsize=(8.0, 2.6))
    axes.plot(timestamps, frame_indices, color="#2166AC", linewidth=1.5)
    axes.set(
        title=f"{video.filename} frame timeline",
        xlabel="Time (s)",
        ylabel="Frame index",
    )
    axes.spines[["top", "right"]].set_visible(False)
    axes.grid(axis="y", color="#D9D9D9", linewidth=0.7, alpha=0.75)
    figure.tight_layout()
    return figure, axes


def _validate_path(path: str | Path) -> Path:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Video file not found: {source}")
    if source.suffix.lower() not in SUPPORTED_VIDEO_EXTENSIONS:
        raise VideoProcessingError(
            f"Unsupported video format {source.suffix!r}; supported formats are "
            f"{', '.join(SUPPORTED_VIDEO_EXTENSIONS)}."
        )
    return source


def _read_metadata(path: Path) -> VideoMetadata:
    capture = _open_capture(path)
    try:
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = float(capture.get(cv2.CAP_PROP_FPS))
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = int(capture.get(cv2.CAP_PROP_FOURCC))
        codec = "".join(chr((fourcc >> (8 * index)) & 0xFF) for index in range(4)).strip()
    finally:
        capture.release()
    if frame_count <= 0:
        raise VideoProcessingError("Video has no readable frames.")
    if fps <= 0 or not np.isfinite(fps):
        raise VideoProcessingError("Video FPS is unavailable or invalid.")
    if width <= 0 or height <= 0:
        raise VideoProcessingError("Video resolution is unavailable or invalid.")
    return VideoMetadata(
        filename=path.name,
        path=str(path),
        duration=frame_count / fps,
        frame_count=frame_count,
        fps=fps,
        width=width,
        height=height,
        codec=codec,
    )


def _open_capture(path: Path) -> cv2.VideoCapture:
    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        capture.release()
        raise VideoProcessingError(f"Could not open video file: {path}")
    return capture


def _frame_preview(frame: np.ndarray, title: str) -> tuple[Figure, Axes]:
    figure, axes = plt.subplots(figsize=(6.0, 4.0))
    axes.imshow(_rgb(frame))
    axes.set_title(title)
    axes.axis("off")
    figure.tight_layout()
    return figure, axes


def _rgb(frame: np.ndarray) -> np.ndarray:
    if frame.ndim == 2:
        return frame
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


def _image_for_write(frame: np.ndarray) -> np.ndarray:
    if np.issubdtype(frame.dtype, np.floating):
        return np.clip(frame * 255.0, 0, 255).astype(np.uint8)
    return frame
