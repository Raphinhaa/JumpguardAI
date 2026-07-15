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
| 1 | 56 | 1.86667 | 67.8698 | 3.25582 | 64.614 | 0.412333 | 0.961117 | left hip triplet includes visibility below 0.5 |
| 2 | 23 | 0.766667 | 57.7781 | 12.9076 | 44.8705 | 0.474882 | 0.959719 | left hip triplet includes visibility below 0.5 |
| 3 | 55 | 1.83333 | 54.3413 | 11.4308 | 42.9105 | 0.440332 | 0.93772 | left hip triplet includes visibility below 0.5 |
| 4 | 25 | 0.833333 | 51.9333 | 14.7726 | 37.1607 | 0.434503 | 0.955834 | left hip triplet includes visibility below 0.5 |
| 5 | 82 | 2.73333 | 107.759 | 141.173 | 33.4143 | 0.239276 | 0.9439 | left hip triplet includes visibility below 0.5 |
| 6 | 16 | 0.533333 | 44.5461 | 12.4883 | 32.0578 | 0.321783 | 0.946733 | left hip triplet includes visibility below 0.5 |
| 7 | 47 | 1.56667 | 108.836 | 138.363 | 29.5273 | 0.170668 | 0.979357 | left hip triplet includes visibility below 0.5 |
| 8 | 52 | 1.73333 | 82.7835 | 53.6613 | 29.1222 | 0.356306 | 0.956345 | left hip triplet includes visibility below 0.5 |
| 9 | 83 | 2.76667 | 110.218 | 139.337 | 29.1186 | 0.305909 | 0.952818 | left hip triplet includes visibility below 0.5 |
| 10 | 68 | 2.26667 | 20.4338 | 48.9034 | 28.4696 | 0.320237 | 0.90966 | left hip triplet includes visibility below 0.5 |

## Confidence And Visibility Summary

| Landmark | Frames | Visibility Mean | Visibility Min | Missing Visibility Frames | Confidence Mean | Confidence Min | Missing Confidence Frames |
|---|---:|---:|---:|---:|---:|---:|---:|
| left_shoulder | 101 | 0.99853 | 0.990692 | 0 | 0.999087 | 0.991492 | 0 |
| right_shoulder | 101 | 0.999802 | 0.997153 | 0 | 0.999659 | 0.993997 | 0 |
| left_hip | 101 | 0.998814 | 0.989078 | 0 | 0.999528 | 0.994973 | 0 |
| right_hip | 101 | 0.999606 | 0.996851 | 0 | 0.999694 | 0.997357 | 0 |
| left_knee | 101 | 0.36091 | 0.155383 | 0 | 0.998425 | 0.990521 | 0 |
| right_knee | 101 | 0.957663 | 0.90966 | 0 | 0.999053 | 0.994135 | 0 |
| left_ankle | 101 | 0.576083 | 0.274378 | 0 | 0.998221 | 0.986221 | 0 |
| right_ankle | 101 | 0.943671 | 0.829829 | 0 | 0.997356 | 0.978044 | 0 |

## Findings

- **Verified implementation trace**: Hip measurements use the existing shoulder -> hip -> knee landmark triplets and the unsigned internal vector-angle formula documented in the code.
- **Observed-data audit**: Large left/right differences, when present, are reported as ranked observations from existing computed values, not as clinical abnormalities or formula errors.
- **Inconclusive cause**: This audit can identify missing or low-confidence landmark evidence, but it cannot prove occlusion, camera perspective, or MediaPipe estimation error without paired visual review and external ground truth.

## Recommendations For Future Work

- Use Measurement Debug Mode to visually inspect ranked frames before considering any formula change.
- If recurrent discrepancies coincide with low shoulder, hip, or knee visibility, document the affected frames as measurement-quality concerns rather than changing biomechanics automatically.
- Do not alter the hip angle definition without paired validation data or an explicitly approved future scientific prompt.
