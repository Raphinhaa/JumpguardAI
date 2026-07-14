"""Developer-only hip measurement validation audit.

This module reads existing Prompt 23 frame/debug records and produces an audit
report. It does not change landmark extraction, angle math, feature extraction,
CSV/JSON schemas, graph generation, or numerical outputs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from html import escape
import json

import numpy as np
import pandas as pd

from src.feature_extraction import ANGLE_SIGNAL_MAP


LOWER_BODY_LANDMARKS: tuple[str, ...] = (
    "left_shoulder",
    "right_shoulder",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
)


def export_hip_validation_audit(
    frame_database: list[dict[str, Any]],
    report_path: str | Path,
    json_path: str | Path,
    *,
    top_n: int = 10,
) -> tuple[Path, Path]:
    """Export a developer-only audit of existing hip measurements."""

    report_destination = Path(report_path)
    json_destination = Path(json_path)
    report_destination.parent.mkdir(parents=True, exist_ok=True)
    audit = build_hip_validation_audit(frame_database, top_n=top_n)
    json_destination.write_text(json.dumps(_json_ready(audit), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_destination.write_text(render_hip_validation_report(audit), encoding="utf-8")
    return report_destination, json_destination


def export_hip_discrepancy_investigation(
    frame_database: list[dict[str, Any]],
    report_path: str | Path,
    json_path: str | Path,
    html_path: str | Path,
    *,
    top_n: int = 10,
) -> tuple[Path, Path, Path]:
    """Export Prompt 25 developer-only hip discrepancy investigation artifacts."""

    report_destination = Path(report_path)
    json_destination = Path(json_path)
    html_destination = Path(html_path)
    report_destination.parent.mkdir(parents=True, exist_ok=True)
    investigation = build_hip_discrepancy_investigation(frame_database, top_n=top_n)
    json_destination.write_text(json.dumps(_json_ready(investigation), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_destination.write_text(render_hip_discrepancy_investigation_report(investigation), encoding="utf-8")
    html_destination.write_text(render_hip_discrepancy_investigation_html(investigation), encoding="utf-8")
    return report_destination, json_destination, html_destination


def build_hip_validation_audit(frame_database: list[dict[str, Any]], *, top_n: int = 10) -> dict[str, Any]:
    """Build audit data from already-computed frame records."""

    return {
        "scope": {
            "purpose": "Investigate observed left/right hip measurement differences using existing diagnostic outputs.",
            "scientific_pipeline_modified": False,
            "measurement_values_recomputed": False,
            "notes": "Angles, deltas, symmetry values, landmarks, confidence, and visibility are read from existing frame records.",
        },
        "measurement_definitions": _measurement_definitions(),
        "hip_discrepancy_summary": _hip_discrepancies(frame_database, top_n=top_n),
        "confidence_summary": _confidence_summary(frame_database),
        "findings": _findings(frame_database),
        "recommendations": _recommendations(),
    }


def build_hip_discrepancy_investigation(frame_database: list[dict[str, Any]], *, top_n: int = 10) -> dict[str, Any]:
    """Build Prompt 25 evidence-only hip discrepancy investigation data."""

    audit = build_hip_validation_audit(frame_database, top_n=top_n)
    frame_investigations = _hip_frame_investigations(frame_database, top_n=top_n)
    audit.update(
        {
            "prompt_25_scope": {
                "purpose": "Investigate likely origins of observed left/right hip measurement discrepancies using existing Prompt 23/24 diagnostics.",
                "evidence_only": True,
                "scientific_pipeline_modified": False,
                "automatic_correction_applied": False,
                "notes": "This investigation reads existing measurements, landmarks, confidence, visibility, and vector geometry for developer review only.",
            },
            "origin_assessment": _origin_assessment(frame_investigations),
            "frame_investigations": frame_investigations,
        }
    )
    return audit


def render_hip_validation_report(audit: dict[str, Any]) -> str:
    """Render a Markdown audit report."""

    lines = [
        "# Hip Measurement Validation Audit",
        "",
        "Developer-only scientific audit generated from existing Prompt 23 diagnostics.",
        "No biomechanics calculations, landmark extraction, feature extraction, exports, or numerical outputs are modified by this report.",
        "",
        "## Measurement Definitions",
        "",
        "| Signal | Landmarks | Vertex | Vector A | Vector B | Formula | Convention | Range | Interpretation Boundary |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row in audit["measurement_definitions"]:
        lines.append(
            "| {signal} | {landmarks} | {vertex} | {vector_a} | {vector_b} | {formula} | {convention} | {expected_range_degrees} | {interpretation_boundary} |".format(
                **{key: _md(value) for key, value in row.items()}
            )
        )
    lines.extend([
        "",
        "## Largest Observed Hip Differences",
        "",
        "Frames are ranked by the existing computed absolute left/right hip angle difference. No clinical threshold is applied.",
        "",
        "| Rank | Frame | Timestamp | Left Hip | Right Hip | Abs Diff | Left Visibility Min | Right Visibility Min | Evidence Notes |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in audit["hip_discrepancy_summary"]["largest_differences"]:
        lines.append(
            f"| {row['rank']} | {row['frame_index']} | {_fmt(row['timestamp'])} | {_fmt(row['hip_flexion_left'])} | {_fmt(row['hip_flexion_right'])} | {_fmt(row['absolute_difference'])} | {_fmt(row['left_visibility_min'])} | {_fmt(row['right_visibility_min'])} | {_md('; '.join(row['evidence_notes']))} |"
        )
    lines.extend([
        "",
        "## Confidence And Visibility Summary",
        "",
        "| Landmark | Frames | Visibility Mean | Visibility Min | Missing Visibility Frames | Confidence Mean | Confidence Min | Missing Confidence Frames |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in audit["confidence_summary"]:
        lines.append(
            f"| {row['landmark_name']} | {row['frame_count']} | {_fmt(row['visibility_mean'])} | {_fmt(row['visibility_min'])} | {row['visibility_missing_frames']} | {_fmt(row['confidence_mean'])} | {_fmt(row['confidence_min'])} | {row['confidence_missing_frames']} |"
        )
    lines.extend([
        "",
        "## Findings",
        "",
    ])
    for finding in audit["findings"]:
        lines.append(f"- **{finding['status']}**: {finding['text']}")
    lines.extend([
        "",
        "## Recommendations For Future Work",
        "",
    ])
    for recommendation in audit["recommendations"]:
        lines.append(f"- {recommendation}")
    lines.append("")
    return "\n".join(lines)


def render_hip_discrepancy_investigation_report(investigation: dict[str, Any]) -> str:
    """Render the Prompt 25 evidence-only investigation as Markdown."""

    origin = investigation["origin_assessment"]
    lines = [
        "# Hip Discrepancy Investigation",
        "",
        "Developer-only Prompt 25 investigation generated from existing Measurement Debug Mode records.",
        "No MediaPipe extraction, landmark generation, angle mathematics, feature extraction, graphs, schemas, clinician workstation behavior, or numerical outputs are modified by this report.",
        "",
        "## Origin Assessment",
        "",
        f"- **Overall origin:** {origin['overall_origin']}",
        f"- **Evidence standard:** {origin['evidence_standard']}",
        f"- **Summary:** {origin['summary']}",
        "",
        "| Candidate Origin | Status | Evidence |",
        "|---|---|---|",
    ]
    for candidate in origin["candidate_origins"]:
        lines.append(
            f"| {_md(candidate['origin'])} | {_md(candidate['status'])} | {_md('; '.join(candidate['evidence']))} |"
        )
    lines.extend(
        [
            "",
            "## Ranked Frame Investigations",
            "",
            "Frames are ranked by the existing computed absolute left/right hip angle difference. Confidence rank is informational only and does not change measurements.",
            "",
            "| Rank | Frame | Timestamp | Left Hip | Right Hip | Abs Diff | Confidence Rank | Origin Evidence |",
            "|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in investigation["frame_investigations"]:
        lines.append(
            f"| {row['rank']} | {row['frame_index']} | {_fmt(row['timestamp'])} | {_fmt(row['hip_flexion_left'])} | {_fmt(row['hip_flexion_right'])} | {_fmt(row['absolute_difference'])} | {row['confidence_rank']} | {_md('; '.join(row['origin_evidence']))} |"
        )
    lines.extend(["", "## Per-Frame Landmark And Vector Evidence", ""])
    for row in investigation["frame_investigations"]:
        lines.extend(
            [
                f"### Rank {row['rank']} - Frame {row['frame_index']}",
                "",
                f"- Timestamp: {_fmt(row['timestamp'])} seconds",
                f"- Existing left hip angle: {_fmt(row['hip_flexion_left'])} degrees",
                f"- Existing right hip angle: {_fmt(row['hip_flexion_right'])} degrees",
                f"- Existing absolute difference: {_fmt(row['absolute_difference'])} degrees",
                f"- Near/far-side inference: {row['near_far_comparison']['near_far_inference']}",
                f"- Z geometry evidence: {row['near_far_comparison']['z_geometry_evidence']}",
                "",
                "| Side | Landmarks | Vector A | Vector B | Visibility Min | Confidence Min | Missing | Nonfinite Coordinates |",
                "|---|---|---|---|---:|---:|---|---|",
            ]
        )
        for side in ("left", "right"):
            triplet = row[f"{side}_hip_triplet"]
            lines.append(
                f"| {side} | {_md(' -> '.join(triplet['landmark_names']))} | {_md(_vector_string(triplet['vector_a']))} | {_md(_vector_string(triplet['vector_b']))} | {_fmt(triplet['visibility_min'])} | {_fmt(triplet['confidence_min'])} | {_md(', '.join(triplet['missing_landmarks']) or 'None')} | {_md(', '.join(triplet['nonfinite_coordinates']) or 'None')} |"
            )
        lines.append("")
    return "\n".join(lines)


def render_hip_discrepancy_investigation_html(investigation: dict[str, Any]) -> str:
    """Render a standalone developer-only HTML investigation report."""

    origin = investigation["origin_assessment"]
    cards = []
    for candidate in origin["candidate_origins"]:
        cards.append(
            "<section class='card'>"
            f"<h3>{escape(candidate['origin'])}</h3>"
            f"<p><strong>Status:</strong> {escape(candidate['status'])}</p>"
            f"<p>{escape('; '.join(candidate['evidence']))}</p>"
            "</section>"
        )
    frames = []
    for row in investigation["frame_investigations"]:
        frames.append(
            "<section class='frame'>"
            f"<h2>Rank {row['rank']} - Frame {escape(str(row['frame_index']))}</h2>"
            f"<p>Timestamp {escape(_fmt(row['timestamp']))} s. Existing left hip {_fmt(row['hip_flexion_left'])} deg; right hip {_fmt(row['hip_flexion_right'])} deg; absolute difference {_fmt(row['absolute_difference'])} deg.</p>"
            f"<p><strong>Origin evidence:</strong> {escape('; '.join(row['origin_evidence']))}</p>"
            f"<p><strong>Near/far-side comparison:</strong> {escape(row['near_far_comparison']['near_far_inference'])} {escape(row['near_far_comparison']['z_geometry_evidence'])}</p>"
            f"{_frame_svg(row)}"
            f"{_triplet_table(row)}"
            "</section>"
        )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>JumpGuard Hip Discrepancy Investigation</title>
  <style>
    body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;margin:0;background:#f4f7fb;color:#17202a;}}
    header{{background:#1d3148;color:white;padding:22px 30px;}}
    header h1{{margin:0 0 8px;font-size:28px;letter-spacing:0;}}
    header p{{margin:0;color:#d9e6f2;max-width:1040px;}}
    main{{max-width:1220px;margin:20px auto;padding:0 18px;}}
    .notice,.frame,.card{{background:white;border:1px solid #d8e2ee;border-radius:8px;padding:16px;margin-bottom:16px;box-shadow:0 1px 2px rgba(16,42,67,.04);}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;}}
    table{{border-collapse:collapse;width:100%;font-size:13px;margin-top:12px;}}
    th,td{{border-bottom:1px solid #e6edf5;padding:7px;text-align:left;vertical-align:top;}}
    th{{font-size:11px;text-transform:uppercase;color:#486581;background:#f8fbfe;}}
    svg{{display:block;width:100%;max-width:760px;height:auto;background:#07111f;border-radius:8px;margin:12px 0;border:1px solid #1f334d;}}
    .legend{{font-size:13px;color:#486581;}}
  </style>
</head>
<body>
  <header>
    <h1>Hip Discrepancy Investigation</h1>
    <p>Developer-only evidence review from existing Measurement Debug Mode outputs. This report displays current landmarks, confidence, visibility, and hip-angle vectors without changing any measurements.</p>
  </header>
  <main>
    <section class="notice">
      <h2>Origin Assessment</h2>
      <p><strong>Overall origin:</strong> {escape(origin['overall_origin'])}</p>
      <p><strong>Summary:</strong> {escape(origin['summary'])}</p>
      <p><strong>Evidence standard:</strong> {escape(origin['evidence_standard'])}</p>
    </section>
    <section class="grid">{''.join(cards)}</section>
    <p class="legend">SVG convention: blue vector = shoulder to hip, orange vector = knee to hip, point color reflects visibility where green is high, amber is moderate, and red is below 0.5.</p>
    {''.join(frames) if frames else '<section class="frame"><h2>No finite hip-pair frames</h2><p>Insufficient evidence to investigate left/right hip discrepancy origins in this run.</p></section>'}
  </main>
</body>
</html>
"""


