"""Prompt 18 healthy normative reference dataset discovery docs.

This module writes documentation only. It does not modify datasets, feature
values, pipelines, reports, dashboards, evidence outputs, or numerical results.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


UNKNOWN = "Unknown from available evidence."


@dataclass(frozen=True)
class CandidateDataset:
    """Public candidate screened for Prompt 18 normative-reference planning."""

    key: str
    name: str
    source_type: str
    source: str
    publication: str
    doi_or_url: str
    population: str
    sample_size: str
    age: str
    sex: str
    healthy_definition: str
    landing_task: str
    camera_view: str
    frame_rate: str
    resolution: str
    license: str
    downloadable_videos: str
    documentation_quality: str
    compatibility: str
    rank: str
    recommendation: str


@dataclass(frozen=True)
class NormativeDiscoveryPaths:
    """Prompt 18 deliverable paths."""

    healthy_dataset_survey: Path
    dataset_compatibility: Path
    normative_reference_plan: Path
    statistical_reference_protocol: Path
    processing_pipeline: Path
    future_validation_roadmap: Path
    dataset_recommendations: Path


CANDIDATES: tuple[CandidateDataset, ...] = (
    CandidateDataset(
        key="finegym",
        name="FineGym",
        source_type="Official project page plus CVPR paper",
        source="https://sdolivia.github.io/FineGym/",
        publication="Shao D, Zhao Y, Dai B, Lin D. FineGym: A Hierarchical Video Dataset for Fine-grained Action Understanding. CVPR 2020.",
        doi_or_url="https://arxiv.org/abs/2004.06704",
        population="Competitive gymnasts in public competition videos; health status not documented.",
        sample_size="Large annotation corpus; exact usable landing-like clip count for JumpGuard is unknown until annotations are filtered and videos are retrievable.",
        age="Unknown from available evidence.",
        sex="Unknown from available evidence.",
        healthy_definition="Unknown; dataset is not a healthy normative biomechanics cohort.",
        landing_task="Gymnastics vault, floor exercise, beam dismounts, and leap/jump/hop categories contain landing-like actions, but not standardized drop jumps.",
        camera_view="Broadcast/competition views; view angle varies by event and video.",
        frame_rate="Unknown from available evidence; source videos are YouTube/broadcast-derived.",
        resolution="Unknown from available evidence; source videos vary.",
        license="Annotations are CC BY-NC 4.0 according to the official page; underlying YouTube video rights are separate and must be verified.",
        downloadable_videos="Annotations downloadable; videos are referenced by YouTube identifiers and may be missing or require a request form.",
        documentation_quality="High for temporal action annotations; incomplete for participant health, age, sex, camera calibration, and recording metadata.",
        compatibility="Conditional pilot only. Landing-like segments may stress MediaPipe because the official page reports pose-estimation misses in intense gymnastics motion.",
        rank="1 for pilot screening; not acceptable as production healthy normative reference.",
        recommendation="Use only for a small feasibility pilot of landing-like clips after manual QC and rights review. Do not use for normative statistics.",
    ),
    CandidateDataset(
        key="ntu_rgbd",
        name="NTU RGB+D / NTU RGB+D 120",
        source_type="Peer-reviewed dataset papers plus official dataset URL cited by authors",
        source="http://rose1.ntu.edu.sg/Datasets/actionRecognition.asp",
        publication="Shahroudy A, Liu J, Ng TT, Wang G. NTU RGB+D: A Large Scale Dataset for 3D Human Activity Analysis. CVPR 2016. Liu J et al. NTU RGB+D 120: A Large-Scale Benchmark for 3D Human Activity Understanding. 2019.",
        doi_or_url="https://arxiv.org/abs/1604.02808; https://arxiv.org/abs/1905.04757",
        population="40 subjects in NTU RGB+D and 106 subjects in NTU RGB+D 120 according to the papers; health status not documented as a healthy biomechanics cohort.",
        sample_size="56,000+ samples for NTU RGB+D and 114,000+ samples for NTU RGB+D 120; usable jump/landing count unknown until official labels are filtered.",
        age="Unknown from available evidence.",
        sex="Unknown from available evidence.",
        healthy_definition="Unknown; dataset is an activity-recognition benchmark, not a screened healthy normative dataset.",
        landing_task="Possible jump/hop activity-recognition samples require verification from official downloaded label metadata; not standardized jump landing.",
        camera_view="Controlled RGB-D multi-view acquisition; exact sagittal suitability must be inspected per sample.",
        frame_rate="Unknown from available evidence in the sources reviewed for Prompt 18.",
        resolution="Unknown from available evidence in the sources reviewed for Prompt 18.",
        license="Unknown from available evidence; dataset terms must be checked at download/registration.",
        downloadable_videos="Dataset papers state availability through official project URL; current web access may require registration or working mirror verification.",
        documentation_quality="Moderate to high for activity-recognition metadata; incomplete for healthy normative biomechanics metadata.",
        compatibility="Conditional pilot only. Controlled camera and full-body RGB are promising, but task and subject health metadata are not normative-grade.",
        rank="2 for technical pilot if jump labels are verified; not acceptable as production healthy normative reference.",
        recommendation="Use only after official action labels, terms, video availability, and sagittal/full-body visibility are verified.",
    ),
    CandidateDataset(
        key="kinetics",
        name="Kinetics human action video datasets",
        source_type="Peer-reviewed dataset papers",
        source="https://arxiv.org/abs/1705.06950; https://arxiv.org/abs/2010.10864",
        publication="Kay W et al. The Kinetics Human Action Video Dataset. 2017. Smaira L et al. A Short Note on the Kinetics-700-2020 Human Action Dataset. 2020.",
        doi_or_url="https://arxiv.org/abs/1705.06950; https://arxiv.org/abs/2010.10864",
        population="Unscreened people in public YouTube videos; health status unknown.",
        sample_size="Hundreds of clips per action class in Kinetics releases; usable healthy jump-landing count unknown.",
        age="Unknown from available evidence.",
        sex="Unknown from available evidence.",
        healthy_definition="Unknown; not a health-screened dataset.",
        landing_task="Human action classes may include jump-related actions, but not standardized drop-jump or landing trials.",
        camera_view="In-the-wild YouTube videos; camera view, stability, occlusion, and scale vary substantially.",
        frame_rate="Unknown or source-dependent.",
        resolution="Unknown or source-dependent.",
        license="Underlying YouTube video rights and availability vary; dataset distribution is commonly metadata/URLs rather than guaranteed video files.",
        downloadable_videos="URL-based retrieval; many links may be unavailable over time.",
        documentation_quality="High for action-recognition benchmark design; low for biomechanics/normative metadata.",
        compatibility="Low-to-moderate for exploratory stress testing only; not controlled enough for normative reference statistics.",
        rank="3 for broad stress testing; reject for normative statistics.",
        recommendation="Do not use for normative reference. At most use as a robustness stress-test set after rights review.",
    ),
    CandidateDataset(
        key="ucf101",
        name="UCF101",
        source_type="Peer-reviewed dataset paper",
        source="https://arxiv.org/abs/1212.0402",
        publication="Soomro K, Zamir AR, Shah M. UCF101: A Dataset of 101 Human Action Classes From Videos in the Wild. 2012.",
        doi_or_url="https://arxiv.org/abs/1212.0402",
        population="Unscreened people in user-uploaded action videos; health status unknown.",
        sample_size="13,000+ clips across 101 action classes; usable jump-landing count unknown.",
        age="Unknown from available evidence.",
        sex="Unknown from available evidence.",
        healthy_definition="Unknown; not a healthy normative biomechanics cohort.",
        landing_task="Action-recognition clips may include jump-related activities, but no standardized landing protocol is documented.",
        camera_view="In-the-wild videos with camera motion and cluttered backgrounds according to the paper.",
        frame_rate="Unknown or source-dependent.",
        resolution="Unknown or source-dependent.",
        license="Unknown from available evidence; rights review required.",
        downloadable_videos="Public benchmark clips are historically downloadable, but current availability and terms require verification.",
        documentation_quality="Good for action recognition; poor for healthy biomechanics metadata.",
        compatibility="Low. Camera motion, clutter, and task heterogeneity make it unsuitable for normative JumpGuard statistics.",
        rank="4; reject for normative reference.",
        recommendation="Reject for normative reference; possible only as a negative-control or robustness set.",
    ),
    CandidateDataset(
        key="human36m_h3wb",
        name="Human3.6M / H3WB",
        source_type="Peer-reviewed dataset papers and derivative whole-body benchmark",
        source="https://arxiv.org/abs/2211.15692",
        publication="Ionescu C et al. Human3.6M. IEEE TPAMI 2014. Zhu Y, Samet N, Picard D. H3WB: Human3.6M 3D WholeBody Dataset and Benchmark. 2022.",
        doi_or_url="https://arxiv.org/abs/2211.15692",
        population="Actors/subjects in laboratory pose-estimation dataset; health status as normative athletes is unknown.",
        sample_size="H3WB reports 100K whole-body annotated images derived from Human3.6M; jump-landing usable count unknown and likely not task-aligned.",
        age="Unknown from available evidence.",
        sex="Unknown from available evidence.",
        healthy_definition="Unknown; not documented as healthy jump-landing normative cohort.",
        landing_task="No verified standardized jump-landing task from available evidence reviewed for Prompt 18.",
        camera_view="Controlled laboratory multi-view imagery.",
        frame_rate="Unknown from available evidence in reviewed sources.",
        resolution="Unknown from available evidence in reviewed sources.",
        license="Access terms and redistribution restrictions require verification.",
        downloadable_videos="May require dataset registration/terms; availability for JumpGuard processing must be verified.",
        documentation_quality="High for pose-estimation benchmarking; low for jump-landing normative design.",
        compatibility="Technically promising for pose estimation but task-incompatible for JumpGuard jump-landing normative reference.",
        rank="5; reject for Prompt 18 normative objective.",
        recommendation="Reject for normative jump-landing reference unless a verified jump-landing subset is documented.",
    ),
)


def generate_normative_dataset_discovery_docs(docs_dir: str | Path = "docs") -> NormativeDiscoveryPaths:
    """Generate all Prompt 18 discovery and planning deliverables."""

    destination = Path(docs_dir)
    destination.mkdir(parents=True, exist_ok=True)
    paths = NormativeDiscoveryPaths(
        healthy_dataset_survey=destination / "HEALTHY_DATASET_SURVEY.md",
        dataset_compatibility=destination / "DATASET_COMPATIBILITY.md",
        normative_reference_plan=destination / "NORMATIVE_REFERENCE_PLAN.md",
        statistical_reference_protocol=destination / "STATISTICAL_REFERENCE_PROTOCOL.md",
        processing_pipeline=destination / "PROCESSING_PIPELINE.md",
        future_validation_roadmap=destination / "FUTURE_VALIDATION_ROADMAP.md",
        dataset_recommendations=destination / "DATASET_RECOMMENDATIONS.md",
    )
    paths.healthy_dataset_survey.write_text(render_healthy_dataset_survey(), encoding="utf-8")
    paths.dataset_compatibility.write_text(render_dataset_compatibility(), encoding="utf-8")
    paths.normative_reference_plan.write_text(render_normative_reference_plan(), encoding="utf-8")
    paths.statistical_reference_protocol.write_text(render_statistical_reference_protocol(), encoding="utf-8")
    paths.processing_pipeline.write_text(render_processing_pipeline(), encoding="utf-8")
    paths.future_validation_roadmap.write_text(render_future_validation_roadmap(), encoding="utf-8")
    paths.dataset_recommendations.write_text(render_dataset_recommendations(), encoding="utf-8")
    return paths


def render_healthy_dataset_survey() -> str:
    rows = [
        "# Healthy Dataset Survey",
        "",
        "Prompt 18 screened public video datasets for future creation of a MediaPipe-derived JumpGuard normative reference. No videos were downloaded, no reports were regenerated, and no numerical outputs were changed.",
        "",
        "## Search Scope",
        "",
        "Sources searched included peer-reviewed dataset papers, official project pages, Figshare/Zenodo/PhysioNet-style repository searches, and documented action-recognition datasets where provenance was clear. The target was a public healthy jump-landing video dataset with enough metadata to support normative statistics generated by the existing JumpGuard pipeline.",
        "",
        "## Primary Finding",
        "",
        "No discovered public dataset satisfies all Prompt 18 requirements for a production healthy JumpGuard normative reference. Several datasets are useful for pilot screening or robustness testing, but each lacks at least one critical requirement: healthy cohort definition, standardized jump-landing task, stable sagittal camera view, clear video rights, complete participant metadata, or durable video availability.",
        "",
        "## Candidate Records",
        "",
        "| Dataset | Population | Sample size | Age | Sex | Healthy definition | Landing task | Camera view | Frame rate | Resolution | License | Downloadable videos | Documentation quality | Recommendation |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for candidate in CANDIDATES:
        rows.append(
            f"| {candidate.name} | {candidate.population} | {candidate.sample_size} | {candidate.age} | {candidate.sex} | {candidate.healthy_definition} | {candidate.landing_task} | {candidate.camera_view} | {candidate.frame_rate} | {candidate.resolution} | {candidate.license} | {candidate.downloadable_videos} | {candidate.documentation_quality} | {candidate.recommendation} |"
        )
    rows.extend([
        "",
        "## Traceability Sources",
        "",
    ])
    for candidate in CANDIDATES:
        rows.append(f"- {candidate.name}: {candidate.publication} Source: {candidate.source}. DOI/URL: {candidate.doi_or_url}.")
    return "\n".join(rows) + "\n"


def render_dataset_compatibility() -> str:
    rows = [
        "# Dataset Compatibility",
        "",
        "Compatibility is assessed against the existing JumpGuard pipeline only. No new pose model, event detector, segmentation algorithm, or feature calculation is proposed here.",
        "",
        "## Compatibility Matrix",
        "",
        "| Dataset | Sagittal view | Full-body visibility | Occlusion | Lighting | Motion blur | Foot visibility | Camera stability | Expected MediaPipe robustness | Pipeline status |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    compatibility_rows = {
        "finegym": (
            "Variable; often oblique/broadcast", "Variable", "Likely during flips/dismounts", "Broadcast quality but variable", "Likely in high-speed gymnastics", "Often uncertain", "Variable pans/zooms", "Conditional to poor for intense motion; official page notes pose-estimation misses", "Pilot only after manual QC"
        ),
        "ntu_rgbd": (
            "Potentially selectable from controlled views", "Likely better than in-the-wild datasets", "Low-to-moderate", "Controlled", "Unknown", "Must inspect RGB frames", "Stable", "Potentially moderate-to-high for simple jumps, if labels/video access are verified", "Pilot only"
        ),
        "kinetics": (
            "Uncontrolled", "Variable", "High variability", "Variable", "Variable", "Variable", "Variable", "Low-to-moderate; large manual rejection expected", "Stress testing only"
        ),
        "ucf101": (
            "Uncontrolled", "Variable", "High variability", "Variable", "Variable", "Variable", "Paper reports camera motion and clutter", "Low for normative use", "Reject for normative reference"
        ),
        "human36m_h3wb": (
            "Controlled but task mismatch", "Likely high", "Low", "Controlled", "Low-to-moderate", "Likely visible", "Stable", "Technically promising, but no verified jump-landing task", "Reject unless task subset is proven"
        ),
    }
    for candidate in CANDIDATES:
        rows.append(f"| {candidate.name} | " + " | ".join(compatibility_rows[candidate.key]) + " |")
    rows.extend(
        [
            "",
            "## Minimum QC Gate For Any Future Pilot",
            "",
            "A video may enter a future JumpGuard normative pilot only if all required MediaPipe landmarks for hip, knee, ankle, shoulder, and foot-index angle calculations are visible for most of the movement, the full body remains in frame, the camera is stable enough for repeated processing, and the landing-like movement can be identified from documented labels or manual review without inventing event timing.",
        ]
    )
    return "\n".join(rows) + "\n"


def render_normative_reference_plan() -> str:
    return """# Normative Reference Plan

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
"""


def render_statistical_reference_protocol() -> str:
    return """# Statistical Reference Protocol

