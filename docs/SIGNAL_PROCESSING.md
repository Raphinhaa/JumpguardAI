# Signal Processing

## Reference Dataset Signal Processing Recovery

| Processing step | Recovered dataset method | Confidence | Evidence |
|---|---|---|---|
| Marker gap filling / interpolation | Unknown from available evidence. | Unknown | No raw C3D, preprocessing scripts, or methods publication recovered. |
| Marker filtering | Unknown from available evidence. | Unknown | No cutoff frequency, filter type, order, or phase information recovered. |
| Joint-angle filtering | Unknown from available evidence. | Unknown | `Joint_Angles` are already processed outputs; no generation settings recovered. |
| COM filtering / differentiation | Unknown from available evidence. | Unknown | COM arrays are present, but generation method is not documented. |
| Resampling | Unknown from available evidence. | Unknown | Time step implies 250 Hz, but no resampling method is documented. |
| Coordinate transforms | Unknown from available evidence. | Unknown | No lab-coordinate or model-coordinate documentation recovered. |
| Normalization | Unknown for raw dataset generation. | Unknown | Participant metadata contains anthropometrics, but no normalization method for IK values is documented. |
| Trial trimming | Unknown from available evidence. | Unknown | Valid frame counts vary from 842 to 2280 and time starts at 0; trimming criteria are not documented. |

## Current Project Feature Processing

The current project extracts full-recording features from the stored `Joint_Angles` arrays. It does not apply additional filtering, smoothing, interpolation, normalization, or event-windowing during feature extraction. Evidence: `src/feature_engineering.py` and `docs/FEATURE_REPORT.md`.

## JumpGuard Uploaded-Video Processing

Prompt 10 exports MediaPipe landmarks without smoothing, trajectory filtering, coordinate rotation, missing-joint inference, or biomechanical angle calculation. Prompt 11 computes deterministic vector-geometry angles and full-recording descriptors. Evidence: `docs/POSE_ESTIMATION_REPORT.md`, `docs/FEATURE_EXTRACTION_REPORT.md`, and `docs/ANGLE_DEFINITION_AUDIT.md`.

## Conclusion

Reference dataset preprocessing remains a major unrecovered methodology component. Harmonization should not assume that the reference IK signals and JumpGuard signals have compatible filtering, coordinate transforms, or temporal windows.
