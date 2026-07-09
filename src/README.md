# Source Code

This folder contains the core implementation of JumpGuard AI.

Current core data modules:

- `dataset.py`: public Dataset API
- `dataset_parser.py`: exclusive raw MATLAB parser
- `participant.py`: participant abstraction
- `trial.py`: trial abstraction and semantic joint-angle access
- `validation.py`: automatic integrity and metadata validation
- `preprocessing.py`: reusable numeric preprocessing
- `visualization.py`: Dataset/Participant/Trial plots
- `load_dataset.py`: source format detection and loading
- `feature_engineering.py`: feature extraction, validation, export, and plots
- `features/`: statistical, temporal, symmetry, and biomechanical primitives
- `eda.py`: deterministic feature-table validation, EDA summaries, plots, PCA,
  and unsupervised feature ranking
- `ml_pipeline.py`: participant-safe splits, train-only preprocessing,
  feature-selection infrastructure, CV summaries, config, and metric interfaces
- `biomechanical_intelligence.py`: dataset-relative athlete assessment and
  explainable biomechanical observations
- `reporting.py`: deterministic Markdown, HTML, and JSON athlete reports
- `dashboard.py`: static interactive dashboard and visualization browser over
  existing Prompt 3-7 outputs
- `video_processing.py`: validated video ingestion, frame access,
  non-destructive preprocessing, clip selection, and previews for future pose work
- `pose_estimation.py`: MediaPipe pose-landmark interface, deterministic
  landmark exports, missing-landmark preservation, and debug visualizations

Machine learning and risk assessment build on these objects and feature tables
in later milestones.
