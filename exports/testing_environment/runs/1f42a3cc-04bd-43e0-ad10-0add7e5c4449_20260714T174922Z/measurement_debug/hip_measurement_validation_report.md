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
| 1 | 145 | 2.41667 | 22.555 | 97.7811 | 75.2261 | 0.769902 | 0.962989 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 2 | 139 | 2.31667 | 91.7143 | 157.154 | 65.4398 | 0.978407 | 0.857248 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 3 | 95 | 1.58333 | 24.6458 | 85.9727 | 61.3269 | 0.818897 | 0.987868 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 4 | 140 | 2.33333 | 74.8212 | 128.427 | 53.6054 | 0.923169 | 0.769656 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 5 | 144 | 2.4 | 10.1004 | 59.8083 | 49.7079 | 0.741314 | 0.844585 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 6 | 72 | 1.2 | 34.1328 | 83.8398 | 49.707 | 0.779857 | 0.888518 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 7 | 252 | 4.2 | 24.1538 | 73.2673 | 49.1135 | 0.974696 | 0.940164 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 8 | 206 | 3.43333 | 55.5027 | 9.81096 | 45.6917 | 0.962656 | 0.87587 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 9 | 115 | 1.91667 | 44.9683 | 6.23164 | 38.7367 | 0.913307 | 0.768853 | No missing/nonfinite hip-triplet landmark evidence detected in existing debug records. |
| 10 | 96 | 1.6 | 24.1971 | 61.7868 | 37.5897 | 0.479079 | 0.916731 | left hip triplet includes visibility below 0.5 |

## Confidence And Visibility Summary

| Landmark | Frames | Visibility Mean | Visibility Min | Missing Visibility Frames | Confidence Mean | Confidence Min | Missing Confidence Frames |
|---|---:|---:|---:|---:|---:|---:|---:|
| left_shoulder | 348 | 0.997823 | 0.899502 | 76 | 0.995179 | 0.785435 | 76 |
| right_shoulder | 348 | 0.998253 | 0.937002 | 76 | 0.99637 | 0.762306 | 76 |
| left_hip | 348 | 0.997519 | 0.847956 | 76 | 0.991557 | 0.420416 | 76 |
| right_hip | 348 | 0.997884 | 0.88063 | 76 | 0.992461 | 0.421479 | 76 |
| left_knee | 348 | 0.713843 | 0.132056 | 76 | 0.99274 | 0.770995 | 76 |
| right_knee | 348 | 0.802678 | 0.0833206 | 76 | 0.994954 | 0.856066 | 76 |
| left_ankle | 348 | 0.729237 | 0.184738 | 76 | 0.986339 | 0.69444 | 76 |
| right_ankle | 348 | 0.795965 | 0.0796544 | 76 | 0.987247 | 0.740519 | 76 |

## Findings

- **Verified implementation trace**: Hip measurements use the existing shoulder -> hip -> knee landmark triplets and the unsigned internal vector-angle formula documented in the code.
- **Observed-data audit**: Large left/right differences, when present, are reported as ranked observations from existing computed values, not as clinical abnormalities or formula errors.
- **Inconclusive cause**: This audit can identify missing or low-confidence landmark evidence, but it cannot prove occlusion, camera perspective, or MediaPipe estimation error without paired visual review and external ground truth.

## Recommendations For Future Work

- Use Measurement Debug Mode to visually inspect ranked frames before considering any formula change.
- If recurrent discrepancies coincide with low shoulder, hip, or knee visibility, document the affected frames as measurement-quality concerns rather than changing biomechanics automatically.
- Do not alter the hip angle definition without paired validation data or an explicitly approved future scientific prompt.
