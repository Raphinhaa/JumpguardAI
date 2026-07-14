"""Interactive dashboard and visualization layer for JumpGuard AI."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import TYPE_CHECKING, Any

import json

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from .dataset import Dataset


@dataclass(frozen=True)
class DashboardExport:
    """Paths written by a dashboard export operation."""

    html: Path
    json: Path


class Dashboard:
    """Static interactive dashboard over existing Prompt 3-7 outputs.

    Args:
        dataset: Optional already-loaded Dataset for time-series viewing only.
        features_path: Existing Prompt 3 feature table path.
        reports_dir: Existing report directory containing Prompt 4-7 outputs.
        athlete_reports_dir: Existing Prompt 7 participant report directory.
        plots_dir: Existing Prompt 4 plot gallery directory.

    Raises:
        FileNotFoundError: If any required existing output is missing.
    """

    def __init__(
        self,
        dataset: "Dataset | None" = None,
        *,
        features_path: str | Path = "data/processed/features.csv",
        reports_dir: str | Path = "reports",
        athlete_reports_dir: str | Path = "reports/athlete_reports",
        plots_dir: str | Path = "reports/plots",
    ) -> None:
        self.dataset = dataset
        self.features_path = Path(features_path)
        self.reports_dir = Path(reports_dir)
        self.athlete_reports_dir = Path(athlete_reports_dir)
        self.plots_dir = Path(plots_dir)
        self.features = _read_csv(self.features_path)
        self.athlete_summary = _read_csv(self.reports_dir / "athlete_summary.csv")
        self.population_statistics = _read_csv(self.reports_dir / "population_statistics.csv")
        self.athlete_percentiles = _read_csv(self.reports_dir / "athlete_percentiles.csv")
        self.observations = _read_csv(self.reports_dir / "biomechanical_observations.csv")
        self.knowledge_mapping = _read_csv(
            self.reports_dir / "biomechanical_knowledge_mapping.csv"
        )
        self.evidence_based_observations = _read_json_records_optional(
            self.reports_dir / "evidence_based_observations.json"
        )
        _require_dir(self.athlete_reports_dir)
        _require_dir(self.plots_dir)

    @property
    def athlete_ids(self) -> list[int]:
        """Return sorted athlete identifiers."""

        return sorted(self.athlete_summary["participant_id"].astype(int).tolist())

    @property
    def feature_names(self) -> list[str]:
        """Return sorted biomechanical feature names."""

        metadata = {"participant_id", "trial_slot", "trial_name", "condition", "is_empty"}
        return [
            column
            for column in self.features.columns
            if column not in metadata and pd.api.types.is_numeric_dtype(self.features[column])
        ]

    def launch(
        self,
        output_dir: str | Path = "reports/dashboard",
        *,
        filename: str = "index.html",
    ) -> Path:
        """Generate and return a static interactive dashboard HTML file."""

        export = self.export(output_dir=output_dir, filename=filename)
        return export.html

    def export(
        self,
        output_dir: str | Path = "reports/dashboard",
        *,
        filename: str = "index.html",
    ) -> DashboardExport:
        """Export dashboard HTML and its deterministic JSON payload."""

        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        payload = self.dashboard_payload()
        json_path = destination / "dashboard_payload.json"
        html_path = destination / filename
        json_path.write_text(
            json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        html_path.write_text(render_dashboard_html(payload), encoding="utf-8")
        return DashboardExport(html=html_path, json=json_path)

    def dashboard_payload(self) -> dict[str, Any]:
        """Return the full deterministic dashboard data payload."""

        return {
            "athletes": [self.show_athlete(participant_id) for participant_id in self.athlete_ids],
            "population": self.show_population(),
            "features": [self.show_feature(feature) for feature in self.feature_names],
            "symmetry": self.show_symmetry(),
            "evidence_based_observations": self.show_evidence_based_observations(),
            "plot_gallery": self.show_plot_gallery(),
            "reports": self.list_reports(),
            "time_series_available": self.dataset is not None,
            "safety_statement": (
                "Dashboard values are descriptive outputs from existing project artifacts. "
                "The dashboard does not recompute features, train models, diagnose injury, "
                "or estimate injury likelihood."
            ),
        }

    def show_athlete(self, participant_id: int) -> dict[str, Any]:
        """Return dashboard data for one athlete."""

        participant_id = int(participant_id)
        summary = self.athlete_summary[
            self.athlete_summary["participant_id"].astype(int).eq(participant_id)
        ]
        if summary.empty:
            raise KeyError(f"Participant {participant_id} is unavailable.")
        percentiles = self.athlete_percentiles[
            self.athlete_percentiles["participant_id"].astype(int).eq(participant_id)
        ].sort_values("feature")
        observations = self.observations[
            self.observations["participant_id"].astype(int).eq(participant_id)
        ].sort_values(["category", "feature"])
        return {
            "participant_id": participant_id,
            "summary": _record(summary.iloc[0].to_dict()),
            "percentiles": _records(percentiles),
            "observations": _records(observations),
            "evidence_based_observations": self.show_evidence_based_observations(participant_id),
            "reports": self.report_paths(participant_id),
            "missing_feature_count": int(percentiles["value"].isna().sum()),
        }

    def show_evidence_based_observations(self, participant_id: int | None = None) -> list[dict[str, Any]]:
        """Return Prompt 13 evidence-backed observations when available."""

        rows = self.evidence_based_observations.copy()
        if rows.empty:
            return []
        if participant_id is not None:
            rows = rows[rows["participant_id"].astype(int).eq(int(participant_id))]
        return _records(rows)

    def show_population(self) -> dict[str, Any]:
        """Return population comparison statistics."""

        return {
            "feature_count": int(len(self.population_statistics)),
            "statistics": _records(self.population_statistics.sort_values("feature")),
        }

    def show_feature(self, feature: str) -> dict[str, Any]:
        """Return feature browser data for one biomechanical feature."""

        if feature not in self.feature_names:
            raise KeyError(f"Feature {feature!r} is not available.")
        population = self.population_statistics[
            self.population_statistics["feature"].eq(feature)
        ]
        percentiles = self.athlete_percentiles[
            self.athlete_percentiles["feature"].eq(feature)
        ].sort_values("participant_id")
        knowledge = self.knowledge_mapping[self.knowledge_mapping["feature"].eq(feature)]
        return {
            "feature": feature,
            "population": _record(population.iloc[0].to_dict()) if not population.empty else {},
            "athlete_values": _records(percentiles),
            "knowledge": _record(knowledge.iloc[0].to_dict()) if not knowledge.empty else {},
        }

    def show_symmetry(self, participant_id: int | None = None) -> dict[str, Any]:
        """Return symmetry dashboard data."""

        rows = self.athlete_percentiles[
            self.athlete_percentiles["feature"].str.contains(
                "absolute_difference|percent_difference|symmetry_index"
            )
        ].copy()
        if participant_id is not None:
            rows = rows[rows["participant_id"].astype(int).eq(int(participant_id))]
        return {"rows": _records(rows.sort_values(["participant_id", "feature"]))}

    def show_time_series(
        self,
        participant_id: int,
        trial_slot: int = 1,
        labels: tuple[str, ...] = ("knee_angle_r", "knee_angle_l"),
    ) -> dict[str, Any]:
        """Return time-series data when an existing Dataset object was supplied.

        The dashboard never loads raw MATLAB data itself. If no Dataset was
        supplied, the response explicitly marks the viewer as unavailable.
        """

        if self.dataset is None:
            return {
                "available": False,
                "reason": "No already-loaded Dataset object was supplied to Dashboard.",
            }
        trial = self.dataset.get_participant(participant_id).get_trial(trial_slot)
        if trial.is_empty:
            return {
                "available": False,
                "reason": f"Participant {participant_id} trial {trial_slot} is empty.",
            }
        time = trial.get_joint_angle("time")
        series = {
            label: trial.get_joint_angle(label).astype(float).tolist()
            for label in labels
        }
        return {
            "available": True,
            "participant_id": int(participant_id),
            "trial_slot": int(trial_slot),
            "time": time.astype(float).tolist(),
            "series": series,
        }

    def load_report(self, participant_id: int, format_name: str = "html") -> str:
        """Load a Prompt 7 athlete report file."""

        if format_name not in {"html", "md", "json"}:
            raise ValueError("format_name must be one of: html, md, json.")
        path = self.athlete_reports_dir / f"participant_{int(participant_id):02d}.{format_name}"
        if not path.exists():
            raise FileNotFoundError(f"Report file is missing: {path}")
        return path.read_text(encoding="utf-8")

    def report_paths(self, participant_id: int) -> dict[str, str]:
        """Return existing report paths for one participant."""

        stem = f"participant_{int(participant_id):02d}"
        paths = {
            "markdown": self.athlete_reports_dir / f"{stem}.md",
            "html": self.athlete_reports_dir / f"{stem}.html",
            "json": self.athlete_reports_dir / f"{stem}.json",
        }
        return {name: str(path) for name, path in paths.items() if path.exists()}

    def list_reports(self) -> list[dict[str, Any]]:
        """Return available Prompt 7 participant reports."""

        return [
            {"participant_id": participant_id, **self.report_paths(participant_id)}
            for participant_id in self.athlete_ids
        ]

    def show_plot_gallery(self) -> list[dict[str, str]]:
        """Return available plot-gallery files from existing outputs."""

        plots = []
        for directory in (self.plots_dir, self.reports_dir / "biomechanical_intelligence_plots"):
            if not directory.exists():
                continue
            for path in sorted(directory.glob("*.png")):
                plots.append({"name": path.stem, "path": str(path)})
        return plots


def render_dashboard_html(payload: dict[str, Any]) -> str:
    """Render dashboard payload as standalone interactive HTML."""

    json_payload = json.dumps(_json_ready(payload), sort_keys=True)
    athletes_options = "\n".join(
        f"<option value=\"{athlete['participant_id']}\">Participant {athlete['participant_id']}</option>"
        for athlete in payload["athletes"]
    )
    feature_options = "\n".join(
        f"<option value=\"{escape(feature['feature'])}\">{escape(feature['feature'])}</option>"
        for feature in payload["features"]
    )
    return f"""<!doctype html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\">
