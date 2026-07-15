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
| 1 | 55 | 1.83333 | 23.2877 | 113.568 | 90.2806 | 0.724294 | 0.99746 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 2 | 56 | 1.86667 | 26.5126 | 106.686 | 80.1733 | 0.597267 | 0.995463 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 3 | 57 | 1.9 | 32.0389 | 103.24 | 71.2013 | 0.669921 | 0.997056 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 4 | 27 | 0.9 | 70.5171 | 10.2182 | 60.2989 | 0.448019 | 0.949613 | left hip triplet includes visibility below 0.5 |
| 5 | 53 | 1.76667 | 25.1216 | 81.8099 | 56.6883 | 0.726364 | 0.997181 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 6 | 54 | 1.8 | 29.8927 | 68.9399 | 39.0471 | 0.618487 | 0.99523 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 7 | 39 | 1.3 | 32.0819 | 2.27847 | 29.8034 | 0.738041 | 0.995229 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 8 | 52 | 1.73333 | 20.5539 | 50.2326 | 29.6788 | 0.654976 | 0.992004 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 9 | 40 | 1.33333 | 27.3034 | 3.53909 | 23.7643 | 0.642627 | 0.992657 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 10 | 26 | 0.866667 | 55.5299 | 31.8139 | 23.716 | 0.495812 | 0.954167 | left hip triplet includes visibility below 0.5 |

## Confidence And Visibility Summary

| Landmark | Frames | Visibility Mean | Visibility Min | Missing Visibility Frames | Confidence Mean | Confidence Min | Missing Confidence Frames |
|---|---:|---:|---:|---:|---:|---:|---:|
| left_shoulder | 58 | 0.999525 | 0.996652 | 0 | 0.999692 | 0.996296 | 0 |
| right_shoulder | 58 | 0.999874 | 0.998439 | 0 | 0.999706 | 0.995208 | 0 |
| left_hip | 58 | 0.999515 | 0.997665 | 0 | 0.999839 | 0.998829 | 0 |
| right_hip | 58 | 0.999827 | 0.998672 | 0 | 0.999861 | 0.998569 | 0 |
| left_knee | 58 | 0.502486 | 0.262568 | 0 | 0.998624 | 0.991854 | 0 |
| right_knee | 58 | 0.977337 | 0.935366 | 0 | 0.99883 | 0.992856 | 0 |
| left_ankle | 58 | 0.673105 | 0.394361 | 0 | 0.996613 | 0.987988 | 0 |
| right_ankle | 58 | 0.96397 | 0.912796 | 0 | 0.991032 | 0.972302 | 0 |

## Findings

- **Verified implementation trace**: Hip measurements use the existing shoulder -> hip -> knee landmark triplets and the unsigned internal vector-angle formula documented in the code.
- **Observed-data audit**: Large left/right differences, when present, are reported as ranked observations from existing computed values, not as clinical abnormalities or formula errors.
- **Inconclusive cause**: This audit can identify missing or low-confidence landmark evidence, but it cannot prove occlusion, camera perspective, or MediaPipe estimation error without paired visual review and external ground truth.

## Recommendations For Future Work

- Use Measurement Debug Mode to visually inspect ranked frames before considering any formula change.
- If recurrent discrepancies coincide with low shoulder, hip, or knee visibility, document the affected frames as measurement-quality concerns rather than changing biomechanics automatically.
- Do not alter the hip angle definition without paired validation data or an explicitly approved future scientific prompt.
