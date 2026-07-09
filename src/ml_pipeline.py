"""Machine-learning data preparation infrastructure for JumpGuard AI."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

import json

import numpy as np
import pandas as pd

from .eda import get_feature_columns, load_feature_table
from .feature_engineering import IDENTIFIER_COLUMNS


SplitName = Literal["train", "validation", "test"]
ScalerName = Literal["standard", "minmax", "robust", "none"]
MissingPolicy = Literal["drop_rows", "median_impute"]
SelectionStrategy = Literal["all", "top_n", "variance_threshold", "correlation_filter"]


@dataclass(frozen=True)
class MLConfig:
    """Configuration for deterministic ML data preparation.

    Args:
        random_seed: Seed used for participant shuffling.
        train_ratio: Fraction of participants assigned to train.
        validation_ratio: Fraction of participants assigned to validation.
        test_ratio: Fraction of participants assigned to test.
        missing_policy: Missing predictor handling policy.
        scaler: Scaling strategy fit only on the training split.
        feature_selection: Feature selector strategy fit only on training data.
        top_n_features: Number of Prompt 4 ranked features for ``top_n``.
        variance_threshold: Minimum training variance for variance filtering.
        correlation_threshold: Maximum absolute training correlation for correlation filtering.
        cross_validation_folds: Participant-aware cross-validation fold count.
        feature_ranking_path: Prompt 4 feature-ranking CSV path.
    """

    random_seed: int = 42
    train_ratio: float = 0.70
    validation_ratio: float = 0.15
    test_ratio: float = 0.15
    missing_policy: MissingPolicy = "drop_rows"
    scaler: ScalerName = "standard"
    feature_selection: SelectionStrategy = "all"
    top_n_features: int = 20
    variance_threshold: float = 0.0
    correlation_threshold: float = 0.95
    cross_validation_folds: int = 5
    feature_ranking_path: str = "reports/feature_ranking.csv"

    def __post_init__(self) -> None:
        """Validate configuration values."""

        ratios = (self.train_ratio, self.validation_ratio, self.test_ratio)
        if any(ratio < 0 for ratio in ratios):
            raise ValueError("Split ratios must be non-negative.")
        if not np.isclose(sum(ratios), 1.0):
            raise ValueError("Split ratios must sum to 1.0.")
        if self.cross_validation_folds < 2:
            raise ValueError("cross_validation_folds must be at least 2.")
        if self.top_n_features < 1:
            raise ValueError("top_n_features must be positive.")
        if self.variance_threshold < 0:
            raise ValueError("variance_threshold must be non-negative.")
        if not 0 < self.correlation_threshold <= 1:
            raise ValueError("correlation_threshold must be in (0, 1].")

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable configuration mapping."""

        return asdict(self)


@dataclass(frozen=True)
class SplitDefinition:
    """Participant-aware train/validation/test split definition."""

    train_participants: tuple[int, ...]
    validation_participants: tuple[int, ...]
    test_participants: tuple[int, ...]

    def to_frame(self) -> pd.DataFrame:
        """Return one row per participant with split assignment."""

        rows = []
        for split_name, participants in (
            ("train", self.train_participants),
            ("validation", self.validation_participants),
            ("test", self.test_participants),
        ):
            rows.extend(
                {"participant_id": participant_id, "split": split_name}
                for participant_id in participants
            )
        return pd.DataFrame(rows).sort_values("participant_id").reset_index(drop=True)


@dataclass(frozen=True)
class PreprocessingArtifact:
    """Fitted preprocessing parameters."""

    feature_names: tuple[str, ...]
    missing_policy: MissingPolicy
    scaler: ScalerName
    impute_values: dict[str, float]
    center: dict[str, float]
    scale: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable artifact."""

        return {
            "feature_names": list(self.feature_names),
            "missing_policy": self.missing_policy,
            "scaler": self.scaler,
            "impute_values": self.impute_values,
            "center": self.center,
            "scale": self.scale,
        }


@dataclass(frozen=True)
class FeatureSelectionArtifact:
    """Fitted feature-selection parameters."""

    strategy: SelectionStrategy
    selected_features: tuple[str, ...]
    removed_features: tuple[str, ...]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable artifact."""

        return {
            "strategy": self.strategy,
            "selected_features": list(self.selected_features),
            "removed_features": list(self.removed_features),
            "reason": self.reason,
        }


