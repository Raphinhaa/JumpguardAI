# Hip Discrepancy Investigation

Prompt 25 adds a developer-only investigation layer for occasional left/right hip measurement discrepancies. It reuses the existing Measurement Debug Mode and Hip Measurement Validation Audit records.

## Scope

This layer is evidence-only. It does not modify MediaPipe pose estimation, landmark extraction, joint-angle mathematics, feature extraction, delta calculations, symmetry calculations, graph generation, CSV/JSON measurement schemas, clinician workstation behavior, or numerical outputs.

## Outputs

Each successful interactive analysis run exports these additional files under `measurement_debug/`:

- `hip_discrepancy_investigation_report.md`
- `hip_discrepancy_investigation_report.json`
- `hip_discrepancy_investigation_report.html`

## Evidence Reviewed

The investigation reads existing frame records only:

- computed `hip_flexion_left` and `hip_flexion_right` values
- shoulder, hip, and knee landmarks used in the current hip-angle definition
- vector geometry for shoulder-to-hip and knee-to-hip construction
- landmark visibility and confidence values
- missing or nonfinite landmark coordinates
- MediaPipe z-coordinate comparison, without inferring camera near/far side

## Origin Categories

The report classifies the available evidence as one of:

- `landmark estimation`
- `occlusion`
- `camera perspective`
- `angle-definition limitations`
- `insufficient evidence`

The classification is conservative. Camera perspective is reported as insufficient evidence unless camera calibration, view metadata, or external ground truth is available. Angle-definition limitations are documented as a scientific boundary of the current MediaPipe-derived shoulder-hip-knee vector definition, not as proof that the definition caused a specific frame discrepancy.

## Scientific Boundary

The investigation may identify evidence consistent with a future mathematical improvement, but Prompt 25 does not implement improvements, corrections, smoothing, filtering, landmark substitution, or new biomechanical formulas.
