"""Developer-only measurement debugger for existing frame-level outputs.

This module renders diagnostic views from already-computed landmarks, joint
angles, deltas, and symmetry values. It must not alter or recompute the
validated scientific pipeline outputs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from copy import deepcopy
import json

import pandas as pd

from app.pipeline.measurement_confidence import attach_measurement_confidence
from src.feature_extraction import ANGLE_SIGNAL_MAP
from src.pose_estimation import MEDIAPIPE_POSE_CONNECTIONS


DEBUG_LANDMARKS: tuple[str, ...] = (
    "left_shoulder",
    "right_shoulder",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
    "left_foot_index",
    "right_foot_index",
)


def export_measurement_debug_raw(
    frame_database: list[dict[str, Any]],
    csv_path: str | Path,
    json_path: str | Path,
) -> tuple[Path, Path]:
    """Export diagnostic rows derived exactly from the existing frame database."""

    csv_destination = Path(csv_path)
    json_destination = Path(json_path)
    csv_destination.parent.mkdir(parents=True, exist_ok=True)
    rows = _debug_rows(_ensure_confidence_metadata(frame_database))
    pd.DataFrame(rows).to_csv(csv_destination, index=False, float_format="%.10g")
    json_destination.write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return csv_destination, json_destination


def render_measurement_debugger_html(
    frame_database: list[dict[str, Any]],
    *,
    source_video: dict[str, Any] | None = None,
) -> str:
    """Render a standalone developer diagnostic page."""

    frames = _ensure_confidence_metadata(frame_database)

    payload = {
        "frames": frames,
        "angle_map": ANGLE_SIGNAL_MAP,
        "connections": MEDIAPIPE_POSE_CONNECTIONS,
        "debug_landmarks": DEBUG_LANDMARKS,
        "source_video": source_video or {},
        "policy": "Developer diagnostic only; values are read from existing computed outputs without modifying measurements.",
    }
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>JumpGuard Developer Measurement Debugger</title>
  <style>
    body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;margin:0;background:#eef3f8;color:#17202a;}}
    header{{background:#20324a;color:white;padding:20px 28px;}}
    header h1{{margin:0 0 6px;font-size:26px;letter-spacing:0;}}
    header p{{margin:0;color:#d9e6f2;max-width:980px;}}
    main{{max-width:1480px;margin:18px auto;padding:0 18px;}}
    .grid{{display:grid;grid-template-columns:minmax(520px,1.4fr) minmax(420px,1fr);gap:16px;align-items:start;}}
    .panel{{background:white;border:1px solid #d9e2ec;border-radius:8px;padding:16px;margin-bottom:16px;box-shadow:0 1px 2px rgba(16,42,67,.04);}}
    .controls{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:12px;}}
    button{{background:#1665d8;color:white;border:0;border-radius:6px;padding:9px 12px;font-weight:700;cursor:pointer;}}
    select,input{{height:36px;border:1px solid #bcccdc;border-radius:6px;padding:6px 8px;background:white;}}
    input[type=range]{{width:100%;accent-color:#1665d8;}}
    canvas{{display:block;width:100%;height:620px;background:#07111f;border:1px solid #1f334d;border-radius:8px;}}
    table{{border-collapse:collapse;width:100%;font-size:13px;}}
    th,td{{border-bottom:1px solid #e6edf5;padding:7px;text-align:left;vertical-align:top;}}
    th{{font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:#486581;background:#f8fbfe;}}
    .muted{{color:#627d98;}}
    .warning{{background:#fff7e6;border:1px solid #f0c36d;border-radius:8px;padding:10px;margin:10px 0;}}
    .status-dot{{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px;}}
    .triple{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;}}
    @media (max-width: 980px){{.grid{{grid-template-columns:1fr;}}canvas{{height:520px;}}}}
  </style>
</head>
<body>
  <header>
    <h1>Developer Measurement Debugger</h1>
    <p>Diagnostic-only visualization of the existing landmark geometry, vectors, angles, deltas, and symmetry values. This page does not define or modify biomechanics.</p>
  </header>
  <main>
    <div class="warning"><strong>Developer mode:</strong> all values are read from existing computed outputs. Missing landmarks, visibility, confidence, NaN angles, deltas, and symmetry values are displayed without smoothing, substitution, or filtering.</div>
    <section class="grid">
      <div class="panel">
        <div class="controls">
          <button id="prev">Previous Frame</button>
          <button id="next">Next Frame</button>
          <label>Angle <select id="angleSelect"></select></label>
          <label>Zoom <input id="zoom" type="range" min="0.6" max="3" value="1" step="0.05"></label>
          <label><input id="trails" type="checkbox"> Landmark trails</label>
        </div>
        <input id="timeline" type="range" min="0" max="0" value="0" step="1">
        <p><strong>Frame:</strong> <span id="frameLabel">--</span> <strong>Timestamp:</strong> <span id="timeLabel">--</span></p>
        <canvas id="skeleton" width="1000" height="720"></canvas>
      </div>
      <aside>
        <div class="panel"><h2>Angle Debug Panel</h2><div id="anglePanel"></div></div>
        <div class="panel"><h2>Landmark Panel</h2><div id="landmarkPanel"></div></div>
        <div class="panel"><h2>Confidence Inspector</h2><div id="confidencePanel"></div></div>
      </aside>
    </section>
    <section class="panel"><h2>Left vs Right Comparison</h2><div id="comparisonPanel" class="triple"></div></section>
  </main>
  <script id="debug-data" type="application/json">{json.dumps(_json_ready(payload), sort_keys=True)}</script>
  <script>
    const data = JSON.parse(document.getElementById('debug-data').textContent);
    const frames = data.frames || [];
    const angleMap = data.angle_map || {{}};
    const connections = data.connections || [];
    const debugLandmarks = data.debug_landmarks || [];
    const timeline = document.getElementById('timeline');
    const angleSelect = document.getElementById('angleSelect');
    const zoomInput = document.getElementById('zoom');
    const trailsInput = document.getElementById('trails');
    const canvas = document.getElementById('skeleton');
    const ctx = canvas.getContext('2d');
    let selected = 0;
    timeline.max = Math.max(frames.length - 1, 0);
    Object.keys(angleMap).forEach(key => {{
      const option = document.createElement('option');
      option.value = key;
      option.textContent = key;
      angleSelect.appendChild(option);
    }});

    function fmt(value, digits=4) {{
      return value === null || value === undefined || Number.isNaN(Number(value)) ? 'NaN' : Number(value).toFixed(digits);
    }}
    function currentFrame() {{ return frames[selected] || {{landmarks: [], measurements: {{}}, derived_measurements: {{}}}}; }}
    function landmarkMap(frame) {{
      const map = {{}};
      (frame.landmarks || []).forEach(row => {{ map[row.landmark_name] = row; map[row.landmark_index] = row; }});
      return map;
    }}
    function point(row) {{
      if (!row || !Number.isFinite(Number(row.x)) || !Number.isFinite(Number(row.y))) return null;
      const z = Number(zoomInput.value || 1);
      return {{x: Number(row.x) * canvas.width * z + canvas.width * (1 - z) / 2, y: Number(row.y) * canvas.height * z + canvas.height * (1 - z) / 2}};
    }}
    function visibilityColor(value) {{
      const v = Number(value);
      if (!Number.isFinite(v)) return '#8a94a6';
      if (v >= 0.75) return '#22c55e';
      if (v >= 0.5) return '#f59e0b';
      return '#ef4444';
    }}
    function draw() {{
      const frame = currentFrame();
      const landmarks = landmarkMap(frame);
      const selectedAngle = angleSelect.value || Object.keys(angleMap)[0];
      const triplet = angleMap[selectedAngle] || [];
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = '#07111f'; ctx.fillRect(0, 0, canvas.width, canvas.height);
      if (trailsInput.checked) drawTrails(selectedAngle);
      ctx.lineWidth = 2; ctx.strokeStyle = '#49657f';
      connections.forEach(pair => {{
        const a = point(landmarks[pair[0]]), b = point(landmarks[pair[1]]);
        if (!a || !b) return;
        ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
      }});
      (frame.landmarks || []).forEach(row => {{
        const p = point(row); if (!p) return;
        const highlight = debugLandmarks.includes(row.landmark_name);
        ctx.fillStyle = highlight ? visibilityColor(row.visibility) : '#dbeafe';
        ctx.beginPath(); ctx.arc(p.x, p.y, highlight ? 5 : 3, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = highlight ? '#ffffff' : '#8fb3d9'; ctx.font = highlight ? '13px Arial' : '10px Arial';
        ctx.fillText(String(row.landmark_index), p.x + 6, p.y - 6);
      }});
      drawAngleConstruction(triplet, landmarks, frame.measurements?.[selectedAngle]);
    }}
    function drawAngleConstruction(triplet, landmarks, angleValue) {{
      if (triplet.length !== 3) return;
      const a = point(landmarks[triplet[0]]), vertex = point(landmarks[triplet[1]]), b = point(landmarks[triplet[2]]);
      if (!a || !vertex || !b) return;
      ctx.lineWidth = 5; ctx.strokeStyle = '#38bdf8';
      ctx.beginPath(); ctx.moveTo(vertex.x, vertex.y); ctx.lineTo(a.x, a.y); ctx.stroke();
      ctx.strokeStyle = '#f97316'; ctx.beginPath(); ctx.moveTo(vertex.x, vertex.y); ctx.lineTo(b.x, b.y); ctx.stroke();
      ctx.strokeStyle = '#facc15'; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(vertex.x, vertex.y, 34, -1.2, 0.6); ctx.stroke();
      ctx.fillStyle = '#ffffff'; ctx.font = '18px Arial'; ctx.fillText(fmt(angleValue, 2) + ' deg', vertex.x + 18, vertex.y + 24);
    }}
    function drawTrails(selectedAngle) {{
      const triplet = angleMap[selectedAngle] || [];
      const start = Math.max(0, selected - 20);
      for (let i = start; i < selected; i += 1) {{
        const landmarks = landmarkMap(frames[i]);
        triplet.forEach(name => {{
          const p = point(landmarks[name]); if (!p) return;
          ctx.fillStyle = 'rgba(250,204,21,.22)'; ctx.beginPath(); ctx.arc(p.x, p.y, 3, 0, Math.PI * 2); ctx.fill();
        }});
      }}
    }}
    function vectorText(frame, triplet) {{
      const landmarks = landmarkMap(frame);
      const a = landmarks[triplet[0]], v = landmarks[triplet[1]], b = landmarks[triplet[2]];
      const va = a && v ? [Number(a.x)-Number(v.x), Number(a.y)-Number(v.y), Number(a.z)-Number(v.z)] : [NaN, NaN, NaN];
      const vb = b && v ? [Number(b.x)-Number(v.x), Number(b.y)-Number(v.y), Number(b.z)-Number(v.z)] : [NaN, NaN, NaN];
      return {{a: va.map(x => fmt(x, 6)).join(', '), b: vb.map(x => fmt(x, 6)).join(', ')}};
    }}
    function renderPanels() {{
      const frame = currentFrame();
      const selectedAngle = angleSelect.value || Object.keys(angleMap)[0];
      const triplet = angleMap[selectedAngle] || [];
      const vectors = vectorText(frame, triplet);
      const confidence = frame.measurement_confidence?.[selectedAngle] || {{}};
      document.getElementById('frameLabel').textContent = frame.frame_index ?? '--';
      document.getElementById('timeLabel').textContent = fmt(frame.timestamp, 3) + ' s';
      document.getElementById('anglePanel').innerHTML = '<table><tbody>' +
        `<tr><th>Signal</th><td>${{selectedAngle}}</td></tr>` +
        `<tr><th>Landmarks</th><td>${{triplet.join(' -> ')}}</td></tr>` +
        `<tr><th>Current angle</th><td>${{fmt(frame.measurements?.[selectedAngle], 6)}} deg</td></tr>` +
        `<tr><th>Confidence</th><td>${{fmt(confidence.score_percent, 1)}}% · ${{confidence.category?.label || 'Low Confidence'}} · ${{confidence.limb_role || 'Unknown limb role'}}</td></tr>` +
        `<tr><th>Confidence method</th><td>${{confidence.calculation || 'Mean visibility of contributing landmarks.'}}</td></tr>` +
        `<tr><th>Vector A</th><td>${{vectors.a}}</td></tr>` +
        `<tr><th>Vector B</th><td>${{vectors.b}}</td></tr>` +
        '</tbody></table>';
      renderLandmarks(frame);
      renderConfidence(frame);
      renderComparison(frame);
    }}
    function renderLandmarks(frame) {{
      const landmarks = landmarkMap(frame);
      document.getElementById('landmarkPanel').innerHTML = '<table><thead><tr><th>Name</th><th>x</th><th>y</th><th>z</th><th>visibility</th></tr></thead><tbody>' +
        debugLandmarks.map(name => {{ const row = landmarks[name] || {{}}; return `<tr><td>${{name}}</td><td>${{fmt(row.x, 6)}}</td><td>${{fmt(row.y, 6)}}</td><td>${{fmt(row.z, 6)}}</td><td>${{fmt(row.visibility, 4)}}</td></tr>`; }}).join('') +
        '</tbody></table>';
    }}
    function renderConfidence(frame) {{
      const landmarks = landmarkMap(frame);
      const measurementRows = Object.entries(frame.measurement_confidence || {{}}).map(([signal, confidence]) => {{
        const visibilities = confidence.landmark_visibilities || {{}};
        const visibilityText = Object.entries(visibilities).map(([name, value]) => `${{name}}=${{fmt(value, 3)}}`).join(', ');
        return `<tr><td>${{signal}}</td><td>${{fmt(confidence.score_percent, 1)}}%</td><td>${{confidence.category?.label || 'Low Confidence'}}</td><td>${{confidence.limb_role || 'Unknown limb role'}}</td><td>${{visibilityText}}</td></tr>`;
      }}).join('');
      const landmarkRows = debugLandmarks.map(name => {{
        const row = landmarks[name] || {{}};
        return `<p><span class="status-dot" style="background:${{visibilityColor(row.visibility)}}"></span>${{name}} visibility ${{fmt(row.visibility, 4)}} confidence ${{fmt(row.confidence, 4)}}</p>`;
      }}).join('');
      document.getElementById('confidencePanel').innerHTML = '<h3>Measurement Confidence Percentages</h3><p class="muted">Developer-only: score is the mean visibility of the landmarks used by each joint-angle measurement.</p><table><thead><tr><th>Signal</th><th>Score</th><th>Category</th><th>Limb role</th><th>Landmark visibilities</th></tr></thead><tbody>' + measurementRows + '</tbody></table><h3>Landmark Visibility</h3>' + landmarkRows;
    }}
    function renderComparison(frame) {{
      const pairs = [['hip_flexion', 'hip_flexion_left', 'hip_flexion_right'], ['knee_flexion', 'knee_flexion_left', 'knee_flexion_right'], ['ankle_angle', 'ankle_angle_left', 'ankle_angle_right']];
      document.getElementById('comparisonPanel').innerHTML = pairs.map(([label, left, right]) => {{
        const symmetry = frame.derived_measurements?.symmetry?.[label] || {{}};
        return `<div><h3>${{label}}</h3><table><tbody><tr><th>Left angle</th><td>${{fmt(frame.measurements?.[left], 6)}}</td></tr><tr><th>Right angle</th><td>${{fmt(frame.measurements?.[right], 6)}}</td></tr><tr><th>Abs diff</th><td>${{fmt(symmetry.absolute_difference, 6)}}</td></tr><tr><th>% diff</th><td>${{fmt(symmetry.percent_difference, 6)}}</td></tr><tr><th>Sym index</th><td>${{fmt(symmetry.symmetry_index, 6)}}</td></tr></tbody></table></div>`;
      }}).join('');
    }}
    function selectFrame(index) {{
      if (!frames.length) return;
      selected = Math.max(0, Math.min(frames.length - 1, index));
      timeline.value = selected;
      renderPanels();
      draw();
    }}
    document.getElementById('prev').onclick = () => selectFrame(selected - 1);
    document.getElementById('next').onclick = () => selectFrame(selected + 1);
    timeline.oninput = () => selectFrame(Number(timeline.value));
    angleSelect.onchange = () => selectFrame(selected);
    zoomInput.oninput = () => draw();
    trailsInput.onchange = () => draw();
    selectFrame(0);
  </script>
</body>
</html>
"""


