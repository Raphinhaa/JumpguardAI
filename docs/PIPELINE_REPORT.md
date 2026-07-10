# Prompt 12 End-to-End JumpGuard Pipeline Report

## Purpose

Prompt 12 adds a single orchestration layer for uploaded-video processing. The new layer coordinates the existing Prompt 9 through Prompt 11 execution path and packages existing reporting and dashboard outputs for one run. It does not introduce new algorithms, biomechanics, feature calculations, machine-learning behavior, predictions, clinical interpretations, or undocumented thresholds.

## Implemented Module

- `src/pipeline.py`
  - `JumpGuardPipeline`: public orchestration API.
  - `PipelineResult`: immutable result object containing the run directory, metadata, and generated file paths.
  - `PipelineExecutionError`: exception raised for graceful failures with partial metadata attached.

## Public API

```python
from src.pipeline import JumpGuardPipeline

result = JumpGuardPipeline().process_video(
    video_path="path/to/video.mp4",
    output_directory="reports",
)
```

The required API is `process_video(video_path, output_directory)`. Optional keyword arguments preserve backward compatibility while allowing repeatable test/demo runs:

- `run_id`: explicit output folder name.
- `frame_skip`: forwarded to the existing Prompt 10 pose estimator.
- `timestamp`: explicit execution timestamp for deterministic tests or demos.

## Orchestrated Flow

The pipeline performs the following stages in order:

1. Load the video with the existing Prompt 9 `Video` abstraction.
2. Copy the input video into the run package.
3. Estimate MediaPipe landmarks with the existing Prompt 10 `PoseEstimator` interface.
4. Export landmarks through the existing Prompt 10 deterministic CSV/JSON exporter.
5. Extract Prompt-3-compatible features through the existing Prompt 11 `FeatureExtractor`.
6. Export Prompt 11 feature tables, summaries, landing-event metadata, trajectory summaries, and plots.
7. Generate a run-local athlete report package from the current feature table.
8. Generate a run-local static dashboard from the current feature table and report links.
9. Write `metadata.json` with status, timing, video metadata, feature count, MediaPipe version, outputs, and stage log.

## Output Package

Each run creates `reports/<run_timestamp_or_run_id>/` with this structure:

```text
reports/<run>/
  video/
    <input_video>
  landmarks/
    landmarks.csv
    landmarks.json
  features/
    feature_table.csv
    feature_table.json
    feature_statistics.json
    symmetry_summary.json
    landing_events.json
    trajectory_features.json
    plots/
  athlete_report/
    athlete_report.json
    athlete_report.md
    athlete_report.html
  dashboard/
    dashboard_payload.json
    index.html
  metadata.json
```

## Metadata

`metadata.json` includes:

- `execution_timestamp`
- `processing_duration_seconds`
- `status`
- `error`
- `mediapipe_version`
- `video` source metadata
- `frame_count`
- `feature_count`
- `output_locations`
- `log`
- `predictions_generated`

`predictions_generated` is always `false` in Prompt 12 because this prompt explicitly forbids new prediction, risk, or clinical interpretation behavior.

## Dashboard And Report Integration

Existing Prompt 7 and Prompt 8 modules are dataset/population-oriented and depend on reference-population artifacts from earlier prompts. A single uploaded-video run does not provide those population artifacts. To avoid modifying earlier layers or inventing assumptions, Prompt 12 generates run-local report and dashboard files directly inside the orchestration layer from the current run's feature table and metadata. These outputs are descriptive packaging views only.

## Error Handling

If video loading, pose estimation, feature extraction, reporting, or dashboard packaging fails, the pipeline:

- marks the run `failed`,
- writes `metadata.json` when possible,
- records the stage log and error message,
- raises `PipelineExecutionError` containing the partial `PipelineResult`.

Unsupported or unreadable videos are handled by the existing Prompt 9 validation rules.

## Tests

`tests/test_pipeline.py` verifies:

- complete run package creation,
- metadata content,
- report and dashboard generation,
- deterministic landmarks/features for identical inputs,
- failure metadata for invalid video input.

The tests inject a deterministic test pose estimator that implements the existing Prompt 10 interface. Production usage still defaults to `MediaPipePoseEstimator`.

## Limitations

- The run-local dashboard is a static HTML package for the current feature table, not a new dashboard analytics engine.
- The run-local athlete report is descriptive and does not use reference-population percentiles, ML predictions, clinical thresholds, or risk scoring.
- Processing duration is measured at runtime, so metadata timing naturally varies between executions.
