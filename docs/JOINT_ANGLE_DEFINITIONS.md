# Joint Angle Definitions

The reference dataset stores named inverse-kinematics coordinates. This document distinguishes recovered label/unit evidence from unrecovered anatomical conventions.

| Joint/signal | Reference dataset coordinate | Units | Internal/external | Signed/unsigned | Range | Anatomical zero | JumpGuard definition | Equivalence status |
|---|---|---|---|---|---|---|---|---|
| right hip | `hip_flexion_r` | degrees | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | `hip_flexion_right` is an unsigned 0-180 degree MediaPipe vector angle from Prompt 14 | Unknown / not established |
| left hip | `hip_flexion_l` | degrees | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | `hip_flexion_left` is an unsigned 0-180 degree MediaPipe vector angle from Prompt 14 | Unknown / not established |
| right knee | `knee_angle_r` | degrees | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | `knee_flexion_right` is an unsigned 0-180 degree MediaPipe vector angle from Prompt 14 | Unknown / not established |
| left knee | `knee_angle_l` | degrees | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | `knee_flexion_left` is an unsigned 0-180 degree MediaPipe vector angle from Prompt 14 | Unknown / not established |
| right ankle | `ankle_angle_r` | degrees | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | `ankle_angle_right` is an unsigned 0-180 degree MediaPipe vector angle from Prompt 14 | Unknown / not established |
| left ankle | `ankle_angle_l` | degrees | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | `ankle_angle_left` is an unsigned 0-180 degree MediaPipe vector angle from Prompt 14 | Unknown / not established |

## Dataset Evidence

- `IK_column_labels.xlsx` proves the coordinate labels and `inDegrees=yes`.
- `Joint_Angles` values are finite for 249 valid trials.
- No available source defines whether these coordinates are internal joint angles, external joint angles, signed model generalized coordinates, flexion-positive conventions, or extension offsets.

## JumpGuard Evidence

Prompt 14 documents JumpGuard angles as deterministic MediaPipe-derived geometric approximations using `degrees(arccos(dot(a,b)/(||a||||b||)))`, producing unsigned angles in `[0, 180]` with no `180 - angle` transformation.

## Conclusion

Joint-angle name and degree units are recovered. The anatomical conventions required for mathematical harmonization are not recovered from available evidence.
