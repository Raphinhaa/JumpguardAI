# Dataset Reverse Engineering

Prompt 15 is a documentation-only reverse-engineering audit. It reuses Prompt 1 and Prompt 14 findings and does not change `DJ.mat`, `data/processed/features.csv`, feature extraction, evidence outputs, athlete reports, or dashboards.

## Evidence Sources Inspected

- `docs/DATASET_REPORT.md`: recursive MATLAB hierarchy, workbook inspection, label mapping, sampling, missingness, event-field inventory.
- `docs/DATASET_SUMMARY.md`: Dataset/Participant/Trial abstraction, dimensions, validation boundary.
- `docs/FEATURE_REPORT.md`: Prompt 3 dataset feature formulas and explicit event-use decision.
- `docs/ANGLE_DEFINITION_AUDIT.md` and `docs/FEATURE_DEFINITION_AUDIT.md`: Prompt 14 uploaded-video measurement provenance.
- `src/dataset_parser.py`, `src/trial.py`, `src/feature_engineering.py`, `src/features/statistical.py`, `src/features/symmetry.py`.
- `data/metadata/IK_column_labels.xlsx`, `data/metadata/labeling_DJ.xlsx`, `data/metadata/participant_log.xlsx`.

## Raw Dataset Structure

| Item | Finding | Evidence |
|---|---|---|
| MAT format | Classic MATLAB 5.0 MAT-file loaded with `scipy.io.loadmat`. | `docs/DATASET_REPORT.md`; `src/load_dataset.py` |
| Top-level variable | `DJ`, object array shape `(44, 1)`. | `docs/DATASET_REPORT.md` |
| Populated participants | 42 populated MAT entries; metadata-backed participants are 1-4 and 6-44. | `docs/DATASET_REPORT.md`; `docs/DATASET_SUMMARY.md` |
| Trial slots | Six slots per metadata-backed participant: `DJ_t1`, `DJ_t2`, `DJ_t3`, `f_DJ_t1`, `f_DJ_t2`, `f_DJ_t3`. | `docs/DATASET_REPORT.md`; `src/dataset_parser.py:TRIAL_NAMES` |
| Valid trials | 249 valid numeric trials; 9 documented empty rows. | `docs/DATASET_REPORT.md`; `docs/DATASET_SUMMARY.md` |
| Joint-angle array | `Joint_Angles` shape `(frames, 44)` for each valid trial. | `docs/DATASET_REPORT.md`; `src/dataset_parser.py` |
| Marker arrays | 59 marker coordinate arrays `(frames, 3)` plus marker `time` `(frames, 1)`. | `docs/DATASET_REPORT.md` |
| COM arrays | `COM_velocity`, `COM_position`, `COM_acceleration` each `(frames, 3)`. | `docs/DATASET_REPORT.md` |

## Reference Joint-Angle Labels

The authoritative label row is `IK_column_labels.xlsx!CMJ_dom_t1_IK!A12:AR12`. Row 4 declares `nColumns=44`, row 10 declares `endheader`, row 11 contains numeric indices 1-44, and row 12 contains the 44 labels used by `Joint_Angles`. Rotational values are in degrees because the workbook header contains `inDegrees=yes`.

## Reverse-Engineered Measurement Properties

