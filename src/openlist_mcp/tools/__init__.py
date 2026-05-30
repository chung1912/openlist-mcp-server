"""OpenList MCP Tools package."""

import os


def validate_path(path: str) -> None:
    """Validate that a path does not contain directory traversal sequences.

    Rejects paths with '..' as a path component to prevent directory traversal.
    Unlike a simple substring match, this only rejects '..' when it appears
    as a standalone component between separators, allowing legitimate names
    like 'backup..2024.tar.gz' or '/foo.v2/bar'.
    """
    if not path:
        raise ValueError("Path must not be empty")

    # Check each path component — reject only exact '..', not filenames containing '..'
    parts = path.replace("\\", "/").split("/")
    if ".." in parts:
        raise ValueError(f"Path must not contain directory traversal: {path}")

    # Also catch ./ components via normpath
    normalized = os.path.normpath(path)
    if path != normalized:
        raise ValueError(f"Path must not contain directory traversal: {path}")


def validate_name(name: str) -> None:
    """Validate that a name is a single file/folder name, not a path."""
    if not name:
        raise ValueError("Name must not be empty")
    if name in (".", ".."):
        raise ValueError(f"Name must not be current or parent directory: {name}")
    if "/" in name or "\\" in name:
        raise ValueError(f"Name must not contain path separators: {name}")
