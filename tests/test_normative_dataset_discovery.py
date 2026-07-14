"""Tests for Prompt 18 healthy normative dataset discovery docs."""

from __future__ import annotations

from pathlib import Path

from src.normative_dataset_discovery import CANDIDATES, generate_normative_dataset_discovery_docs


def test_normative_dataset_discovery_docs_are_complete_and_conservative(tmp_path: Path) -> None:
    paths = generate_normative_dataset_discovery_docs(tmp_path)
    generated = list(paths.__dict__.values())

    assert len(generated) == 7
    assert all(path.exists() for path in generated)

    survey = paths.healthy_dataset_survey.read_text(encoding="utf-8")
    compatibility = paths.dataset_compatibility.read_text(encoding="utf-8")
    plan = paths.normative_reference_plan.read_text(encoding="utf-8")
    protocol = paths.statistical_reference_protocol.read_text(encoding="utf-8")
    pipeline = paths.processing_pipeline.read_text(encoding="utf-8")
    roadmap = paths.future_validation_roadmap.read_text(encoding="utf-8")
    recommendations = paths.dataset_recommendations.read_text(encoding="utf-8")

    for candidate in CANDIDATES:
        assert candidate.name in survey
        assert candidate.name in compatibility
        assert candidate.name in pipeline
        assert candidate.name in recommendations
        assert candidate.doi_or_url in survey

    assert "No discovered public dataset satisfies all Prompt 18 requirements" in survey
    assert "Unknown from available evidence" in survey
    assert "without code changes" in pipeline
    assert "No new pose model" in compatibility
    assert "No smoothing, pose interpolation" in plan
    assert "existing 57-feature JumpGuard schema" in protocol
    assert "Healthy Videos" in roadmap
    assert "No discovered public dataset is recommended for immediate production use" in recommendations
    assert "must not be inferred from video appearance" in recommendations
