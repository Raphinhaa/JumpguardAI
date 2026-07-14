# Implementation Validation

This document compares the literature-backed measurement standard against the current JumpGuard implementation without modifying the implementation.

## Validation Legend

| Status | Meaning |
|---|---|
| Verified Match | Current implementation exactly matches the documented mathematical definition. |
| Partial Match | Formula is explicit and useful, but literature support is construct-level rather than exact-method support. |
| Unknown | Available evidence cannot verify the scientific equivalence or acquisition validity. |
| Not Supported | The implementation would make a claim that literature or available evidence does not support. |

## Source-Code Evidence

| Component | Source | Validation result |
|---|---|---|
| Angle landmarks and vector angle formula | `src/feature_extraction.py:ANGLE_SIGNAL_MAP`, `_angle_for_points`, `_angle_between` | Verified implementation of deterministic 3D vector geometry. |
| Dataset feature descriptors | `src/feature_engineering.py:FeatureExtractor.extract`; `src/features/statistical.py` | Verified formulas for descriptors over full recordings. |
| Uploaded-video descriptors | `src/feature_extraction.py:calculate_temporal_features`, `_finite_descriptor`, `_time_to_peak` | Verified formulas over finite full-recording values. |
| Symmetry formulas | `src/features/symmetry.py` | Verified formulas for absolute difference, percent difference, and signed symmetry index. |
| Landing events | `src/feature_extraction.py:_landing_events` | Beginning, end, and duration remain missing; no undocumented detector is introduced. |

## Feature-by-Feature Validation

