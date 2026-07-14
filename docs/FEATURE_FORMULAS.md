# Feature Formulas

These formulas are recovered from the project feature extraction code. They define the current reference feature table and JumpGuard-compatible feature schema; they do not recover the upstream laboratory IK angle-generation method.

## Scalar Descriptor Formulas

Let `x` be the finite full-recording angle signal and `t` its corresponding time vector.

| Descriptor | Formula | Dataset implementation | JumpGuard implementation | Formula equivalence |
|---|---|---|---|---|
| Maximum | `max(x)` | `describe_signal` / `FeatureExtractor.extract` | `_finite_descriptor(..., 'maximum')` | Verified equivalent |
| Minimum | `min(x)` | `describe_signal` / `FeatureExtractor.extract` | `_finite_descriptor(..., 'minimum')` | Verified equivalent |
| Mean | `sum(x) / N` | `np.mean` | `np.mean` over finite values | Verified equivalent |
| Median | `median(x)` | `np.median` | `np.median` over finite values | Verified equivalent |
| ROM | `max(x) - min(x)` | `describe_signal` | `_finite_descriptor(..., 'rom')` | Verified equivalent |
| Variance | population variance, `ddof=0` | `np.var(..., ddof=0)` | `np.var(..., ddof=0)` over finite values | Verified equivalent |
| STD | population standard deviation, `ddof=0` | `np.std(..., ddof=0)` | `np.std(..., ddof=0)` over finite values | Verified equivalent |
| Time-to-peak | `t[argmax(x)] - t[0]` | `src/features/temporal.py:time_to_peak` | `_time_to_peak` | Verified equivalent for available time vectors |

## Symmetry Formulas

Let `L` and `R` be left and right full-recording ROM values.

| Metric | Formula | Implementation | Formula equivalence |
|---|---|---|---|
| Absolute Difference | `abs(L - R)` | `src/features/symmetry.py:absolute_difference` | Verified equivalent |
| Percent Difference | `100 * abs(L - R) / ((abs(L) + abs(R)) / 2)` | `src/features/symmetry.py:percent_difference` | Verified equivalent |
| Symmetry Index | `100 * (L - R) / ((abs(L) + abs(R)) / 2)` | `src/features/symmetry.py:symmetry_index` | Verified equivalent |

## Every Exported Feature

