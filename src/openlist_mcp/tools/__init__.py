"""OpenList MCP Tools package."""

import os


def validate_path(path: str) -> None:
    """Validate that a path does not contain directory traversal sequences.

    Rejects paths with '..' components to prevent TOCTOU/client-side traversal.
    """
    normalized = os.path.normpath(path)
    if path != normalized or ".." in path:
        raise ValueError(f"Path must not contain directory traversal: {path}")


def validate_name(name: str) -> None:
    """Validate that a name is a single file/folder name, not a path."""
    if not name:
        raise ValueError("Name must not be empty")
    if name in (".", ".."):
        raise ValueError(f"Name must not be current or parent directory: {name}")
    if "/" in name or "\\" in name:
        raise ValueError(f"Name must not contain path separators: {name}")
