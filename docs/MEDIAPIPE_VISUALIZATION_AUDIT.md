# Stabilization S1 MediaPipe Visualization Audit

## Objective

Verify and complete the MediaPipe visualization pipeline so every standard `JumpGuardPipeline.process_video(...)` run exports a canonical annotated video showing detected MediaPipe landmarks and skeleton connections. This stabilization pass does not add machine learning, biomechanics, ACL prediction, clinical interpretation, or user interface components.

## Root Cause

Prompt 10 already included reusable visualization utilities:

- `annotate_frame(...)`
- `export_annotated_frames(...)`
- `export_annotated_video(...)`

Prompt 12 did not call `export_annotated_video(...)`. Instead, it copied the original input video into `reports/<run>/video/` and registered that copied file as the canonical pipeline `video` artifact. As a result, reports, dashboard payloads, metadata, and `PipelineResult.generated_files["video"]` all pointed to the unannotated source video copy.

The existing `annotate_frame(...)` utility also drew landmark points only. It did not draw skeleton connections, and the installed MediaPipe Tasks package did not expose `mediapipe.solutions.pose.POSE_CONNECTIONS`, so a static MediaPipe 33-landmark pose topology fallback was required for connection drawing.

## Integration Fix

The stabilization fix preserves Prompt 10 and Prompt 12 architecture and integrates existing functionality rather than replacing it.

Changes made:

- `src/pose_estimation.py`
  - Extended existing `annotate_frame(...)` so it draws both landmark points and skeleton connections.
  - Added `MEDIAPIPE_POSE_CONNECTIONS` as a fallback topology when MediaPipe drawing/solution utilities are unavailable.
  - Kept landmark data unchanged; visualization is applied only to copied frame pixels.

- `src/pipeline.py`
  - Replaced original-video copying with a call to existing Prompt 10 `export_annotated_video(...)`.
  - Added `JumpGuardPipeline.export_video(...)` as an orchestration stage that writes `reports/<run>/video/<stem>_annotated.avi`.
  - Registered the annotated video as the canonical `generated_files["video"]` and metadata `output_locations.video` artifact.
  - Passed the annotated video path into the run-local report and dashboard payloads.
  - Cleared previous video exports inside the current run's `video/` directory before writing the canonical annotated artifact, preventing duplicate original and annotated video outputs for reruns.

No feature extraction, biomechanical calculations, ML infrastructure, reports analytics, dashboard analytics, or clinical interpretation logic was modified.

## Verification Summary

Targeted automated tests:

```text
PYTHONPATH=. .venv/bin/python -m pytest -q tests/test_pose_estimation.py tests/test_pipeline.py
12 passed
```

The tests verify:

- skeleton connections are drawn by `annotate_frame(...)`,
- the pipeline exports `*_annotated.avi` as the canonical video artifact,
- the run `video/` directory contains only the annotated video,
- the annotated video frame count matches pipeline metadata,
- the annotated first frame differs from the source first frame when landmarks are present,
- athlete report JSON references the annotated video,
- dashboard payload JSON references the annotated video.

Real pipeline audit run:

```text
Input: data/sample/jump.mp4
Run: reports/run_s1_visualization_audit
Canonical video: reports/run_s1_visualization_audit/video/jump_annotated.avi
```

Programmatic verification results:

```json
{
  "annotated_frame_count": 92,
  "canonical_video": "reports/run_s1_visualization_audit/video/jump_annotated.avi",
  "dashboard_video_reference_matches": true,
  "first_frame_changed": true,
  "landmark_frame_count": 92,
  "landmark_rows": 3036,
  "metadata_frame_count": 92,
  "report_video_reference_matches": true,
  "source_frame_count": 92,
  "status": "success",
  "video_files": [
    "jump_annotated.avi"
  ]
}
```

Full regression suite:

```text
PYTHONPATH=. .venv/bin/python -m pytest -q
90 passed
```

## Regression Confirmation

No regressions were introduced. Existing Prompts 1-12 tests pass after the S1 stabilization change. Landmark CSV/JSON export, feature extraction, athlete report generation, dashboard generation, and metadata generation continue to use the existing architecture and schemas.

The canonical standard pipeline video is now the annotated MediaPipe visualization, not a copied original input video.