def _measurement_definitions() -> list[dict[str, str]]:
    definitions = []
    for signal, landmarks in ANGLE_SIGNAL_MAP.items():
        first, vertex, third = landmarks
        definitions.append(
            {
                "signal": signal,
                "landmarks": " -> ".join(landmarks),
                "vertex": vertex,
                "vector_a": f"{first} - {vertex}",
                "vector_b": f"{third} - {vertex}",
                "formula": "degrees(arccos(clip(dot(vector_a, vector_b) / (||vector_a|| * ||vector_b||), -1, 1)))",
                "convention": "Unsigned internal 3D vector angle from MediaPipe landmark coordinates.",
                "expected_range_degrees": "0 to 180 when vectors are finite and nonzero; NaN otherwise.",
                "interpretation_boundary": "MediaPipe-derived geometric approximation; not laboratory inverse kinematics or a clinical score.",
            }
        )
    return definitions


def _hip_frame_investigations(frame_database: list[dict[str, Any]], *, top_n: int) -> list[dict[str, Any]]:
    ranked = _hip_discrepancies(frame_database, top_n=top_n)["largest_differences"]
    frames_by_index = {frame.get("frame_index"): frame for frame in frame_database}
    investigations = []
    for row in ranked:
        frame = frames_by_index.get(row["frame_index"], {})
        left_triplet = _triplet_detail(frame, ANGLE_SIGNAL_MAP["hip_flexion_left"])
        right_triplet = _triplet_detail(frame, ANGLE_SIGNAL_MAP["hip_flexion_right"])
        evidence = _classify_frame_evidence(left_triplet, right_triplet)
        investigations.append(
            {
                **row,
                "confidence_rank": None,
                "left_hip_triplet": left_triplet,
                "right_hip_triplet": right_triplet,
                "near_far_comparison": _near_far_comparison(left_triplet, right_triplet),
                "origin_evidence": evidence,
            }
        )
    investigations.sort(key=lambda item: (_confidence_sort_value(item), -item["absolute_difference"]))
    for rank, row in enumerate(investigations, start=1):
        row["confidence_rank"] = rank
    investigations.sort(key=lambda item: item["rank"])
    return investigations