@dataclass(frozen=True)
class MLPreparationResult:
    """All outputs from deterministic ML data preparation."""

    config: MLConfig
    split_definition: SplitDefinition
    split_summary: pd.DataFrame
    preprocessing_summary: pd.DataFrame
    feature_selection_summary: pd.DataFrame
    cross_validation_summary: pd.DataFrame
    leakage_summary: pd.DataFrame
    preprocessing_artifact: PreprocessingArtifact
    feature_selection_artifact: FeatureSelectionArtifact


def default_ml_config() -> MLConfig:
    """Return the default Prompt 5 ML preparation configuration."""

    return MLConfig()


def participant_split(frame: pd.DataFrame, config: MLConfig) -> SplitDefinition:
    """Create a deterministic participant-aware train/validation/test split.

    Args:
        frame: Feature table with ``participant_id`` metadata.
        config: ML preparation configuration.

    Returns:
        SplitDefinition with each participant assigned exactly once.
    """

    participants = np.array(sorted(frame["participant_id"].dropna().astype(int).unique()))
    rng = np.random.default_rng(config.random_seed)
    shuffled = participants.copy()
    rng.shuffle(shuffled)
    n_total = len(shuffled)
    n_train = int(round(config.train_ratio * n_total))
    n_validation = int(round(config.validation_ratio * n_total))
    if n_train + n_validation > n_total:
        n_validation = n_total - n_train
    train = tuple(sorted(int(item) for item in shuffled[:n_train]))
    validation = tuple(sorted(int(item) for item in shuffled[n_train : n_train + n_validation]))
    test = tuple(sorted(int(item) for item in shuffled[n_train + n_validation :]))
    return SplitDefinition(train, validation, test)


def apply_split(frame: pd.DataFrame, split_definition: SplitDefinition) -> pd.DataFrame:
    """Attach split labels to a feature table."""

    split_map = {
        participant_id: split_name
        for split_name, participants in (
            ("train", split_definition.train_participants),
            ("validation", split_definition.validation_participants),
            ("test", split_definition.test_participants),
        )
        for participant_id in participants
    }
    assigned = frame.copy()
    assigned["split"] = assigned["participant_id"].map(split_map)
    if assigned["split"].isna().any():
        raise ValueError("Every participant must be assigned to exactly one split.")
    return assigned


def split_summary(frame: pd.DataFrame, split_definition: SplitDefinition) -> pd.DataFrame:
    """Summarize split row counts, participants, and missingness."""

    assigned = apply_split(frame, split_definition)
    features = get_feature_columns(frame)
    rows = []
    for split_name in ("train", "validation", "test"):
        subset = assigned[assigned["split"] == split_name]
        rows.append(
            {
                "split": split_name,
                "participant_count": int(subset["participant_id"].nunique()),
                "row_count": int(len(subset)),
                "empty_trial_rows": int(subset["is_empty"].sum()) if "is_empty" in subset else 0,
                "complete_feature_rows": int(subset.loc[:, features].notna().all(axis=1).sum()),
                "missing_feature_values": int(subset.loc[:, features].isna().sum().sum()),
            }
        )
    return pd.DataFrame(rows)


def validate_no_participant_leakage(split_definition: SplitDefinition) -> pd.DataFrame:
    """Validate that no participant appears in more than one split."""

    split_sets = {
        "train": set(split_definition.train_participants),
        "validation": set(split_definition.validation_participants),
        "test": set(split_definition.test_participants),
    }
    rows = []
    for left_name, right_name in (
        ("train", "validation"),
        ("train", "test"),
        ("validation", "test"),
    ):
        overlap = sorted(split_sets[left_name] & split_sets[right_name])
        rows.append(
            {
                "check": f"{left_name}_vs_{right_name}",
                "overlap_count": len(overlap),
                "overlapping_participants": ",".join(str(item) for item in overlap),
                "passed": len(overlap) == 0,
            }
        )
    return pd.DataFrame(rows)


def prepare_predictor_matrix(
    frame: pd.DataFrame,
    feature_names: list[str] | tuple[str, ...] | None = None,
) -> pd.DataFrame:
    """Return predictor columns only, excluding metadata by default."""

    features = list(feature_names or get_feature_columns(frame))
    return frame.loc[:, features].copy()


