"""Interpretable biomechanical intelligence layer for JumpGuard AI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .eda import get_feature_columns, load_feature_table


ATHLETE_METADATA_COLUMNS: tuple[str, ...] = ("participant_id", "trial_count", "empty_trial_count")


@dataclass(frozen=True)
class KnowledgeConcept:
    """Cautious literature mapping for a measurable feature family."""

    pattern: str
    concept: str
    literature_language: str
    source: str


@dataclass(frozen=True)
class IntelligenceResult:
    """Container for biomechanical intelligence outputs."""

    athlete_summary: pd.DataFrame
    population_statistics: pd.DataFrame
    athlete_percentiles: pd.DataFrame
    observations: pd.DataFrame
    knowledge_mapping: pd.DataFrame


def default_knowledge_layer() -> tuple[KnowledgeConcept, ...]:
    """Return configurable ACL-biomechanics concept mappings.

    The language is intentionally associative, not causal or diagnostic.
    """

    return (
        KnowledgeConcept(
            pattern="knee_flexion",
            concept="Knee sagittal-plane mechanics",
            literature_language=(
                "Knee flexion during landing is commonly evaluated in ACL biomechanics "
                "and jump-landing movement-quality literature."
            ),
            source="Hewett et al. 2005, Am J Sports Med; https://doi.org/10.1177/0363546504269591",
        ),
        KnowledgeConcept(
            pattern="hip_flexion",
            concept="Hip sagittal-plane mechanics",
            literature_language=(
                "Hip flexion and trunk-lower-extremity strategy are discussed in "
                "landing biomechanics literature as part of movement-pattern assessment."
            ),
            source="Padua et al. 2009, Am J Sports Med; https://doi.org/10.1177/0363546509343200",
        ),
        KnowledgeConcept(
            pattern="ankle_angle",
            concept="Ankle sagittal-plane mechanics",
            literature_language=(
                "Ankle motion is commonly evaluated with hip and knee motion when "
                "describing lower-extremity landing mechanics."
            ),
            source="Padua et al. 2009, Am J Sports Med; https://doi.org/10.1177/0363546509343200",
        ),
        KnowledgeConcept(
            pattern="symmetry",
            concept="Bilateral movement symmetry",
            literature_language=(
                "Limb symmetry and asymmetry are commonly evaluated in return-to-sport "
                "and landing biomechanics research."
            ),
            source="Paterno et al. 2010, Am J Sports Med; https://doi.org/10.1177/0363546510376053",
        ),
        KnowledgeConcept(
            pattern="std",
            concept="Joint-angle variability",
            literature_language=(
                "Movement variability is a descriptive neuromuscular-control measure; "
                "interpretation should remain task- and dataset-specific."
            ),
            source="Krosshaug et al. 2007, Am J Sports Med; https://doi.org/10.1177/0363546507299489",
        ),
    )


def build_athlete_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """Aggregate trial-level features into participant-level athlete summaries.

    Args:
        frame: Prompt 3 feature table.

    Returns:
        One row per participant with mean observed feature values.
    """

    features = get_feature_columns(frame)
    grouped = frame.groupby("participant_id", sort=True)
    summary = grouped[features].mean(numeric_only=True).reset_index()
    counts = grouped.agg(
        trial_count=("trial_slot", "count"),
        empty_trial_count=("is_empty", "sum"),
    ).reset_index()
    return counts.merge(summary, on="participant_id", how="left")


def compute_population_statistics(athlete_summary: pd.DataFrame) -> pd.DataFrame:
    """Compute reference population statistics over athlete summaries."""

    features = _athlete_feature_columns(athlete_summary)
    rows: list[dict[str, Any]] = []
    for feature in features:
        series = athlete_summary[feature].dropna()
        rows.append(
            {
                "feature": feature,
                "count": int(series.count()),
                "mean": float(series.mean()) if not series.empty else np.nan,
                "std": float(series.std(ddof=0)) if not series.empty else np.nan,
                "min": float(series.min()) if not series.empty else np.nan,
                "p05": float(series.quantile(0.05)) if not series.empty else np.nan,
                "p25": float(series.quantile(0.25)) if not series.empty else np.nan,
                "median": float(series.median()) if not series.empty else np.nan,
                "p75": float(series.quantile(0.75)) if not series.empty else np.nan,
                "p95": float(series.quantile(0.95)) if not series.empty else np.nan,
                "max": float(series.max()) if not series.empty else np.nan,
            }
        )
    return pd.DataFrame(rows)


def compute_athlete_percentiles(
    athlete_summary: pd.DataFrame,
    population_statistics: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Compute percentile and Z-score comparisons for each athlete feature."""

    features = _athlete_feature_columns(athlete_summary)
    population = population_statistics
    if population is None:
        population = compute_population_statistics(athlete_summary)
    pop_lookup = population.set_index("feature")
    rows: list[dict[str, Any]] = []
    for _, athlete in athlete_summary.iterrows():
        for feature in features:
            value = athlete[feature]
            reference = athlete_summary[feature].dropna()
            if pd.isna(value) or reference.empty:
                percentile = np.nan
                z_score = np.nan
            else:
                percentile = float((reference <= value).mean() * 100.0)
                std = float(pop_lookup.loc[feature, "std"])
                mean = float(pop_lookup.loc[feature, "mean"])
                z_score = (float(value) - mean) / std if std else 0.0
            rows.append(
                {
                    "participant_id": int(athlete["participant_id"]),
                    "feature": feature,
                    "value": float(value) if pd.notna(value) else np.nan,
                    "percentile": percentile,
                    "z_score": z_score,
                    "population_mean": float(pop_lookup.loc[feature, "mean"]),
                    "population_std": float(pop_lookup.loc[feature, "std"]),
                    "population_p05": float(pop_lookup.loc[feature, "p05"]),
                    "population_p95": float(pop_lookup.loc[feature, "p95"]),
                }
            )
    return pd.DataFrame(rows)


