"""Pose-estimation layer built on the Prompt 9 Video abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
from typing import Any

import json

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .video_processing import Video


MEDIAPIPE_POSE_LANDMARKS: tuple[str, ...] = (
    "nose",
    "left_eye_inner",
    "left_eye",
    "left_eye_outer",
    "right_eye_inner",
    "right_eye",
    "right_eye_outer",
    "left_ear",
    "right_ear",
    "mouth_left",
    "mouth_right",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_pinky",
    "right_pinky",
    "left_index",
    "right_index",
    "left_thumb",
    "right_thumb",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
    "left_heel",
    "right_heel",
    "left_foot_index",
    "right_foot_index",
)

MEDIAPIPE_POSE_CONNECTIONS: tuple[tuple[int, int], ...] = (
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 7),
    (0, 4),
    (4, 5),
    (5, 6),
    (6, 8),
    (9, 10),
    (11, 12),
    (11, 13),
    (13, 15),
    (15, 17),
    (15, 19),
    (15, 21),
    (17, 19),
    (12, 14),
    (14, 16),
    (16, 18),
    (16, 20),
    (16, 22),
    (18, 20),
    (11, 23),
    (12, 24),
    (23, 24),
    (23, 25),
    (24, 26),
    (25, 27),
    (26, 28),
    (27, 29),
    (28, 30),
    (29, 31),
    (30, 32),
    (27, 31),
    (28, 32),
)


@dataclass(frozen=True)
class LandmarkRecord:
    """One MediaPipe landmark for one video frame."""

    frame_number: int
    timestamp: float
    landmark_index: int
    landmark_name: str
    x: float
    y: float
    z: float
    visibility: float
    confidence: float


@dataclass(frozen=True)
class PoseEstimationResult:
    """Pose-estimation result table and source metadata."""

    video_path: str
    backend: str
    frame_count: int
    fps: float
    landmarks: pd.DataFrame


@dataclass(frozen=True)
class BrowserVideoExportResult:
    """Result of converting an annotated video into browser-playable MP4."""

    mp4_path: Path | None
    warning: str | None
    command: tuple[str, ...] | None = None


class PoseEstimationError(RuntimeError):
    """Raised when pose estimation cannot run or validate."""


class PoseEstimator(ABC):
    """Backend-independent pose-estimation interface."""

    @abstractmethod
    def load_model(self) -> None:
        """Load backend model resources."""

    @abstractmethod
    def estimate(
        self,
        video: Video,
        *,
        frame_skip: int = 1,
        confidence_threshold: float | None = None,
    ) -> PoseEstimationResult:
        """Estimate landmarks for a Video."""

    @abstractmethod
    def estimate_frame(
        self,
        frame: np.ndarray,
        *,
        frame_number: int = 0,
        timestamp: float = 0.0,
        confidence_threshold: float | None = None,
    ) -> pd.DataFrame:
        """Estimate landmarks for one frame."""

    def export_landmarks(
        self,
        result: PoseEstimationResult,
        csv_path: str | Path,
        json_path: str | Path,
    ) -> tuple[Path, Path]:
        """Export deterministic CSV and JSON landmark files."""

        self.validate_output(result)
        csv_destination = Path(csv_path)
        json_destination = Path(json_path)
        csv_destination.parent.mkdir(parents=True, exist_ok=True)
        json_destination.parent.mkdir(parents=True, exist_ok=True)
        result.landmarks.to_csv(csv_destination, index=False, float_format="%.10g")
        payload = {
            "video_path": result.video_path,
            "backend": result.backend,
            "frame_count": result.frame_count,
            "fps": result.fps,
            "landmarks": _json_records(result.landmarks),
        }
        json_destination.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return csv_destination, json_destination

    def validate_output(self, result: PoseEstimationResult) -> None:
        """Validate landmark schema and per-frame landmark count."""

        expected_columns = (
            "frame_number",
            "timestamp",
            "landmark_index",
            "landmark_name",
            "x",
            "y",
            "z",
            "visibility",
            "confidence",
        )
        if tuple(result.landmarks.columns) != expected_columns:
            raise PoseEstimationError("Landmark output schema is invalid.")
        counts = result.landmarks.groupby("frame_number")["landmark_index"].count()
        if not counts.empty and not counts.eq(len(MEDIAPIPE_POSE_LANDMARKS)).all():
            raise PoseEstimationError("Every processed frame must contain 33 landmark rows.")


class MediaPipePoseEstimator(PoseEstimator):
    """MediaPipe Pose backend using Tasks API with optional legacy fallback.

    Args:
        model_path: MediaPipe ``.task`` model asset path.
        min_pose_detection_confidence: MediaPipe detection confidence setting.
        min_pose_presence_confidence: MediaPipe pose-presence confidence setting.
        min_tracking_confidence: MediaPipe tracking confidence setting.
    """

    def __init__(
        self,
        model_path: str | Path = "models/pose_landmarker_lite.task",
        *,
        min_pose_detection_confidence: float = 0.5,
        min_pose_presence_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ) -> None:
        self.model_path = Path(model_path)
        self.min_pose_detection_confidence = min_pose_detection_confidence
        self.min_pose_presence_confidence = min_pose_presence_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.backend_name = "mediapipe_tasks"
        self._landmarker: Any | None = None
        self._mp: Any | None = None
        self._legacy_pose: Any | None = None

    def load_model(self) -> None:
        """Load MediaPipe PoseLandmarker resources."""

        if self._landmarker is not None or self._legacy_pose is not None:
            return
        try:
            import mediapipe as mp
            from mediapipe.tasks.python import BaseOptions
            from mediapipe.tasks.python import vision
        except Exception:
            try:
                import mediapipe as mp

                pose_api = mp.solutions.pose
            except Exception as exc:
                raise PoseEstimationError(
                    "MediaPipe Tasks or classic MediaPipe Pose is required."
                ) from exc
            self.backend_name = "mediapipe_solutions"
            self._mp = mp
            self._legacy_pose = pose_api.Pose(
                static_image_mode=True,
                model_complexity=1,
                enable_segmentation=False,
                min_detection_confidence=self.min_pose_detection_confidence,
            )
            return

        if not self.model_path.exists():
            raise PoseEstimationError(
                f"MediaPipe pose model file not found: {self.model_path}. "
                "Download a Pose Landmarker .task file before inference."
            )

        options = vision.PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(self.model_path)),
            running_mode=vision.RunningMode.IMAGE,
            num_poses=1,
            min_pose_detection_confidence=self.min_pose_detection_confidence,
            min_pose_presence_confidence=self.min_pose_presence_confidence,
            min_tracking_confidence=self.min_tracking_confidence,
            output_segmentation_masks=False,
        )
        self._landmarker = vision.PoseLandmarker.create_from_options(options)
        self._mp = mp

    def estimate(
        self,
        video: Video,
        *,
        frame_skip: int = 1,
        confidence_threshold: float | None = None,
    ) -> PoseEstimationResult:
        """Estimate MediaPipe pose landmarks for a validated Video."""

        if frame_skip < 1:
            raise ValueError("frame_skip must be at least 1.")
        rows = []
        self.load_model()
        for frame_number, frame in enumerate(video):
            if frame_number % frame_skip != 0:
                continue
            timestamp = frame_number / video.fps
            frame_rows = self.estimate_frame(
                frame,
                frame_number=frame_number,
                timestamp=timestamp,
                confidence_threshold=confidence_threshold,
            )
            rows.append(frame_rows)
        landmarks = (
            pd.concat(rows, ignore_index=True)
            if rows
            else _empty_landmark_frame()
        )
        result = PoseEstimationResult(
            video_path=str(video.path),
            backend=self.backend_name,
            frame_count=video.frame_count,
            fps=video.fps,
            landmarks=landmarks,
        )
        self.validate_output(result)
        return result

    def estimate_frame(
        self,
        frame: np.ndarray,
        *,
        frame_number: int = 0,
        timestamp: float = 0.0,
        confidence_threshold: float | None = None,
    ) -> pd.DataFrame:
        """Estimate MediaPipe pose landmarks for one BGR frame."""

        self.load_model()
        assert self._mp is not None
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if self._legacy_pose is not None:
            detection = self._legacy_pose.process(rgb)
            pose_landmarks = (
                detection.pose_landmarks.landmark
                if detection.pose_landmarks is not None
                else None
            )
            return _landmark_rows(
                pose_landmarks,
                frame_number=frame_number,
                timestamp=timestamp,
                confidence_threshold=confidence_threshold,
            )
        assert self._landmarker is not None
        image = self._mp.Image(image_format=self._mp.ImageFormat.SRGB, data=rgb)
        detection = self._landmarker.detect(image)
        pose_landmarks = detection.pose_landmarks[0] if detection.pose_landmarks else None
        return _landmark_rows(
            pose_landmarks,
            frame_number=frame_number,
            timestamp=timestamp,
            confidence_threshold=confidence_threshold,
        )


def export_landmarks(
    result: PoseEstimationResult,
    csv_path: str | Path,
    json_path: str | Path,
) -> tuple[Path, Path]:
    """Export landmarks without requiring direct estimator access."""

    estimator = _ExportOnlyEstimator()
    return estimator.export_landmarks(result, csv_path, json_path)


def landmark_preview(
    frame: np.ndarray,
    frame_landmarks: pd.DataFrame,
) -> tuple[Figure, Axes]:
    """Create a debugging preview with detected landmarks overlaid."""

    annotated = annotate_frame(frame, frame_landmarks)
    figure, axes = plt.subplots(figsize=(6.0, 4.0))
    axes.imshow(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB))
    axes.set_title("Pose landmark preview")
    axes.axis("off")
    figure.tight_layout()
    return figure, axes


def annotate_frame(frame: np.ndarray, frame_landmarks: pd.DataFrame) -> np.ndarray:
    """Overlay available landmark points and skeleton connections on a frame copy."""

    annotated = frame.copy()
    height, width = annotated.shape[:2]
    points = _landmark_pixel_points(frame_landmarks, width=width, height=height)
    for start, end in _pose_connections():
        if start in points and end in points:
            cv2.line(annotated, points[start], points[end], (0, 180, 255), 2)
    for _, row in frame_landmarks.dropna(subset=["x", "y"]).iterrows():
        x = int(float(row["x"]) * width)
        y = int(float(row["y"]) * height)
        cv2.circle(annotated, (x, y), 3, (0, 255, 0), -1)
    return annotated


def _landmark_pixel_points(
    frame_landmarks: pd.DataFrame,
    *,
    width: int,
    height: int,
) -> dict[int, tuple[int, int]]:
    points: dict[int, tuple[int, int]] = {}
    for _, row in frame_landmarks.dropna(subset=["x", "y"]).iterrows():
        points[int(row["landmark_index"])] = (
            int(float(row["x"]) * width),
            int(float(row["y"]) * height),
        )
    return points


def _pose_connections() -> tuple[tuple[int, int], ...]:
    try:
        import mediapipe as mp

        return tuple((int(start), int(end)) for start, end in mp.solutions.pose.POSE_CONNECTIONS)
    except Exception:
        return MEDIAPIPE_POSE_CONNECTIONS


def export_annotated_frames(
    video: Video,
    result: PoseEstimationResult,
    output_dir: str | Path,
    *,
    max_frames: int = 5,
) -> list[Path]:
    """Export representative annotated frames for debugging."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    frame_numbers = sorted(result.landmarks["frame_number"].unique().tolist())[:max_frames]
    paths = []
    for frame_number in frame_numbers:
        frame = video.get_frame(int(frame_number))
        rows = result.landmarks[result.landmarks["frame_number"].eq(frame_number)]
        annotated = annotate_frame(frame, rows)
        path = destination / f"annotated_frame_{int(frame_number):04d}.png"
        if not cv2.imwrite(str(path), annotated):
            raise PoseEstimationError(f"Could not write annotated frame: {path}")
        paths.append(path)
    return paths


