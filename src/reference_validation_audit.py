"""Prompt 15 reference-dataset reverse-engineering audit.

This module generates documentation only. It does not modify data, numerical
outputs, feature extraction, evidence interpretation, reports, or dashboards.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .feature_engineering import FeatureExtractor as DatasetFeatureExtractor
from .features.biomechanics import PRIMARY_JOINT_PAIRS, PRIMARY_JOINT_SIGNALS
from .features.statistical import DESCRIPTORS


UNKNOWN = "Unknown from available evidence."


@dataclass(frozen=True)
class ReferenceValidationAuditPaths:
    """Prompt 15 documentation paths."""

    dataset_reverse_engineering: Path
    feature_mapping: Path
    mathematical_equivalence: Path
    event_definition_audit: Path
    frame_comparability: Path
    angle_standardization: Path
    harmonization_recommendations: Path
    scientific_confidence_matrix: Path


def generate_reference_validation_audit(docs_dir: str | Path = "docs") -> ReferenceValidationAuditPaths:
    """Generate all Prompt 15 audit documents."""

    destination = Path(docs_dir)
    destination.mkdir(parents=True, exist_ok=True)
    paths = ReferenceValidationAuditPaths(
        dataset_reverse_engineering=destination / "DATASET_REVERSE_ENGINEERING.md",
        feature_mapping=destination / "FEATURE_MAPPING.md",
        mathematical_equivalence=destination / "MATHEMATICAL_EQUIVALENCE.md",
        event_definition_audit=destination / "EVENT_DEFINITION_AUDIT.md",
        frame_comparability=destination / "FRAME_COMPARABILITY.md",
        angle_standardization=destination / "ANGLE_STANDARDIZATION.md",
        harmonization_recommendations=destination / "HARMONIZATION_RECOMMENDATIONS.md",
        scientific_confidence_matrix=destination / "SCIENTIFIC_CONFIDENCE_MATRIX.md",
    )
    paths.dataset_reverse_engineering.write_text(render_dataset_reverse_engineering(), encoding="utf-8")
    paths.feature_mapping.write_text(render_feature_mapping(), encoding="utf-8")
    paths.mathematical_equivalence.write_text(render_mathematical_equivalence(), encoding="utf-8")
    paths.event_definition_audit.write_text(render_event_definition_audit(), encoding="utf-8")
    paths.frame_comparability.write_text(render_frame_comparability(), encoding="utf-8")
    paths.angle_standardization.write_text(render_angle_standardization(), encoding="utf-8")
    paths.harmonization_recommendations.write_text(render_harmonization_recommendations(), encoding="utf-8")
    paths.scientific_confidence_matrix.write_text(render_scientific_confidence_matrix(), encoding="utf-8")
    return paths


def render_dataset_reverse_engineering() -> str:
    rows = [
        "# Dataset Reverse Engineering",
        "",
        "Prompt 15 is a documentation-only reverse-engineering audit. It reuses Prompt 1 and Prompt 14 findings and does not change `DJ.mat`, `data/processed/features.csv`, feature extraction, evidence outputs, athlete reports, or dashboards.",
        "",
        "## Evidence Sources Inspected",
        "",
        "- `docs/DATASET_REPORT.md`: recursive MATLAB hierarchy, workbook inspection, label mapping, sampling, missingness, event-field inventory.",
        "- `docs/DATASET_SUMMARY.md`: Dataset/Participant/Trial abstraction, dimensions, validation boundary.",
        "- `docs/FEATURE_REPORT.md`: Prompt 3 dataset feature formulas and explicit event-use decision.",
        "- `docs/ANGLE_DEFINITION_AUDIT.md` and `docs/FEATURE_DEFINITION_AUDIT.md`: Prompt 14 uploaded-video measurement provenance.",
        "- `src/dataset_parser.py`, `src/trial.py`, `src/feature_engineering.py`, `src/features/statistical.py`, `src/features/symmetry.py`.",
        "- `data/metadata/IK_column_labels.xlsx`, `data/metadata/labeling_DJ.xlsx`, `data/metadata/participant_log.xlsx`.",
        "",
        "## Raw Dataset Structure",
        "",
        "| Item | Finding | Evidence |",
        "|---|---|---|",
        "| MAT format | Classic MATLAB 5.0 MAT-file loaded with `scipy.io.loadmat`. | `docs/DATASET_REPORT.md`; `src/load_dataset.py` |",
        "| Top-level variable | `DJ`, object array shape `(44, 1)`. | `docs/DATASET_REPORT.md` |",
        "| Populated participants | 42 populated MAT entries; metadata-backed participants are 1-4 and 6-44. | `docs/DATASET_REPORT.md`; `docs/DATASET_SUMMARY.md` |",
        "| Trial slots | Six slots per metadata-backed participant: `DJ_t1`, `DJ_t2`, `DJ_t3`, `f_DJ_t1`, `f_DJ_t2`, `f_DJ_t3`. | `docs/DATASET_REPORT.md`; `src/dataset_parser.py:TRIAL_NAMES` |",
        "| Valid trials | 249 valid numeric trials; 9 documented empty rows. | `docs/DATASET_REPORT.md`; `docs/DATASET_SUMMARY.md` |",
        "| Joint-angle array | `Joint_Angles` shape `(frames, 44)` for each valid trial. | `docs/DATASET_REPORT.md`; `src/dataset_parser.py` |",
        "| Marker arrays | 59 marker coordinate arrays `(frames, 3)` plus marker `time` `(frames, 1)`. | `docs/DATASET_REPORT.md` |",
        "| COM arrays | `COM_velocity`, `COM_position`, `COM_acceleration` each `(frames, 3)`. | `docs/DATASET_REPORT.md` |",
        "",
        "## Reference Joint-Angle Labels",
        "",
        "The authoritative label row is `IK_column_labels.xlsx!CMJ_dom_t1_IK!A12:AR12`. Row 4 declares `nColumns=44`, row 10 declares `endheader`, row 11 contains numeric indices 1-44, and row 12 contains the 44 labels used by `Joint_Angles`. Rotational values are in degrees because the workbook header contains `inDegrees=yes`.",
        "",
        "## Reverse-Engineered Measurement Properties",
        "",
        "| Property | Dataset finding | Evidence level |",
        "|---|---|---|",
        "| Mathematical definition of raw IK columns | The values are precomputed inverse-kinematics columns named by the workbook, including `hip_flexion_r`, `knee_angle_r`, and `ankle_angle_r`. The underlying model equations are not present. | Partially known; label-level evidence only. |",
        "| Units | Time in seconds; rotational values in degrees; general SI units for non-rotational quantities. | Direct evidence from workbook header. |",
        "| Angle convention | Labels identify flexion/angle/adduction/rotation names. Sign convention, axis order, segment coordinate definitions, internal vs external angle convention, and positive direction are not defined in available files. | Unknown from available evidence. |",
        "| Coordinate system | Marker arrays have `(frames, 3)` coordinates and COM arrays have `(frames, 3)`, but the global coordinate axes, calibration frame, and IK anatomical coordinate system are not defined in available files. | Unknown from available evidence. |",
        "| 2D or 3D | Dataset contains 3D markers and precomputed IK joint angles. Whether each IK angle was produced by a 3D musculoskeletal model is plausible from the data structure but not explicitly documented here. | Unknown from available evidence. |",
        "| Preprocessing | No authoritative smoothing, filtering, interpolation, gap-fill, marker-set preprocessing, or IK solver settings were found in the available files. | Unknown from available evidence. |",
        "| Sampling | Median time step is `0.004` seconds, implying 250 Hz from the time column. No explicit sampling-frequency field was found. | Inferred from data, documented in `docs/DATASET_REPORT.md`. |",
        "| Event fields | Four scalar fields exist: `IC_first_K`, `IC_second_K`, `IC_first_A`, `IC_second_A`. Values are in range and ordered first <= second. Meaning of `K` and `A` is not defined. | Field existence known; semantics unknown. |",
        "| Feature aggregation | Current project reference features use the full recording for all descriptors and symmetry metrics. Event fields are intentionally not used. | Direct code evidence from `src/feature_engineering.py`; documented in `docs/FEATURE_REPORT.md`. |",
        "| Single-frame vs multi-frame | Maximum, minimum, and time-to-peak depend on extrema frames; mean, median, std, variance, ROM, and symmetry depend on multiple frames. | Direct code evidence. |",
        "",
        "## Feature Families Used As Reference Features",
        "",
        _reference_feature_family_table(),
        "",
        "## Unknowns That Must Not Be Inferred",
        "",
        "- Raw dataset IK model, segment definitions, and anatomical coordinate systems.",
        "- Whether dataset flexion columns are internal angles, external angles, signed flexion/extension angles, or model-coordinate generalized coordinates.",
        "- Whether preprocessing included filtering, smoothing, interpolation, marker gap filling, or normalization before `Joint_Angles` were saved.",
        "- Authoritative meanings of `K` and `A` event suffixes.",
        "- Whether the stored event fields correspond to initial contact, takeoff, peak landing, or another operational definition.",
    ]
    return "\n".join(rows) + "\n"


def render_feature_mapping() -> str:
    rows = [
        "# Feature Mapping",
        "",
        "Each row maps one reference-dataset feature to the corresponding JumpGuard uploaded-video feature name. The feature names and aggregation formulas are intentionally identical, but the upstream angle source is different: reference features use `Trial.get_joint_angle(...)` on stored MATLAB inverse-kinematics columns, while uploaded-video features use MediaPipe-derived geometric angles from landmark triplets.",
        "",
        "| Dataset feature | JumpGuard feature | Dataset source signal | JumpGuard source signal | Mathematical definition | Units | Aggregation | Assumptions/unknowns | Confidence |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for definition in DatasetFeatureExtractor().definitions:
        dataset_signal = _dataset_signal_for_feature(definition.name)
        jumpguard_signal = _jumpguard_signal_for_feature(definition.name)
        confidence = _mapping_confidence(definition.name)
        rows.append(
            "| "
            f"`{definition.name}` | `{definition.name}` | {_md(dataset_signal)} | {_md(jumpguard_signal)} | `{_md(definition.formula)}` | {_md(definition.units)} | {_md(_aggregation_for_feature(definition.name))} | {_md(_mapping_assumption(definition.name))} | {confidence} |"
        )
    rows.extend([
        "",
        "## Mapping Summary",
        "",
        "- Name-level mapping: high confidence for all 57 features because the uploaded-video extractor reuses `Prompt3FeatureExtractor().feature_names` and validates the same ordered schema.",
        "- Formula-level mapping: high confidence for descriptors and symmetry formulas because both paths use the same descriptor names and equivalent NumPy/statistical formulas.",
        "- Measurement-level mapping: low to unknown confidence because dataset IK angle definitions are not available and JumpGuard angles are documented MediaPipe vector-geometry approximations.",
    ])
    return "\n".join(rows) + "\n"


def render_mathematical_equivalence() -> str:
    rows = [
        "# Mathematical Equivalence Audit",
        "",
        "Classification vocabulary: Equivalent, Equivalent after transformation, Not equivalent, Unknown. No transformations are applied in Prompt 15.",
        "",
        "## Global Equivalence Findings",
        "",
        "| Component | Classification | Evidence |",
        "|---|---|---|",
        "| Feature names | Equivalent | `src/feature_extraction.py` initializes uploaded-video feature names from `src.feature_engineering.FeatureExtractor().feature_names`. |",
        "| Descriptor formulas | Equivalent | Dataset path uses `describe_signal`; uploaded-video path uses `_finite_descriptor` with the same mean, median, population std, population variance, maximum, minimum, and ROM formulas. |",
        "| Time-to-peak formula | Equivalent for available time arrays | Both use first maximum and subtract first timestamp: `time[argmax(x)] - time[0]`. |",
        "| Symmetry formulas | Equivalent | Both paths call or mirror `absolute_difference`, `percent_difference`, and `symmetry_index` from `src/features/symmetry.py`. |",
        "| Units of feature outputs | Equivalent for currently exported descriptors | Dataset workbook states rotational values are degrees; JumpGuard geometric angles are degrees; time-to-peak is seconds; percent metrics are percent. |",
        "| Source landmarks/segments | Not equivalent | Dataset source is stored IK joint-angle columns; JumpGuard source is MediaPipe pose landmarks and explicit triplet vectors. |",
        "| Coordinate system | Unknown | Dataset IK coordinate system is not documented in available evidence; JumpGuard uses MediaPipe normalized coordinates. |",
        "| Angle convention | Unknown | Dataset sign/range/internal-external convention is not documented. JumpGuard uses unsigned 0-180 degree geometric internal vector angles. |",
        "| Event/window equivalence | Equivalent for current feature extraction window only | Both current feature extractors compute over full recordings and do not use `IC_*` fields. |",
        "| Biomechanical equivalence of raw angles | Unknown / not established | There is no evidence proving `hip_flexion_r`, `knee_angle_r`, or `ankle_angle_r` from the reference dataset are mathematically identical to the MediaPipe triplet angles. |",
        "",
        "## Feature-Level Equivalence",
        "",
        "| Feature | Landmarks/vectors | Angle convention | Units | Transformation | Aggregation | Symmetry/ROM | Overall classification | Evidence |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for definition in DatasetFeatureExtractor().definitions:
        rows.append(
            f"| `{definition.name}` | {_md(_landmark_equivalence(definition.name))} | Unknown | Equivalent | Unknown | Equivalent | {_md(_symmetry_equivalence(definition.name))} | {_overall_equivalence(definition.name)} | {_md(_equivalence_evidence(definition.name))} |"
        )
    return "\n".join(rows) + "\n"


def render_event_definition_audit() -> str:
    return """# Event Definition Audit

