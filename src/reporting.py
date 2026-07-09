"""Deterministic athlete reporting layer for JumpGuard AI."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import TYPE_CHECKING, Any

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .biomechanical_intelligence import (
    IntelligenceResult,
    plot_athlete_vs_population,
    plot_percentiles,
    plot_radar,
    plot_symmetry,
)

if TYPE_CHECKING:
    from .dataset import Dataset


REPORT_FEATURE_FAMILIES: dict[str, str] = {
    "hip_flexion": "Hip Flexion",
    "knee_flexion": "Knee Flexion",
    "ankle_angle": "Ankle Angle",
}

SUMMARY_DESCRIPTORS: tuple[str, ...] = (
    "mean",
    "median",
    "rom",
    "std",
    "absolute_difference",
    "percent_difference",
    "symmetry_index",
)


@dataclass(frozen=True)
class AthleteReport:
    """Structured participant report.

    Args:
        participant_id: Athlete/participant identifier.
        overview: Trial availability and completeness summary.
        biomechanical_summary: Family-grouped feature summary rows.
        population_comparison: Dataset-relative feature comparisons.
        symmetry_summary: Prompt 3 symmetry feature rows.
        observations: Prompt 6 observation rows for this athlete.
        literature_context: Prompt 6 literature mapping rows.
        visualizations: Exported visualization paths.
    """

    participant_id: int
    overview: dict[str, Any]
    biomechanical_summary: dict[str, list[dict[str, Any]]]
    population_comparison: list[dict[str, Any]]
    symmetry_summary: list[dict[str, Any]]
    observations: list[dict[str, Any]]
    literature_context: list[dict[str, Any]]
    visualizations: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable report dictionary."""

        return {
            "participant_id": self.participant_id,
            "overview": self.overview,
            "biomechanical_summary": self.biomechanical_summary,
            "population_comparison": self.population_comparison,
            "symmetry_summary": self.symmetry_summary,
            "observations": self.observations,
            "literature_context": self.literature_context,
            "visualizations": self.visualizations,
            "safety_statement": (
                "This report is descriptive and dataset-relative. It does not provide "
                "medical diagnosis, treatment advice, injury prediction, or probabilistic injury estimates."
            ),
        }


