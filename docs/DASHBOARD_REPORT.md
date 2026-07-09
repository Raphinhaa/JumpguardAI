# Dashboard and Visualization Report

## Scope

Prompt 8 adds an independent dashboard and visualization layer implemented in `src/dashboard.py`. It consumes existing outputs from Prompts 3-7 and does not reload MATLAB files, recompute features, rerun preprocessing, rerun EDA, train models, predict ACL outcomes, estimate injury likelihood, generate diagnoses, or modify previous CSV/report outputs.

## Architecture

The dashboard reads existing artifacts only:

- `data/processed/features.csv`
- `reports/athlete_summary.csv`
- `reports/population_statistics.csv`
- `reports/athlete_percentiles.csv`
- `reports/biomechanical_observations.csv`
- `reports/biomechanical_knowledge_mapping.csv`
- `reports/athlete_reports/`
- `reports/plots/`

It exports a static interactive HTML dashboard plus a deterministic JSON payload under `reports/dashboard/`.

## API

```python
from src.dashboard import Dashboard

dashboard = Dashboard()
dashboard.launch()
dashboard.show_athlete(12)
dashboard.show_population()
dashboard.show_feature("knee_flexion_right_rom")
dashboard.export("reports/dashboard")
```

`Dashboard(dataset=existing_dataset)` may be used to enable the time-series viewer through an already-loaded Dataset object. The dashboard never loads raw MATLAB data by itself.

## UI Coverage

The generated dashboard includes:

- Athlete selector for 43 participants
- Population comparison summary
- Feature browser for 57 biomechanical features
- Symmetry dashboard rows
- Athlete report links for 43 participant reports
- Plot gallery with 134 existing PNG plots
- Exported dashboard JSON payload

## Exports

- `reports/dashboard/index.html`
- `reports/dashboard/dashboard_payload.json`

## Missing Data Handling

The dashboard preserves existing missing values as null values in JSON and empty values in the UI. It does not fabricate plots, percentiles, summaries, time-series data, or athlete reports. Participant 44 remains represented with missing athlete feature values and no invented observations.

## Dependencies

The implementation uses the existing project dependencies: Python, pandas, NumPy, and standard-library HTML/JSON rendering. No additional dashboard server dependency is required.

## Limitations

- The dashboard is a static local HTML artifact, not a deployed web service.
- Time-series viewing requires a Dataset object supplied by caller code; this prevents hidden MATLAB reloads.
- All values are descriptive existing outputs, not clinical interpretations or predictive model outputs.
