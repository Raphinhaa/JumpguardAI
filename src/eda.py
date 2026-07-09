"""Exploratory analysis utilities for the exported feature table."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .feature_engineering import IDENTIFIER_COLUMNS


@dataclass(frozen=True)
class EDAResults:
    """Container for deterministic EDA tables.

    Args:
        validation_summary: Dataset-level validation metrics.
        descriptive_statistics: Per-feature descriptive statistics.
        missing_summary: Per-column missingness statistics.
        correlation_matrix: Pearson feature correlation matrix.
        feature_variance: Per-feature variance and low-variance flags.
        outlier_summary: Per-feature IQR and Z-score outlier counts.
        pca_summary: Explained variance by principal component.
        feature_ranking: Unsupervised candidate-feature ranking.
    """

    validation_summary: pd.DataFrame
    descriptive_statistics: pd.DataFrame
    missing_summary: pd.DataFrame
    correlation_matrix: pd.DataFrame
    feature_variance: pd.DataFrame
    outlier_summary: pd.DataFrame
    pca_summary: pd.DataFrame
    feature_ranking: pd.DataFrame


def load_feature_table(path: str | Path = "data/processed/features.csv") -> pd.DataFrame:
    """Load the Prompt 3 feature table.

    Args:
        path: CSV path written by ``export_features``.

    Returns:
        Loaded feature DataFrame.

    Raises:
        FileNotFoundError: If the feature table is unavailable.
    """

    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Feature table not found: {source}")
    return pd.read_csv(source)


def get_feature_columns(frame: pd.DataFrame) -> list[str]:
    """Return numeric feature columns, excluding identifier metadata.

    Args:
        frame: Feature DataFrame.

    Returns:
        Ordered feature column names.
    """

    excluded = set(IDENTIFIER_COLUMNS)
    return [
        column
        for column in frame.columns
        if column not in excluded and pd.api.types.is_numeric_dtype(frame[column])
    ]


def validation_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """Create a dataset validation summary.

    Args:
        frame: Feature DataFrame.

    Returns:
        Two-column table with validation metric names and values.
    """

    features = get_feature_columns(frame)
    identifiers = [column for column in IDENTIFIER_COLUMNS if column in frame.columns]
    duplicate_rows = int(frame.duplicated().sum())
    duplicate_slots = (
        int(frame.duplicated(["participant_id", "trial_slot"]).sum())
        if {"participant_id", "trial_slot"}.issubset(frame.columns)
        else np.nan
    )
    feature_values = frame.loc[:, features]
    infinite_values = int(np.isinf(feature_values.to_numpy(dtype=float)).sum())
    rows = [
        ("row_count", int(frame.shape[0])),
        ("column_count", int(frame.shape[1])),
        ("identifier_column_count", len(identifiers)),
        ("numeric_feature_count", len(features)),
        ("duplicate_full_rows", duplicate_rows),
        ("duplicate_participant_trial_rows", duplicate_slots),
        ("missing_values_total", int(frame.isna().sum().sum())),
        ("infinite_feature_values", infinite_values),
        ("empty_trial_rows", int(frame["is_empty"].sum()) if "is_empty" in frame else np.nan),
        ("complete_feature_rows", int(feature_values.notna().all(axis=1).sum())),
    ]
    return pd.DataFrame(rows, columns=["metric", "value"])


def descriptive_statistics(frame: pd.DataFrame) -> pd.DataFrame:
    """Compute descriptive statistics for every numeric feature.

    Args:
        frame: Feature DataFrame.

    Returns:
        Statistics table with one row per feature.
    """

    rows: list[dict[str, Any]] = []
    for feature in get_feature_columns(frame):
        series = frame[feature].dropna()
        q1 = float(series.quantile(0.25)) if not series.empty else np.nan
        q3 = float(series.quantile(0.75)) if not series.empty else np.nan
        rows.append(
            {
                "feature": feature,
                "count": int(series.count()),
                "missing_count": int(frame[feature].isna().sum()),
                "missing_percent": _percent(frame[feature].isna().sum(), len(frame)),
                "mean": float(series.mean()) if not series.empty else np.nan,
                "median": float(series.median()) if not series.empty else np.nan,
                "std": float(series.std(ddof=0)) if not series.empty else np.nan,
                "min": float(series.min()) if not series.empty else np.nan,
                "q1": q1,
                "q3": q3,
                "max": float(series.max()) if not series.empty else np.nan,
                "iqr": q3 - q1 if np.isfinite(q1) and np.isfinite(q3) else np.nan,
                "skewness": float(series.skew()) if len(series) > 2 else np.nan,
                "kurtosis": float(series.kurt()) if len(series) > 3 else np.nan,
            }
        )
    return pd.DataFrame(rows)


def missing_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """Compute missingness counts and percentages for every column.

    Args:
        frame: Feature DataFrame.

    Returns:
        Missingness summary sorted by missing count descending.
    """

    rows = [
        {
            "column": column,
            "missing_count": int(frame[column].isna().sum()),
            "missing_percent": _percent(frame[column].isna().sum(), len(frame)),
        }
        for column in frame.columns
    ]
    return pd.DataFrame(rows).sort_values(
        ["missing_count", "column"], ascending=[False, True]
    ).reset_index(drop=True)


def correlation_matrix(frame: pd.DataFrame) -> pd.DataFrame:
    """Compute the Pearson correlation matrix over numeric features.

    Args:
        frame: Feature DataFrame.

    Returns:
        Feature-by-feature Pearson correlation matrix.
    """

    return frame.loc[:, get_feature_columns(frame)].corr(method="pearson")


def highly_correlated_pairs(correlation: pd.DataFrame, threshold: float = 0.95) -> pd.DataFrame:
    """Identify feature pairs with high absolute Pearson correlation.

    Args:
        correlation: Feature correlation matrix.
        threshold: Absolute correlation cutoff.

    Returns:
        Pair table sorted by absolute correlation descending.
    """

    pairs: list[dict[str, Any]] = []
    columns = list(correlation.columns)
    for left_index, left in enumerate(columns):
        for right in columns[left_index + 1 :]:
            value = correlation.loc[left, right]
            if pd.notna(value) and abs(value) >= threshold:
                pairs.append(
                    {
                        "feature_1": left,
                        "feature_2": right,
                        "correlation": float(value),
                        "absolute_correlation": float(abs(value)),
                    }
                )
    return pd.DataFrame(pairs).sort_values(
        "absolute_correlation", ascending=False
    ).reset_index(drop=True)


def feature_variance(frame: pd.DataFrame, near_constant_threshold: float = 1e-8) -> pd.DataFrame:
    """Compute per-feature variance and low-variance flags.

    Args:
        frame: Feature DataFrame.
        near_constant_threshold: Variance at or below this value is near-constant.

    Returns:
        Variance table sorted by variance ascending.
    """

    rows: list[dict[str, Any]] = []
    features = get_feature_columns(frame)
    variances = frame.loc[:, features].var(skipna=True, ddof=0)
    positive = variances[variances > near_constant_threshold]
    very_low_threshold = float(positive.quantile(0.10)) if not positive.empty else near_constant_threshold
    for feature in features:
        series = frame[feature].dropna()
        variance = float(variances[feature])
        rows.append(
            {
                "feature": feature,
                "variance": variance,
                "std": float(series.std(ddof=0)) if not series.empty else np.nan,
                "non_null_count": int(series.count()),
                "unique_non_null_values": int(series.nunique()),
                "near_constant": bool(variance <= near_constant_threshold),
                "very_low_variance": bool(variance <= very_low_threshold),
                "very_low_variance_threshold": very_low_threshold,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["variance", "feature"], ascending=[True, True]
    ).reset_index(drop=True)


def outlier_summary(frame: pd.DataFrame, z_threshold: float = 3.0) -> pd.DataFrame:
    """Count IQR and Z-score outliers for every feature.

    Args:
        frame: Feature DataFrame.
        z_threshold: Absolute Z-score threshold.

    Returns:
        Outlier summary table.
    """

    rows: list[dict[str, Any]] = []
    for feature in get_feature_columns(frame):
        series = frame[feature].dropna()
        q1 = series.quantile(0.25) if not series.empty else np.nan
        q3 = series.quantile(0.75) if not series.empty else np.nan
        iqr = q3 - q1 if pd.notna(q1) and pd.notna(q3) else np.nan
        lower = q1 - 1.5 * iqr if pd.notna(iqr) else np.nan
        upper = q3 + 1.5 * iqr if pd.notna(iqr) else np.nan
        iqr_count = int(((series < lower) | (series > upper)).sum()) if pd.notna(iqr) else 0
        std = series.std(ddof=0)
        z_count = int(((series - series.mean()).abs() / std > z_threshold).sum()) if std else 0
        rows.append(
            {
                "feature": feature,
                "iqr_lower_bound": float(lower) if pd.notna(lower) else np.nan,
                "iqr_upper_bound": float(upper) if pd.notna(upper) else np.nan,
                "iqr_outlier_count": iqr_count,
                "iqr_outlier_percent": _percent(iqr_count, len(series)),
                "zscore_threshold": z_threshold,
                "zscore_outlier_count": z_count,
                "zscore_outlier_percent": _percent(z_count, len(series)),
            }
        )
    return pd.DataFrame(rows)


def pca_analysis(
    frame: pd.DataFrame,
    n_components: int = 10,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Run PCA with NumPy SVD on complete feature rows.

    Args:
        frame: Feature DataFrame.
        n_components: Maximum number of principal components to return.

    Returns:
        Tuple of PCA summary, score table, and loading table.
    """

    features = get_feature_columns(frame)
    complete = frame.loc[:, features].dropna()
    if complete.empty:
        raise ValueError("PCA requires at least one complete feature row.")
    means = complete.mean(axis=0)
    stds = complete.std(axis=0, ddof=0).replace(0.0, 1.0)
    standardized = (complete - means) / stds
    _, singular_values, vt = np.linalg.svd(standardized.to_numpy(dtype=float), full_matrices=False)
    max_components = min(n_components, len(singular_values), len(features))
    explained = (singular_values**2) / (len(standardized) - 1)
    ratios = explained / explained.sum()
    summary_rows = []
    for index in range(max_components):
        summary_rows.append(
            {
                "component": f"PC{index + 1}",
                "explained_variance": float(explained[index]),
                "explained_variance_ratio": float(ratios[index]),
                "cumulative_explained_variance_ratio": float(ratios[: index + 1].sum()),
            }
        )
    scores = standardized.to_numpy(dtype=float) @ vt[:max_components].T
    score_columns = [f"PC{index + 1}" for index in range(max_components)]
    scores_frame = pd.DataFrame(scores, columns=score_columns, index=complete.index)
    loadings = pd.DataFrame(
        vt[:max_components].T,
        index=features,
        columns=score_columns,
    ).reset_index(names="feature")
    return pd.DataFrame(summary_rows), scores_frame.reset_index(names="source_row"), loadings


