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

from . import __version__  # noqa: F401 — used in except ValueError branch
from .config import get_config
from .tools.admin import register_admin_tools
from .tools.advanced import register_advanced_tools
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
    register_admin_tools(mcp)
    register_fs_tools(mcp)
    register_transfer_tools(mcp)
    register_task_tools(mcp)
    register_share_tools(mcp)
    register_advanced_tools(mcp)
    logger.info("All tools registered successfully")


def main() -> None:
    """Main entry point for the OpenList MCP Server."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    try:
        config = get_config()
    except ValueError:
        print(
            "\n"
            "╔══════════════════════════════════════════════════════════════╗\n"
            "║              OpenList MCP Server v{__version__:<24}║\n"
            "╠══════════════════════════════════════════════════════════════╣\n"
            "║                                                              ║\n"
            "║  What is this?                                               ║\n"
            "║  An MCP server that lets AI agents (Claude, SOLO, etc.)      ║\n"
            "║  manage files on your OpenList instance.                     ║\n"
            "║                                                              ║\n"
            "║  67 tools available:                                         ║\n"
            "║  • Browse:   list_files, list_dirs, get_file_info,           ║\n"
            "║              search_files                                    ║\n"
            "║  • Manage:   create_folder, rename, batch_rename,              ║\n"
            "║              regex_rename, copy, move, remove,                  ║\n"
            "║              remove_empty_dirs, recursive_move               ║\n"
            "║  • Transfer: upload_file, upload_local_file, get_download_url║\n"
            "║  • Auth:     login (supports 2FA/TOTP), get_public_settings, ║\n"
            "║              get_me, logout                                   ║\n"
            "║  • Tasks:    list_tasks, get_task_info, retry_task,         ║\n"
            "║              cancel_task, delete_task, batch_cancel_tasks,   ║\n"
            "║              batch_delete_tasks, batch_retry_tasks,          ║\n"
            "║              clear_done_tasks, clear_succeeded_tasks,        ║\n"
            "║              retry_failed_tasks                              ║\n"
            "║  • Shares:   create_share, list_shares, update_share,         ║\n"
            "║              enable_share, disable_share, cancel_share,      ║\n"
            "║              delete_share                                    ║\n"
            "║  • Smart:    tree, disk_usage, find_duplicates,              ║\n"
            "║              content_preview, batch_download                 ║\n"
            "║  • System:   list_storages, get_storage_info, list_drivers,  ║\n"
            "║              get_driver_info, get_settings, get_setting,      ║\n"
            "║              get_index_progress, list_my_ssh_keys,           ║\n"
            "║              add_ssh_key, delete_ssh_key, update_current_user║\n"
            "║  • Advanced: offline_download, decompress_archive,            ║\n"
            "║              list_archive_files, list_download_tools,         ║\n"
            "║              parse_torrent, generate_torrent,                 ║\n"
            "║              torrent_rapid_upload                             ║\n"
            "║                                                              ║\n"
            "║  Quick start:                                                ║\n"
            "║  Set these environment variables and restart:                ║\n"
            "║                                                              ║\n"
            "║    export OPENLIST_URL=https://your-openlist.com             ║\n"
            "║    export OPENLIST_USERNAME=your_username                     ║\n"
            "║    export OPENLIST_PASSWORD=your_password                    ║\n"
            "║                                                              ║\n"
            '║  Then try: "List files on my OpenList server."               ║\n'
            "║                                                              ║\n"
            "║  For more: https://github.com/hbestm/openlist-mcp-server     ║\n"
            "║                                                              ║\n"
            "╚══════════════════════════════════════════════════════════════╝\n",
            file=sys.stderr,
        )
        sys.exit(1)

    logger.info("OpenList MCP Server starting")
    logger.info("Target: %s", config.base_url)
    if config.is_authenticated:
        logger.info("Authentication: configured")
    else:
        logger.warning(
            "Authentication: not configured. "
            "Set OPENLIST_USERNAME and OPENLIST_PASSWORD for full access."
        )

    register_all_tools()
    mcp.run()


if __name__ == "__main__":
    main()
