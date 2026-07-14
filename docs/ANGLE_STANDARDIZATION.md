# Angle Standardization Audit

Prompt 15 identifies possible standardization needs but does not apply transformations.

## Dataset Angle Convention Evidence

| Question | Dataset answer | Evidence |
|---|---|---|
| Are rotational values degrees or radians? | Degrees. | `IK_column_labels.xlsx` header: `inDegrees=yes`. |
| Are columns named as flexion/adduction/rotation? | Yes, labels include `hip_flexion_*`, `knee_angle_*`, and `ankle_angle_*`. | `IK_column_labels.xlsx!A12:AR12`; `docs/DATASET_REPORT.md`. |
| Internal or external angles? | Unknown from available evidence. | No model definition or sign convention documentation found. |
| Flexion or extension sign convention? | Unknown from available evidence. | Labels alone do not define positive direction. |
| Signed or unsigned? | Unknown from available evidence. | Raw value ranges can be inspected, but sign convention cannot be inferred as authoritative. |
| Range convention? | Unknown from available evidence. | Workbook does not define range. |
| Coordinate axes / anatomical coordinate system? | Unknown from available evidence. | No IK model documentation found in local files. |

## JumpGuard Angle Convention Evidence

JumpGuard uploaded-video angles are deterministic 3D vector-geometry angles from MediaPipe landmarks. They use `degrees(arccos(dot(a,b)/(||a||||b||)))`, produce unsigned values in `[0, 180]`, use MediaPipe `x,y,z` coordinates, and apply no `180 - angle` transformation. Evidence: `docs/ANGLE_DEFINITION_AUDIT.md`; `src/feature_extraction.py`.

## Standardization Requirements By Signal

| Signal family | Dataset source | JumpGuard source | Required transformation | Confidence | Rationale |
|---|---|---|---|---|---|
| `hip_flexion_right` | `hip_flexion_r` stored IK column | MediaPipe triplet angle | Unknown from available evidence | Low | Dataset IK convention is not documented, so angle inversion, sign flip, offset, or internal/external conversion cannot be justified yet. |
| `hip_flexion_left` | `hip_flexion_l` stored IK column | MediaPipe triplet angle | Unknown from available evidence | Low | Dataset IK convention is not documented, so angle inversion, sign flip, offset, or internal/external conversion cannot be justified yet. |
| `knee_flexion_right` | `knee_angle_r` stored IK column | MediaPipe triplet angle | Unknown from available evidence | Low | Dataset IK convention is not documented, so angle inversion, sign flip, offset, or internal/external conversion cannot be justified yet. |
| `knee_flexion_left` | `knee_angle_l` stored IK column | MediaPipe triplet angle | Unknown from available evidence | Low | Dataset IK convention is not documented, so angle inversion, sign flip, offset, or internal/external conversion cannot be justified yet. |
| `ankle_angle_right` | `ankle_angle_r` stored IK column | MediaPipe triplet angle | Unknown from available evidence | Low | Dataset IK convention is not documented, so angle inversion, sign flip, offset, or internal/external conversion cannot be justified yet. |
| `ankle_angle_left` | `ankle_angle_l` stored IK column | MediaPipe triplet angle | Unknown from available evidence | Low | Dataset IK convention is not documented, so angle inversion, sign flip, offset, or internal/external conversion cannot be justified yet. |

## Prohibited Inferences

- Do not assume `knee_angle_*` equals MediaPipe hip-knee-ankle internal angle.
- Do not assume `hip_flexion_*` equals shoulder-hip-knee angle; laboratory hip flexion is usually model-based, but the exact model definition is not available here.
- Do not apply `180 - angle`, sign flips, offsets, or event-window transformations without external evidence or a validation dataset that pairs source videos with the reference IK outputs.
