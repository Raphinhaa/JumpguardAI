# Scientific Confidence Matrix

| Feature family | Landmark equivalence | Angle convention equivalence | Aggregation equivalence | Event definition equivalence | Overall scientific comparability | Evidence summary |
|---|---|---|---|---|---|---|
| `hip_flexion` | Low | Unknown | High | Not applicable for current full-recording features; unknown for event-based windows | Low-to-moderate | Same feature formulas, different and not-yet-harmonized source angle definitions. |
| `knee_flexion` | Low | Unknown | High | Not applicable for current full-recording features; unknown for event-based windows | Low-to-moderate | Same feature formulas, different and not-yet-harmonized source angle definitions. |
| `ankle_angle` | Low | Unknown | High | Not applicable for current full-recording features; unknown for event-based windows | Low-to-moderate | Same feature formulas, different and not-yet-harmonized source angle definitions. |
| bilateral ROM symmetry | Low for upstream landmarks; high for scalar formula once ROM values exist | Unknown because source ROM angle conventions are unknown | High | Not applicable for current full-recording features | Moderate for formula-only comparison; low for biomechanical equivalence | Symmetry formulas match, but ROM values inherit upstream angle-source uncertainty. |

## Confidence Scale

- High: directly verified from code, workbook metadata, or generated Prompt 14 provenance.
- Moderate: verified for the implemented formula but limited by upstream measurement uncertainty.
- Low: known structural mismatch or insufficient source evidence for biomechanical equivalence.
- Unknown: definition cannot be verified from available evidence.

## Overall Conclusion

The athlete pipeline and reference dataset are mathematically equivalent at the feature-name and aggregation-formula level. They are not established as mathematically equivalent at the raw biomechanical measurement level because the reference dataset's IK angle definitions, coordinate system, preprocessing, and event semantics are unknown from available evidence, while JumpGuard uses documented MediaPipe vector geometry.
