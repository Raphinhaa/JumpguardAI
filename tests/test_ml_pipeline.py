"""Tests for Prompt 5 ML infrastructure and data preparation."""

from pathlib import Path

import numpy as np
import pandas as pd

from src.eda import get_feature_columns, load_feature_table
from src.ml_pipeline import (
    MLConfig,
    accuracy_score,
    apply_split,
    default_ml_config,
    export_ml_outputs,
    fit_feature_selector,
    fit_preprocessor,
    mean_absolute_error,
    participant_cross_validation,
    participant_split,
    prepare_ml_data,
    root_mean_squared_error,
    transform_features,
    validate_no_participant_leakage,
)


def test_participant_split_has_no_leakage_and_is_deterministic() -> None:
    frame = load_feature_table("data/processed/features.csv")
    config = default_ml_config()
    first = participant_split(frame, config)
    second = participant_split(frame, config)
    leakage = validate_no_participant_leakage(first)

    assert first == second
    assert leakage["passed"].all()
    all_participants = (
        set(first.train_participants)
        | set(first.validation_participants)
        | set(first.test_participants)
    )
    assert all_participants == set(frame["participant_id"].unique())


def test_preprocessor_fits_training_only_and_transforms_splits() -> None:
    frame = load_feature_table("data/processed/features.csv")
    features = get_feature_columns(frame)
    config = MLConfig(missing_policy="drop_rows", scaler="standard")
    split = participant_split(frame, config)
    assigned = apply_split(frame, split)
    train = assigned[assigned["split"] == "train"]

    artifact = fit_preprocessor(train, features, config)
    transformed_train = transform_features(train, artifact)

    assert artifact.scaler == "standard"
    assert transformed_train.shape[1] == 57
    assert transformed_train.isna().sum().sum() == 0
    assert np.allclose(transformed_train.mean(axis=0).to_numpy(), 0.0, atol=1e-10)


def test_median_impute_policy_preserves_rows() -> None:
    frame = load_feature_table("data/processed/features.csv")
    features = get_feature_columns(frame)
    config = MLConfig(missing_policy="median_impute", scaler="none")
    split = participant_split(frame, config)
    assigned = apply_split(frame, split)
    train = assigned[assigned["split"] == "train"]

    artifact = fit_preprocessor(train, features, config)
    transformed = transform_features(train, artifact)

    assert len(transformed) == len(train)
    assert transformed.isna().sum().sum() == 0
    assert set(artifact.impute_values) == set(features)


def test_feature_selection_strategies() -> None:
    frame = load_feature_table("data/processed/features.csv")
    features = get_feature_columns(frame)
    split = participant_split(frame, default_ml_config())
    train = apply_split(frame, split).query("split == 'train'")

    top_n = fit_feature_selector(train, features, MLConfig(feature_selection="top_n", top_n_features=7))
    variance = fit_feature_selector(
        train,
        features,
        MLConfig(feature_selection="variance_threshold", variance_threshold=0.0),
    )
    correlation = fit_feature_selector(
        train,
        features,
        MLConfig(feature_selection="correlation_filter", correlation_threshold=0.95),
    )

    assert len(top_n.selected_features) == 7
    assert len(variance.selected_features) == 57
    assert len(correlation.selected_features) < 57
    assert set(top_n.selected_features).isdisjoint(top_n.removed_features)


def test_cross_validation_is_participant_aware() -> None:
    frame = load_feature_table("data/processed/features.csv")
    summary = participant_cross_validation(frame, MLConfig(cross_validation_folds=5))

    assert summary.shape[0] == 5
    assert summary["participant_overlap_count"].sum() == 0
    assert summary["validation_participant_count"].sum() == frame["participant_id"].nunique()


def test_prepare_and_export_ml_outputs_are_deterministic(tmp_path: Path) -> None:
    frame = load_feature_table("data/processed/features.csv")
    result = prepare_ml_data(frame, default_ml_config())
    paths = export_ml_outputs(
        result,
        output_dir=tmp_path / "reports",
        config_path=tmp_path / "configs" / "default_ml_config.yaml",
        artifact_dir=tmp_path / "reports" / "ml_artifacts",
    )
    second = prepare_ml_data(frame, default_ml_config())

    pd.testing.assert_frame_equal(result.split_summary, second.split_summary)
    pd.testing.assert_frame_equal(result.preprocessing_summary, second.preprocessing_summary)
    pd.testing.assert_frame_equal(
        result.feature_selection_summary,
        second.feature_selection_summary,
    )
    assert all(path.exists() for path in paths.values())
    assert result.preprocessing_summary["fit_source"].eq("train_only").all()
    assert result.feature_selection_summary["selected"].sum() == 57


def test_metric_interfaces() -> None:
    actual = np.array([0.0, 1.0, 2.0])
    predicted = np.array([0.0, 2.0, 1.0])

    assert mean_absolute_error(actual, predicted) == 2 / 3
    assert root_mean_squared_error(actual, predicted) == np.sqrt(2 / 3)
    assert accuracy_score(actual, predicted) == 1 / 3
