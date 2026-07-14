"""Tests for Prompt 13.1 professional evidence report rendering."""

import json
from pathlib import Path

from src.evidence_report_rendering import render_evidence_observations_html


def test_evidence_cards_render_without_raw_json_and_export_figures(tmp_path: Path) -> None:
    observation = json.loads(Path("reports/evidence_based_observations.json").read_text(encoding="utf-8"))[0]
    html = render_evidence_observations_html(
        [observation],
        asset_dir=tmp_path,
        asset_href_prefix="assets/",
    )

    assert "evidence-card" in html
    assert "measurement-table" in html
    assert "Supporting Literature" in html
    assert "DOI:" in html
    assert first_internal_prefix(observation) not in html
    assert any(label in html for label in ("Hip flexion", "Knee flexion", "Ankle angle"))
    assert "<pre>[" not in html
    first_feature = observation["supporting_features"][0]
    assert f"{first_feature['measured_value']:.2f}" in html
    assert f"{first_feature['reference_mean']:.2f}" in html
    assert f"{first_feature['reference_p05']:.2f} to {first_feature['reference_p95']:.2f}" in html
    assert len(sorted(tmp_path.glob("*.png"))) == 2


def first_internal_prefix(observation: dict) -> str:
    return str(observation["supporting_features"][0]["feature"]).split("_left")[0].split("_right")[0]