This protocol defines future normative statistics only after videos have passed QC and have been processed by the existing JumpGuard pipeline without algorithmic changes.

## Feature Source

Use the existing 57-feature JumpGuard schema documented in `docs/JUMPGUARD_MEASUREMENT_STANDARD.md`. Do not add features, alter formulas, or reinterpret MediaPipe-derived geometric angles as laboratory inverse-kinematics angles.

## Per-Feature Reference Statistics

For every feature with sufficient finite observations, compute:

| Statistic | Definition |
|---|---|
| Count | Number of finite observations. |
| Missing count | Number of videos where the feature is missing or NaN. |
| Mean | Arithmetic mean. |
| Median | Median. |
| Standard deviation | Population and sample definitions must be explicitly stated; current project feature variance uses population `ddof=0`, but reference confidence intervals should state their estimator. |
| Percentiles | 1st, 2.5th, 5th, 25th, 50th, 75th, 95th, 97.5th, and 99th percentiles. |
| Central 90 percent interval | 5th to 95th percentile. |
| Central 95 percent interval | 2.5th to 97.5th percentile. |
| Confidence intervals | Bootstrap confidence intervals for the mean, median, and selected percentiles, with seed and resampling count documented. |

## Stratification

Stratification is allowed only when metadata are sufficiently documented and sample sizes are adequate. Candidate strata include sex/gender, age band, sport/activity level, task type, camera view, and dataset source. If metadata are missing, report unknown rather than pooling as healthy normative data.

