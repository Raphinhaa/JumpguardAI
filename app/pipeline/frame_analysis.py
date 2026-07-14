"""Interactive frame-by-frame biomechanical analysis engine.

This module reuses the validated video, pose, annotation, and joint-angle
calculation code paths. It intentionally does not generate athlete reports,
evidence observations, reference comparisons, recommendations, or clinical
interpretations.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any

import json

import numpy as np
import pandas as pd

from app.pipeline.hip_validation_audit import export_hip_discrepancy_investigation, export_hip_validation_audit
from app.pipeline.measurement_debug import export_measurement_debug_raw, render_measurement_debugger_html
from app.ui.artifacts import artifact_href
from src.feature_extraction import ANGLE_SIGNAL_MAP
from src.feature_extraction import FeatureExtractor as LandmarkFeatureExtractor
from src.features.symmetry import absolute_difference, percent_difference, symmetry_index
from src.pose_estimation import (
    MediaPipePoseEstimator,
    PoseEstimator,
    export_annotated_video,
    export_browser_compatible_video,
)
from src.video_processing import Video


ANGLE_COLUMNS: tuple[str, ...] = tuple(ANGLE_SIGNAL_MAP.keys())
JOINT_PAIRS: tuple[tuple[str, str, str], ...] = (
    ("hip_flexion", "hip_flexion_left", "hip_flexion_right"),
    ("knee_flexion", "knee_flexion_left", "knee_flexion_right"),
    ("ankle_angle", "ankle_angle_left", "ankle_angle_right"),
)


@dataclass(frozen=True)
class InteractiveAnalysisResult:
    """Paths and metadata from one clinician-driven interactive analysis."""

    run_directory: Path
    metadata: dict[str, Any]
    generated_files: dict[str, str]


class InteractiveFrameAnalyzer:
    """Generate synchronized per-frame measurements from existing modules."""

    def __init__(
        self,
        *,
        pose_estimator: PoseEstimator | None = None,
        feature_extractor: LandmarkFeatureExtractor | None = None,
    ) -> None:
        default_model_path = Path(__file__).resolve().parents[2] / "models" / "pose_landmarker_lite.task"
        self.pose_estimator = pose_estimator or MediaPipePoseEstimator(model_path=default_model_path)
        self.feature_extractor = feature_extractor or LandmarkFeatureExtractor()

    def process_video(
        self,
        video_path: str | Path,
        output_directory: str | Path,
        *,
        run_id: str,
        frame_skip: int = 1,
        timestamp: datetime | None = None,
    ) -> InteractiveAnalysisResult:
        """Process a video for interactive frame-by-frame review only."""

        started = timestamp or datetime.now(UTC)
        if started.tzinfo is None:
            started = started.replace(tzinfo=UTC)
        start_time = perf_counter()
        run_directory = Path(output_directory) / run_id
        run_directory.mkdir(parents=True, exist_ok=True)
        generated: dict[str, str] = {}
        log: list[dict[str, Any]] = []
        status = "success"
        error: str | None = None
        video_details: dict[str, Any] | None = None
        try:
            video = Video(video_path)
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

            pose_result = self.pose_estimator.estimate(video, frame_skip=frame_skip)
            landmarks_dir = run_directory / "landmarks"
            landmarks_csv, landmarks_json = self.pose_estimator.export_landmarks(
                pose_result,
                landmarks_dir / "landmarks.csv",
                landmarks_dir / "landmarks.json",
            )
            generated["landmarks_csv"] = str(landmarks_csv)
            generated["landmarks_json"] = str(landmarks_json)
            _log(log, "pose_estimated", start_time, "Exported MediaPipe landmarks")

            annotated_video = export_annotated_video(
                video,
                pose_result,
                run_directory / "video" / f"{video.path.stem}_annotated.avi",
            )
            browser_video = export_browser_compatible_video(annotated_video)
            generated["annotated_video_debug_avi"] = str(annotated_video)
            generated["annotated_video"] = str(browser_video.mp4_path or annotated_video)
            if browser_video.mp4_path is not None:
                generated["annotated_video_mp4"] = str(browser_video.mp4_path)
            if browser_video.warning:
                generated["annotated_video_warning"] = browser_video.warning
            _log(log, "video_annotated", start_time, "Exported existing annotated video")
            if browser_video.mp4_path is not None:
                _log(log, "video_mp4_exported", start_time, "Exported browser-compatible annotated MP4")
            else:
                _log(log, "video_mp4_unavailable", start_time, browser_video.warning or "Browser-compatible MP4 unavailable")

            joint_angles = self.feature_extractor.calculate_joint_angles(pose_result.landmarks)
            frame_database = build_frame_measurement_database(joint_angles, pose_result.landmarks)
            measurements_dir = run_directory / "measurements"
            measurements_dir.mkdir(parents=True, exist_ok=True)
            measurements_csv = measurements_dir / "per_frame_measurements.csv"
            measurements_json = measurements_dir / "per_frame_measurements.json"
            time_series_json = measurements_dir / "time_series.json"
            _frame_table(frame_database).to_csv(measurements_csv, index=False, float_format="%.10g")
            measurements_json.write_text(
                json.dumps(_json_ready(frame_database), indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            time_series_json.write_text(
                json.dumps(_json_ready(_time_series_payload(frame_database)), indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            generated["per_frame_measurements_csv"] = str(measurements_csv)
            generated["per_frame_measurements_json"] = str(measurements_json)
            generated["time_series_json"] = str(time_series_json)
            _log(log, "measurements_exported", start_time, "Exported per-frame measurements")

            debug_dir = run_directory / "measurement_debug"
            debug_raw_csv = debug_dir / "measurement_debug_raw.csv"
            debug_raw_json = debug_dir / "measurement_debug_raw.json"
            debug_html = debug_dir / "measurement_debugger.html"
            export_measurement_debug_raw(frame_database, debug_raw_csv, debug_raw_json)
            debug_html.write_text(
                render_measurement_debugger_html(frame_database, source_video=video_details),
                encoding="utf-8",
            )
            generated["measurement_debugger_html"] = str(debug_html)
            generated["measurement_debug_raw_csv"] = str(debug_raw_csv)
            generated["measurement_debug_raw_json"] = str(debug_raw_json)
            _log(log, "measurement_debug_exported", start_time, "Exported developer-only measurement debug artifacts")

            hip_audit_report = debug_dir / "hip_measurement_validation_report.md"
            hip_audit_json = debug_dir / "hip_measurement_validation_report.json"
            export_hip_validation_audit(frame_database, hip_audit_report, hip_audit_json)
            generated["hip_measurement_validation_report"] = str(hip_audit_report)
            generated["hip_measurement_validation_json"] = str(hip_audit_json)
            _log(log, "hip_measurement_validation_exported", start_time, "Exported developer-only hip measurement validation audit")

            hip_investigation_report = debug_dir / "hip_discrepancy_investigation_report.md"
            hip_investigation_json = debug_dir / "hip_discrepancy_investigation_report.json"
            hip_investigation_html = debug_dir / "hip_discrepancy_investigation_report.html"
            export_hip_discrepancy_investigation(
                frame_database,
                hip_investigation_report,
                hip_investigation_json,
                hip_investigation_html,
            )
            generated["hip_discrepancy_investigation_report"] = str(hip_investigation_report)
            generated["hip_discrepancy_investigation_json"] = str(hip_investigation_json)
            generated["hip_discrepancy_investigation_html"] = str(hip_investigation_html)
            _log(log, "hip_discrepancy_investigation_exported", start_time, "Exported developer-only hip discrepancy investigation")

            viewer_html = run_directory / "interactive_viewer.html"
            viewer_html.write_text(
                render_interactive_viewer_html(
                    frame_database,
                    video_path=generated["annotated_video"],
                    video_warning=browser_video.warning,
                    source_video=video_details,
                    generated_files=generated,
                ),
                encoding="utf-8",
            )
            generated["interactive_viewer_html"] = str(viewer_html)
            _log(log, "interactive_viewer_exported", start_time, "Exported synchronized viewer")
        except Exception as exc:
            status = "failed"
            error = f"{type(exc).__name__}: {exc}"
            _log(log, "failed", start_time, error)

        metadata = {
            "execution_timestamp": started.isoformat(),
            "processing_duration_seconds": perf_counter() - start_time,
            "status": status,
            "error": error,
            "video": video_details,
            "frame_count": None if video_details is None else video_details["frame_count"],
            "processed_frame_count": _processed_frame_count(generated.get("per_frame_measurements_csv")),
            "measurement_columns": list(ANGLE_COLUMNS),
            "derived_measurement_columns": [
                "delta_from_previous_frame",
                "absolute_difference",
                "percent_difference",
                "symmetry_index",
            ],
            "automatic_reports_generated": False,
            "automatic_reference_comparison_generated": False,
            "automatic_clinical_interpretation_generated": False,
            "event_detection_generated": False,
            "developer_measurement_debug_generated": "measurement_debugger_html" in generated,
            "developer_hip_validation_generated": "hip_measurement_validation_report" in generated,
            "developer_hip_discrepancy_investigation_generated": "hip_discrepancy_investigation_report" in generated,
            "selected_frame_policy": "Clinician-controlled frame selection only; no event inference.",
            "browser_video_warning": generated.get("annotated_video_warning"),
            "output_locations": dict(sorted(generated.items())),
            "log": log,
        }
        metadata_path = run_directory / "metadata.json"
        generated["metadata"] = str(metadata_path)
        metadata["output_locations"] = dict(sorted(generated.items()))
        metadata_path.write_text(json.dumps(_json_ready(metadata), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if status != "success":
            raise InteractiveAnalysisError(error or "Interactive analysis failed.", InteractiveAnalysisResult(run_directory, metadata, generated))
        return InteractiveAnalysisResult(run_directory, metadata, generated)


class InteractiveAnalysisError(RuntimeError):
    """Raised for graceful interactive-analysis failures with partial output."""

    def __init__(self, message: str, result: InteractiveAnalysisResult) -> None:
        super().__init__(message)
        self.result = result


def build_frame_measurement_database(
    joint_angles: pd.DataFrame,
    landmarks: pd.DataFrame,
) -> list[dict[str, Any]]:
    """Build one JSON-ready frame record per processed frame."""

    records: list[dict[str, Any]] = []
    previous_measurements: dict[str, float | None] | None = None
    for row in joint_angles.sort_values("frame_number").to_dict(orient="records"):
        frame_number = int(row["frame_number"])
        frame_landmarks = landmarks[landmarks["frame_number"].astype(int).eq(frame_number)].copy()
        confidences = pd.to_numeric(frame_landmarks["confidence"], errors="coerce") if "confidence" in frame_landmarks else pd.Series(dtype=float)
        visibility = pd.to_numeric(frame_landmarks["visibility"], errors="coerce") if "visibility" in frame_landmarks else pd.Series(dtype=float)
        measurements = {column: _float_or_none(row.get(column)) for column in ANGLE_COLUMNS}
        deltas = _delta_from_previous(measurements, previous_measurements)
        symmetry = _frame_symmetry(measurements)
        records.append(
            {
                "frame_index": frame_number,
                "timestamp": _float_or_none(row.get("timestamp")),
                "measurements": measurements,
                "derived_measurements": {
                    "delta_from_previous_frame": deltas,
                    "symmetry": symmetry,
                    "trunk": {
                        "available": False,
                        "reason": "No trunk angle signal is produced by the validated Prompt 11 frame-level measurement set.",
                    },
                },
                "landmark_confidence": {
                    "mean": _float_or_none(confidences.mean(skipna=True)),
                    "minimum": _float_or_none(confidences.min(skipna=True)),
                    "visible_landmark_count": int(frame_landmarks[["x", "y", "z"]].dropna().shape[0])
                    if {"x", "y", "z"}.issubset(frame_landmarks.columns)
                    else 0,
                    "mean_visibility": _float_or_none(visibility.mean(skipna=True)),
                },
                "landmarks": _json_ready(frame_landmarks.to_dict(orient="records")),
            }
        )
        previous_measurements = measurements
    return records


def render_interactive_viewer_html(
    frame_database: list[dict[str, Any]],
    *,
    video_path: str | Path,
    source_video: dict[str, Any] | None,
    video_warning: str | None = None,
    generated_files: dict[str, str] | None = None,
) -> str:
    """Render a standalone synchronized frame-by-frame viewer."""

    source = source_video or {}
    session_summary_html = _session_summary_html(source, frame_database)
    export_panel_html = _export_panel_html(generated_files or {}, video_path)
    payload = {
        "frames": frame_database,
        "video": str(video_path),
        "source_video": source,
        "video_warning": video_warning,
        "angle_columns": list(ANGLE_COLUMNS),
        "policy": "No landing event, peak flexion, initial contact, diagnosis, risk, or recommendation is inferred.",
    }
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>JumpGuard AI Clinical Biomechanical Analysis Workspace</title>
  <style>
    :root{{--ink:#17202a;--muted:#52677a;--line:#d7e0ea;--panel:#ffffff;--surface:#f4f7fb;--canvas:#fbfdff;--brand:#12314d;--brand-2:#0b4f8a;--accent:#1665d8;--accent-soft:#e9f2ff;--danger:#d64545;--ok:#1f8a5b;}}
    *{{box-sizing:border-box;}}
    body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;margin:0;background:var(--surface);color:var(--ink);line-height:1.45;}}
    header{{background:var(--brand);color:white;padding:22px 30px;border-bottom:1px solid rgba(255,255,255,.14);}}
    .brand-row{{display:flex;justify-content:space-between;gap:18px;align-items:flex-start;max-width:1520px;margin:0 auto;}}
    .brand-mark{{font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:#a8c7e6;font-weight:800;margin-bottom:6px;}}
    header h1{{font-size:30px;margin:0 0 6px;letter-spacing:0;font-weight:760;}}
    header p{{max-width:1080px;margin:0;color:#dbe8f3;}}
    .status-pill{{display:inline-flex;align-items:center;gap:8px;white-space:nowrap;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);border-radius:999px;padding:8px 12px;color:#eef6ff;font-size:13px;font-weight:700;}}
    .status-dot{{width:9px;height:9px;border-radius:999px;background:#49d18c;display:inline-block;}}
    main{{max-width:1520px;margin:18px auto;padding:0 18px;}}
    .workspace-shell{{display:grid;gap:16px;}}
    .workstation{{display:grid;grid-template-columns:minmax(620px,1.65fr) minmax(390px,.9fr);gap:16px;align-items:start;}}
    .triple{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px;}}
    .panel{{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:16px;margin-bottom:16px;box-shadow:0 1px 2px rgba(16,42,67,.05);}}
    .panel h2{{font-size:18px;margin:0 0 8px;color:#1f3449;}}
    .video-panel{{padding:0;overflow:hidden;}}
    .video-title{{display:flex;justify-content:space-between;gap:12px;align-items:center;padding:16px 18px;border-bottom:1px solid var(--line);background:#fbfdff;}}
    .video-title h2{{font-size:18px;margin:0;}}
    .video-wrap{{position:relative;background:#05080d;overflow:hidden;display:flex;align-items:center;justify-content:center;min-height:360px;}}
    video{{display:block;width:100%;max-height:700px;background:#05080d;object-fit:contain;}}
    .transport{{display:flex;flex-wrap:wrap;gap:10px;align-items:center;padding:14px 16px;border-top:1px solid var(--line);background:#f8fbfe;}}
    .control-group{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:6px 8px;border:1px solid #e4ebf3;border-radius:8px;background:white;}}
    button{{background:var(--accent);color:white;border:0;border-radius:6px;padding:9px 12px;font-weight:750;cursor:pointer;min-height:38px;}}
    button.secondary{{background:#e6edf5;color:#17324d;}}
    button:hover{{filter:brightness(.97);}}
    button:focus,input:focus,select:focus{{outline:3px solid rgba(22,101,216,.24);outline-offset:2px;}}
    input.jump,select{{height:38px;padding:7px 9px;border:1px solid #bcccdc;border-radius:6px;background:white;color:var(--ink);}}
    input.jump{{width:96px;}}
    .timeline-row{{padding:0 16px 16px;background:#f8fbfe;}}
    input[type=range]{{width:100%;accent-color:var(--accent);}}
    .frame-readout{{display:flex;flex-wrap:wrap;gap:12px;margin:10px 0 0;font-size:14px;color:#334e68;}}
    .readout-chip{{display:inline-flex;gap:6px;align-items:center;border:1px solid #dfe8f2;border-radius:999px;background:white;padding:6px 10px;}}
    table{{border-collapse:collapse;width:100%;font-size:14px;}}
    th,td{{border-bottom:1px solid #e6edf5;padding:8px;text-align:left;vertical-align:top;}}
    th{{font-size:12px;text-transform:uppercase;color:#486581;letter-spacing:.04em;background:#f8fbfe;}}
    canvas{{width:100%;height:170px;border:1px solid var(--line);border-radius:6px;background:#fff;display:block;margin:12px 0;}}
    .muted{{color:var(--muted);}}
    .measurement-section{{border:1px solid #e6edf5;border-radius:8px;padding:12px;margin:12px 0;background:#fbfdff;}}
    .measurement-section h3{{font-size:15px;margin:0 0 10px;color:#243b53;}}
    .metric-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;}}
    .metric-card{{border:1px solid #e6edf5;border-radius:8px;padding:10px;background:white;}}
    .metric-card strong{{display:block;margin-bottom:4px;color:#334e68;font-size:12px;text-transform:uppercase;letter-spacing:.04em;}}
    .summary-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;}}
    .summary-card{{border:1px solid #e6edf5;border-radius:8px;background:#fff;padding:12px;min-height:76px;}}
    .summary-card span{{display:block;color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.04em;font-weight:800;margin-bottom:5px;}}
    .summary-card strong{{display:block;font-size:18px;color:#1f3449;word-break:break-word;}}
    .export-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px;margin-top:10px;}}
    .export-link{{display:block;border:1px solid #dbe5ef;border-radius:8px;background:white;padding:11px 12px;color:#12314d;text-decoration:none;font-weight:750;}}
    .export-link span{{display:block;color:var(--muted);font-size:12px;font-weight:650;margin-top:2px;}}
    .export-link:hover{{border-color:#9fc4ed;background:var(--accent-soft);}}
    .graph-heading{{display:flex;justify-content:space-between;gap:12px;align-items:flex-end;}}
    .shortcut{{font-size:13px;color:var(--muted);}}
    .visually-muted{{font-size:13px;color:#627d98;}}
    @media (max-width: 1100px){{.workstation{{grid-template-columns:1fr;}}.brand-row{{flex-direction:column;}}}}
  </style>
</head>
<body>
  <header>
    <div class="brand-row">
      <div>
        <div class="brand-mark">JumpGuard AI</div>
        <h1>Clinical Biomechanical Analysis Workspace</h1>
        <p>Clinician-controlled frame review with synchronized video, measurements, deltas, symmetry indices, and graphs. No automatic events, clinical conclusions, ACL risk, or reference comparison are generated.</p>
      </div>
      <div class="status-pill"><span class="status-dot"></span> Measurement-only workspace</div>
    </div>
  </header>
  <main>
    <div class="workspace-shell">
    <section class="panel">
      <h2>Session Summary</h2>
      {session_summary_html}
    </section>
    <section class="workstation">
      <div class="panel video-panel">
        <div class="video-title">
          <h2>Annotated Video</h2>
          <span class="shortcut">Keyboard: Space play/pause, Left/Right step frames</span>
        </div>
        <div class="video-wrap">
          <video id="video" controls preload="metadata" playsinline muted>
            <source src="{artifact_href(video_path)}" type="{_video_mime_type(video_path)}">
          </video>
        </div>
        {f'<div class="measurement-section"><strong>Browser Playback Warning</strong><br>{_html_escape(video_warning)}</div>' if video_warning else ''}
        <div class="transport" aria-label="Video transport controls">
          <div class="control-group"><button id="play">Play</button><button id="pause" class="secondary">Pause</button></div>
          <div class="control-group"><button id="prev" class="secondary">Previous Frame</button><button id="next" class="secondary">Next Frame</button></div>
          <div class="control-group"><label>Jump to time <input id="jumpTime" class="jump" type="number" step="0.01" min="0" value="0"></label><button id="jumpButton">Jump</button></div>
          <div class="control-group"><label>Speed <select id="playbackSpeed"><option value="0.25">0.25x</option><option value="0.5">0.5x</option><option value="1" selected>1x</option><option value="1.5">1.5x</option><option value="2">2x</option></select></label><button id="fullscreen" class="secondary">Fullscreen</button></div>
        </div>
        <div class="timeline-row">
          <label for="timeline">Timeline</label>
          <input id="timeline" type="range" min="0" max="0" value="0" step="1">
          <div class="frame-readout"><span class="readout-chip"><strong>Selected frame:</strong> <span id="frameLabel">--</span></span><span class="readout-chip"><strong>Timestamp:</strong> <span id="timeLabel">--</span></span></div>
        </div>
      </div>
      <aside class="panel">
        <h2>Live Measurement Panel</h2>
        <p class="muted">Values correspond exactly to the selected processed frame. No interpolation or averaging is applied.</p>
        <div id="frameInfo" class="measurement-section"></div>
        <div id="measurements" class="measurement-section"></div>
        <div id="deltaValues" class="measurement-section"></div>
        <div id="symmetryValues" class="measurement-section"></div>
        <div id="confidencePanel"></div>
      </aside>
    </section>
    <section class="panel">
      <h2>Exports</h2>
      <p class="muted">Existing generated artifacts for review and reproducibility. These links do not trigger reprocessing.</p>
      {export_panel_html}
    </section>
    <section class="panel">
      <div class="graph-heading"><h2>Interactive Time-Series</h2><span class="shortcut">Each graph includes a red current-frame cursor</span></div>
      <p class="muted">Click any graph to pause playback and select the nearest processed frame shown on that graph. Trunk graph is shown only if a validated trunk signal exists.</p>
      <canvas id="kneeGraph" width="1100" height="220"></canvas>
      <canvas id="hipGraph" width="1100" height="220"></canvas>
      <canvas id="ankleGraph" width="1100" height="220"></canvas>
      <canvas id="deltaGraph" width="1100" height="220"></canvas>
      <canvas id="symmetryGraph" width="1100" height="220"></canvas>
      <div id="trunkUnavailable" class="muted">Trunk graph unavailable: no validated trunk angle signal is currently produced.</div>
    </section>
    <section class="panel">
      <h2>Selected-Frame Left/Right Comparison</h2>
      <div class="triple">
        <canvas id="hipBars" width="360" height="240"></canvas>
        <canvas id="kneeBars" width="360" height="240"></canvas>
        <canvas id="ankleBars" width="360" height="240"></canvas>
      </div>
    </section>
    </div>
  </main>
  <script id="analysis-data" type="application/json">{json.dumps(_json_ready(payload), sort_keys=True)}</script>
  <script>
    const data = JSON.parse(document.getElementById('analysis-data').textContent);
    const frames = data.frames || [];
    const video = document.getElementById('video');
    const slider = document.getElementById('timeline');
    const frameLabel = document.getElementById('frameLabel');
    const timeLabel = document.getElementById('timeLabel');
    const frameInfo = document.getElementById('frameInfo');
    const measurements = document.getElementById('measurements');
    const deltaValues = document.getElementById('deltaValues');
    const symmetryValues = document.getElementById('symmetryValues');
    const confidencePanel = document.getElementById('confidencePanel');
    const jumpTime = document.getElementById('jumpTime');
    const playbackSpeed = document.getElementById('playbackSpeed');
    const fullscreen = document.getElementById('fullscreen');
    let selected = 0;
    let isTimelineDragging = false;
    let resumeAfterTimelineDrag = false;
    slider.max = Math.max(frames.length - 1, 0);
    const jointPairs = [
      ['Hip', 'hip_flexion_left', 'hip_flexion_right', 'hip_flexion'],
      ['Knee', 'knee_flexion_left', 'knee_flexion_right', 'knee_flexion'],
      ['Ankle', 'ankle_angle_left', 'ankle_angle_right', 'ankle_angle']
    ];

    function fmt(value, suffix='') {{
      return value === null || value === undefined || Number.isNaN(value) ? 'NaN' : Number(value).toFixed(2) + suffix;
    }}
    function selectFrame(index, seek=true) {{
      if (!frames.length) return;
      selected = Math.max(0, Math.min(frames.length - 1, index));
      const frame = frames[selected];
      slider.value = selected;
      frameLabel.textContent = frame.frame_index;
      timeLabel.textContent = fmt(frame.timestamp, ' s');
      jumpTime.value = Number.isFinite(frame.timestamp) ? Number(frame.timestamp).toFixed(2) : '0';
      if (seek && Number.isFinite(frame.timestamp)) video.currentTime = frame.timestamp;
      const entries = Object.entries(frame.measurements || {{}});
      frameInfo.innerHTML = '<h3>Frame Information</h3><div class="metric-grid">' +
        '<div class="metric-card"><strong>Frame</strong>' + frame.frame_index + '</div>' +
        '<div class="metric-card"><strong>Timestamp</strong>' + fmt(frame.timestamp, ' s') + '</div>' +
        '<div class="metric-card"><strong>Mean Confidence</strong>' + fmt(frame.landmark_confidence?.mean) + '</div>' +
        '</div>';
      measurements.innerHTML = '<h3>Joint Angles</h3><table><thead><tr><th>Measurement</th><th>Degrees</th></tr></thead><tbody>' +
        entries.map(([name, value]) => `<tr><td>${{name}}</td><td>${{fmt(value)}}</td></tr>`).join('') +
        '</tbody></table>';
      const deltas = frame.derived_measurements?.delta_from_previous_frame || {{}};
      const symmetry = frame.derived_measurements?.symmetry || {{}};
      deltaValues.innerHTML = '<h3>Delta Values</h3><table><thead><tr><th>Signal</th><th>Delta</th></tr></thead><tbody>' +
        Object.entries(deltas).map(([name, value]) => `<tr><td>${{name}}</td><td>${{fmt(value)}} deg</td></tr>`).join('') +
        '</tbody></table>';
      symmetryValues.innerHTML = '<h3>Symmetry Indices</h3><table><thead><tr><th>Joint</th><th>Abs Diff</th><th>% Diff</th><th>Sym Index</th></tr></thead><tbody>' +
        Object.entries(symmetry).map(([name, values]) => `<tr><td>${{name}}</td><td>${{fmt(values.absolute_difference)}} deg</td><td>${{fmt(values.percent_difference)}}%</td><td>${{fmt(values.symmetry_index)}}%</td></tr>`).join('') +
        '</tbody></table><div class="metric-card"><strong>Trunk</strong>' + (frame.derived_measurements?.trunk?.reason || 'Unavailable') + '</div>';
      confidencePanel.innerHTML = '<h3>Landmark Confidence</h3>' +
        '<div class="metric-grid"><div class="metric-card"><strong>Mean confidence</strong>' + fmt(frame.landmark_confidence?.mean) + '</div>' +
        '<div class="metric-card"><strong>Minimum confidence</strong>' + fmt(frame.landmark_confidence?.minimum) + '</div>' +
        '<div class="metric-card"><strong>Visible landmarks</strong>' + (frame.landmark_confidence?.visible_landmark_count ?? 'NaN') + '</div></div>';
      drawGraphs();
      drawComparisonBars();
    }}
    function frameFromTime(time) {{
      if (!frames.length) return 0;
      let best = 0, bestDelta = Infinity;
      frames.forEach((frame, i) => {{
        const delta = Math.abs((frame.timestamp || 0) - time);
        if (delta < bestDelta) {{ best = i; bestDelta = delta; }}
      }});
      return best;
    }}
    function valueFor(frame, key, source='measurements') {{
      if (source === 'delta') return frame.derived_measurements?.delta_from_previous_frame?.[key];
      if (source === 'symmetry') {{
        const [joint, metric] = key.split(':');
        return frame.derived_measurements?.symmetry?.[joint]?.[metric];
      }}
      return frame.measurements?.[key];
    }}
    function drawGraph(canvasId, title, keys, colors, source='measurements') {{
      const canvas = document.getElementById(canvasId);
      const ctx = canvas.getContext('2d');
      const w = canvas.width, h = canvas.height;
      ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = '#17202a'; ctx.font = '18px Arial'; ctx.fillText(title, 18, 26);
      const values = [];
      keys.forEach(k => frames.forEach(f => {{ const v = valueFor(f, k, source); if (Number.isFinite(v)) values.push(v); }}));
      const min = values.length ? Math.min(...values) : 0;
      const max = values.length ? Math.max(...values) : 1;
      const pad = 42;
      ctx.strokeStyle = '#d9e2ec'; ctx.beginPath(); ctx.moveTo(pad, h-pad); ctx.lineTo(w-pad, h-pad); ctx.lineTo(w-pad, pad); ctx.stroke();
      keys.forEach((key, keyIndex) => {{
        ctx.strokeStyle = colors[keyIndex]; ctx.lineWidth = 2; ctx.beginPath();
        frames.forEach((frame, i) => {{
          const v = valueFor(frame, key, source);
          if (!Number.isFinite(v)) return;
          const x = pad + (frames.length <= 1 ? 0 : i / (frames.length - 1)) * (w - 2*pad);
          const y = h - pad - ((v - min) / (max - min || 1)) * (h - 2*pad);
          if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        }});
        ctx.stroke();
        ctx.fillStyle = colors[keyIndex]; ctx.fillText(key.replace(':', ' '), pad + keyIndex * 250, h - 12);
      }});
      const markerX = pad + (frames.length <= 1 ? 0 : selected / (frames.length - 1)) * (w - 2*pad);
      ctx.strokeStyle = '#d64545'; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(markerX, pad); ctx.lineTo(markerX, h-pad); ctx.stroke();
      canvas.onclick = event => {{
        video.pause();
        const rect = canvas.getBoundingClientRect();
        const ratio = Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width));
        selectFrame(Math.round(ratio * (frames.length - 1)));
      }};
    }}
    function drawGraphs() {{
      drawGraph('kneeGraph', 'Knee Angles', ['knee_flexion_left','knee_flexion_right'], ['#1f77b4','#ff7f0e']);
      drawGraph('hipGraph', 'Hip Angles', ['hip_flexion_left','hip_flexion_right'], ['#2ca02c','#9467bd']);
      drawGraph('ankleGraph', 'Ankle Angles', ['ankle_angle_left','ankle_angle_right'], ['#8c564b','#17becf']);
      drawGraph('deltaGraph', 'Frame-to-Frame Delta Values', ['knee_flexion_left','knee_flexion_right','hip_flexion_left','hip_flexion_right'], ['#1f77b4','#ff7f0e','#2ca02c','#9467bd'], 'delta');
      drawGraph('symmetryGraph', 'Frame-Level Symmetry Index', ['hip_flexion:symmetry_index','knee_flexion:symmetry_index','ankle_angle:symmetry_index'], ['#2ca02c','#1f77b4','#8c564b'], 'symmetry');
    }}
    function drawBar(canvasId, title, left, right) {{
      const canvas = document.getElementById(canvasId);
      const ctx = canvas.getContext('2d');
      const w = canvas.width, h = canvas.height;
      ctx.clearRect(0,0,w,h);
      ctx.fillStyle = '#17202a'; ctx.font = '18px Arial'; ctx.fillText(title, 16, 28);
      const values = [left, right].filter(Number.isFinite);
      const max = values.length ? Math.max(...values, 1) : 1;
      [['Left', left, '#1f77b4'], ['Right', right, '#ff7f0e']].forEach((item, i) => {{
        const [label, value, color] = item;
        const x = 64 + i * 120;
        const barHeight = Number.isFinite(value) ? (value / max) * 145 : 0;
        ctx.fillStyle = color;
        ctx.fillRect(x, h - 42 - barHeight, 70, barHeight);
        ctx.fillStyle = '#17202a'; ctx.font = '14px Arial';
        ctx.fillText(label, x + 12, h - 18);
        ctx.fillText(fmt(value), x + 4, h - 50 - barHeight);
      }});
    }}
    function drawComparisonBars() {{
      if (!frames.length) return;
      const frame = frames[selected];
      drawBar('hipBars', 'Hip Left/Right', frame.measurements?.hip_flexion_left, frame.measurements?.hip_flexion_right);
      drawBar('kneeBars', 'Knee Left/Right', frame.measurements?.knee_flexion_left, frame.measurements?.knee_flexion_right);
      drawBar('ankleBars', 'Ankle Left/Right', frame.measurements?.ankle_angle_left, frame.measurements?.ankle_angle_right);
    }}
    document.getElementById('play').onclick = () => video.play();
    document.getElementById('pause').onclick = () => video.pause();
    document.getElementById('prev').onclick = () => {{ video.pause(); selectFrame(selected - 1); }};
    document.getElementById('next').onclick = () => {{ video.pause(); selectFrame(selected + 1); }};
    document.getElementById('jumpButton').onclick = () => {{ video.pause(); selectFrame(frameFromTime(Number(jumpTime.value || 0))); }};
    playbackSpeed.onchange = () => {{ video.playbackRate = Number(playbackSpeed.value || 1); }};
    fullscreen.onclick = () => {{
      const target = document.querySelector('.video-wrap');
      if (target.requestFullscreen) target.requestFullscreen();
    }};
    slider.onpointerdown = () => {{ isTimelineDragging = true; resumeAfterTimelineDrag = !video.paused; video.pause(); }};
    slider.oninput = () => {{ selectFrame(Number(slider.value)); }};
    slider.onpointerup = () => {{ isTimelineDragging = false; if (resumeAfterTimelineDrag) video.play(); }};
    video.ontimeupdate = () => {{ if (!isTimelineDragging) selectFrame(frameFromTime(video.currentTime), false); }};
    document.addEventListener('keydown', event => {{
      if (event.target && ['INPUT','SELECT','TEXTAREA'].includes(event.target.tagName)) return;
      if (event.code === 'Space') {{ event.preventDefault(); video.paused ? video.play() : video.pause(); }}
      if (event.code === 'ArrowLeft') {{ event.preventDefault(); video.pause(); selectFrame(selected - 1); }}
      if (event.code === 'ArrowRight') {{ event.preventDefault(); video.pause(); selectFrame(selected + 1); }}
    }});
    selectFrame(0, false);
  </script>
</body>
</html>
"""


