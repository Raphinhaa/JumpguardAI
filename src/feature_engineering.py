"""Public feature extraction, validation, export, and visualization API."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .features.biomechanics import PRIMARY_JOINT_PAIRS, PRIMARY_JOINT_SIGNALS
from .features.statistical import DESCRIPTORS, describe_signal
from .features.symmetry import absolute_difference, percent_difference, symmetry_index
from .features.temporal import time_to_peak
from .trial import Trial

if TYPE_CHECKING:
    from .dataset import Dataset
    from .participant import Participant


IDENTIFIER_COLUMNS: tuple[str, ...] = (
    "participant_id",
    "trial_slot",
    "trial_name",
    "condition",
    "is_empty",
)


@dataclass(frozen=True)
class FeatureDefinition:
    """Documentation metadata for one generated feature.

    Args:
        name: Output column name.
        description: Plain-language quantity description.
        formula: Mathematical or operational definition.
        units: Output units.
        clinical_relevance: Biomechanical interpretation without risk scoring.
        missing_behavior: Behavior for unavailable or invalid signals.
    """

    name: str
    description: str
    formula: str
    units: str
    clinical_relevance: str
    missing_behavior: str


class FeatureValidationError(ValueError):
    """Raised when extracted feature output violates its declared schema."""


class FeatureExtractor:
    """Extract deterministic full-recording joint-angle features.

    Args:
        missing_policy: ``nan`` emits missing values for empty/corrupted signals;
            ``raise`` stops on the first unavailable signal.

    Examples:
        >>> extractor = FeatureExtractor()
        >>> features = extractor.extract(trial)
        >>> len(features)
        57
    """

    def __init__(self, missing_policy: Literal["nan", "raise"] = "nan") -> None:
        if missing_policy not in {"nan", "raise"}:
            raise ValueError("missing_policy must be 'nan' or 'raise'.")
        self.missing_policy = missing_policy
        self._definitions = _build_feature_definitions()

    @property
    def feature_names(self) -> tuple[str, ...]:
        """Return the deterministic ordered feature schema.

        Returns:
            Fifty-seven unique feature names.
        """
        return tuple(definition.name for definition in self._definitions)

    @property
    def definitions(self) -> tuple[FeatureDefinition, ...]:
        """Return documentation metadata for every feature.

        Returns:
            Ordered immutable feature definitions.
        """
        return self._definitions

    def extract(self, trial: Trial) -> dict[str, float]:
        """Extract one feature vector from a clean Trial.

        All features use the complete recording. Event fields are intentionally
        ignored because their K/A suffixes are not authoritatively defined.

        Args:
            trial: Prompt 2 Trial object.

        Returns:
            Ordered feature mapping matching ``feature_names``.

        Raises:
            ValueError: Under ``raise`` policy when data is empty or nonfinite.

        Examples:
            >>> FeatureExtractor().extract(trial)["knee_flexion_right_rom"] >= 0
            True
        """
        if trial.is_empty:
            return self._missing_vector(
                f"Participant {trial.participant_id} trial {trial.slot} is empty."
            )
        time = trial.get_joint_angle("time")
        result: dict[str, float] = {}
        signal_descriptors: dict[str, dict[str, float]] = {}
        for signal in PRIMARY_JOINT_SIGNALS:
            try:
                values = trial.get_joint_angle(signal.label)
                descriptors = describe_signal(values)
                signal_descriptors[signal.label] = descriptors
                for descriptor in DESCRIPTORS:
                    result[f"{signal.key}_{descriptor}"] = descriptors[descriptor]
                result[f"{signal.key}_time_to_peak"] = time_to_peak(values, time)
            except (KeyError, ValueError) as exc:
                if self.missing_policy == "raise":
                    raise ValueError(
                        f"Could not extract {signal.label!r} for participant "
                        f"{trial.participant_id} trial {trial.slot}: {exc}"
                    ) from exc
                for descriptor in (*DESCRIPTORS, "time_to_peak"):
                    result[f"{signal.key}_{descriptor}"] = np.nan

        for pair in PRIMARY_JOINT_PAIRS:
            left_rom = signal_descriptors.get(pair.left_label, {}).get("rom", np.nan)
            right_rom = signal_descriptors.get(pair.right_label, {}).get("rom", np.nan)
            result[f"{pair.key}_rom_absolute_difference"] = _finite_binary(
                absolute_difference, left_rom, right_rom
            )
            result[f"{pair.key}_rom_percent_difference"] = _finite_binary(
                percent_difference, left_rom, right_rom
            )
            result[f"{pair.key}_rom_symmetry_index"] = _finite_binary(
                symmetry_index, left_rom, right_rom
            )
        ordered = {name: float(result[name]) for name in self.feature_names}
        validate_feature_vector(ordered, self.feature_names)
        return ordered

    def extract_dataset(self, dataset: "Dataset") -> pd.DataFrame:
        """Extract one row for every metadata-defined dataset trial slot.

        Args:
            dataset: Prompt 2 Dataset object.

        Returns:
            DataFrame with identifiers followed by the feature schema.

        Examples:
            >>> FeatureExtractor().extract_dataset(dataset).shape[0]
            258
        """
        rows = [
            _feature_row(trial, self.extract(trial))
            for trial in dataset.iter_trials(include_empty=True)
        ]
        frame = pd.DataFrame(rows, columns=(*IDENTIFIER_COLUMNS, *self.feature_names))
        validate_feature_table(frame, self.feature_names)
        return frame

    def extract_participant(self, participant: "Participant") -> pd.DataFrame:
        """Extract one row for every trial slot of a Participant.

        Args:
            participant: Prompt 2 Participant object.

        Returns:
            Six-row feature DataFrame in trial-slot order.

        Examples:
            >>> FeatureExtractor().extract_participant(participant).shape[0]
            6
        """
        rows = [
            _feature_row(trial, self.extract(trial))
            for trial in participant.list_trials(include_empty=True)
        ]
        frame = pd.DataFrame(rows, columns=(*IDENTIFIER_COLUMNS, *self.feature_names))
        validate_feature_table(frame, self.feature_names)
        return frame

    def _missing_vector(self, message: str) -> dict[str, float]:
        if self.missing_policy == "raise":
            raise ValueError(message)
        return {name: np.nan for name in self.feature_names}


def validate_feature_vector(
    features: dict[str, float],
    expected_names: tuple[str, ...],
) -> None:
    """Validate one feature vector's names, count, and scalar values.

    Args:
        features: Extracted feature mapping.
        expected_names: Required ordered schema.

    Raises:
        FeatureValidationError: If names are duplicated, missing, extra, or nonscalar.

    Examples:
        >>> validate_feature_vector({"x": 1.0}, ("x",))
    """
    if len(expected_names) != len(set(expected_names)):
        raise FeatureValidationError("Expected feature schema contains duplicate names.")
    if tuple(features) != expected_names:
        raise FeatureValidationError("Feature vector names or order do not match the schema.")
    nonscalar = [name for name, value in features.items() if not np.isscalar(value)]
    if nonscalar:
        raise FeatureValidationError(f"Features must be scalar; invalid: {nonscalar}.")


def validate_feature_table(frame: pd.DataFrame, expected_names: tuple[str, ...]) -> None:
    """Validate feature-table schema and trial-row uniqueness.

    Args:
        frame: Extracted feature table.
        expected_names: Required ordered feature names.

    Raises:
        FeatureValidationError: If columns or participant/slot rows are duplicated.

    Examples:
        >>> validate_feature_table(feature_frame, extractor.feature_names)
    """
    if frame.columns.duplicated().any():
        raise FeatureValidationError("Feature table contains duplicate columns.")
    expected_columns = (*IDENTIFIER_COLUMNS, *expected_names)
    if tuple(frame.columns) != expected_columns:
        raise FeatureValidationError("Feature table columns do not match the declared schema.")
    if frame.duplicated(["participant_id", "trial_slot"]).any():
        raise FeatureValidationError("Feature table contains duplicate participant/trial rows.")


def export_features(frame: pd.DataFrame, path: str | Path) -> Path:
    """Export a validated feature table as deterministic CSV.

    Args:
        frame: Feature DataFrame.
        path: Destination CSV path.

    Returns:
        Resolved written path.

    Examples:
        >>> export_features(feature_frame, "data/processed/features.csv").suffix
        '.csv'
    """
    destination = Path(path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(destination, index=False, float_format="%.10g")
    return destination


def plot_feature_distribution(
    frame: pd.DataFrame,
    feature: str,
    *,
    bins: int = 24,
    ax: Axes | None = None,
) -> tuple[Figure, Axes]:
    """Plot a feature histogram.

    Args:
        frame: Extracted feature table.
        feature: Numeric feature column.
        bins: Histogram bin count.
        ax: Optional existing axes.

    Returns:
        Figure and axes.
    """
    figure, axes = _figure_and_axes(ax)
    axes.hist(frame[feature].dropna(), bins=bins, color="#2166AC", edgecolor="white")
    axes.set(title=feature.replace("_", " ").title(), xlabel=feature, ylabel="Trial count")
    _style_axes(axes)
    figure.tight_layout()
    return figure, axes


def plot_correlation_heatmap(
    frame: pd.DataFrame,
    features: list[str] | tuple[str, ...],
) -> tuple[Figure, Axes]:
    """Plot a correlation heatmap for selected features.

    Args:
        frame: Extracted feature table.
        features: Numeric feature columns.

    Returns:
        Figure and axes.
    """
    correlation = frame.loc[:, features].corr()
    figure, axes = plt.subplots(figsize=(8.0, 6.5))
    image = axes.imshow(correlation, vmin=-1, vmax=1, cmap="RdBu_r")
    axes.set_xticks(range(len(features)), [name.replace("_", " ") for name in features], rotation=45, ha="right")
    axes.set_yticks(range(len(features)), [name.replace("_", " ") for name in features])
    figure.colorbar(image, ax=axes, label="Pearson correlation")
    axes.set_title("Feature correlation")
    figure.tight_layout()
    return figure, axes


def plot_left_right_comparison(
    frame: pd.DataFrame,
    left_feature: str,
    right_feature: str,
    *,
    ax: Axes | None = None,
) -> tuple[Figure, Axes]:
    """Plot paired left/right feature measurements.

    Args:
        frame: Extracted feature table.
        left_feature: Left-side numeric column.
        right_feature: Right-side numeric column.
        ax: Optional existing axes.

    Returns:
        Figure and axes.
    """
    valid = frame[[left_feature, right_feature]].dropna()
    figure, axes = _figure_and_axes(ax)
    axes.scatter(valid[right_feature], valid[left_feature], s=18, alpha=0.65, color="#4D9221")
    bounds = [
        float(min(valid.min())) if not valid.empty else 0.0,
        float(max(valid.max())) if not valid.empty else 1.0,
    ]
    axes.plot(bounds, bounds, color="#4A4A4A", linestyle="--", linewidth=1)
    axes.set(xlabel=right_feature, ylabel=left_feature, title="Left/right comparison")
    _style_axes(axes)
    figure.tight_layout()
    return figure, axes


def plot_time_series_overlay(
    trial: Trial,
    labels: tuple[str, ...] = ("knee_angle_r", "knee_angle_l"),
    *,
    ax: Axes | None = None,
) -> tuple[Figure, Axes]:
    """Overlay semantically named joint-angle time series.

    Args:
        trial: Non-empty Prompt 2 Trial.
        labels: Semantic joint-angle labels.
        ax: Optional existing axes.

    Returns:
        Figure and axes.
    """
    figure, axes = _figure_and_axes(ax)
    time = trial.get_joint_angle("time")
    for label in labels:
        axes.plot(time, trial.get_joint_angle(label), linewidth=1.4, label=label)
    axes.set(xlabel="Time (s)", ylabel="Angle (degrees)", title=f"Participant {trial.participant_id} - {trial.name}")
    axes.legend(frameon=False)
    _style_axes(axes)
    figure.tight_layout()
    return figure, axes


def _build_feature_definitions() -> tuple[FeatureDefinition, ...]:
    definitions: list[FeatureDefinition] = []
    descriptor_metadata = {
        "mean": ("Arithmetic mean over all frames", "Σx / N", "degrees"),
        "median": ("Median over all frames", "median(x)", "degrees"),
        "std": ("Population standard deviation", "sqrt(Σ(x-mean)² / N)", "degrees"),
        "variance": ("Population variance", "Σ(x-mean)² / N", "degrees²"),
        "maximum": ("Maximum recorded angle", "max(x)", "degrees"),
        "minimum": ("Minimum recorded angle", "min(x)", "degrees"),
        "rom": ("Range of motion over the recording", "max(x) - min(x)", "degrees"),
    }
    missing = "NaN for an empty trial or an unavailable/nonfinite source signal."
    relevance = "Describes directly measured joint-angle magnitude or variability."
    for signal in PRIMARY_JOINT_SIGNALS:
        for descriptor in DESCRIPTORS:
            description, formula, units = descriptor_metadata[descriptor]
            definitions.append(
                FeatureDefinition(
                    f"{signal.key}_{descriptor}",
                    f"{signal.side.title()} {signal.joint} {description.lower()}.",
                    formula,
                    units,
                    relevance,
                    missing,
                )
            )
        definitions.append(
            FeatureDefinition(
                f"{signal.key}_time_to_peak",
                f"Elapsed time to the first maximum of the {signal.side} {signal.joint} signal.",
                "time[argmax(x)] - time[0]",
                "seconds",
                "Describes timing of the directly measured maximum over the recording.",
                missing,
            )
        )
    for pair in PRIMARY_JOINT_PAIRS:
        definitions.extend(
            (
                FeatureDefinition(
                    f"{pair.key}_rom_absolute_difference",
                    f"Unsigned left/right difference in {pair.joint} ROM.",
                    "|ROM_L - ROM_R|",
                    "degrees",
                    "Quantifies bilateral ROM disparity without assigning risk.",
                    missing,
                ),
                FeatureDefinition(
                    f"{pair.key}_rom_percent_difference",
                    f"Absolute bilateral percent difference in {pair.joint} ROM.",
                    "100 × |ROM_L-ROM_R| / ((|ROM_L|+|ROM_R|)/2)",
                    "percent",
                    "Normalizes bilateral ROM disparity to side magnitude.",
                    f"{missing} Also NaN when both ROM values are zero.",
                ),
                FeatureDefinition(
                    f"{pair.key}_rom_symmetry_index",
                    f"Signed bilateral symmetry index for {pair.joint} ROM.",
                    "100 × (ROM_L-ROM_R) / ((|ROM_L|+|ROM_R|)/2)",
                    "percent",
                    "Positive values indicate larger left-side ROM; no risk threshold is applied.",
                    f"{missing} Also NaN when both ROM values are zero.",
                ),
            )
        )
    return tuple(definitions)


def _feature_row(trial: Trial, features: dict[str, float]) -> dict[str, Any]:
    return {
        "participant_id": trial.participant_id,
        "trial_slot": trial.slot,
        "trial_name": trial.name,
        "condition": trial.condition,
        "is_empty": trial.is_empty,
        **features,
    }


def _finite_binary(function: Any, left: float, right: float) -> float:
    if not np.isfinite(left) or not np.isfinite(right):
        return np.nan
    return float(function(left, right))


def _figure_and_axes(ax: Axes | None) -> tuple[Figure, Axes]:
    if ax is not None:
        return ax.figure, ax
    return plt.subplots(figsize=(8.0, 4.8))


def _style_axes(ax: Axes) -> None:
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.7, alpha=0.75)
    ax.spines[["top", "right"]].set_visible(False)
