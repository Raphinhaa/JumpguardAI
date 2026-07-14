# Future Validation Roadmap

## Architecture

```text
Healthy Videos
  -> Rights / Metadata / QC Gate
  -> Existing JumpGuard Video Processing
  -> Existing MediaPipe Landmark Extraction
  -> Existing Prompt 11 Feature Extraction
  -> Normative Feature Table
  -> Normative Statistics
  -> Athlete Comparison
  -> Evidence Layer
```

## Narrative

The future normative reference should be generated from videos processed through the same JumpGuard pipeline as athlete videos. This avoids comparing MediaPipe-derived geometric approximations against inverse-kinematics signals whose preprocessing and coordinate definitions are unknown.

The pipeline must remain deterministic and traceable. Every normative row should retain source dataset, video identifier, participant metadata, task metadata, QC status, processing version, feature schema version, and missingness metrics. Athlete comparisons should use only features generated with the same pipeline and should continue to avoid diagnosis, ACL prediction, clinical thresholds, and unsupported interpretations.

## Validation Milestones

| Milestone | Success criterion |
|---|---|
| Dataset rights audit | Every video has traceable permission for research processing and aggregate statistics. |
| Metadata completeness audit | Health status, task, camera, and participant metadata are sufficient for the planned reference use. |
| Pipeline reproducibility audit | Re-running the same videos produces identical feature tables within deterministic export precision. |
| Missingness audit | Landmark and feature missingness rates are acceptable and reported by dataset/source/task. |
| Reliability audit | Repeat or duplicate recordings quantify variability from recording setup and MediaPipe processing. |
| Statistical audit | Percentile intervals and confidence intervals are reproducible from a frozen manifest. |
