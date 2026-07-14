# Interactive Testing Environment Installation

## Requirements

Use the existing JumpGuard project environment. Prompt 19 does not add a web-framework dependency.

```bash
.venv/bin/python -m pip install -r requirements.txt
```

The MediaPipe model file must remain available at the project model location used by `src.pipeline.JumpGuardPipeline`.

## Start The App

```bash
PYTHONPATH=. .venv/bin/python -m app.ui.server
```

Default URL: `http://127.0.0.1:7860`.

## Configuration

Configuration lives in `config/testing_environment.json`.

| Setting | Purpose |
|---|---|
| `input_dir` | Uploaded video storage. |
| `output_dir` | Existing pipeline run package destination. |
| `logs_dir` | Testing-environment logs. |
| `frame_skip` | Passed through to existing pipeline processing. |
| `max_upload_mb` | Upload-size guard. |
| `allowed_extensions` | Accepted video extensions. |
| `confidence_threshold` | Reserved configuration field; not wired into calculations by Prompt 19. |
| `annotated_video_codec` | Reserved documentation/config field; Prompt 19 does not alter existing codec behavior. |
| `future_model_selection` | Reserved future-selection field; Prompt 19 does not change model selection. |

The interactive workflow does not install or invoke report-generation, reference-comparison, clinical interpretation, or event-detection services.
