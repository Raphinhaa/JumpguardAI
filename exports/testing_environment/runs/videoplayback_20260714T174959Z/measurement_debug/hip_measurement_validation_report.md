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
| 1 | 50 | 1.67381 | 81.5886 | 10.3666 | 71.2221 | 0.390461 | 0.959549 | left hip triplet includes visibility below 0.5 |
| 2 | 51 | 1.70728 | 79.9974 | 8.93441 | 71.063 | 0.432884 | 0.970254 | left hip triplet includes visibility below 0.5 |
| 3 | 46 | 1.5399 | 80.7731 | 14.7637 | 66.0094 | 0.234487 | 0.902834 | left hip triplet includes visibility below 0.5 |
| 4 | 47 | 1.57338 | 83.9576 | 18.333 | 65.6246 | 0.270222 | 0.935947 | left hip triplet includes visibility below 0.5 |
| 5 | 52 | 1.74076 | 76.3622 | 12.9647 | 63.3975 | 0.415826 | 0.970341 | left hip triplet includes visibility below 0.5 |
| 6 | 48 | 1.60686 | 73.7286 | 16.2062 | 57.5224 | 0.334835 | 0.93834 | left hip triplet includes visibility below 0.5 |
| 7 | 42 | 1.406 | 77.4264 | 22.6857 | 54.7406 | 0.284211 | 0.92524 | left hip triplet includes visibility below 0.5 |
| 8 | 45 | 1.50643 | 73.4514 | 19.0498 | 54.4016 | 0.242333 | 0.912514 | left hip triplet includes visibility below 0.5 |
| 9 | 49 | 1.64033 | 73.9303 | 20.2513 | 53.679 | 0.389042 | 0.944083 | left hip triplet includes visibility below 0.5 |
| 10 | 53 | 1.77424 | 71.0792 | 19.0475 | 52.0317 | 0.466066 | 0.977528 | left hip triplet includes visibility below 0.5 |

## Confidence And Visibility Summary

| Landmark | Frames | Visibility Mean | Visibility Min | Missing Visibility Frames | Confidence Mean | Confidence Min | Missing Confidence Frames |
|---|---:|---:|---:|---:|---:|---:|---:|
| left_shoulder | 140 | 0.997747 | 0.969195 | 1 | 0.9987 | 0.976867 | 1 |
| right_shoulder | 140 | 0.999411 | 0.981354 | 1 | 0.999309 | 0.982905 | 1 |
| left_hip | 140 | 0.999002 | 0.996889 | 1 | 0.999329 | 0.994468 | 1 |
| right_hip | 140 | 0.999572 | 0.99803 | 1 | 0.999589 | 0.997374 | 1 |
| left_knee | 140 | 0.408965 | 0.109666 | 1 | 0.999066 | 0.994511 | 1 |
| right_knee | 140 | 0.947619 | 0.747102 | 1 | 0.99933 | 0.995821 | 1 |
| left_ankle | 140 | 0.599649 | 0.141644 | 1 | 0.998962 | 0.994129 | 1 |
| right_ankle | 140 | 0.936982 | 0.716264 | 1 | 0.998837 | 0.991426 | 1 |

## Findings

- **Verified implementation trace**: Hip measurements use the existing shoulder -> hip -> knee landmark triplets and the unsigned internal vector-angle formula documented in the code.
- **Observed-data audit**: Large left/right differences, when present, are reported as ranked observations from existing computed values, not as clinical abnormalities or formula errors.
- **Inconclusive cause**: This audit can identify missing or low-confidence landmark evidence, but it cannot prove occlusion, camera perspective, or MediaPipe estimation error without paired visual review and external ground truth.

## Recommendations For Future Work

- Use Measurement Debug Mode to visually inspect ranked frames before considering any formula change.
- If recurrent discrepancies coincide with low shoulder, hip, or knee visibility, document the affected frames as measurement-quality concerns rather than changing biomechanics automatically.
- Do not alter the hip angle definition without paired validation data or an explicitly approved future scientific prompt.
