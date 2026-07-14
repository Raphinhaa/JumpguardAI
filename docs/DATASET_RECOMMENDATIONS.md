# Dataset Recommendations

## Decision

**No discovered public dataset is recommended for immediate production use as a healthy JumpGuard normative reference.**

The most scientifically defensible path is to create or obtain a JumpGuard-native healthy video cohort with explicit consent/licensing, standardized jump-landing protocol, stable camera views, complete metadata, and full-body visibility. Public datasets may be useful only for feasibility and robustness pilots.

## Ranked Recommendations

| Rank | Dataset | Decision | Evidence-backed rationale | Required next evidence |
|---|---|---|---|---|
| 1 for pilot screening; not acceptable as production healthy normative reference. | FineGym | Use only for a small feasibility pilot of landing-like clips after manual QC and rights review. Do not use for normative statistics. | Conditional pilot only. Landing-like segments may stress MediaPipe because the official page reports pose-estimation misses in intense gymnastics motion. | Verify video rights, retrieve landing-like clips, quantify MediaPipe failure rate, and exclude from normative statistics unless health/task metadata become adequate. |
| 2 for technical pilot if jump labels are verified; not acceptable as production healthy normative reference. | NTU RGB+D / NTU RGB+D 120 | Use only after official action labels, terms, video availability, and sagittal/full-body visibility are verified. | Conditional pilot only. Controlled camera and full-body RGB are promising, but task and subject health metadata are not normative-grade. | Verify official labels, access terms, jump/hop class availability, RGB video quality, sagittal view suitability, and health metadata. |
| 3 for broad stress testing; reject for normative statistics. | Kinetics human action video datasets | Do not use for normative reference. At most use as a robustness stress-test set after rights review. | Low-to-moderate for exploratory stress testing only; not controlled enough for normative reference statistics. | Verify jump-related classes, video availability, rights, health metadata, and QC yield; expected to remain unsuitable for normative statistics. |
| 4; reject for normative reference. | UCF101 | Reject for normative reference; possible only as a negative-control or robustness set. | Low. Camera motion, clutter, and task heterogeneity make it unsuitable for normative JumpGuard statistics. | Verify rights and jump-related classes only if needed for stress testing; not recommended for normative use. |
| 5; reject for Prompt 18 normative objective. | Human3.6M / H3WB | Reject for normative jump-landing reference unless a verified jump-landing subset is documented. | Technically promising for pose estimation but task-incompatible for JumpGuard jump-landing normative reference. | Verify whether a documented jump-landing action subset exists; otherwise reject for this objective. |

## Production Normative Reference Recommendation

Build a new healthy cohort or obtain a purpose-collected dataset rather than relying on action-recognition or broadcast-sports datasets. A production reference should be based on known healthy participants, standardized task instructions, fixed recording geometry, stable RGB video, documented frame rate and resolution, complete rights, and unchanged JumpGuard processing.

## What Must Remain Unknown

For any public candidate where health status, age, sex, license, frame rate, resolution, camera view, or task protocol is not documented by a publication or official source, the field must remain `Unknown from available evidence` and must not be inferred from video appearance.