def fit_preprocessor(
    train_frame: pd.DataFrame,
    feature_names: list[str] | tuple[str, ...],
    config: MLConfig,
) -> PreprocessingArtifact:
    """Fit missing-value and scaling parameters on training rows only."""

    train = prepare_predictor_matrix(train_frame, feature_names)
    impute_values: dict[str, float] = {}
    fit_frame = train.copy()
    if config.missing_policy == "median_impute":
        impute_values = {
            feature: float(fit_frame[feature].median(skipna=True))
            for feature in fit_frame.columns
        }
        fit_frame = fit_frame.fillna(impute_values)
    elif config.missing_policy == "drop_rows":
        fit_frame = fit_frame.dropna(axis=0, how="any")
    else:
        raise ValueError(f"Unsupported missing_policy: {config.missing_policy}")
    if fit_frame.empty:
        raise ValueError("Training data has no complete rows after missing-value policy.")

    center: dict[str, float] = {}
    scale: dict[str, float] = {}
    if config.scaler == "standard":
        center = {feature: float(fit_frame[feature].mean()) for feature in fit_frame.columns}
        scale = {
            feature: _nonzero(float(fit_frame[feature].std(ddof=0)))
            for feature in fit_frame.columns
        }
    elif config.scaler == "minmax":
        center = {feature: float(fit_frame[feature].min()) for feature in fit_frame.columns}
        scale = {
            feature: _nonzero(float(fit_frame[feature].max() - fit_frame[feature].min()))
            for feature in fit_frame.columns
        }
    elif config.scaler == "robust":
        center = {feature: float(fit_frame[feature].median()) for feature in fit_frame.columns}
        scale = {
            feature: _nonzero(
                float(fit_frame[feature].quantile(0.75) - fit_frame[feature].quantile(0.25))
            )
            for feature in fit_frame.columns
        }
    elif config.scaler == "none":
        center = {feature: 0.0 for feature in fit_frame.columns}
        scale = {feature: 1.0 for feature in fit_frame.columns}
    else:
        raise ValueError(f"Unsupported scaler: {config.scaler}")
    return PreprocessingArtifact(
        feature_names=tuple(feature_names),
        missing_policy=config.missing_policy,
        scaler=config.scaler,
        impute_values=impute_values,
        center=center,
        scale=scale,
    )


def transform_features(
    frame: pd.DataFrame,
    artifact: PreprocessingArtifact,
) -> pd.DataFrame:
    """Apply a fitted preprocessor to rows from any split."""

    data = prepare_predictor_matrix(frame, artifact.feature_names)
    if artifact.missing_policy == "median_impute":
        data = data.fillna(artifact.impute_values)
    elif artifact.missing_policy == "drop_rows":
        data = data.dropna(axis=0, how="any")
    else:
        raise ValueError(f"Unsupported missing_policy: {artifact.missing_policy}")
    for feature in artifact.feature_names:
        data[feature] = (data[feature] - artifact.center[feature]) / artifact.scale[feature]
    return data


def preprocessing_summary(
    frame: pd.DataFrame,
    split_definition: SplitDefinition,
    artifact: PreprocessingArtifact,
) -> pd.DataFrame:
    """Summarize train-fitted preprocessing effects by split."""

    assigned = apply_split(frame, split_definition)
    rows = []
    for split_name in ("train", "validation", "test"):
        subset = assigned[assigned["split"] == split_name]
        transformed = transform_features(subset, artifact)
        rows.append(
            {
                "split": split_name,
                "input_rows": int(len(subset)),
                "output_rows": int(len(transformed)),
                "rows_removed_by_missing_policy": int(len(subset) - len(transformed)),
                "feature_count": len(artifact.feature_names),
                "missing_policy": artifact.missing_policy,
                "scaler": artifact.scaler,
                "fit_source": "train_only",
            }
        )
    return pd.DataFrame(rows)


