# Biomechanical Intelligence Report

## Scope

Prompt 6 adds an interpretable Biomechanical Intelligence Engine on top of the existing Dataset, Feature Engineering, EDA, and ML infrastructure. It does not bypass earlier abstractions, create new biomechanical features, train predictive models, produce probabilistic injury estimates, diagnose injury, or apply clinical thresholds.

The engine treats `participant_id` as the athlete identifier because that is the only stable athlete-level identifier available in the feature table. Trial-level Prompt 3 features are aggregated to athlete-level means across observed non-empty trials, then compared with the participant-level reference population derived from the same dataset.

## Generated Outputs

Required outputs:

- `reports/athlete_summary.csv`
- `reports/population_statistics.csv`
- `reports/athlete_percentiles.csv`
- `docs/BIOMECHANICAL_INTELLIGENCE_REPORT.md`
- `notebooks/06_biomechanical_intelligence.ipynb`

Supporting outputs:

- `reports/biomechanical_observations.csv`
- `reports/biomechanical_knowledge_mapping.csv`
- `reports/biomechanical_intelligence_plots/` (10 PNG files)

## Methodology

Input rows: 258. Athlete summaries: 43. Measurable biomechanical features: 57. Athlete-feature percentile rows: 2451.

Population statistics are computed over athlete-level feature means, not raw trial rows, so each participant contributes at most one value per feature to the reference distribution. For each feature, the engine exports count, mean, population standard deviation, minimum, 5th percentile, 25th percentile, median, 75th percentile, 95th percentile, and maximum.

Athlete comparisons include percentile and Z-score:

- Percentile: percentage of non-missing reference athletes with values less than or equal to the athlete value.
- Z-score: `(athlete_value - population_mean) / population_std` using population standard deviation.

Reference counts range from 42 to 42 athletes depending on feature availability. Participants with no observed non-empty trials, currently [44], receive missing athlete-level feature comparisons rather than inferred values.

## Movement Assessment Coverage

The engine generates interpretable assessments for measurable feature families:

- Knee mechanics: knee flexion descriptors and ROM features.
- Hip mechanics: hip flexion descriptors and ROM features.
- Ankle mechanics: ankle angle descriptors and ROM features.
- Bilateral symmetry: ROM absolute difference, percent difference, and symmetry index features.
- Joint variability: standard deviation and variance features.
- Movement consistency: time-to-peak features.

Every observation includes the triggering feature, numeric value, percentile, Z-score, population comparison, plain-language explanation, and literature concept mapping.

## Observation Rules

Observations are descriptive flags for unusual dataset-relative values. A feature is flagged when its athlete-level value is at or beyond the 5th or 95th percentile, or has an absolute Z-score of at least 2.0. These are statistical rules for explanation, not clinical thresholds. Generated observations: 286.

Example observations:

| Athlete | Category | Feature | Percentile | Z-score | Comparison |
| ---: | --- | --- | ---: | ---: | --- |
| 1 | ankle | `ankle_angle_left_median` | 4.8 | -1.60 | below the reference mean by 1.60 SD |
| 1 | ankle | `ankle_angle_right_median` | 2.4 | -1.68 | below the reference mean by 1.68 SD |
| 1 | hip | `hip_flexion_left_maximum` | 2.4 | -2.03 | below the reference mean by 2.03 SD |
| 1 | hip | `hip_flexion_right_maximum` | 2.4 | -1.98 | below the reference mean by 1.98 SD |
| 2 | ankle | `ankle_angle_left_maximum` | 95.2 | 1.39 | above the reference mean by 1.39 SD |
| 2 | hip | `hip_flexion_left_time_to_peak` | 97.6 | 1.77 | above the reference mean by 1.77 SD |
| 2 | hip | `hip_flexion_right_time_to_peak` | 95.2 | 1.61 | above the reference mean by 1.61 SD |
| 2 | symmetry | `knee_flexion_rom_percent_difference` | 4.8 | -1.19 | below the reference mean by 1.19 SD |
| 3 | ankle | `ankle_angle_left_mean` | 95.2 | 1.83 | above the reference mean by 1.83 SD |
| 3 | ankle | `ankle_angle_left_median` | 95.2 | 1.63 | above the reference mean by 1.63 SD |
| 3 | ankle | `ankle_angle_left_minimum` | 97.6 | 2.22 | above the reference mean by 2.22 SD |
| 3 | ankle | `ankle_angle_left_std` | 2.4 | -1.66 | below the reference mean by 1.66 SD |

## Literature Mapping

The knowledge layer maps feature families to published ACL and jump-landing biomechanics concepts using cautious language only. It does not state causation and does not assign risk probabilities. Current mappings use language such as "commonly evaluated in," "discussed in," and "descriptive."

Configured source anchors:

- Hewett et al. 2005, knee valgus and neuromuscular-control biomechanics, https://doi.org/10.1177/0363546504269591
- Padua et al. 2009, Landing Error Scoring System and jump-landing biomechanics, https://doi.org/10.1177/0363546509343200
- Paterno et al. 2010, landing biomechanics and limb symmetry after ACL reconstruction, https://doi.org/10.1177/0363546510376053
- Krosshaug et al. 2007, video analysis of ACL injury mechanisms, https://doi.org/10.1177/0363546507299489

## Athlete Report Content

The generated CSV outputs support structured athlete reports containing:

- Athlete summary from `reports/athlete_summary.csv`
- Feature summary and population comparison from `reports/athlete_percentiles.csv`
- Symmetry analysis from symmetry feature rows
- Biomechanical observations from `reports/biomechanical_observations.csv`
- Feature-to-literature mapping from `reports/biomechanical_knowledge_mapping.csv`
- Suggested movement focus areas expressed as descriptive review categories, not clinical recommendations

## Safety Boundaries

This engine intentionally avoids:

- ACL outcome prediction
- Probabilistic injury estimation
- Clinical diagnosis
- Clinical cutoffs not present in the dataset
- Recommendations that require force plates, clinician labels, event segmentation, or unsupported medical inference

All conclusions are descriptive and dataset-relative.