def rank_features(frame: pd.DataFrame, loadings: pd.DataFrame) -> pd.DataFrame:
    """Rank candidate features using unsupervised criteria only.

    Args:
        frame: Feature DataFrame.
        loadings: PCA loadings returned by ``pca_analysis``.

    Returns:
        Ranked feature table. Higher scores indicate stronger unsupervised
        candidacy for later modeling review.
    """

    features = get_feature_columns(frame)
    variance = frame.loc[:, features].var(skipna=True, ddof=0)
    variance_score = _minmax(variance)
    corr = frame.loc[:, features].corr().abs()
    redundancy = corr.mask(np.eye(len(corr), dtype=bool)).max(axis=1).fillna(0.0)
    redundancy_penalty = 1.0 - redundancy
    pc_columns = [column for column in loadings.columns if column.startswith("PC")]
    loading_score = loadings.set_index("feature").loc[features, pc_columns].abs().mean(axis=1)
    loading_score = _minmax(loading_score)
    score = (0.4 * variance_score) + (0.4 * loading_score) + (0.2 * redundancy_penalty)
    return (
        pd.DataFrame(
            {
                "feature": features,
                "ranking_score": score.loc[features].astype(float),
                "variance_score": variance_score.loc[features].astype(float),
                "pca_loading_score": loading_score.loc[features].astype(float),
                "nonredundancy_score": redundancy_penalty.loc[features].astype(float),
                "max_absolute_correlation": redundancy.loc[features].astype(float),
            }
        )
        .sort_values(["ranking_score", "feature"], ascending=[False, True])
        .reset_index(drop=True)
    )