def fit_feature_selector(
    train_frame: pd.DataFrame,
    feature_names: list[str] | tuple[str, ...],
    config: MLConfig,
) -> FeatureSelectionArtifact:
    """Fit feature-selection infrastructure on training data only."""

    features = list(feature_names)
    train = prepare_predictor_matrix(train_frame, features)
    complete_train = train.dropna(axis=0, how="any")
    if complete_train.empty:
        raise ValueError("Feature selection requires complete training rows.")

    if config.feature_selection == "all":
        selected = features
        removed: list[str] = []
        reason = "All Prompt 3 biomechanical features retained."
    elif config.feature_selection == "top_n":
        ranking_path = Path(config.feature_ranking_path)
        if not ranking_path.exists():
            raise FileNotFoundError(f"Feature ranking file not found: {ranking_path}")
        ranking = pd.read_csv(ranking_path)
        ranked = [feature for feature in ranking["feature"].tolist() if feature in features]
        selected = ranked[: config.top_n_features]
        removed = [feature for feature in features if feature not in selected]
        reason = f"Selected top {len(selected)} features from Prompt 4 ranking."
    elif config.feature_selection == "variance_threshold":
        variances = complete_train.var(axis=0, ddof=0)
        selected = [
            feature for feature in features if float(variances[feature]) >= config.variance_threshold
        ]
        removed = [feature for feature in features if feature not in selected]
        reason = f"Removed features with training variance below {config.variance_threshold}."
    elif config.feature_selection == "correlation_filter":
        selected = _correlation_filter(complete_train, features, config.correlation_threshold)
        removed = [feature for feature in features if feature not in selected]
        reason = (
            "Greedy correlation filter fit on training data with absolute threshold "
            f"{config.correlation_threshold}."
        )
    else:
        raise ValueError(f"Unsupported feature_selection: {config.feature_selection}")

    if not selected:
        raise ValueError("Feature selection produced zero selected features.")
    return FeatureSelectionArtifact(
        strategy=config.feature_selection,
        selected_features=tuple(selected),
        removed_features=tuple(removed),
        reason=reason,
    )


def feature_selection_summary(artifact: FeatureSelectionArtifact) -> pd.DataFrame:
    """Return selected and removed features as a summary table."""

    rows = [
        {
            "feature": feature,
            "selected": True,
            "strategy": artifact.strategy,
            "reason": artifact.reason,
        }
        for feature in artifact.selected_features
    ]
    rows.extend(
        {
            "feature": feature,
            "selected": False,
            "strategy": artifact.strategy,
            "reason": artifact.reason,
        }
        for feature in artifact.removed_features
    )
    return pd.DataFrame(rows)


def participant_cross_validation(
    frame: pd.DataFrame,
    config: MLConfig,
) -> pd.DataFrame:
    """Create participant-aware cross-validation folds."""

    participants = np.array(sorted(frame["participant_id"].dropna().astype(int).unique()))
    if config.cross_validation_folds > len(participants):
        raise ValueError("cross_validation_folds cannot exceed participant count.")
    rng = np.random.default_rng(config.random_seed)
    shuffled = participants.copy()
    rng.shuffle(shuffled)
    folds = np.array_split(shuffled, config.cross_validation_folds)
    rows = []
    for fold_index, validation_participants in enumerate(folds, start=1):
        validation_set = set(int(item) for item in validation_participants)
        train_set = set(int(item) for item in participants) - validation_set
        validation_rows = frame[frame["participant_id"].isin(validation_set)]
        train_rows = frame[frame["participant_id"].isin(train_set)]
        rows.append(
            {
                "fold": fold_index,
                "train_participant_count": len(train_set),
                "validation_participant_count": len(validation_set),
                "train_row_count": int(len(train_rows)),
                "validation_row_count": int(len(validation_rows)),
                "participant_overlap_count": len(train_set & validation_set),
                "validation_participants": ",".join(str(item) for item in sorted(validation_set)),
            }
        )
    return pd.DataFrame(rows)


def prepare_ml_data(
    frame: pd.DataFrame | None = None,
    config: MLConfig | None = None,
) -> MLPreparationResult:
    """Run deterministic Prompt 5 ML data preparation.

    Args:
        frame: Optional feature table; defaults to ``data/processed/features.csv``.
        config: Optional MLConfig; defaults to ``default_ml_config``.

    Returns:
        MLPreparationResult containing summaries and fitted artifacts.
    """

    config = config or default_ml_config()
    frame = frame.copy() if frame is not None else load_feature_table()
    features = get_feature_columns(frame)
    split_definition = participant_split(frame, config)
    assigned = apply_split(frame, split_definition)
    train_frame = assigned[assigned["split"] == "train"]
    selector = fit_feature_selector(train_frame, features, config)
    preprocessor = fit_preprocessor(train_frame, selector.selected_features, config)
    return MLPreparationResult(
        config=config,
        split_definition=split_definition,
        split_summary=split_summary(frame, split_definition),
        preprocessing_summary=preprocessing_summary(frame, split_definition, preprocessor),
        feature_selection_summary=feature_selection_summary(selector),
        cross_validation_summary=participant_cross_validation(frame, config),
        leakage_summary=validate_no_participant_leakage(split_definition),
        preprocessing_artifact=preprocessor,
        feature_selection_artifact=selector,
    )


