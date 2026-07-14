"""Tests for Prompt 17 measurement-standard documentation."""

from __future__ import annotations

from pathlib import Path

from src.feature_engineering import FeatureExtractor
from src.measurement_standard import generate_measurement_standard_docs


def test_measurement_standard_docs_are_complete_and_conservative(tmp_path: Path) -> None:
    paths = generate_measurement_standard_docs(tmp_path)
    generated = list(paths.__dict__.values())

    assert len(generated) == 7
    assert all(path.exists() for path in generated)

    validation = paths.implementation_validation.read_text(encoding="utf-8")
    matrix = paths.standards_matrix.read_text(encoding="utf-8")
    standard = paths.measurement_standard.read_text(encoding="utf-8")
    literature = paths.literature_review.read_text(encoding="utf-8")
    context = paths.clinical_context.read_text(encoding="utf-8")
    gaps = paths.gap_analysis.read_text(encoding="utf-8")
    readiness = paths.measurement_standard_readiness.read_text(encoding="utf-8")

    for feature in FeatureExtractor().feature_names:
        assert f"`{feature}`" in validation
        assert f"`{feature}`" in matrix

    assert "MediaPipe-derived geometric approximations" in standard
    assert "They are not laboratory inverse-kinematics joint angles" in standard
    assert "10.1016/S0021-9290(01)00222-6" in literature
    assert "10.1115/1.3138397" in literature
    assert "10.1177/0363546509343200" in literature
    assert "No diagnosis" in context
    assert "Not measured" in gaps
    assert "Not ready to claim laboratory biomechanical equivalence" in readiness
    assert "clinical prediction, diagnosis, injury-risk scoring" in readiness
