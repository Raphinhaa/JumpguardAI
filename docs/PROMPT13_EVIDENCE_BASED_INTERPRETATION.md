# Prompt 13 Evidence-Based ACL Biomechanical Interpretation

## Objective

Prompt 13 adds an evidence-based interpretation layer that translates existing Prompt 11 biomechanical features into literature-supported, dataset-relative movement observations. The layer provides context only. It does not diagnose injury, estimate ACL injury probability, assign risk labels, generate a risk score, infer tissue damage, or infer ligament integrity.

## Architecture

```text
Video -> MediaPipe -> Prompt 11 Features -> Evidence-Based Interpretation -> Athlete Report / Dashboard / Pipeline Run Package
```

Implementation:

- `src/evidence_interpretation.py`
  - `EvidenceBasedInterpreter`
  - `EvidenceRule`
  - `LiteratureSource`
  - `EvidenceInterpretationResult`
  - `export_evidence_outputs(...)`
- `src/reporting.py`
  - Adds `Evidence-Based ACL Biomechanical Observations` to athlete reports.
- `src/dashboard.py`
  - Adds an `Evidence-Based Observations` panel to the dashboard payload and HTML.
- `src/pipeline.py`
  - Exports `reports/<run>/evidence_based_observations.json` and `evidence_based_knowledge_base.json` for each processed video.

## Supported Features

Prompt 13 only interprets existing Prompt 11-compatible features:

- Hip flexion sagittal-plane descriptors: `mean`, `median`, `maximum`, `minimum`, `rom`
- Knee flexion sagittal-plane descriptors: `mean`, `median`, `maximum`, `minimum`, `rom`
- Ankle sagittal-plane angle descriptors: `mean`, `median`, `maximum`, `minimum`, `rom`
- Bilateral ROM symmetry descriptors: `absolute_difference`, `percent_difference`, `symmetry_index`

Timing features (`time_to_peak`), variance, and standard-deviation features remain exported by earlier layers but are not interpreted by Prompt 13. They were omitted because the current evidence mapping is not specific enough to support ACL-biomechanical interpretation from these features without speculation.

## Methodology

For each athlete or uploaded-video feature row:

1. Use only existing feature columns.
2. Compare measured values with the reference dataset.
3. Generate an observation only when a supported feature falls in the reference dataset low or high tail: at or below the 5th percentile or at or above the 95th percentile.
4. Combine related features into a single observation per movement characteristic.
5. Attach supporting features, measured values, percentile comparisons, z-scores, reference summary values, literature sources, evidence strength, suggested clinical consideration, and limitation text.

The percentile interval is a dataset-relative reporting rule, not a clinical threshold.

## Knowledge Base

The knowledge base is centralized in `default_knowledge_base()` and is exported as `evidence_based_knowledge_base.json`. Each rule contains:

- feature patterns
- movement-characteristic description
- dataset comparison method
- evidence-based interpretation
- supporting literature
- evidence strength
- suggested clinical consideration
- limitation

No hard-coded interpretation rules are scattered through report or dashboard renderers.

## Literature Sources

The initial knowledge base uses the following peer-reviewed ACL biomechanics and jump-landing assessment sources:

- Hewett TE, Myer GD, Ford KR, Heidt RS Jr, Colosimo AJ, McLean SG, van den Bogert AJ, Paterno MV, Succop P. Biomechanical measures of neuromuscular control and valgus loading of the knee predict anterior cruciate ligament injury risk in female athletes: a prospective study. *American Journal of Sports Medicine*. 2005;33(4):492-501. DOI: `10.1177/0363546504269591`. PMID: `15722287`.
- Padua DA, Marshall SW, Boling MC, Thigpen CA, Garrett WE Jr, Beutler AI. The Landing Error Scoring System (LESS) is a valid and reliable clinical assessment tool of jump-landing biomechanics: The JUMP-ACL study. *American Journal of Sports Medicine*. 2009;37(10):1996-2002. DOI: `10.1177/0363546509343200`. PMID: `19726623`.
- Paterno MV, Schmitt LC, Ford KR, Rauh MJ, Myer GD, Huang B, Hewett TE. Biomechanical measures during landing and postural stability predict second anterior cruciate ligament injury after anterior cruciate ligament reconstruction and return to sport. *American Journal of Sports Medicine*. 2010;38(10):1968-1978. DOI: `10.1177/0363546510376053`. PMID: `20702858`.

## Outputs

Dataset-level exports:

- `reports/evidence_based_observations.json`
- `reports/evidence_based_observations.csv`
- `reports/evidence_based_knowledge_base.json`

Run-level exports:

- `reports/<run>/evidence_based_observations.json`
- `reports/<run>/evidence_based_observations.csv`
- `reports/<run>/evidence_based_knowledge_base.json`

Each observation contains:

- feature(s) used
- measured value(s)
- reference comparison
- evidence-based explanation
- suggested clinical consideration
- limitation
- literature source(s)
- safety label: `context_only_not_diagnosis_not_prediction`

## Limitations

- MediaPipe-derived geometric angles are approximations and are not laboratory inverse-kinematics joint angles.
- Prompt 13 does not measure joint moments, ground-reaction forces, trunk kinematics, muscle activation, contact timing, fatigue, strength, prior injury, sex, age, sport exposure, or tissue status.
- Observations are dataset-relative and depend on the available reference dataset.
- Literature-backed context does not convert a feature value into a diagnosis, injury prediction, or clinical decision.
- Unsupported feature-to-literature mappings are omitted.

## Validation Strategy

Automated tests verify:

- knowledge-base traceability and literature source presence,
- no risk score or probability output,
- supported feature filtering,
- timing feature omission,
- deterministic JSON export,
- athlete report integration,
- dashboard panel integration,
- run-local pipeline export and traceability.

Validation commands run during Prompt 13:

```text
PYTHONPATH=. .venv/bin/python -m pytest -q tests/test_evidence_interpretation.py tests/test_reporting.py tests/test_dashboard.py tests/test_pipeline.py
PYTHONPATH=. .venv/bin/python -m pytest -q
```
