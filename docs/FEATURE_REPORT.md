# JumpGuard AI Feature Report

This report documents Prompt 03 biomechanical feature engineering. Features
are deterministic, directly measurable quantities derived only from semantic
joint-angle signals exposed by the Prompt 2 `Trial` abstraction.

## Scope and Decisions

- All features are computed over the **full recording**.
- No undocumented event marker is used for segmentation.
- `IC_first_K`, `IC_second_K`, `IC_first_A`, and `IC_second_A` were inspected
  in the MATLAB hierarchy, repository documentation, all metadata workbooks,
  and available labels. No authoritative source defines `K` or `A`.
- Event-dependent features, landing duration, and landing-phase features are
  therefore omitted.
- No ACL risk metric, clinical score, threshold, or injury-risk estimate is
  computed.
- Features use bilateral hip flexion, knee flexion, and ankle-angle signals.
  These are present by semantic name in every valid trial.

## Output

- Rows: `258` metadata-defined trial slots
- Valid numeric rows: `249`
- Documented empty rows: `9`
- Identifier columns: `5`
- Biomechanical feature columns: `57`
- Total CSV columns: `62`
- File: `data/processed/features.csv`

Empty trials are retained as rows. Their identifier fields are populated and
all 57 biomechanical feature values are `NaN`.

## Feature Families

For each of six bilateral signals, the extractor computes mean, median,
population standard deviation, population variance, maximum, minimum, range
of motion, and time to the first maximum. For each of three left/right joint
pairs, symmetry is computed from full-recording ROM.

Symmetry formulas use left (`L`) and right (`R`) ROM:

- Absolute difference: `|L - R|`
- Percent difference: `100 * |L - R| / ((|L| + |R|) / 2)`
- Symmetry index: `100 * (L - R) / ((|L| + |R|) / 2)`

A positive symmetry index means left ROM is larger. A negative value means
right ROM is larger. If both values are zero, normalized symmetry outputs are
`NaN` because the denominator is zero.

## Complete Feature Dictionary

