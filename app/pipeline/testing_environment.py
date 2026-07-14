"""Prompt 19 testing-environment orchestration.

This layer coordinates existing JumpGuard pipeline outputs for a local testing
application. It does not alter pose estimation, landmarks, features,
biomechanics, evidence interpretation, reports, dashboards, or model outputs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any, Protocol

import json
import re
import shutil

from src.video_processing import SUPPORTED_VIDEO_EXTENSIONS

from .frame_analysis import InteractiveAnalysisError, InteractiveAnalysisResult, InteractiveFrameAnalyzer


DEFAULT_CONFIG_PATH = Path("config/testing_environment.json")


class PipelineLike(Protocol):
    """Subset of the interactive analyzer used by the testing environment."""

    def process_video(
        self,
        video_path: str | Path,
        output_directory: str | Path,
        *,
        run_id: str,
        frame_skip: int = 1,
        timestamp: datetime | None = None,
    ) -> InteractiveAnalysisResult:
        """Process a video and return interactive frame-analysis artifacts."""


@dataclass(frozen=True)
class TestingEnvironmentConfig:
    """Configuration for the local JumpGuard testing environment."""

    __test__ = False

    input_dir: Path = Path("exports/testing_environment/uploads")
    output_dir: Path = Path("exports/testing_environment/runs")
    logs_dir: Path = Path("logs/testing_environment")
    frame_skip: int = 1
    max_upload_mb: int = 512
    allowed_extensions: tuple[str, ...] = SUPPORTED_VIDEO_EXTENSIONS
    confidence_threshold: float | None = None
    annotated_video_codec: str = "MJPG"
    future_model_selection: str = "mediapipe_pose_landmarker_lite"

    @classmethod
    def load(cls, path: str | Path = DEFAULT_CONFIG_PATH) -> "TestingEnvironmentConfig":
        """Load configuration from JSON, falling back to safe defaults."""

        config_path = Path(path)
        if not config_path.exists():
            return cls()
        payload = json.loads(config_path.read_text(encoding="utf-8"))
        return cls(
            input_dir=Path(payload.get("input_dir", cls.input_dir)),
            output_dir=Path(payload.get("output_dir", cls.output_dir)),
            logs_dir=Path(payload.get("logs_dir", cls.logs_dir)),
            frame_skip=int(payload.get("frame_skip", cls.frame_skip)),
            max_upload_mb=int(payload.get("max_upload_mb", cls.max_upload_mb)),
            allowed_extensions=tuple(payload.get("allowed_extensions", cls.allowed_extensions)),
            confidence_threshold=payload.get("confidence_threshold"),
            annotated_video_codec=str(payload.get("annotated_video_codec", cls.annotated_video_codec)),
            future_model_selection=str(payload.get("future_model_selection", cls.future_model_selection)),
        )

    def ensure_directories(self) -> None:
        """Create app-owned upload, output, and log directories."""

        for directory in (self.input_dir, self.output_dir, self.logs_dir):
            directory.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class TestingEnvironmentResult:
    """Single testing-environment run summary."""

    __test__ = False

    run_id: str
    status: str
    run_directory: Path
    uploaded_video: Path
    generated_files: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    log_path: Path | None = None
    manifest_path: Path | None = None
    error: str | None = None

    @property
    def annotated_video(self) -> str | None:
        """Return the existing annotated-video artifact path when available."""

        return self.generated_files.get("annotated_video")

    @property
    def per_frame_measurements_csv(self) -> str | None:
        """Return the per-frame measurement CSV path when available."""

        return self.generated_files.get("per_frame_measurements_csv")

    @property
    def interactive_viewer_html(self) -> str | None:
        """Return the synchronized interactive viewer path when available."""

        return self.generated_files.get("interactive_viewer_html")

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic JSON-ready run summary."""

        return {
            "run_id": self.run_id,
            "status": self.status,
            "run_directory": str(self.run_directory),
            "uploaded_video": str(self.uploaded_video),
            "generated_files": dict(sorted(self.generated_files.items())),
            "metadata": self.metadata,
            "log_path": None if self.log_path is None else str(self.log_path),
            "manifest_path": None if self.manifest_path is None else str(self.manifest_path),
            "error": self.error,
            "experimental_notice": experimental_notice(),
        }