def generate_observations(
    athlete_percentiles: pd.DataFrame,
    knowledge_layer: tuple[KnowledgeConcept, ...] | None = None,
    z_threshold: float = 2.0,
    low_percentile: float = 5.0,
    high_percentile: float = 95.0,
) -> pd.DataFrame:
    """Generate explainable, non-diagnostic biomechanical observations."""

    knowledge = knowledge_layer or default_knowledge_layer()
    rows: list[dict[str, Any]] = []
    candidates = athlete_percentiles[
        (athlete_percentiles["z_score"].abs() >= z_threshold)
        | (athlete_percentiles["percentile"] <= low_percentile)
        | (athlete_percentiles["percentile"] >= high_percentile)
    ].copy()
    for _, row in candidates.iterrows():
        feature = str(row["feature"])
        concept = _match_concept(feature, knowledge)
        direction = "above" if row["z_score"] >= 0 else "below"
        rows.append(
            {
                "participant_id": int(row["participant_id"]),
                "category": _feature_category(feature),
                "feature": feature,
                "value": float(row["value"]),
                "percentile": float(row["percentile"]),
                "z_score": float(row["z_score"]),
                "population_comparison": (
                    f"{direction} the reference mean by {abs(row['z_score']):.2f} SD"
                ),
                "plain_language_explanation": _plain_language(feature, row, direction),
                "literature_concept": concept.concept,
                "literature_language": concept.literature_language,
                "source": concept.source,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["participant_id", "category", "feature"]
    ).reset_index(drop=True)


def build_knowledge_mapping_table(
    feature_names: list[str] | tuple[str, ...],
    knowledge_layer: tuple[KnowledgeConcept, ...] | None = None,
) -> pd.DataFrame:
    """Map every feature to the configured knowledge layer."""

    knowledge = knowledge_layer or default_knowledge_layer()
    rows = []
    for feature in feature_names:
        concept = _match_concept(feature, knowledge)
        rows.append(
            {
                "feature": feature,
                "category": _feature_category(feature),
                "concept": concept.concept,
                "literature_language": concept.literature_language,
                "source": concept.source,
            }
        )
    return pd.DataFrame(rows)


def assess_biomechanics(frame: pd.DataFrame | None = None) -> IntelligenceResult:
    """Run the full biomechanical intelligence assessment."""

    feature_frame = frame.copy() if frame is not None else load_feature_table()
    athlete_summary = build_athlete_summary(feature_frame)
    population = compute_population_statistics(athlete_summary)
    percentiles = compute_athlete_percentiles(athlete_summary, population)
    observations = generate_observations(percentiles)
    mapping = build_knowledge_mapping_table(_athlete_feature_columns(athlete_summary))
    return IntelligenceResult(
        athlete_summary=athlete_summary,
        population_statistics=population,
        athlete_percentiles=percentiles,
        observations=observations,
        knowledge_mapping=mapping,
    )


def export_intelligence_outputs(
    result: IntelligenceResult,
    output_dir: str | Path = "reports",
) -> dict[str, Path]:
    """Export required and supporting intelligence outputs."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    paths = {
        "athlete_summary": destination / "athlete_summary.csv",
        "population_statistics": destination / "population_statistics.csv",
        "athlete_percentiles": destination / "athlete_percentiles.csv",
        "biomechanical_observations": destination / "biomechanical_observations.csv",
        "knowledge_mapping": destination / "biomechanical_knowledge_mapping.csv",
    }
    result.athlete_summary.to_csv(paths["athlete_summary"], index=False, float_format="%.10g")
    result.population_statistics.to_csv(
        paths["population_statistics"], index=False, float_format="%.10g"
    )
    result.athlete_percentiles.to_csv(
        paths["athlete_percentiles"], index=False, float_format="%.10g"
    )
    result.observations.to_csv(paths["biomechanical_observations"], index=False, float_format="%.10g")
    result.knowledge_mapping.to_csv(paths["knowledge_mapping"], index=False)
    return paths


def export_intelligence_plots(
    result: IntelligenceResult,
    participant_id: int,
    output_dir: str | Path = "reports/biomechanical_intelligence_plots",
) -> list[Path]:
    """Export reusable visualizations for one athlete."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    plotters = {
        f"athlete_{participant_id}_radar.png": lambda: plot_radar(result, participant_id),
        f"athlete_{participant_id}_symmetry.png": lambda: plot_symmetry(result, participant_id),
        f"athlete_{participant_id}_percentiles.png": lambda: plot_percentiles(result, participant_id),
        f"athlete_{participant_id}_feature_comparison.png": lambda: plot_feature_comparison(
            result, participant_id
        ),
        f"athlete_{participant_id}_vs_population.png": lambda: plot_athlete_vs_population(
            result, participant_id
        ),
    }
    paths: list[Path] = []
    for filename, plotter in plotters.items():
        figure, _ = plotter()
        path = destination / filename
        figure.savefig(
            path,
            dpi=140,
            bbox_inches="tight",
            metadata={"Software": "JumpGuardAI"},
        )
        plt.close(figure)
        paths.append(path)
    return paths


