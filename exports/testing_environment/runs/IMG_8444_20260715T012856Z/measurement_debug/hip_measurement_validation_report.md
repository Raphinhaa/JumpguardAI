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
| 1 | 175 | 5.83333 | 68.1371 | 7.24891 | 60.8882 | 0.433891 | 0.952855 | left hip triplet includes visibility below 0.5 |
| 2 | 176 | 5.86667 | 62.2483 | 10.0212 | 52.227 | 0.406876 | 0.963386 | left hip triplet includes visibility below 0.5 |
| 3 | 173 | 5.76667 | 71.3576 | 19.4587 | 51.8989 | 0.566867 | 0.963531 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 4 | 131 | 4.36667 | 29.7887 | 72.9722 | 43.1835 | 0.823131 | 0.996342 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 5 | 159 | 5.3 | 99.5914 | 142.021 | 42.4292 | 0.410575 | 0.989985 | left hip triplet includes visibility below 0.5 |
| 6 | 174 | 5.8 | 78.8252 | 37.1887 | 41.6365 | 0.469315 | 0.967201 | left hip triplet includes visibility below 0.5 |
| 7 | 172 | 5.73333 | 66.4087 | 25.1832 | 41.2255 | 0.708347 | 0.989429 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 8 | 160 | 5.33333 | 116.779 | 150.871 | 34.0917 | 0.288579 | 0.989069 | left hip triplet includes visibility below 0.5 |
| 9 | 161 | 5.36667 | 109.866 | 143.567 | 33.7009 | 0.24229 | 0.982295 | left hip triplet includes visibility below 0.5 |
| 10 | 109 | 3.63333 | 21.8891 | 54.6326 | 32.7435 | 0.838297 | 0.996006 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |

## Confidence And Visibility Summary

| Landmark | Frames | Visibility Mean | Visibility Min | Missing Visibility Frames | Confidence Mean | Confidence Min | Missing Confidence Frames |
|---|---:|---:|---:|---:|---:|---:|---:|
| left_shoulder | 208 | 0.998928 | 0.982891 | 0 | 0.999389 | 0.989275 | 0 |
| right_shoulder | 208 | 0.999829 | 0.998666 | 0 | 0.999669 | 0.996126 | 0 |
| left_hip | 208 | 0.999236 | 0.993651 | 0 | 0.999623 | 0.993475 | 0 |
| right_hip | 208 | 0.999745 | 0.997965 | 0 | 0.999651 | 0.996032 | 0 |
| left_knee | 208 | 0.567589 | 0.24229 | 0 | 0.998575 | 0.979509 | 0 |
| right_knee | 208 | 0.973733 | 0.877473 | 0 | 0.998923 | 0.987211 | 0 |
| left_ankle | 208 | 0.707593 | 0.348556 | 0 | 0.997514 | 0.970605 | 0 |
| right_ankle | 208 | 0.967199 | 0.859815 | 0 | 0.995413 | 0.927281 | 0 |

## Findings

- **Verified implementation trace**: Hip measurements use the existing shoulder -> hip -> knee landmark triplets and the unsigned internal vector-angle formula documented in the code.
- **Observed-data audit**: Large left/right differences, when present, are reported as ranked observations from existing computed values, not as clinical abnormalities or formula errors.
- **Inconclusive cause**: This audit can identify missing or low-confidence landmark evidence, but it cannot prove occlusion, camera perspective, or MediaPipe estimation error without paired visual review and external ground truth.

## Recommendations For Future Work

- Use Measurement Debug Mode to visually inspect ranked frames before considering any formula change.
- If recurrent discrepancies coincide with low shoulder, hip, or knee visibility, document the affected frames as measurement-quality concerns rather than changing biomechanics automatically.
- Do not alter the hip angle definition without paired validation data or an explicitly approved future scientific prompt.
