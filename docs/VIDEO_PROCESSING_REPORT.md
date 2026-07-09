# Video Processing Report

## Scope

Prompt 9 adds an independent Video Processing Layer in `src/video_processing.py`. It prepares uploaded videos for future pose-estimation work. It does not perform pose estimation, estimate joints, calculate joint angles, extract biomechanical features, rerun analytics, infer landing events, train models, or modify previous project outputs.

## Architecture

The layer exposes a reusable `Video` abstraction and supporting utilities:

- `Video(path)`: validates and opens MP4, MOV, or AVI files.
- `VideoMetadata`: filename, path, duration, frame count, FPS, resolution, and codec.
- `VideoPreprocessingConfig`: optional resize, grayscale, normalization, and frame sampling.
- `preprocess_frame(...)`: non-destructive frame preprocessing.
- `save_frames(...)`: deterministic image export for selected frames.
- Preview helpers: first frame, last frame, playback storyboard, and frame timeline.

The module is independent and does not import Dataset, feature extraction, EDA, ML, intelligence, reporting, or dashboard logic.

## Supported Formats

Supported file extensions: `.mp4`, `.mov`, `.avi`.

Validation checks:

- file existence
- supported extension
- OpenCV readability
- frame count greater than zero
- FPS greater than zero
- positive width and height
- codec metadata when available

Unsupported formats, including the existing sample `.webm`, are rejected rather than guessed.

## API Example

```python
from src.video_processing import Video, VideoPreprocessingConfig

video = Video("reports/video_processing/sample_video.avi")
metadata = video.metadata
frame = video.get_frame(0)
frame_at_time = video.get_frame_at_timestamp(0.5)
clip = video.select_clip_by_frames(0, 10)
processed = video.extract_frames([0, 5, 10], VideoPreprocessingConfig(grayscale=True))
```

## Preprocessing Options

All preprocessing is optional and non-destructive. Source video pixels are not modified.

- Resize: deterministic OpenCV area interpolation to configured `(width, height)`.
- Grayscale: BGR-to-grayscale conversion.
- Normalization: float32 conversion to `[0, 1]`.
- Sampling: `sample_every_n` frame iteration.

## Clip Selection

Clips can be selected by explicit frame indices or timestamp bounds. The module does not detect landing, takeoff, impact, or any other movement event automatically.

## Demo Artifact

Generated deterministic demo video: `reports/video_processing/sample_video.avi`.

Demo metadata:

| Field | Value |
| --- | ---: |
| Frame count | 24 |
| FPS | 12.000 |
| Duration seconds | 2.000 |
| Width | 96 |
| Height | 64 |
| Codec | `MJPG` |
| Sampled frames with Prompt 9 config | 6 |

## Prompt 10 Integration

Prompt 10 can consume this layer directly as `Video -> Frames`. Pose-estimation code should receive frames from `Video.iter_frames`, `Video.extract_frames`, or clip-selection methods. Any pose landmarks, joint estimates, or biomechanical feature computation must be implemented outside this layer in a future prompt.

## Limitations

- Codec availability depends on the local OpenCV build.
- Timestamp access maps timestamps to nearest frame index using FPS metadata.
- No pixel enhancement, denoising, stabilization, calibration, camera inference, event detection, or pose estimation is performed.
