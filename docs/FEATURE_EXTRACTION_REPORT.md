# Feature Extraction Report

## Scope

Prompt 11 implements the Biomechanical Feature Extraction Layer in `src/feature_extraction.py`. It consumes Prompt 10 landmark outputs and converts landmark trajectories into the Prompt 3-compatible feature table schema. It does not modify Prompts 1-10, train models, predict ACL injury, estimate risk, generate medical interpretations, or alter downstream dashboard/reporting logic.

## Architecture

Current flow:

`Video -> Prompt 9 Video Processing -> Prompt 10 MediaPipe Pose Estimation -> Prompt 11 Landmark Feature Extraction -> Prompt 3 Feature Table Schema -> Existing Downstream Layers`

Prompt 11 consumes:

- Prompt 10 landmark CSV
- Prompt 10 landmark JSON
- frame numbers
- timestamps
- MediaPipe x/y/z coordinates
- confidence and visibility values indirectly through missing-coordinate preservation

It does not consume MATLAB files or the original motion-capture dataset.

## Joint-Angle Convention

The implemented joint angles are deterministic MediaPipe-derived geometric approximations. They are not equivalent to the laboratory inverse-kinematics joint angles in the original MATLAB dataset.

Angles are calculated in degrees from MediaPipe 3D landmark coordinates `(x, y, z)` when all required landmarks are present:

- Knee angle: internal angle at the knee from Hip -> Knee -> Ankle.
- Hip angle: angle between Shoulder -> Hip and Hip -> Knee vectors.
- Ankle angle: angle between Knee -> Ankle and Ankle -> Foot Index vectors.

If any required landmark coordinate is missing, the frame-level angle is preserved as `NaN`.

## Feature Schema

The exported feature table preserves the Prompt 3 table structure:

- 5 identifier columns: `participant_id`, `trial_slot`, `trial_name`, `condition`, `is_empty`
- 57 established Prompt 3 biomechanical feature columns

No Prompt 3 feature names were renamed, removed, or redefined. Unsupported or unavailable calculations are represented as missing values.

## Computed Quantities

For each bilateral hip, knee, and ankle geometric angle signal, the layer calculates:

- mean
- median
- population standard deviation
- population variance
- maximum
- minimum
- range of motion
- time to peak

For ROM symmetry, the layer reuses the Prompt 3 formulas:

- absolute difference
- percent difference
- symmetry index

Trajectory descriptors are exported separately in `trajectory_features.json` and are not added as extra columns to the Prompt 3-compatible table.

## Landing Events

No robust landing-event detector is defined from landmarks alone in the current project specifications. Prompt 11 therefore preserves beginning frame, end frame, and landing duration as missing values. A peak-flexion frame is reported only when knee-angle data are available.

## Generated Outputs

Required outputs:

- `reports/feature_extraction/feature_table.csv`
- `reports/feature_extraction/feature_table.json`
- `reports/feature_extraction/feature_statistics.json`
- `reports/feature_extraction/symmetry_summary.json`
- `reports/feature_extraction/landing_events.json`

Supporting outputs:

- `reports/feature_extraction/trajectory_features.json`
- `reports/feature_extraction/plots/feature_preview.png`
- `reports/feature_extraction/plots/joint_angles.png`
- `reports/feature_extraction/plots/rom.png`
- `reports/feature_extraction/plots/symmetry.png`

## Demo Extraction Result

Input: `reports/pose_estimation/sample_landmarks.csv`.

The Prompt 10 sample video is synthetic and contains no detected person, so MediaPipe landmark coordinates are missing. Prompt 11 preserved this missingness.

| Metric | Value |
| --- | ---: |
| Prompt 3 feature columns | 57 |
| Non-missing feature values | 0 |
| Missing feature values | 57 |

## Validation

Implemented validation checks include:

- required landmark columns exist
- frame order is preserved
- missing landmarks remain missing
- generated table matches Prompt 3 column names exactly
- deterministic CSV and JSON exports
- no extra feature columns are introduced into the Prompt 3-compatible table

## Limitations

- MediaPipe-derived geometric angles are approximate and camera/model dependent.
- They are not laboratory inverse-kinematics joint angles.
- Missing landmarks are not interpolated or estimated.
- Landing phase events are not inferred without a documented detector.
- No clinical interpretation or injury-risk output is produced.

## Prompt 12 Integration

Prompt 12 and downstream application layers can consume `feature_table.csv` using the same feature-column names as Prompt 3. Rows with missing landmark-derived quantities should be handled by the existing missing-data and preprocessing policies.
