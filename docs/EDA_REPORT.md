# EDA Report

## Scope

Prompt 4 analyzes the existing Prompt 3 feature table at `data/processed/features.csv`. No features were created, removed, imputed, or recalculated for this analysis. Empty metadata-defined trial rows are retained and represented as missing feature values, matching the Prompt 3 feature extraction behavior.

## Dataset Validation

| Metric | Value |
| --- | ---: |
| Rows | 258 |
| Columns | 62 |
| Identifier columns | 5 |
| Numeric feature columns | 57 |
| Duplicate full rows | 0 |
| Duplicate participant/trial rows | 0 |
| Empty trial rows | 9 |
| Complete feature rows | 249 |
| Missing values total | 513 |
| Infinite feature values | 0 |

The table has the expected Prompt 3 structure: 5 identifiers plus 57 numeric biomechanical features. The 9 empty trial rows account for all missing feature values: each empty row has 57 missing features, for 513 total missing values. No duplicate participant/trial rows or infinite feature values were detected.

## Descriptive Statistics

Per-feature mean, median, population standard deviation, minimum, maximum, quartiles, IQR, skewness, and kurtosis were exported to `reports/descriptive_statistics.csv`. Statistics are computed over observed values only; missing values from empty trials are not imputed.

## Missing Values

Missingness was exported to `reports/missing_summary.csv` and visualized in `reports/plots/missing_heatmap.png`. Identifier columns have no missing values. All 57 numeric features have 9 missing values (3.49% of rows), corresponding exactly to the 9 empty trial rows.

## Feature Distributions and Outliers

Histogram and box-plot PNGs were generated for every numeric feature in `reports/plots/`. IQR and Z-score outlier counts were exported to `reports/outlier_summary.csv`. IQR outliers were detected for 43 features, and Z-score outliers above the absolute threshold of 3.0 were detected for 34 features. Outliers were summarized only; no values were removed or winsorized.

## Correlation and Redundancy

The Pearson correlation matrix was exported to `reports/correlation_matrix.csv` and visualized in `reports/plots/correlation_heatmap.png`. Using an absolute correlation threshold of 0.95, 29 highly correlated feature pairs were identified and exported to `reports/high_correlation_pairs.csv`. These pairs are recommendations for future review only; no redundant features were deleted.

## Low Variance Features

Variance diagnostics were exported to `reports/feature_variance.csv`. Near-constant features are defined as variance <= 1e-8; 0 features met that threshold. Very low variance features are defined as features at or below the 10th percentile of positive variances; 6 features were flagged. These flags are preparation for Prompt 5 and do not modify the feature set.

## PCA

PCA was run for visualization only using complete feature rows. This excludes the 9 empty trial rows because PCA requires observed numeric values and Prompt 4 forbids imputation. The first component explains 0.2547 of standardized feature variance, and the first two components cumulatively explain 0.4641. PCA outputs were exported to `reports/pca_summary.csv`, `reports/pca_loadings.csv`, and `reports/pca_scores.csv`; plots were exported for explained variance, cumulative variance, and PC1 vs PC2.

## Pairwise Relationships

Pairwise scatter plots were generated for the requested biomechanical relationships where the Prompt 3 feature names support them: hip vs knee ROM, left vs right knee ROM, hip vs ankle ROM, left vs right hip ROM, and left vs right ankle ROM. These plots are stored in `reports/plots/`.

## Target Leakage Check

The feature table includes identifier and metadata columns: `participant_id`, `trial_slot`, `trial_name`, `condition`, and `is_empty`. These columns should not be treated as biomechanical model inputs by default. `participant_id` can leak participant identity, `trial_slot` and `trial_name` can encode repeated-measure ordering, `condition` can encode fatigue grouping, and `is_empty` encodes missingness rather than movement. Future supervised modeling should explicitly separate identifiers/metadata from numeric biomechanical features and use participant-aware validation splits.

No supervised target label was identified in `data/processed/features.csv`, so supervised feature selection was not performed.

## Feature Selection Preparation

Unsupervised feature ranking was exported to `reports/feature_ranking.csv`. The ranking combines normalized feature variance, average absolute PCA loading magnitude, and a non-redundancy score derived from maximum absolute correlation. It is a candidate list for future modeling review, not an automatic selection step.

Top 10 candidate features:

| Rank | Feature | Score |
| ---: | --- | ---: |
| 1 | `hip_flexion_right_variance` | 0.4324 |
| 2 | `knee_flexion_rom_symmetry_index` | 0.4123 |
| 3 | `hip_flexion_left_variance` | 0.4067 |
| 4 | `knee_flexion_rom_absolute_difference` | 0.4045 |
| 5 | `knee_flexion_rom_percent_difference` | 0.3813 |
| 6 | `hip_flexion_rom_symmetry_index` | 0.3775 |
| 7 | `hip_flexion_right_maximum` | 0.3745 |
| 8 | `hip_flexion_left_maximum` | 0.3694 |
| 9 | `ankle_angle_rom_symmetry_index` | 0.3440 |
| 10 | `ankle_angle_left_maximum` | 0.3204 |

## Generated Outputs

Required CSV outputs:

- `reports/descriptive_statistics.csv`
- `reports/missing_summary.csv`
- `reports/correlation_matrix.csv`
- `reports/feature_variance.csv`
- `reports/outlier_summary.csv`
- `reports/pca_summary.csv`
- `reports/feature_ranking.csv`

Additional validation/support outputs:

- `reports/validation_summary.csv`
- `reports/high_correlation_pairs.csv`
- `reports/pca_loadings.csv`
- `reports/pca_scores.csv`
- `reports/plots/` (124 PNG files)

## Prompt 5 Recommendations

- Keep identifier and metadata columns out of biomechanical feature matrices unless a later prompt explicitly models metadata.
- Use participant-aware train/test splitting to avoid repeated-trial identity leakage.
- Review highly correlated feature families before model fitting, but defer removal until modeling objectives and validation strategy are defined.
- Treat empty trial rows as missing-data records; do not impute or drop them without an explicit downstream policy.
- Consider variance and PCA-loading rankings as exploratory signals only, not validated predictors.
