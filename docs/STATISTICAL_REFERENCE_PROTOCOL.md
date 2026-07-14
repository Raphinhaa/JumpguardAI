# Statistical Reference Protocol

This protocol defines future normative statistics only after videos have passed QC and have been processed by the existing JumpGuard pipeline without algorithmic changes.

## Feature Source

Use the existing 57-feature JumpGuard schema documented in `docs/JUMPGUARD_MEASUREMENT_STANDARD.md`. Do not add features, alter formulas, or reinterpret MediaPipe-derived geometric angles as laboratory inverse-kinematics angles.

## Per-Feature Reference Statistics

For every feature with sufficient finite observations, compute:

| Statistic | Definition |
|---|---|
| Count | Number of finite observations. |
| Missing count | Number of videos where the feature is missing or NaN. |
| Mean | Arithmetic mean. |
| Median | Median. |
| Standard deviation | Population and sample definitions must be explicitly stated; current project feature variance uses population `ddof=0`, but reference confidence intervals should state their estimator. |
| Percentiles | 1st, 2.5th, 5th, 25th, 50th, 75th, 95th, 97.5th, and 99th percentiles. |
| Central 90 percent interval | 5th to 95th percentile. |
| Central 95 percent interval | 2.5th to 97.5th percentile. |
| Confidence intervals | Bootstrap confidence intervals for the mean, median, and selected percentiles, with seed and resampling count documented. |

## Stratification

Stratification is allowed only when metadata are sufficiently documented and sample sizes are adequate. Candidate strata include sex/gender, age band, sport/activity level, task type, camera view, and dataset source. If metadata are missing, report unknown rather than pooling as healthy normative data.

## Sample-Size Recommendations

| Stage | Minimum target | Purpose |
|---|---|---|
| Feasibility pilot | 20 to 30 usable videos after QC | Validate pipeline throughput and missingness patterns only. |
| Preliminary normative reference | At least 100 usable healthy videos from a standardized protocol | Estimate broad distributions with uncertainty. |
| Robust stratified reference | At least 100 usable videos per planned stratum | Support subgroup summaries without unstable intervals. |

These are planning targets, not clinical thresholds. Final adequacy must be judged by missingness, interval width, repeatability, and whether participant/task metadata support the intended comparison.

## Missing Data Policy

Report feature-level missingness for every dataset and every stratum. Do not impute missing landmarks or features for normative statistics unless a future validated imputation protocol is explicitly approved.
