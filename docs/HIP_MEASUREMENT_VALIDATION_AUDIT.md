# Hip Measurement Validation Audit

Prompt 24 adds a developer-only scientific audit for investigating left/right hip measurement discrepancies. This is a validation and documentation layer only.

## Scope

The audit does not modify:

- MediaPipe pose estimation,
- landmark extraction,
- joint-angle mathematics,
- feature extraction,
- delta calculations,
- symmetry calculations,
- time-series generation,
- graph generation,
- clinician workstation behavior,
- Measurement Debug Mode,
- CSV/JSON schemas, or
- numerical outputs.

## Method

The audit reuses the existing Prompt 23 frame database and debug artifacts. It reads the already-computed per-frame landmark coordinates, visibility, confidence, hip angles, delta values, and symmetry values.

It produces developer-only reports in the run's `measurement_debug/` folder:

- `hip_measurement_validation_report.md`
- `hip_measurement_validation_report.json`

## What The Audit Reports

- Exact measurement definitions for hip, knee, and ankle signals using `ANGLE_SIGNAL_MAP`.
- The vector construction and unsigned internal angle convention used by the current implementation.
- Ranked frames with the largest observed left/right hip differences.
- Landmark visibility and confidence summaries for shoulders, hips, knees, and ankles.
- Evidence notes for missing, nonfinite, or low-visibility hip-triplet landmarks.
- Recommendations for future validation without implementing formula changes.

## Scientific Boundary

The audit can identify evidence such as missing landmarks or low visibility in frames with large hip differences. It cannot prove occlusion, camera perspective, or MediaPipe model error without paired visual review or external ground truth. Any future change to measurement formulas must be handled in a separate scientific prompt with validation evidence.