## Event Fields Present In The Reference Dataset

| Field | Present? | Observed properties | Detection algorithm | Frame selection | Timing definition | Evidence source | Classification |
|---|---|---|---|---|---|---|---|
| `IC_first_K` | Yes | Scalar integer per valid trial; in frame range; first <= second for K fields. | Unknown from available evidence. | Unknown from available evidence. | Unknown from available evidence. | `docs/DATASET_REPORT.md`; `src/dataset_parser.py:EVENT_FIELDS` | Semantics unknown |
| `IC_second_K` | Yes | Scalar integer per valid trial; in frame range. | Unknown from available evidence. | Unknown from available evidence. | Unknown from available evidence. | `docs/DATASET_REPORT.md`; `src/dataset_parser.py:EVENT_FIELDS` | Semantics unknown |
| `IC_first_A` | Yes | Scalar integer per valid trial; in frame range; first <= second for A fields. | Unknown from available evidence. | Unknown from available evidence. | Unknown from available evidence. | `docs/DATASET_REPORT.md`; `src/dataset_parser.py:EVENT_FIELDS` | Semantics unknown |
| `IC_second_A` | Yes | Scalar integer per valid trial; in frame range. | Unknown from available evidence. | Unknown from available evidence. | Unknown from available evidence. | `docs/DATASET_REPORT.md`; `src/dataset_parser.py:EVENT_FIELDS` | Semantics unknown |

