"""Evidence-based ACL biomechanical interpretation layer.

This module translates existing Prompt 11-compatible feature tables into
traceable, literature-supported movement observations. It does not diagnose,
predict ACL injury, calculate injury probability, or assign risk scores.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import json

import numpy as np
import pandas as pd

from .eda import get_feature_columns, load_feature_table


IDENTIFIER_COLUMNS: tuple[str, ...] = (
    "participant_id",
    "trial_slot",
    "trial_name",
    "condition",
    "is_empty",
)

SUPPORTED_DESCRIPTORS: tuple[str, ...] = (
    "mean",
    "median",
    "maximum",
    "minimum",
    "rom",
    "absolute_difference",
    "percent_difference",
    "symmetry_index",
)

DEFAULT_REFERENCE_PERCENTILE_LOW = 5.0
DEFAULT_REFERENCE_PERCENTILE_HIGH = 95.0


@dataclass(frozen=True)
class LiteratureSource:
    """Peer-reviewed source used by an evidence rule."""

    citation: str
    doi: str | None = None
    pmid: str | None = None
    url: str | None = None


@dataclass(frozen=True)
class EvidenceRule:
    """Structured interpretation rule for a supported feature family."""

    rule_id: str
    feature_patterns: tuple[str, ...]
    description: str
    dataset_comparison_method: str
    evidence_based_interpretation: str
    evidence_strength: str
    suggested_clinical_consideration: str
    limitation: str
    sources: tuple[LiteratureSource, ...]


@dataclass(frozen=True)
class EvidenceInterpretationResult:
    """Generated observations and knowledge-base traceability tables."""

    observations: pd.DataFrame
    knowledge_base: pd.DataFrame


class EvidenceBasedInterpreter:
    """Generate non-diagnostic ACL-biomechanics observations from existing features."""

    def __init__(
        self,
        knowledge_base: tuple[EvidenceRule, ...] | None = None,
        *,
        low_percentile: float = DEFAULT_REFERENCE_PERCENTILE_LOW,
        high_percentile: float = DEFAULT_REFERENCE_PERCENTILE_HIGH,
    ) -> None:
        self.knowledge_base = knowledge_base or default_knowledge_base()
        self.low_percentile = float(low_percentile)
        self.high_percentile = float(high_percentile)

    def interpret_athlete_percentiles(
        self,
        athlete_percentiles: pd.DataFrame,
        *,
        participant_id: int | None = None,
    ) -> EvidenceInterpretationResult:
        """Interpret existing Prompt 6 percentile comparisons."""

        frame = athlete_percentiles.copy()
        if participant_id is not None:
            frame = frame[frame["participant_id"].astype(int).eq(int(participant_id))]
        observations = self._observations_from_comparison_rows(frame)
        return EvidenceInterpretationResult(
            observations=observations,
            knowledge_base=self.knowledge_base_table(),
        )

    def interpret_feature_table(
        self,
        feature_table: pd.DataFrame,
        reference_table: pd.DataFrame,
    ) -> EvidenceInterpretationResult:
        """Interpret one or more feature rows against a reference feature table."""

        comparison = self._compare_feature_table(feature_table, reference_table)
        observations = self._observations_from_comparison_rows(comparison)
        return EvidenceInterpretationResult(
            observations=observations,
            knowledge_base=self.knowledge_base_table(),
        )

    def knowledge_base_table(self) -> pd.DataFrame:
        """Return the configured knowledge base as a traceable table."""

        rows: list[dict[str, Any]] = []
        for rule in self.knowledge_base:
            rows.append(
                {
                    "rule_id": rule.rule_id,
                    "feature_patterns": list(rule.feature_patterns),
                    "description": rule.description,
                    "dataset_comparison_method": rule.dataset_comparison_method,
                    "evidence_based_interpretation": rule.evidence_based_interpretation,
                    "evidence_strength": rule.evidence_strength,
                    "suggested_clinical_consideration": rule.suggested_clinical_consideration,
                    "limitation": rule.limitation,
                    "supporting_literature": [_source_dict(source) for source in rule.sources],
                }
            )
        return pd.DataFrame(rows)

    def _compare_feature_table(
        self,
        feature_table: pd.DataFrame,
        reference_table: pd.DataFrame,
    ) -> pd.DataFrame:
        features = _shared_supported_features(feature_table, reference_table)
        rows: list[dict[str, Any]] = []
        for row_index, row in feature_table.reset_index(drop=True).iterrows():
            participant_id = row.get("participant_id", row_index + 1)
            for feature in features:
                value = row[feature]
                reference = pd.to_numeric(reference_table[feature], errors="coerce").dropna()
                if pd.isna(value) or reference.empty:
                    continue
                value_float = float(value)
                mean = float(reference.mean())
                std = float(reference.std(ddof=0))
                rows.append(
                    {
                        "participant_id": _safe_participant_id(participant_id, row_index),
                        "feature": feature,
                        "value": value_float,
                        "percentile": float((reference <= value_float).mean() * 100.0),
                        "z_score": (value_float - mean) / std if std else 0.0,
                        "population_mean": mean,
                        "population_std": std,
                        "population_p05": float(reference.quantile(0.05)),
                        "population_p95": float(reference.quantile(0.95)),
                    }
                )
        return pd.DataFrame(rows)

    def _observations_from_comparison_rows(self, rows: pd.DataFrame) -> pd.DataFrame:
        if rows.empty:
            return _observation_frame()
        candidates = rows[
            rows["percentile"].le(self.low_percentile)
            | rows["percentile"].ge(self.high_percentile)
        ].copy()
        if candidates.empty:
            return _observation_frame()
        observations: list[dict[str, Any]] = []
        for participant_id, participant_rows in candidates.groupby("participant_id", sort=True):
            for rule in self.knowledge_base:
                rule_rows = participant_rows[
                    participant_rows["feature"].map(lambda feature: _rule_supports(rule, str(feature)))
                ].copy()
                rule_rows = rule_rows[rule_rows["feature"].map(_is_supported_descriptor)]
                if rule_rows.empty:
                    continue
                observations.append(
                    _build_observation(
                        int(participant_id),
                        rule,
                        rule_rows.sort_values("feature"),
                        self.low_percentile,
                        self.high_percentile,
                    )
                )
        if not observations:
            return _observation_frame()
        return pd.DataFrame(observations, columns=_observation_columns())


def default_knowledge_base() -> tuple[EvidenceRule, ...]:
    """Return the curated Prompt 13 knowledge base."""

    non_diagnostic_limitation = (
        "This observation is descriptive and dataset-relative. It is not diagnostic, "
        "does not predict ACL injury, and does not establish tissue status or ligament integrity."
    )
    return (
        EvidenceRule(
            rule_id="sagittal_knee_flexion",
            feature_patterns=("knee_flexion",),
            description="Knee sagittal-plane flexion features from Prompt 11.",
            dataset_comparison_method="Report only measured knee-flexion features at or below the 5th percentile or at or above the 95th percentile of the reference dataset.",
            evidence_based_interpretation=(
                "Sagittal-plane knee flexion is commonly evaluated in jump-landing ACL biomechanics. "
                "Prospective and clinical jump-landing studies discuss knee mechanics as part of neuromuscular-control assessment."
            ),
            evidence_strength="Moderate for movement-context interpretation; not sufficient for diagnosis or prediction from this feature alone.",
            suggested_clinical_consideration=(
                "Consider reviewing the landing video and full lower-extremity movement pattern with a qualified clinician or biomechanist."
            ),
            limitation=non_diagnostic_limitation,
            sources=(
                LiteratureSource(
                    citation="Hewett TE, Myer GD, Ford KR, Heidt RS Jr, Colosimo AJ, McLean SG, van den Bogert AJ, Paterno MV, Succop P. Biomechanical measures of neuromuscular control and valgus loading of the knee predict anterior cruciate ligament injury risk in female athletes: a prospective study. Am J Sports Med. 2005;33(4):492-501.",
                    doi="10.1177/0363546504269591",
                    pmid="15722287",
                    url="https://doi.org/10.1177/0363546504269591",
                ),
                LiteratureSource(
                    citation="Padua DA, Marshall SW, Boling MC, Thigpen CA, Garrett WE Jr, Beutler AI. The Landing Error Scoring System (LESS) is a valid and reliable clinical assessment tool of jump-landing biomechanics: The JUMP-ACL study. Am J Sports Med. 2009;37(10):1996-2002.",
                    doi="10.1177/0363546509343200",
                    pmid="19726623",
                    url="https://doi.org/10.1177/0363546509343200",
                ),
            ),
        ),
        EvidenceRule(
            rule_id="sagittal_hip_strategy",
            feature_patterns=("hip_flexion",),
            description="Hip sagittal-plane flexion features from Prompt 11.",
            dataset_comparison_method="Report only measured hip-flexion features at or below the 5th percentile or at or above the 95th percentile of the reference dataset.",
            evidence_based_interpretation=(
                "Hip flexion is part of sagittal-plane landing strategy and is considered alongside trunk, knee, and ankle mechanics in jump-landing assessment research."
            ),
            evidence_strength="Limited-to-moderate for movement-context interpretation; this project does not measure trunk motion or joint moments.",
            suggested_clinical_consideration=(
                "Consider reviewing whether the observed hip strategy is consistent across trials and with the athlete's task context."
            ),
            limitation=non_diagnostic_limitation,
            sources=(
                LiteratureSource(
                    citation="Padua DA, Marshall SW, Boling MC, Thigpen CA, Garrett WE Jr, Beutler AI. The Landing Error Scoring System (LESS) is a valid and reliable clinical assessment tool of jump-landing biomechanics: The JUMP-ACL study. Am J Sports Med. 2009;37(10):1996-2002.",
                    doi="10.1177/0363546509343200",
                    pmid="19726623",
                    url="https://doi.org/10.1177/0363546509343200",
                ),
            ),
        ),
        EvidenceRule(
            rule_id="sagittal_ankle_strategy",
            feature_patterns=("ankle_angle",),
            description="Ankle sagittal-plane angle features from Prompt 11.",
            dataset_comparison_method="Report only measured ankle-angle features at or below the 5th percentile or at or above the 95th percentile of the reference dataset.",
            evidence_based_interpretation=(
                "Ankle position is one component of lower-extremity jump-landing assessment. This interpretation is limited to descriptive sagittal-plane movement context."
            ),
            evidence_strength="Limited for ACL-specific interpretation from ankle angle alone.",
            suggested_clinical_consideration=(
                "Consider ankle observations only in combination with the full landing pattern and source video review."
            ),
            limitation=non_diagnostic_limitation,
            sources=(
                LiteratureSource(
                    citation="Padua DA, Marshall SW, Boling MC, Thigpen CA, Garrett WE Jr, Beutler AI. The Landing Error Scoring System (LESS) is a valid and reliable clinical assessment tool of jump-landing biomechanics: The JUMP-ACL study. Am J Sports Med. 2009;37(10):1996-2002.",
                    doi="10.1177/0363546509343200",
                    pmid="19726623",
                    url="https://doi.org/10.1177/0363546509343200",
                ),
            ),
        ),
        EvidenceRule(
            rule_id="bilateral_rom_symmetry",
            feature_patterns=("absolute_difference", "percent_difference", "symmetry_index"),
            description="Bilateral ROM symmetry features from Prompt 11.",
            dataset_comparison_method="Report only measured bilateral symmetry features at or below the 5th percentile or at or above the 95th percentile of the reference dataset.",
            evidence_based_interpretation=(
                "Bilateral movement asymmetry is commonly examined in ACL rehabilitation and return-to-sport biomechanics. Prompt 11 symmetry features describe joint-angle ROM symmetry only and are not equivalent to hop-test or kinetic limb-symmetry criteria."
            ),
            evidence_strength="Moderate for general asymmetry context; limited for ROM-only MediaPipe-derived symmetry interpretation.",
            suggested_clinical_consideration=(
                "Consider comparing the symmetry observation with video review, task consistency, and any clinician-collected strength or functional tests when available."
            ),
            limitation=non_diagnostic_limitation,
            sources=(
                LiteratureSource(
                    citation="Paterno MV, Schmitt LC, Ford KR, Rauh MJ, Myer GD, Huang B, Hewett TE. Biomechanical measures during landing and postural stability predict second anterior cruciate ligament injury after anterior cruciate ligament reconstruction and return to sport. Am J Sports Med. 2010;38(10):1968-1978.",
                    doi="10.1177/0363546510376053",
                    pmid="20702858",
                    url="https://doi.org/10.1177/0363546510376053",
                ),
            ),
        ),
    )


def assess_evidence_based_interpretation(
    feature_table: pd.DataFrame | None = None,
    *,
    reference_table: pd.DataFrame | None = None,
) -> EvidenceInterpretationResult:
    """Run Prompt 13 evidence interpretation over a feature table."""

    features = feature_table.copy() if feature_table is not None else load_feature_table()
    reference = reference_table.copy() if reference_table is not None else features
    return EvidenceBasedInterpreter().interpret_feature_table(features, reference)


def export_evidence_outputs(
    result: EvidenceInterpretationResult,
    output_dir: str | Path = "reports",
) -> dict[str, Path]:
    """Export Prompt 13 observations and knowledge base."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    paths = {
        "observations_json": destination / "evidence_based_observations.json",
        "observations_csv": destination / "evidence_based_observations.csv",
        "knowledge_base_json": destination / "evidence_based_knowledge_base.json",
    }
    result.observations.to_csv(paths["observations_csv"], index=False)
    paths["observations_json"].write_text(
        json.dumps(_json_ready(_records(result.observations)), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    paths["knowledge_base_json"].write_text(
        json.dumps(_json_ready(_records(result.knowledge_base)), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return paths


def load_reference_feature_table(path: str | Path = "data/processed/features.csv") -> pd.DataFrame | None:
    """Load the existing reference feature table when available."""

    reference_path = Path(path)
    if not reference_path.exists():
        return None
    return pd.read_csv(reference_path)


def _build_observation(
    participant_id: int,
    rule: EvidenceRule,
    rows: pd.DataFrame,
    low_percentile: float,
    high_percentile: float,
) -> dict[str, Any]:
    supporting = [_supporting_feature(row) for _, row in rows.iterrows()]
    comparison = _comparison_summary(rows, low_percentile, high_percentile)
    return {
        "participant_id": participant_id,
        "observation_id": f"participant_{participant_id}_{rule.rule_id}",
        "title": rule.description,
        "features_used": [item["feature"] for item in supporting],
        "supporting_features": supporting,
        "comparison_performed": comparison,
        "evidence_based_explanation": rule.evidence_based_interpretation,
        "suggested_clinical_consideration": rule.suggested_clinical_consideration,
        "limitation": rule.limitation,
        "evidence_strength": rule.evidence_strength,
        "literature_sources": [_source_dict(source) for source in rule.sources],
        "safety_label": "context_only_not_diagnosis_not_prediction",
    }


def _comparison_summary(
    rows: pd.DataFrame,
    low_percentile: float,
    high_percentile: float,
) -> str:
    low_count = int(rows["percentile"].le(low_percentile).sum())
    high_count = int(rows["percentile"].ge(high_percentile).sum())
    return (
        f"{len(rows)} supporting feature(s) fell outside the reference dataset's "
        f"central {100 - low_percentile - (100 - high_percentile):.0f}% interval "
        f"({low_count} low-tail, {high_count} high-tail). This is a dataset-relative "
        "comparison, not a clinical threshold."
    )


def _supporting_feature(row: pd.Series) -> dict[str, Any]:
    percentile = float(row["percentile"])
    tail = "low_reference_tail" if percentile <= DEFAULT_REFERENCE_PERCENTILE_LOW else "high_reference_tail"
    return {
        "feature": str(row["feature"]),
        "measured_value": float(row["value"]),
        "reference_percentile": percentile,
        "z_score": float(row["z_score"]),
        "reference_mean": float(row["population_mean"]),
        "reference_std": float(row["population_std"]),
        "reference_p05": float(row["population_p05"]),
        "reference_p95": float(row["population_p95"]),
        "reference_tail": tail,
    }


def _shared_supported_features(feature_table: pd.DataFrame, reference_table: pd.DataFrame) -> list[str]:
    feature_names = [feature for feature in get_feature_columns(feature_table) if feature in reference_table.columns]
    return [feature for feature in feature_names if _is_supported_descriptor(feature)]


def _rule_supports(rule: EvidenceRule, feature: str) -> bool:
    return any(pattern in feature for pattern in rule.feature_patterns)


def _is_supported_descriptor(feature: str) -> bool:
    return any(feature.endswith(descriptor) for descriptor in SUPPORTED_DESCRIPTORS)


def _safe_participant_id(value: Any, fallback_index: int) -> int:
    try:
        if pd.notna(value):
            return int(value)
    except Exception:
        pass
    return fallback_index + 1


def _source_dict(source: LiteratureSource) -> dict[str, str | None]:
    return {
        "citation": source.citation,
        "doi": source.doi,
        "pmid": source.pmid,
        "url": source.url,
    }


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return [_json_ready(row) for row in frame.to_dict(orient="records")]


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return None if np.isnan(value) else float(value)
    if isinstance(value, float) and np.isnan(value):
        return None
    return value


def _observation_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=_observation_columns())


def _observation_columns() -> list[str]:
    return [
        "participant_id",
        "observation_id",
        "title",
        "features_used",
        "supporting_features",
        "comparison_performed",
        "evidence_based_explanation",
        "suggested_clinical_consideration",
        "limitation",
        "evidence_strength",
        "literature_sources",
        "safety_label",
    ]
