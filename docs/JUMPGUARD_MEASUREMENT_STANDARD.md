# JumpGuard Biomechanical Measurement Standard

This is the official Prompt 17 measurement standard for quantities currently produced by JumpGuard. It validates measurement definitions, not clinical outcomes. The standard is independent of undocumented reference-dataset assumptions.

## Governing Principles

1. Every measurement must name its source signal, mathematical formula, units, and limitations.
2. Uploaded-video joint angles are MediaPipe-derived geometric approximations from landmarks. They are not laboratory inverse-kinematics joint angles.
3. Reference-dataset inverse-kinematics angle labels remain useful for feature names, but undocumented coordinate-system details are not used as scientific authority.
4. Full-recording descriptors are valid only for the processed recording window unless a future validated event detector defines a landing phase.
5. No feature implies ACL injury risk, diagnosis, tissue status, or clinical readiness by itself.

## Primary Angle Signals

| Signal | Mathematical definition | Biomechanical meaning | Units | Literature support | Standard status |
|---|---|---|---|---|---|
| `hip_flexion_right` | `angle between shoulder-to-hip and hip-to-knee vectors` | right hip sagittal-plane movement approximation from landmarks. | degrees | ISB hip reporting context plus jump-landing posture literature | Partial match: construct supported, exact MediaPipe vector angle is a geometric approximation. |
| `hip_flexion_left` | `angle between shoulder-to-hip and hip-to-knee vectors` | left hip sagittal-plane movement approximation from landmarks. | degrees | ISB hip reporting context plus jump-landing posture literature | Partial match: construct supported, exact MediaPipe vector angle is a geometric approximation. |
| `knee_flexion_right` | `internal angle formed by hip, knee, and ankle landmarks` | right knee sagittal-plane movement approximation from landmarks. | degrees | Grood-Suntay knee coordinate-system context plus ACL landing-biomechanics literature | Partial match: knee motion construct supported, exact unsigned vector angle is not laboratory knee flexion. |
| `knee_flexion_left` | `internal angle formed by hip, knee, and ankle landmarks` | left knee sagittal-plane movement approximation from landmarks. | degrees | Grood-Suntay knee coordinate-system context plus ACL landing-biomechanics literature | Partial match: knee motion construct supported, exact unsigned vector angle is not laboratory knee flexion. |
| `ankle_angle_right` | `angle between knee-to-ankle and ankle-to-foot-index vectors` | right ankle sagittal-plane movement approximation from landmarks. | degrees | ISB ankle reporting context plus landing-posture literature | Partial match: ankle motion construct supported, exact foot-index vector angle is a geometric approximation. |
| `ankle_angle_left` | `angle between knee-to-ankle and ankle-to-foot-index vectors` | left ankle sagittal-plane movement approximation from landmarks. | degrees | ISB ankle reporting context plus landing-posture literature | Partial match: ankle motion construct supported, exact foot-index vector angle is a geometric approximation. |

## Descriptor Families

| Family | Formula | Meaning | Units | Literature support | Standard status |
|---|---|---|---|---|---|
| Mean | `sum(x) / N` | Average angle magnitude over the full processed recording. | degrees | Statistical descriptor; reliability context supported by Atkinson and Nevill. | Verified mathematical descriptor; biomechanical interpretation depends on source signal validity. |
| Median | `median(x)` | Central angle magnitude over the full processed recording. | degrees | Statistical descriptor; robust descriptive summary. | Verified mathematical descriptor; not a separate clinical construct. |
| Standard deviation | `sqrt(sum((x - mean)^2) / N)` with `ddof=0` | Full-recording angular variability. | degrees | Reliability and measurement-error literature supports explicit variability reporting. | Verified mathematical descriptor; reliability must be validated for each acquisition setup. |
| Variance | `sum((x - mean)^2) / N` with `ddof=0` | Squared angular variability. | degrees squared | Reliability and measurement-error literature supports explicit variability reporting. | Verified mathematical descriptor; clinical meaning is limited without repeatability evidence. |
| Maximum | `max(x)` | Largest recorded geometric angle in the processed recording. | degrees | Peak joint postures are common in landing biomechanics, but exact timing window matters. | Verified mathematical descriptor; event-specific interpretation is inconclusive. |
| Minimum | `min(x)` | Smallest recorded geometric angle in the processed recording. | degrees | Extrema are common kinematic descriptors, but exact timing window matters. | Verified mathematical descriptor; event-specific interpretation is inconclusive. |
| Range of motion | `max(x) - min(x)` | Full-recording angular excursion. | degrees | Joint excursion/ROM is a standard biomechanical descriptor. | Verified mathematical descriptor; not equivalent to clinical passive ROM. |
| Time-to-peak | `time[argmax(x)] - time[0]` | Elapsed time from first finite timestamp to first maximum. | seconds | Timing of kinematic peaks is used in movement analysis, but full-recording first-maximum timing is task-specific. | Partial match; implementation is verified, clinical interpretation is inconclusive. |

## Symmetry Families

| Family | Formula | Meaning | Units | Literature support | Standard status |
|---|---|---|---|---|---|
| Absolute difference | `abs(ROM_L - ROM_R)` | Unsigned side-to-side ROM difference. | degrees | Bilateral symmetry/asymmetry is a recognized biomechanical construct. | Verified mathematical descriptor; no threshold is implied. |
| Percent difference | `100 * abs(ROM_L - ROM_R) / ((abs(ROM_L) + abs(ROM_R)) / 2)` | Unsigned side-to-side ROM difference normalized to average side magnitude. | percent | Literature uses multiple asymmetry normalizations. | Verified implementation; consensus on this exact formula is partial. |
| Symmetry index | `100 * (ROM_L - ROM_R) / ((abs(ROM_L) + abs(ROM_R)) / 2)` | Signed side-to-side ROM difference; positive means larger left ROM in JumpGuard. | percent | Symmetry-index concepts are used in biomechanics, but formula conventions vary. | Verified implementation; no clinical threshold is implied. |
