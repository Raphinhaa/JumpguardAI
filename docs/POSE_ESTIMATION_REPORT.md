# Pose Estimation Report

## Scope

Prompt 10 adds an independent Pose Estimation Layer in `src/pose_estimation.py`. It consumes the Prompt 9 `Video` abstraction and converts validated video frames into MediaPipe pose landmark coordinates. It does not reload videos independently, duplicate video validation, calculate joint angles, compute ROM or symmetry, extract biomechanical features, classify movement, estimate ACL outcomes, estimate injury likelihood, train models, or modify Prompts 1-9 outputs.

## Architecture

The public backend-independent interface is `PoseEstimator`:

- `load_model()`
- `estimate(video)`
- `estimate_frame(frame)`
- `export_landmarks(...)`
- `validate_output(...)`

`MediaPipePoseEstimator` implements the interface using Google's MediaPipe Pose Landmarker Tasks API. If Tasks is unavailable in another environment, the implementation can fall back to classic MediaPipe Pose when that API exists, while keeping the same public interface.

## MediaPipe Backend

Installed package: `mediapipe`.

Model asset: `models/pose_landmarker_lite.task`.

The model asset was downloaded from the official MediaPipe model storage path for Pose Landmarker Lite and is used locally for deterministic inference. Downstream code depends on the `PoseEstimator` interface rather than on MediaPipe-specific objects.

## Coordinate Schema

The output preserves MediaPipe landmark coordinates exactly as returned by the backend. No smoothing, trajectory filtering, coordinate rotation, coordinate normalization beyond MediaPipe's own model output, missing-joint inference, or biomechanical angle calculation is performed.

Each row contains:

- `frame_number`
- `timestamp`
- `landmark_index`
- `landmark_name`
- `x`
- `y`
- `z`
- `visibility`
- `confidence`

The complete MediaPipe 33-landmark set is preserved:

`nose, left_eye_inner, left_eye, left_eye_outer, right_eye_inner, right_eye, right_eye_outer, left_ear, right_ear, mouth_left, mouth_right, left_shoulder, right_shoulder, left_elbow, right_elbow, left_wrist, right_wrist, left_pinky, right_pinky, left_index, right_index, left_thumb, right_thumb, left_hip, right_hip, left_knee, right_knee, left_ankle, right_ankle, left_heel, right_heel, left_foot_index, right_foot_index`

## Missing Data Policy

Every processed frame emits exactly 33 landmark rows. If MediaPipe does not detect a pose or a landmark is unavailable, x/y/z/visibility/confidence are stored as NaN in CSV and null in JSON. The layer never interpolates or fabricates missing landmarks.

Optional confidence filtering preserves the row schema and stores filtered coordinates as missing rather than deleting landmarks.

## Demo Output

Input video: `reports/video_processing/sample_video.avi`.

Processed frame count with `frame_skip=6`: 4.

Landmark rows exported: 132.

Rows with missing x/y/z coordinates: 132.

Generated outputs:

- `reports/pose_estimation/sample_landmarks.csv`
- `reports/pose_estimation/sample_landmarks.json`
- `reports/pose_estimation/landmark_preview.png`
- `reports/pose_estimation/annotated_frames/`
- `reports/pose_estimation/sample_annotated.avi`

The Prompt 9 demo video is synthetic and does not contain a person, so MediaPipe returns missing landmarks. This is valid behavior and demonstrates the missing-data policy without fabricating landmarks.

## Validation

Validation checks ensure:

- deterministic column schema
- exactly 33 landmark rows per processed frame
- MediaPipe landmark names are preserved
- CSV and JSON exports are deterministic
- missing landmarks remain missing

## Visualization Utilities

Debugging utilities include:

- `annotate_frame(...)`
- `landmark_preview(...)`
- `export_annotated_frames(...)`
- `export_annotated_video(...)`

These visualizations do not modify stored landmark data.

## Prompt 11 Integration

Prompt 11 can consume `PoseEstimationResult.landmarks` or the exported CSV/JSON files directly to calculate biomechanical quantities. Prompt 10 intentionally stops at landmark estimation and does not compute joint angles or features.

## Limitations

- Inference quality depends on MediaPipe model behavior and video content.
- The demo video has no human subject, so it is expected to contain missing landmarks.
- No camera calibration, event detection, feature extraction, or clinical interpretation is performed.
