"""Public API for the JumpGuard AI core data framework."""

from .dataset import Dataset
from .eda import EDAResults, load_feature_table, run_eda
from .feature_engineering import FeatureExtractor
from .ml_pipeline import MLConfig, MLPreparationResult, default_ml_config, prepare_ml_data
from .participant import Participant
from .trial import EmptyTrialError, Trial
from .validation import (
    DatasetValidationError,
    ValidationIssue,
    ValidationReport,
    validate_dataset,
    validate_trial,
)

__all__ = [
    "Dataset",
    "DatasetValidationError",
    "EDAResults",
    "EmptyTrialError",
    "FeatureExtractor",
    "MLConfig",
    "MLPreparationResult",
    "Participant",
    "Trial",
    "default_ml_config",
    "load_feature_table",
    "prepare_ml_data",
    "run_eda",
    "ValidationIssue",
    "ValidationReport",
    "validate_dataset",
    "validate_trial",
]
