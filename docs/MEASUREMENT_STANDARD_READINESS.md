# Measurement Standard Readiness

## Readiness Decision

**Ready as a transparent JumpGuard measurement-definition standard. Not ready to claim laboratory biomechanical equivalence or clinical prediction.**

## What Is Ready

| Area | Status | Evidence |
|---|---|---|
| Feature schema coverage | Ready | All 57 currently produced feature names are covered in `STANDARDS_MATRIX.md` and `IMPLEMENTATION_VALIDATION.md`. |
| Mathematical definitions | Ready | Formulas are derived from `src/feature_engineering.py`, `src/feature_extraction.py`, and `src/features/*`. |
| Literature context | Ready with limits | Peer-reviewed sources support joint-coordinate reporting standards, jump-landing biomechanics context, sports-medicine reliability reporting, and bilateral symmetry constructs. |
| Safety constraints | Ready | The standard explicitly rejects diagnosis, risk scoring, clinical thresholds, and undocumented event inference. |

## What Remains Inconclusive

| Area | Status | Reason |
|---|---|---|
| MediaPipe-to-laboratory equivalence | Inconclusive | No validation study specific to JumpGuard's landmark pipeline and angle definitions is available. |
| ISB coordinate-system equivalence | Inconclusive | JumpGuard computes vector angles, not full anatomical segment coordinate systems. |
| Reference dataset harmonization | Partially ready, formula-only | Prompt 16 found reference IK methodology unknown. Prompt 17 supplies an independent JumpGuard standard but does not recover the dataset methodology. |
| Event-based landing metrics | Not ready | No validated landing-event detector or dataset event dictionary is available. |

## Required Evidence Before Harmonization Upgrade

1. A validation study comparing JumpGuard MediaPipe-derived angles against laboratory motion capture for the same movements.
2. A documented coordinate-frame mapping if future work attempts ISB-style anatomical angles.
3. Reference dataset methods files or publication details sufficient to recover the original IK pipeline.
4. Reliability analysis for repeated JumpGuard videos and repeated processing.
5. A validated event detector before any contact-relative or landing-phase features are treated as standards.

## Final Statement

JumpGuard now has a conservative, literature-backed measurement-definition standard independent of undocumented reference-dataset assumptions. This standard supports transparent reporting of what JumpGuard measures. It does not support clinical prediction, diagnosis, injury-risk scoring, or raw-angle harmonization with the reference dataset.
