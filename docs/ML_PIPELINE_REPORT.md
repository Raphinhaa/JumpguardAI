# ML Pipeline Report

## Scope

Prompt 5 builds reusable machine-learning infrastructure on top of the existing Prompt 3 feature table and Prompt 4 EDA outputs. It does not create new biomechanical features, modify feature extraction, modify the EDA layer, train production models, benchmark models, or infer target labels.

The pipeline uses `data/processed/features.csv`. The 57 biomechanical feature columns are predictors by default. `participant_id`, `trial_slot`, `trial_name`, `condition`, and `is_empty` are treated as metadata and are excluded from predictor matrices unless a future prompt explicitly changes that policy.

## Default Configuration

The default configuration was written to `configs/default_ml_config.yaml` and snapshotted to `reports/ml_artifacts/config_snapshot.yaml`.

| Setting | Value |
| --- | ---: |
| Random seed | 42 |
| Train ratio | 0.70 |
| Validation ratio | 0.15 |
| Test ratio | 0.15 |
| Missing policy | `drop_rows` |
| Scaler | `standard` |
| Feature selection | `all` |
| Cross-validation folds | 5 |

## Participant-Aware Splitting

Participant-aware splits were generated with no participant appearing in more than one split. Split summaries were exported to `reports/split_summary.csv`, and exact participant assignments were serialized to `reports/ml_artifacts/split_definitions.csv`.

| Split | Participants | Rows |
| --- | ---: | ---: |
| Train | 30 | 180 |
| Validation | 6 | 36 |
| Test | 7 | 42 |

Leakage validation was exported to `reports/leakage_summary.csv`. Participant-overlap checks passed: `True`.

## Preprocessing Pipeline

Preprocessing was fit only on the training split and then reused for validation and test. The default missing-value policy is `drop_rows`, which removes rows with missing predictor values from transformed matrices. This removes empty trial rows from modeling matrices while preserving them in the original feature table and split summaries.

The default scaler is `standard`, implemented as `(x - training_mean) / training_population_std`. Fitted preprocessing parameters were serialized to `reports/ml_artifacts/preprocessing_artifact.json`; split-level effects were exported to `reports/preprocessing_summary.csv`.

Rows removed by the default missing policy across transformed splits: 9.

## Feature Selection Infrastructure

Feature selection is configurable and fit only on training data. Supported strategies are:

- `all`: retain all Prompt 3 biomechanical predictors
- `top_n`: select top-N features from `reports/feature_ranking.csv`
- `variance_threshold`: keep features meeting a training variance threshold
- `correlation_filter`: greedily remove highly correlated predictors using training correlations

The default strategy is `all`, so 57 features are selected and 0 are removed. The default selection artifact was serialized to `reports/ml_artifacts/feature_selection_artifact.json`, and the feature-level summary was exported to `reports/feature_selection_summary.csv`.

## Cross-Validation

Participant-aware cross-validation was created with 5 folds. Each participant appears in the validation fold exactly once and never appears in both train and validation within the same fold. Fold summaries were exported to `reports/cross_validation_summary.csv`. Total train/validation overlap across folds: 0.

## Evaluation Infrastructure

Reusable metric interfaces were added for future prompts: mean absolute error, root mean squared error, and accuracy. These utilities validate input shape and do not train or evaluate a production model in Prompt 5.

## Serialization and Reproducibility

Persisted artifacts:

- `configs/default_ml_config.yaml`
- `reports/ml_artifacts/config_snapshot.yaml`
- `reports/ml_artifacts/split_definitions.csv`
- `reports/ml_artifacts/preprocessing_artifact.json`
- `reports/ml_artifacts/feature_selection_artifact.json`

All outputs are deterministic for the same feature table and configuration seed.

## Validation Results

- No participant leakage across train/validation/test splits.
- Preprocessing fit source is `train_only` for every split summary row.
- Feature selection is fit on training data only.
- Metadata columns are excluded from predictor matrices by default.
- No target labels were assumed or inferred.
- No production ML model was trained.

## Ready for Prompt 6

The repository now has participant-safe split definitions, configurable preprocessing, configurable feature-selection infrastructure, participant-aware cross-validation, deterministic configuration, serialized preparation artifacts, and metric interfaces. Prompt 6 can build training logic on these prepared abstractions without revisiting feature extraction or EDA.
