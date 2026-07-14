# Normative Reference Plan

## Objective

Create a future JumpGuard-native normative reference dataset by processing healthy jump-landing videos through the same MediaPipe landmark detector, feature extraction pipeline, feature names, and statistical methodology used for athlete videos.

## Inclusion Criteria

| Category | Required criterion |
|---|---|
| Health status | Participants documented as healthy or uninjured at collection; if absent, mark unknown and exclude from production normative statistics. |
| Task | Standardized jump-landing task with documented instructions, start/end criteria, and footwear/surface context. |
| Camera | Stable RGB video with full-body visibility; sagittal or near-sagittal view preferred for current hip/knee/ankle vector-angle definitions. |
| Visibility | Shoulders, hips, knees, ankles, and foot-index landmarks visible throughout the analyzed recording. |
| Metadata | Participant ID, age or age band, sex/gender if collected, height, mass if available, sport/activity status if available, task type, camera frame rate, resolution, recording date/version, and license. |
| Rights | License or permission explicitly allows research processing and derivative aggregate statistics. |

## Exclusion Criteria

| Category | Exclude when |
|---|---|
| Health status | Injury, pain, ACL reconstruction status, neurological condition, or health status unknown for production normative use. |
| Video quality | Body leaves frame, severe occlusion, severe motion blur, unstable camera, or feet not visible. |
| Task ambiguity | The clip is a generic jump, gymnastics skill, or action-recognition segment with no standardized landing protocol. |
| Legal ambiguity | Video rights, license, or redistribution terms are unknown or incompatible. |
| Processing failure | Existing JumpGuard pipeline cannot produce required landmark-derived angle features without modification. |

## Recording Standard For New Data Collection

1. Record at a fixed distance with the whole body visible from takeoff preparation through landing recovery.
2. Prefer sagittal and frontal views as separate cameras; process only the view documented for the chosen standard.
3. Use stable tripod placement, even lighting, minimal background clutter, and visible feet.
4. Capture frame rate and resolution directly from video metadata.
5. Preserve raw videos and immutable metadata; do not trim unless trimming rules are documented and deterministic.
6. Use the existing JumpGuard full-recording feature extraction unless a future validated event detector is approved.

## Preprocessing Policy

No smoothing, pose interpolation, manual landmark correction, angle transformation, event segmentation, or feature engineering changes are authorized by Prompt 18. Any future preprocessing must be documented as a separate prompt and validated before use.
