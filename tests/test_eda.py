"""Tests for Prompt 4 exploratory feature validation."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.eda import (
    correlation_matrix,
    descriptive_statistics,
    export_eda_tables,
    export_plots,
    feature_variance,
    get_feature_columns,
    load_feature_table,
    missing_summary,
    outlier_summary,
    pca_analysis,
    rank_features,
    run_eda,
    validation_summary,
)


def test_feature_table_validation_outputs_expected_counts() -> None:
    frame = load_feature_table("data/processed/features.csv")
    summary = validation_summary(frame).set_index("metric")["value"]

    assert int(summary["row_count"]) == 258
    assert int(summary["column_count"]) == 62
    assert int(summary["numeric_feature_count"]) == 57
    assert int(summary["duplicate_full_rows"]) == 0
    assert int(summary["duplicate_participant_trial_rows"]) == 0
    assert int(summary["empty_trial_rows"]) == 9
    assert int(summary["complete_feature_rows"]) == 249


def test_descriptive_missing_variance_and_outlier_tables_cover_all_features() -> None:
    frame = load_feature_table("data/processed/features.csv")
    features = get_feature_columns(frame)

    assert len(features) == 57
    assert descriptive_statistics(frame).shape[0] == 57
    assert feature_variance(frame).shape[0] == 57
    assert outlier_summary(frame).shape[0] == 57
    assert missing_summary(frame).shape[0] == 62


def test_correlation_pca_and_ranking_are_deterministic() -> None:
    frame = load_feature_table("data/processed/features.csv")
    corr = correlation_matrix(frame)
    pca_summary, scores, loadings = pca_analysis(frame)
    ranking = rank_features(frame, loadings)

    assert corr.shape == (57, 57)
    assert pca_summary["component"].tolist()[0] == "PC1"
    assert scores.shape[0] == 249
    assert loadings.shape[0] == 57
    assert ranking.shape[0] == 57
    assert ranking["ranking_score"].is_monotonic_decreasing

    second_summary, second_scores, second_loadings = pca_analysis(frame)
    pd.testing.assert_frame_equal(pca_summary, second_summary)
    pd.testing.assert_frame_equal(scores, second_scores)
    pd.testing.assert_frame_equal(loadings, second_loadings)


def test_export_eda_tables_and_plots(tmp_path: Path) -> None:
    frame = load_feature_table("data/processed/features.csv")
    results = run_eda(frame)
    table_paths = export_eda_tables(results, tmp_path / "reports")
    plot_paths = export_plots(frame, tmp_path / "plots")

    expected = {
        "validation_summary",
        "descriptive_statistics",
        "missing_summary",
        "correlation_matrix",
        "feature_variance",
        "outlier_summary",
        "pca_summary",
        "feature_ranking",
    }
    assert set(table_paths) == expected
    assert all(path.exists() for path in table_paths.values())
    assert len(plot_paths) >= (57 * 2) + 5
    assert all(path.exists() for path in plot_paths)
    plt.close("all")
