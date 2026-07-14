"""Standard-library web UI for the JumpGuard AI testing environment."""

from __future__ import annotations

from functools import partial
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from email import policy
from email.parser import BytesParser
import json
import mimetypes

from app.pipeline import TestingEnvironment, TestingEnvironmentConfig, TestingEnvironmentResult
from app.pipeline.testing_environment import TestingEnvironmentError, experimental_notice
from app.ui.artifacts import artifact_href


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 7860


class TestingEnvironmentHandler(BaseHTTPRequestHandler):
    """HTTP handler for upload, analysis, and safe artifact downloads."""

    server_version = "JumpGuardTestingEnvironment/1.0"

    def __init__(self, *args, environment: TestingEnvironment, **kwargs) -> None:
        self.environment = environment
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._send_html(render_home())
            return
        if parsed.path == "/artifact":
            self._serve_artifact(parsed.query)
            return
        if parsed.path == "/health":
            self._send_json({"status": "ok", "notice": experimental_notice()})
            return
        self.send_error(404, "Not found")

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        parsed = urlparse(self.path)
        if parsed.path != "/analyze":
            self.send_error(404, "Not found")
            return
        try:
            result = self._handle_upload()
            self._send_html(render_result(result))
        except TestingEnvironmentError as exc:
            self._send_html(render_error(str(exc)), status=400)
        except Exception as exc:  # UI safety net only.
            self._send_html(render_error(f"Unexpected UI error: {type(exc).__name__}: {exc}"), status=500)

    def log_message(self, format: str, *args: object) -> None:
        """Keep request logging compact and local."""

        return

    def _handle_upload(self) -> TestingEnvironmentResult:
        length = int(self.headers.get("Content-Length", "0") or "0")
        content_type = self.headers.get("Content-Type", "")
        if not length or "multipart/form-data" not in content_type:
            raise TestingEnvironmentError("Expected a multipart video upload.")
        body = self.rfile.read(length)
        message = BytesParser(policy=policy.default).parsebytes(
            b"Content-Type: "
            + content_type.encode("utf-8")
            + b"\r\nMIME-Version: 1.0\r\n\r\n"
            + body
        )
        upload = None
        for part in message.iter_parts():
            if part.get_param("name", header="content-disposition") == "video":
                upload = part
                break
        if upload is None or not upload.get_filename():
            raise TestingEnvironmentError("Please choose a video file before analyzing.")
        content = upload.get_payload(decode=True) or b""
        return self.environment.analyze_upload(upload.get_filename() or "uploaded_video.mp4", content)

    def _serve_artifact(self, query: str) -> None:
        params = parse_qs(query)
        requested = unquote(params.get("path", [""])[0])
        if not requested:
            self.send_error(400, "Missing artifact path")
            return
        path = Path(requested).resolve()
        if not _is_allowed_artifact(path, self.environment.config):
            self.send_error(403, "Artifact path is outside testing-environment outputs")
            return
        if not path.exists() or not path.is_file():
            self.send_error(404, "Artifact not found")
            return
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(path.stat().st_size))
        self.send_header("Content-Disposition", f'inline; filename="{path.name}"')
        self.end_headers()
        with path.open("rb") as handle:
            self.wfile.write(handle.read())

    def _send_html(self, body: str, *, status: int = 200) -> None:
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _send_json(self, payload: dict[str, object], *, status: int = 200) -> None:
        encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def run_server(
    *,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    config_path: str | Path = "config/testing_environment.json",
) -> None:
    """Run the local testing-environment web server."""

    environment = TestingEnvironment(TestingEnvironmentConfig.load(config_path))
    handler = partial(TestingEnvironmentHandler, environment=environment)
    server = ThreadingHTTPServer((host, port), handler)
    print(f"JumpGuard AI Testing Environment: http://{host}:{port}")
    try:
        server.serve_forever()
    finally:
        server.server_close()