## Requested Event Concepts

| Event concept | Reference dataset status | JumpGuard status | Prompt 15 conclusion |
|---|---|---|---|
| Initial Contact | The `IC_*` prefix may suggest initial contact, but K/A suffix meaning and detection algorithm are not documented. | No initial-contact detector exists; Prompt 14 marks it unavailable. | Unknown from available evidence. Do not use for harmonization without external documentation. |
| Peak Landing | No explicit peak-landing field or algorithm found. | No documented peak-landing detector exists. | Unknown from available evidence. |
| Maximum Knee Flexion | Can be computed by feature code as the first maximum of `knee_angle_*` or `knee_flexion_*`; not a stored dataset event field. | Prompt 14 computes extrema provenance for first maximum frame of each source signal and a peak mean knee-flexion frame for audit only. | Feature-derived extrema are documented; event semantics are not equivalent to a landing event. |
| Takeoff | No takeoff field or algorithm found. | No takeoff detector exists. | Unknown from available evidence. |
| Landing Phase | Four `IC_*` fields exist but are not used because their semantics are not defined. | No landing phase segmentation exists. | Unknown from available evidence; current features are full-recording features. |

## Decision Boundary

Prompt 15 does not infer `K` or `A`, does not convert one-based event indices, and does not introduce event detectors. Any future use of these event fields requires authoritative documentation or a validated algorithm.
"""


def render_frame_comparability() -> str:
    rows = [
        "# Frame Comparability Audit",
        "",
        "This audit uses Prompt 14 `frame_provenance.json` conceptually: uploaded-video features are traced to full processed recordings and, where applicable, representative extrema frames. The reference dataset feature extractor uses the same full-recording aggregation definitions over stored IK time series. This document does not alter provenance files or numerical outputs.",
        "",
        "Classification vocabulary: Directly comparable, Comparable after event detection, Not comparable, Unknown.",
        "",
        "| Feature | Dataset frame basis | JumpGuard frame basis | Comparability | Rationale |",
        "|---|---|---|---|---|",
    ]
    for definition in DatasetFeatureExtractor().definitions:
        rows.append(
            f"| `{definition.name}` | {_md(_dataset_frame_basis(definition.name))} | {_md(_jumpguard_frame_basis(definition.name))} | {_frame_comparability(definition.name)} | {_md(_frame_rationale(definition.name))} |"
        )
    rows.extend([
        "",
        "## Summary",
        "",
        "Frame/window comparability is high for the implemented full-recording feature formulas because neither path uses landing-phase segmentation. However, biomechanical comparability remains limited by unknown dataset IK conventions and non-equivalent upstream measurement sources.",
    ])
    return "\n".join(rows) + "\n"


def render_angle_standardization() -> str:
    rows = [
        "# Angle Standardization Audit",
        "",
        "Prompt 15 identifies possible standardization needs but does not apply transformations.",
        "",
        "## Dataset Angle Convention Evidence",
        "",
        "| Question | Dataset answer | Evidence |",
        "|---|---|---|",
        "| Are rotational values degrees or radians? | Degrees. | `IK_column_labels.xlsx` header: `inDegrees=yes`. |",
        "| Are columns named as flexion/adduction/rotation? | Yes, labels include `hip_flexion_*`, `knee_angle_*`, and `ankle_angle_*`. | `IK_column_labels.xlsx!A12:AR12`; `docs/DATASET_REPORT.md`. |",
        "| Internal or external angles? | Unknown from available evidence. | No model definition or sign convention documentation found. |",
        "| Flexion or extension sign convention? | Unknown from available evidence. | Labels alone do not define positive direction. |",
        "| Signed or unsigned? | Unknown from available evidence. | Raw value ranges can be inspected, but sign convention cannot be inferred as authoritative. |",
        "| Range convention? | Unknown from available evidence. | Workbook does not define range. |",
        "| Coordinate axes / anatomical coordinate system? | Unknown from available evidence. | No IK model documentation found in local files. |",
        "",
        "## JumpGuard Angle Convention Evidence",
        "",
        "JumpGuard uploaded-video angles are deterministic 3D vector-geometry angles from MediaPipe landmarks. They use `degrees(arccos(dot(a,b)/(||a||||b||)))`, produce unsigned values in `[0, 180]`, use MediaPipe `x,y,z` coordinates, and apply no `180 - angle` transformation. Evidence: `docs/ANGLE_DEFINITION_AUDIT.md`; `src/feature_extraction.py`.",
        "",
        "## Standardization Requirements By Signal",
        "",
        "| Signal family | Dataset source | JumpGuard source | Required transformation | Confidence | Rationale |",
        "|---|---|---|---|---|---|",
    ]
    for signal in PRIMARY_JOINT_SIGNALS:
        rows.append(
            f"| `{signal.key}` | `{signal.label}` stored IK column | MediaPipe triplet angle | Unknown from available evidence | Low | Dataset IK convention is not documented, so angle inversion, sign flip, offset, or internal/external conversion cannot be justified yet. |"
        )
    rows.extend([
        "",
        "## Prohibited Inferences",
        "",
        "- Do not assume `knee_angle_*` equals MediaPipe hip-knee-ankle internal angle.",
        "- Do not assume `hip_flexion_*` equals shoulder-hip-knee angle; laboratory hip flexion is usually model-based, but the exact model definition is not available here.",
        "- Do not apply `180 - angle`, sign flips, offsets, or event-window transformations without external evidence or a validation dataset that pairs source videos with the reference IK outputs.",
    ])
    return "\n".join(rows) + "\n"


def render_harmonization_recommendations() -> str:
    return """# Harmonization Recommendations

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
"""


def render_scientific_confidence_matrix() -> str:
    rows = [
        "# Scientific Confidence Matrix",
        "",
        "| Feature family | Landmark equivalence | Angle convention equivalence | Aggregation equivalence | Event definition equivalence | Overall scientific comparability | Evidence summary |",
        "|---|---|---|---|---|---|---|",
    ]
    for family in ("hip_flexion", "knee_flexion", "ankle_angle"):
        rows.append(
            f"| `{family}` | Low | Unknown | High | Not applicable for current full-recording features; unknown for event-based windows | Low-to-moderate | Same feature formulas, different and not-yet-harmonized source angle definitions. |"
        )
    rows.append(
        "| bilateral ROM symmetry | Low for upstream landmarks; high for scalar formula once ROM values exist | Unknown because source ROM angle conventions are unknown | High | Not applicable for current full-recording features | Moderate for formula-only comparison; low for biomechanical equivalence | Symmetry formulas match, but ROM values inherit upstream angle-source uncertainty. |"
    )
    rows.extend([
        "",
        "## Confidence Scale",
        "",
        "- High: directly verified from code, workbook metadata, or generated Prompt 14 provenance.",
        "- Moderate: verified for the implemented formula but limited by upstream measurement uncertainty.",
        "- Low: known structural mismatch or insufficient source evidence for biomechanical equivalence.",
        "- Unknown: definition cannot be verified from available evidence.",
        "",
        "## Overall Conclusion",
        "",
        "The athlete pipeline and reference dataset are mathematically equivalent at the feature-name and aggregation-formula level. They are not established as mathematically equivalent at the raw biomechanical measurement level because the reference dataset's IK angle definitions, coordinate system, preprocessing, and event semantics are unknown from available evidence, while JumpGuard uses documented MediaPipe vector geometry.",
    ])
    return "\n".join(rows) + "\n"


def _reference_feature_family_table() -> str:
    rows = [
        "| Dataset labels | Project feature prefix | Feature formulas | Evidence |",
        "|---|---|---|---|",
    ]
    for signal in PRIMARY_JOINT_SIGNALS:
        rows.append(
            f"| `{signal.label}` | `{signal.key}` | {', '.join(DESCRIPTORS)} plus `time_to_peak` | `src/features/biomechanics.py`; `src/feature_engineering.py` |"
        )
    for pair in PRIMARY_JOINT_PAIRS:
        rows.append(
            f"| `{pair.left_label}` and `{pair.right_label}` ROM | `{pair.key}_rom_*` | absolute difference, percent difference, symmetry index | `src/features/symmetry.py`; `src/feature_engineering.py` |"
        )
    return "\n".join(rows)


def _dataset_signal_for_feature(feature: str) -> str:
    for signal in PRIMARY_JOINT_SIGNALS:
        if feature.startswith(signal.key):
            return f"`{signal.label}` from `Joint_Angles`"
    for pair in PRIMARY_JOINT_PAIRS:
        if feature.startswith(pair.key):
            return f"ROM from `{pair.left_label}` and `{pair.right_label}`"
    return UNKNOWN


def _jumpguard_signal_for_feature(feature: str) -> str:
    for signal in PRIMARY_JOINT_SIGNALS:
        if feature.startswith(signal.key):
            return f"`{signal.key}` MediaPipe geometric angle"
    for pair in PRIMARY_JOINT_PAIRS:
        if feature.startswith(pair.key):
            left = _key_for_label(pair.left_label)
            right = _key_for_label(pair.right_label)
            return f"ROM from `{left}` and `{right}` MediaPipe geometric angles"
    return UNKNOWN


def _key_for_label(label: str) -> str:
    return {signal.label: signal.key for signal in PRIMARY_JOINT_SIGNALS}[label]


def _aggregation_for_feature(feature: str) -> str:
    if feature.endswith("time_to_peak"):
        return "time[argmax(x)] - time[0] over the full recording"
    for descriptor in DESCRIPTORS:
        if feature.endswith(descriptor):
            return {
                "mean": "arithmetic mean over all finite frames",
                "median": "median over all finite frames",
                "std": "population standard deviation over all finite frames, ddof=0",
                "variance": "population variance over all finite frames, ddof=0",
                "maximum": "maximum over all finite frames",
                "minimum": "minimum over all finite frames",
                "rom": "maximum minus minimum over all finite frames",
            }[descriptor]
    if feature.endswith("absolute_difference"):
        return "absolute difference between left and right full-recording ROM"
    if feature.endswith("percent_difference"):
        return "absolute ROM difference divided by mean side magnitude"
    if feature.endswith("symmetry_index"):
        return "signed ROM difference divided by mean side magnitude"
    return UNKNOWN


def _mapping_confidence(feature: str) -> str:
    if any(token in feature for token in ("absolute_difference", "percent_difference", "symmetry_index")):
        return "Moderate: formula matches, source ROM angles not proven equivalent"
    return "Moderate: feature formula matches, source angle not proven equivalent"


def _mapping_assumption(feature: str) -> str:
    return "No assumption of raw biomechanical equivalence; dataset IK convention remains unknown."


def _landmark_equivalence(feature: str) -> str:
    if any(feature.startswith(pair.key) for pair in PRIMARY_JOINT_PAIRS):
        return "Not equivalent upstream; symmetry uses stored IK ROM versus MediaPipe ROM"
    return "Not equivalent: stored IK column versus MediaPipe landmark triplet"


def _symmetry_equivalence(feature: str) -> str:
    if any(token in feature for token in ("absolute_difference", "percent_difference", "symmetry_index")):
        return "Equivalent formula after ROM values exist; upstream ROM equivalence unknown"
    if feature.endswith("rom"):
        return "Equivalent ROM formula; upstream angle equivalence unknown"
    return "Not applicable"


def _overall_equivalence(feature: str) -> str:
    if any(token in feature for token in ("absolute_difference", "percent_difference", "symmetry_index")):
        return "Unknown"
    return "Unknown"


def _equivalence_evidence(feature: str) -> str:
    return "Formula and units are supported by code/workbook evidence; raw angle equivalence cannot be verified from available evidence."


def _dataset_frame_basis(feature: str) -> str:
    if feature.endswith("maximum") or feature.endswith("minimum") or feature.endswith("time_to_peak"):
        return "First full-recording source-signal extremum frame by feature code"
    if feature.endswith("rom"):
        return "Full-recording maximum and minimum frames"
    if any(token in feature for token in ("absolute_difference", "percent_difference", "symmetry_index")):
        return "Left/right full-recording ROM extrema; no single frame"
    return "All frames in full recording"


def _jumpguard_frame_basis(feature: str) -> str:
    if feature.endswith("maximum") or feature.endswith("minimum") or feature.endswith("time_to_peak"):
        return "Prompt 14 representative source frame for first extremum"
    if feature.endswith("rom"):
        return "Prompt 14 provenance records all finite frames and representative extrema"
    if any(token in feature for token in ("absolute_difference", "percent_difference", "symmetry_index")):
        return "Prompt 14 traces left/right ROM extrema; no single anatomical frame"
    return "Prompt 14 traces all finite source frames and representative aggregate frame"


def _frame_comparability(feature: str) -> str:
    if any(token in feature for token in ("absolute_difference", "percent_difference", "symmetry_index")):
        return "Directly comparable as full-recording scalar formula; not comparable as a single frame"
    return "Directly comparable as full-recording feature window"


def _frame_rationale(feature: str) -> str:
    return "Both current extractors use the full recording and do not use undocumented landing events; angle-source equivalence remains separate and unresolved."


def _md(value: Any) -> str:
    return str(value).replace("|", "\\|")


if __name__ == "__main__":
    generated = generate_reference_validation_audit()
    for value in generated.__dict__.values():
        print(value)