class AthleteReportGenerator:
    """Generate deterministic athlete reports from existing Prompt 6 outputs.

    Args:
        dataset: Optional already-loaded Dataset used only for overview metadata.
        reports_dir: Directory containing Prompt 6 CSV outputs.

    Raises:
        FileNotFoundError: If required Prompt 6 output files are unavailable.
    """

    def __init__(
        self,
        dataset: "Dataset | None" = None,
        reports_dir: str | Path = "reports",
    ) -> None:
        self.dataset = dataset
        self.reports_dir = Path(reports_dir)
        self.athlete_summary = _read_required(self.reports_dir / "athlete_summary.csv")
        self.population_statistics = _read_required(
            self.reports_dir / "population_statistics.csv"
        )
        self.athlete_percentiles = _read_required(self.reports_dir / "athlete_percentiles.csv")
        self.observations = _read_required(self.reports_dir / "biomechanical_observations.csv")
        self.knowledge_mapping = _read_required(
            self.reports_dir / "biomechanical_knowledge_mapping.csv"
        )

    def generate(
        self,
        participant_id: int,
        *,
        include_visualizations: bool = True,
        output_dir: str | Path = "reports/athlete_reports",
    ) -> AthleteReport:
        """Generate one structured participant report.

        Args:
            participant_id: Participant identifier.
            include_visualizations: Export report-specific figures.
            output_dir: Directory for visual assets.

        Returns:
            AthleteReport.
        """

        participant_id = int(participant_id)
        if participant_id not in set(self.athlete_summary["participant_id"].astype(int)):
            raise KeyError(f"Participant {participant_id} is not available in athlete_summary.csv.")
        athlete_rows = self._participant_percentiles(participant_id)
        visualizations: dict[str, str] = {}
        if include_visualizations and athlete_rows["value"].notna().any():
            visualizations = self.export_visualizations(participant_id, output_dir=output_dir)
        return AthleteReport(
            participant_id=participant_id,
            overview=self._overview(participant_id),
            biomechanical_summary=self._biomechanical_summary(athlete_rows),
            population_comparison=_records(athlete_rows),
            symmetry_summary=_records(_symmetry_rows(athlete_rows)),
            observations=_records(
                self.observations[
                    self.observations["participant_id"].astype(int).eq(participant_id)
                ]
            ),
            literature_context=self._literature_context(athlete_rows),
            visualizations=visualizations,
        )

    def generate_all_reports(
        self,
        output_dir: str | Path = "reports/athlete_reports",
        *,
        include_visualizations: bool = True,
    ) -> list[AthleteReport]:
        """Generate and save Markdown, HTML, and JSON reports for every participant."""

        destination = Path(output_dir)
        reports = []
        for participant_id in sorted(self.athlete_summary["participant_id"].astype(int)):
            report = self.generate(
                participant_id,
                include_visualizations=include_visualizations,
                output_dir=destination,
            )
            self.save_json(report, destination / f"participant_{participant_id:02d}.json")
            self.save_markdown(report, destination / f"participant_{participant_id:02d}.md")
            self.save_html(report, destination / f"participant_{participant_id:02d}.html")
            reports.append(report)
        return reports

    def save_json(self, report: AthleteReport, path: str | Path) -> Path:
        """Save a report as deterministic JSON."""

        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(_json_ready(report.to_dict()), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return destination

    def save_markdown(self, report: AthleteReport, path: str | Path) -> Path:
        """Save a report as Markdown."""

        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(render_markdown(report), encoding="utf-8")
        return destination

    def save_html(self, report: AthleteReport, path: str | Path) -> Path:
        """Save a report as standalone HTML."""

        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(render_html(report), encoding="utf-8")
        return destination

    def export_visualizations(
        self,
        participant_id: int,
        output_dir: str | Path = "reports/athlete_reports",
    ) -> dict[str, str]:
        """Export report visualizations for one participant."""

        destination = Path(output_dir) / f"participant_{participant_id:02d}_assets"
        destination.mkdir(parents=True, exist_ok=True)
        result = IntelligenceResult(
            athlete_summary=self.athlete_summary,
            population_statistics=self.population_statistics,
            athlete_percentiles=self.athlete_percentiles,
            observations=self.observations,
            knowledge_mapping=self.knowledge_mapping,
        )
        plotters = {
            "radar_chart": lambda: plot_radar(result, participant_id),
            "percentile_comparison": lambda: plot_percentiles(result, participant_id),
            "population_comparison": lambda: plot_athlete_vs_population(result, participant_id),
            "symmetry_comparison": lambda: plot_symmetry(result, participant_id),
            "distribution_plots": lambda: plot_distribution_panel(result, participant_id),
        }
        paths: dict[str, str] = {}
        for name, plotter in plotters.items():
            figure, _ = plotter()
            path = destination / f"{name}.png"
            figure.savefig(
                path,
                dpi=150,
                bbox_inches="tight",
                metadata={"Software": "JumpGuardAI"},
            )
            plt.close(figure)
            paths[name] = str(path)
        return paths

    def _participant_percentiles(self, participant_id: int) -> pd.DataFrame:
        return self.athlete_percentiles[
            self.athlete_percentiles["participant_id"].astype(int).eq(participant_id)
        ].sort_values("feature").reset_index(drop=True)

    def _overview(self, participant_id: int) -> dict[str, Any]:
        summary = self.athlete_summary[
            self.athlete_summary["participant_id"].astype(int).eq(participant_id)
        ].iloc[0]
        available_trials = int(summary["trial_count"])
        empty_trials = int(summary["empty_trial_count"])
        valid_trials = available_trials - empty_trials
        dataset_participants = int(self.athlete_summary["participant_id"].nunique())
        observed_features = int(
            self._participant_percentiles(participant_id)["value"].notna().sum()
        )
        total_features = int(self.population_statistics["feature"].nunique())
        overview = {
            "participant_id": participant_id,
            "available_trials": available_trials,
            "valid_trials": valid_trials,
            "empty_trials": empty_trials,
            "recording_completeness": _safe_ratio(valid_trials, available_trials),
            "observed_feature_count": observed_features,
            "total_feature_count": total_features,
            "feature_completeness": _safe_ratio(observed_features, total_features),
            "dataset_participant_count": dataset_participants,
        }
        if self.dataset is not None:
            participant = self.dataset.get_participant(participant_id)
            dataset_summary = self.dataset.summary()
            overview["dataset_valid_trials"] = dataset_summary["valid_trials"]
            overview["dataset_total_trial_slots"] = dataset_summary["total_trial_slots"]
            overview["dataset_completeness"] = _safe_ratio(
                dataset_summary["valid_trials"],
                dataset_summary["total_trial_slots"],
            )
            overview["trial_names"] = [
                trial.name for trial in participant.list_trials(include_empty=True)
            ]
        else:
            total_slots = int(self.athlete_summary["trial_count"].sum())
            total_empty = int(self.athlete_summary["empty_trial_count"].sum())
            overview["dataset_valid_trials"] = total_slots - total_empty
            overview["dataset_total_trial_slots"] = total_slots
            overview["dataset_completeness"] = _safe_ratio(total_slots - total_empty, total_slots)
        return overview

    def _biomechanical_summary(self, athlete_rows: pd.DataFrame) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for prefix, label in REPORT_FEATURE_FAMILIES.items():
            family = athlete_rows[
                athlete_rows["feature"].map(
                    lambda feature: _is_summary_feature(str(feature), prefix)
                )
            ].copy()
            grouped[label] = _records(family)
        return grouped

    def _literature_context(self, athlete_rows: pd.DataFrame) -> list[dict[str, Any]]:
        features = set(athlete_rows["feature"])
        mapping = self.knowledge_mapping[self.knowledge_mapping["feature"].isin(features)]
        return _records(mapping.drop_duplicates(["concept", "source"]).sort_values("concept"))


def render_markdown(report: AthleteReport) -> str:
    """Render an AthleteReport as Markdown."""

    lines = [
        f"# Athlete Report: Participant {report.participant_id}",
        "",
        report.to_dict()["safety_statement"],
        "",
        "## Athlete Overview",
        "",
        _markdown_table(_dict_rows(report.overview)),
        "",
        "## Biomechanical Summary",
        "",
    ]
    for family, rows in report.biomechanical_summary.items():
        lines.extend([f"### {family}", "", _markdown_table(_display_rows(rows)), ""])
    lines.extend(
        [
            "## Population Comparison",
            "",
            _markdown_table(_display_rows(report.population_comparison)),
            "",
            "## Symmetry Summary",
            "",
            _markdown_table(_display_rows(report.symmetry_summary)),
            "",
            "## Biomechanical Observations",
            "",
            _markdown_table(_display_rows(report.observations)),
            "",
            "## Literature Context",
            "",
            _markdown_table(_display_rows(report.literature_context)),
            "",
            "## Visualizations",
            "",
        ]
    )
    if report.visualizations:
        for name, path in sorted(report.visualizations.items()):
            lines.append(f"- {name}: `{path}`")
    else:
        lines.append("- No visualizations generated because no observed athlete feature values were available.")
    lines.append("")
    return "\n".join(lines)


def render_html(report: AthleteReport) -> str:
    """Render an AthleteReport as standalone HTML."""

    markdown = render_markdown(report)
    body_lines = []
    for line in markdown.splitlines():
        if line.startswith("# "):
            body_lines.append(f"<h1>{escape(line[2:])}</h1>")
        elif line.startswith("## "):
            body_lines.append(f"<h2>{escape(line[3:])}</h2>")
        elif line.startswith("### "):
            body_lines.append(f"<h3>{escape(line[4:])}</h3>")
        elif line.startswith("- "):
            body_lines.append(f"<p>{escape(line)}</p>")
        elif line.startswith("|"):
            body_lines.append(f"<pre>{escape(line)}</pre>")
        elif not line:
            continue
        else:
            body_lines.append(f"<p>{escape(line)}</p>")
    return (
        "<!doctype html>\n"
        "<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        f"<title>Athlete Report {report.participant_id}</title>\n"
        "<style>body{font-family:Arial,sans-serif;line-height:1.45;max-width:1100px;margin:32px auto;padding:0 20px;}"
        "pre{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;white-space:pre-wrap;}"
        "h1,h2,h3{color:#1f2933;}p{color:#263238;}</style>\n"
        "</head>\n<body>\n"
        + "\n".join(body_lines)
        + "\n</body>\n</html>\n"
    )


def plot_distribution_panel(
    result: IntelligenceResult,
    participant_id: int,
) -> tuple[Figure, Axes]:
    """Plot dataset distributions for representative ROM features."""

    selected = [
        "hip_flexion_right_rom",
        "hip_flexion_left_rom",
        "knee_flexion_right_rom",
        "knee_flexion_left_rom",
        "ankle_angle_right_rom",
        "ankle_angle_left_rom",
    ]
    data = result.athlete_percentiles[result.athlete_percentiles["feature"].isin(selected)]
    athlete = data[data["participant_id"].astype(int).eq(participant_id)]
    figure, axes = plt.subplots(2, 3, figsize=(12.0, 6.8))
    flat_axes = axes.ravel()
    for axis, feature in zip(flat_axes, selected):
        feature_values = data[data["feature"].eq(feature)]["value"].dropna()
        athlete_value = athlete[athlete["feature"].eq(feature)]["value"]
        axis.hist(feature_values, bins=14, color="#A6CEE3", edgecolor="white")
        if not athlete_value.empty and pd.notna(athlete_value.iloc[0]):
            axis.axvline(float(athlete_value.iloc[0]), color="#B2182B", linewidth=2)
        axis.set_title(feature, fontsize=9)
        axis.spines[["top", "right"]].set_visible(False)
    figure.suptitle(f"Participant {participant_id} ROM Distributions", y=1.02)
    figure.tight_layout()
    return figure, flat_axes[0]


def _read_required(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Required reporting input is missing: {path}")
    return pd.read_csv(path)


def _symmetry_rows(rows: pd.DataFrame) -> pd.DataFrame:
    return rows[
        rows["feature"].str.contains("absolute_difference|percent_difference|symmetry_index")
    ].copy()


def _is_summary_feature(feature: str, prefix: str) -> bool:
    if not feature.startswith(prefix):
        return False
    return any(feature.endswith(descriptor) for descriptor in SUMMARY_DESCRIPTORS)


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return [_json_ready(row) for row in frame.to_dict(orient="records")]


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return None if np.isnan(value) else float(value)
    if isinstance(value, float) and np.isnan(value):
        return None
    return value


def _dict_rows(mapping: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"field": key, "value": value} for key, value in mapping.items()]


def _display_rows(rows: list[dict[str, Any]], limit: int = 24) -> list[dict[str, Any]]:
    return rows[:limit]


def _markdown_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "_No rows available._"
    columns = list(rows[0])
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        values = [_format_markdown_value(row.get(column)) for column in columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def _format_markdown_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if np.isnan(value):
            return ""
        return f"{value:.4g}"
    return str(value).replace("|", "\\|")


def _safe_ratio(numerator: int, denominator: int) -> float | None:
    return None if denominator == 0 else float(numerator / denominator)
