"""Professional HTML rendering for Prompt 13 evidence observations."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np


def render_evidence_observations_html(
    observations: list[dict[str, Any]],
    *,
    asset_dir: str | Path | None = None,
    asset_href_prefix: str = "",
    filename_prefix: str = "evidence_observation",
) -> str:
    """Render evidence observations as clinician-readable HTML cards.

    The renderer consumes existing Prompt 13 observation records and does not
    modify or reinterpret the scientific content.
    """

    if not observations:
        return (
            "<section class=\"evidence-section\"><h2>Evidence-Based ACL Biomechanical Observations</h2>"
            "<p class=\"muted\">No evidence-based observations generated.</p></section>"
        )
    rendered = [
        "<section class=\"evidence-section\">",
        "<h2>Evidence-Based ACL Biomechanical Observations</h2>",
        "<p class=\"section-note\">Observations are descriptive, dataset-relative, and non-diagnostic. "
        "They do not estimate ACL injury probability or assign a risk score.</p>",
    ]
    for index, observation in enumerate(observations, start=1):
        figures = _export_figures(observation, asset_dir, filename_prefix, index)
        rendered.append(_render_observation_card(observation, figures, asset_href_prefix, index))
    rendered.append("</section>")
    return "".join(rendered)


def evidence_report_css() -> str:
    """Return CSS used by professional evidence report cards."""

    return """