class TestingEnvironment:
    """Thin app wrapper around the existing JumpGuardPipeline."""

    __test__ = False

    def __init__(
        self,
        config: TestingEnvironmentConfig | None = None,
        *,
        analyzer: PipelineLike | None = None,
    ) -> None:
        self.config = config or TestingEnvironmentConfig.load()
        self.config.ensure_directories()
        self.analyzer = analyzer or InteractiveFrameAnalyzer()

    def save_upload(self, filename: str, content: bytes, *, run_id: str | None = None) -> Path:
        """Validate and persist one uploaded video without altering it."""

        if not content:
            raise TestingEnvironmentError("Uploaded file is empty.")
        max_bytes = self.config.max_upload_mb * 1024 * 1024
        if len(content) > max_bytes:
            raise TestingEnvironmentError(
                f"Uploaded file exceeds {self.config.max_upload_mb} MB limit."
            )
        safe_name = _safe_filename(filename)
        suffix = Path(safe_name).suffix.lower()
        if suffix not in {extension.lower() for extension in self.config.allowed_extensions}:
            raise TestingEnvironmentError(
                f"Unsupported upload extension {suffix!r}. Allowed: {', '.join(self.config.allowed_extensions)}."
            )
        upload_run_id = run_id or _new_run_id()
        upload_dir = self.config.input_dir / upload_run_id
        upload_dir.mkdir(parents=True, exist_ok=True)
        destination = upload_dir / safe_name
        destination.write_bytes(content)
        return destination

    def analyze_video(
        self,
        video_path: str | Path,
        *,
        run_id: str | None = None,
    ) -> TestingEnvironmentResult:
        """Run interactive frame analysis and collect app-facing outputs."""

        started = datetime.now(UTC)
        start_time = perf_counter()
        video = Path(video_path)
        analysis_run_id = run_id or _new_run_id(video.stem)
        log_path = self.config.logs_dir / f"{analysis_run_id}.log"
        _write_log(log_path, f"Starting JumpGuard testing run {analysis_run_id}")
        _write_log(log_path, f"Input video: {video}")
        _write_log(log_path, f"{experimental_notice()}")
        generated: dict[str, str] = {}
        metadata: dict[str, Any] = {}
        status = "success"
        error: str | None = None
        run_directory = self.config.output_dir / analysis_run_id
        try:
            analysis_result = self.analyzer.process_video(
                video,
                self.config.output_dir,
                run_id=analysis_run_id,
                frame_skip=self.config.frame_skip,
                timestamp=started,
            )
            generated = dict(analysis_result.generated_files)
            metadata = dict(analysis_result.metadata)
            run_directory = analysis_result.run_directory
            _write_log(log_path, "Interactive frame analysis completed successfully.")
        except InteractiveAnalysisError as exc:
            status = "failed"
            error = str(exc)
            generated = dict(exc.result.generated_files)
            metadata = dict(exc.result.metadata)
            run_directory = exc.result.run_directory
            _write_log(log_path, f"Interactive analysis failed gracefully: {error}")
        except Exception as exc:  # UI safety net; scientific behavior is untouched.
            status = "failed"
            error = f"{type(exc).__name__}: {exc}"
            run_directory.mkdir(parents=True, exist_ok=True)
            _write_log(log_path, f"Unexpected app-layer failure: {error}")
        duration = perf_counter() - start_time
        metadata.setdefault("testing_environment", {})
        metadata["testing_environment"].update(
            {
                "run_id": analysis_run_id,
                "status": status,
                "app_duration_seconds": duration,
                "config": _config_summary(self.config),
                "experimental_notice": experimental_notice(),
                "workflow": "interactive_frame_by_frame",
            }
        )
        result = TestingEnvironmentResult(
            run_id=analysis_run_id,
            status=status,
            run_directory=run_directory,
            uploaded_video=video,
            generated_files=generated,
            metadata=metadata,
            log_path=log_path,
            error=error,
        )
        manifest_path = run_directory / "testing_environment_manifest.json"
        manifest_result = TestingEnvironmentResult(
            run_id=result.run_id,
            status=result.status,
            run_directory=result.run_directory,
            uploaded_video=result.uploaded_video,
            generated_files=result.generated_files,
            metadata=result.metadata,
            log_path=result.log_path,
            manifest_path=manifest_path,
            error=result.error,
        )
        manifest_path.write_text(
            json.dumps(_json_ready(manifest_result.to_dict()), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        _write_log(log_path, f"Wrote testing manifest: {manifest_path}")
        return manifest_result

    def analyze_upload(self, filename: str, content: bytes) -> TestingEnvironmentResult:
        """Persist an upload and analyze it through the existing pipeline."""

        run_id = _new_run_id(Path(filename).stem)
        upload_path = self.save_upload(filename, content, run_id=run_id)
        return self.analyze_video(upload_path, run_id=run_id)

    def export_bundle(self, result: TestingEnvironmentResult, destination: str | Path) -> Path:
        """Copy generated run artifacts into a user-selected export directory."""

        export_dir = Path(destination)
        export_dir.mkdir(parents=True, exist_ok=True)
        for key, path_text in result.generated_files.items():
            source = Path(path_text)
            if source.exists() and source.is_file():
                target = export_dir / f"{key}{source.suffix}"
                shutil.copy2(source, target)
        if result.manifest_path and result.manifest_path.exists():
            shutil.copy2(result.manifest_path, export_dir / result.manifest_path.name)
        if result.log_path and result.log_path.exists():
            shutil.copy2(result.log_path, export_dir / result.log_path.name)
        return export_dir


class TestingEnvironmentError(ValueError):
    """Raised when the testing app cannot accept or prepare an upload."""

    __test__ = False


def experimental_notice() -> str:
    """Return the Prompt 19 experimental-report notice."""

    return (
        "JumpGuard AI frame-by-frame outputs are clinician-selected measurements only. "
        "No landing event, peak flexion moment, initial contact, ACL risk, diagnosis, "
        "recommendation, or athlete-versus-reference comparison is inferred."
    )


def _safe_filename(filename: str) -> str:
    name = Path(filename or "uploaded_video.mp4").name
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    return cleaned or "uploaded_video.mp4"


def _new_run_id(prefix: str = "run") -> str:
    safe_prefix = re.sub(r"[^A-Za-z0-9_-]+", "_", prefix).strip("_") or "run"
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"{safe_prefix}_{timestamp}"


def _write_log(path: Path, message: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).isoformat()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"[{timestamp}] {message}\n")


def _config_summary(config: TestingEnvironmentConfig) -> dict[str, Any]:
    return {
        "input_dir": str(config.input_dir),
        "output_dir": str(config.output_dir),
        "logs_dir": str(config.logs_dir),
        "frame_skip": config.frame_skip,
        "max_upload_mb": config.max_upload_mb,
        "allowed_extensions": list(config.allowed_extensions),
        "confidence_threshold": config.confidence_threshold,
        "annotated_video_codec": config.annotated_video_codec,
        "future_model_selection": config.future_model_selection,
    }


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    return value