| Feature | Implementation formula | Literature-backed definition | Match status | Confidence | Rationale |
|---|---|---|---|---|---|
| `hip_flexion_right_mean` | `Σx / N` | Average full-recording joint-angle magnitude. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `hip_flexion_right_median` | `median(x)` | Median full-recording joint-angle magnitude. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `hip_flexion_right_std` | `sqrt(Σ(x-mean)² / N)` | Full-recording angular variability as population standard deviation. | Verified Match | Moderate | Formula is implementation-verified; reliability and measurement-error interpretation require task-specific validation. |
| `hip_flexion_right_variance` | `Σ(x-mean)² / N` | Full-recording angular variability as population variance. | Verified Match | Moderate | Formula is implementation-verified; reliability and measurement-error interpretation require task-specific validation. |
| `hip_flexion_right_maximum` | `max(x)` | Maximum full-recording joint-angle value. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `hip_flexion_right_minimum` | `min(x)` | Minimum full-recording joint-angle value. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `hip_flexion_right_rom` | `max(x) - min(x)` | Full-recording angular excursion computed as maximum minus minimum. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `hip_flexion_right_time_to_peak` | `time[argmax(x)] - time[0]` | Elapsed time from recording start to first maximum; event-relative meaning is inconclusive. | Partial Match | Moderate | Formula is implementation-verified, but literature-backed event-relative peak timing is not established for the full-recording window. |
| `hip_flexion_left_mean` | `Σx / N` | Average full-recording joint-angle magnitude. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `hip_flexion_left_median` | `median(x)` | Median full-recording joint-angle magnitude. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `hip_flexion_left_std` | `sqrt(Σ(x-mean)² / N)` | Full-recording angular variability as population standard deviation. | Verified Match | Moderate | Formula is implementation-verified; reliability and measurement-error interpretation require task-specific validation. |
| `hip_flexion_left_variance` | `Σ(x-mean)² / N` | Full-recording angular variability as population variance. | Verified Match | Moderate | Formula is implementation-verified; reliability and measurement-error interpretation require task-specific validation. |
| `hip_flexion_left_maximum` | `max(x)` | Maximum full-recording joint-angle value. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `hip_flexion_left_minimum` | `min(x)` | Minimum full-recording joint-angle value. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `hip_flexion_left_rom` | `max(x) - min(x)` | Full-recording angular excursion computed as maximum minus minimum. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `hip_flexion_left_time_to_peak` | `time[argmax(x)] - time[0]` | Elapsed time from recording start to first maximum; event-relative meaning is inconclusive. | Partial Match | Moderate | Formula is implementation-verified, but literature-backed event-relative peak timing is not established for the full-recording window. |
| `knee_flexion_right_mean` | `Σx / N` | Average full-recording joint-angle magnitude. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `knee_flexion_right_median` | `median(x)` | Median full-recording joint-angle magnitude. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `knee_flexion_right_std` | `sqrt(Σ(x-mean)² / N)` | Full-recording angular variability as population standard deviation. | Verified Match | Moderate | Formula is implementation-verified; reliability and measurement-error interpretation require task-specific validation. |
| `knee_flexion_right_variance` | `Σ(x-mean)² / N` | Full-recording angular variability as population variance. | Verified Match | Moderate | Formula is implementation-verified; reliability and measurement-error interpretation require task-specific validation. |
| `knee_flexion_right_maximum` | `max(x)` | Maximum full-recording joint-angle value. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `knee_flexion_right_minimum` | `min(x)` | Minimum full-recording joint-angle value. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `knee_flexion_right_rom` | `max(x) - min(x)` | Full-recording angular excursion computed as maximum minus minimum. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `knee_flexion_right_time_to_peak` | `time[argmax(x)] - time[0]` | Elapsed time from recording start to first maximum; event-relative meaning is inconclusive. | Partial Match | Moderate | Formula is implementation-verified, but literature-backed event-relative peak timing is not established for the full-recording window. |
| `knee_flexion_left_mean` | `Σx / N` | Average full-recording joint-angle magnitude. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `knee_flexion_left_median` | `median(x)` | Median full-recording joint-angle magnitude. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `knee_flexion_left_std` | `sqrt(Σ(x-mean)² / N)` | Full-recording angular variability as population standard deviation. | Verified Match | Moderate | Formula is implementation-verified; reliability and measurement-error interpretation require task-specific validation. |
| `knee_flexion_left_variance` | `Σ(x-mean)² / N` | Full-recording angular variability as population variance. | Verified Match | Moderate | Formula is implementation-verified; reliability and measurement-error interpretation require task-specific validation. |
| `knee_flexion_left_maximum` | `max(x)` | Maximum full-recording joint-angle value. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `knee_flexion_left_minimum` | `min(x)` | Minimum full-recording joint-angle value. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `knee_flexion_left_rom` | `max(x) - min(x)` | Full-recording angular excursion computed as maximum minus minimum. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `knee_flexion_left_time_to_peak` | `time[argmax(x)] - time[0]` | Elapsed time from recording start to first maximum; event-relative meaning is inconclusive. | Partial Match | Moderate | Formula is implementation-verified, but literature-backed event-relative peak timing is not established for the full-recording window. |
| `ankle_angle_right_mean` | `Σx / N` | Average full-recording joint-angle magnitude. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `ankle_angle_right_median` | `median(x)` | Median full-recording joint-angle magnitude. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `ankle_angle_right_std` | `sqrt(Σ(x-mean)² / N)` | Full-recording angular variability as population standard deviation. | Verified Match | Moderate | Formula is implementation-verified; reliability and measurement-error interpretation require task-specific validation. |
| `ankle_angle_right_variance` | `Σ(x-mean)² / N` | Full-recording angular variability as population variance. | Verified Match | Moderate | Formula is implementation-verified; reliability and measurement-error interpretation require task-specific validation. |
| `ankle_angle_right_maximum` | `max(x)` | Maximum full-recording joint-angle value. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `ankle_angle_right_minimum` | `min(x)` | Minimum full-recording joint-angle value. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `ankle_angle_right_rom` | `max(x) - min(x)` | Full-recording angular excursion computed as maximum minus minimum. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `ankle_angle_right_time_to_peak` | `time[argmax(x)] - time[0]` | Elapsed time from recording start to first maximum; event-relative meaning is inconclusive. | Partial Match | Moderate | Formula is implementation-verified, but literature-backed event-relative peak timing is not established for the full-recording window. |
| `ankle_angle_left_mean` | `Σx / N` | Average full-recording joint-angle magnitude. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `ankle_angle_left_median` | `median(x)` | Median full-recording joint-angle magnitude. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `ankle_angle_left_std` | `sqrt(Σ(x-mean)² / N)` | Full-recording angular variability as population standard deviation. | Verified Match | Moderate | Formula is implementation-verified; reliability and measurement-error interpretation require task-specific validation. |
| `ankle_angle_left_variance` | `Σ(x-mean)² / N` | Full-recording angular variability as population variance. | Verified Match | Moderate | Formula is implementation-verified; reliability and measurement-error interpretation require task-specific validation. |
| `ankle_angle_left_maximum` | `max(x)` | Maximum full-recording joint-angle value. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `ankle_angle_left_minimum` | `min(x)` | Minimum full-recording joint-angle value. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `ankle_angle_left_rom` | `max(x) - min(x)` | Full-recording angular excursion computed as maximum minus minimum. | Verified Match | Moderate-to-high | Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window. |
| `ankle_angle_left_time_to_peak` | `time[argmax(x)] - time[0]` | Elapsed time from recording start to first maximum; event-relative meaning is inconclusive. | Partial Match | Moderate | Formula is implementation-verified, but literature-backed event-relative peak timing is not established for the full-recording window. |
| `hip_flexion_rom_absolute_difference` | `|ROM_L - ROM_R|` | Unsigned bilateral ROM difference as a side-to-side symmetry descriptor. | Verified Match | Moderate | Formula is implementation-verified and bilateral difference is a supported construct; no clinical threshold is applied. |
| `hip_flexion_rom_percent_difference` | `100 × |ROM_L-ROM_R| / ((|ROM_L|+|ROM_R|)/2)` | Bilateral ROM asymmetry normalized to average side magnitude; formula conventions vary. | Partial Match | Moderate | Formula is implementation-verified, but symmetry-index conventions vary across biomechanics literature. |
| `hip_flexion_rom_symmetry_index` | `100 × (ROM_L-ROM_R) / ((|ROM_L|+|ROM_R|)/2)` | Signed bilateral ROM symmetry index; formula conventions vary. | Partial Match | Moderate | Formula is implementation-verified, but symmetry-index conventions vary across biomechanics literature. |
| `knee_flexion_rom_absolute_difference` | `|ROM_L - ROM_R|` | Unsigned bilateral ROM difference as a side-to-side symmetry descriptor. | Verified Match | Moderate | Formula is implementation-verified and bilateral difference is a supported construct; no clinical threshold is applied. |
| `knee_flexion_rom_percent_difference` | `100 × |ROM_L-ROM_R| / ((|ROM_L|+|ROM_R|)/2)` | Bilateral ROM asymmetry normalized to average side magnitude; formula conventions vary. | Partial Match | Moderate | Formula is implementation-verified, but symmetry-index conventions vary across biomechanics literature. |
| `knee_flexion_rom_symmetry_index` | `100 × (ROM_L-ROM_R) / ((|ROM_L|+|ROM_R|)/2)` | Signed bilateral ROM symmetry index; formula conventions vary. | Partial Match | Moderate | Formula is implementation-verified, but symmetry-index conventions vary across biomechanics literature. |
| `ankle_angle_rom_absolute_difference` | `|ROM_L - ROM_R|` | Unsigned bilateral ROM difference as a side-to-side symmetry descriptor. | Verified Match | Moderate | Formula is implementation-verified and bilateral difference is a supported construct; no clinical threshold is applied. |
| `ankle_angle_rom_percent_difference` | `100 × |ROM_L-ROM_R| / ((|ROM_L|+|ROM_R|)/2)` | Bilateral ROM asymmetry normalized to average side magnitude; formula conventions vary. | Partial Match | Moderate | Formula is implementation-verified, but symmetry-index conventions vary across biomechanics literature. |
| `ankle_angle_rom_symmetry_index` | `100 × (ROM_L-ROM_R) / ((|ROM_L|+|ROM_R|)/2)` | Signed bilateral ROM symmetry index; formula conventions vary. | Partial Match | Moderate | Formula is implementation-verified, but symmetry-index conventions vary across biomechanics literature. |

## Explicit Non-Matches

- JumpGuard MediaPipe angles are not validated as ISB joint coordinate angles.
- JumpGuard MediaPipe angles are not validated as OpenSim inverse-kinematics coordinates.
- JumpGuard does not compute knee abduction moments, ground-reaction forces, LESS scores, or ACL injury probabilities.
- JumpGuard does not identify initial contact, stance, propulsion, or landing phase using a literature-validated event method.
