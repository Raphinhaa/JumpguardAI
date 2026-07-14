# Angle Definition Audit

This audit documents the existing uploaded-video angle implementation. These angles are MediaPipe-derived geometric approximations from normalized 3D landmark coordinates `(x, y, z)`. They are not laboratory inverse-kinematics joint angles.

## Shared Calculation

- Source code: `src/feature_extraction.py`, `ANGLE_SIGNAL_MAP`, `_angle_for_points`, `_angle_between`.
- Coordinate system: MediaPipe normalized image/world-like landmark coordinates exported by Prompt 10: `x`, `y`, `z`; overlay drawing uses `x` and `y` scaled to video pixels only for visualization.
- Units: degrees.
- Formula: `degrees(arccos(clip(dot(a,b) / (||a|| ||b||), -1, 1)))`.
- Valid numeric range from arccos: 0 to 180 degrees.
- Missing behavior: if any required landmark is missing, nonfinite, or a vector has zero norm, the angle is `NaN`.
- Landing phase: no landing phase is detected; angles are computed for every processed frame.

## Joint Definitions

| Signal | Side | Joint | Landmarks | Vectors Used | Convention | Transformations | Source |
|---|---|---|---|---|---|---|---|
| `hip_flexion_right` | right | hip | `right_shoulder` -> `right_hip` -> `right_knee` | `right_hip - right_shoulder; right_knee - right_hip` | Internal geometric angle between the two vectors listed | None; no `180 - angle` transform is applied | `src/feature_extraction.py:ANGLE_SIGNAL_MAP,_angle_for_points,_angle_between` |
| `hip_flexion_left` | left | hip | `left_shoulder` -> `left_hip` -> `left_knee` | `left_hip - left_shoulder; left_knee - left_hip` | Internal geometric angle between the two vectors listed | None; no `180 - angle` transform is applied | `src/feature_extraction.py:ANGLE_SIGNAL_MAP,_angle_for_points,_angle_between` |
| `knee_flexion_right` | right | knee | `right_hip` -> `right_knee` -> `right_ankle` | `right_hip - right_knee; right_ankle - right_knee` | Internal geometric angle between the two vectors listed | None; no `180 - angle` transform is applied | `src/feature_extraction.py:ANGLE_SIGNAL_MAP,_angle_for_points,_angle_between` |
| `knee_flexion_left` | left | knee | `left_hip` -> `left_knee` -> `left_ankle` | `left_hip - left_knee; left_ankle - left_knee` | Internal geometric angle between the two vectors listed | None; no `180 - angle` transform is applied | `src/feature_extraction.py:ANGLE_SIGNAL_MAP,_angle_for_points,_angle_between` |
| `ankle_angle_right` | right | ankle | `right_knee` -> `right_ankle` -> `right_foot_index` | `right_ankle - right_knee; right_foot_index - right_ankle` | Internal geometric angle between the two vectors listed | None; no `180 - angle` transform is applied | `src/feature_extraction.py:ANGLE_SIGNAL_MAP,_angle_for_points,_angle_between` |
| `ankle_angle_left` | left | ankle | `left_knee` -> `left_ankle` -> `left_foot_index` | `left_ankle - left_knee; left_foot_index - left_ankle` | Internal geometric angle between the two vectors listed | None; no `180 - angle` transform is applied | `src/feature_extraction.py:ANGLE_SIGNAL_MAP,_angle_for_points,_angle_between` |

## Validation Notes

The code does not apply clinical sign conventions, anatomical coordinate transformations, inverse-kinematics model constraints, or event segmentation. Therefore these measurements should be interpreted as deterministic MediaPipe landmark geometry only.
