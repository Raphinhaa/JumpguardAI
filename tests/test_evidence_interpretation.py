"""Tests for Prompt 13 evidence-based interpretation layer."""

from pathlib import Path
import json

import pandas as pd

from src.evidence_interpretation import (
    EvidenceBasedInterpreter,
    assess_evidence_based_interpretation,
    export_evidence_outputs,
)


def test_knowledge_base_is_traceable_and_non_predictive() -> None:
    interpreter = EvidenceBasedInterpreter()
    table = interpreter.knowledge_base_table()

    assert set(table["rule_id"]) == {
        "sagittal_knee_flexion",
        "sagittal_hip_strategy",
        "sagittal_ankle_strategy",
        "bilateral_rom_symmetry",
    }
    assert table["supporting_literature"].map(bool).all()
    text = json.dumps(table.to_dict(orient="records")).lower()
    assert "risk score" not in text
    assert "probability" not in text
    assert "diagnostic" in text


def test_interpretation_uses_supported_features_and_omits_timing() -> None:
    percentiles = pd.read_csv("reports/athlete_percentiles.csv")
    result = EvidenceBasedInterpreter().interpret_athlete_percentiles(percentiles, participant_id=1)

    assert not result.observations.empty
    exported = result.observations.to_dict(orient="records")
    serialized = json.dumps(exported).lower()
    assert "time_to_peak" not in serialized
    assert "prediction" in serialized
    assert all(row["literature_sources"] for row in exported)
    for row in exported:
        assert row["safety_label"] == "context_only_not_diagnosis_not_prediction"
        assert row["features_used"]
        assert row["supporting_features"]


def test_feature_table_export_is_deterministic(tmp_path: Path) -> None:
    features = pd.read_csv("data/processed/features.csv").head(6)
    result = assess_evidence_based_interpretation(features, reference_table=pd.read_csv("data/processed/features.csv"))

    first = export_evidence_outputs(result, tmp_path)
    first_json = first["observations_json"].read_text(encoding="utf-8")
    second = export_evidence_outputs(result, tmp_path)
    second_json = second["observations_json"].read_text(encoding="utf-8")

    assert first_json == second_json
    assert first["knowledge_base_json"].exists()
    payload = json.loads(first_json)
    assert isinstance(payload, list)