<title>JumpGuard AI Dashboard</title>
<style>
body{{font-family:Arial,sans-serif;margin:0;background:#f7f9fb;color:#1f2933;}}
header{{background:#102a43;color:white;padding:20px 28px;}}
main{{padding:24px 28px;display:grid;gap:18px;}}
section{{background:white;border:1px solid #d9e2ec;border-radius:6px;padding:16px;}}
label{{font-weight:700;margin-right:8px;}}
select,button{{padding:7px 9px;border:1px solid #bcccdc;border-radius:4px;background:white;}}
pre{{white-space:pre-wrap;background:#f0f4f8;padding:12px;border-radius:4px;max-height:340px;overflow:auto;}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px;}}
.muted{{color:#52606d;}}
a{{color:#0b65c2;}}
</style>
</head>
<body>
<header>
<h1>JumpGuard AI Dashboard</h1>
<p>{escape(payload['safety_statement'])}</p>
</header>
<main>
<section>
<label for=\"athleteSelector\">Athlete</label>
<select id=\"athleteSelector\">{athletes_options}</select>
<button onclick=\"renderAthlete()\">Show Athlete</button>
</section>
<section class=\"grid\">
<div><h2>Athlete Overview</h2><pre id=\"athleteOverview\"></pre></div>
<div><h2>Biomechanical Observations</h2><pre id=\"athleteObservations\"></pre></div>
<div><h2>Evidence-Based Observations</h2><pre id=\"evidenceObservations\"></pre></div>
<div><h2>Athlete Reports</h2><div id=\"athleteReports\"></div></div>
</section>
<section>
<label for=\"featureSelector\">Feature Browser</label>
<select id=\"featureSelector\">{feature_options}</select>
<button onclick=\"renderFeature()\">Show Feature</button>
<pre id=\"featureBrowser\"></pre>
</section>
<section class=\"grid\">
<div><h2>Population Summary</h2><pre id=\"populationSummary\"></pre></div>
<div><h2>Symmetry Dashboard</h2><pre id=\"symmetrySummary\"></pre></div>
</section>
<section>
<h2>Plot Gallery</h2>
<div id=\"plotGallery\"></div>
</section>
</main>
<script>
const DATA = {json_payload};
function pretty(value) {{ return JSON.stringify(value, null, 2); }}
function currentAthlete() {{
  const id = Number(document.getElementById('athleteSelector').value);
  return DATA.athletes.find(item => item.participant_id === id);
}}
function renderAthlete() {{
  const athlete = currentAthlete();
  document.getElementById('athleteOverview').textContent = pretty(athlete.summary);
  document.getElementById('athleteObservations').textContent = pretty(athlete.observations.slice(0, 20));
  document.getElementById('evidenceObservations').textContent = pretty(athlete.evidence_based_observations.slice(0, 20));
  const reports = athlete.reports;
  document.getElementById('athleteReports').innerHTML = Object.keys(reports).map(
    key => `<p><a href=\"../../${{reports[key]}}\">${{key}}</a></p>`
  ).join('') || '<p class=\"muted\">No report files available.</p>';
  document.getElementById('symmetrySummary').textContent = pretty(
    DATA.symmetry.rows.filter(row => row.participant_id === athlete.participant_id)
  );
}}
function renderFeature() {{
  const name = document.getElementById('featureSelector').value;
  const feature = DATA.features.find(item => item.feature === name);
  document.getElementById('featureBrowser').textContent = pretty(feature);
}}
function renderStatic() {{
  document.getElementById('populationSummary').textContent = pretty({{
    feature_count: DATA.population.feature_count,
    first_features: DATA.population.statistics.slice(0, 8)
  }});
  document.getElementById('plotGallery').innerHTML = DATA.plot_gallery.slice(0, 80).map(
    plot => `<p><a href=\"../../${{plot.path}}\">${{plot.name}}</a></p>`
  ).join('');
  renderAthlete();
  renderFeature();
}}
renderStatic();
</script>
</body>
</html>
"""


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Required dashboard input is missing: {path}")
    return pd.read_csv(path)


def _read_json_records_optional(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.DataFrame(json.loads(path.read_text(encoding="utf-8")))


def _require_dir(path: Path) -> None:
    if not path.exists() or not path.is_dir():
        raise FileNotFoundError(f"Required dashboard directory is missing: {path}")


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return [_record(row) for row in frame.to_dict(orient="records")]


def _record(mapping: dict[str, Any]) -> dict[str, Any]:
    return {str(key): _json_ready(value) for key, value in mapping.items()}


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