def plot_radar(result: IntelligenceResult, participant_id: int) -> tuple[Figure, Axes]:
    """Plot radar-style category percentile averages for one athlete."""

    data = result.athlete_percentiles[result.athlete_percentiles["participant_id"] == participant_id]
    categories = ["knee", "hip", "ankle", "symmetry", "variability", "consistency"]
    values = [
        float(data[data["feature"].map(_feature_category) == category]["percentile"].mean())
        for category in categories
    ]
    values = [0.0 if np.isnan(value) else value for value in values]
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]
    figure, axes = plt.subplots(figsize=(6.0, 6.0), subplot_kw={"projection": "polar"})
    axes.plot(angles, values, color="#2C7FB8", linewidth=2)
    axes.fill(angles, values, color="#2C7FB8", alpha=0.2)
    axes.set_xticks(angles[:-1], categories)
    axes.set_ylim(0, 100)
    axes.set_title(f"Athlete {participant_id} Category Percentiles")
    return figure, axes


def plot_symmetry(result: IntelligenceResult, participant_id: int) -> tuple[Figure, Axes]:
    """Plot symmetry features for one athlete."""

    data = result.athlete_percentiles[
        (result.athlete_percentiles["participant_id"] == participant_id)
        & (result.athlete_percentiles["feature"].str.contains("symmetry|absolute_difference|percent_difference"))
    ].copy()
    figure, axes = plt.subplots(figsize=(9.0, 4.8))
    axes.bar(data["feature"], data["value"], color="#4D9221")
    axes.set(title=f"Athlete {participant_id} Symmetry Features", ylabel="Feature value")
    axes.tick_params(axis="x", rotation=75, labelsize=7)
    _style_axes(axes)
    figure.tight_layout()
    return figure, axes


