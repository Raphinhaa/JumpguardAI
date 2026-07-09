"""Shared utilities for JumpGuard AI dataset exploration."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
SAMPLE_DIR = DATA_DIR / "sample"
METADATA_DIR = DATA_DIR / "metadata"


def resolve_project_path(path: str | Path) -> Path:
    """Resolve a relative path from the project root.

    Args:
        path: Relative project path or an absolute path.

    Returns:
        An absolute Path.

    Examples:
        >>> resolve_project_path("data").name
        'data'
    """
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return PROJECT_ROOT / candidate


def require_file(path: str | Path) -> Path:
    """Validate and resolve a required file.

    Args:
        path: Relative project path or absolute file path.

    Returns:
        Resolved existing file path.

    Raises:
        FileNotFoundError: If the path is missing or is not a file.

    Examples:
        >>> require_file("requirements.txt").name
        'requirements.txt'
    """
    resolved = resolve_project_path(path)
    if not resolved.exists():
        raise FileNotFoundError(f"Required file not found: {resolved}")
    if not resolved.is_file():
        raise FileNotFoundError(f"Expected a file but found another path type: {resolved}")
    return resolved


def format_bytes(size_bytes: int) -> str:
    """Format a byte count for readable output.

    Args:
        size_bytes: Nonnegative byte count.

    Returns:
        Human-readable binary-unit text.

    Examples:
        >>> format_bytes(1024)
        '1.0 KB'
    """
    units = ("B", "KB", "MB", "GB", "TB")
    value = float(size_bytes)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{size_bytes} B"
