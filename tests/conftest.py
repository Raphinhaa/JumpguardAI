"""Shared fixtures for the core data framework tests."""

from __future__ import annotations

import matplotlib
import pytest

from src.dataset import Dataset


matplotlib.use("Agg")


@pytest.fixture(scope="session")
def dataset() -> Dataset:
    """Load the canonical Dataset once for integration-oriented unit tests."""
    return Dataset.load("data/sample/DJ.mat")
