# Hip Measurement Validation Audit

Developer-only scientific audit generated from existing Prompt 23 diagnostics.
No biomechanics calculations, landmark extraction, feature extraction, exports, or numerical outputs are modified by this report.

## Measurement Definitions

| Signal | Landmarks | Vertex | Vector A | Vector B | Formula | Convention | Range | Interpretation Boundary |
|---|---|---|---|---|---|---|---|---|
| hip_flexion_right | right_shoulder -> right_hip -> right_knee | right_hip | right_shoulder - right_hip | right_knee - right_hip | degrees(arccos(clip(dot(vector_a, vector_b) / (\|\|vector_a\|\| * \|\|vector_b\|\|), -1, 1))) | Unsigned internal 3D vector angle from MediaPipe landmark coordinates. | 0 to 180 when vectors are finite and nonzero; NaN otherwise. | MediaPipe-derived geometric approximation; not laboratory inverse kinematics or a clinical score. |
| hip_flexion_left | left_shoulder -> left_hip -> left_knee | left_hip | left_shoulder - left_hip | left_knee - left_hip | degrees(arccos(clip(dot(vector_a, vector_b) / (\|\|vector_a\|\| * \|\|vector_b\|\|), -1, 1))) | Unsigned internal 3D vector angle from MediaPipe landmark coordinates. | 0 to 180 when vectors are finite and nonzero; NaN otherwise. | MediaPipe-derived geometric approximation; not laboratory inverse kinematics or a clinical score. |
| knee_flexion_right | right_hip -> right_knee -> right_ankle | right_knee | right_hip - right_knee | right_ankle - right_knee | degrees(arccos(clip(dot(vector_a, vector_b) / (\|\|vector_a\|\| * \|\|vector_b\|\|), -1, 1))) | Unsigned internal 3D vector angle from MediaPipe landmark coordinates. | 0 to 180 when vectors are finite and nonzero; NaN otherwise. | MediaPipe-derived geometric approximation; not laboratory inverse kinematics or a clinical score. |
| knee_flexion_left | left_hip -> left_knee -> left_ankle | left_knee | left_hip - left_knee | left_ankle - left_knee | degrees(arccos(clip(dot(vector_a, vector_b) / (\|\|vector_a\|\| * \|\|vector_b\|\|), -1, 1))) | Unsigned internal 3D vector angle from MediaPipe landmark coordinates. | 0 to 180 when vectors are finite and nonzero; NaN otherwise. | MediaPipe-derived geometric approximation; not laboratory inverse kinematics or a clinical score. |
| ankle_angle_right | right_knee -> right_ankle -> right_foot_index | right_ankle | right_knee - right_ankle | right_foot_index - right_ankle | degrees(arccos(clip(dot(vector_a, vector_b) / (\|\|vector_a\|\| * \|\|vector_b\|\|), -1, 1))) | Unsigned internal 3D vector angle from MediaPipe landmark coordinates. | 0 to 180 when vectors are finite and nonzero; NaN otherwise. | MediaPipe-derived geometric approximation; not laboratory inverse kinematics or a clinical score. |
| ankle_angle_left | left_knee -> left_ankle -> left_foot_index | left_ankle | left_knee - left_ankle | left_foot_index - left_ankle | degrees(arccos(clip(dot(vector_a, vector_b) / (\|\|vector_a\|\| * \|\|vector_b\|\|), -1, 1))) | Unsigned internal 3D vector angle from MediaPipe landmark coordinates. | 0 to 180 when vectors are finite and nonzero; NaN otherwise. | MediaPipe-derived geometric approximation; not laboratory inverse kinematics or a clinical score. |

## Largest Observed Hip Differences

Frames are ranked by the existing computed absolute left/right hip angle difference. No clinical threshold is applied.

| Rank | Frame | Timestamp | Left Hip | Right Hip | Abs Diff | Left Visibility Min | Right Visibility Min | Evidence Notes |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 32 | 1.06667 | 63.6468 | 11.214 | 52.4328 | 0.992882 | 0.988939 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 2 | 29 | 0.966667 | 69.0335 | 17.714 | 51.3195 | 0.987835 | 0.975248 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 3 | 31 | 1.03333 | 61.6386 | 20.0761 | 41.5625 | 0.992245 | 0.986485 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 4 | 40 | 1.33333 | 60.7465 | 20.8611 | 39.8855 | 0.986127 | 0.974937 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 5 | 28 | 0.933333 | 33.8721 | 8.05049 | 25.8216 | 0.98814 | 0.976805 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 6 | 38 | 1.26667 | 51.0321 | 25.5102 | 25.5219 | 0.988098 | 0.98772 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 7 | 36 | 1.2 | 30.8558 | 5.7707 | 25.0851 | 0.986035 | 0.980711 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 8 | 37 | 1.23333 | 51.2633 | 28.1587 | 23.1046 | 0.982098 | 0.976523 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 9 | 19 | 0.633333 | 60.3811 | 83.4177 | 23.0366 | 0.987226 | 0.994449 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 10 | 21 | 0.7 | 48.742 | 67.1686 | 18.4265 | 0.94903 | 0.976223 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |

## Confidence And Visibility Summary

| Landmark | Frames | Visibility Mean | Visibility Min | Missing Visibility Frames | Confidence Mean | Confidence Min | Missing Confidence Frames |
|---|---:|---:|---:|---:|---:|---:|---:|
| left_shoulder | 65 | 0.999828 | 0.998461 | 0 | 0.999529 | 0.993937 | 0 |
| right_shoulder | 65 | 0.999498 | 0.996856 | 0 | 0.99896 | 0.992916 | 0 |
| left_hip | 65 | 0.999851 | 0.999384 | 0 | 0.99986 | 0.999194 | 0 |
| right_hip | 65 | 0.999755 | 0.99902 | 0 | 0.999826 | 0.999047 | 0 |
| left_knee | 65 | 0.984145 | 0.882782 | 0 | 0.999031 | 0.993568 | 0 |
| right_knee | 65 | 0.985329 | 0.895543 | 0 | 0.999008 | 0.995311 | 0 |
| left_ankle | 65 | 0.968283 | 0.82984 | 0 | 0.992331 | 0.975649 | 0 |
| right_ankle | 65 | 0.975176 | 0.881337 | 0 | 0.993266 | 0.976615 | 0 |

## Findings

- **Verified implementation trace**: Hip measurements use the existing shoulder -> hip -> knee landmark triplets and the unsigned internal vector-angle formula documented in the code.
- **Observed-data audit**: Large left/right differences, when present, are reported as ranked observations from existing computed values, not as clinical abnormalities or formula errors.
- **Inconclusive cause**: This audit can identify missing or low-confidence landmark evidence, but it cannot prove occlusion, camera perspective, or MediaPipe estimation error without paired visual review and external ground truth.

## Recommendations For Future Work

- Use Measurement Debug Mode to visually inspect ranked frames before considering any formula change.
- If recurrent discrepancies coincide with low shoulder, hip, or knee visibility, document the affected frames as measurement-quality concerns rather than changing biomechanics automatically.
- Do not alter the hip angle definition without paired validation data or an explicitly approved future scientific prompt.
