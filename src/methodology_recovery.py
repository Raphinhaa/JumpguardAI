"""Prompt 16 scientific methodology recovery documentation.

This module writes documentation only. It does not modify datasets, feature
values, pipelines, reports, dashboards, or evidence outputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .feature_engineering import FeatureExtractor
from .features.biomechanics import PRIMARY_JOINT_PAIRS, PRIMARY_JOINT_SIGNALS
from .features.statistical import DESCRIPTORS


UNKNOWN = "Unknown from available evidence."


@dataclass(frozen=True)
class MethodologyRecoveryPaths:
    """Prompt 16 deliverable paths."""

    dataset_lineage: Path
    ik_reconstruction: Path
    joint_angle_definitions: Path
    event_methods: Path
    signal_processing: Path
    feature_formulas: Path
    scientific_equivalence_matrix: Path
    unknowns_register: Path
    harmonization_readiness: Path


def generate_methodology_recovery_docs(docs_dir: str | Path = "docs") -> MethodologyRecoveryPaths:
    """Generate all Prompt 16 methodology-recovery deliverables."""

    destination = Path(docs_dir)
    destination.mkdir(parents=True, exist_ok=True)
    paths = MethodologyRecoveryPaths(
        dataset_lineage=destination / "DATASET_LINEAGE.md",
        ik_reconstruction=destination / "IK_RECONSTRUCTION.md",
        joint_angle_definitions=destination / "JOINT_ANGLE_DEFINITIONS.md",
        event_methods=destination / "EVENT_METHODS.md",
        signal_processing=destination / "SIGNAL_PROCESSING.md",
        feature_formulas=destination / "FEATURE_FORMULAS.md",
        scientific_equivalence_matrix=destination / "SCIENTIFIC_EQUIVALENCE_MATRIX.md",
        unknowns_register=destination / "UNKNOWNS_REGISTER.md",
        harmonization_readiness=destination / "HARMONIZATION_READINESS.md",
    )
    paths.dataset_lineage.write_text(render_dataset_lineage(), encoding="utf-8")
    paths.ik_reconstruction.write_text(render_ik_reconstruction(), encoding="utf-8")
    paths.joint_angle_definitions.write_text(render_joint_angle_definitions(), encoding="utf-8")
    paths.event_methods.write_text(render_event_methods(), encoding="utf-8")
    paths.signal_processing.write_text(render_signal_processing(), encoding="utf-8")
    paths.feature_formulas.write_text(render_feature_formulas(), encoding="utf-8")
    paths.scientific_equivalence_matrix.write_text(render_scientific_equivalence_matrix(), encoding="utf-8")
    paths.unknowns_register.write_text(render_unknowns_register(), encoding="utf-8")
    paths.harmonization_readiness.write_text(render_harmonization_readiness(), encoding="utf-8")
    return paths


def render_dataset_lineage() -> str:
    return """# Dataset Lineage

Prompt 16 reconstructs methodology from available documentation and published sources only. No code, dataset values, reports, dashboards, or evidence outputs are changed.

## Evidence Sources Used

| Source | Evidence contributed | Dataset-specific? |
|---|---|---|
| `docs/DATASET_REPORT.md` | MAT-file hierarchy, `DJ` participant/trial organization, `Joint_Angles` shape, marker/COM arrays, IK labels, event-field inventory, sampling inferred from time. | Yes |
| `docs/DATASET_SUMMARY.md` | Clean Dataset/Participant/Trial abstraction and validation summary. | Yes |
| `docs/DATASET_REVERSE_ENGINEERING.md` | Prompt 15 conclusion that feature formulas match but raw measurement equivalence is not established. | Yes |
| `data/metadata/IK_column_labels.xlsx` | OpenSim-style coordinate header with `inDegrees=yes`, `nColumns=44`, and 44 coordinate labels. | Yes |
| `data/metadata/labeling_DJ.xlsx` | Subject/trial rows, fatigue condition, missing-data flags and notes. | Yes |
| `data/metadata/participant_log.xlsx` | Participant metadata including group, gender, age, height, weight, leg dominance, fatigued leg, activity metadata, jump-height and BORG columns. | Yes |
| `data/metadata/ACL_questionnaires.xlsx` | ACL group questionnaire sheets: IKDC, ACL-RSI, Tampa. | Yes |
| OpenSim publications and documentation | General context for OpenSim modeling and inverse kinematics workflows. | No; contextual only unless local dataset files identify the same model/settings. |

## Recovered Lineage Fields

| Required field | Recovered value | Evidence and confidence |
|---|---|---|
| Dataset title | Drop Jump dataset stored as `DJ.mat`; exact public dataset title unknown. | Local filename and metadata support Drop Jump/DJ. Publication title unknown. |
| Original publication | Unknown from available evidence. | No DOI, PMID, manuscript title, author list, or citation appears in local files. Web searches using local filenames/column names did not identify a unique publication. |
| DOI / PMID | Unknown from available evidence. | No dataset-specific DOI/PMID recovered. |
| Authors / institution | Unknown from available evidence. | No author or institutional metadata found. |
| Repository / version / licence | Unknown from available evidence. | Local repository contains copied dataset files but no source repository, version, or licence metadata for the reference dataset. |
| Participant population | 43 metadata-backed subjects, IDs 1-4 and 6-44. Metadata contains control/ACL group coding, gender, anthropometrics, leg dominance, fatigued leg, and ACL injured leg. | High confidence from `labeling_DJ.xlsx`, `participant_log.xlsx`, and `docs/DATASET_REPORT.md`; clinical recruitment criteria unknown. |
| Movement task | Six Drop Jump slots per metadata subject: three nonfatigued and three fatigued trials where available. | High confidence from `.File` values, `labeling_DJ.xlsx`, and parser constants. |
| Hardware | Unknown from available evidence. | Marker arrays imply motion capture, but camera system, force plates, analog devices, and lab hardware are not documented. |
| Marker set | 59 named markers plus marker `time`; names include pelvis, thigh, tibia, foot, trunk, head, and upper-limb markers. | High confidence for marker names and dimensions from `docs/DATASET_REPORT.md`; marker-placement protocol unknown. |
| Sampling frequency | 250 Hz inferred from median `Joint_Angles` time step of 0.004 s. | Moderate confidence; derived from data, not an explicit metadata field. |
| Force plates | Unknown from available evidence. | No force-plate channels or GRF arrays were found. Event fields may have used force or kinematic criteria, but that is not documented. |
| Software | OpenSim-compatible evidence exists: `IK_column_labels.xlsx` has a `Coordinates` header, `inDegrees=yes`, and OpenSim-like coordinate labels. Exact software and version remain unknown. | Moderate for OpenSim-compatible coordinate export; unknown for exact software/version. |
| OpenSim model | Unknown from available evidence. | Coordinate names resemble common OpenSim lower-extremity/full-body coordinate names, but no `.osim` model, scale file, setup file, or model name is present. |

## Published Context, Not Dataset-Specific Proof

- Delp et al. describe OpenSim as open-source software for creating and analyzing dynamic simulations of movement: https://doi.org/10.1109/TBME.2007.901024
- Seth et al. describe OpenSim for musculoskeletal dynamics and neuromuscular-control simulations: https://doi.org/10.1371/journal.pcbi.1006223
- OpenSim documentation describes inverse kinematics as a tool-driven process using a model, marker trajectories, and setup choices. Because the dataset-specific setup files are absent, these sources cannot recover this dataset's exact model or settings.

## Lineage Conclusion

The local evidence supports a processed Drop Jump biomechanics dataset containing OpenSim-style inverse-kinematics coordinate outputs, 3D marker trajectories, COM arrays, participant/trial metadata, fatigue labels, and ACL questionnaires. The original publication, source repository, hardware, exact OpenSim model, IK setup, filtering, and event definitions remain unknown from available evidence.
"""


def render_ik_reconstruction() -> str:
    rows = [
        "# Inverse Kinematics Reconstruction",
        "",
        "This document reconstructs only what can be verified. OpenSim literature is used as context, not as proof that a specific model or setup was used for this dataset.",
        "",
        "## Recovered IK Workflow Components",
        "",
        "| Component | Recovered definition | Confidence | Evidence |",
        "|---|---|---|---|",
        "| Input marker trajectories | 59 named marker arrays plus marker `time`, with marker coordinates shaped `(frames, 3)`. | High | `docs/DATASET_REPORT.md` |",
        "| Output generalized coordinates | `Joint_Angles` arrays shaped `(frames, 44)` with coordinate labels from `IK_column_labels.xlsx!A12:AR12`. | High | `docs/DATASET_REPORT.md`; workbook row `nColumns=44` |",
        "| Units | Rotational coordinates are degrees. | High | `IK_column_labels.xlsx` header `inDegrees=yes` |",
        "| Time base | First `Joint_Angles` column is `time`; median step 0.004 s, inferred 250 Hz. | Moderate | `docs/DATASET_REPORT.md` |",
        "| IK solver | Unknown from available evidence. | Unknown | No setup file or publication recovered. |",
        "| Coordinate systems | Unknown from available evidence. | Unknown | No global lab axes, segment coordinate frames, or model file recovered. |",
        "| Joint frames | Unknown from available evidence. | Unknown | No `.osim` model or joint definitions recovered. |",
        "| Rotation order | Unknown from available evidence. | Unknown | Coordinate labels alone do not define rotation order. |",
        "| Anatomical zero | Unknown from available evidence. | Unknown | No model calibration/scaling documentation recovered. |",
        "| Static calibration trial | Unknown from available evidence. | Unknown | No static trial, setup XML, or methods section recovered. |",
        "| Model scaling | Unknown from available evidence. | Unknown | Participant anthropometrics exist, but no scale tool settings or marker-pair scale factors are present. |",
        "| Marker weights | Unknown from available evidence. | Unknown | No IK setup file recovered. |",
        "| Error thresholds / residuals | Unknown from available evidence. | Unknown | No IK log, marker-error table, or threshold documentation recovered. |",
        "| Optimisation objective | Unknown for this dataset. OpenSim IK generally minimizes weighted marker-coordinate errors, but dataset-specific settings are absent. | Contextual only | OpenSim documentation/literature; no dataset-specific setup file. |",
        "",
        "## Coordinate Labels Recovered",
        "",
        _coordinate_table(),
        "",
        "## Reconstruction Boundary",
        "",
        "The local files recover the existence of OpenSim-style coordinate outputs but not the exact inverse-kinematics methodology. A faithful reconstruction would require the original `.osim` model, marker set protocol, static calibration/scaling files, IK setup XML, marker weights, software version, filtering settings, and original methods publication.",
    ]
    return "\n".join(rows) + "\n"


def render_joint_angle_definitions() -> str:
    rows = [
        "# Joint Angle Definitions",
        "",
        "The reference dataset stores named inverse-kinematics coordinates. This document distinguishes recovered label/unit evidence from unrecovered anatomical conventions.",
        "",
        "| Joint/signal | Reference dataset coordinate | Units | Internal/external | Signed/unsigned | Range | Anatomical zero | JumpGuard definition | Equivalence status |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for signal in PRIMARY_JOINT_SIGNALS:
        rows.append(
            f"| {signal.side} {signal.joint} | `{signal.label}` | degrees | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | `{signal.key}` is an unsigned 0-180 degree MediaPipe vector angle from Prompt 14 | Unknown / not established |"
        )
    rows.extend([
        "",
        "## Dataset Evidence",
        "",
        "- `IK_column_labels.xlsx` proves the coordinate labels and `inDegrees=yes`.",
        "- `Joint_Angles` values are finite for 249 valid trials.",
        "- No available source defines whether these coordinates are internal joint angles, external joint angles, signed model generalized coordinates, flexion-positive conventions, or extension offsets.",
        "",
        "## JumpGuard Evidence",
        "",
        "Prompt 14 documents JumpGuard angles as deterministic MediaPipe-derived geometric approximations using `degrees(arccos(dot(a,b)/(||a||||b||)))`, producing unsigned angles in `[0, 180]` with no `180 - angle` transformation.",
        "",
        "## Conclusion",
        "",
        "Joint-angle name and degree units are recovered. The anatomical conventions required for mathematical harmonization are not recovered from available evidence.",
    ])
    return "\n".join(rows) + "\n"


def render_event_methods() -> str:
    return """# Event Methods

## Dataset Event Fields

| Stored field | Recovered status | Algorithm | Frame selection | Threshold | Timing definition | Evidence |
|---|---|---|---|---|---|---|
| `IC_first_K` | Present as scalar frame index in valid trials | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | `docs/DATASET_REPORT.md`; `src/dataset_parser.py:EVENT_FIELDS` |
| `IC_second_K` | Present as scalar frame index in valid trials | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | `docs/DATASET_REPORT.md`; `src/dataset_parser.py:EVENT_FIELDS` |
| `IC_first_A` | Present as scalar frame index in valid trials | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | `docs/DATASET_REPORT.md`; `src/dataset_parser.py:EVENT_FIELDS` |
| `IC_second_A` | Present as scalar frame index in valid trials | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | Unknown from available evidence | `docs/DATASET_REPORT.md`; `src/dataset_parser.py:EVENT_FIELDS` |

## Requested Biomechanical Events

| Event | Dataset method recovered? | JumpGuard method recovered? | Harmonization implication |
|---|---|---|---|
| Initial Contact | No. `IC_*` names may suggest initial contact, but K/A meanings and detection method are unknown. | No documented detector exists. | Blocks event-based harmonization. |
| Toe Off | No. | No. | Unknown. |
| Peak Landing | No. | No. Prompt 14 has an audit-only peak mean knee-flexion frame, not a landing detector. | Blocks landing-phase harmonization. |
| Maximum Knee Flexion | Feature-code extrema are defined; dataset event semantics are not. | Prompt 14 provenance identifies extrema frames for audit. | Comparable as an extrema feature, not as a named landing event. |
| Landing Phase | No authoritative definition. | No landing phase segmentation. | Current features remain full-recording features. |
| Propulsion | No. | No. | Unknown. |
| Stance | No. | No. | Unknown. |
| Flight | No. | No. | Unknown. |

## Safety Decision

No event field is used for feature extraction because the K/A suffixes and detection algorithms are not documented. Prompt 16 does not infer event semantics and does not introduce event detectors.
"""


def render_signal_processing() -> str:
    return """# Signal Processing

## Reference Dataset Signal Processing Recovery

| Processing step | Recovered dataset method | Confidence | Evidence |
|---|---|---|---|
| Marker gap filling / interpolation | Unknown from available evidence. | Unknown | No raw C3D, preprocessing scripts, or methods publication recovered. |
| Marker filtering | Unknown from available evidence. | Unknown | No cutoff frequency, filter type, order, or phase information recovered. |
| Joint-angle filtering | Unknown from available evidence. | Unknown | `Joint_Angles` are already processed outputs; no generation settings recovered. |
| COM filtering / differentiation | Unknown from available evidence. | Unknown | COM arrays are present, but generation method is not documented. |
| Resampling | Unknown from available evidence. | Unknown | Time step implies 250 Hz, but no resampling method is documented. |
| Coordinate transforms | Unknown from available evidence. | Unknown | No lab-coordinate or model-coordinate documentation recovered. |
| Normalization | Unknown for raw dataset generation. | Unknown | Participant metadata contains anthropometrics, but no normalization method for IK values is documented. |
| Trial trimming | Unknown from available evidence. | Unknown | Valid frame counts vary from 842 to 2280 and time starts at 0; trimming criteria are not documented. |

