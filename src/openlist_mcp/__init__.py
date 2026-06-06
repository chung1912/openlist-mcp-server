"""OpenList MCP Server - enables AI agents to manage files via OpenList API."""

import re
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def _get_version() -> str:
    """Get version from installed package metadata or pyproject.toml."""
    try:
        return version("openlist-mcp-server")
    except PackageNotFoundError:
        pass
    # Development fallback: read version from pyproject.toml (no static string)
    here = Path(__file__).resolve().parent.parent.parent
    pyproject = here / "pyproject.toml"
    if pyproject.exists():
        match = re.search(
            r'^version\s*=\s*"([^"]+)"',
            pyproject.read_text(encoding="utf-8"),
            re.M,
        )
        if match:
            return match.group(1)
    return "0.0.0"


__version__ = _get_version()
