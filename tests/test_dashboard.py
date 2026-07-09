"""Tests for Prompt 8 dashboard and visualization layer."""

from pathlib import Path
import json

import pytest

from src.dashboard import Dashboard, render_dashboard_html


def test_dashboard_loads_existing_outputs() -> None:
    dashboard = Dashboard()

    assert len(dashboard.athlete_ids) == 43
    assert len(dashboard.feature_names) == 57
    assert dashboard.features.shape[0] == 258
    assert dashboard.athlete_summary.shape[0] == 43


def test_show_athlete_and_missing_data() -> None:
    dashboard = Dashboard()
    athlete = dashboard.show_athlete(1)
    empty = dashboard.show_athlete(44)

    assert athlete["participant_id"] == 1
    assert athlete["missing_feature_count"] == 0
    assert athlete["observations"]
    assert empty["participant_id"] == 44
    assert empty["missing_feature_count"] == 57
    assert empty["observations"] == []


def test_feature_population_symmetry_and_report_loading() -> None:
    dashboard = Dashboard()
    feature = dashboard.show_feature("knee_flexion_right_rom")
    population = dashboard.show_population()
    symmetry = dashboard.show_symmetry(participant_id=1)
    html = dashboard.load_report(1, "html")

    assert feature["feature"] == "knee_flexion_right_rom"
    assert len(feature["athlete_values"]) == 43
    assert population["feature_count"] == 57
    assert symmetry["rows"]
    assert "<html" in html


def test_time_series_requires_existing_dataset() -> None:
    dashboard = Dashboard()
    response = dashboard.show_time_series(1)

    assert response["available"] is False
    assert "Dataset" in response["reason"]


def test_export_and_launch_are_deterministic(tmp_path: Path) -> None:
    dashboard = Dashboard()
    first = dashboard.export(tmp_path)
    first_json = first.json.read_text(encoding="utf-8")
    first_html = first.html.read_text(encoding="utf-8")
    second = dashboard.export(tmp_path)

    assert first.html == second.html
    assert first.json == second.json
    assert second.json.read_text(encoding="utf-8") == first_json
    assert second.html.read_text(encoding="utf-8") == first_html
    assert dashboard.launch(tmp_path) == first.html
    payload = json.loads(first.json.read_text(encoding="utf-8"))
    assert payload["time_series_available"] is False


def test_dashboard_payload_and_html_renderer() -> None:
    dashboard = Dashboard()
    payload = dashboard.dashboard_payload()
    html = render_dashboard_html(payload)

    assert set(payload) >= {"athletes", "features", "population", "plot_gallery", "reports"}
    assert "JumpGuard AI Dashboard" in html
    assert "athleteSelector" in html
    assert "featureSelector" in html


def test_invalid_feature_report_and_missing_inputs(tmp_path: Path) -> None:
    dashboard = Dashboard()

    with pytest.raises(KeyError):
        dashboard.show_feature("not_a_feature")
    with pytest.raises(ValueError):
        dashboard.load_report(1, "pdf")
    with pytest.raises(FileNotFoundError):
        Dashboard(features_path=tmp_path / "missing.csv")
