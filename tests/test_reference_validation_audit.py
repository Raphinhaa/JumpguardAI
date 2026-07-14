"""Tests for Prompt 15 reference-dataset validation audit docs."""

from __future__ import annotations

from pathlib import Path

from src.feature_engineering import FeatureExtractor
from src.reference_validation_audit import generate_reference_validation_audit


def test_reference_validation_audit_documents_every_feature_and_unknown(tmp_path: Path) -> None:
    paths = generate_reference_validation_audit(tmp_path)
    generated = list(paths.__dict__.values())

    assert len(generated) == 8
    assert all(path.exists() for path in generated)

    feature_mapping = paths.feature_mapping.read_text(encoding="utf-8")
    mathematical = paths.mathematical_equivalence.read_text(encoding="utf-8")
    frame = paths.frame_comparability.read_text(encoding="utf-8")
    for feature in FeatureExtractor().feature_names:
        assert f"`{feature}`" in feature_mapping
        assert f"`{feature}`" in mathematical
        assert f"`{feature}`" in frame

    dataset_doc = paths.dataset_reverse_engineering.read_text(encoding="utf-8")
    event_doc = paths.event_definition_audit.read_text(encoding="utf-8")
    angle_doc = paths.angle_standardization.read_text(encoding="utf-8")
    recommendations = paths.harmonization_recommendations.read_text(encoding="utf-8")
    confidence = paths.scientific_confidence_matrix.read_text(encoding="utf-8")

    assert "Unknown from available evidence" in dataset_doc
    assert "Unknown from available evidence" in event_doc
    assert "Do not apply" in angle_doc
    assert "No data or calculations are changed" in recommendations
    assert "not established" in confidence or "not-yet-harmonized" in confidence
