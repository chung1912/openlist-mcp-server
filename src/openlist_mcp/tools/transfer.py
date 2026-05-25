"""File transfer tools for OpenList MCP Server."""

from __future__ import annotations

import base64
import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from ..client import get_client


def register_transfer_tools(mcp: FastMCP) -> None:
    """Register file upload/download MCP tools."""

    @mcp.tool()
    async def get_download_url(
        path: str,
        password: str = "",
    ) -> str:
        """Get the download URL for a file on OpenList.

        This returns the direct download link (or proxy link) for a file.
        The URL may include a time-limited signature for security.

        Args:
            path: Full path to the file.
            password: Password if the path is password-protected. Defaults to "".

        Returns:
            The download URL for the file, or file info with raw_url.
        """
        client = await get_client()
        data = await client.request(
            "POST",
            "fs/get",
            json={"path": path, "password": password},
        )
        raw_url = data.get("raw_url", "")
        if raw_url:
            return f"Download URL: {raw_url}"
        return json.dumps(data, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def upload_file(
        path: str,
        file_name: str,
        file_content_base64: str,
        as_task: bool = True,
    ) -> str:
        """Upload a file to OpenList from base64-encoded content.

        Args:
            path: Target directory path on OpenList (e.g. "/documents").
            file_name: Name for the uploaded file (e.g. "report.pdf").
            file_content_base64: Base64-encoded file content.
            as_task: Process as async task for large files. Defaults to True.

        Returns:
            Success message or task ID for async uploads.
        """
        client = await get_client()
        try:
            file_bytes = base64.b64decode(file_content_base64)
        except Exception as e:
            return f"Failed to decode base64 content: {e}"

        data = await client.upload(
            path=path,
            file_content=file_bytes,
            file_name=file_name,
            as_task=as_task,
        )
        if data is not None and data != {}:
            return f"Upload task created: {json.dumps(data, ensure_ascii=False)}"
        return f"File uploaded successfully: {path}/{file_name}"

    @mcp.tool()
    async def upload_local_file(
        local_path: str,
        remote_dir: str,
        remote_name: str = "",
        as_task: bool = True,
    ) -> str:
        """Upload a local file that the MCP server process can access.

        Use this when the agent and MCP server run on the same machine, or when the
        MCP server can read the provided file path. For generic MCP clients that
        cannot expose local files to the server, use upload_file with base64 content.

        Args:
            local_path: Local filesystem path readable by the MCP server process.
            remote_dir: Target directory path on OpenList (e.g. "/documents").
            remote_name: Optional remote filename. Defaults to the local filename.
            as_task: Process as async task for large files. Defaults to True.

        Returns:
            Success message or task ID for async uploads.
        """
        file_path = Path(local_path).expanduser()
        if not file_path.is_file():
            return f"Local file not found or not a regular file: {local_path}"

        final_name = remote_name.strip() or file_path.name
        if not final_name or "/" in final_name or "\\" in final_name:
            return "remote_name must be a filename only, not a path"

        client = await get_client()
        data = await client.upload(
            path=remote_dir,
            file_content=file_path.read_bytes(),
            file_name=final_name,
            as_task=as_task,
        )
        if data is not None and data != {}:
            return f"Upload task created: {json.dumps(data, ensure_ascii=False)}"
        return f"File uploaded successfully: {remote_dir}/{final_name}"