def _origin_assessment(frame_investigations: list[dict[str, Any]]) -> dict[str, Any]:
    if not frame_investigations:
        return {
            "overall_origin": "insufficient evidence",
            "evidence_standard": "No finite paired left/right hip measurements were available for origin assessment.",
            "summary": "The run does not contain finite left and right hip angle pairs, so discrepancy origin cannot be evaluated.",
            "candidate_origins": _candidate_origin_rows(
                landmark_estimation=[],
                occlusion=[],
                camera=[],
                angle_definition=[],
            ),
        }

    landmark_estimation: list[str] = []
    occlusion: list[str] = []
    angle_definition: list[str] = []
    for frame in frame_investigations:
        label = f"frame {frame['frame_index']}"
        notes = "; ".join(frame["origin_evidence"])
        if "missing" in notes or "nonfinite" in notes:
            occlusion.append(f"{label}: {notes}")
        if "visibility below 0.5" in notes or "confidence below 0.5" in notes:
            landmark_estimation.append(f"{label}: {notes}")
    angle_definition.append(
        "Hip flexion is represented as an unsigned internal shoulder-hip-knee vector angle from MediaPipe landmarks; this is a documented geometric definition, not laboratory inverse kinematics."
    )

    if occlusion:
        overall = "occlusion"
        summary = "At least one ranked discrepancy frame contains missing or nonfinite hip-triplet landmark evidence, which is most consistent with occlusion or landmark dropout in the available records."
    elif landmark_estimation:
        overall = "landmark estimation"
        summary = "Ranked discrepancy frames contain low visibility or confidence on landmarks used directly in the hip-angle triplets."
    else:
        overall = "insufficient evidence"
        summary = "Ranked discrepancy frames are finite and do not show missing, nonfinite, or low-confidence hip-triplet evidence in the available records; camera perspective and true cause cannot be determined without external ground truth or camera metadata."

    return {
        "overall_origin": overall,
        "evidence_standard": "Classification is based only on existing measurements, landmark coordinates, visibility, confidence, and documented angle definitions; no thresholds beyond MediaPipe-style visibility/confidence quality flags are used for clinical interpretation.",
        "summary": summary,
        "candidate_origins": _candidate_origin_rows(
            landmark_estimation=landmark_estimation,
            occlusion=occlusion,
            camera=["No camera calibration, view label, synchronized multi-view data, or external ground-truth video annotation is present in the frame database."],
            angle_definition=angle_definition,
        ),
    }