| Feature | Description | Formula | Units | Biomechanical relevance | Missing-value behavior |
|---|---|---|---|---|---|
| `hip_flexion_right_mean` | Right hip arithmetic mean over all frames. | `Σx / N` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `hip_flexion_right_median` | Right hip median over all frames. | `median(x)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `hip_flexion_right_std` | Right hip population standard deviation. | `sqrt(Σ(x-mean)² / N)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `hip_flexion_right_variance` | Right hip population variance. | `Σ(x-mean)² / N` | degrees² | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `hip_flexion_right_maximum` | Right hip maximum recorded angle. | `max(x)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `hip_flexion_right_minimum` | Right hip minimum recorded angle. | `min(x)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `hip_flexion_right_rom` | Right hip range of motion over the recording. | `max(x) - min(x)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `hip_flexion_right_time_to_peak` | Elapsed time to the first maximum of the right hip signal. | `time[argmax(x)] - time[0]` | seconds | Describes timing of the directly measured maximum over the recording. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `hip_flexion_left_mean` | Left hip arithmetic mean over all frames. | `Σx / N` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `hip_flexion_left_median` | Left hip median over all frames. | `median(x)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `hip_flexion_left_std` | Left hip population standard deviation. | `sqrt(Σ(x-mean)² / N)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `hip_flexion_left_variance` | Left hip population variance. | `Σ(x-mean)² / N` | degrees² | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `hip_flexion_left_maximum` | Left hip maximum recorded angle. | `max(x)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `hip_flexion_left_minimum` | Left hip minimum recorded angle. | `min(x)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `hip_flexion_left_rom` | Left hip range of motion over the recording. | `max(x) - min(x)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `hip_flexion_left_time_to_peak` | Elapsed time to the first maximum of the left hip signal. | `time[argmax(x)] - time[0]` | seconds | Describes timing of the directly measured maximum over the recording. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `knee_flexion_right_mean` | Right knee arithmetic mean over all frames. | `Σx / N` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `knee_flexion_right_median` | Right knee median over all frames. | `median(x)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `knee_flexion_right_std` | Right knee population standard deviation. | `sqrt(Σ(x-mean)² / N)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `knee_flexion_right_variance` | Right knee population variance. | `Σ(x-mean)² / N` | degrees² | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `knee_flexion_right_maximum` | Right knee maximum recorded angle. | `max(x)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `knee_flexion_right_minimum` | Right knee minimum recorded angle. | `min(x)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `knee_flexion_right_rom` | Right knee range of motion over the recording. | `max(x) - min(x)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `knee_flexion_right_time_to_peak` | Elapsed time to the first maximum of the right knee signal. | `time[argmax(x)] - time[0]` | seconds | Describes timing of the directly measured maximum over the recording. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `knee_flexion_left_mean` | Left knee arithmetic mean over all frames. | `Σx / N` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `knee_flexion_left_median` | Left knee median over all frames. | `median(x)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `knee_flexion_left_std` | Left knee population standard deviation. | `sqrt(Σ(x-mean)² / N)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `knee_flexion_left_variance` | Left knee population variance. | `Σ(x-mean)² / N` | degrees² | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `knee_flexion_left_maximum` | Left knee maximum recorded angle. | `max(x)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `knee_flexion_left_minimum` | Left knee minimum recorded angle. | `min(x)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `knee_flexion_left_rom` | Left knee range of motion over the recording. | `max(x) - min(x)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `knee_flexion_left_time_to_peak` | Elapsed time to the first maximum of the left knee signal. | `time[argmax(x)] - time[0]` | seconds | Describes timing of the directly measured maximum over the recording. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `ankle_angle_right_mean` | Right ankle arithmetic mean over all frames. | `Σx / N` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `ankle_angle_right_median` | Right ankle median over all frames. | `median(x)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `ankle_angle_right_std` | Right ankle population standard deviation. | `sqrt(Σ(x-mean)² / N)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `ankle_angle_right_variance` | Right ankle population variance. | `Σ(x-mean)² / N` | degrees² | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `ankle_angle_right_maximum` | Right ankle maximum recorded angle. | `max(x)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `ankle_angle_right_minimum` | Right ankle minimum recorded angle. | `min(x)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `ankle_angle_right_rom` | Right ankle range of motion over the recording. | `max(x) - min(x)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `ankle_angle_right_time_to_peak` | Elapsed time to the first maximum of the right ankle signal. | `time[argmax(x)] - time[0]` | seconds | Describes timing of the directly measured maximum over the recording. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `ankle_angle_left_mean` | Left ankle arithmetic mean over all frames. | `Σx / N` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `ankle_angle_left_median` | Left ankle median over all frames. | `median(x)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `ankle_angle_left_std` | Left ankle population standard deviation. | `sqrt(Σ(x-mean)² / N)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `ankle_angle_left_variance` | Left ankle population variance. | `Σ(x-mean)² / N` | degrees² | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `ankle_angle_left_maximum` | Left ankle maximum recorded angle. | `max(x)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `ankle_angle_left_minimum` | Left ankle minimum recorded angle. | `min(x)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `ankle_angle_left_rom` | Left ankle range of motion over the recording. | `max(x) - min(x)` | degrees | Describes directly measured joint-angle magnitude or variability. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `ankle_angle_left_time_to_peak` | Elapsed time to the first maximum of the left ankle signal. | `time[argmax(x)] - time[0]` | seconds | Describes timing of the directly measured maximum over the recording. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `hip_flexion_rom_absolute_difference` | Unsigned left/right difference in hip ROM. | `\|ROM_L - ROM_R\|` | degrees | Quantifies bilateral ROM disparity without assigning risk. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `hip_flexion_rom_percent_difference` | Absolute bilateral percent difference in hip ROM. | `100 × \|ROM_L-ROM_R\| / ((\|ROM_L\|+\|ROM_R\|)/2)` | percent | Normalizes bilateral ROM disparity to side magnitude. | NaN for an empty trial or an unavailable/nonfinite source signal. Also NaN when both ROM values are zero. |
| `hip_flexion_rom_symmetry_index` | Signed bilateral symmetry index for hip ROM. | `100 × (ROM_L-ROM_R) / ((\|ROM_L\|+\|ROM_R\|)/2)` | percent | Positive values indicate larger left-side ROM; no risk threshold is applied. | NaN for an empty trial or an unavailable/nonfinite source signal. Also NaN when both ROM values are zero. |
| `knee_flexion_rom_absolute_difference` | Unsigned left/right difference in knee ROM. | `\|ROM_L - ROM_R\|` | degrees | Quantifies bilateral ROM disparity without assigning risk. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `knee_flexion_rom_percent_difference` | Absolute bilateral percent difference in knee ROM. | `100 × \|ROM_L-ROM_R\| / ((\|ROM_L\|+\|ROM_R\|)/2)` | percent | Normalizes bilateral ROM disparity to side magnitude. | NaN for an empty trial or an unavailable/nonfinite source signal. Also NaN when both ROM values are zero. |
| `knee_flexion_rom_symmetry_index` | Signed bilateral symmetry index for knee ROM. | `100 × (ROM_L-ROM_R) / ((\|ROM_L\|+\|ROM_R\|)/2)` | percent | Positive values indicate larger left-side ROM; no risk threshold is applied. | NaN for an empty trial or an unavailable/nonfinite source signal. Also NaN when both ROM values are zero. |
| `ankle_angle_rom_absolute_difference` | Unsigned left/right difference in ankle ROM. | `\|ROM_L - ROM_R\|` | degrees | Quantifies bilateral ROM disparity without assigning risk. | NaN for an empty trial or an unavailable/nonfinite source signal. |
| `ankle_angle_rom_percent_difference` | Absolute bilateral percent difference in ankle ROM. | `100 × \|ROM_L-ROM_R\| / ((\|ROM_L\|+\|ROM_R\|)/2)` | percent | Normalizes bilateral ROM disparity to side magnitude. | NaN for an empty trial or an unavailable/nonfinite source signal. Also NaN when both ROM values are zero. |
| `ankle_angle_rom_symmetry_index` | Signed bilateral symmetry index for ankle ROM. | `100 × (ROM_L-ROM_R) / ((\|ROM_L\|+\|ROM_R\|)/2)` | percent | Positive values indicate larger left-side ROM; no risk threshold is applied. | NaN for an empty trial or an unavailable/nonfinite source signal. Also NaN when both ROM values are zero. |

## Missing-Value Behavior

The default extractor policy is `nan`. Empty trials receive a complete NaN
feature vector. If a required signal is missing or nonfinite, only features
depending on that signal become NaN. `FeatureExtractor(missing_policy='raise')`
is available for workflows that must stop immediately.

The canonical dataset has no NaN or infinite values in valid joint-angle
arrays, so all 249 valid rows contain finite values for all 57 features.

## Validation and Reproducibility

- Feature names are unique and ordered deterministically.
- Participant/slot rows are unique.
- Repeated extraction produces equal DataFrames.
- Statistics use NumPy population definitions (`ddof=0`).
- Time-to-peak uses the first occurrence of the maximum and the recorded time
  column, relative to recording start.
- CSV floating-point output uses a fixed `%.10g` format.
- The complete project test suite verifies formulas, dimensions, missingness,
  semantic mapping, plotting, and export.

## Limitations

- Full-recording features include all movement phases present in each file and
  must not be described as landing-phase measurements.
- K/A event semantics remain unknown; event-dependent temporal measurements are
  intentionally absent.
- Joint-angle signs and coordinate conventions are preserved from the source.
  No clinical interpretation of positive or negative angle direction is added.
- Symmetry values quantify measured bilateral differences only; no risk
  threshold or normative judgment is applied.
- Empty trials cannot produce numeric biomechanical features.