def plot_percentiles(result: IntelligenceResult, participant_id: int) -> tuple[Figure, Axes]:
    """Plot all athlete feature percentiles."""

    data = result.athlete_percentiles[
        result.athlete_percentiles["participant_id"] == participant_id
    ].sort_values("percentile")
    figure, axes = plt.subplots(figsize=(10.0, 7.0))
    axes.scatter(data["percentile"], range(len(data)), s=20, color="#756BB1")
    axes.axvline(5, color="#B2182B", linestyle="--", linewidth=1)
    axes.axvline(95, color="#B2182B", linestyle="--", linewidth=1)
    axes.set(title=f"Athlete {participant_id} Feature Percentiles", xlabel="Percentile")
    axes.set_yticks([])
    _style_axes(axes)
    figure.tight_layout()
    return figure, axes


def plot_feature_comparison(result: IntelligenceResult, participant_id: int) -> tuple[Figure, Axes]:
    """Plot selected ROM features against population means."""

    selected = [
        "hip_flexion_right_rom",
        "hip_flexion_left_rom",
        "knee_flexion_right_rom",
        "knee_flexion_left_rom",
        "ankle_angle_right_rom",
        "ankle_angle_left_rom",
    ]
    data = result.athlete_percentiles[
        (result.athlete_percentiles["participant_id"] == participant_id)
        & (result.athlete_percentiles["feature"].isin(selected))
    ]
    figure, axes = plt.subplots(figsize=(9.0, 4.8))
    positions = np.arange(len(data))
    axes.bar(positions - 0.2, data["value"], width=0.4, label="Athlete", color="#2C7FB8")
    axes.bar(
        positions + 0.2,
        data["population_mean"],
        width=0.4,
        label="Population mean",
        color="#FDB863",
    )
    axes.set_xticks(positions, data["feature"], rotation=60, ha="right", fontsize=8)
    axes.set(title=f"Athlete {participant_id} ROM Comparison", ylabel="Degrees")
    axes.legend(frameon=False)
    _style_axes(axes)
    figure.tight_layout()
    return figure, axes


def plot_athlete_vs_population(result: IntelligenceResult, participant_id: int) -> tuple[Figure, Axes]:
    """Plot athlete Z-scores for all features."""

    data = result.athlete_percentiles[result.athlete_percentiles["participant_id"] == participant_id]
    figure, axes = plt.subplots(figsize=(10.0, 5.5))
    axes.scatter(range(len(data)), data["z_score"], s=18, color="#2C7FB8")
    axes.axhline(2, color="#B2182B", linestyle="--", linewidth=1)
    axes.axhline(-2, color="#B2182B", linestyle="--", linewidth=1)
    axes.axhline(0, color="#4A4A4A", linewidth=1)
    axes.set(title=f"Athlete {participant_id} vs Population", ylabel="Z-score")
    axes.set_xticks([])
    _style_axes(axes)
    figure.tight_layout()
    return figure, axes


def _athlete_feature_columns(frame: pd.DataFrame) -> list[str]:
    metadata = set(ATHLETE_METADATA_COLUMNS)
    return [
        column
        for column in frame.columns
        if column not in metadata and pd.api.types.is_numeric_dtype(frame[column])
    ]


def _feature_category(feature: str) -> str:
    if "symmetry" in feature or "absolute_difference" in feature or "percent_difference" in feature:
        return "symmetry"
    if "knee" in feature:
        return "knee"
    if "hip" in feature:
        return "hip"
    if "ankle" in feature:
        return "ankle"
    if "std" in feature or "variance" in feature:
        return "variability"
    if "time_to_peak" in feature:
        return "consistency"
    return "feature"


def _match_concept(feature: str, knowledge_layer: tuple[KnowledgeConcept, ...]) -> KnowledgeConcept:
    for concept in knowledge_layer:
        if concept.pattern in feature:
            return concept
    return KnowledgeConcept(
        pattern="default",
        concept="Measured joint-angle feature",
        literature_language=(
            "This feature is interpreted descriptively against the dataset reference "
            "population without assigning a clinical meaning."
        ),
        source="Dataset-derived measurement; no external clinical threshold applied.",
    )


def _plain_language(feature: str, row: pd.Series, direction: str) -> str:
    category = _feature_category(feature).replace("_", " ")
    return (
        f"The athlete's {feature} value is {row['value']:.3g}, which is "
        f"{direction} the dataset mean and at percentile {row['percentile']:.1f}. "
        f"This is a descriptive {category} observation, not a diagnosis or injury prediction."
    )


def _style_axes(ax: Axes) -> None:
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.7, alpha=0.75)
    ax.spines[["top", "right"]].set_visible(False)
