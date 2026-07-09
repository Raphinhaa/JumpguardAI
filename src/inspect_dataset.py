"""Inspection helpers for dynamically understanding dataset structure."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

import numpy as np

from .dataset_parser import RawArraySummary, summarize_raw_structure

if TYPE_CHECKING:
    import pandas as pd


ArraySummary = RawArraySummary


def describe_object(value: Any) -> tuple[str, tuple[int, ...] | None, str | None, int | None]:
    """Describe the type and available array metadata of a value.

    Args:
        value: Any Python value.

    Returns:
        Type name, shape, dtype text, and dimension count.

    Examples:
        >>> describe_object(np.zeros((2, 3)))[1]
        (2, 3)
    """
    type_name = type(value).__name__
    shape = tuple(value.shape) if hasattr(value, "shape") else None
    dtype = str(value.dtype) if hasattr(value, "dtype") else None
    ndim = int(value.ndim) if hasattr(value, "ndim") else None
    return type_name, shape, dtype, ndim


def summarize_structure(
    obj: Any,
    name: str = "root",
    max_depth: int = 5,
    max_object_items: int = 300,
    _depth: int = 0,
) -> list[ArraySummary]:
    """Recursively summarize raw source containers through the parser.

    Args:
        obj: Raw value to inspect.
        name: Root path shown in summaries.
        max_depth: Maximum recursive depth.
        max_object_items: Largest object container expanded element by element.
        _depth: Internal recursion depth retained for backwards compatibility.

    Returns:
        Ordered structure summaries.

    Examples:
        >>> summarize_structure(np.zeros((2, 3)))[0].shape
        (2, 3)
    """
    return summarize_raw_structure(obj, name, max_depth, max_object_items, _depth)


def print_structure_summary(summaries: Iterable[ArraySummary]) -> None:
    """Print structure summaries in a compact table.

    Args:
        summaries: Structure descriptions to print.

    Returns:
        None.

    Examples:
        >>> print_structure_summary(summarize_structure(np.zeros((1, 2))))
    """
    print(f"{'Path':60} {'Type':20} {'Shape':20} {'Dtype':20} {'Ndim'}")
    print("-" * 130)
    for item in summaries:
        print(
            f"{item.path[:60]:60} "
            f"{item.type_name[:20]:20} "
            f"{str(item.shape)[:20]:20} "
            f"{str(item.dtype)[:20]:20} "
            f"{str(item.ndim)}"
        )


def summarize_label_workbook(workbook: dict[str, "pd.DataFrame"]) -> "pd.DataFrame":
    """Summarize worksheet dimensions and non-null content.

    Args:
        workbook: Worksheet names mapped to DataFrames.

    Returns:
        One summary row per worksheet.

    Examples:
        >>> summarize_label_workbook({"labels": frame}).iloc[0]["sheet"]
        'labels'
    """
    import pandas as pd

    rows: list[dict[str, object]] = []
    for sheet_name, frame in workbook.items():
        rows.append(
            {
                "sheet": sheet_name,
                "rows": frame.shape[0],
                "columns": frame.shape[1],
                "column_names": list(frame.columns),
                "non_null_cells": int(frame.notna().sum().sum()),
            }
        )
    return pd.DataFrame(rows)


def extract_label_values(workbook: dict[str, "pd.DataFrame"]) -> list[str]:
    """Extract every non-empty string from workbook cells.

    Args:
        workbook: Worksheet names mapped to DataFrames.

    Returns:
        Strings in worksheet and row-major cell order.

    Examples:
        >>> extract_label_values({"sheet": frame})
        ['time', 'knee_angle_r']
    """
    labels: list[str] = []
    for frame in workbook.values():
        for value in frame.to_numpy().ravel():
            if isinstance(value, str) and value.strip():
                labels.append(value.strip())
    return labels


def find_numeric_arrays(
    summaries: Iterable[ArraySummary],
    min_dimensions: int = 2,
) -> list[ArraySummary]:
    """Select numeric array summaries with a minimum dimension count.

    Args:
        summaries: Structure descriptions to search.
        min_dimensions: Minimum number of array dimensions.

    Returns:
        Matching numeric-array summaries.

    Examples:
        >>> find_numeric_arrays(summarize_structure(np.zeros((2, 3))))[0].shape
        (2, 3)
    """
    numeric_markers = ("float", "int", "uint", "double", "single")
    arrays: list[ArraySummary] = []
    for item in summaries:
        if not item.shape or item.ndim is None or item.ndim < min_dimensions:
            continue
        if item.dtype and any(marker in item.dtype.lower() for marker in numeric_markers):
            arrays.append(item)
    return arrays


def investigate_label_mapping(
    summaries: Iterable[ArraySummary],
    label_count: int,
) -> "pd.DataFrame":
    """Find numeric array axes matching an IK-label count.

    Args:
        summaries: Structure descriptions to search.
        label_count: Number of semantic labels.

    Returns:
        Candidate paths, shapes, dtypes, and matching axes.

    Examples:
        >>> result = investigate_label_mapping(summaries, 44)
        >>> "path" in result.columns
        True
    """
    import pandas as pd

    rows: list[dict[str, object]] = []
    for item in find_numeric_arrays(summaries):
        matching_axes = [
            axis_index
            for axis_index, axis_size in enumerate(item.shape or ())
            if axis_size == label_count
        ]
        if matching_axes:
            rows.append(
                {
                    "path": item.path,
                    "shape": item.shape,
                    "dtype": item.dtype,
                    "matching_axes": matching_axes,
                    "label_count": label_count,
                }
            )
    return pd.DataFrame(rows)