## Current Project Feature Processing

The current project extracts full-recording features from the stored `Joint_Angles` arrays. It does not apply additional filtering, smoothing, interpolation, normalization, or event-windowing during feature extraction. Evidence: `src/feature_engineering.py` and `docs/FEATURE_REPORT.md`.

## JumpGuard Uploaded-Video Processing

Prompt 10 exports MediaPipe landmarks without smoothing, trajectory filtering, coordinate rotation, missing-joint inference, or biomechanical angle calculation. Prompt 11 computes deterministic vector-geometry angles and full-recording descriptors. Evidence: `docs/POSE_ESTIMATION_REPORT.md`, `docs/FEATURE_EXTRACTION_REPORT.md`, and `docs/ANGLE_DEFINITION_AUDIT.md`.

## Conclusion

Reference dataset preprocessing remains a major unrecovered methodology component. Harmonization should not assume that the reference IK signals and JumpGuard signals have compatible filtering, coordinate transforms, or temporal windows.
"""


def render_feature_formulas() -> str:
    rows = [
        "# Feature Formulas",
        "",
        "These formulas are recovered from the project feature extraction code. They define the current reference feature table and JumpGuard-compatible feature schema; they do not recover the upstream laboratory IK angle-generation method.",
        "",
        "## Scalar Descriptor Formulas",
        "",
        "Let `x` be the finite full-recording angle signal and `t` its corresponding time vector.",
        "",
        "| Descriptor | Formula | Dataset implementation | JumpGuard implementation | Formula equivalence |",
        "|---|---|---|---|---|",
        "| Maximum | `max(x)` | `describe_signal` / `FeatureExtractor.extract` | `_finite_descriptor(..., 'maximum')` | Verified equivalent |",
        "| Minimum | `min(x)` | `describe_signal` / `FeatureExtractor.extract` | `_finite_descriptor(..., 'minimum')` | Verified equivalent |",
        "| Mean | `sum(x) / N` | `np.mean` | `np.mean` over finite values | Verified equivalent |",
        "| Median | `median(x)` | `np.median` | `np.median` over finite values | Verified equivalent |",
        "| ROM | `max(x) - min(x)` | `describe_signal` | `_finite_descriptor(..., 'rom')` | Verified equivalent |",
        "| Variance | population variance, `ddof=0` | `np.var(..., ddof=0)` | `np.var(..., ddof=0)` over finite values | Verified equivalent |",
        "| STD | population standard deviation, `ddof=0` | `np.std(..., ddof=0)` | `np.std(..., ddof=0)` over finite values | Verified equivalent |",
        "| Time-to-peak | `t[argmax(x)] - t[0]` | `src/features/temporal.py:time_to_peak` | `_time_to_peak` | Verified equivalent for available time vectors |",
        "",
        "## Symmetry Formulas",
        "",
        "Let `L` and `R` be left and right full-recording ROM values.",
        "",
        "| Metric | Formula | Implementation | Formula equivalence |",
        "|---|---|---|---|",
        "| Absolute Difference | `abs(L - R)` | `src/features/symmetry.py:absolute_difference` | Verified equivalent |",
        "| Percent Difference | `100 * abs(L - R) / ((abs(L) + abs(R)) / 2)` | `src/features/symmetry.py:percent_difference` | Verified equivalent |",
        "| Symmetry Index | `100 * (L - R) / ((abs(L) + abs(R)) / 2)` | `src/features/symmetry.py:symmetry_index` | Verified equivalent |",
        "",
        "## Every Exported Feature",
        "",
        "| Feature | Formula | Units | Source signal | Equivalence of formula | Upstream measurement equivalence |",
        "|---|---|---|---|---|---|",
    ]
    for definition in FeatureExtractor().definitions:
        rows.append(
            f"| `{definition.name}` | `{_md(definition.formula)}` | {_md(definition.units)} | {_md(_source_signal(definition.name))} | Verified equivalent | Unknown / not established |"
        )
    rows.extend([
        "",
        "## Formula Recovery Conclusion",
        "",
        "The feature formulas themselves are recovered and verified equivalent across the current reference-feature and JumpGuard-feature code paths. This does not establish equivalence of the raw angle signals that feed those formulas.",
    ])
    return "\n".join(rows) + "\n"


def render_scientific_equivalence_matrix() -> str:
    rows = [
        "# Scientific Equivalence Matrix",
        "",
        "Classification terms: Verified Equivalent, Equivalent after transformation, Unknown, Not Equivalent.",
        "",
        "| Measurement level | Hip | Knee | Ankle | Symmetry features | Evidence |",
        "|---|---|---|---|---|---|",
        "| Feature names | Verified Equivalent | Verified Equivalent | Verified Equivalent | Verified Equivalent | Shared 57-feature schema enforced by code. |",
        "| Units | Verified Equivalent for exported degrees/seconds/percent | Verified Equivalent for exported degrees/seconds/percent | Verified Equivalent for exported degrees/seconds/percent | Verified Equivalent | Dataset header `inDegrees=yes`; JumpGuard angles are degrees. |",
        "| Raw landmarks / segment sources | Not Equivalent | Not Equivalent | Not Equivalent | Unknown via upstream ROM | Dataset stores IK columns; JumpGuard uses MediaPipe triplets. |",
        "| Coordinate system | Unknown | Unknown | Unknown | Unknown | Dataset coordinate system unrecovered; JumpGuard MediaPipe coordinates documented. |",
        "| Angle convention | Unknown | Unknown | Unknown | Unknown | Dataset sign/range/internal-external conventions unrecovered. |",
        "| Required transformation | Unknown | Unknown | Unknown | Unknown | No evidence supports inversion, sign flip, offset, or event window. |",
        "| Aggregation formulas | Verified Equivalent | Verified Equivalent | Verified Equivalent | Verified Equivalent | Prompt 3/P11 code formulas match. |",
        "| Event/window definition | Verified Equivalent for current full-recording features; Unknown for event-based future features | Verified Equivalent for current full-recording features; Unknown for event-based future features | Verified Equivalent for current full-recording features; Unknown for event-based future features | Verified Equivalent for current full-recording ROM inputs | Event fields are not used; current features are full-recording. |",
        "| Overall scientific equivalence | Unknown | Unknown | Unknown | Unknown / formula-only equivalence | Upstream IK methodology is unrecovered. |",
        "",
        "## Feature-Level Matrix",
        "",
        "| Feature | Formula | Raw measurement source | Event/window | Overall classification |",
        "|---|---|---|---|---|",
    ]
    for definition in FeatureExtractor().definitions:
        rows.append(
            f"| `{definition.name}` | Verified Equivalent | Unknown | Verified Equivalent for full recording | Unknown |"
        )
    return "\n".join(rows) + "\n"


def render_unknowns_register() -> str:
    unknowns = [
        ("Original publication / DOI / repository", "Needed for authoritative methods and licensing.", "Yes", "Potentially recoverable by obtaining source dataset citation from provider."),
        ("Motion-capture hardware", "Affects marker accuracy, sampling, event detection, and force data availability.", "Partially", "Could be recovered from publication or lab protocol."),
        ("Force-plate availability and thresholds", "Required for initial contact, toe off, stance, and landing phase definitions if events were force based.", "Yes for event harmonization", "Could be recovered from methods or raw acquisition files."),
        ("OpenSim model name and version", "Defines joint frames, coordinates, constraints, and anatomical zero.", "Yes for angle harmonization", "Could be recovered from `.osim` model or methods."),
        ("Static calibration and scaling workflow", "Defines subject-specific segment geometry and anatomical coordinate systems.", "Yes for exact IK reconstruction", "Could be recovered from scale setup files or methods."),
        ("Marker placement protocol", "Determines anatomical meaning and IK marker mapping.", "Yes for exact IK reconstruction", "Could be recovered from lab protocol or publication."),
        ("IK marker weights", "Affects solved joint coordinates.", "Yes for exact numerical reconstruction", "Could be recovered from IK setup XML."),
        ("IK solver tolerances and thresholds", "Affects solution quality and reproducibility.", "Partially", "Could be recovered from setup/log files."),
        ("Filtering / smoothing / interpolation", "Affects extrema, variance, ROM, and time-to-peak.", "Yes for numerical harmonization", "Could be recovered from scripts/methods; may be experimentally approximated but not proven."),
        ("Event suffixes K and A", "Determines whether `IC_*` fields can define landing windows.", "Yes for event-based harmonization", "Could be recovered from data dictionary or author clarification."),
        ("Angle sign and range conventions", "Determines whether transformations such as sign flip or `180 - angle` are needed.", "Yes", "Could be recovered from model coordinate definitions and paired validation."),
        ("Trial trimming criteria", "Defines what full recording contains and whether phases are comparable.", "Partially", "Could be recovered from preprocessing scripts or raw files."),
    ]
    rows = [
        "# Unknowns Register",
        "",
        "| Unknown | Why it matters | Blocks harmonization? | Can it later be experimentally inferred? |",
        "|---|---|---|---|",
    ]
    rows.extend(f"| {_md(a)} | {_md(b)} | {_md(c)} | {_md(d)} |" for a, b, c, d in unknowns)
    rows.extend([
        "",
        "## Principle",
        "",
        "Unknowns must remain unknown until tied to a published source, dataset documentation, setup file, raw acquisition file, or validated paired reconstruction. Experimental inference may suggest a transformation, but it does not replace documentary evidence unless validated prospectively.",
    ])
    return "\n".join(rows) + "\n"


def render_harmonization_readiness() -> str:
    return """# Harmonization Readiness

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
"""


def _coordinate_table() -> str:
    rows = [
        "| Coordinate group | Labels recovered | Evidence |",
        "|---|---|---|",
        "| Time | `time` | IK label workbook row 12 |",
        "| Pelvis translations/rotations | `pelvis_list`, `pelvis_tilt`, `pelvis_rotation`, `pelvis_tx`, `pelvis_ty`, `pelvis_tz` | IK label workbook row 12 |",
        "| Right lower limb | `hip_flexion_r`, `hip_adduction_r`, `hip_rotation_r`, `knee_angle_r`, `knee_adduction_r`, `knee_rotation_r`, `knee_angle_r_beta`, `ankle_angle_r`, `subtalar_angle_r`, `mtp_angle_r` | IK label workbook row 12 |",
        "| Left lower limb | `hip_flexion_l`, `hip_adduction_l`, `hip_rotation_l`, `knee_angle_l`, `knee_adduction_l`, `knee_rotation_l`, `knee_angle_l_beta`, `ankle_angle_l`, `subtalar_angle_l`, `mtp_angle_l` | IK label workbook row 12 |",
        "| Lumbar | `lumbar_extension`, `lumbar_bending`, `lumbar_rotation` | IK label workbook row 12 |",
        "| Upper limbs | arm, elbow, forearm, wrist coordinates for both sides | IK label workbook row 12 |",
    ]
    return "\n".join(rows)


def _source_signal(feature: str) -> str:
    for signal in PRIMARY_JOINT_SIGNALS:
        if feature.startswith(signal.key):
            return f"dataset `{signal.label}` / JumpGuard `{signal.key}`"
    for pair in PRIMARY_JOINT_PAIRS:
        if feature.startswith(pair.key):
            return f"ROM pair `{pair.left_label}` and `{pair.right_label}`"
    return UNKNOWN


def _md(value: Any) -> str:
    return str(value).replace("|", "\\|")


if __name__ == "__main__":
    paths = generate_methodology_recovery_docs()
    for value in paths.__dict__.values():
        print(value)
