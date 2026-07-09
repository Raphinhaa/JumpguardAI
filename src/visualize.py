"""Visualization helpers for dataset exploration."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def plot_sheet_completeness(workbook: dict[str, "pd.DataFrame"]) -> None:
    """Plot non-null cell counts for each workbook sheet.

    Args:
        workbook: Worksheet names mapped to DataFrames.

    Returns:
        None. The plot is created on the current Matplotlib backend.

    Examples:
        >>> plot_sheet_completeness({"labels": frame})
    """
    import matplotlib.pyplot as plt

    sheet_names = list(workbook.keys())
    non_null_counts = [int(frame.notna().sum().sum()) for frame in workbook.values()]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(sheet_names, non_null_counts, color="#3b82f6")
    ax.set_title("IK label workbook non-null cells by sheet")
    ax.set_xlabel("Sheet")
    ax.set_ylabel("Non-null cells")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