| Feature | Formula | Units | Source signal | Equivalence of formula | Upstream measurement equivalence |
|---|---|---|---|---|---|
| `hip_flexion_right_mean` | `Σx / N` | degrees | dataset `hip_flexion_r` / JumpGuard `hip_flexion_right` | Verified equivalent | Unknown / not established |
| `hip_flexion_right_median` | `median(x)` | degrees | dataset `hip_flexion_r` / JumpGuard `hip_flexion_right` | Verified equivalent | Unknown / not established |
| `hip_flexion_right_std` | `sqrt(Σ(x-mean)² / N)` | degrees | dataset `hip_flexion_r` / JumpGuard `hip_flexion_right` | Verified equivalent | Unknown / not established |
| `hip_flexion_right_variance` | `Σ(x-mean)² / N` | degrees² | dataset `hip_flexion_r` / JumpGuard `hip_flexion_right` | Verified equivalent | Unknown / not established |
| `hip_flexion_right_maximum` | `max(x)` | degrees | dataset `hip_flexion_r` / JumpGuard `hip_flexion_right` | Verified equivalent | Unknown / not established |
| `hip_flexion_right_minimum` | `min(x)` | degrees | dataset `hip_flexion_r` / JumpGuard `hip_flexion_right` | Verified equivalent | Unknown / not established |
| `hip_flexion_right_rom` | `max(x) - min(x)` | degrees | dataset `hip_flexion_r` / JumpGuard `hip_flexion_right` | Verified equivalent | Unknown / not established |
| `hip_flexion_right_time_to_peak` | `time[argmax(x)] - time[0]` | seconds | dataset `hip_flexion_r` / JumpGuard `hip_flexion_right` | Verified equivalent | Unknown / not established |
| `hip_flexion_left_mean` | `Σx / N` | degrees | dataset `hip_flexion_l` / JumpGuard `hip_flexion_left` | Verified equivalent | Unknown / not established |
| `hip_flexion_left_median` | `median(x)` | degrees | dataset `hip_flexion_l` / JumpGuard `hip_flexion_left` | Verified equivalent | Unknown / not established |
| `hip_flexion_left_std` | `sqrt(Σ(x-mean)² / N)` | degrees | dataset `hip_flexion_l` / JumpGuard `hip_flexion_left` | Verified equivalent | Unknown / not established |
| `hip_flexion_left_variance` | `Σ(x-mean)² / N` | degrees² | dataset `hip_flexion_l` / JumpGuard `hip_flexion_left` | Verified equivalent | Unknown / not established |
| `hip_flexion_left_maximum` | `max(x)` | degrees | dataset `hip_flexion_l` / JumpGuard `hip_flexion_left` | Verified equivalent | Unknown / not established |
| `hip_flexion_left_minimum` | `min(x)` | degrees | dataset `hip_flexion_l` / JumpGuard `hip_flexion_left` | Verified equivalent | Unknown / not established |
| `hip_flexion_left_rom` | `max(x) - min(x)` | degrees | dataset `hip_flexion_l` / JumpGuard `hip_flexion_left` | Verified equivalent | Unknown / not established |
| `hip_flexion_left_time_to_peak` | `time[argmax(x)] - time[0]` | seconds | dataset `hip_flexion_l` / JumpGuard `hip_flexion_left` | Verified equivalent | Unknown / not established |
| `knee_flexion_right_mean` | `Σx / N` | degrees | dataset `knee_angle_r` / JumpGuard `knee_flexion_right` | Verified equivalent | Unknown / not established |
| `knee_flexion_right_median` | `median(x)` | degrees | dataset `knee_angle_r` / JumpGuard `knee_flexion_right` | Verified equivalent | Unknown / not established |
| `knee_flexion_right_std` | `sqrt(Σ(x-mean)² / N)` | degrees | dataset `knee_angle_r` / JumpGuard `knee_flexion_right` | Verified equivalent | Unknown / not established |
| `knee_flexion_right_variance` | `Σ(x-mean)² / N` | degrees² | dataset `knee_angle_r` / JumpGuard `knee_flexion_right` | Verified equivalent | Unknown / not established |
| `knee_flexion_right_maximum` | `max(x)` | degrees | dataset `knee_angle_r` / JumpGuard `knee_flexion_right` | Verified equivalent | Unknown / not established |
| `knee_flexion_right_minimum` | `min(x)` | degrees | dataset `knee_angle_r` / JumpGuard `knee_flexion_right` | Verified equivalent | Unknown / not established |
| `knee_flexion_right_rom` | `max(x) - min(x)` | degrees | dataset `knee_angle_r` / JumpGuard `knee_flexion_right` | Verified equivalent | Unknown / not established |
| `knee_flexion_right_time_to_peak` | `time[argmax(x)] - time[0]` | seconds | dataset `knee_angle_r` / JumpGuard `knee_flexion_right` | Verified equivalent | Unknown / not established |
| `knee_flexion_left_mean` | `Σx / N` | degrees | dataset `knee_angle_l` / JumpGuard `knee_flexion_left` | Verified equivalent | Unknown / not established |
| `knee_flexion_left_median` | `median(x)` | degrees | dataset `knee_angle_l` / JumpGuard `knee_flexion_left` | Verified equivalent | Unknown / not established |
| `knee_flexion_left_std` | `sqrt(Σ(x-mean)² / N)` | degrees | dataset `knee_angle_l` / JumpGuard `knee_flexion_left` | Verified equivalent | Unknown / not established |
| `knee_flexion_left_variance` | `Σ(x-mean)² / N` | degrees² | dataset `knee_angle_l` / JumpGuard `knee_flexion_left` | Verified equivalent | Unknown / not established |
| `knee_flexion_left_maximum` | `max(x)` | degrees | dataset `knee_angle_l` / JumpGuard `knee_flexion_left` | Verified equivalent | Unknown / not established |
| `knee_flexion_left_minimum` | `min(x)` | degrees | dataset `knee_angle_l` / JumpGuard `knee_flexion_left` | Verified equivalent | Unknown / not established |
| `knee_flexion_left_rom` | `max(x) - min(x)` | degrees | dataset `knee_angle_l` / JumpGuard `knee_flexion_left` | Verified equivalent | Unknown / not established |
| `knee_flexion_left_time_to_peak` | `time[argmax(x)] - time[0]` | seconds | dataset `knee_angle_l` / JumpGuard `knee_flexion_left` | Verified equivalent | Unknown / not established |
| `ankle_angle_right_mean` | `Σx / N` | degrees | dataset `ankle_angle_r` / JumpGuard `ankle_angle_right` | Verified equivalent | Unknown / not established |
| `ankle_angle_right_median` | `median(x)` | degrees | dataset `ankle_angle_r` / JumpGuard `ankle_angle_right` | Verified equivalent | Unknown / not established |
| `ankle_angle_right_std` | `sqrt(Σ(x-mean)² / N)` | degrees | dataset `ankle_angle_r` / JumpGuard `ankle_angle_right` | Verified equivalent | Unknown / not established |
| `ankle_angle_right_variance` | `Σ(x-mean)² / N` | degrees² | dataset `ankle_angle_r` / JumpGuard `ankle_angle_right` | Verified equivalent | Unknown / not established |
| `ankle_angle_right_maximum` | `max(x)` | degrees | dataset `ankle_angle_r` / JumpGuard `ankle_angle_right` | Verified equivalent | Unknown / not established |
| `ankle_angle_right_minimum` | `min(x)` | degrees | dataset `ankle_angle_r` / JumpGuard `ankle_angle_right` | Verified equivalent | Unknown / not established |
| `ankle_angle_right_rom` | `max(x) - min(x)` | degrees | dataset `ankle_angle_r` / JumpGuard `ankle_angle_right` | Verified equivalent | Unknown / not established |
| `ankle_angle_right_time_to_peak` | `time[argmax(x)] - time[0]` | seconds | dataset `ankle_angle_r` / JumpGuard `ankle_angle_right` | Verified equivalent | Unknown / not established |
| `ankle_angle_left_mean` | `Σx / N` | degrees | dataset `ankle_angle_l` / JumpGuard `ankle_angle_left` | Verified equivalent | Unknown / not established |
| `ankle_angle_left_median` | `median(x)` | degrees | dataset `ankle_angle_l` / JumpGuard `ankle_angle_left` | Verified equivalent | Unknown / not established |
| `ankle_angle_left_std` | `sqrt(Σ(x-mean)² / N)` | degrees | dataset `ankle_angle_l` / JumpGuard `ankle_angle_left` | Verified equivalent | Unknown / not established |
| `ankle_angle_left_variance` | `Σ(x-mean)² / N` | degrees² | dataset `ankle_angle_l` / JumpGuard `ankle_angle_left` | Verified equivalent | Unknown / not established |
| `ankle_angle_left_maximum` | `max(x)` | degrees | dataset `ankle_angle_l` / JumpGuard `ankle_angle_left` | Verified equivalent | Unknown / not established |
| `ankle_angle_left_minimum` | `min(x)` | degrees | dataset `ankle_angle_l` / JumpGuard `ankle_angle_left` | Verified equivalent | Unknown / not established |
| `ankle_angle_left_rom` | `max(x) - min(x)` | degrees | dataset `ankle_angle_l` / JumpGuard `ankle_angle_left` | Verified equivalent | Unknown / not established |
| `ankle_angle_left_time_to_peak` | `time[argmax(x)] - time[0]` | seconds | dataset `ankle_angle_l` / JumpGuard `ankle_angle_left` | Verified equivalent | Unknown / not established |
| `hip_flexion_rom_absolute_difference` | `\|ROM_L - ROM_R\|` | degrees | ROM pair `hip_flexion_l` and `hip_flexion_r` | Verified equivalent | Unknown / not established |
| `hip_flexion_rom_percent_difference` | `100 × \|ROM_L-ROM_R\| / ((\|ROM_L\|+\|ROM_R\|)/2)` | percent | ROM pair `hip_flexion_l` and `hip_flexion_r` | Verified equivalent | Unknown / not established |
| `hip_flexion_rom_symmetry_index` | `100 × (ROM_L-ROM_R) / ((\|ROM_L\|+\|ROM_R\|)/2)` | percent | ROM pair `hip_flexion_l` and `hip_flexion_r` | Verified equivalent | Unknown / not established |
| `knee_flexion_rom_absolute_difference` | `\|ROM_L - ROM_R\|` | degrees | ROM pair `knee_angle_l` and `knee_angle_r` | Verified equivalent | Unknown / not established |
| `knee_flexion_rom_percent_difference` | `100 × \|ROM_L-ROM_R\| / ((\|ROM_L\|+\|ROM_R\|)/2)` | percent | ROM pair `knee_angle_l` and `knee_angle_r` | Verified equivalent | Unknown / not established |
| `knee_flexion_rom_symmetry_index` | `100 × (ROM_L-ROM_R) / ((\|ROM_L\|+\|ROM_R\|)/2)` | percent | ROM pair `knee_angle_l` and `knee_angle_r` | Verified equivalent | Unknown / not established |
| `ankle_angle_rom_absolute_difference` | `\|ROM_L - ROM_R\|` | degrees | ROM pair `ankle_angle_l` and `ankle_angle_r` | Verified equivalent | Unknown / not established |
| `ankle_angle_rom_percent_difference` | `100 × \|ROM_L-ROM_R\| / ((\|ROM_L\|+\|ROM_R\|)/2)` | percent | ROM pair `ankle_angle_l` and `ankle_angle_r` | Verified equivalent | Unknown / not established |
| `ankle_angle_rom_symmetry_index` | `100 × (ROM_L-ROM_R) / ((\|ROM_L\|+\|ROM_R\|)/2)` | percent | ROM pair `ankle_angle_l` and `ankle_angle_r` | Verified equivalent | Unknown / not established |

## Formula Recovery Conclusion

The feature formulas themselves are recovered and verified equivalent across the current reference-feature and JumpGuard-feature code paths. This does not establish equivalence of the raw angle signals that feed those formulas.
