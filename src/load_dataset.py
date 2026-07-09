"""Dataset loading helpers for MATLAB and spreadsheet source files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import h5py

from .utils import require_file

if TYPE_CHECKING:
    import pandas as pd


@dataclass(frozen=True)
class MatFileInfo:
    """Basic information about a MATLAB data file.

    Args:
        path: Resolved MAT-file path.
        version: Detected format description.
        loader: Selected loader name.
        header: Decoded 128-byte MAT header.
        size_bytes: Source file size.

    Examples:
        >>> info = detect_matlab_version("data/sample/DJ.mat")
        >>> info.loader
        'scipy.io.loadmat'
    """

    path: Path
    version: str
    loader: str
    header: str
    size_bytes: int


def detect_matlab_version(path: str | Path) -> MatFileInfo:
    """Detect whether a MAT file is classic or HDF5-backed.

    Args:
        path: MAT-file path.

    Returns:
        Detection metadata and the required loader.

    Examples:
        >>> detect_matlab_version("data/sample/DJ.mat").loader
        'scipy.io.loadmat'
    """
    mat_path = require_file(path)
    with mat_path.open("rb") as file:
        header_bytes = file.read(128)

    header = header_bytes.decode("latin-1", errors="replace").strip("\x00").strip()
    if h5py.is_hdf5(mat_path):
        version = "MATLAB v7.3 or HDF5-backed MAT-file"
        loader = "h5py"
    elif "MATLAB 5.0 MAT-file" in header:
        version = "MATLAB v5/v6/v7 classic MAT-file"
        loader = "scipy.io.loadmat"
    else:
        version = "Unknown MAT-file variant"
        loader = "undetermined"

    return MatFileInfo(
        path=mat_path,
        version=version,
        loader=loader,
        header=header,
        size_bytes=mat_path.stat().st_size,
    )


def _load_hdf5_group(group: h5py.Group) -> dict[str, Any]:
    """Recursively copy HDF5 datasets and groups into Python containers."""
    output: dict[str, Any] = {}
    for key, value in group.items():
        if isinstance(value, h5py.Dataset):
            output[key] = value[()]
        elif isinstance(value, h5py.Group):
            output[key] = _load_hdf5_group(value)
        else:
            output[key] = value
    return output


def load_mat_dataset(path: str | Path) -> tuple[MatFileInfo, dict[str, Any]]:
    """Load a MATLAB source without interpreting its domain hierarchy.

    Args:
        path: MAT-file path.

    Returns:
        Detection metadata and the raw loaded mapping.

    Raises:
        ValueError: If the MAT variant cannot be determined.

    Examples:
        >>> info, raw = load_mat_dataset("data/sample/DJ.mat")
        >>> "DJ" in raw
        True
    """
    info = detect_matlab_version(path)

    if info.loader == "h5py":
        with h5py.File(info.path, "r") as file:
            data = _load_hdf5_group(file)
        return info, data

    if info.loader == "scipy.io.loadmat":
        try:
            from scipy.io import loadmat
        except ImportError as exc:
            raise ImportError(
                "scipy is required to load this classic MATLAB file. "
                "Install project requirements before running this notebook."
            ) from exc

        data = loadmat(info.path, squeeze_me=False, struct_as_record=False)
        return info, data

    raise ValueError(
        f"Could not determine how to load MATLAB file {info.path}. "
        f"Header begins with: {info.header[:80]!r}"
    )


def load_excel_workbook(path: str | Path) -> dict[str, "pd.DataFrame"]:
    """Load every worksheet into a named DataFrame mapping.

    Args:
        path: Excel workbook path.

    Returns:
        Mapping from worksheet name to DataFrame.

    Examples:
        >>> workbook = load_excel_workbook("data/metadata/IK_column_labels.xlsx")
        >>> list(workbook)
        ['CMJ_dom_t1_IK']
    """
    excel_path = require_file(path)
    try:
        import pandas as pd

        workbook = pd.read_excel(excel_path, sheet_name=None)
    except ImportError as exc:
        raise ImportError(
            "pandas with openpyxl is required to read Excel metadata files. "
            "Install project requirements before running this notebook."
        ) from exc

    return workbook