def export_annotated_video(
    video: Video,
    result: PoseEstimationResult,
    output_path: str | Path,
) -> Path:
    """Export an annotated video for debugging only."""

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(destination),
        cv2.VideoWriter_fourcc(*"MJPG"),
        video.fps,
        (video.width, video.height),
    )
    if not writer.isOpened():
        raise PoseEstimationError(f"Could not create annotated video: {destination}")
    try:
        for frame_number, frame in enumerate(video):
            rows = result.landmarks[result.landmarks["frame_number"].eq(frame_number)]
            writer.write(annotate_frame(frame, rows))
    finally:
        writer.release()
    return destination


def export_browser_compatible_video(
    annotated_video_path: str | Path,
    output_path: str | Path | None = None,
) -> BrowserVideoExportResult:
    """Create an H.264 MP4 copy of an annotated video for browser playback."""

    source = Path(annotated_video_path)
    destination = Path(output_path) if output_path is not None else source.with_suffix(".mp4")
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        return BrowserVideoExportResult(
            None,
            "FFmpeg is unavailable; annotated AVI was retained, but embedded browser playback may be unavailable.",
            None,
        )
    command = (
        ffmpeg,
        "-y",
        "-i",
        str(source),
        "-vcodec",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(destination),
    )
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "unknown FFmpeg error").strip().splitlines()
        message = detail[-1] if detail else "unknown FFmpeg error"
        return BrowserVideoExportResult(
            None,
            f"FFmpeg could not create browser-compatible MP4: {message}",
            command,
        )
    if not destination.exists() or destination.stat().st_size == 0:
        return BrowserVideoExportResult(
            None,
            "FFmpeg completed, but the browser-compatible MP4 was not created or was empty.",
            command,
        )
    return BrowserVideoExportResult(destination, None, command)