:root{--ink:#1f2933;--muted:#52606d;--line:#d9e2ec;--panel:#ffffff;--soft:#f7f9fb;--accent:#315a7d;--accent-soft:#e7eef5;--ok:#4d7c59;--warn:#a86816;--low:#2f6f9f;}
body{font-family:Arial,Helvetica,sans-serif;line-height:1.5;color:var(--ink);background:#f4f7fa;margin:0;}
.report-shell{max-width:1180px;margin:0 auto;padding:32px 24px 48px;}
.report-header{background:#102a43;color:#fff;padding:28px 32px;border-radius:8px;margin-bottom:22px;}
.report-header h1{margin:0 0 8px;font-size:28px;letter-spacing:0;}
.report-header p{margin:0;color:#dbe8f4;}
.summary-card,.evidence-card,.simple-card{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:20px;margin:18px 0;box-shadow:0 1px 2px rgba(16,42,67,.05);}
.evidence-section h2{font-size:24px;margin:26px 0 8px;color:#102a43;}
.section-note,.muted{color:var(--muted);}
.evidence-card h3{margin:0;color:#102a43;font-size:21px;}
.card-meta{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 16px;}
.badge{display:inline-block;border:1px solid var(--line);background:var(--accent-soft);color:#17324d;border-radius:999px;padding:4px 10px;font-size:12px;font-weight:700;}
.evidence-grid{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(280px,.9fr);gap:18px;align-items:start;}
.prose-block h4,.measurement-block h4,.literature-block h4{margin:16px 0 6px;color:#243b53;font-size:15px;text-transform:uppercase;letter-spacing:.03em;}
.prose-block p{margin:0 0 10px;color:#263238;}
.measurement-table{width:100%;border-collapse:collapse;font-size:13px;background:#fff;border:1px solid var(--line);}
.measurement-table th{background:#eef3f8;text-align:left;color:#243b53;font-weight:700;border-bottom:1px solid var(--line);padding:9px;}
.measurement-table td{border-bottom:1px solid #edf2f7;padding:8px 9px;vertical-align:top;}
.measurement-table tr:nth-child(even) td{background:#fbfdff;}
.figure-grid{display:grid;grid-template-columns:1fr;gap:12px;margin-top:14px;}
.figure-grid figure{margin:0;border:1px solid var(--line);border-radius:6px;background:#fff;padding:10px;}
.figure-grid img{display:block;width:100%;height:auto;}
.figure-grid figcaption{font-size:12px;color:var(--muted);margin-top:6px;}
.literature-list{margin:8px 0 0;padding-left:18px;}
.literature-list li{margin-bottom:8px;}
.literature-list a{color:#0b65c2;text-decoration:none;}
.literature-list a:hover{text-decoration:underline;}
.limitation{border-left:4px solid #bcccdc;background:#f8fafc;padding:10px 12px;color:#394b59;}
@media(max-width:900px){.evidence-grid{grid-template-columns:1fr}.report-shell{padding:18px 14px}.report-header{border-radius:0;margin:0 -14px 18px}.measurement-table{font-size:12px}}
"""


def _render_observation_card(
    observation: dict[str, Any],
    figures: dict[str, Path],
    asset_href_prefix: str,
    index: int,
) -> str:
    title = _clean_title(str(observation.get("title", f"Observation {index}")))
    evidence_strength = str(observation.get("evidence_strength", "Not specified"))
    supporting = observation.get("supporting_features") or []
    return (
        "<article class=\"evidence-card\">"
        f"<h3>{escape(title)}</h3>"
        "<div class=\"card-meta\">"
        f"<span class=\"badge\">Evidence strength: {escape(evidence_strength)}</span>"
        f"<span class=\"badge\">{len(supporting)} supporting measurement(s)</span>"
        "</div>"
        "<div class=\"evidence-grid\">"
        "<div>"
        + _render_prose_blocks(observation)
        + _render_literature(observation)
        + "</div>"
        "<div class=\"measurement-block\">"
        "<h4>Athlete vs Reference Dataset</h4>"
        + _render_measurement_table(supporting)
        + _render_figures(figures, asset_href_prefix)
        + "</div>"
        "</div>"
        "</article>"
    )


def _render_prose_blocks(observation: dict[str, Any]) -> str:
    return (
        "<div class=\"prose-block\">"
        "<h4>Clinical Relevance</h4>"
        f"<p>{escape(str(observation.get('comparison_performed', 'Dataset-relative comparison unavailable.')))}</p>"
        "<h4>Interpretation</h4>"
        f"<p>{escape(str(observation.get('evidence_based_explanation', '')))}</p>"
        "<h4>Suggested Clinical Consideration</h4>"
        f"<p>{escape(str(observation.get('suggested_clinical_consideration', '')))}</p>"
        "<h4>Limitations</h4>"
        f"<p class=\"limitation\">{escape(str(observation.get('limitation', '')))}</p>"
        "</div>"
    )


def _render_measurement_table(features: list[dict[str, Any]]) -> str:
    if not features:
        return "<p class=\"muted\">No supporting measurements available.</p>"
    rows = []
    for feature in features:
        rows.append(
            "<tr>"
            f"<td>{escape(_human_feature_label(str(feature.get('feature', ''))))}</td>"
            f"<td>{_format_number(feature.get('measured_value'))}</td>"
            f"<td>{_format_number(feature.get('reference_mean'))}</td>"
            f"<td>{_format_interval(feature)}</td>"
            f"<td>{_format_percentile(feature.get('reference_percentile'))}</td>"
            "</tr>"
        )
    return (
        "<table class=\"measurement-table\"><thead><tr>"
        "<th>Measurement</th><th>Athlete</th><th>Reference Dataset Mean</th>"
        "<th>Reference Dataset Central 90% Interval</th><th>Percentile</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )


def _render_literature(observation: dict[str, Any]) -> str:
    sources = observation.get("literature_sources") or []
    if not sources:
        return ""
    items = []
    for source in sources:
        citation = escape(str(source.get("citation", "")))
        url = source.get("url") or (f"https://doi.org/{source.get('doi')}" if source.get("doi") else None)
        doi = source.get("doi")
        link = f" <a href=\"{escape(str(url))}\">DOI: {escape(str(doi))}</a>" if url and doi else ""
        items.append(f"<li>{citation}{link}</li>")
    return "<div class=\"literature-block\"><h4>Supporting Literature</h4><ul class=\"literature-list\">" + "".join(items) + "</ul></div>"


def _render_figures(figures: dict[str, Path], asset_href_prefix: str) -> str:
    if not figures:
        return ""
    parts = ["<div class=\"figure-grid\">"]
    captions = {
        "interval": "Athlete measurement relative to the reference central 90% interval.",
        "comparison": "Athlete measurements compared with reference dataset means.",
    }
    for key in ("interval", "comparison"):
        path = figures.get(key)
        if path is None:
            continue
        href = f"{asset_href_prefix}{path.name}"
        parts.append(
            f"<figure><img src=\"{escape(href)}\" alt=\"{escape(captions[key])}\">"
            f"<figcaption>{escape(captions[key])}</figcaption></figure>"
        )
    parts.append("</div>")
    return "".join(parts)


def _export_figures(
    observation: dict[str, Any],
    asset_dir: str | Path | None,
    filename_prefix: str,
    index: int,
) -> dict[str, Path]:
    features = observation.get("supporting_features") or []
    if asset_dir is None or not features:
        return {}
    destination = Path(asset_dir)
    destination.mkdir(parents=True, exist_ok=True)
    safe_id = _safe_filename(str(observation.get("observation_id", f"observation_{index}")))
    paths = {
        "interval": destination / f"{filename_prefix}_{index:02d}_{safe_id}_interval.png",
        "comparison": destination / f"{filename_prefix}_{index:02d}_{safe_id}_comparison.png",
    }
    _plot_reference_interval(features, paths["interval"])
    _plot_grouped_comparison(features, paths["comparison"])
    return paths


def _plot_reference_interval(features: list[dict[str, Any]], path: Path) -> None:
    labels = [_human_feature_label(str(item.get("feature", ""))) for item in features]
    y = np.arange(len(features))
    p05 = np.array([float(item["reference_p05"]) for item in features])
    p95 = np.array([float(item["reference_p95"]) for item in features])
    mean = np.array([float(item["reference_mean"]) for item in features])
    athlete = np.array([float(item["measured_value"]) for item in features])
    fig_height = max(3.2, 0.46 * len(features) + 1.4)
    figure, axis = plt.subplots(figsize=(8.8, fig_height))
    for idx, item in enumerate(features):
        color = _tail_color(float(item["measured_value"]), float(item["reference_p05"]), float(item["reference_p95"]))
        axis.hlines(idx, p05[idx], p95[idx], color="#8aa7bf", linewidth=5, alpha=0.85)
        axis.scatter(mean[idx], idx, marker="D", color="#243b53", s=34, label="Reference mean" if idx == 0 else None)
        axis.scatter(athlete[idx], idx, marker="o", color=color, edgecolor="white", linewidth=0.8, s=54, label="Athlete measurement" if idx == 0 else None)
    axis.scatter([], [], color="#2f6f9f", label="Below reference central 90% interval")
    axis.scatter([], [], color="#4d7c59", label="Within reference central 90% interval")
    axis.scatter([], [], color="#a86816", label="Above reference central 90% interval")
    axis.set_yticks(y, labels)
    axis.invert_yaxis()
    axis.set_xlabel("Measurement value")
    axis.set_title("Reference Interval Comparison")
    axis.grid(axis="x", color="#d9e2ec", linewidth=0.8)
    axis.spines[["top", "right"]].set_visible(False)
    axis.legend(loc="lower center", bbox_to_anchor=(0.5, -0.34), ncol=2, frameon=False, fontsize=8)
    figure.tight_layout()
    figure.savefig(path, dpi=150, bbox_inches="tight", metadata={"Software": "JumpGuardAI"})
    plt.close(figure)


def _plot_grouped_comparison(features: list[dict[str, Any]], path: Path) -> None:
    labels = [_human_feature_label(str(item.get("feature", ""))) for item in features]
    y = np.arange(len(features))
    athlete = np.array([float(item["measured_value"]) for item in features])
    mean = np.array([float(item["reference_mean"]) for item in features])
    fig_height = max(3.2, 0.46 * len(features) + 1.4)
    figure, axis = plt.subplots(figsize=(8.8, fig_height))
    offset = 0.18
    axis.barh(y - offset, athlete, height=0.34, color="#315a7d", label="Athlete")
    axis.barh(y + offset, mean, height=0.34, color="#9fb3c8", label="Reference dataset mean")
    axis.set_yticks(y, labels)
    axis.invert_yaxis()
    axis.set_xlabel("Measurement value")
    axis.set_title("Athlete vs Reference Dataset Mean")
    axis.grid(axis="x", color="#d9e2ec", linewidth=0.8)
    axis.spines[["top", "right"]].set_visible(False)
    axis.legend(loc="lower center", bbox_to_anchor=(0.5, -0.2), ncol=2, frameon=False)
    figure.tight_layout()
    figure.savefig(path, dpi=150, bbox_inches="tight", metadata={"Software": "JumpGuardAI"})
    plt.close(figure)


def _tail_color(value: float, p05: float, p95: float) -> str:
    if value < p05:
        return "#2f6f9f"
    if value > p95:
        return "#a86816"
    return "#4d7c59"


def _clean_title(title: str) -> str:
    return title.replace(" from Prompt 11", "").rstrip(".")


def _human_feature_label(feature: str) -> str:
    replacements = {
        "hip_flexion": "Hip flexion",
        "knee_flexion": "Knee flexion",
        "ankle_angle": "Ankle angle",
        "right": "right",
        "left": "left",
        "rom": "range of motion",
        "mean": "mean",
        "median": "median",
        "maximum": "maximum",
        "minimum": "minimum",
        "absolute_difference": "absolute difference",
        "percent_difference": "percent difference",
        "symmetry_index": "symmetry index",
    }
    label = feature
    for old, new in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
        label = label.replace(old, new)
    return " ".join(label.split("_")).capitalize()


def _format_interval(feature: dict[str, Any]) -> str:
    return f"{_format_number(feature.get('reference_p05'))} to {_format_number(feature.get('reference_p95'))}"


def _format_percentile(value: Any) -> str:
    if value is None:
        return ""
    return f"{float(value):.1f}th"


def _format_number(value: Any) -> str:
    if value is None:
        return ""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return escape(str(value))
    if np.isnan(number):
        return ""
    return f"{number:.2f}"


def _safe_filename(value: str) -> str:
    safe = [character.lower() if character.isalnum() else "_" for character in value]
    return "".join(safe).strip("_")[:80] or "observation"