def _debug_rows(frame_database: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for frame in frame_database:
        landmark_lookup = {str(row.get("landmark_name")): row for row in frame.get("landmarks", [])}
        for signal, landmarks in ANGLE_SIGNAL_MAP.items():
            joint = signal.rsplit("_", 1)[0]
            symmetry = frame.get("derived_measurements", {}).get("symmetry", {}).get(joint, {})
            row: dict[str, Any] = {
                "frame_index": frame.get("frame_index"),
                "timestamp": frame.get("timestamp"),
                "signal": signal,
                "landmarks_used": " -> ".join(landmarks),
                "angle_value": frame.get("measurements", {}).get(signal),
                "delta_from_previous_frame": frame.get("derived_measurements", {}).get("delta_from_previous_frame", {}).get(signal),
                "absolute_difference": symmetry.get("absolute_difference"),
                "percent_difference": symmetry.get("percent_difference"),
                "symmetry_index": symmetry.get("symmetry_index"),
            }
            confidence = frame.get("measurement_confidence", {}).get(signal, {})
            row["measurement_confidence_percent"] = confidence.get("score_percent")
            row["measurement_confidence_category"] = confidence.get("category", {}).get("label")
            row["measurement_confidence_limb_role"] = confidence.get("limb_role")
            row["measurement_confidence_calculation"] = confidence.get("calculation")
            for label, landmark in zip(("first", "vertex", "third"), landmarks, strict=True):
                source = landmark_lookup.get(landmark, {})
                row[f"{label}_landmark"] = landmark
                row[f"{label}_x"] = source.get("x")
                row[f"{label}_y"] = source.get("y")
                row[f"{label}_z"] = source.get("z")
                row[f"{label}_visibility"] = source.get("visibility")
                row[f"{label}_confidence"] = source.get("confidence")
            rows.append(row)
    return _json_ready(rows)


def _ensure_confidence_metadata(frame_database: list[dict[str, Any]]) -> list[dict[str, Any]]:
    frames = deepcopy(frame_database)
    if frames and any("measurement_confidence" not in frame or "camera_orientation" not in frame for frame in frames):
        attach_measurement_confidence(frames)
    return frames


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if pd.isna(value):
        return None
    return value
