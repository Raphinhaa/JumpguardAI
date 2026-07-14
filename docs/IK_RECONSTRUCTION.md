# Inverse Kinematics Reconstruction

This document reconstructs only what can be verified. OpenSim literature is used as context, not as proof that a specific model or setup was used for this dataset.

## Recovered IK Workflow Components

| Component | Recovered definition | Confidence | Evidence |
|---|---|---|---|
| Input marker trajectories | 59 named marker arrays plus marker `time`, with marker coordinates shaped `(frames, 3)`. | High | `docs/DATASET_REPORT.md` |
| Output generalized coordinates | `Joint_Angles` arrays shaped `(frames, 44)` with coordinate labels from `IK_column_labels.xlsx!A12:AR12`. | High | `docs/DATASET_REPORT.md`; workbook row `nColumns=44` |
| Units | Rotational coordinates are degrees. | High | `IK_column_labels.xlsx` header `inDegrees=yes` |
| Time base | First `Joint_Angles` column is `time`; median step 0.004 s, inferred 250 Hz. | Moderate | `docs/DATASET_REPORT.md` |
| IK solver | Unknown from available evidence. | Unknown | No setup file or publication recovered. |
| Coordinate systems | Unknown from available evidence. | Unknown | No global lab axes, segment coordinate frames, or model file recovered. |
| Joint frames | Unknown from available evidence. | Unknown | No `.osim` model or joint definitions recovered. |
| Rotation order | Unknown from available evidence. | Unknown | Coordinate labels alone do not define rotation order. |
| Anatomical zero | Unknown from available evidence. | Unknown | No model calibration/scaling documentation recovered. |
| Static calibration trial | Unknown from available evidence. | Unknown | No static trial, setup XML, or methods section recovered. |
| Model scaling | Unknown from available evidence. | Unknown | Participant anthropometrics exist, but no scale tool settings or marker-pair scale factors are present. |
| Marker weights | Unknown from available evidence. | Unknown | No IK setup file recovered. |
| Error thresholds / residuals | Unknown from available evidence. | Unknown | No IK log, marker-error table, or threshold documentation recovered. |
| Optimisation objective | Unknown for this dataset. OpenSim IK generally minimizes weighted marker-coordinate errors, but dataset-specific settings are absent. | Contextual only | OpenSim documentation/literature; no dataset-specific setup file. |

## Coordinate Labels Recovered

| Coordinate group | Labels recovered | Evidence |
|---|---|---|
| Time | `time` | IK label workbook row 12 |
| Pelvis translations/rotations | `pelvis_list`, `pelvis_tilt`, `pelvis_rotation`, `pelvis_tx`, `pelvis_ty`, `pelvis_tz` | IK label workbook row 12 |
| Right lower limb | `hip_flexion_r`, `hip_adduction_r`, `hip_rotation_r`, `knee_angle_r`, `knee_adduction_r`, `knee_rotation_r`, `knee_angle_r_beta`, `ankle_angle_r`, `subtalar_angle_r`, `mtp_angle_r` | IK label workbook row 12 |
| Left lower limb | `hip_flexion_l`, `hip_adduction_l`, `hip_rotation_l`, `knee_angle_l`, `knee_adduction_l`, `knee_rotation_l`, `knee_angle_l_beta`, `ankle_angle_l`, `subtalar_angle_l`, `mtp_angle_l` | IK label workbook row 12 |
| Lumbar | `lumbar_extension`, `lumbar_bending`, `lumbar_rotation` | IK label workbook row 12 |
| Upper limbs | arm, elbow, forearm, wrist coordinates for both sides | IK label workbook row 12 |

## Reconstruction Boundary

The local files recover the existence of OpenSim-style coordinate outputs but not the exact inverse-kinematics methodology. A faithful reconstruction would require the original `.osim` model, marker set protocol, static calibration/scaling files, IK setup XML, marker weights, software version, filtering settings, and original methods publication.
