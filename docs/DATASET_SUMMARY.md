# JumpGuard AI Core Dataset Summary

This document summarizes the clean object model produced by Prompt 02. The
source hierarchy and workbook evidence remain documented in
`docs/DATASET_REPORT.md`.

## Public Architecture

```text
DJ.mat + metadata workbooks
        |
        v
load_dataset.py       source loading and format detection
        |
        v
dataset_parser.py     only module that interprets raw MATLAB structs
        |
        v
Dataset
  └── Participant
        └── Trial     clean NumPy arrays and semantic labels
              |
              +── validation.py
              +── preprocessing.py
              └── visualization.py
```

The supported entry point is:

```python
from src import Dataset

dataset = Dataset.load("data/sample/DJ.mat")
participant = dataset.get_participant("sub01")
trial = participant.get_trial("DJ_t1")
right_knee = trial.get_joint_angle("knee_angle_r")
```

Future modules should not load or traverse MATLAB structs directly.

## Participants and Trials

| Measure | Verified value |
|---|---:|
| Metadata-backed participants | 43 |
| Participant IDs | 1-4 and 6-44 |
| Metadata-defined trial slots | 258 |
| Valid numeric trials | 249 |
| Documented empty trial slots | 9 |
| Trial slots per participant | 6 |

Subject 5 is not represented because it is absent from `labeling_DJ.xlsx`.
Subject 32 has three valid non-fatigued trials and three documented empty
fatigued trials. Subject 44 has six documented empty trials. Empty slots remain
addressable as `Trial` objects and are never silently discarded.

Trial order:

| Slot | Name | Condition |
|---:|---|---|
| 1 | `DJ_t1` | nonfatigued |
| 2 | `DJ_t2` | nonfatigued |
| 3 | `DJ_t3` | nonfatigued |
| 4 | `f_DJ_t1` | fatigued |
| 5 | `f_DJ_t2` | fatigued |
| 6 | `f_DJ_t3` | fatigued |

## Joint-Angle Labels

The framework loads 44 semantic labels from
`IK_column_labels.xlsx!CMJ_dom_t1_IK!A12:AR12`. It verifies that this row is
preceded by numeric indices 1 through 44. Column indices are not hardcoded in
the public API.

Every valid joint-angle matrix has shape `(frames, 44)` and dtype `float64`.
Access is by exact semantic name:

```python
trial.get_joint_angle("hip_flexion_r")
trial.get_joint_angle("knee_angle_l")
```

The first semantic column is `time`. Rotational values are in degrees according
to the workbook header.

## Dimensions and Frames

| Measure | Verified value |
|---|---:|
| Minimum frames per valid trial | 842 |
| Maximum frames per valid trial | 2280 |
| Mean frames per valid trial | 1401.12 |
| Median frames per valid trial | 1395 |
| Inferred sampling frequency | 250 Hz |

For every valid Trial:

- `joint_angles`: `(frames, 44)`
- `com_velocity`: `(frames, 3)`
- `com_position`: `(frames, 3)`
- `com_acceleration`: `(frames, 3)`
- 59 anatomical marker arrays: `(frames, 3)`
- marker `time`: `(frames, 1)`
- four event indices stored as one-based source-frame values

## Missing Values and Validation

Automatic validation covers:

- missing labels and duplicate labels
- empty trials
- NaN and infinite values
- nonnumeric or corrupted arrays
- joint-angle, COM, and marker dimensions
- marker count and event-index ranges
- source trial-name ordering
- metadata missing-flag consistency

Canonical validation result:

| Severity | Count | Meaning |
|---|---:|---|
| Errors | 0 | No corruption or inconsistent dimensions detected |
| Warnings | 9 | Metadata-documented empty trial slots |

Across the 249 valid trials, joint-angle, COM, and marker arrays contain no NaN
or infinite values.

## Preprocessing Boundary

`src/preprocessing.py` provides reusable interpolation, missing-value handling,
normalization, frame trimming, and zero-phase Butterworth low-pass filtering.
These helpers operate on numeric arrays and do not compute biomechanical
features.

## Verification

- Public API loads the real dataset successfully.
- `notebooks/02_loader_demo.ipynb` executes end to end.
- Unit tests cover loading, parsing, Dataset, Participant, Trial, validation,
  preprocessing, and visualization.
- Semantic joint-angle access is tested against the corresponding source matrix
  column.

## Technical Debt

- Metadata values are preserved as source-coded integers. A later metadata
  domain layer may add enums while retaining the original values.
- Sampling frequency remains inferred from the time column because no explicit
  MAT field provides it.
- Event indices remain one-based to preserve source meaning. Feature engineering
  should use a named conversion helper when zero-based slicing is required.
- The framework currently targets the documented Drop Jump dataset. Supporting
  another movement should add a parser strategy rather than weakening the
  validated DJ schema.
- Package metadata and a distributable build configuration are not yet present.

## Recommended Prompt 3 Starting Point

Begin feature engineering from `Trial` objects only. First define and test a
named event-index conversion/windowing utility, then create pure functions that
accept a Trial and return explicitly documented scalar or tabular features.
Preserve semantic label access and keep feature tables separate from the core
dataset objects.
