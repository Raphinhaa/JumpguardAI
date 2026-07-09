"""Tests for the public feature extraction pipeline."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

from src.dataset import Dataset
from src.feature_engineering import (
    FeatureExtractor,
    export_features,
    plot_correlation_heatmap,
    plot_feature_distribution,
    plot_left_right_comparison,
    plot_time_series_overlay,
    validate_feature_table,
)


@pytest.fixture(scope="module")
def extractor() -> FeatureExtractor:
    return FeatureExtractor()


@pytest.fixture(scope="module")
def feature_frame(dataset: Dataset, extractor: FeatureExtractor) -> pd.DataFrame:
    return extractor.extract_dataset(dataset)


def test_feature_schema_is_unique_and_expected_size(extractor: FeatureExtractor) -> None:
    assert len(extractor.feature_names) == 57
    assert len(set(extractor.feature_names)) == 57
    assert len(extractor.definitions) == 57


def test_trial_api_matches_shared_extractor(
    dataset: Dataset,
    extractor: FeatureExtractor,
) -> None:
    trial = dataset.get_participant(1).get_trial(1)
    assert trial.extract_features(extractor) == extractor.extract(trial)
    assert trial.extract_features(extractor)["knee_flexion_right_rom"] == pytest.approx(
        np.ptp(trial.get_joint_angle("knee_angle_r"))
    )


def test_dataset_and_participant_delegate_to_shared_pipeline(
    dataset: Dataset,
    extractor: FeatureExtractor,
) -> None:
    assert dataset.extract_features(extractor).equals(extractor.extract_dataset(dataset))
    participant_frame = dataset.get_participant(32).extract_features(extractor)
    assert participant_frame.shape == (6, 62)
    assert participant_frame["is_empty"].sum() == 3


def test_feature_table_preserves_every_slot_and_missingness(
    feature_frame: pd.DataFrame,
    extractor: FeatureExtractor,
) -> None:
    assert feature_frame.shape == (258, 62)
    assert feature_frame["is_empty"].sum() == 9
    values = feature_frame.loc[:, extractor.feature_names]
    assert values.loc[~feature_frame["is_empty"]].notna().all().all()
    assert values.loc[feature_frame["is_empty"]].isna().all().all()
    validate_feature_table(feature_frame, extractor.feature_names)


def test_extraction_is_deterministic(
    dataset: Dataset,
    extractor: FeatureExtractor,
    feature_frame: pd.DataFrame,
) -> None:
    pd.testing.assert_frame_equal(feature_frame, extractor.extract_dataset(dataset))


def test_raise_policy_rejects_empty_trial(dataset: Dataset) -> None:
    with pytest.raises(ValueError, match="empty"):
        FeatureExtractor(missing_policy="raise").extract(
            dataset.get_participant(44).get_trial(1)
        )


def test_csv_export_round_trip(
    tmp_path: Path,
    feature_frame: pd.DataFrame,
) -> None:
    destination = export_features(feature_frame, tmp_path / "features.csv")
    loaded = pd.read_csv(destination)
    assert loaded.shape == feature_frame.shape
    assert tuple(loaded.columns) == tuple(feature_frame.columns)


def test_feature_visualizations_smoke(
    dataset: Dataset,
    feature_frame: pd.DataFrame,
) -> None:
    selected = (
        "hip_flexion_right_rom",
        "knee_flexion_right_rom",
        "ankle_angle_right_rom",
    )
    results = [
        plot_feature_distribution(feature_frame, selected[1]),
        plot_correlation_heatmap(feature_frame, selected),
        plot_left_right_comparison(
            feature_frame,
            "knee_flexion_left_rom",
            "knee_flexion_right_rom",
        ),
        plot_time_series_overlay(dataset.get_participant(1).get_trial(1)),
    ]
    assert all(figure is not None and axes is not None for figure, axes in results)
    plt.close("all")