def render_home() -> str:
    """Render the upload page."""

    return _page(
        """
        <section class="panel">
          <h2>Upload Jump-Landing Video</h2>
          <form method="post" action="/analyze" enctype="multipart/form-data">
            <input class="file" type="file" name="video" accept=".mp4,.mov,.avi" required>
            <button type="submit">Analyze</button>
          </form>
          <p class="muted">Processing may take a few minutes depending on video length and local hardware.</p>
        </section>
        <section class="panel">
          <h2>Progress</h2>
          <ol>
            <li>Upload video</li>
            <li>Run existing video, MediaPipe landmark, annotation, and joint-angle code paths</li>
            <li>Export annotated video, synchronized per-frame measurements, time-series, metadata, and logs</li>
          </ol>
          <p class="muted">No automatic athlete report, evidence report, reference comparison, event detection, or clinical interpretation is generated.</p>
        </section>
        """
    )


def render_result(result: TestingEnvironmentResult) -> str:
    """Render one analysis result page."""

    rows = []
    for label, key in _primary_artifacts():
        value = result.generated_files.get(key)
        if value:
            rows.append(f"<li><a href='{_artifact_href(value)}'>{escape(label)}</a></li>")
    if result.log_path:
        rows.append(f"<li><a href='{_artifact_href(result.log_path)}'>Processing log</a></li>")
    if result.manifest_path:
        rows.append(f"<li><a href='{_artifact_href(result.manifest_path)}'>Testing manifest</a></li>")
    video_block = ""
    if result.annotated_video:
        video_block = (
            "<video controls class='preview'>"
            f"<source src='{_artifact_href(result.annotated_video)}' type='{_video_mime_type(result.annotated_video)}'>"
            "Your browser could not preview this video; use the export link below."
            "</video>"
        )
    measurements = _measurement_preview(result)
    viewer = _viewer_panel(result)
    status_class = "ok" if result.status == "success" else "bad"
    return _page(
        f"""
        <section class="hero-panel">
          <div>
            <p class="eyebrow">Clinician Workstation</p>
            <h2>Interactive Biomechanics Review Ready</h2>
            <p class="muted">Open the synchronized workstation to review the annotated video as the master clock with per-frame measurements, deltas, symmetry indices, graphs, and comparison bars.</p>
          </div>
          <div class="hero-actions">{viewer}</div>
        </section>
        <section class="grid">
          <div class="panel">
            <h2>Run Status</h2>
            <p class="status {status_class}">{escape(result.status.upper())}</p>
            <p><strong>Run ID:</strong> {escape(result.run_id)}</p>
            <p><strong>Output folder:</strong> {escape(str(result.run_directory))}</p>
            {f'<p class="error">{escape(result.error)}</p>' if result.error else ''}
          </div>
          <div class="panel"><h2>Per-Frame Measurements</h2>{measurements}</div>
        </section>
        <section class="panel">
          <h2>Annotated Video Preview</h2>
          {video_block or '<p class="muted">No annotated video was generated.</p>'}
        </section>
        <section class="panel">
          <h2>Exports</h2>
          <ul>{''.join(rows) if rows else '<li>No export artifacts available.</li>'}</ul>
        </section>
        <p><a href="/">Analyze another video</a></p>
        """
    )


def render_error(message: str) -> str:
    """Render an app-level error without exposing a traceback."""

    return _page(
        f"""
        <section class="panel">
          <h2>Upload Error</h2>
          <p class="error">{escape(message)}</p>
          <p><a href="/">Return to upload</a></p>
        </section>
        """
    )


