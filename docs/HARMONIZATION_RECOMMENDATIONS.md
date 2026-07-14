# Harmonization Recommendations

These are evidence-based recommendations for Prompt 16 planning only. No data or calculations are changed in Prompt 15.

| Recommendation | Rationale | Supporting evidence | Confidence | Action status |
|---|---|---|---|---|
| Preserve the current shared 57-feature schema. | Name-level and formula-level compatibility is already established across dataset and uploaded-video features. | `src/feature_extraction.py` uses `Prompt3FeatureExtractor().feature_names`; `validate_feature_table` enforces the same ordered schema. | High | Recommended |
| Treat current reference comparisons as dataset-relative descriptive comparisons, not proof of measurement equivalence. | The reference dataset source angles are precomputed IK columns; JumpGuard source angles are MediaPipe vector geometry. | `docs/DATASET_REPORT.md`; `docs/ANGLE_DEFINITION_AUDIT.md`; `src/feature_extraction.py`. | High | Required caution |
| Do not apply angle inversion, sign flips, offsets, or `180 - angle` transformations yet. | Dataset angle convention and anatomical coordinate system are unknown from available evidence. | `IK_column_labels.xlsx` gives labels and degrees but not model conventions. | High | Defer to Prompt 16 only if new evidence appears |
| Do not use `IC_first_K`, `IC_second_K`, `IC_first_A`, or `IC_second_A` for landing-phase harmonization yet. | K/A suffix meanings and event detection algorithms are not documented. | `docs/DATASET_REPORT.md`; `docs/FEATURE_REPORT.md`; `src/dataset_parser.py:EVENT_FIELDS`. | High | Defer |
| If harmonization is required later, first obtain authoritative dataset IK documentation or paired source C3D/video with known IK outputs. | Without paired evidence, transformations between MediaPipe geometry and laboratory IK cannot be validated. | Prompt 15 equivalence audit. | High | Recommended prerequisite |
| Keep full-recording aggregation as the default until event semantics are validated. | Current dataset and JumpGuard feature extractors both compute over the full recording. Changing windows would alter numerical outputs and create unsupported assumptions. | `docs/FEATURE_REPORT.md`; `docs/FEATURE_DEFINITION_AUDIT.md`. | High | Preserve |
| Consider a future calibration study rather than direct mathematical conversion. | MediaPipe normalized landmark geometry and lab IK generalized coordinates may differ in segment definitions, coordinate systems, depth scaling, and model constraints. | `docs/ANGLE_DEFINITION_AUDIT.md`; dataset IK convention unknowns. | Moderate | Future work |

## Bottom Line

The safest Prompt 16 starting point is not to force equivalence. First acquire or reconstruct authoritative IK definitions, event semantics, and paired validation data. Until then, JumpGuard and the reference dataset should be described as sharing feature names and aggregation formulas, but not as mathematically equivalent biomechanical measurements.
