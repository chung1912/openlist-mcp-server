"""Advanced file operation tools for OpenList MCP Server.

Includes offline download, archive decompression, and related utilities.
"""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from ..client import get_client
from . import validate_path


def register_advanced_tools(mcp: FastMCP) -> None:
    """Register advanced file operation MCP tools."""

    @mcp.tool()
    async def offline_download(
        url: str,
        path: str = "/",
        tool: str = "aria2",
        delete_policy: str = "",
    ) -> str:
        """Download a file from a remote URL directly to the OpenList server.

        The server fetches the file in the background. Use list_tasks to monitor progress.

        Available download tools on the server can be queried via the
        `/api/public/offline_download_tools` endpoint.

        Args:
            url: Remote URL to download from.
            path: Destination directory on OpenList (e.g. "/downloads"). Defaults to root.
            tool: Download tool name. Defaults to "aria2" (supports https/http/magnet).
                  Alternatives: "SimpleHttp" (http only), or others as listed by
                  the server's public settings.
            delete_policy: Optional delete policy for completed tasks.

        Returns:
            JSON string with created task info.
        """
        validate_path(path)

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
        validate_path(src_dir)
        name_list = [n.strip() for n in names.split(",") if n.strip()]
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
            validate_path(dst_dir)
            body["dst_dir"] = dst_dir
        if archive_pass:
            body["archive_pass"] = archive_pass

        data = await client.request("POST", "fs/archive/decompress", json=body)
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