def _candidate_origin_rows(
    *,
    landmark_estimation: list[str],
    occlusion: list[str],
    camera: list[str],
    angle_definition: list[str],
) -> list[dict[str, Any]]:
    return [
        {
            "origin": "landmark estimation",
            "status": "evidence present" if landmark_estimation else "insufficient evidence",
            "evidence": landmark_estimation or ["No ranked finite hip-pair frame shows low hip-triplet visibility or confidence in the available records."],
        },
        {
            "origin": "occlusion",
            "status": "evidence present" if occlusion else "insufficient evidence",
            "evidence": occlusion or ["No ranked finite hip-pair frame shows missing or nonfinite hip-triplet landmarks in the available records."],
        },
        {
            "origin": "camera perspective",
            "status": "insufficient evidence",
            "evidence": camera,
        },
        {
            "origin": "angle-definition limitations",
            "status": "documented limitation, not proven frame-specific cause" if angle_definition else "insufficient evidence",
            "evidence": angle_definition or ["No finite hip-pair frames were available to inspect the documented angle definition."],
        },
    ]


def _triplet_detail(frame: dict[str, Any], names: tuple[str, str, str]) -> dict[str, Any]:
    lookup = {str(row.get("landmark_name")): row for row in frame.get("landmarks", [])}
    stats = _landmark_triplet_stats(frame, names)
    landmarks = []
    for name in names:
        row = lookup.get(name, {})
        landmarks.append(
            {
                "name": name,
                "x": _float_or_nan(row.get("x")),
                "y": _float_or_nan(row.get("y")),
                "z": _float_or_nan(row.get("z")),
                "visibility": _float_or_nan(row.get("visibility")),
                "confidence": _float_or_nan(row.get("confidence")),
            }
        )
    return {
        "landmark_names": list(names),
        "landmarks": landmarks,
        "vector_a": _vector(landmarks[1], landmarks[0]),
        "vector_b": _vector(landmarks[1], landmarks[2]),
        "visibility_min": stats["visibility_min"],
        "confidence_min": stats["confidence_min"],
        "missing_landmarks": stats["missing_landmarks"],
        "nonfinite_coordinates": stats["nonfinite_coordinates"],
        "z_mean": _nanmean(np.array([point["z"] for point in landmarks], dtype=float)),
    }