def run_eda(frame: pd.DataFrame) -> EDAResults:
    """Run all deterministic EDA table computations.

    Args:
        frame: Feature DataFrame.

    Returns:
        EDAResults container.
    """

    corr = correlation_matrix(frame)
    pca_summary, _, loadings = pca_analysis(frame)
    return EDAResults(
        validation_summary=validation_summary(frame),
        descriptive_statistics=descriptive_statistics(frame),
        missing_summary=missing_summary(frame),
        correlation_matrix=corr,
        feature_variance=feature_variance(frame),
        outlier_summary=outlier_summary(frame),
        pca_summary=pca_summary,
        feature_ranking=rank_features(frame, loadings),
    )


def export_eda_tables(results: EDAResults, output_dir: str | Path = "reports") -> dict[str, Path]:
    """Export Prompt 4 EDA tables as deterministic CSV files.

    Args:
        results: EDA tables.
        output_dir: Destination directory.

    Returns:
        Mapping from logical table name to written path.
    """

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    tables = {
        "validation_summary": results.validation_summary,
        "descriptive_statistics": results.descriptive_statistics,
        "missing_summary": results.missing_summary,
        "correlation_matrix": results.correlation_matrix,
        "feature_variance": results.feature_variance,
        "outlier_summary": results.outlier_summary,
        "pca_summary": results.pca_summary,
        "feature_ranking": results.feature_ranking,
    }
    paths: dict[str, Path] = {}
    for name, table in tables.items():
        path = destination / f"{name}.csv"
        if name == "correlation_matrix":
            table.to_csv(path, index=True, index_label="feature", float_format="%.10g")
        else:
            table.to_csv(path, index=False, float_format="%.10g")
        paths[name] = path
    return paths