| Property | Dataset finding | Evidence level |
|---|---|---|
| Mathematical definition of raw IK columns | The values are precomputed inverse-kinematics columns named by the workbook, including `hip_flexion_r`, `knee_angle_r`, and `ankle_angle_r`. The underlying model equations are not present. | Partially known; label-level evidence only. |
| Units | Time in seconds; rotational values in degrees; general SI units for non-rotational quantities. | Direct evidence from workbook header. |
| Angle convention | Labels identify flexion/angle/adduction/rotation names. Sign convention, axis order, segment coordinate definitions, internal vs external angle convention, and positive direction are not defined in available files. | Unknown from available evidence. |
| Coordinate system | Marker arrays have `(frames, 3)` coordinates and COM arrays have `(frames, 3)`, but the global coordinate axes, calibration frame, and IK anatomical coordinate system are not defined in available files. | Unknown from available evidence. |
| 2D or 3D | Dataset contains 3D markers and precomputed IK joint angles. Whether each IK angle was produced by a 3D musculoskeletal model is plausible from the data structure but not explicitly documented here. | Unknown from available evidence. |
| Preprocessing | No authoritative smoothing, filtering, interpolation, gap-fill, marker-set preprocessing, or IK solver settings were found in the available files. | Unknown from available evidence. |
| Sampling | Median time step is `0.004` seconds, implying 250 Hz from the time column. No explicit sampling-frequency field was found. | Inferred from data, documented in `docs/DATASET_REPORT.md`. |
| Event fields | Four scalar fields exist: `IC_first_K`, `IC_second_K`, `IC_first_A`, `IC_second_A`. Values are in range and ordered first <= second. Meaning of `K` and `A` is not defined. | Field existence known; semantics unknown. |
| Feature aggregation | Current project reference features use the full recording for all descriptors and symmetry metrics. Event fields are intentionally not used. | Direct code evidence from `src/feature_engineering.py`; documented in `docs/FEATURE_REPORT.md`. |
| Single-frame vs multi-frame | Maximum, minimum, and time-to-peak depend on extrema frames; mean, median, std, variance, ROM, and symmetry depend on multiple frames. | Direct code evidence. |

## Feature Families Used As Reference Features

| Dataset labels | Project feature prefix | Feature formulas | Evidence |
|---|---|---|---|
| `hip_flexion_r` | `hip_flexion_right` | mean, median, std, variance, maximum, minimum, rom plus `time_to_peak` | `src/features/biomechanics.py`; `src/feature_engineering.py` |
| `hip_flexion_l` | `hip_flexion_left` | mean, median, std, variance, maximum, minimum, rom plus `time_to_peak` | `src/features/biomechanics.py`; `src/feature_engineering.py` |
| `knee_angle_r` | `knee_flexion_right` | mean, median, std, variance, maximum, minimum, rom plus `time_to_peak` | `src/features/biomechanics.py`; `src/feature_engineering.py` |
| `knee_angle_l` | `knee_flexion_left` | mean, median, std, variance, maximum, minimum, rom plus `time_to_peak` | `src/features/biomechanics.py`; `src/feature_engineering.py` |
| `ankle_angle_r` | `ankle_angle_right` | mean, median, std, variance, maximum, minimum, rom plus `time_to_peak` | `src/features/biomechanics.py`; `src/feature_engineering.py` |
| `ankle_angle_l` | `ankle_angle_left` | mean, median, std, variance, maximum, minimum, rom plus `time_to_peak` | `src/features/biomechanics.py`; `src/feature_engineering.py` |
| `hip_flexion_l` and `hip_flexion_r` ROM | `hip_flexion_rom_*` | absolute difference, percent difference, symmetry index | `src/features/symmetry.py`; `src/feature_engineering.py` |
| `knee_angle_l` and `knee_angle_r` ROM | `knee_flexion_rom_*` | absolute difference, percent difference, symmetry index | `src/features/symmetry.py`; `src/feature_engineering.py` |
| `ankle_angle_l` and `ankle_angle_r` ROM | `ankle_angle_rom_*` | absolute difference, percent difference, symmetry index | `src/features/symmetry.py`; `src/feature_engineering.py` |

## Unknowns That Must Not Be Inferred

- Raw dataset IK model, segment definitions, and anatomical coordinate systems.
- Whether dataset flexion columns are internal angles, external angles, signed flexion/extension angles, or model-coordinate generalized coordinates.
- Whether preprocessing included filtering, smoothing, interpolation, marker gap filling, or normalization before `Joint_Angles` were saved.
- Authoritative meanings of `K` and `A` event suffixes.
- Whether the stored event fields correspond to initial contact, takeoff, peak landing, or another operational definition.
