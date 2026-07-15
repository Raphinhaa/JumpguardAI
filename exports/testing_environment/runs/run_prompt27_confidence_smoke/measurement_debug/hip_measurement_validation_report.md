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
| 1 | 62 | 2.06667 | 30.9417 | 97.8726 | 66.931 | 0.505037 | 0.942807 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 2 | 58 | 1.93333 | 18.937 | 83.0473 | 64.1103 | 0.751912 | 0.942265 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 3 | 90 | 3 | 18.1174 | 80.1287 | 62.0112 | 0.370074 | 0.959706 | left hip triplet includes visibility below 0.5 |
| 4 | 56 | 1.86667 | 11.1157 | 63.4009 | 52.2851 | 0.794 | 0.979272 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 5 | 61 | 2.03333 | 69.8625 | 111.854 | 41.9912 | 0.408537 | 0.934921 | left hip triplet includes visibility below 0.5 |
| 6 | 55 | 1.83333 | 17.4503 | 50.2638 | 32.8135 | 0.679767 | 0.97595 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 7 | 43 | 1.43333 | 9.02798 | 40.7243 | 31.6963 | 0.564429 | 0.976029 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 8 | 91 | 3.03333 | 28.7464 | 59.0574 | 30.311 | 0.278874 | 0.944547 | left hip triplet includes visibility below 0.5 |
| 9 | 89 | 2.96667 | 28.6271 | 57.6302 | 29.0031 | 0.448548 | 0.974905 | left hip triplet includes visibility below 0.5 |
| 10 | 67 | 2.23333 | 27.2686 | 54.8459 | 27.5773 | 0.382486 | 0.971809 | left hip triplet includes visibility below 0.5 |

## Confidence And Visibility Summary

| Landmark | Frames | Visibility Mean | Visibility Min | Missing Visibility Frames | Confidence Mean | Confidence Min | Missing Confidence Frames |
|---|---:|---:|---:|---:|---:|---:|---:|
| left_shoulder | 92 | 0.997215 | 0.968094 | 0 | 0.998082 | 0.969389 | 0 |
| right_shoulder | 92 | 0.999152 | 0.99152 | 0 | 0.998901 | 0.980446 | 0 |
| left_hip | 92 | 0.999093 | 0.996347 | 0 | 0.99913 | 0.986711 | 0 |
| right_hip | 92 | 0.999511 | 0.996037 | 0 | 0.999307 | 0.98619 | 0 |
| left_knee | 92 | 0.413005 | 0.128011 | 0 | 0.998672 | 0.987959 | 0 |
| right_knee | 92 | 0.958213 | 0.915665 | 0 | 0.998824 | 0.982405 | 0 |
| left_ankle | 92 | 0.643056 | 0.201713 | 0 | 0.998413 | 0.976299 | 0 |
| right_ankle | 92 | 0.958214 | 0.895729 | 0 | 0.997812 | 0.96089 | 0 |

## Findings

- **Verified implementation trace**: Hip measurements use the existing shoulder -> hip -> knee landmark triplets and the unsigned internal vector-angle formula documented in the code.
- **Observed-data audit**: Large left/right differences, when present, are reported as ranked observations from existing computed values, not as clinical abnormalities or formula errors.
- **Inconclusive cause**: This audit can identify missing or low-confidence landmark evidence, but it cannot prove occlusion, camera perspective, or MediaPipe estimation error without paired visual review and external ground truth.

## Recommendations For Future Work

- Use Measurement Debug Mode to visually inspect ranked frames before considering any formula change.
- If recurrent discrepancies coincide with low shoulder, hip, or knee visibility, document the affected frames as measurement-quality concerns rather than changing biomechanics automatically.
- Do not alter the hip angle definition without paired validation data or an explicitly approved future scientific prompt.
