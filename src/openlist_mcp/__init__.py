"""OpenList MCP Server - enables AI agents to manage files via OpenList API."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("openlist-mcp-server")
except PackageNotFoundError:
    __version__ = "0.2.8"