## Sample-Size Recommendations

| Stage | Minimum target | Purpose |
|---|---|---|
| Feasibility pilot | 20 to 30 usable videos after QC | Validate pipeline throughput and missingness patterns only. |
| Preliminary normative reference | At least 100 usable healthy videos from a standardized protocol | Estimate broad distributions with uncertainty. |
| Robust stratified reference | At least 100 usable videos per planned stratum | Support subgroup summaries without unstable intervals. |

These are planning targets, not clinical thresholds. Final adequacy must be judged by missingness, interval width, repeatability, and whether participant/task metadata support the intended comparison.

## Missing Data Policy

Report feature-level missingness for every dataset and every stratum. Do not impute missing landmarks or features for normative statistics unless a future validated imputation protocol is explicitly approved.
"""


def render_processing_pipeline() -> str:
    rows = [
        "# Processing Pipeline",
        "",
        "Prompt 18 does not run processing. This is a future roadmap for processing candidate videos through the existing JumpGuard architecture only.",
        "",
        "## Ranked Candidate Roadmap",
        "",
        "| Rank | Dataset | Estimated usable videos | Expected feature coverage | Processing effort | Recommendation |",
        "|---|---|---|---|---|---|",
    ]
    estimates = {
        "finegym": ("Unknown until YouTube availability, event filters, and manual QC are complete", "Potentially partial due to high motion and occlusion", "High manual QC and rights review", "Pilot only"),
        "ntu_rgbd": ("Unknown until official action labels and download access are verified", "Potentially good for simple full-body jumps if labels exist and views are sagittal enough", "Moderate access verification and QC", "Technical pilot only"),
        "kinetics": ("Unknown and likely unstable over time due to URL rot", "Variable and noisy", "Very high manual filtering", "Reject for normative statistics"),
        "ucf101": ("Unknown", "Variable and noisy", "High manual filtering", "Reject for normative statistics"),
        "human36m_h3wb": ("Unknown; no verified jump-landing subset", "High pose quality if task existed", "Access and task verification", "Reject unless task subset is proven"),
    }
    for candidate in CANDIDATES:
        rows.append(f"| {candidate.rank} | {candidate.name} | " + " | ".join(estimates[candidate.key]) + " |")
    rows.extend(
        [
            "",
            "## Future Processing Phases",
            "",
            "1. Rights and access verification: confirm licenses, download mechanisms, and durable source availability.",
            "2. Metadata extraction: build a candidate manifest with dataset source, video ID, participant metadata, task label, camera view, frame rate, resolution, and rights status.",
            "3. Manual QC: reject videos that fail full-body visibility, foot visibility, stable camera, and task-standardization gates.",
            "4. Dry-run processing: run a small approved subset through the existing JumpGuard pipeline without code changes.",
            "5. Missingness audit: summarize landmark failures and feature NaN rates.",
            "6. Normative-statistics generation: only after enough health-screened standardized videos remain.",
            "7. Evidence-layer integration: compare athlete videos against the new MediaPipe-derived reference only after the statistical protocol is complete.",
        ]
    )
    return "\n".join(rows) + "\n"


def render_future_validation_roadmap() -> str:
    return """# Future Validation Roadmap

## Architecture

```text
Healthy Videos
  -> Rights / Metadata / QC Gate
  -> Existing JumpGuard Video Processing
  -> Existing MediaPipe Landmark Extraction
  -> Existing Prompt 11 Feature Extraction
  -> Normative Feature Table
  -> Normative Statistics
  -> Athlete Comparison
  -> Evidence Layer
```

## Narrative

The future normative reference should be generated from videos processed through the same JumpGuard pipeline as athlete videos. This avoids comparing MediaPipe-derived geometric approximations against inverse-kinematics signals whose preprocessing and coordinate definitions are unknown.

The pipeline must remain deterministic and traceable. Every normative row should retain source dataset, video identifier, participant metadata, task metadata, QC status, processing version, feature schema version, and missingness metrics. Athlete comparisons should use only features generated with the same pipeline and should continue to avoid diagnosis, ACL prediction, clinical thresholds, and unsupported interpretations.

## Validation Milestones

| Milestone | Success criterion |
|---|---|
| Dataset rights audit | Every video has traceable permission for research processing and aggregate statistics. |
| Metadata completeness audit | Health status, task, camera, and participant metadata are sufficient for the planned reference use. |
| Pipeline reproducibility audit | Re-running the same videos produces identical feature tables within deterministic export precision. |
| Missingness audit | Landmark and feature missingness rates are acceptable and reported by dataset/source/task. |
| Reliability audit | Repeat or duplicate recordings quantify variability from recording setup and MediaPipe processing. |
| Statistical audit | Percentile intervals and confidence intervals are reproducible from a frozen manifest. |
"""


def render_dataset_recommendations() -> str:
    rows = [
        "# Dataset Recommendations",
        "",
        "## Decision",
        "",
        "**No discovered public dataset is recommended for immediate production use as a healthy JumpGuard normative reference.**",
        "",
        "The most scientifically defensible path is to create or obtain a JumpGuard-native healthy video cohort with explicit consent/licensing, standardized jump-landing protocol, stable camera views, complete metadata, and full-body visibility. Public datasets may be useful only for feasibility and robustness pilots.",
        "",
        "## Ranked Recommendations",
        "",
        "| Rank | Dataset | Decision | Evidence-backed rationale | Required next evidence |",
        "|---|---|---|---|---|",
    ]
    next_evidence = {
        "finegym": "Verify video rights, retrieve landing-like clips, quantify MediaPipe failure rate, and exclude from normative statistics unless health/task metadata become adequate.",
        "ntu_rgbd": "Verify official labels, access terms, jump/hop class availability, RGB video quality, sagittal view suitability, and health metadata.",
        "kinetics": "Verify jump-related classes, video availability, rights, health metadata, and QC yield; expected to remain unsuitable for normative statistics.",
        "ucf101": "Verify rights and jump-related classes only if needed for stress testing; not recommended for normative use.",
        "human36m_h3wb": "Verify whether a documented jump-landing action subset exists; otherwise reject for this objective.",
    }
    for candidate in CANDIDATES:
        rows.append(
            f"| {candidate.rank} | {candidate.name} | {candidate.recommendation} | {candidate.compatibility} | {next_evidence[candidate.key]} |"
        )
    rows.extend(
        [
            "",
            "## Production Normative Reference Recommendation",
            "",
            "Build a new healthy cohort or obtain a purpose-collected dataset rather than relying on action-recognition or broadcast-sports datasets. A production reference should be based on known healthy participants, standardized task instructions, fixed recording geometry, stable RGB video, documented frame rate and resolution, complete rights, and unchanged JumpGuard processing.",
            "",
            "## What Must Remain Unknown",
            "",
            "For any public candidate where health status, age, sex, license, frame rate, resolution, camera view, or task protocol is not documented by a publication or official source, the field must remain `Unknown from available evidence` and must not be inferred from video appearance.",
        ]
    )
    return "\n".join(rows) + "\n"


def main() -> None:
    """CLI entry point for regenerating Prompt 18 docs only."""

    paths = generate_normative_dataset_discovery_docs()
    for path in paths.__dict__.values():
        print(path)


if __name__ == "__main__":
    main()
