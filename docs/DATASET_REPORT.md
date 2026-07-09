# JumpGuard AI Dataset Report

Generated for Prompt 1 dataset exploration. This report is limited to dataset structure inspection. It does not perform feature engineering, pose estimation, risk scoring, or ML.

## Files Inspected

- `data/sample/DJ.mat`
- `data/metadata/IK_column_labels.xlsx`
- `data/metadata/labeling_DJ.xlsx`
- `data/metadata/participant_log.xlsx`

## MATLAB File Format

- `DJ.mat` is a classic MATLAB file, not HDF5-backed MATLAB v7.3.
- Header begins with `MATLAB 5.0 MAT-file`.
- Correct loader: `scipy.io.loadmat`.

## Top-Level MATLAB Structure

Top-level variables:

| Variable | Type | Shape | Dtype |
|---|---:|---:|---|
| `DJ` | `numpy.ndarray` | `(44, 1)` | `object` |

`DJ` is organized as 44 row entries. Entries 5 and 44 are empty at the top MATLAB level. The other 42 entries contain:

```text
DJ[entry].DJ_bil.sub_data
```

For all 42 populated entries, `sub_data` has shape `(6, 1)`.

## Complete Recursive Hierarchy

The file was traversed recursively through every object array and every MATLAB
struct field. The hierarchy terminates at the numeric/string arrays shown
below; no additional struct or object-array nesting exists beneath the marker
fields.

`scipy.io.loadmat(..., squeeze_me=False, struct_as_record=False)` preserves
MATLAB singleton wrappers. The complete physical representation is:

```text
loaded MAT dictionary
└── DJ: ndarray<object>, shape (44, 1)
    ├── DJ[4,0], DJ[43,0]: ndarray<float64>, shape (1, 0)
    │   └── empty; no deeper fields
    └── DJ[p,0]: ndarray<object>, shape (1, 1), for 42 populated entries
        └── [0,0]: mat_struct
            └── DJ_bil: ndarray<object>, shape (1, 1)
                └── [0,0]: mat_struct
                    └── sub_data: ndarray<object>, shape (6, 1)
                        └── sub_data[t,0]: mat_struct, six trial slots
                            ├── File
                            ├── IC_first_K
                            ├── IC_second_K
                            ├── IC_first_A
                            ├── IC_second_A
                            ├── COM_velocity
                            ├── COM_position
                            ├── COM_acceleration
                            ├── Joint_Angles
                            └── marker
                                ├── valid: ndarray<object>, shape (1, 1)
                                │   └── [0,0]: mat_struct with 60 fields
                                │       ├── time: float64 (frames, 1)
                                │       └── 59 named markers: float64 (frames, 3)
                                └── empty slot: float64 (1, 0)
```

Here, `p` is a zero-based SciPy participant-entry index from 0 through 43,
and `t` is a zero-based trial-slot index from 0 through 5. MATLAB entry
numbers and report subject numbers are `p + 1`; human-readable trial slots
are `t + 1`.

### Every Trial-Level Leaf

All 249 valid trial records have the same ten fields:

| Path below `sub_data[t,0]` | Type and shape | Observed count/details |
|---|---|---|
| `.File` | Unicode ndarray `(1,)` | 126 are `<U5`; 123 are `<U7>` |
| `.IC_first_K` | unsigned integer ndarray `(1,1)` | 226 `uint16`; 23 `uint8` |
| `.IC_second_K` | unsigned integer ndarray `(1,1)` | 246 `uint16`; 3 `uint8` |
| `.IC_first_A` | unsigned integer ndarray `(1,1)` | 226 `uint16`; 23 `uint8` |
| `.IC_second_A` | unsigned integer ndarray `(1,1)` | 246 `uint16`; 3 `uint8` |
| `.COM_velocity` | `float64 (frames,3)` | 249 |
| `.COM_position` | `float64 (frames,3)` | 249 |
| `.COM_acceleration` | `float64 (frames,3)` | 249 |
| `.Joint_Angles` | `float64 (frames,44)` | 249 |
| `.marker` | object ndarray `(1,1)` containing a struct | 249 |