def _landmark_rows(
    pose_landmarks: list[Any] | None,
    *,
    frame_number: int,
    timestamp: float,
    confidence_threshold: float | None,
) -> pd.DataFrame:
    rows = []
    for index, name in enumerate(MEDIAPIPE_POSE_LANDMARKS):
        landmark = pose_landmarks[index] if pose_landmarks and index < len(pose_landmarks) else None
        if landmark is None:
            values = (np.nan, np.nan, np.nan, np.nan, np.nan)
        else:
            visibility = float(getattr(landmark, "visibility", np.nan))
            confidence = float(getattr(landmark, "presence", visibility))
            if confidence_threshold is not None and confidence < confidence_threshold:
                values = (np.nan, np.nan, np.nan, visibility, confidence)
            else:
                values = (
                    float(landmark.x),
                    float(landmark.y),
                    float(landmark.z),
                    visibility,
                    confidence,
                )
        x, y, z, visibility, confidence = values
        rows.append(
            LandmarkRecord(
                frame_number=int(frame_number),
                timestamp=float(timestamp),
                landmark_index=index,
                landmark_name=name,
                x=x,
                y=y,
                z=z,
                visibility=visibility,
                confidence=confidence,
            )
        )
    return pd.DataFrame([record.__dict__ for record in rows], columns=_landmark_columns())


def _empty_landmark_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=_landmark_columns())


def _landmark_columns() -> tuple[str, ...]:
    return (
        "frame_number",
        "timestamp",
        "landmark_index",
        "landmark_name",
        "x",
        "y",
        "z",
        "visibility",
        "confidence",
    )


def _json_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    records = []
    for row in frame.to_dict(orient="records"):
        records.append(
            {
                key: (None if isinstance(value, float) and np.isnan(value) else value)
                for key, value in row.items()
            }
        )
    return records


class _ExportOnlyEstimator(PoseEstimator):
    def load_model(self) -> None:
        return None

    def estimate(
        self,
        video: Video,
        *,
        frame_skip: int = 1,
        confidence_threshold: float | None = None,
    ) -> PoseEstimationResult:
        raise NotImplementedError

    def estimate_frame(
        self,
        frame: np.ndarray,
        *,
        frame_number: int = 0,
        timestamp: float = 0.0,
        confidence_threshold: float | None = None,
    ) -> pd.DataFrame:
        raise NotImplementedError
