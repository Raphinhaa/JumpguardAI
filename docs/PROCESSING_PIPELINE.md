# Processing Pipeline

Prompt 18 does not run processing. This is a future roadmap for processing candidate videos through the existing JumpGuard architecture only.

## Ranked Candidate Roadmap

| Rank | Dataset | Estimated usable videos | Expected feature coverage | Processing effort | Recommendation |
|---|---|---|---|---|---|
| 1 for pilot screening; not acceptable as production healthy normative reference. | FineGym | Unknown until YouTube availability, event filters, and manual QC are complete | Potentially partial due to high motion and occlusion | High manual QC and rights review | Pilot only |
| 2 for technical pilot if jump labels are verified; not acceptable as production healthy normative reference. | NTU RGB+D / NTU RGB+D 120 | Unknown until official action labels and download access are verified | Potentially good for simple full-body jumps if labels exist and views are sagittal enough | Moderate access verification and QC | Technical pilot only |
| 3 for broad stress testing; reject for normative statistics. | Kinetics human action video datasets | Unknown and likely unstable over time due to URL rot | Variable and noisy | Very high manual filtering | Reject for normative statistics |
| 4; reject for normative reference. | UCF101 | Unknown | Variable and noisy | High manual filtering | Reject for normative statistics |
| 5; reject for Prompt 18 normative objective. | Human3.6M / H3WB | Unknown; no verified jump-landing subset | High pose quality if task existed | Access and task verification | Reject unless task subset is proven |

## Future Processing Phases

1. Rights and access verification: confirm licenses, download mechanisms, and durable source availability.
2. Metadata extraction: build a candidate manifest with dataset source, video ID, participant metadata, task label, camera view, frame rate, resolution, and rights status.
3. Manual QC: reject videos that fail full-body visibility, foot visibility, stable camera, and task-standardization gates.
4. Dry-run processing: run a small approved subset through the existing JumpGuard pipeline without code changes.
5. Missingness audit: summarize landmark failures and feature NaN rates.
6. Normative-statistics generation: only after enough health-screened standardized videos remain.
7. Evidence-layer integration: compare athlete videos against the new MediaPipe-derived reference only after the statistical protocol is complete.