In entry 32, slots 4-6 still contain trial `mat_struct` records with the same
ten field names, but every field value, including `File` and `marker`, is an
empty `float64 (1,0)` array. Thus the empty trial records have no marker
subfields. Entries 5 and 44 are empty one level higher and have neither
`DJ_bil` nor trial records.

The event dtype variation is storage variation, not a shape or field
variation. Values were range-checked independently of dtype.

### Every Marker-Level Leaf

Every valid marker struct has the same 60-field set. The `time` leaf is
`float64 (frames,1)`. Each of the other 59 leaves is a `float64 (frames,3)`
array:

```text
C7, CLAV, LANK, LANKM, LASI, LBHD, LCI, LELB, LFHD, LFIN, LFRM, LGT,
LHEE, LKNE, LKNEM, LPSI, LSHO, LTHI1, LTHI2, LTHI3, LTHI4, LTIB1,
LTIB2, LTIB3, LTIB4, LTOE, LUPA, LWRA, LWRB, RANK, RANKM, RASI,
RBAK, RBHD, RCI, RELB, RFHD, RFIN, RFRM, RGT, RHEE, RKNE, RKNEM,
RPSI, RSHO, RTHI1, RTHI2, RTHI3, RTHI4, RTIB1, RTIB2, RTIB3, RTIB4,
RTOE, RUPA, RWRA, RWRB, STRN, T10
```

There are no object wrappers below these 60 numeric leaves. All marker leaf
frame counts equal the containing trial's `Joint_Angles` frame count.

### Drop Jump Joint-Angle Paths

Conceptual MATLAB path for participant entry `P` and trial slot `T`:

```matlab
DJ{P}.DJ_bil.sub_data{T}.Joint_Angles
```

Exact SciPy path with the loader settings used in this project:

```python
trial = data["DJ"][P - 1, 0][0, 0].DJ_bil[0, 0].sub_data[T - 1, 0]
joint_angles = trial.Joint_Angles
```

The Drop Jump slot mapping is:

| `T` | `.File` | Joint-angle path suffix |
|---:|---|---|
| 1 | `DJ_t1` | `.sub_data[0,0].Joint_Angles` |
| 2 | `DJ_t2` | `.sub_data[1,0].Joint_Angles` |
| 3 | `DJ_t3` | `.sub_data[2,0].Joint_Angles` |
| 4 | `f_DJ_t1` | `.sub_data[3,0].Joint_Angles` |
| 5 | `f_DJ_t2` | `.sub_data[4,0].Joint_Angles` |
| 6 | `f_DJ_t3` | `.sub_data[5,0].Joint_Angles` |

The first three slots are non-fatigued Drop Jump trials and the last three
are fatigued Drop Jump trials, as supported jointly by the `.File` values
and `labeling_DJ.xlsx`. The three fatigued paths for entry 32 exist as empty
trial fields; no paths exist below entries 5 or 44 because those top-level
entries are empty.

## Per-Trial Record Fields

Across all 252 available trial slots, the MATLAB record field set is consistent:

```text
File
IC_first_K
IC_second_K
IC_first_A
IC_second_A
COM_velocity
COM_position
COM_acceleration
Joint_Angles
marker
```

## Participant Organization

Observed MATLAB organization:

- 44 MATLAB entries are present in `DJ`.
- 42 entries are populated.
- Entry 5 is empty.
- Entry 44 is empty.
- Entry 32 is populated but has only the first three valid trials; trial slots 4-6 are empty.

Metadata alignment:

- `labeling_DJ.xlsx` contains 43 subject numbers: `1-4` and `6-44`; subject 5 is absent.
- `labeling_DJ.xlsx` has 6 rows per listed subject, for 258 rows total.
- The missing-data flag has 249 rows marked `0` and 9 rows marked `1`.
- The 9 missing rows correspond to subject 32 post-fatigue trial rows and all six subject 44 rows.

This matches the MAT structure:

- Subject/entry 32 has three empty post-fatigue slots.
- Subject/entry 44 is completely empty.
- Subject/entry 5 is absent/empty and also absent from `labeling_DJ.xlsx`.

## Trial and Movement Organization

Each populated participant normally has six trial slots:

| Slot | File value | Interpretation from filename and metadata |
|---:|---|---|
| 1 | `DJ_t1` | non-fatigued DJ trial 1 |
| 2 | `DJ_t2` | non-fatigued DJ trial 2 |
| 3 | `DJ_t3` | non-fatigued DJ trial 3 |
| 4 | `f_DJ_t1` | fatigued DJ trial 1 |
| 5 | `f_DJ_t2` | fatigued DJ trial 2 |
| 6 | `f_DJ_t3` | fatigued DJ trial 3 |

Evidence:

- Valid file counts are `DJ_t1: 42`, `DJ_t2: 42`, `DJ_t3: 42`, `f_DJ_t1: 41`, `f_DJ_t2: 41`, `f_DJ_t3: 41`.
- Entry 32 has `DJ_t1`, `DJ_t2`, `DJ_t3`, then three empty trial slots.
- `labeling_DJ.xlsx` marks subject 32's fatigued rows as missing with note `no c3d file; excessive marker movement`.

## Valid Trial Counts

- Total MATLAB trial slots under populated entries: 252.
- Valid trials with `Joint_Angles` shape `(frames, 44)`: 249.
- Invalid/empty trial slots: 3.

Invalid slots:

| Entry | Slot | File | Joint_Angles shape | Notes |
|---:|---:|---|---|---|
| 32 | 4 | empty | `(1, 0)` | all fields empty |
| 32 | 5 | empty | `(1, 0)` | all fields empty |
| 32 | 6 | empty | `(1, 0)` | all fields empty |

## IK Column Label Workbook

Workbook sheets:

```text
CMJ_dom_t1_IK
```

Sheet dimensions:

| Sheet | Dimensions | Range |
|---|---:|---|
| `CMJ_dom_t1_IK` | 12 rows x 44 columns | `A1:AR12` |

First 20 rows as inspected programmatically. The sheet only contains 12 rows:

```text
R01: Coordinates |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
R02: version=1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
R03: nRows=1425 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
R04: nColumns=44 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
R05: inDegrees=yes |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
R06:  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
R07: Units are S.I. units (second, meters, Newtons, ...) |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
R08: If the header above contains a line with 'inDegrees', this indicates whether rotational values are in degrees (yes) or radians (no). |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
R09:  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
R10: endheader |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
R11: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 29 | 30 | 31 | 32 | 33 | 34 | 35 | 36 | 37 | 38 | 39 | 40 | 41 | 42 | 43 | 44
R12: time | pelvis_list | pelvis_tilt | pelvis_rotation | pelvis_tx | pelvis_ty | pelvis_tz | hip_flexion_r | hip_adduction_r | hip_rotation_r | knee_angle_r | knee_adduction_r | knee_rotation_r | knee_angle_r_beta | ankle_angle_r | subtalar_angle_r | mtp_angle_r | hip_flexion_l | hip_adduction_l | hip_rotation_l | knee_angle_l | knee_adduction_l | knee_rotation_l | knee_angle_l_beta | ankle_angle_l | subtalar_angle_l | mtp_angle_l | lumbar_extension | lumbar_bending | lumbar_rotation | arm_flex_r | arm_add_r | arm_rot_r | elbow_flex_r | pro_sup_r | wrist_flex_r | wrist_dev_r | arm_flex_l | arm_add_l | arm_rot_l | elbow_flex_l | pro_sup_l | wrist_flex_l | wrist_dev_l
```

### Authoritative IK Label Range

The authoritative IK label range is:

```text
CMJ_dom_t1_IK!A12:AR12
```

Evidence:

