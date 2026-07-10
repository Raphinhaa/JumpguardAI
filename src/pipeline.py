"""End-to-end orchestration for the JumpGuard AI pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from time import perf_counter
from typing import Any

import json
import shutil

import pandas as pd

from .feature_extraction import ExtractionMetadata
from .feature_extraction import FeatureExtractor as LandmarkFeatureExtractor
from .pose_estimation import MediaPipePoseEstimator, PoseEstimator
from .video_processing import Video


@dataclass(frozen=True)
class PipelineResult:
    """Paths and metadata from one pipeline execution."""

    run_directory: Path
    metadata: dict[str, Any]
    generated_files: dict[str, str]


class JumpGuardPipeline:
    """Coordinate existing video, pose, feature, report, and dashboard layers.

    This class orchestrates existing modules only. It does not introduce new
    pose-estimation methods, biomechanical calculations, machine learning, or
    clinical interpretations.

    Args:
        pose_estimator: Optional existing PoseEstimator implementation.
        feature_extractor: Optional Prompt 11 feature extractor.
    """

    def __init__(
        self,
        *,
        pose_estimator: PoseEstimator | None = None,
        feature_extractor: LandmarkFeatureExtractor | None = None,
    ) -> None:
        default_model_path = Path(__file__).resolve().parent.parent / "models" / "pose_landmarker_lite.task"
        self.pose_estimator = pose_estimator or MediaPipePoseEstimator(model_path=default_model_path)
        self.feature_extractor = feature_extractor or LandmarkFeatureExtractor()

    def process_video(
        self,
        video_path: str | Path,
        output_directory: str | Path = "reports",
        *,
        run_id: str | None = None,
        frame_skip: int = 1,
        timestamp: datetime | None = None,
    ) -> PipelineResult:
        """Process one video through the completed Prompt 9-11 pipeline."""

        started = timestamp or datetime.now(UTC)
        if started.tzinfo is None:
            started = started.replace(tzinfo=UTC)
        start_time = perf_counter()
        output_root = Path(output_directory)
        output_root.mkdir(parents=True, exist_ok=True)
        run_name = run_id or started.strftime("run_%Y%m%dT%H%M%SZ")
        run_directory = output_root / run_name
        run_directory.mkdir(parents=True, exist_ok=True)
        log: list[dict[str, Any]] = []
        generated: dict[str, str] = {}
        status = "success"
        error: str | None = None
        video_details: dict[str, Any] | None = None
        try:
            video = self.load_video(video_path)
            video_details = {
                "filename": video.filename,
                "path": str(video.path),
                "duration_seconds": video.duration,
                "frame_count": video.frame_count,
                "fps": video.fps,
                "width": video.width,
                "height": video.height,
                "codec": video.metadata.codec,
            }
            generated["video"] = str(_copy_video(video.path, run_directory / "video"))
            _log(log, "video_loaded", start_time, f"Loaded {video.filename}")

            pose_result = self.estimate_pose(video, frame_skip=frame_skip)
            landmarks_dir = run_directory / "landmarks"
            landmarks_csv, landmarks_json = self.pose_estimator.export_landmarks(
                pose_result,
                landmarks_dir / "landmarks.csv",
                landmarks_dir / "landmarks.json",
            )
            generated["landmarks_csv"] = str(landmarks_csv)
            generated["landmarks_json"] = str(landmarks_json)
            _log(log, "pose_estimated", start_time, "Exported MediaPipe landmarks")

            feature_result = self.extract_features(video, pose_result)
            features_dir = run_directory / "features"
            feature_paths = self.feature_extractor.export(feature_result, features_dir)
            generated.update({f"features_{key}": str(path) for key, path in feature_paths.items()})
            _log(log, "features_extracted", start_time, "Exported Prompt-3-compatible features")

            report_paths = self.generate_report(feature_result.feature_table, run_directory / "athlete_report")
            generated.update({f"athlete_report_{key}": str(path) for key, path in report_paths.items()})
            _log(log, "report_generated", start_time, "Generated run-local athlete report")

            dashboard_paths = self.generate_dashboard(
                feature_result.feature_table,
                run_directory / "dashboard",
                report_paths,
            )
            generated.update({f"dashboard_{key}": str(path) for key, path in dashboard_paths.items()})
            _log(log, "dashboard_generated", start_time, "Generated run-local dashboard")
        except Exception as exc:
            status = "failed"
            error = f"{type(exc).__name__}: {exc}"
            _log(log, "failed", start_time, error)

        duration = perf_counter() - start_time
        metadata = self._metadata(
            started=started,
            duration=duration,
            status=status,
            error=error,
            generated=generated,
            log=log,
            video_details=video_details,
        )
        metadata_path = run_directory / "metadata.json"
        generated["metadata"] = str(metadata_path)
        metadata["output_locations"] = dict(sorted(generated.items()))
        metadata_path.write_text(
            json.dumps(_json_ready(metadata), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        if status != "success":
            raise PipelineExecutionError(error or "Pipeline failed.", PipelineResult(run_directory, metadata, generated))
        return PipelineResult(run_directory=run_directory, metadata=metadata, generated_files=generated)

    def load_video(self, video_path: str | Path) -> Video:
        """Load a video through the Prompt 9 Video abstraction."""

        return Video(video_path)

    def estimate_pose(self, video: Video, *, frame_skip: int = 1) -> Any:
        """Estimate landmarks using the configured Prompt 10 pose estimator."""

        return self.pose_estimator.estimate(video, frame_skip=frame_skip)

    def extract_features(self, video: Video, pose_result: Any) -> Any:
        """Extract Prompt-3-compatible features using Prompt 11."""

        return self.feature_extractor.extract_video(
            video,
            pose_result=pose_result,
            metadata=ExtractionMetadata(trial_name=video.filename, condition="uploaded"),
        )

    def generate_report(self, feature_table: pd.DataFrame, output_dir: str | Path) -> dict[str, Path]:
        """Generate run-local Markdown, HTML, and JSON reports."""

        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        payload = {
            "summary": "Run-local uploaded-video report generated from existing pipeline outputs.",
            "feature_table": _json_records(feature_table),
            "safety_statement": (
                "This report is descriptive. It does not diagnose injury, estimate risk, "
                "or introduce clinical interpretation."
            ),
        }
        json_path = destination / "athlete_report.json"
        md_path = destination / "athlete_report.md"
        html_path = destination / "athlete_report.html"
        json_path.write_text(
            json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        md_path.write_text(_render_run_report_markdown(payload), encoding="utf-8")
        html_path.write_text(_render_run_report_html(payload), encoding="utf-8")
        return {"json": json_path, "markdown": md_path, "html": html_path}

    def generate_dashboard(
        self,
        feature_table: pd.DataFrame,
        output_dir: str | Path,
        report_paths: dict[str, Path],
    ) -> dict[str, Path]:
        """Generate a run-local static dashboard for current feature table."""

        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        payload = {
            "feature_table": _json_records(feature_table),
            "feature_count": int(feature_table.shape[1] - 5),
            "reports": {key: str(path) for key, path in report_paths.items()},
            "safety_statement": (
                "Dashboard coordinates current run outputs only. No models are trained "
                "and no clinical interpretations are produced."
            ),
        }
        json_path = destination / "dashboard_payload.json"
        html_path = destination / "index.html"
        json_path.write_text(
            json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        html_path.write_text(_render_run_dashboard_html(payload), encoding="utf-8")
        return {"json": json_path, "html": html_path}

    def _metadata(
        self,
        *,
        started: datetime,
        duration: float,
        status: str,
        error: str | None,
        generated: dict[str, str],
        log: list[dict[str, Any]],
        video_details: dict[str, Any] | None,
    ) -> dict[str, Any]:
        try:
            import mediapipe as mp

            mediapipe_version = getattr(mp, "__version__", None)
        except Exception:
            mediapipe_version = None
        feature_count = len(self.feature_extractor.feature_names)
        return {
            "execution_timestamp": started.isoformat(),
            "processing_duration_seconds": duration,
            "status": status,
            "error": error,
            "mediapipe_version": mediapipe_version,
            "video": video_details,
            "frame_count": None if video_details is None else video_details["frame_count"],
            "feature_count": feature_count,
            "output_locations": dict(sorted(generated.items())),
            "log": log,
            "predictions_generated": False,
        }


class PipelineExecutionError(RuntimeError):
    """Raised for graceful pipeline failures with a partial result."""

    def __init__(self, message: str, result: PipelineResult) -> None:
        super().__init__(message)
        self.result = result


def _copy_video(source: Path, destination_dir: Path) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / source.name
    shutil.copy2(source, destination)
    return destination


def _log(log: list[dict[str, Any]], stage: str, start_time: float, message: str) -> None:
    log.append(
        {
            "stage": stage,
            "elapsed_seconds": perf_counter() - start_time,
            "message": message,
        }
    )


def _render_run_report_markdown(payload: dict[str, Any]) -> str:
    return (
        "# JumpGuard Uploaded Video Report\n\n"
        f"{payload['safety_statement']}\n\n"
        "## Summary\n\n"
        f"{payload['summary']}\n\n"
        "## Feature Table\n\n"
        "```json\n"
        + json.dumps(_json_ready(payload["feature_table"]), indent=2, sort_keys=True)
        + "\n```\n"
    )


def _render_run_report_html(payload: dict[str, Any]) -> str:
    return (
        "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<title>JumpGuard Uploaded Video Report</title>"
        "<style>body{font-family:Arial,sans-serif;max-width:1000px;margin:32px auto;line-height:1.45;}"
        "pre{background:#f0f4f8;padding:12px;overflow:auto;}</style></head><body>"
        "<h1>JumpGuard Uploaded Video Report</h1>"
        f"<p>{escape(payload['safety_statement'])}</p>"
        f"<p>{escape(payload['summary'])}</p>"
        "<h2>Feature Table</h2><pre>"
        + escape(json.dumps(_json_ready(payload["feature_table"]), indent=2, sort_keys=True))
        + "</pre></body></html>\n"
    )


def _render_run_dashboard_html(payload: dict[str, Any]) -> str:
    return (
        "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<title>JumpGuard Run Dashboard</title>"
        "<style>body{font-family:Arial,sans-serif;max-width:1100px;margin:32px auto;line-height:1.45;}"
        "pre{background:#f0f4f8;padding:12px;overflow:auto;}a{color:#0b65c2;}</style></head><body>"
        "<h1>JumpGuard Run Dashboard</h1>"
        f"<p>{escape(payload['safety_statement'])}</p>"
        f"<p>Feature count: {payload['feature_count']}</p>"
        "<h2>Reports</h2>"
        + "".join(
            f"<p>{escape(name)}: <a href=\"../athlete_report/{Path(path).name}\">{escape(Path(path).name)}</a></p>"
            for name, path in payload["reports"].items()
        )
        + "<h2>Feature Table</h2><pre>"
        + escape(json.dumps(_json_ready(payload["feature_table"]), indent=2, sort_keys=True))
        + "</pre></body></html>\n"
    )


def _json_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return _json_ready(frame.to_dict(orient="records"))


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    try:
        import numpy as np

        if isinstance(value, np.integer):
            return int(value)
        if isinstance(value, np.floating):
            return None if np.isnan(value) else float(value)
    except Exception:
        pass
    if isinstance(value, float) and pd.isna(value):
        return None
    return value
