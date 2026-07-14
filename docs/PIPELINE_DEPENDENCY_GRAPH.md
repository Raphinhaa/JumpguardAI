# Pipeline Dependency Graph

```text
Video file
  -> src.video_processing.Video
     validates extension, metadata, fps, frame count, frame access
  -> src.pose_estimation.MediaPipePoseEstimator
     converts each BGR frame to RGB and exports 33 MediaPipe pose landmarks per processed frame
  -> landmarks.csv / landmarks.json
     frame_number, timestamp, landmark_index, landmark_name, x, y, z, visibility, confidence
  -> src.feature_extraction.FeatureExtractor.calculate_joint_angles
     computes six MediaPipe-derived geometric angle trajectories from documented landmark triplets
  -> src.feature_extraction.FeatureExtractor.calculate_temporal_features
     computes full-recording descriptors and time-to-peak for each angle trajectory
  -> src.feature_extraction.FeatureExtractor.calculate_symmetry
     computes bilateral ROM absolute difference, percent difference, and symmetry index
  -> feature_table.csv / feature_table.json
     one Prompt-3-compatible row for the uploaded video
  -> src.evidence_interpretation.load_reference_feature_table
     loads data/processed/features.csv as the reference feature table when present
  -> src.evidence_interpretation.EvidenceBasedInterpreter
     computes dataset-relative percentiles, z-scores, p05/p95, and evidence-backed non-diagnostic observations
  -> athlete_report / dashboard
     renders existing pipeline outputs without changing measurements
```

## Dataset Reference Path

```text
DJ.mat + metadata workbooks
  -> Dataset / Participant / Trial abstractions
  -> src.feature_engineering.FeatureExtractor
     extracts the same 57 feature names from laboratory joint-angle labels over full recordings
  -> data/processed/features.csv
  -> src.biomechanical_intelligence
     participant-level means, population statistics, athlete percentiles, descriptive observations
  -> Prompt 13 evidence engine and athlete reporting layers
```

No dependency in this graph performs ACL diagnosis, injury prediction, probability estimation, or clinical scoring.