- Row 4 declares `nColumns=44`.
- Row 10 declares `endheader`.
- Row 11 contains exactly 44 numeric column indices: `1` through `44`.
- Row 12 contains exactly 44 text labels.
- Every valid `Joint_Angles` array in `DJ.mat` has 44 columns.
- The 44 labels in row 12 align one-to-one with the 44 `Joint_Angles` columns.

Potential candidate range considered but rejected:

- `A11:AR11` also has 44 values, but they are numeric indices, not biomechanical labels.
- Metadata/header cells in rows 1-10 include strings, but they do not form a 44-column label vector and include file metadata such as `version=1`, `nRows=1425`, and `inDegrees=yes`.

## Joint_Angles Mapping

All 249 valid trials have:

```text
Joint_Angles.shape == (frames, 44)
```

Column mapping:

| Column | Label |
|---:|---|
| 1 | `time` |
| 2 | `pelvis_list` |
| 3 | `pelvis_tilt` |
| 4 | `pelvis_rotation` |
| 5 | `pelvis_tx` |
| 6 | `pelvis_ty` |
| 7 | `pelvis_tz` |
| 8 | `hip_flexion_r` |
| 9 | `hip_adduction_r` |
| 10 | `hip_rotation_r` |
| 11 | `knee_angle_r` |
| 12 | `knee_adduction_r` |
| 13 | `knee_rotation_r` |
| 14 | `knee_angle_r_beta` |
| 15 | `ankle_angle_r` |
| 16 | `subtalar_angle_r` |
| 17 | `mtp_angle_r` |
| 18 | `hip_flexion_l` |
| 19 | `hip_adduction_l` |
| 20 | `hip_rotation_l` |
| 21 | `knee_angle_l` |
| 22 | `knee_adduction_l` |
| 23 | `knee_rotation_l` |
| 24 | `knee_angle_l_beta` |
| 25 | `ankle_angle_l` |
| 26 | `subtalar_angle_l` |
| 27 | `mtp_angle_l` |
| 28 | `lumbar_extension` |
| 29 | `lumbar_bending` |
| 30 | `lumbar_rotation` |
| 31 | `arm_flex_r` |
| 32 | `arm_add_r` |
| 33 | `arm_rot_r` |
| 34 | `elbow_flex_r` |
| 35 | `pro_sup_r` |
| 36 | `wrist_flex_r` |
| 37 | `wrist_dev_r` |
| 38 | `arm_flex_l` |
| 39 | `arm_add_l` |
| 40 | `arm_rot_l` |
| 41 | `elbow_flex_l` |
| 42 | `pro_sup_l` |
| 43 | `wrist_flex_l` |
| 44 | `wrist_dev_l` |

Workbook metadata states `inDegrees=yes`, so rotational values are reported in degrees. Row 7 states SI units generally, so translations and COM values should be treated as SI-unit quantities; this report does not infer additional biomechanical semantics beyond that.

## Frame Counts and Sampling

Valid trial frame statistics:

| Statistic | Frames |
|---|---:|
| Minimum | 842 |
| Maximum | 2280 |
| Mean | 1401.12 |
| Median | 1395 |

Frame counts by file:

| File | Valid trials | Min frames | Max frames | Mean frames |
|---|---:|---:|---:|---:|
| `DJ_t1` | 42 | 856 | 2040 | 1365.64 |
| `DJ_t2` | 42 | 906 | 2280 | 1431.69 |
| `DJ_t3` | 42 | 975 | 2235 | 1462.38 |
| `f_DJ_t1` | 41 | 842 | 2185 | 1348.34 |
| `f_DJ_t2` | 41 | 983 | 2022 | 1396.41 |
| `f_DJ_t3` | 41 | 1011 | 1795 | 1400.88 |

Sampling frequency:

- The first `Joint_Angles` column is `time`.
- For all valid trials, the median time step is `0.004` seconds.
- Therefore, the inferred sampling frequency from the time column is `250 Hz`.
- This is inferred from the data; no separate explicit sampling-frequency metadata field was found in `DJ.mat`.

Valid trial time ranges:

- Time starts at `0.0` for valid trials.
- Time end range: `3.364` to `9.116` seconds.

