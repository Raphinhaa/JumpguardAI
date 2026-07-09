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

Feature extraction, machine learning, and risk assessment build on these
objects in later milestones.
