"""Tests for Prompt 7 athlete reporting layer."""

from pathlib import Path
import json

from src.reporting import AthleteReportGenerator, render_html, render_markdown


def test_report_generation_uses_existing_outputs() -> None:
    generator = AthleteReportGenerator(reports_dir="reports")
    report = generator.generate(1, include_visualizations=False)

    assert report.participant_id == 1
    assert report.overview["available_trials"] == 6
    assert report.overview["valid_trials"] == 6
    assert report.overview["empty_trials"] == 0
    assert set(report.biomechanical_summary) == {
        "Hip Flexion",
        "Knee Flexion",
        "Ankle Angle",
    }
    assert len(report.population_comparison) == 57
    assert report.observations


def test_empty_participant_report_preserves_missing_values() -> None:
    generator = AthleteReportGenerator(reports_dir="reports")
    report = generator.generate(44, include_visualizations=True)

    assert report.overview["valid_trials"] == 0
    assert report.overview["feature_completeness"] == 0.0
    assert report.visualizations == {}
    assert all(row["value"] is None for row in report.population_comparison)


def test_markdown_html_and_json_exports(tmp_path: Path) -> None:
    generator = AthleteReportGenerator(reports_dir="reports")
    report = generator.generate(1, include_visualizations=False)

    json_path = generator.save_json(report, tmp_path / "participant_01.json")
    markdown_path = generator.save_markdown(report, tmp_path / "participant_01.md")
    html_path = generator.save_html(report, tmp_path / "participant_01.html")

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    html = html_path.read_text(encoding="utf-8")

    assert payload["participant_id"] == 1
    assert "overview" in payload
    assert "population_comparison" in payload
    assert "# Athlete Report: Participant 1" in markdown
    assert "<html" in html
    assert "medical diagnosis" in payload["safety_statement"]


def test_visualization_export(tmp_path: Path) -> None:
    generator = AthleteReportGenerator(reports_dir="reports")
    report = generator.generate(1, include_visualizations=True, output_dir=tmp_path)

    assert set(report.visualizations) == {
        "radar_chart",
        "percentile_comparison",
        "population_comparison",
        "symmetry_comparison",
        "distribution_plots",
    }
    assert all(Path(path).exists() for path in report.visualizations.values())


def test_batch_generation_and_determinism(tmp_path: Path) -> None:
    generator = AthleteReportGenerator(reports_dir="reports")
    first = generator.generate_all_reports(tmp_path / "reports", include_visualizations=False)
    first_json = (tmp_path / "reports" / "participant_01.json").read_text(encoding="utf-8")
    second = generator.generate_all_reports(tmp_path / "reports", include_visualizations=False)
    second_json = (tmp_path / "reports" / "participant_01.json").read_text(encoding="utf-8")

    assert len(first) == 43
    assert len(second) == 43
    assert first_json == second_json
    assert (tmp_path / "reports" / "participant_44.md").exists()


def test_renderer_api_is_pure() -> None:
    generator = AthleteReportGenerator(reports_dir="reports")
    report = generator.generate(1, include_visualizations=False)

    assert render_markdown(report) == render_markdown(report)
    assert render_html(report) == render_html(report)
