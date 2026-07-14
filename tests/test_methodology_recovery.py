"""Tests for Prompt 16 methodology recovery documentation."""

from __future__ import annotations

from pathlib import Path

from src.feature_engineering import FeatureExtractor
from src.methodology_recovery import generate_methodology_recovery_docs


def test_methodology_recovery_docs_are_complete_and_conservative(tmp_path: Path) -> None:
    paths = generate_methodology_recovery_docs(tmp_path)
    generated = list(paths.__dict__.values())

    assert len(generated) == 9
    assert all(path.exists() for path in generated)

    formulas = paths.feature_formulas.read_text(encoding="utf-8")
    equivalence = paths.scientific_equivalence_matrix.read_text(encoding="utf-8")
    for feature in FeatureExtractor().feature_names:
        assert f"`{feature}`" in formulas
        assert f"`{feature}`" in equivalence

    lineage = paths.dataset_lineage.read_text(encoding="utf-8")
    ik = paths.ik_reconstruction.read_text(encoding="utf-8")
    events = paths.event_methods.read_text(encoding="utf-8")
    processing = paths.signal_processing.read_text(encoding="utf-8")
    readiness = paths.harmonization_readiness.read_text(encoding="utf-8")
    unknowns = paths.unknowns_register.read_text(encoding="utf-8")

    assert "Original publication" in lineage
    assert "Unknown from available evidence" in lineage
    assert "OpenSim-compatible" in lineage
    assert "Marker weights" in ik
    assert "Unknown from available evidence" in events
    assert "Unknown from available evidence" in processing
    assert "Partially ready, formula-only" in readiness
    assert "must remain unknown" in unknowns