def _page(content: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>JumpGuard AI Testing Environment</title>
  <style>
    body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;margin:0;background:#eef3f8;color:#17202a;}}
    header{{background:#12314d;color:white;padding:24px 32px;border-bottom:1px solid rgba(255,255,255,.14);}}
    header h1{{margin:0 0 8px;font-size:30px;letter-spacing:0;}}
    header p{{max-width:980px;margin:0;color:#dbe8f3;}}
    main{{max-width:1180px;margin:24px auto;padding:0 18px;}}
    .panel,.hero-panel{{background:white;border:1px solid #d9e2ec;border-radius:8px;padding:18px;margin-bottom:18px;box-shadow:0 1px 2px rgba(16,42,67,.04);}}
    .hero-panel{{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:18px;align-items:center;}}
    .hero-panel h2{{font-size:26px;margin:4px 0 8px;}}
    .hero-actions a{{display:inline-block;background:#1665d8;color:white;text-decoration:none;border-radius:6px;padding:11px 16px;font-weight:700;}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px;}}
    button{{background:#1665d8;color:white;border:0;border-radius:6px;padding:10px 16px;font-weight:700;cursor:pointer;}}
    input.file{{display:block;margin:12px 0 18px;}}
    a{{color:#0b65c2;}}
    .eyebrow{{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:#486581;font-weight:700;margin:0;}}
    .muted{{color:#627d98;}}
    .error,.bad{{color:#b00020;font-weight:700;}}
    .ok{{color:#1b7f3a;font-weight:700;}}
    .preview{{display:block;width:100%;max-height:520px;background:#111;border-radius:6px;}}
    pre{{background:#f0f4f8;padding:12px;border-radius:6px;overflow:auto;max-height:360px;}}
    @media (max-width: 760px){{.hero-panel{{grid-template-columns:1fr;}}}}
  </style>
</head>
<body>
  <header>
    <h1>JumpGuard Interactive Frame Analysis</h1>
    <p>{escape(experimental_notice())}</p>
  </header>
  <main>{content}</main>
</body>
</html>
"""


def _primary_artifacts() -> tuple[tuple[str, str], ...]:
    return (
        ("Interactive synchronized viewer", "interactive_viewer_html"),
        ("Annotated video", "annotated_video"),
        ("Annotated video MP4", "annotated_video_mp4"),
        ("Annotated video debug AVI", "annotated_video_debug_avi"),
        ("Per-frame measurements CSV", "per_frame_measurements_csv"),
        ("Per-frame measurements JSON", "per_frame_measurements_json"),
        ("Time-series JSON", "time_series_json"),
        ("Landmarks CSV", "landmarks_csv"),
        ("Landmarks JSON", "landmarks_json"),
        ("Developer measurement debugger", "measurement_debugger_html"),
        ("Developer measurement debug raw CSV", "measurement_debug_raw_csv"),
        ("Developer measurement debug raw JSON", "measurement_debug_raw_json"),
        ("Developer hip measurement validation report", "hip_measurement_validation_report"),
        ("Developer hip measurement validation JSON", "hip_measurement_validation_json"),
        ("Developer hip discrepancy investigation report", "hip_discrepancy_investigation_report"),
        ("Developer hip discrepancy investigation JSON", "hip_discrepancy_investigation_json"),
        ("Developer hip discrepancy investigation HTML", "hip_discrepancy_investigation_html"),
        ("Run metadata", "metadata"),
    )


def _measurement_preview(result: TestingEnvironmentResult) -> str:
    path = result.per_frame_measurements_csv
    if not path:
        return "<p class='muted'>No per-frame measurement table generated.</p>"
    return f"<p><a href='{_artifact_href(path)}'>Open per-frame measurement CSV</a></p>"


def _viewer_panel(result: TestingEnvironmentResult) -> str:
    path = result.interactive_viewer_html
    if not path:
        return "<p class='muted'>No synchronized viewer generated.</p>"
    return f"<p><a href='{_artifact_href(path)}'>Open Professional Workstation</a></p>"


def _artifact_href(path: str | Path) -> str:
    return artifact_href(path)


def _video_mime_type(path: str | Path) -> str:
    return "video/mp4" if Path(path).suffix.lower() == ".mp4" else "video/x-msvideo"


def _is_allowed_artifact(path: Path, config: TestingEnvironmentConfig) -> bool:
    roots = (config.input_dir, config.output_dir, config.logs_dir)
    try:
        resolved_roots = [root.resolve() for root in roots]
        return any(path == root or root in path.parents for root in resolved_roots)
    except OSError:
        return False


def main() -> None:
    """CLI entry point."""

    run_server()


if __name__ == "__main__":
    main()