def _frame_table(frame_database: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for frame in frame_database:
        row = {
            "frame_index": frame["frame_index"],
            "timestamp": frame["timestamp"],
            "landmark_confidence_mean": frame["landmark_confidence"]["mean"],
            "landmark_confidence_minimum": frame["landmark_confidence"]["minimum"],
            "landmark_visibility_mean": frame["landmark_confidence"]["mean_visibility"],
            "visible_landmark_count": frame["landmark_confidence"]["visible_landmark_count"],
        }
        row.update(frame["measurements"])
        for column, value in frame["derived_measurements"]["delta_from_previous_frame"].items():
            row[f"delta_{column}"] = value
        for joint, values in frame["derived_measurements"]["symmetry"].items():
            row[f"{joint}_absolute_difference"] = values["absolute_difference"]
            row[f"{joint}_percent_difference"] = values["percent_difference"]
            row[f"{joint}_symmetry_index"] = values["symmetry_index"]
        rows.append(row)
    return pd.DataFrame(rows)


def _time_series_payload(frame_database: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "frame_index": [frame["frame_index"] for frame in frame_database],
        "timestamp": [frame["timestamp"] for frame in frame_database],
        "measurements": {
            column: [frame["measurements"].get(column) for frame in frame_database]
            for column in ANGLE_COLUMNS
        },
        "delta_from_previous_frame": {
            column: [frame["derived_measurements"]["delta_from_previous_frame"].get(column) for frame in frame_database]
            for column in ANGLE_COLUMNS
        },
        "symmetry": {
            joint: {
                metric: [frame["derived_measurements"]["symmetry"][joint].get(metric) for frame in frame_database]
                for metric in ("absolute_difference", "percent_difference", "symmetry_index")
            }
            for joint, _, _ in JOINT_PAIRS
        },
        "policy": "Frame-level series only; no event inference or interpolation.",
    }


def _delta_from_previous(
    measurements: dict[str, float | None],
    previous_measurements: dict[str, float | None] | None,
) -> dict[str, float | None]:
    deltas: dict[str, float | None] = {}
    for column in ANGLE_COLUMNS:
        current = measurements.get(column)
        previous = None if previous_measurements is None else previous_measurements.get(column)
        deltas[column] = None if current is None or previous is None else float(current - previous)
    return deltas


def _frame_symmetry(measurements: dict[str, float | None]) -> dict[str, dict[str, float | None]]:
    summary: dict[str, dict[str, float | None]] = {}
    for joint, left_key, right_key in JOINT_PAIRS:
        left = measurements.get(left_key)
        right = measurements.get(right_key)
        if left is None or right is None:
            summary[joint] = {
                "absolute_difference": None,
                "percent_difference": None,
                "symmetry_index": None,
            }
            continue
        summary[joint] = {
            "absolute_difference": _float_or_none(absolute_difference(left, right)),
            "percent_difference": _float_or_none(percent_difference(left, right)),
            "symmetry_index": _float_or_none(symmetry_index(left, right)),
        }
    return summary


def _processed_frame_count(csv_path: str | None) -> int | None:
    if not csv_path or not Path(csv_path).exists():
        return None
    try:
        return int(pd.read_csv(csv_path, usecols=["frame_index"]).shape[0])
    except Exception:
        return None


def _log(log: list[dict[str, Any]], stage: str, start_time: float, message: str) -> None:
    log.append({"stage": stage, "elapsed_seconds": perf_counter() - start_time, "message": message})


def _float_or_none(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return None if not np.isfinite(number) else number


def _session_summary_html(source_video: dict[str, Any], frame_database: list[dict[str, Any]]) -> str:
    confidence_values = [
        _float_or_none(frame.get("landmark_confidence", {}).get("mean"))
        for frame in frame_database
    ]
    finite_confidence = [value for value in confidence_values if value is not None]
    mean_confidence = None if not finite_confidence else float(np.mean(finite_confidence))
    cards = [
        ("Uploaded file", source_video.get("filename") or "Unknown"),
        ("Duration", _format_seconds(source_video.get("duration_seconds"))),
        ("Source frames", _format_count(source_video.get("frame_count"))),
        ("Processed frames", _format_count(len(frame_database))),
        ("Frame rate", _format_rate(source_video.get("fps"))),
        ("Pose confidence", _format_number(mean_confidence)),
    ]
    return "<div class=\"summary-grid\">" + "".join(
        f"<div class=\"summary-card\"><span>{_html_escape(label)}</span><strong>{_html_escape(value)}</strong></div>"
        for label, value in cards
    ) + "</div>"


def _export_panel_html(generated_files: dict[str, str], video_path: str | Path) -> str:
    exports = [
        ("Annotated MP4", generated_files.get("annotated_video_mp4") or str(video_path), "Browser playback video"),
        ("Annotated debug AVI", generated_files.get("annotated_video_debug_avi"), "Debug video artifact"),
        ("Per-frame CSV", generated_files.get("per_frame_measurements_csv"), "Measurements table"),
        ("Per-frame JSON", generated_files.get("per_frame_measurements_json"), "Frame database"),
        ("Time-series JSON", generated_files.get("time_series_json"), "Graph source data"),
        ("Landmarks CSV", generated_files.get("landmarks_csv"), "MediaPipe landmarks"),
        ("Measurement Debugger", generated_files.get("measurement_debugger_html"), "Developer diagnostic viewer"),
        ("Hip Investigation", generated_files.get("hip_discrepancy_investigation_html"), "Developer evidence report"),
    ]
    links = []
    for label, path, description in exports:
        if not path:
            continue
        links.append(
            f"<a class=\"export-link\" href=\"{artifact_href(path)}\">{_html_escape(label)}<span>{_html_escape(description)}</span></a>"
        )
    if not links:
        return "<p class=\"muted\">No export artifacts were provided to this viewer.</p>"
    return "<div class=\"export-grid\">" + "".join(links) + "</div>"


def _format_seconds(value: Any) -> str:
    number = _float_or_none(value)
    return "Unknown" if number is None else f"{number:.2f} s"


def _format_rate(value: Any) -> str:
    number = _float_or_none(value)
    return "Unknown" if number is None else f"{number:.2f} fps"


def _format_number(value: Any) -> str:
    number = _float_or_none(value)
    return "Unknown" if number is None else f"{number:.2f}"


def _format_count(value: Any) -> str:
    try:
        return str(int(value))
    except (TypeError, ValueError):
        return "Unknown"


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return None if np.isnan(value) else float(value)
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def _html_escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _video_mime_type(video_path: str | Path) -> str:
    return "video/mp4" if Path(video_path).suffix.lower() == ".mp4" else "video/x-msvideo"
