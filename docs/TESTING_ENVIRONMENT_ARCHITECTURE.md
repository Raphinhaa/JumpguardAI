# Interactive Testing Environment Architecture

```text
Browser Upload
  -> app.ui.server
  -> app.pipeline.TestingEnvironment
  -> app.pipeline.InteractiveFrameAnalyzer
  -> existing Video abstraction
  -> existing MediaPipe pose estimator
  -> existing annotated-video exporter
  -> existing Prompt 11 joint-angle calculation
  -> per-frame measurement database
  -> synchronized clinical workstation viewer
```

## Components

| Component | Responsibility | Scientific behavior |
|---|---|---|
| `app/ui/server.py` | Local HTTP upload form, result page, artifact serving. | Does not compute biomechanics. |
| `app/pipeline/testing_environment.py` | Upload validation, logs, manifests, app orchestration. | Does not alter measurements. |
| `app/pipeline/frame_analysis.py` | Runs existing video/pose/annotation/angle code paths and exports per-frame measurements, deltas, and symmetry values. | Reuses existing validated calculations and existing symmetry formulas. |
| `src/pose_estimation.py` | Existing MediaPipe landmark extraction and annotated-video generation. | Unchanged. |
| `src/feature_extraction.py` | Existing landmark-derived joint angle calculations. | Unchanged. |
| `config/testing_environment.json` | App-owned runtime settings. | Does not change measurement definitions. |

## Removed From This Workflow

- automatic athlete report generation
- automatic evidence report generation
- athlete-versus-reference comparison
- automatic ACL observations
- automatic recommendations
- event inference
- clinical interpretation

## Workstation Views

- annotated video as the primary interface
- play, pause, scrub, previous/next frame, and jump-to-timestamp controls
- live measurement panel for the selected frame
- delta and symmetry panels for the selected frame
- knee, hip, ankle, delta, and symmetry time-series graphs
- left/right comparison bar charts for the selected frame
- trunk unavailable notice unless a future validated trunk signal exists

Backward-compatible source modules remain in the repository, but this interactive testing workflow does not call them.