## COM Arrays

For all 249 valid trials:

- `COM_velocity.shape == (frames, 3)`
- `COM_position.shape == (frames, 3)`
- `COM_acceleration.shape == (frames, 3)`
- No COM shape mismatches were found.

## Marker Organization

For all 249 valid trials:

- `marker` is a MATLAB struct.
- The marker set contains 60 fields.
- The marker field set is consistent across valid trials.
- Marker field order is not fully consistent: 7 order variants were observed.

Because field order varies, marker access should use field names, not positional order.

Marker fields:

```text
C7, CLAV, LANK, LANKM, LASI, LBHD, LCI, LELB, LFHD, LFIN, LFRM, LGT,
LHEE, LKNE, LKNEM, LPSI, LSHO, LTHI1, LTHI2, LTHI3, LTHI4, LTIB1,
LTIB2, LTIB3, LTIB4, LTOE, LUPA, LWRA, LWRB, RANK, RANKM, RASI,
RBAK, RBHD, RCI, RELB, RFHD, RFIN, RFRM, RGT, RHEE, RKNE, RKNEM,
RPSI, RSHO, RTHI1, RTHI2, RTHI3, RTHI4, RTIB1, RTIB2, RTIB3, RTIB4,
RTOE, RUPA, RWRA, RWRB, STRN, T10, time
```

## Event Index Fields

Each valid trial has four event index fields:

- `IC_first_K`
- `IC_second_K`
- `IC_first_A`
- `IC_second_A`

Findings:

- No valid trial has event indices outside its frame range.
- No valid trial has first-contact index greater than second-contact index for the K or A fields.
- Event indices are stored as MATLAB numeric scalars. They appear to be one-based frame indices because they are MATLAB-origin indices. Downstream Python code should convert carefully and document whether zero-based conversion has occurred.

## Missing Values

Across the 249 valid trials:

| Data block | NaN count | Inf count |
|---|---:|---:|
| `Joint_Angles` | 0 | 0 |
| COM arrays | 0 | 0 |
| marker arrays | 0 | 0 |

Structural missingness:

- Entry 5 is empty.
- Entry 44 is empty.
- Entry 32 slots 4-6 are empty `(1, 0)` arrays across all per-trial fields.

`labeling_DJ.xlsx` missing-data evidence:

| Subject | Rows flagged missing | Notes |
|---:|---:|---|
| 32 | 3 | `no c3d file; excessive marker movement` |
| 44 | 6 | `no c3d file; pain reported` |

## Inconsistencies and Cautions

1. `DJ` has 44 entries, but only 42 are populated.
2. `labeling_DJ.xlsx` omits subject 5 entirely but includes subject 44 with all rows flagged missing.
3. Subject/entry 32 is partially populated: non-fatigued trials are present, fatigued trials are empty.
4. Marker field order varies across valid trials, although the marker field set is consistent.
5. `IK_column_labels.xlsx` row 3 says `nRows=1425`, but valid trial frame counts vary from 842 to 2280. Treat that workbook value as label-file/header metadata, not as a universal frame count.
6. The mapping between MATLAB entry number and `labeling_DJ.xlsx` subject number is strongly supported by the missingness pattern, but downstream code should still preserve explicit entry/subject identifiers rather than relying on implicit row order alone.

## Recommended Loader Rules for Next Milestone

- Load `DJ.mat` with `scipy.io.loadmat` unless version detection shows HDF5/v7.3.
- Treat `DJ` as a `(44, 1)` MATLAB cell-like object array.
- Skip or explicitly flag empty top-level entries.
- For populated entries, iterate `DJ_bil.sub_data[:, 0]`.
- Treat a valid trial as one with `Joint_Angles.shape[1] == 44`.
- Use `IK_column_labels.xlsx!A12:AR12` for `Joint_Angles` column names.
- Use names, not positions, for marker fields.
- Preserve missing trial slots rather than silently dropping them.
- Convert MATLAB one-based event indices to Python zero-based indices only in a named, tested function.
