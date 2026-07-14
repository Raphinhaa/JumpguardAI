# Harmonization Readiness

## Readiness Decision

**Partially ready, formula-only. Not ready for raw biomechanical harmonization.**

## What Is Ready

| Area | Status | Evidence |
|---|---|---|
| Shared feature schema | Ready | Both paths use the same 57 feature names. |
| Descriptor formulas | Ready | Mean, median, maximum, minimum, ROM, variance, STD, and time-to-peak formulas are recovered and equivalent. |
| Symmetry formulas | Ready | Absolute difference, percent difference, and symmetry index formulas are recovered and equivalent. |
| Full-recording window | Ready for current features | Current project features intentionally avoid undocumented event windows. |

## What Is Not Ready

| Area | Status | Blocker |
|---|---|---|
| Raw angle harmonization | Not ready | Dataset IK coordinate definitions, model, sign conventions, and anatomical zero are unknown. |
| Event-based harmonization | Not ready | `IC_*` event semantics, K/A meanings, thresholds, and algorithms are unknown. |
| Numerical reconstruction of reference IK | Not ready | OpenSim model, scaling, marker weights, filtering, interpolation, and solver settings are unknown. |
| Clinical/biomechanical equivalence claims | Not ready | MediaPipe vector geometry and laboratory IK coordinates are not proven equivalent. |

## Required Evidence Before Prompt 16 Can Advance To Harmonization

1. Dataset publication or methods document with acquisition and processing details.
2. Original OpenSim model or coordinate definitions used for `Joint_Angles`.
3. Scaling and IK setup files, including marker weights and solver settings.
4. Filtering/interpolation/trial-trimming methods.
5. Event dictionary defining `IC_first_K`, `IC_second_K`, `IC_first_A`, and `IC_second_A`.
6. Preferably paired raw video or marker/C3D files with the exported IK coordinates for validation.

## Final Statement

Future harmonization may safely preserve feature names and formulas. It must not yet standardize angles, apply transformations, segment landing phases, or claim measurement equivalence. The current evidence supports only formula-level compatibility, not full scientific equivalence of biomechanical measurements.
