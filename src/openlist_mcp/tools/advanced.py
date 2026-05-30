"""Advanced file operation tools for OpenList MCP Server.

Includes offline download, archive decompression, and related utilities.
"""

from __future__ import annotations

import json
import os
import posixpath
from typing import Any

from mcp.server.fastmcp import FastMCP

from ..client import get_client
from ..config import get_config
from . import enforce_path_allowed, enforce_writable, normalize_names, validate_name, validate_path


def register_advanced_tools(mcp: FastMCP) -> None:
    """Register advanced file operation MCP tools."""

    @mcp.tool()
    async def get_capabilities() -> str:
        """Summarize this MCP server's OpenList capabilities and safety settings.

        Returns public server settings, the authenticated user profile when available,
        configured offline download tools, and local MCP safety configuration.
        Use this before high-impact operations to understand what the server supports.
        """
        config = get_config()
        client = await get_client()
        public_settings = await client.request(
            "GET",
            "public/settings",
            require_auth=False,
        )
        user = await client.request("GET", "me")
        download_tools_data = await client.request(
            "GET",
            "public/offline_download_tools",
            require_auth=False,
        )
        download_tools = (
            download_tools_data
            if isinstance(download_tools_data, list)
            else download_tools_data.get(
                "value",
                download_tools_data.get("data", []),
            )
        )

        capabilities = {
            "server": {
                "base_url": config.base_url,
                "uses_https": config.base_url.startswith("https://"),
                "public_settings": public_settings,
            },
            "authentication": {
                "credentials_configured": config.is_authenticated,
                "totp_secret_configured": config.has_totp_secret,
                "user": user,
            },
            "features": {
                "file_browse": True,
                "file_manage": True,
                "file_transfer": True,
                "shares": True,
                "tasks": True,
                "offline_download_tools": download_tools,
                "archive_decompress": True,
            },
            "mcp_safety": {
                "high_impact_operations_require_confirm": True,
                "read_only": config.read_only,
                "allowed_paths": config.allowed_paths,
                "local_upload_roots_configured": bool(
                    os.environ.get("OPENLIST_LOCAL_UPLOAD_ROOTS", "")
                ),
            },
        }
        return json.dumps(capabilities, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def offline_download(
        url: str,
        path: str = "/",
        tool: str = "aria2",
        delete_policy: str = "",
    ) -> str:
        """Download a file from a remote URL directly to the OpenList server.

        The server fetches the file in the background. Use get_task_info with the
        returned task ID to monitor progress.

        Available download tools on the server can be queried via `list_download_tools`.
        Common options include: "aria2" (supports http/https/magnet/torrent),
        "qbittorrent" (BitTorrent/HTTP), "transmission" (BitTorrent/HTTP).

        Args:
            url: Remote URL to download from.
            path: Destination directory on OpenList (e.g. "/downloads"). Defaults to root.
            tool: Download tool name. Defaults to "aria2". Use `list_download_tools`
                  to see what's available on this server.
            delete_policy: Optional delete policy for completed tasks.

        Returns:
            JSON string with created task info.
        """
        enforce_path_allowed(path)
        enforce_writable("offline_download")

        client = await get_client()
        body: dict[str, Any] = {"urls": [url], "path": path}
        if tool:
            body["tool"] = tool
        if delete_policy:
            body["delete_policy"] = delete_policy

        data = await client.request("POST", "fs/add_offline_download", json=body)
        return json.dumps(data, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def decompress_archive(
        src_dir: str,
        names: str,
        dst_dir: str = "",
        archive_pass: str = "",
        overwrite: bool = False,
        put_into_new_dir: bool = False,
    ) -> str:
        """Decompress an archive file (zip, rar, 7z, tar.gz, etc.) on the OpenList server.

        The archive file must already exist on the server.

        Args:
            src_dir: Directory containing the archive file(s) (e.g. "/downloads").
            names: Comma-separated archive filenames to decompress (e.g. "data.zip").
            dst_dir: Optional extraction target directory. Defaults to same as src_dir.
            archive_pass: Optional password for encrypted archives.
            overwrite: Whether to overwrite existing files. Defaults to false.
            put_into_new_dir: Whether to place extracted files in a new directory named after the archive. Defaults to false.

        Returns:
            JSON string with decompression result.
        """
        enforce_path_allowed(src_dir)
        enforce_writable("decompress_archive")
        name_list = normalize_names(names)
        if not name_list:
            return json.dumps(
                {"ok": False, "error": "No archive files specified."},
                ensure_ascii=False,
            )

        client = await get_client()
        body: dict[str, Any] = {
            "src_dir": src_dir,
            "name": name_list,
            "overwrite": overwrite,
            "put_into_new_dir": put_into_new_dir,
        }
        if dst_dir:
            enforce_path_allowed(dst_dir)
            body["dst_dir"] = dst_dir
        if archive_pass:
            body["archive_pass"] = archive_pass

        data = await client.request("POST", "fs/archive/decompress", json=body)
        return json.dumps(data, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def list_archive_files(
        src_dir: str,
        name: str,
        inner_path: str = "/",
        archive_pass: str = "",
        refresh: bool = False,
    ) -> str:
        """List files inside an archive without extracting it.

        Args:
            src_dir: Directory containing the archive file.
            name: Archive filename, not a full path.
            inner_path: Inner archive directory to list. Defaults to "/".
            archive_pass: Optional password for encrypted archives.
            refresh: Whether to refresh archive cache when supported by OpenList.

        Returns:
            JSON string containing archive entries.
        """
        enforce_path_allowed(src_dir)
        validate_name(name)
        validate_path(inner_path)
        archive_path = posixpath.join(src_dir.rstrip("/"), name)
        if src_dir == "/":
            archive_path = f"/{name}"
        client = await get_client()
        body: dict[str, Any] = {
            "path": archive_path,
            "inner_path": inner_path,
            "refresh": refresh,
        }
        if archive_pass:
            body["archive_pass"] = archive_pass

        data = await client.request("POST", "fs/archive/list", json=body)
        return json.dumps(data, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def get_me() -> str:
        """Get the current authenticated user's profile information.

        Returns user details including username, role, permissions, and 2FA status.
        """
        client = await get_client()
        data = await client.request("GET", "me")
        return json.dumps(data, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def logout() -> str:
        """Logout from the OpenList server and invalidate the current token.

        After logout, the next API call will trigger automatic re-login
        using configured credentials.
        """
        client = await get_client()
        await client.request("GET", "auth/logout")
        # Clear the cached token
        import openlist_mcp.client as cm

        if cm._client:
            cm._client._token = None
        return "Logged out successfully. Token invalidated."

    @mcp.tool()
    async def list_download_tools() -> str:
        """List available offline download tools configured on this OpenList server.

        The result depends on which download tools (aria2, Transmission, qBittorrent, etc.)
        are installed and configured on the OpenList server. Only tools that are
        properly set up will appear in the list.

        Returns:
            JSON array of available download tool names.
        """
        import json

        client = await get_client()
        data = await client.request("GET", "public/offline_download_tools", require_auth=False)
        tools = data if isinstance(data, list) else data.get("value", data.get("data", []))
        return json.dumps(tools, ensure_ascii=False)