def _vector(origin: dict[str, Any], destination: dict[str, Any]) -> list[float]:
    return [
        _float_or_nan(destination.get(axis)) - _float_or_nan(origin.get(axis))
        for axis in ("x", "y", "z")
    ]


def _near_far_comparison(left: dict[str, Any], right: dict[str, Any]) -> dict[str, str]:
    left_z = left.get("z_mean")
    right_z = right.get("z_mean")
    if np.isfinite(_float_or_nan(left_z)) and np.isfinite(_float_or_nan(right_z)):
        z_text = f"left hip-triplet mean z={_fmt(left_z)}, right hip-triplet mean z={_fmt(right_z)}. MediaPipe z is available for comparison, but this audit does not infer camera near/far side from z alone."
    else:
        z_text = "Mean z could not be compared because one or both hip triplets contain nonfinite z coordinates."
    return {
        "near_far_inference": "Unknown; no camera calibration or documented camera-side metadata is available in the existing debug records.",
        "z_geometry_evidence": z_text,
    }


def _classify_frame_evidence(left: dict[str, Any], right: dict[str, Any]) -> list[str]:
    evidence = []
    for side, triplet in (("left", left), ("right", right)):
        if triplet["missing_landmarks"]:
            evidence.append(f"{side} hip triplet missing landmarks: {', '.join(triplet['missing_landmarks'])}")
        if triplet["nonfinite_coordinates"]:
            evidence.append(f"{side} hip triplet nonfinite coordinates: {', '.join(triplet['nonfinite_coordinates'])}")
        if np.isfinite(_float_or_nan(triplet["visibility_min"])) and _float_or_nan(triplet["visibility_min"]) < 0.5:
            evidence.append(f"{side} hip triplet visibility below 0.5")
        if np.isfinite(_float_or_nan(triplet["confidence_min"])) and _float_or_nan(triplet["confidence_min"]) < 0.5:
            evidence.append(f"{side} hip triplet confidence below 0.5")
    evidence.append("camera perspective cannot be determined from available single-view debug records")
    evidence.append("hip angle uses documented unsigned shoulder-hip-knee vector geometry")
    return evidence


