"""Tests for Prompt 19 JumpGuard AI testing environment."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import json
import pandas as pd
import pytest

from app.pipeline import TestingEnvironment, TestingEnvironmentConfig
from app.pipeline.frame_analysis import build_frame_measurement_database, render_interactive_viewer_html
from app.pipeline.hip_validation_audit import (
    build_hip_discrepancy_investigation,
    build_hip_validation_audit,
    export_hip_discrepancy_investigation,
    export_hip_validation_audit,
)
from app.pipeline.measurement_debug import export_measurement_debug_raw, render_measurement_debugger_html
from app.pipeline.testing_environment import TestingEnvironmentError
from app.ui.server import render_home, render_result
from app.pipeline.frame_analysis import InteractiveAnalysisError, InteractiveAnalysisResult


class FakeAnalyzer:
    """Small test double that preserves the interactive analyzer contract."""

    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.calls: list[dict[str, Any]] = []

    def process_video(
        self,
        video_path: str | Path,
        output_directory: str | Path = "reports",
        *,
        run_id: str | None = None,
        frame_skip: int = 1,
        timestamp: datetime | None = None,
    ) -> InteractiveAnalysisResult:
        self.calls.append(
            {
                "video_path": str(video_path),
                "output_directory": str(output_directory),
                "run_id": run_id,
                "frame_skip": frame_skip,
                "timestamp": timestamp,
            }
        )
        run_dir = Path(output_directory) / (run_id or "run_fake")
        run_dir.mkdir(parents=True, exist_ok=True)
        metadata_path = run_dir / "metadata.json"
        generated = {"metadata": str(metadata_path)}
        metadata = {
            "status": "failed" if self.fail else "success",
            "processed_frame_count": 3,
            "automatic_reports_generated": False,
            "automatic_reference_comparison_generated": False,
            "automatic_clinical_interpretation_generated": False,
        }
        if self.fail:
            metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
            result = InteractiveAnalysisResult(run_dir, metadata, generated)
            raise InteractiveAnalysisError("fake interactive failure", result)

        video = run_dir / "video" / "jump_annotated.mp4"
        debug_video = run_dir / "video" / "jump_annotated.avi"
        measurements = run_dir / "measurements" / "per_frame_measurements.csv"
        measurements_json = run_dir / "measurements" / "per_frame_measurements.json"
        time_series = run_dir / "measurements" / "time_series.json"
        viewer = run_dir / "interactive_viewer.html"
        debug_viewer = run_dir / "measurement_debug" / "measurement_debugger.html"
        debug_raw_csv = run_dir / "measurement_debug" / "measurement_debug_raw.csv"
        debug_raw_json = run_dir / "measurement_debug" / "measurement_debug_raw.json"
        hip_report = run_dir / "measurement_debug" / "hip_measurement_validation_report.md"
        hip_json = run_dir / "measurement_debug" / "hip_measurement_validation_report.json"
        hip_investigation_report = run_dir / "measurement_debug" / "hip_discrepancy_investigation_report.md"
        hip_investigation_json = run_dir / "measurement_debug" / "hip_discrepancy_investigation_report.json"
        hip_investigation_html = run_dir / "measurement_debug" / "hip_discrepancy_investigation_report.html"
        landmarks = run_dir / "landmarks" / "landmarks.csv"
        for path in (
            video,
            debug_video,
            measurements,
            measurements_json,
            time_series,
            viewer,
            debug_viewer,
            debug_raw_csv,
            debug_raw_json,
            hip_report,
            hip_json,
            hip_investigation_report,
            hip_investigation_json,
            hip_investigation_html,
            landmarks,
        ):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(path.name, encoding="utf-8")
        generated.update(
            {
                "annotated_video": str(video),
                "annotated_video_mp4": str(video),
                "annotated_video_debug_avi": str(debug_video),
                "per_frame_measurements_csv": str(measurements),
                "per_frame_measurements_json": str(measurements_json),
                "time_series_json": str(time_series),
                "interactive_viewer_html": str(viewer),
                "measurement_debugger_html": str(debug_viewer),
                "measurement_debug_raw_csv": str(debug_raw_csv),
                "measurement_debug_raw_json": str(debug_raw_json),
                "hip_measurement_validation_report": str(hip_report),
                "hip_measurement_validation_json": str(hip_json),
                "hip_discrepancy_investigation_report": str(hip_investigation_report),
                "hip_discrepancy_investigation_json": str(hip_investigation_json),
                "hip_discrepancy_investigation_html": str(hip_investigation_html),
                "landmarks_csv": str(landmarks),
            }
        )
        metadata["output_locations"] = generated
        metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
        return InteractiveAnalysisResult(run_dir, metadata, generated)


def _config(tmp_path: Path) -> TestingEnvironmentConfig:
    return TestingEnvironmentConfig(
        input_dir=tmp_path / "uploads",
        output_dir=tmp_path / "runs",
        logs_dir=tmp_path / "logs",
        frame_skip=4,
        max_upload_mb=1,
    )


def test_testing_environment_analyzes_upload_and_collects_interactive_outputs(tmp_path: Path) -> None:
    analyzer = FakeAnalyzer()
    environment = TestingEnvironment(_config(tmp_path), analyzer=analyzer)

    result = environment.analyze_upload("jump test.mp4", b"video-bytes")

    assert result.status == "success"
    assert result.annotated_video and result.annotated_video.endswith("jump_annotated.mp4")
    assert result.generated_files["annotated_video_debug_avi"].endswith("jump_annotated.avi")
    assert result.per_frame_measurements_csv and result.per_frame_measurements_csv.endswith("per_frame_measurements.csv")
    assert result.interactive_viewer_html and result.interactive_viewer_html.endswith("interactive_viewer.html")
    assert result.generated_files["measurement_debugger_html"].endswith("measurement_debugger.html")
    assert result.generated_files["measurement_debug_raw_csv"].endswith("measurement_debug_raw.csv")
    assert result.generated_files["hip_measurement_validation_report"].endswith("hip_measurement_validation_report.md")
    assert result.generated_files["hip_discrepancy_investigation_html"].endswith("hip_discrepancy_investigation_report.html")
    assert not any("athlete_report" in key for key in result.generated_files)
    assert not any("evidence" in key for key in result.generated_files)
    assert not any("dashboard" in key for key in result.generated_files)
    assert result.log_path and result.log_path.exists()
    assert result.manifest_path and result.manifest_path.exists()
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert "No landing event" in manifest["experimental_notice"]
    assert analyzer.calls[0]["frame_skip"] == 4
    assert Path(analyzer.calls[0]["video_path"]).name == "jump_test.mp4"


def test_testing_environment_rejects_invalid_upload_extension(tmp_path: Path) -> None:
    environment = TestingEnvironment(_config(tmp_path), analyzer=FakeAnalyzer())

    with pytest.raises(TestingEnvironmentError, match="Unsupported upload extension"):
        environment.save_upload("jump.webm", b"video-bytes")


def test_testing_environment_gracefully_returns_failed_pipeline_result(tmp_path: Path) -> None:
    environment = TestingEnvironment(_config(tmp_path), analyzer=FakeAnalyzer(fail=True))
    upload = environment.save_upload("jump.mp4", b"video-bytes", run_id="run_bad")

    result = environment.analyze_video(upload, run_id="run_bad")

    assert result.status == "failed"
    assert result.error == "fake interactive failure"
    assert result.log_path and "Interactive analysis failed gracefully" in result.log_path.read_text(encoding="utf-8")
    assert result.manifest_path and result.manifest_path.exists()


def test_testing_environment_ui_renders_upload_and_result(tmp_path: Path) -> None:
    environment = TestingEnvironment(_config(tmp_path), analyzer=FakeAnalyzer())
    result = environment.analyze_upload("jump.mp4", b"video-bytes")

    home = render_home()
    page = render_result(result)

    assert "Upload Jump-Landing Video" in home
    assert "Analyze" in home
    assert "Annotated Video" in page
    assert "type='video/mp4'" in page
    assert "Per-Frame Measurements" in page
    assert "Open Professional Workstation" in page
    assert "Interactive Biomechanics Review Ready" in page
    assert "Processing log" in page
    assert "athlete report" not in page.lower()


def test_frame_measurement_database_values_match_selected_frame() -> None:
    joint_angles = pd.DataFrame(
        [
            {
                "frame_number": 2,
                "timestamp": 0.08,
                "hip_flexion_right": 101.0,
                "hip_flexion_left": 102.0,
                "knee_flexion_right": 121.0,
                "knee_flexion_left": 122.0,
                "ankle_angle_right": 91.0,
                "ankle_angle_left": 92.0,
            }
        ]
    )
    landmarks = pd.DataFrame(
        [
            {
                "frame_number": 2,
                "timestamp": 0.08,
                "landmark_index": 25,
                "landmark_name": "left_knee",
                "x": 0.1,
                "y": 0.2,
                "z": 0.3,
                "visibility": 0.9,
                "confidence": 0.8,
            }
        ]
    )

    database = build_frame_measurement_database(joint_angles, landmarks)

    assert database[0]["frame_index"] == 2
    assert database[0]["timestamp"] == 0.08
    assert database[0]["measurements"]["knee_flexion_left"] == 122.0
    assert database[0]["measurements"]["ankle_angle_right"] == 91.0
    assert database[0]["landmark_confidence"]["mean"] == 0.8
    assert database[0]["derived_measurements"]["delta_from_previous_frame"]["knee_flexion_left"] is None
    assert database[0]["derived_measurements"]["symmetry"]["knee_flexion"]["absolute_difference"] == 1.0
    assert database[0]["derived_measurements"]["trunk"]["available"] is False


def test_frame_measurement_database_computes_frame_delta_and_symmetry_with_existing_formulas() -> None:
    joint_angles = pd.DataFrame(
        [
            {
                "frame_number": 1,
                "timestamp": 0.04,
                "hip_flexion_right": 100.0,
                "hip_flexion_left": 110.0,
                "knee_flexion_right": 80.0,
                "knee_flexion_left": 100.0,
                "ankle_angle_right": 70.0,
                "ankle_angle_left": 90.0,
            },
            {
                "frame_number": 2,
                "timestamp": 0.08,
                "hip_flexion_right": 103.0,
                "hip_flexion_left": 111.0,
                "knee_flexion_right": 85.0,
                "knee_flexion_left": 105.0,
                "ankle_angle_right": 72.0,
                "ankle_angle_left": 96.0,
            },
        ]
    )
    landmarks = pd.DataFrame(
        [
            {
                "frame_number": frame,
                "timestamp": frame * 0.04,
                "landmark_index": 25,
                "landmark_name": "left_knee",
                "x": 0.1,
                "y": 0.2,
                "z": 0.3,
                "visibility": 0.9,
                "confidence": 0.8,
            }
            for frame in (1, 2)
        ]
    )

    database = build_frame_measurement_database(joint_angles, landmarks)

    second = database[1]
    assert second["derived_measurements"]["delta_from_previous_frame"]["knee_flexion_left"] == 5.0
    assert second["derived_measurements"]["symmetry"]["knee_flexion"]["absolute_difference"] == 20.0
    assert round(second["derived_measurements"]["symmetry"]["knee_flexion"]["percent_difference"], 6) == round(100 * 20 / 95, 6)
    assert round(second["derived_measurements"]["symmetry"]["knee_flexion"]["symmetry_index"], 6) == round(100 * 20 / 95, 6)


def test_interactive_viewer_contains_professional_workstation_controls_and_no_report_language() -> None:
    frame_database = [
        {
            "frame_index": 0,
            "timestamp": 0.0,
            "measurements": {
                "hip_flexion_left": 100.0,
                "hip_flexion_right": 90.0,
                "knee_flexion_left": 120.0,
                "knee_flexion_right": 110.0,
                "ankle_angle_left": 80.0,
                "ankle_angle_right": 75.0,
            },
            "derived_measurements": {
                "delta_from_previous_frame": {},
                "symmetry": {
                    "hip_flexion": {"absolute_difference": 10.0, "percent_difference": 10.5, "symmetry_index": 10.5},
                    "knee_flexion": {"absolute_difference": 10.0, "percent_difference": 8.7, "symmetry_index": 8.7},
                    "ankle_angle": {"absolute_difference": 5.0, "percent_difference": 6.4, "symmetry_index": 6.4},
                },
                "trunk": {"available": False, "reason": "No trunk angle signal is produced."},
            },
            "landmark_confidence": {"mean": 0.9, "minimum": 0.8, "visible_landmark_count": 33, "mean_visibility": 0.9},
            "landmarks": [],
        }
    ]

    html = render_interactive_viewer_html(
        frame_database,
        video_path="video/jump.mp4",
        source_video={"filename": "jump.mp4", "duration_seconds": 1.2, "frame_count": 30, "fps": 25.0},
        generated_files={
            "annotated_video_mp4": "video/jump.mp4",
            "per_frame_measurements_csv": "measurements/per_frame_measurements.csv",
            "per_frame_measurements_json": "measurements/per_frame_measurements.json",
            "time_series_json": "measurements/time_series.json",
            "measurement_debugger_html": "measurement_debug/measurement_debugger.html",
        },
    )

    assert "Jump to time" in html
    assert "JumpGuard AI" in html
    assert "Clinical Biomechanical Analysis Workspace" in html
    assert "Measurement-only workspace" in html
    assert "Session Summary" in html
    assert "Processed frames" in html
    assert "Camera-facing limb" in html
    assert "Exports" in html
    assert "Annotated MP4" in html
    assert "Per-frame CSV" in html
    assert "Measurement Debugger" in html
    assert "Measurement Definitions" in html
    assert "High Confidence" in html
    assert "Low Confidence" in html
    assert "Camera-Facing Limb" in html
    assert "Left Knee Flexion" in html
    assert "Frame-to-Frame Change" in html
    assert "Left/Right Symmetry" in html
    assert "Knee Flexion Over Time" in html
    assert "graphTooltip" in html
    assert "0 reference" in html
    assert "°" in html
    assert "score_percent" not in html
    assert "Frame Confidence" not in html
    assert "Overall Frame Confidence" not in html
    assert "Overall confidence" not in html
    assert '<source src="/artifact?path=video/jump.mp4" type="video/mp4">' in html
    assert '<video id="video" controls preload="metadata" playsinline muted>' in html
    assert "Annotated Video" in html
    assert "playbackSpeed" in html
    assert "Fullscreen" in html
    assert "Space play/pause" in html
    assert "ArrowLeft" in html
    assert "ArrowRight" in html
    assert "Selected Frame" in html
    assert "Joint Angles" in html
    assert "Frame-to-Frame Change" in html
    assert "Left/Right Symmetry" in html
    assert "deltaGraph" in html
    assert "symmetryGraph" in html
    assert "current-frame cursor" in html
    assert "Selected-Frame Left/Right Comparison" in html
    assert "trunkUnavailable" in html
    assert "isTimelineDragging" in html
    assert "resumeAfterTimelineDrag" in html
    assert 'id="overlay"' not in html
    assert "overlay.innerHTML" not in html
    assert "No automatic events" in html
    assert "athlete report" not in html.lower()
    assert "risk summary" not in html.lower()


def test_interactive_viewer_reports_browser_video_warning() -> None:
    html = render_interactive_viewer_html([], video_path="video/jump.avi", source_video={}, video_warning="FFmpeg unavailable")

    assert "Browser Playback Warning" in html
    assert "FFmpeg unavailable" in html


def test_measurement_debugger_exports_diagnostic_artifacts_without_recomputing_values(tmp_path: Path) -> None:
    frame_database = [
        {
            "frame_index": 4,
            "timestamp": 0.16,
            "measurements": {
                "hip_flexion_left": 101.25,
                "hip_flexion_right": 99.0,
                "knee_flexion_left": 120.5,
                "knee_flexion_right": 118.0,
                "ankle_angle_left": 80.0,
                "ankle_angle_right": 77.0,
            },
            "derived_measurements": {
                "delta_from_previous_frame": {"knee_flexion_left": 2.5},
                "symmetry": {
                    "hip_flexion": {"absolute_difference": 2.25, "percent_difference": 2.24, "symmetry_index": 2.24},
                    "knee_flexion": {"absolute_difference": 2.5, "percent_difference": 2.1, "symmetry_index": 2.1},
                    "ankle_angle": {"absolute_difference": 3.0, "percent_difference": 3.8, "symmetry_index": 3.8},
                },
                "trunk": {"available": False, "reason": "No trunk angle signal is produced."},
            },
            "landmark_confidence": {"mean": 0.9, "minimum": 0.7, "visible_landmark_count": 10, "mean_visibility": 0.8},
            "landmarks": [
                {"frame_number": 4, "timestamp": 0.16, "landmark_index": 11, "landmark_name": "left_shoulder", "x": 0.3, "y": 0.2, "z": 0.1, "visibility": 0.9, "confidence": 0.9},
                {"frame_number": 4, "timestamp": 0.16, "landmark_index": 23, "landmark_name": "left_hip", "x": 0.3, "y": 0.45, "z": 0.1, "visibility": 0.8, "confidence": 0.8},
                {"frame_number": 4, "timestamp": 0.16, "landmark_index": 25, "landmark_name": "left_knee", "x": 0.35, "y": 0.7, "z": 0.1, "visibility": 0.7, "confidence": 0.7},
            ],
        }
    ]

    html = render_measurement_debugger_html(frame_database, source_video={"filename": "jump.mp4"})
    csv_path, json_path = export_measurement_debug_raw(
        frame_database,
        tmp_path / "measurement_debug_raw.csv",
        tmp_path / "measurement_debug_raw.json",
    )

    assert "Developer Measurement Debugger" in html
    assert "Angle Debug Panel" in html
    assert "Landmark Panel" in html
    assert "Confidence Inspector" in html
    assert "Landmark trails" in html
    assert "left_shoulder" in html
    debug_table = pd.read_csv(csv_path)
    hip_left = debug_table[debug_table["signal"].eq("hip_flexion_left")].iloc[0]
    assert hip_left["angle_value"] == 101.25
    assert hip_left["landmarks_used"] == "left_shoulder -> left_hip -> left_knee"
    assert hip_left["measurement_confidence_percent"] == 80.0
    assert hip_left["measurement_confidence_category"] == "Moderate Confidence"
    assert "Measurement Confidence Percentages" in html
    assert "score_percent" in html
    assert "80.0" in html
    assert json.loads(json_path.read_text(encoding="utf-8"))[0]["frame_index"] == 4


def test_camera_aware_confidence_uses_fixed_orientation_and_frame_level_joint_visibility() -> None:
    joint_angles = pd.DataFrame(
        [
            {
                "frame_number": 1,
                "timestamp": 0.04,
                "hip_flexion_right": 101.0,
                "hip_flexion_left": 102.0,
                "knee_flexion_right": 121.0,
                "knee_flexion_left": 122.0,
                "ankle_angle_right": 91.0,
                "ankle_angle_left": 92.0,
            },
            {
                "frame_number": 2,
                "timestamp": 0.08,
                "hip_flexion_right": 103.0,
                "hip_flexion_left": 104.0,
                "knee_flexion_right": 123.0,
                "knee_flexion_left": 124.0,
                "ankle_angle_right": 93.0,
                "ankle_angle_left": 94.0,
            },
        ]
    )
    landmarks = pd.DataFrame(
        _confidence_landmarks(1, left_visibility=0.95, right_visibility=0.35)
        + _confidence_landmarks(2, left_visibility=0.95, right_visibility=0.95, left_knee_visibility=0.45)
    )

    database = build_frame_measurement_database(joint_angles, landmarks)

    first = database[0]
    second = database[1]
    assert first["camera_orientation"]["camera_facing_side"] == "left"
    assert second["camera_orientation"]["camera_facing_side"] == "left"
    assert first["measurement_confidence"]["hip_flexion_left"]["limb_role"] == "Camera-Facing Limb"
    assert first["measurement_confidence"]["hip_flexion_right"]["limb_role"] == "Opposite Limb"
    assert first["measurement_confidence"]["hip_flexion_left"]["category"]["label"] == "High Confidence"
    assert first["measurement_confidence"]["hip_flexion_right"]["category"]["label"] == "Low Confidence"
    assert second["measurement_confidence"]["knee_flexion_left"]["category"]["label"] == "Moderate Confidence"
    assert second["measurements"]["knee_flexion_left"] == 124.0


def test_hip_validation_audit_ranks_existing_hip_differences_and_preserves_values(tmp_path: Path) -> None:
    frame_database = [
        {
            "frame_index": 1,
            "timestamp": 0.04,
            "measurements": {
                "hip_flexion_left": 80.0,
                "hip_flexion_right": 120.0,
                "knee_flexion_left": 100.0,
                "knee_flexion_right": 101.0,
                "ankle_angle_left": 90.0,
                "ankle_angle_right": 91.0,
            },
            "derived_measurements": {
                "delta_from_previous_frame": {"hip_flexion_left": None, "hip_flexion_right": None},
                "symmetry": {
                    "hip_flexion": {"absolute_difference": 40.0, "percent_difference": 40.0, "symmetry_index": -40.0},
                    "knee_flexion": {"absolute_difference": 1.0, "percent_difference": 1.0, "symmetry_index": -1.0},
                    "ankle_angle": {"absolute_difference": 1.0, "percent_difference": 1.0, "symmetry_index": -1.0},
                },
                "trunk": {"available": False, "reason": "No trunk angle signal is produced."},
            },
            "landmark_confidence": {"mean": 0.8, "minimum": 0.4, "visible_landmark_count": 6, "mean_visibility": 0.8},
            "landmarks": _hip_audit_landmarks(1, visibility=0.4),
        },
        {
            "frame_index": 2,
            "timestamp": 0.08,
            "measurements": {
                "hip_flexion_left": 100.0,
                "hip_flexion_right": 105.0,
                "knee_flexion_left": 100.0,
                "knee_flexion_right": 101.0,
                "ankle_angle_left": 90.0,
                "ankle_angle_right": 91.0,
            },
            "derived_measurements": {
                "delta_from_previous_frame": {"hip_flexion_left": 20.0, "hip_flexion_right": -15.0},
                "symmetry": {
                    "hip_flexion": {"absolute_difference": 5.0, "percent_difference": 4.878, "symmetry_index": -4.878},
                    "knee_flexion": {"absolute_difference": 1.0, "percent_difference": 1.0, "symmetry_index": -1.0},
                    "ankle_angle": {"absolute_difference": 1.0, "percent_difference": 1.0, "symmetry_index": -1.0},
                },
                "trunk": {"available": False, "reason": "No trunk angle signal is produced."},
            },
            "landmark_confidence": {"mean": 0.9, "minimum": 0.9, "visible_landmark_count": 6, "mean_visibility": 0.9},
            "landmarks": _hip_audit_landmarks(2, visibility=0.9),
        },
    ]

    audit = build_hip_validation_audit(frame_database, top_n=2)
    report_path, json_path = export_hip_validation_audit(
        frame_database,
        tmp_path / "hip_measurement_validation_report.md",
        tmp_path / "hip_measurement_validation_report.json",
        top_n=2,
    )

    largest = audit["hip_discrepancy_summary"]["largest_differences"][0]
    assert largest["frame_index"] == 1
    assert largest["absolute_difference"] == 40.0
    assert "visibility below 0.5" in "; ".join(largest["evidence_notes"])
    assert audit["measurement_definitions"][0]["convention"].startswith("Unsigned internal")
    assert audit["scope"]["scientific_pipeline_modified"] is False
    assert "Hip Measurement Validation Audit" in report_path.read_text(encoding="utf-8")
    assert json.loads(json_path.read_text(encoding="utf-8"))["scope"]["measurement_values_recomputed"] is False


def test_hip_discrepancy_investigation_exports_evidence_only_reports(tmp_path: Path) -> None:
    frame_database = [
        {
            "frame_index": 7,
            "timestamp": 0.28,
            "measurements": {
                "hip_flexion_left": 72.0,
                "hip_flexion_right": 118.0,
                "knee_flexion_left": 100.0,
                "knee_flexion_right": 101.0,
                "ankle_angle_left": 90.0,
                "ankle_angle_right": 91.0,
            },
            "derived_measurements": {"delta_from_previous_frame": {}, "symmetry": {}, "trunk": {"available": False}},
            "landmark_confidence": {"mean": 0.8, "minimum": 0.3, "visible_landmark_count": 6, "mean_visibility": 0.8},
            "landmarks": _hip_audit_landmarks(7, visibility=0.35),
        }
    ]

    original_frame_database = json.loads(json.dumps(frame_database))
    investigation = build_hip_discrepancy_investigation(frame_database, top_n=1)
    report_path, json_path, html_path = export_hip_discrepancy_investigation(
        frame_database,
        tmp_path / "hip_discrepancy_investigation_report.md",
        tmp_path / "hip_discrepancy_investigation_report.json",
        tmp_path / "hip_discrepancy_investigation_report.html",
        top_n=1,
    )

    assert investigation["prompt_25_scope"]["evidence_only"] is True
    assert investigation["prompt_25_scope"]["scientific_pipeline_modified"] is False
    assert investigation["origin_assessment"]["overall_origin"] == "landmark estimation"
    assert investigation["frame_investigations"][0]["absolute_difference"] == 46.0
    assert "visibility below 0.5" in "; ".join(investigation["frame_investigations"][0]["origin_evidence"])
    assert "camera perspective" in {row["origin"] for row in investigation["origin_assessment"]["candidate_origins"]}
    assert "Hip Discrepancy Investigation" in report_path.read_text(encoding="utf-8")
    assert "Hip Discrepancy Investigation" in html_path.read_text(encoding="utf-8")
    exported = json.loads(json_path.read_text(encoding="utf-8"))
    assert exported["prompt_25_scope"]["automatic_correction_applied"] is False
    assert json.loads(json.dumps(frame_database)) == original_frame_database


def test_hip_discrepancy_investigation_reports_insufficient_evidence_without_finite_pairs() -> None:
    investigation = build_hip_discrepancy_investigation(
        [
            {
                "frame_index": 3,
                "timestamp": 0.12,
                "measurements": {"hip_flexion_left": None, "hip_flexion_right": None},
                "landmarks": _hip_audit_landmarks(3, visibility=0.9),
            }
        ],
        top_n=1,
    )

    assert investigation["origin_assessment"]["overall_origin"] == "insufficient evidence"
    assert investigation["frame_investigations"] == []


def _hip_audit_landmarks(frame_number: int, *, visibility: float) -> list[dict[str, float | int | str]]:
    names = [
        (11, "left_shoulder"),
        (12, "right_shoulder"),
        (23, "left_hip"),
        (24, "right_hip"),
        (25, "left_knee"),
        (26, "right_knee"),
        (27, "left_ankle"),
        (28, "right_ankle"),
    ]
    return [
        {
            "frame_number": frame_number,
            "timestamp": frame_number * 0.04,
            "landmark_index": index,
            "landmark_name": name,
            "x": 0.1 + index / 100,
            "y": 0.2 + index / 100,
            "z": 0.0,
            "visibility": visibility,
            "confidence": visibility,
        }
        for index, name in names
    ]


def _confidence_landmarks(
    frame_number: int,
    *,
    left_visibility: float,
    right_visibility: float,
    left_knee_visibility: float | None = None,
) -> list[dict[str, float | int | str]]:
    names = [
        (11, "left_shoulder", left_visibility),
        (12, "right_shoulder", right_visibility),
        (23, "left_hip", left_visibility),
        (24, "right_hip", right_visibility),
        (25, "left_knee", left_knee_visibility if left_knee_visibility is not None else left_visibility),
        (26, "right_knee", right_visibility),
        (27, "left_ankle", left_visibility),
        (28, "right_ankle", right_visibility),
        (29, "left_heel", left_visibility),
        (30, "right_heel", right_visibility),
        (31, "left_foot_index", left_visibility),
        (32, "right_foot_index", right_visibility),
    ]
    return [
        {
            "frame_number": frame_number,
            "timestamp": frame_number * 0.04,
            "landmark_index": index,
            "landmark_name": name,
            "x": 0.1 + index / 100,
            "y": 0.2 + index / 100,
            "z": 0.0,
            "visibility": visibility,
            "confidence": visibility,
        }
        for index, name, visibility in names
    ]
