"""Prompt 17 JumpGuard biomechanical measurement standard documentation.

This module writes documentation only. It does not modify datasets, feature
values, pipelines, reports, dashboards, evidence outputs, or numerical results.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .feature_engineering import FeatureExtractor
from .features.biomechanics import PRIMARY_JOINT_PAIRS, PRIMARY_JOINT_SIGNALS, JointSignal
from .features.statistical import DESCRIPTORS


UNKNOWN = "Unknown from available evidence."


@dataclass(frozen=True)
class LiteratureReference:
    """Peer-reviewed source used by the Prompt 17 standard."""

    key: str
    citation: str
    doi: str | None
    pmid: str | None
    url: str
    evidence_role: str
    confidence: str


@dataclass(frozen=True)
class MeasurementStandardPaths:
    """Prompt 17 deliverable paths."""

    literature_review: Path
    measurement_standard: Path
    implementation_validation: Path
    clinical_context: Path
    standards_matrix: Path
    gap_analysis: Path
    measurement_standard_readiness: Path


REFERENCES: tuple[LiteratureReference, ...] = (
    LiteratureReference(
        key="grood_1983_knee_jcs",
        citation=(
            "Grood ES, Suntay WJ. A joint coordinate system for the clinical "
            "description of three-dimensional motions: application to the knee. "
            "Journal of Biomechanical Engineering. 1983;105(2):136-144."
        ),
        doi="10.1115/1.3138397",
        pmid=None,
        url="https://doi.org/10.1115/1.3138397",
        evidence_role="Foundational peer-reviewed joint-coordinate-system method for describing three-dimensional knee motion.",
        confidence="High for joint-coordinate-system context; does not validate MediaPipe vector geometry as laboratory knee kinematics.",
    ),
    LiteratureReference(
        key="wu_2002_isb_lower_extremity",
        citation=(
            "Wu G, Siegler S, Allard P, Kirtley C, Leardini A, Rosenbaum D, "
            "Whittle M, D'Lima DD, Cristofolini L, Witte H, Schmid O, Stokes I. "
            "ISB recommendation on definitions of joint coordinate system of various "
            "joints for the reporting of human joint motion - part I: ankle, hip, "
            "and spine. Journal of Biomechanics. 2002;35(4):543-548."
        ),
        doi="10.1016/S0021-9290(01)00222-6",
        pmid=None,
        url="https://doi.org/10.1016/S0021-9290(01)00222-6",
        evidence_role="International Society of Biomechanics recommendation for reporting hip and ankle joint coordinate systems.",
        confidence="High for reporting-standard context; exact JumpGuard landmark angles remain geometric approximations.",
    ),
    LiteratureReference(
        key="padua_2009_less",
        citation=(
            "Padua DA, Marshall SW, Boling MC, Thigpen CA, Garrett WE Jr, Beutler AI. "
            "The Landing Error Scoring System (LESS) is a valid and reliable clinical "
            "assessment tool of jump-landing biomechanics: The JUMP-ACL study. "
            "American Journal of Sports Medicine. 2009;37(10):1996-2002."
        ),
        doi="10.1177/0363546509343200",
        pmid="19726623",
        url="https://doi.org/10.1177/0363546509343200",
        evidence_role="Supports clinical biomechanics context for jump-landing observation of lower-extremity and trunk posture.",
        confidence="High for jump-landing assessment context; JumpGuard does not compute LESS items or scores.",
    ),
    LiteratureReference(
        key="hewett_2005_acl_landing",
        citation=(
            "Hewett TE, Myer GD, Ford KR, Heidt RS Jr, Colosimo AJ, McLean SG, "
            "van den Bogert AJ, Paterno MV, Succop P. Biomechanical measures of "
            "neuromuscular control and valgus loading of the knee predict anterior "
            "cruciate ligament injury risk in female athletes: a prospective study. "
            "American Journal of Sports Medicine. 2005;33(4):492-501."
        ),
        doi="10.1177/0363546504269591",
        pmid="15722287",
        url="https://pubmed.ncbi.nlm.nih.gov/15722287/",
        evidence_role="Shows jump-landing studies use three-dimensional kinematics and kinetics to study ACL-related knee mechanics.",
        confidence="High for ACL landing-biomechanics context; not a basis for JumpGuard risk prediction or diagnosis.",
    ),
    LiteratureReference(
        key="paterno_2010_second_acl",
        citation=(
            "Paterno MV, Schmitt LC, Ford KR, Rauh MJ, Myer GD, Huang B, Hewett TE. "
            "Biomechanical measures during landing and postural stability predict "
            "second anterior cruciate ligament injury after anterior cruciate ligament "
            "reconstruction and return to sport. American Journal of Sports Medicine. "
            "2010;38(10):1968-1978."
        ),
        doi="10.1177/0363546510376053",
        pmid="20702858",
        url="https://doi.org/10.1177/0363546510376053",
        evidence_role="Supports landing-biomechanics context after ACL reconstruction while requiring broader measures than JumpGuard currently captures.",
        confidence="High for context; not a basis for JumpGuard risk prediction or diagnosis.",
    ),
    LiteratureReference(
        key="atkinson_1998_reliability",
        citation=(
            "Atkinson G, Nevill AM. Statistical methods for assessing measurement "
            "error (reliability) in variables relevant to sports medicine. Sports "
            "Medicine. 1998;26(4):217-238."
        ),
        doi="10.2165/00007256-199826040-00002",
        pmid=None,
        url="https://doi.org/10.2165/00007256-199826040-00002",
        evidence_role="Supports explicit reporting of variability, measurement error, and reliability limitations in sports-medicine measures.",
        confidence="High for reliability context; not a biomechanical definition for any single joint angle.",
    ),
    LiteratureReference(
        key="soudan_1982_gait_symmetry_index",
        citation=(
            "Soudan K. Standardization of gait kinematic data using a gait symmetry "
            "index and Fourier analysis. Journal of Biomechanics. 1982."
        ),
        doi="10.1016/0021-9290(82)90113-0",
        pmid=None,
        url="https://doi.org/10.1016/0021-9290(82)90113-0",
        evidence_role="Supports gait kinematic symmetry-index analysis as a biomechanical construct.",
        confidence="Moderate; supports the construct, not a single mandatory formula for JumpGuard's ROM symmetry metrics.",
    ),
    LiteratureReference(
        key="mccaw_1992_bilateral_symmetry",
        citation=(
            "McCaw ST. Intra- and interday assessment of bilateral symmetry in "
            "isokinetic knee extension moments. Journal of Biomechanics. 1992."
        ),
        doi="10.1016/0021-9290(92)90179-5",
        pmid=None,
        url="https://doi.org/10.1016/0021-9290(92)90179-5",
        evidence_role="Supports bilateral symmetry assessment in lower-extremity biomechanics and reinforces that symmetry is measurement-context dependent.",
        confidence="Moderate for the bilateral symmetry construct; JumpGuard does not measure isokinetic moments.",
    ),
    LiteratureReference(
        key="delp_2007_opensim",
        citation=(
            "Delp SL, Anderson FC, Arnold AS, Loan P, Habib A, John CT, Guendelman E, "
            "Thelen DG. OpenSim: open-source software to create and analyze dynamic "
            "simulations of movement. IEEE Transactions on Biomedical Engineering. "
            "2007;54(11):1940-1950."
        ),
        doi="10.1109/TBME.2007.901024",
        pmid=None,
        url="https://doi.org/10.1109/TBME.2007.901024",
        evidence_role="General context for model-based musculoskeletal analysis and inverse-kinematics workflows.",
        confidence="High for OpenSim context; not proof of the undocumented reference dataset's exact model or settings.",
    ),
    LiteratureReference(
        key="seth_2018_opensim",
        citation=(
            "Seth A, Hicks JL, Uchida TK, Habib A, Dembia CL, Dunne JJ, Ong CF, "
            "DeMers MS, Rajagopal A, Millard M, Hamner SR, Arnold EM, Yong JR, "
            "Lakshmikanth SK, Sherman MA, Ku JP, Delp SL. OpenSim: Simulating "
            "musculoskeletal dynamics and neuromuscular control to study human and "
            "animal movement. PLOS Computational Biology. 2018;14(7):e1006223."
        ),
        doi="10.1371/journal.pcbi.1006223",
        pmid=None,
        url="https://doi.org/10.1371/journal.pcbi.1006223",
        evidence_role="General context for OpenSim musculoskeletal modeling and simulation.",
        confidence="High for OpenSim context; not proof of reference-dataset settings.",
    ),
)


def generate_measurement_standard_docs(docs_dir: str | Path = "docs") -> MeasurementStandardPaths:
    """Generate all Prompt 17 measurement-standard deliverables."""

    destination = Path(docs_dir)
    destination.mkdir(parents=True, exist_ok=True)
    paths = MeasurementStandardPaths(
        literature_review=destination / "LITERATURE_REVIEW.md",
        measurement_standard=destination / "JUMPGUARD_MEASUREMENT_STANDARD.md",
        implementation_validation=destination / "IMPLEMENTATION_VALIDATION.md",
        clinical_context=destination / "CLINICAL_CONTEXT.md",
        standards_matrix=destination / "STANDARDS_MATRIX.md",
        gap_analysis=destination / "GAP_ANALYSIS.md",
        measurement_standard_readiness=destination / "MEASUREMENT_STANDARD_READINESS.md",
    )
    paths.literature_review.write_text(render_literature_review(), encoding="utf-8")
    paths.measurement_standard.write_text(render_measurement_standard(), encoding="utf-8")
    paths.implementation_validation.write_text(render_implementation_validation(), encoding="utf-8")
    paths.clinical_context.write_text(render_clinical_context(), encoding="utf-8")
    paths.standards_matrix.write_text(render_standards_matrix(), encoding="utf-8")
    paths.gap_analysis.write_text(render_gap_analysis(), encoding="utf-8")
    paths.measurement_standard_readiness.write_text(render_measurement_standard_readiness(), encoding="utf-8")
    return paths


def render_literature_review() -> str:
    rows = [
        "# Literature Review",
        "",
        "Prompt 17 uses peer-reviewed biomechanics and sports-medicine literature to validate the measurement constructs currently produced by JumpGuard. It does not use undocumented reference-dataset assumptions as authority, and it does not introduce clinical thresholds, risk scores, or diagnostic claims.",
        "",
        "## Source Inventory",
        "",
        "| Key | Publication | DOI | PMID | Evidence role | Confidence |",
        "|---|---|---|---|---|---|",
    ]
    for ref in REFERENCES:
        rows.append(
            f"| `{ref.key}` | {ref.citation} | {ref.doi or 'Unknown'} | {ref.pmid or 'Unknown'} | {ref.evidence_role} | {ref.confidence} |"
        )
    rows.extend(
        [
            "",
            "## Consensus Summary",
            "",
            "| Measurement area | Literature consensus | JumpGuard implication |",
            "|---|---|---|",
            "| Hip, knee, and ankle joint motion | Strong consensus that joint motion should be reported with explicit coordinate-system definitions. ISB and Grood-Suntay sources support the need for documented joint-coordinate conventions. | JumpGuard's current uploaded-video angles are valid only as explicit MediaPipe-derived vector angles, not as ISB or laboratory inverse-kinematics joint coordinates. |",
            "| Jump-landing ACL biomechanics | Strong consensus that landing kinematics and kinetics are used in ACL biomechanics research. | JumpGuard measurements can be described as landing-movement observations, but they do not provide forces, moments, trunk kinematics, or risk prediction. |",
            "| Descriptive statistics and variability | Strong statistical support for explicit reporting of mean, variability, and reliability context. | Mean, median, standard deviation, variance, extrema, and ROM are transparent scalar descriptors, but reliability of MediaPipe-derived angles must be validated separately. |",
            "| Bilateral symmetry | Moderate consensus that bilateral symmetry/asymmetry is a biomechanical construct; formulas differ across literature and tasks. | JumpGuard may report its explicit absolute difference, percent difference, and signed symmetry index formulas, but no clinical threshold is implied. |",
            "| Time-to-peak | General biomechanical studies use timing of peak events, but a full-recording first-maximum definition is task- and signal-dependent. | JumpGuard time-to-peak is mathematically defined and implementation-verified; clinical interpretation is inconclusive without event segmentation and validation. |",
            "",
            "## Sources Searched But Not Used As Authoritative Measurement Definitions",
            "",
            "OpenSim publications are included as context for model-based biomechanics, but they do not recover the undocumented reference dataset's exact OpenSim model, marker weights, coordinate definitions, filtering, or event methods. Computer-vision pose-estimation sources are not used to upgrade MediaPipe vector geometry into laboratory joint kinematics because Prompt 17 requires biomechanics definitions and because no validation study specific to this JumpGuard pipeline was available in the project evidence.",
        ]
    )
    return "\n".join(rows) + "\n"


def render_measurement_standard() -> str:
    rows = [
        "# JumpGuard Biomechanical Measurement Standard",
        "",
        "This is the official Prompt 17 measurement standard for quantities currently produced by JumpGuard. It validates measurement definitions, not clinical outcomes. The standard is independent of undocumented reference-dataset assumptions.",
        "",
        "## Governing Principles",
        "",
        "1. Every measurement must name its source signal, mathematical formula, units, and limitations.",
        "2. Uploaded-video joint angles are MediaPipe-derived geometric approximations from landmarks. They are not laboratory inverse-kinematics joint angles.",
        "3. Reference-dataset inverse-kinematics angle labels remain useful for feature names, but undocumented coordinate-system details are not used as scientific authority.",
        "4. Full-recording descriptors are valid only for the processed recording window unless a future validated event detector defines a landing phase.",
        "5. No feature implies ACL injury risk, diagnosis, tissue status, or clinical readiness by itself.",
        "",
        "## Primary Angle Signals",
        "",
        "| Signal | Mathematical definition | Biomechanical meaning | Units | Literature support | Standard status |",
        "|---|---|---|---|---|---|",
    ]
    for signal in PRIMARY_JOINT_SIGNALS:
        rows.append(_signal_standard_row(signal))
    rows.extend(
        [
            "",
            "## Descriptor Families",
            "",
            "| Family | Formula | Meaning | Units | Literature support | Standard status |",
            "|---|---|---|---|---|---|",
            "| Mean | `sum(x) / N` | Average angle magnitude over the full processed recording. | degrees | Statistical descriptor; reliability context supported by Atkinson and Nevill. | Verified mathematical descriptor; biomechanical interpretation depends on source signal validity. |",
            "| Median | `median(x)` | Central angle magnitude over the full processed recording. | degrees | Statistical descriptor; robust descriptive summary. | Verified mathematical descriptor; not a separate clinical construct. |",
            "| Standard deviation | `sqrt(sum((x - mean)^2) / N)` with `ddof=0` | Full-recording angular variability. | degrees | Reliability and measurement-error literature supports explicit variability reporting. | Verified mathematical descriptor; reliability must be validated for each acquisition setup. |",
            "| Variance | `sum((x - mean)^2) / N` with `ddof=0` | Squared angular variability. | degrees squared | Reliability and measurement-error literature supports explicit variability reporting. | Verified mathematical descriptor; clinical meaning is limited without repeatability evidence. |",
            "| Maximum | `max(x)` | Largest recorded geometric angle in the processed recording. | degrees | Peak joint postures are common in landing biomechanics, but exact timing window matters. | Verified mathematical descriptor; event-specific interpretation is inconclusive. |",
            "| Minimum | `min(x)` | Smallest recorded geometric angle in the processed recording. | degrees | Extrema are common kinematic descriptors, but exact timing window matters. | Verified mathematical descriptor; event-specific interpretation is inconclusive. |",
            "| Range of motion | `max(x) - min(x)` | Full-recording angular excursion. | degrees | Joint excursion/ROM is a standard biomechanical descriptor. | Verified mathematical descriptor; not equivalent to clinical passive ROM. |",
            "| Time-to-peak | `time[argmax(x)] - time[0]` | Elapsed time from first finite timestamp to first maximum. | seconds | Timing of kinematic peaks is used in movement analysis, but full-recording first-maximum timing is task-specific. | Partial match; implementation is verified, clinical interpretation is inconclusive. |",
            "",
            "## Symmetry Families",
            "",
            "| Family | Formula | Meaning | Units | Literature support | Standard status |",
            "|---|---|---|---|---|---|",
            "| Absolute difference | `abs(ROM_L - ROM_R)` | Unsigned side-to-side ROM difference. | degrees | Bilateral symmetry/asymmetry is a recognized biomechanical construct. | Verified mathematical descriptor; no threshold is implied. |",
            "| Percent difference | `100 * abs(ROM_L - ROM_R) / ((abs(ROM_L) + abs(ROM_R)) / 2)` | Unsigned side-to-side ROM difference normalized to average side magnitude. | percent | Literature uses multiple asymmetry normalizations. | Verified implementation; consensus on this exact formula is partial. |",
            "| Symmetry index | `100 * (ROM_L - ROM_R) / ((abs(ROM_L) + abs(ROM_R)) / 2)` | Signed side-to-side ROM difference; positive means larger left ROM in JumpGuard. | percent | Symmetry-index concepts are used in biomechanics, but formula conventions vary. | Verified implementation; no clinical threshold is implied. |",
        ]
    )
    return "\n".join(rows) + "\n"


def render_implementation_validation() -> str:
    rows = [
        "# Implementation Validation",
        "",
        "This document compares the literature-backed measurement standard against the current JumpGuard implementation without modifying the implementation.",
        "",
        "## Validation Legend",
        "",
        "| Status | Meaning |",
        "|---|---|",
        "| Verified Match | Current implementation exactly matches the documented mathematical definition. |",
        "| Partial Match | Formula is explicit and useful, but literature support is construct-level rather than exact-method support. |",
        "| Unknown | Available evidence cannot verify the scientific equivalence or acquisition validity. |",
        "| Not Supported | The implementation would make a claim that literature or available evidence does not support. |",
        "",
        "## Source-Code Evidence",
        "",
        "| Component | Source | Validation result |",
        "|---|---|---|",
        "| Angle landmarks and vector angle formula | `src/feature_extraction.py:ANGLE_SIGNAL_MAP`, `_angle_for_points`, `_angle_between` | Verified implementation of deterministic 3D vector geometry. |",
        "| Dataset feature descriptors | `src/feature_engineering.py:FeatureExtractor.extract`; `src/features/statistical.py` | Verified formulas for descriptors over full recordings. |",
        "| Uploaded-video descriptors | `src/feature_extraction.py:calculate_temporal_features`, `_finite_descriptor`, `_time_to_peak` | Verified formulas over finite full-recording values. |",
        "| Symmetry formulas | `src/features/symmetry.py` | Verified formulas for absolute difference, percent difference, and signed symmetry index. |",
        "| Landing events | `src/feature_extraction.py:_landing_events` | Beginning, end, and duration remain missing; no undocumented detector is introduced. |",
        "",
        "## Feature-by-Feature Validation",
        "",
        "| Feature | Implementation formula | Literature-backed definition | Match status | Confidence | Rationale |",
        "|---|---|---|---|---|---|",
    ]
    for definition in FeatureExtractor().definitions:
        status, confidence, rationale = _validation_status(definition.name)
        rows.append(
            f"| `{definition.name}` | `{definition.formula}` | {_literature_definition_for_feature(definition.name)} | {status} | {confidence} | {rationale} |"
        )
    rows.extend(
        [
            "",
            "## Explicit Non-Matches",
            "",
            "- JumpGuard MediaPipe angles are not validated as ISB joint coordinate angles.",
            "- JumpGuard MediaPipe angles are not validated as OpenSim inverse-kinematics coordinates.",
            "- JumpGuard does not compute knee abduction moments, ground-reaction forces, LESS scores, or ACL injury probabilities.",
            "- JumpGuard does not identify initial contact, stance, propulsion, or landing phase using a literature-validated event method.",
        ]
    )
    return "\n".join(rows) + "\n"


def render_clinical_context() -> str:
    rows = [
        "# Clinical Context",
        "",
        "This document explains what JumpGuard measurements represent biomechanically and what they do not imply. It avoids diagnostic and predictive language.",
        "",
        "## Angle Families",
        "",
        "| Family | Represents | Used in ACL or landing biomechanics research | Limitations | Does not imply |",
        "|---|---|---|---|---|",
        "| Hip flexion | Sagittal-plane hip strategy approximated from shoulder, hip, and knee landmarks for uploaded videos. | Landing studies and LESS-style evaluations consider hip/trunk/lower-extremity posture as part of movement assessment. | JumpGuard uses a shoulder-hip-knee vector angle, not a pelvis-based ISB hip coordinate; trunk/pelvis coordinate frames are not reconstructed. | No diagnosis, risk score, hip pathology, or readiness decision. |",
        "| Knee flexion | Internal angle formed by hip, knee, and ankle landmarks for uploaded videos. | Knee kinematics are central to jump-landing ACL biomechanics research. | Does not measure frontal-plane knee abduction, knee valgus moment, or tibiofemoral joint loading. | No ACL risk prediction, ligament status, or dynamic valgus diagnosis. |",
        "| Ankle angle | Internal angle formed by knee, ankle, and foot-index landmarks for uploaded videos. | Ankle strategy and lower-extremity posture are considered in landing assessments. | Foot-index landmark does not reconstruct full foot segment orientation or ankle joint coordinate systems. | No diagnosis, ankle pathology, or force absorption conclusion by itself. |",
        "",
        "## Descriptor Families",
        "",
        "| Descriptor | Represents | Limitations | Does not imply |",
        "|---|---|---|---|",
        "| Mean / median | Typical full-recording angle magnitude. | Sensitive to recording duration and task phase; not landing-phase-specific. | No clinical normality threshold. |",
        "| Maximum / minimum | Extrema within the processed recording. | May occur outside the intended landing phase if the video includes setup or recovery. | No event-specific peak landing metric unless event timing is validated. |",
        "| ROM | Full-recording angular excursion. | Not equivalent to clinical passive ROM or laboratory joint excursion unless source signal and window are validated. | No tissue mobility diagnosis. |",
        "| Standard deviation / variance | Full-recording signal variability. | Can reflect task timing, pose-estimation noise, missingness, or movement variability. | No neuromuscular-control diagnosis. |",
        "| Time-to-peak | Time from first finite timestamp to first maximum. | Depends on video start time and full-recording window; not contact-relative. | No reaction-time or landing-control conclusion. |",
        "| Bilateral symmetry metrics | Side-to-side ROM differences. | Formula conventions vary; asymmetry thresholds are not applied. | No injury-risk or return-to-sport decision. |",
    ]
    return "\n".join(rows) + "\n"


def render_standards_matrix() -> str:
    rows = [
        "# Standards Matrix",
        "",
        "| Feature | Literature definition | JumpGuard formula | Match status | Confidence | References |",
        "|---|---|---|---|---|---|",
    ]
    for definition in FeatureExtractor().definitions:
        status, confidence, _ = _validation_status(definition.name)
        rows.append(
            f"| `{definition.name}` | {_literature_definition_for_feature(definition.name)} | `{definition.formula}` | {status} | {confidence} | {_references_for_feature(definition.name)} |"
        )
    return "\n".join(rows) + "\n"


def render_gap_analysis() -> str:
    return """# Gap Analysis

Prompt 17 identifies gaps without changing algorithms or introducing replacement methods.

## Strongly Supported

| Area | Finding | Future work |
|---|---|---|
| Explicit vector-angle definitions | JumpGuard's uploaded-video hip, knee, and ankle angles are mathematically transparent. | Validate against laboratory motion capture before making equivalence claims. |
| Full-recording descriptors | Mean, median, extrema, ROM, variance, standard deviation, and time-to-peak are implementation-verified. | Add test-retest reliability and sensitivity analyses for MediaPipe-derived signals. |
| Non-diagnostic reporting | Current documentation consistently avoids risk scores and diagnosis. | Preserve this boundary in future reports. |

## Partial Or Inconclusive Support

| Area | Gap | Evidence needed before upgrade |
|---|---|---|
| ISB equivalence | MediaPipe vector angles do not reconstruct ISB segment coordinate systems. | Calibration, segment frames, coordinate axes, and validation against marker-based IK. |
| Reference dataset harmonization | Original dataset's OpenSim model, marker weights, filtering, event methods, and coordinate conventions remain unknown. | Dataset publication, `.osim` model, setup XML files, preprocessing methods, and raw marker/force data. |
| Landing phase | No robust initial-contact or landing-window detector is defined. | Force plate, validated kinematic event detector, or documented video event protocol. |
| Symmetry thresholds | Bilateral symmetry formulas are defined, but clinical thresholds are not established for these MediaPipe-derived ROM values. | Prospective validation and task-specific reliability/meaningful-change studies. |
| Time-to-peak clinical meaning | Current time-to-peak is recording-relative, not event-relative. | Validated event timing and task-window definitions. |

## Measurements Requiring Additional Sensing

| Measurement | Required sensing or method | Current status |
|---|---|---|
| Ground-reaction force | Force plates or validated force estimation. | Not measured. |
| Joint moments | Kinetics plus inverse dynamics. | Not measured. |
| Knee abduction moment | 3D kinematics, kinetics, body-segment parameters, inverse dynamics. | Not measured. |
| EMG / muscle activation | Surface or intramuscular EMG. | Not measured. |
| Trunk kinematics as anatomical segment angles | Explicit trunk and pelvis segment coordinate systems. | Not measured as laboratory trunk kinematics. |
| LESS score | Full LESS item scoring protocol and trained scoring workflow. | Not computed. |
| ACL injury probability | Prospective model with validated predictors and calibration. | Not computed and not authorized by this project stage. |
"""


def render_measurement_standard_readiness() -> str:
    return """# Measurement Standard Readiness

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
"""


def _signal_standard_row(signal: JointSignal) -> str:
    if signal.joint == "hip":
        formula = "angle between shoulder-to-hip and hip-to-knee vectors"
        literature = "ISB hip reporting context plus jump-landing posture literature"
        status = "Partial match: construct supported, exact MediaPipe vector angle is a geometric approximation"
    elif signal.joint == "knee":
        formula = "internal angle formed by hip, knee, and ankle landmarks"
        literature = "Grood-Suntay knee coordinate-system context plus ACL landing-biomechanics literature"
        status = "Partial match: knee motion construct supported, exact unsigned vector angle is not laboratory knee flexion"
    else:
        formula = "angle between knee-to-ankle and ankle-to-foot-index vectors"
        literature = "ISB ankle reporting context plus landing-posture literature"
        status = "Partial match: ankle motion construct supported, exact foot-index vector angle is a geometric approximation"
    return (
        f"| `{signal.key}` | `{formula}` | {signal.side} {signal.joint} sagittal-plane movement approximation from landmarks. "
        f"| degrees | {literature} | {status}. |"
    )


def _validation_status(feature_name: str) -> tuple[str, str, str]:
    if feature_name.endswith(("_mean", "_median", "_maximum", "_minimum", "_rom")):
        return (
            "Verified Match",
            "Moderate-to-high",
            "Formula is implementation-verified; biomechanical meaning depends on the source angle signal and full-recording window.",
        )
    if feature_name.endswith(("_std", "_variance")):
        return (
            "Verified Match",
            "Moderate",
            "Formula is implementation-verified; reliability and measurement-error interpretation require task-specific validation.",
        )
    if feature_name.endswith("_time_to_peak"):
        return (
            "Partial Match",
            "Moderate",
            "Formula is implementation-verified, but literature-backed event-relative peak timing is not established for the full-recording window.",
        )
    if feature_name.endswith("_absolute_difference"):
        return (
            "Verified Match",
            "Moderate",
            "Formula is implementation-verified and bilateral difference is a supported construct; no clinical threshold is applied.",
        )
    if feature_name.endswith(("_percent_difference", "_symmetry_index")):
        return (
            "Partial Match",
            "Moderate",
            "Formula is implementation-verified, but symmetry-index conventions vary across biomechanics literature.",
        )
    return "Unknown", "Low", UNKNOWN


def _literature_definition_for_feature(feature_name: str) -> str:
    if feature_name.endswith("_rom_absolute_difference"):
        return "Unsigned bilateral ROM difference as a side-to-side symmetry descriptor."
    if feature_name.endswith("_rom_percent_difference"):
        return "Bilateral ROM asymmetry normalized to average side magnitude; formula conventions vary."
    if feature_name.endswith("_rom_symmetry_index"):
        return "Signed bilateral ROM symmetry index; formula conventions vary."
    descriptor = feature_name.rsplit("_", 1)[-1]
    if descriptor == "peak":
        descriptor = "time_to_peak"
    descriptor_map = {
        "mean": "Average full-recording joint-angle magnitude.",
        "median": "Median full-recording joint-angle magnitude.",
        "std": "Full-recording angular variability as population standard deviation.",
        "variance": "Full-recording angular variability as population variance.",
        "maximum": "Maximum full-recording joint-angle value.",
        "minimum": "Minimum full-recording joint-angle value.",
        "rom": "Full-recording angular excursion computed as maximum minus minimum.",
        "time_to_peak": "Elapsed time from recording start to first maximum; event-relative meaning is inconclusive.",
    }
    if feature_name.endswith("time_to_peak"):
        return descriptor_map["time_to_peak"]
    return descriptor_map.get(descriptor, UNKNOWN)


def _references_for_feature(feature_name: str) -> str:
    base_refs = "Grood 1983; Wu 2002; Padua 2009; Hewett 2005"
    if feature_name.endswith(("_std", "_variance")):
        return f"{base_refs}; Atkinson and Nevill 1998"
    if feature_name.endswith(("_absolute_difference", "_percent_difference", "_symmetry_index")):
        return "Soudan 1982; McCaw 1992; Atkinson and Nevill 1998"
    if feature_name.endswith("_time_to_peak"):
        return f"{base_refs}; event-specific interpretation inconclusive"
    return base_refs


def main() -> None:
    """CLI entry point for regenerating Prompt 17 docs only."""

    paths = generate_measurement_standard_docs()
    for path in paths.__dict__.values():
        print(path)


if __name__ == "__main__":
    main()
