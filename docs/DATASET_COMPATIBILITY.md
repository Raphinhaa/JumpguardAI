# Dataset Compatibility

Compatibility is assessed against the existing JumpGuard pipeline only. No new pose model, event detector, segmentation algorithm, or feature calculation is proposed here.

## Compatibility Matrix

| Dataset | Sagittal view | Full-body visibility | Occlusion | Lighting | Motion blur | Foot visibility | Camera stability | Expected MediaPipe robustness | Pipeline status |
|---|---|---|---|---|---|---|---|---|---|
| FineGym | Variable; often oblique/broadcast | Variable | Likely during flips/dismounts | Broadcast quality but variable | Likely in high-speed gymnastics | Often uncertain | Variable pans/zooms | Conditional to poor for intense motion; official page notes pose-estimation misses | Pilot only after manual QC |
| NTU RGB+D / NTU RGB+D 120 | Potentially selectable from controlled views | Likely better than in-the-wild datasets | Low-to-moderate | Controlled | Unknown | Must inspect RGB frames | Stable | Potentially moderate-to-high for simple jumps, if labels/video access are verified | Pilot only |
| Kinetics human action video datasets | Uncontrolled | Variable | High variability | Variable | Variable | Variable | Variable | Low-to-moderate; large manual rejection expected | Stress testing only |
| UCF101 | Uncontrolled | Variable | High variability | Variable | Variable | Variable | Paper reports camera motion and clutter | Low for normative use | Reject for normative reference |
| Human3.6M / H3WB | Controlled but task mismatch | Likely high | Low | Controlled | Low-to-moderate | Likely visible | Stable | Technically promising, but no verified jump-landing task | Reject unless task subset is proven |

## Minimum QC Gate For Any Future Pilot

A video may enter a future JumpGuard normative pilot only if all required MediaPipe landmarks for hip, knee, ankle, shoulder, and foot-index angle calculations are visible for most of the movement, the full body remains in frame, the camera is stable enough for repeated processing, and the landing-like movement can be identified from documented labels or manual review without inventing event timing.