def export_ml_outputs(
    result: MLPreparationResult,
    output_dir: str | Path = "reports",
    config_path: str | Path = "configs/default_ml_config.yaml",
    artifact_dir: str | Path = "reports/ml_artifacts",
) -> dict[str, Path]:
    """Persist Prompt 5 summaries, configuration, and fitted artifacts."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    artifacts = Path(artifact_dir)
    artifacts.mkdir(parents=True, exist_ok=True)
    paths = {
        "split_summary": output / "split_summary.csv",
        "preprocessing_summary": output / "preprocessing_summary.csv",
        "feature_selection_summary": output / "feature_selection_summary.csv",
        "cross_validation_summary": output / "cross_validation_summary.csv",
        "leakage_summary": output / "leakage_summary.csv",
        "split_definitions": artifacts / "split_definitions.csv",
        "preprocessing_artifact": artifacts / "preprocessing_artifact.json",
        "feature_selection_artifact": artifacts / "feature_selection_artifact.json",
        "config": Path(config_path),
        "config_snapshot": artifacts / "config_snapshot.yaml",
    }
    result.split_summary.to_csv(paths["split_summary"], index=False, float_format="%.10g")
    result.preprocessing_summary.to_csv(
        paths["preprocessing_summary"], index=False, float_format="%.10g"
    )
    result.feature_selection_summary.to_csv(paths["feature_selection_summary"], index=False)
    result.cross_validation_summary.to_csv(paths["cross_validation_summary"], index=False)
    result.leakage_summary.to_csv(paths["leakage_summary"], index=False)
    result.split_definition.to_frame().to_csv(paths["split_definitions"], index=False)
    _write_json(paths["preprocessing_artifact"], result.preprocessing_artifact.to_dict())
    _write_json(paths["feature_selection_artifact"], result.feature_selection_artifact.to_dict())
    write_config(result.config, paths["config"])
    write_config(result.config, paths["config_snapshot"])
    return paths


def write_config(config: MLConfig, path: str | Path) -> Path:
    """Write MLConfig as a simple deterministic YAML file."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Default Prompt 5 ML infrastructure configuration"]
    for key, value in config.to_dict().items():
        lines.append(f"{key}: {json.dumps(value)}")
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return destination


def mean_absolute_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute mean absolute error for future evaluation code."""

    actual, predicted = _validate_metric_inputs(y_true, y_pred)
    return float(np.mean(np.abs(actual - predicted)))


def root_mean_squared_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute root mean squared error for future evaluation code."""

    actual, predicted = _validate_metric_inputs(y_true, y_pred)
    return float(np.sqrt(np.mean((actual - predicted) ** 2)))


def accuracy_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute classification accuracy for future evaluation code."""

    actual, predicted = _validate_metric_inputs(y_true, y_pred)
    return float(np.mean(actual == predicted))


def _correlation_filter(
    frame: pd.DataFrame,
    features: list[str],
    threshold: float,
) -> list[str]:
    selected: list[str] = []
    corr = frame.loc[:, features].corr().abs()
    for feature in features:
        if all(corr.loc[feature, kept] < threshold for kept in selected):
            selected.append(feature)
    return selected


def _nonzero(value: float) -> float:
    return value if np.isfinite(value) and value != 0.0 else 1.0


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _validate_metric_inputs(y_true: np.ndarray, y_pred: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    actual = np.asarray(y_true)
    predicted = np.asarray(y_pred)
    if actual.shape != predicted.shape:
        raise ValueError("Metric inputs must have the same shape.")
    if actual.size == 0:
        raise ValueError("Metric inputs must not be empty.")
    return actual, predicted
