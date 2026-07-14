# Scientific Equivalence Matrix

Classification terms: Verified Equivalent, Equivalent after transformation, Unknown, Not Equivalent.

| Measurement level | Hip | Knee | Ankle | Symmetry features | Evidence |
|---|---|---|---|---|---|
| Feature names | Verified Equivalent | Verified Equivalent | Verified Equivalent | Verified Equivalent | Shared 57-feature schema enforced by code. |
| Units | Verified Equivalent for exported degrees/seconds/percent | Verified Equivalent for exported degrees/seconds/percent | Verified Equivalent for exported degrees/seconds/percent | Verified Equivalent | Dataset header `inDegrees=yes`; JumpGuard angles are degrees. |
| Raw landmarks / segment sources | Not Equivalent | Not Equivalent | Not Equivalent | Unknown via upstream ROM | Dataset stores IK columns; JumpGuard uses MediaPipe triplets. |
| Coordinate system | Unknown | Unknown | Unknown | Unknown | Dataset coordinate system unrecovered; JumpGuard MediaPipe coordinates documented. |
| Angle convention | Unknown | Unknown | Unknown | Unknown | Dataset sign/range/internal-external conventions unrecovered. |
| Required transformation | Unknown | Unknown | Unknown | Unknown | No evidence supports inversion, sign flip, offset, or event window. |
| Aggregation formulas | Verified Equivalent | Verified Equivalent | Verified Equivalent | Verified Equivalent | Prompt 3/P11 code formulas match. |
| Event/window definition | Verified Equivalent for current full-recording features; Unknown for event-based future features | Verified Equivalent for current full-recording features; Unknown for event-based future features | Verified Equivalent for current full-recording features; Unknown for event-based future features | Verified Equivalent for current full-recording ROM inputs | Event fields are not used; current features are full-recording. |
| Overall scientific equivalence | Unknown | Unknown | Unknown | Unknown / formula-only equivalence | Upstream IK methodology is unrecovered. |

## Feature-Level Matrix

| Feature | Formula | Raw measurement source | Event/window | Overall classification |
|---|---|---|---|---|
| `hip_flexion_right_mean` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `hip_flexion_right_median` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `hip_flexion_right_std` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `hip_flexion_right_variance` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `hip_flexion_right_maximum` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `hip_flexion_right_minimum` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `hip_flexion_right_rom` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `hip_flexion_right_time_to_peak` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `hip_flexion_left_mean` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `hip_flexion_left_median` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `hip_flexion_left_std` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `hip_flexion_left_variance` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `hip_flexion_left_maximum` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `hip_flexion_left_minimum` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `hip_flexion_left_rom` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `hip_flexion_left_time_to_peak` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `knee_flexion_right_mean` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `knee_flexion_right_median` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `knee_flexion_right_std` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `knee_flexion_right_variance` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `knee_flexion_right_maximum` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `knee_flexion_right_minimum` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `knee_flexion_right_rom` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `knee_flexion_right_time_to_peak` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `knee_flexion_left_mean` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `knee_flexion_left_median` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `knee_flexion_left_std` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `knee_flexion_left_variance` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `knee_flexion_left_maximum` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `knee_flexion_left_minimum` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `knee_flexion_left_rom` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `knee_flexion_left_time_to_peak` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `ankle_angle_right_mean` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `ankle_angle_right_median` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `ankle_angle_right_std` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `ankle_angle_right_variance` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `ankle_angle_right_maximum` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `ankle_angle_right_minimum` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `ankle_angle_right_rom` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `ankle_angle_right_time_to_peak` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `ankle_angle_left_mean` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `ankle_angle_left_median` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `ankle_angle_left_std` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `ankle_angle_left_variance` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `ankle_angle_left_maximum` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `ankle_angle_left_minimum` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `ankle_angle_left_rom` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `ankle_angle_left_time_to_peak` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `hip_flexion_rom_absolute_difference` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `hip_flexion_rom_percent_difference` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `hip_flexion_rom_symmetry_index` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `knee_flexion_rom_absolute_difference` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `knee_flexion_rom_percent_difference` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `knee_flexion_rom_symmetry_index` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `ankle_angle_rom_absolute_difference` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `ankle_angle_rom_percent_difference` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
| `ankle_angle_rom_symmetry_index` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |
