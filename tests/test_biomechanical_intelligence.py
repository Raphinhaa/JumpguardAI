"""Tests for Prompt 6 biomechanical intelligence engine."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.biomechanical_intelligence import (
    assess_biomechanics,
    build_athlete_summary,
    build_knowledge_mapping_table,
    compute_athlete_percentiles,
    compute_population_statistics,
    export_intelligence_outputs,
    export_intelligence_plots,
    generate_observations,
)
from src.eda import get_feature_columns, load_feature_table


def test_athlete_summary_and_population_statistics_shape() -> None:
    frame = load_feature_table("data/processed/features.csv")
    athlete_summary = build_athlete_summary(frame)
    population = compute_population_statistics(athlete_summary)

    assert athlete_summary.shape == (43, 60)
    assert athlete_summary["participant_id"].is_unique
    assert population.shape[0] == 57
    assert set(population["feature"]) == set(get_feature_columns(frame))


def test_percentiles_are_bounded_and_deterministic() -> None:
    frame = load_feature_table("data/processed/features.csv")
    athlete_summary = build_athlete_summary(frame)
    population = compute_population_statistics(athlete_summary)
    first = compute_athlete_percentiles(athlete_summary, population)
    second = compute_athlete_percentiles(athlete_summary, population)

    assert first.shape[0] == 43 * 57
    assert first["percentile"].dropna().between(0, 100).all()
    pd.testing.assert_frame_equal(first, second)


def test_observations_are_explainable_and_non_diagnostic() -> None:
    result = assess_biomechanics(load_feature_table("data/processed/features.csv"))
    observations = generate_observations(result.athlete_percentiles)

    assert not observations.empty
    assert {
        "feature",
        "value",
        "population_comparison",
        "plain_language_explanation",
        "literature_language",
    }.issubset(observations.columns)
    combined = " ".join(observations["plain_language_explanation"].str.lower())
    assert "diagnosis" in combined
    assert "injury prediction" in combined
    assert "probability" not in combined


def test_knowledge_mapping_covers_all_features() -> None:
    frame = load_feature_table("data/processed/features.csv")
    mapping = build_knowledge_mapping_table(get_feature_columns(frame))

    assert mapping.shape[0] == 57
    assert mapping["concept"].notna().all()
    assert mapping["literature_language"].str.contains("associated|evaluated|discussed|descriptive").all()


def test_assessment_exports_and_plots(tmp_path: Path) -> None:
    result = assess_biomechanics(load_feature_table("data/processed/features.csv"))
    paths = export_intelligence_outputs(result, tmp_path / "reports")
    plot_paths = export_intelligence_plots(result, participant_id=1, output_dir=tmp_path / "plots")

    expected = {
        "athlete_summary",
        "population_statistics",
        "athlete_percentiles",
        "biomechanical_observations",
        "knowledge_mapping",
    }
    assert set(paths) == expected
    assert all(path.exists() for path in paths.values())
    assert len(plot_paths) == 5
    assert all(path.exists() for path in plot_paths)
    plt.close("all")
