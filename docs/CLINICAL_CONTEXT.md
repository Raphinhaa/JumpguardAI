# Clinical Context

This document explains what JumpGuard measurements represent biomechanically and what they do not imply. It avoids diagnostic and predictive language.

## Angle Families

| Family | Represents | Used in ACL or landing biomechanics research | Limitations | Does not imply |
|---|---|---|---|---|
| Hip flexion | Sagittal-plane hip strategy approximated from shoulder, hip, and knee landmarks for uploaded videos. | Landing studies and LESS-style evaluations consider hip/trunk/lower-extremity posture as part of movement assessment. | JumpGuard uses a shoulder-hip-knee vector angle, not a pelvis-based ISB hip coordinate; trunk/pelvis coordinate frames are not reconstructed. | No diagnosis, risk score, hip pathology, or readiness decision. |
| Knee flexion | Internal angle formed by hip, knee, and ankle landmarks for uploaded videos. | Knee kinematics are central to jump-landing ACL biomechanics research. | Does not measure frontal-plane knee abduction, knee valgus moment, or tibiofemoral joint loading. | No ACL risk prediction, ligament status, or dynamic valgus diagnosis. |
| Ankle angle | Internal angle formed by knee, ankle, and foot-index landmarks for uploaded videos. | Ankle strategy and lower-extremity posture are considered in landing assessments. | Foot-index landmark does not reconstruct full foot segment orientation or ankle joint coordinate systems. | No diagnosis, ankle pathology, or force absorption conclusion by itself. |

## Descriptor Families

| Descriptor | Represents | Limitations | Does not imply |
|---|---|---|---|
| Mean / median | Typical full-recording angle magnitude. | Sensitive to recording duration and task phase; not landing-phase-specific. | No clinical normality threshold. |
| Maximum / minimum | Extrema within the processed recording. | May occur outside the intended landing phase if the video includes setup or recovery. | No event-specific peak landing metric unless event timing is validated. |
| ROM | Full-recording angular excursion. | Not equivalent to clinical passive ROM or laboratory joint excursion unless source signal and window are validated. | No tissue mobility diagnosis. |
| Standard deviation / variance | Full-recording signal variability. | Can reflect task timing, pose-estimation noise, missingness, or movement variability. | No neuromuscular-control diagnosis. |
| Time-to-peak | Time from first finite timestamp to first maximum. | Depends on video start time and full-recording window; not contact-relative. | No reaction-time or landing-control conclusion. |
| Bilateral symmetry metrics | Side-to-side ROM differences. | Formula conventions vary; asymmetry thresholds are not applied. | No injury-risk or return-to-sport decision. |
