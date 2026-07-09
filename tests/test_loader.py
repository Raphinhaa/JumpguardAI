"""Tests for source-file loading and version detection."""

from pathlib import Path

from src.load_dataset import detect_matlab_version, load_excel_workbook, load_mat_dataset


def test_detects_classic_mat_file() -> None:
    info = detect_matlab_version("data/sample/DJ.mat")
    assert info.loader == "scipy.io.loadmat"
    assert "MATLAB" in info.header
    assert info.size_bytes > 0


def test_loads_mat_without_interpreting_raw_structure() -> None:
    info, data = load_mat_dataset("data/sample/DJ.mat")
    assert info.path.name == "DJ.mat"
    assert set(key for key in data if not key.startswith("__")) == {"DJ"}


def test_loads_every_workbook_sheet() -> None:
    workbook = load_excel_workbook("data/metadata/IK_column_labels.xlsx")
    assert list(workbook) == ["CMJ_dom_t1_IK"]
    assert workbook["CMJ_dom_t1_IK"].shape == (11, 44)
