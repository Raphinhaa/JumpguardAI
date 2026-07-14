"""End-to-end orchestration for the JumpGuard AI pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from time import perf_counter
from typing import Any

import json

import pandas as pd

from .feature_extraction import ExtractionMetadata
from .feature_extraction import FeatureExtractor as LandmarkFeatureExtractor
from .evidence_interpretation import (
    EvidenceBasedInterpreter,
    export_evidence_outputs,
    load_reference_feature_table,
)
from .evidence_report_rendering import evidence_report_css, render_evidence_observations_html
from .pose_estimation import (
    MediaPipePoseEstimator,
    PoseEstimator,
    export_annotated_video,
    export_browser_compatible_video,
)
from .video_processing import SUPPORTED_VIDEO_EXTENSIONS, Video


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

            annotated_video = self.export_video(video, pose_result, run_directory / "video")
            generated["video"] = str(annotated_video)
            _log(log, "video_annotated", start_time, "Exported annotated MediaPipe video")

            feature_result = self.extract_features(video, pose_result)
            features_dir = run_directory / "features"
            feature_paths = self.feature_extractor.export(feature_result, features_dir)
            generated.update({f"features_{key}": str(path) for key, path in feature_paths.items()})
            _log(log, "features_extracted", start_time, "Exported Prompt-3-compatible features")

            evidence_result = self.generate_evidence(feature_result.feature_table)
            evidence_paths = export_evidence_outputs(evidence_result, run_directory)
            generated.update({f"evidence_{key}": str(path) for key, path in evidence_paths.items()})
            evidence_observations = _json_records(evidence_result.observations)
            _log(log, "evidence_interpreted", start_time, "Exported evidence-based observations")

            report_paths = self.generate_report(
                feature_result.feature_table,
                run_directory / "athlete_report",
                video_path=annotated_video,
                evidence_observations=evidence_observations,
            )
            generated.update({f"athlete_report_{key}": str(path) for key, path in report_paths.items()})
            _log(log, "report_generated", start_time, "Generated run-local athlete report")

            dashboard_paths = self.generate_dashboard(
                feature_result.feature_table,
                run_directory / "dashboard",
                report_paths,
                video_path=annotated_video,
                evidence_observations=evidence_observations,
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

    def export_video(self, video: Video, pose_result: Any, output_dir: str | Path) -> Path:
        """Export the canonical annotated video using the Prompt 10 utility."""

        destination = Path(output_dir)
        _clear_video_exports(destination)
        avi_path = export_annotated_video(
            video,
            pose_result,
            destination / f"{video.path.stem}_annotated.avi",
        )
        mp4_result = export_browser_compatible_video(avi_path)
        return mp4_result.mp4_path or avi_path

    def generate_evidence(self, feature_table: pd.DataFrame) -> Any:
        """Generate Prompt 13 evidence observations using the reference dataset when available."""

        reference = load_reference_feature_table()
        if reference is None:
            reference = feature_table
        return EvidenceBasedInterpreter().interpret_feature_table(feature_table, reference)

    def generate_report(
        self,
        feature_table: pd.DataFrame,
        output_dir: str | Path,
        *,
        video_path: str | Path | None = None,
        evidence_observations: list[dict[str, Any]] | None = None,
    ) -> dict[str, Path]:
        """Generate run-local Markdown, HTML, and JSON reports."""

        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        payload = {
            "summary": "Run-local uploaded-video report generated from existing pipeline outputs.",
            "video": None if video_path is None else str(video_path),
            "evidence_based_observations": evidence_observations or [],
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
        html_path.write_text(
            _render_run_report_html(
                payload,
                asset_dir=destination / "evidence_assets",
                asset_href_prefix="evidence_assets/",
            ),
            encoding="utf-8",
        )
        return {"json": json_path, "markdown": md_path, "html": html_path}

    def generate_dashboard(
        self,
        feature_table: pd.DataFrame,
        output_dir: str | Path,
        report_paths: dict[str, Path],
        *,
        video_path: str | Path | None = None,
        evidence_observations: list[dict[str, Any]] | None = None,
    ) -> dict[str, Path]:
        """Generate a run-local static dashboard for current feature table."""

        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        payload = {
            "feature_table": _json_records(feature_table),
            "feature_count": int(feature_table.shape[1] - 5),
            "video": None if video_path is None else str(video_path),
            "evidence_based_observations": evidence_observations or [],
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


def _clear_video_exports(destination_dir: Path) -> None:
    destination_dir.mkdir(parents=True, exist_ok=True)
    for path in destination_dir.iterdir():
        if path.is_file() and path.suffix.lower() in SUPPORTED_VIDEO_EXTENSIONS:
            path.unlink()


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
        + _markdown_video_reference(payload)
        + _markdown_evidence_reference(payload)
        + "## Feature Table\n\n"
        "```json\n"
        + json.dumps(_json_ready(payload["feature_table"]), indent=2, sort_keys=True)
        + "\n```\n"
    )


def _render_run_report_html(
    payload: dict[str, Any],
    *,
    asset_dir: str | Path | None = None,
    asset_href_prefix: str = "",
) -> str:
    return (
        "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        "<title>JumpGuard Uploaded Video Report</title>"
        "<style>"
        + evidence_report_css()
        + "pre{background:#f0f4f8;padding:12px;overflow:auto;border-radius:6px;}"
        + "</style></head><body><main class=\"report-shell\">"
        "<header class=\"report-header\"><h1>JumpGuard Uploaded Video Report</h1>"
        f"<p>{escape(payload['safety_statement'])}</p></header>"
        f"<section class=\"summary-card\"><h2>Summary</h2><p>{escape(payload['summary'])}</p>"
        + _html_video_reference(payload)
        + "</section>"
        + render_evidence_observations_html(
            payload.get("evidence_based_observations") or [],
            asset_dir=asset_dir,
            asset_href_prefix=asset_href_prefix,
            filename_prefix="run_evidence_observation",
        )
        + "<section class=\"simple-card\"><h2>Feature Table</h2><pre>"
        + escape(json.dumps(_json_ready(payload["feature_table"]), indent=2, sort_keys=True))
        + "</pre></section></main></body></html>\n"
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
        + _html_video_reference(payload)
        + _html_evidence_reference(payload)
        + "<h2>Reports</h2>"
        + "".join(
            f"<p>{escape(name)}: <a href=\"../athlete_report/{Path(path).name}\">{escape(Path(path).name)}</a></p>"
            for name, path in payload["reports"].items()
        )
        + "<h2>Feature Table</h2><pre>"
        + escape(json.dumps(_json_ready(payload["feature_table"]), indent=2, sort_keys=True))
        + "</pre></body></html>\n"
    )


def _markdown_video_reference(payload: dict[str, Any]) -> str:
    if not payload.get("video"):
        return ""
    return f"## Annotated Video\n\n{payload['video']}\n\n"


def _html_video_reference(payload: dict[str, Any]) -> str:
    if not payload.get("video"):
        return ""
    path = Path(payload["video"])
    return f"<h2>Annotated Video</h2><p><a href=\"../video/{escape(path.name)}\">{escape(path.name)}</a></p>"


def _markdown_evidence_reference(payload: dict[str, Any]) -> str:
    observations = payload.get("evidence_based_observations") or []
    if not observations:
        return "## Evidence-Based ACL Biomechanical Observations\n\n_No evidence-based observations generated._\n\n"
    return (
        "## Evidence-Based ACL Biomechanical Observations\n\n"
        "```json\n"
        + json.dumps(_json_ready(observations), indent=2, sort_keys=True)
        + "\n```\n\n"
    )


def _html_evidence_reference(payload: dict[str, Any]) -> str:
    observations = payload.get("evidence_based_observations") or []
    if not observations:
        return "<h2>Evidence-Based Observations</h2><p>No evidence-based observations generated.</p>"
    return (
        "<h2>Evidence-Based Observations</h2><pre>"
        + escape(json.dumps(_json_ready(observations), indent=2, sort_keys=True))
        + "</pre>"
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
