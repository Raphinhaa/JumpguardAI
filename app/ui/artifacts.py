"""Shared browser URL helpers for served JumpGuard artifacts."""

from __future__ import annotations

from html import escape
from pathlib import Path


def artifact_href(path: str | Path) -> str:
    """Return the browser URL used by the app's `/artifact` endpoint."""

    return "/artifact?path=" + escape(str(path), quote=True)

