# Athlete Reporting Layer Report

## Scope

Prompt 7 adds an independent Athlete Reporting Layer on top of the existing Prompt 6 Biomechanical Intelligence outputs. It does not reload MATLAB files, recompute features, rerun preprocessing, rerun EDA, train models, create new biomechanical observations, infer undocumented biomechanics, produce probabilistic injury estimates, or generate medical diagnosis.

## Architecture

The reporting layer is implemented in `src/reporting.py`. It consumes existing Prompt 6 CSV outputs from `reports/`:

- `athlete_summary.csv`
- `population_statistics.csv`
- `athlete_percentiles.csv`
- `biomechanical_observations.csv`
- `biomechanical_knowledge_mapping.csv`

An optional already-loaded `Dataset` object may be supplied to enrich overview metadata, but the layer never loads raw MATLAB data and never invokes feature extraction or preprocessing.

## API

```python
from src.reporting import AthleteReportGenerator

generator = AthleteReportGenerator(dataset=None, reports_dir="reports")
report = generator.generate(participant_id=12)
generator.save_markdown(report, "reports/athlete_reports/participant_12.md")
generator.save_html(report, "reports/athlete_reports/participant_12.html")
generator.save_json(report, "reports/athlete_reports/participant_12.json")
generator.generate_all_reports("reports/athlete_reports")
```

## Report Structure

Each report contains:

1. Athlete Overview: participant ID, trial counts, valid/empty trials, recording completeness, feature completeness, and dataset completeness.
2. Biomechanical Summary: Hip Flexion, Knee Flexion, and Ankle Angle feature families using Prompt 3-derived values and Prompt 6 percentiles.
3. Population Comparison: participant value, dataset mean, dataset standard deviation, percentile, and Z-score.
4. Symmetry Summary: absolute difference, percent difference, and symmetry index features reused from Prompt 3 outputs.
5. Biomechanical Observations: Prompt 6 observations only; no new observations are invented.
6. Literature Context: Prompt 6 feature-to-literature mappings with concept text and source/DOI links when available.
7. Visualizations: radar, percentile comparison, population comparison, symmetry comparison, and ROM distribution plots.

## Exports

Generated report files:

- Markdown reports: 43
- HTML reports: 43
- JSON reports: 43
- Visualization PNG files: 210

Output directory: `reports/athlete_reports/`.

## Determinism

JSON exports use sorted keys and stable formatting. Markdown and HTML are rendered from the same structured report object. Plot exports use deterministic source data and stable metadata. Batch generation overwrites the same paths deterministically for unchanged inputs.

## Missing-Value Handling

Missing values are preserved as missing/null values in structured JSON and blank cells in Markdown/HTML tables. The reporting layer does not fabricate, interpolate, impute, or estimate missing values. Participant 44 has no observed feature values and receives a report with explicit zero feature completeness and no visualizations.

## Limitations

- Reports are dataset-relative and descriptive only.
- Literature context is inherited from Prompt 6 mappings and does not create clinical thresholds.
- No treatment advice, diagnosis, injury prediction, or probabilistic injury estimate is produced.
- HTML reports are static local artifacts intended for review and future application integration.

## Future Application Integration

The `AthleteReport` dataclass and JSON schema can be consumed by a web frontend, API service, or PDF renderer in later prompts. The current layer is intentionally independent of future predictive models.