def plot_missing_heatmap(frame: pd.DataFrame) -> tuple[Figure, Axes]:
    """Plot a missingness heatmap over rows and columns."""

    figure, axes = plt.subplots(figsize=(12.0, 6.5))
    axes.imshow(frame.isna().to_numpy(dtype=int), aspect="auto", cmap="Greys", interpolation="nearest")
    axes.set(title="Missing Value Heatmap", xlabel="Columns", ylabel="Rows")
    axes.set_xticks(range(len(frame.columns)), frame.columns, rotation=90, fontsize=6)
    figure.tight_layout()
    return figure, axes


def plot_correlation_heatmap(correlation: pd.DataFrame) -> tuple[Figure, Axes]:
    """Plot a full feature correlation heatmap."""

    figure, axes = plt.subplots(figsize=(12.0, 10.0))
    image = axes.imshow(correlation, vmin=-1, vmax=1, cmap="RdBu_r", interpolation="nearest")
    axes.set(title="Pearson Feature Correlation")
    axes.set_xticks(range(len(correlation.columns)), correlation.columns, rotation=90, fontsize=5)
    axes.set_yticks(range(len(correlation.index)), correlation.index, fontsize=5)
    figure.colorbar(image, ax=axes, label="Pearson r", fraction=0.046, pad=0.04)
    figure.tight_layout()
    return figure, axes


def plot_feature_histogram(frame: pd.DataFrame, feature: str) -> tuple[Figure, Axes]:
    """Plot one feature histogram."""

    figure, axes = plt.subplots(figsize=(7.0, 4.5))
    axes.hist(frame[feature].dropna(), bins=24, color="#2C7FB8", edgecolor="white")
    axes.set(title=feature, xlabel=feature, ylabel="Trial count")
    _style_axes(axes)
    figure.tight_layout()
    return figure, axes


def plot_feature_boxplot(frame: pd.DataFrame, feature: str) -> tuple[Figure, Axes]:
    """Plot one feature box plot."""

    figure, axes = plt.subplots(figsize=(6.0, 4.0))
    axes.boxplot(frame[feature].dropna(), orientation="vertical", widths=0.45)
    axes.set(title=feature, ylabel=feature, xticks=[])
    _style_axes(axes)
    figure.tight_layout()
    return figure, axes


def plot_pca_variance(pca_summary: pd.DataFrame, cumulative: bool = False) -> tuple[Figure, Axes]:
    """Plot explained or cumulative explained PCA variance."""

    column = "cumulative_explained_variance_ratio" if cumulative else "explained_variance_ratio"
    title = "Cumulative PCA Explained Variance" if cumulative else "PCA Explained Variance"
    figure, axes = plt.subplots(figsize=(7.0, 4.5))
    axes.plot(pca_summary["component"], pca_summary[column], marker="o", color="#2C7FB8")
    axes.set(title=title, xlabel="Component", ylabel="Variance ratio")
    axes.set_ylim(0, 1.05)
    _style_axes(axes)
    figure.tight_layout()
    return figure, axes