def _confidence_sort_value(row: dict[str, Any]) -> float:
    values = [
        _float_or_nan(row["left_hip_triplet"].get("visibility_min")),
        _float_or_nan(row["right_hip_triplet"].get("visibility_min")),
        _float_or_nan(row["left_hip_triplet"].get("confidence_min")),
        _float_or_nan(row["right_hip_triplet"].get("confidence_min")),
    ]
    finite = [value for value in values if np.isfinite(value)]
    return min(finite) if finite else -1.0


def _vector_string(vector: list[float]) -> str:
    return "(" + ", ".join(_fmt(value) for value in vector) + ")"


def _frame_svg(row: dict[str, Any]) -> str:
    points = row["left_hip_triplet"]["landmarks"] + row["right_hip_triplet"]["landmarks"]
    finite_points = [point for point in points if np.isfinite(_float_or_nan(point["x"])) and np.isfinite(_float_or_nan(point["y"]))]
    if not finite_points:
        return "<p>No finite x/y landmark coordinates available for SVG visualization.</p>"
    width = 760
    height = 460
    margin = 42
    xs = [_float_or_nan(point["x"]) for point in finite_points]
    ys = [_float_or_nan(point["y"]) for point in finite_points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max(max_x - min_x, 1e-9)
    span_y = max(max_y - min_y, 1e-9)

    def project(point: dict[str, Any]) -> tuple[float, float] | None:
        x = _float_or_nan(point["x"])
        y = _float_or_nan(point["y"])
        if not np.isfinite(x) or not np.isfinite(y):
            return None
        return (
            margin + ((x - min_x) / span_x) * (width - margin * 2),
            margin + ((y - min_y) / span_y) * (height - margin * 2),
        )

    def color(point: dict[str, Any]) -> str:
        visibility = _float_or_nan(point.get("visibility"))
        if not np.isfinite(visibility):
            return "#8a94a6"
        if visibility >= 0.75:
            return "#22c55e"
        if visibility >= 0.5:
            return "#f59e0b"
        return "#ef4444"

    parts = [f"<svg viewBox='0 0 {width} {height}' role='img' aria-label='Hip landmark and vector diagnostic'>"]
    for side, triplet in (("left", row["left_hip_triplet"]), ("right", row["right_hip_triplet"])):
        landmarks = triplet["landmarks"]
        shoulder = project(landmarks[0])
        hip = project(landmarks[1])
        knee = project(landmarks[2])
        if hip and shoulder:
            parts.append(_svg_line(hip, shoulder, "#38bdf8", 5))
        if hip and knee:
            parts.append(_svg_line(hip, knee, "#f97316", 5))
        for point in landmarks:
            projected = project(point)
            if not projected:
                continue
            x, y = projected
            parts.append(f"<circle cx='{x:.2f}' cy='{y:.2f}' r='7' fill='{color(point)}' stroke='white' stroke-width='1.5'/>")
            parts.append(f"<text x='{x + 10:.2f}' y='{y - 10:.2f}' fill='white' font-size='13'>{escape(side)} {escape(point['name'].split('_')[-1])}</text>")
    parts.append("</svg>")
    return "".join(parts)


def _svg_line(start: tuple[float, float], end: tuple[float, float], color: str, width: int) -> str:
    return f"<line x1='{start[0]:.2f}' y1='{start[1]:.2f}' x2='{end[0]:.2f}' y2='{end[1]:.2f}' stroke='{color}' stroke-width='{width}' stroke-linecap='round'/>"


def _triplet_table(row: dict[str, Any]) -> str:
    lines = [
        "<table><thead><tr><th>Side</th><th>Landmark</th><th>x</th><th>y</th><th>z</th><th>Visibility</th><th>Confidence</th></tr></thead><tbody>"
    ]
    for side in ("left", "right"):
        for point in row[f"{side}_hip_triplet"]["landmarks"]:
            lines.append(
                "<tr>"
                f"<td>{escape(side)}</td>"
                f"<td>{escape(point['name'])}</td>"
                f"<td>{escape(_fmt(point['x']))}</td>"
                f"<td>{escape(_fmt(point['y']))}</td>"
                f"<td>{escape(_fmt(point['z']))}</td>"
                f"<td>{escape(_fmt(point['visibility']))}</td>"
                f"<td>{escape(_fmt(point['confidence']))}</td>"
                "</tr>"
            )
    lines.append("</tbody></table>")
    return "".join(lines)


def _hip_discrepancies(frame_database: list[dict[str, Any]], *, top_n: int) -> dict[str, Any]:
    rows = []
    for frame in frame_database:
        measurements = frame.get("measurements", {})
        left = _float_or_nan(measurements.get("hip_flexion_left"))
        right = _float_or_nan(measurements.get("hip_flexion_right"))
        if not np.isfinite(left) or not np.isfinite(right):
            continue
        left_triplet = _landmark_triplet_stats(frame, ANGLE_SIGNAL_MAP["hip_flexion_left"])
        right_triplet = _landmark_triplet_stats(frame, ANGLE_SIGNAL_MAP["hip_flexion_right"])
        rows.append(
            {
                "frame_index": frame.get("frame_index"),
                "timestamp": frame.get("timestamp"),
                "hip_flexion_left": left,
                "hip_flexion_right": right,
                "absolute_difference": abs(left - right),
                "left_visibility_min": left_triplet["visibility_min"],
                "right_visibility_min": right_triplet["visibility_min"],
                "left_confidence_min": left_triplet["confidence_min"],
                "right_confidence_min": right_triplet["confidence_min"],
                "evidence_notes": _evidence_notes(left_triplet, right_triplet),
            }
        )
    rows.sort(key=lambda item: item["absolute_difference"], reverse=True)
    for index, row in enumerate(rows[:top_n], start=1):
        row["rank"] = index
    return {
        "rank_policy": "Ranked by existing computed abs(hip_flexion_left - hip_flexion_right); no clinical threshold is applied.",
        "finite_hip_pair_count": len(rows),
        "largest_differences": rows[:top_n],
    }


def _confidence_summary(frame_database: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows_by_name: dict[str, list[dict[str, Any]]] = {name: [] for name in LOWER_BODY_LANDMARKS}
    for frame in frame_database:
        for row in frame.get("landmarks", []):
            name = str(row.get("landmark_name"))
            if name in rows_by_name:
                rows_by_name[name].append(row)
    summaries = []
    for name, rows in rows_by_name.items():
        visibility = np.array([_float_or_nan(row.get("visibility")) for row in rows], dtype=float)
        confidence = np.array([_float_or_nan(row.get("confidence")) for row in rows], dtype=float)
        summaries.append(
            {
                "landmark_name": name,
                "frame_count": len(rows),
                "visibility_mean": _nanmean(visibility),
                "visibility_min": _nanmin(visibility),
                "visibility_missing_frames": int(np.count_nonzero(~np.isfinite(visibility))),
                "confidence_mean": _nanmean(confidence),
                "confidence_min": _nanmin(confidence),
                "confidence_missing_frames": int(np.count_nonzero(~np.isfinite(confidence))),
            }
        )
    return summaries


def _findings(frame_database: list[dict[str, Any]]) -> list[dict[str, str]]:
    finite_pairs = [
        frame
        for frame in frame_database
        if np.isfinite(_float_or_nan(frame.get("measurements", {}).get("hip_flexion_left")))
        and np.isfinite(_float_or_nan(frame.get("measurements", {}).get("hip_flexion_right")))
    ]
    if not finite_pairs:
        return [
            {
                "status": "Unknown",
                "text": "No frames contained finite left and right hip angles in this run, so hip discrepancy causes cannot be evaluated from available evidence.",
            }
        ]
    return [
        {
            "status": "Verified implementation trace",
            "text": "Hip measurements use the existing shoulder -> hip -> knee landmark triplets and the unsigned internal vector-angle formula documented in the code.",
        },
        {
            "status": "Observed-data audit",
            "text": "Large left/right differences, when present, are reported as ranked observations from existing computed values, not as clinical abnormalities or formula errors.",
        },
        {
            "status": "Inconclusive cause",
            "text": "This audit can identify missing or low-confidence landmark evidence, but it cannot prove occlusion, camera perspective, or MediaPipe estimation error without paired visual review and external ground truth.",
        },
    ]


def _recommendations() -> list[str]:
    return [
        "Use Measurement Debug Mode to visually inspect ranked frames before considering any formula change.",
        "If recurrent discrepancies coincide with low shoulder, hip, or knee visibility, document the affected frames as measurement-quality concerns rather than changing biomechanics automatically.",
        "Do not alter the hip angle definition without paired validation data or an explicitly approved future scientific prompt.",
    ]


def _landmark_triplet_stats(frame: dict[str, Any], names: tuple[str, str, str]) -> dict[str, Any]:
    lookup = {str(row.get("landmark_name")): row for row in frame.get("landmarks", [])}
    visibility = np.array([_float_or_nan(lookup.get(name, {}).get("visibility")) for name in names], dtype=float)
    confidence = np.array([_float_or_nan(lookup.get(name, {}).get("confidence")) for name in names], dtype=float)
    return {
        "visibility_min": _nanmin(visibility),
        "confidence_min": _nanmin(confidence),
        "missing_landmarks": [name for name in names if name not in lookup],
        "nonfinite_coordinates": [name for name in names if _nonfinite_coordinates(lookup.get(name, {}))],
    }


def _evidence_notes(left: dict[str, Any], right: dict[str, Any]) -> list[str]:
    notes = []
    if left["missing_landmarks"]:
        notes.append("left hip triplet missing: " + ", ".join(left["missing_landmarks"]))
    if right["missing_landmarks"]:
        notes.append("right hip triplet missing: " + ", ".join(right["missing_landmarks"]))
    if left["nonfinite_coordinates"]:
        notes.append("left hip triplet nonfinite coordinates: " + ", ".join(left["nonfinite_coordinates"]))
    if right["nonfinite_coordinates"]:
        notes.append("right hip triplet nonfinite coordinates: " + ", ".join(right["nonfinite_coordinates"]))
    if np.isfinite(left["visibility_min"]) and left["visibility_min"] < 0.5:
        notes.append("left hip triplet includes visibility below 0.5")
    if np.isfinite(right["visibility_min"]) and right["visibility_min"] < 0.5:
        notes.append("right hip triplet includes visibility below 0.5")
    return notes or ["No missing/nonfinite hip-triplet landmark evidence detected in existing debug records."]


def _nonfinite_coordinates(row: dict[str, Any]) -> bool:
    return any(not np.isfinite(_float_or_nan(row.get(axis))) for axis in ("x", "y", "z"))


def _float_or_nan(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def _nanmean(values: np.ndarray) -> float | None:
    finite = values[np.isfinite(values)]
    return None if finite.size == 0 else float(np.mean(finite))


def _nanmin(values: np.ndarray) -> float | None:
    finite = values[np.isfinite(values)]
    return None if finite.size == 0 else float(np.min(finite))


def _fmt(value: Any) -> str:
    number = _float_or_nan(value)
    return "NaN" if not np.isfinite(number) else f"{number:.6g}"


def _md(value: Any) -> str:
    return str(value).replace("|", "\\|")


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return None if np.isnan(value) else float(value)
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value
