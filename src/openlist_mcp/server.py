"""OpenList MCP Server - main entry point.

This server exposes OpenList file management capabilities as MCP tools,
enabling AI agents to browse, upload, download, search, and manage files
on any OpenList instance.

Usage:
    openlist-mcp

Environment Variables:
    OPENLIST_URL      - Base URL of your OpenList instance (required)
    OPENLIST_USERNAME - Username for authentication (required)
    OPENLIST_PASSWORD - Password for authentication (required)
"""

from __future__ import annotations

import logging
import sys

from mcp.server.fastmcp import FastMCP

from .config import get_config
from .tools.auth import register_auth_tools, register_public_tools
from .tools.fs import register_fs_tools
from .tools.share import register_share_tools
from .tools.task import register_task_tools
from .tools.transfer import register_transfer_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("openlist-mcp")

# Create MCP server instance
mcp = FastMCP(
    name="openlist",
    instructions=(
        "OpenList MCP Server - Manage files on your OpenList instance. "
        "You can browse directories, search files, upload/download, "
        "create folders, rename/copy/move/delete files, manage shares, "
        "and monitor async tasks. "
        "Authentication is handled automatically on first use."
    ),
)


def register_all_tools() -> None:
    """Register all tool groups with the MCP server."""
    register_public_tools(mcp)
    register_auth_tools(mcp)
    register_fs_tools(mcp)
    register_transfer_tools(mcp)
    register_task_tools(mcp)
    register_share_tools(mcp)
    logger.info("All tools registered successfully")


def main() -> None:
    """Main entry point for the OpenList MCP Server."""
    # Validate configuration early
    try:
        config = get_config()
        logger.info("OpenList MCP Server starting")
        logger.info("Target: %s", config.base_url)
        if config.is_authenticated:
            logger.info("Authentication: configured")
        else:
            logger.warning(
                "Authentication: not configured. "
                "Set OPENLIST_USERNAME and OPENLIST_PASSWORD for full access."
            )
    except ValueError:
        logger.info(
            "OpenList MCP Server v0.2.5 installed successfully. "
            "Set OPENLIST_URL, OPENLIST_USERNAME, and OPENLIST_PASSWORD to get started."
        )
        sys.exit(0)

    # Register all tools
    register_all_tools()

    # Run the MCP server (stdio transport)
    mcp.run()


if __name__ == "__main__":
    main()