def plot_pca_scatter(scores: pd.DataFrame) -> tuple[Figure, Axes]:
    """Plot PC1 versus PC2 scores."""

    figure, axes = plt.subplots(figsize=(6.5, 5.5))
    axes.scatter(scores["PC1"], scores["PC2"], s=20, alpha=0.7, color="#4D9221")
    axes.set(title="PCA Scores: PC1 vs PC2", xlabel="PC1", ylabel="PC2")
    _style_axes(axes)
    figure.tight_layout()
    return figure, axes


def plot_pairwise_scatter(frame: pd.DataFrame, x_feature: str, y_feature: str) -> tuple[Figure, Axes]:
    """Plot one pairwise feature relationship."""

    valid = frame[[x_feature, y_feature]].dropna()
    figure, axes = plt.subplots(figsize=(6.5, 5.0))
    axes.scatter(valid[x_feature], valid[y_feature], s=20, alpha=0.7, color="#756BB1")
    axes.set(title=f"{y_feature} vs {x_feature}", xlabel=x_feature, ylabel=y_feature)
    _style_axes(axes)
    figure.tight_layout()
    return figure, axes


def export_plots(frame: pd.DataFrame, output_dir: str | Path = "reports/plots") -> list[Path]:
    """Export all Prompt 4 EDA plots.

    Args:
        frame: Feature DataFrame.
        output_dir: Destination plot directory.

    Returns:
        Written PNG paths.
    """

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    corr = correlation_matrix(frame)
    pca_summary, scores, _ = pca_analysis(frame)
    plot_jobs = [
        ("missing_heatmap.png", lambda: plot_missing_heatmap(frame)),
        ("correlation_heatmap.png", lambda: plot_correlation_heatmap(corr)),
        ("pca_explained_variance.png", lambda: plot_pca_variance(pca_summary)),
        (
            "pca_cumulative_variance.png",
            lambda: plot_pca_variance(pca_summary, cumulative=True),
        ),
        ("pca_pc1_pc2_scatter.png", lambda: plot_pca_scatter(scores)),
    ]
    pairwise = [
        ("pair_hip_knee_rom.png", "hip_flexion_right_rom", "knee_flexion_right_rom"),
        ("pair_left_right_knee_rom.png", "knee_flexion_left_rom", "knee_flexion_right_rom"),
        ("pair_hip_ankle_rom.png", "hip_flexion_right_rom", "ankle_angle_right_rom"),
        ("pair_left_right_hip_rom.png", "hip_flexion_left_rom", "hip_flexion_right_rom"),
        ("pair_left_right_ankle_rom.png", "ankle_angle_left_rom", "ankle_angle_right_rom"),
    ]
    for filename, x_feature, y_feature in pairwise:
        if x_feature in frame and y_feature in frame:
            plot_jobs.append(
                (
                    filename,
                    lambda x=x_feature, y=y_feature: plot_pairwise_scatter(frame, x, y),
                )
            )
    for feature in get_feature_columns(frame):
        plot_jobs.append((f"hist_{feature}.png", lambda name=feature: plot_feature_histogram(frame, name)))
        plot_jobs.append((f"box_{feature}.png", lambda name=feature: plot_feature_boxplot(frame, name)))
    for filename, plotter in plot_jobs:
        figure, _ = plotter()
        path = destination / filename
        figure.savefig(path, dpi=140, bbox_inches="tight")
        plt.close(figure)
        paths.append(path)
    return paths


def _percent(count: int | float, total: int | float) -> float:
    return float(count / total * 100.0) if total else np.nan


def _minmax(series: pd.Series) -> pd.Series:
    minimum = series.min()
    maximum = series.max()
    if not np.isfinite(minimum) or not np.isfinite(maximum) or maximum == minimum:
        return pd.Series(0.0, index=series.index)
    return (series - minimum) / (maximum - minimum)


def _style_axes(ax: Axes) -> None:
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.7, alpha=0.75)
    ax.spines[["top", "right"]].set_visible(False)
