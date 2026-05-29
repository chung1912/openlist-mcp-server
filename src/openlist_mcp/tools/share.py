"""Share management tools for OpenList MCP Server."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..client import get_client
from . import validate_path


def register_share_tools(mcp: FastMCP) -> None:
    """Register share management MCP tools."""

    @mcp.tool()
    async def create_share(path: str, password: str = "", days: int = 0) -> str:
        """Create a share link for a file or folder."""
        import json

        validate_path(path)
        client = await get_client()
        data = await client.request(
            "POST",
            "share/create",
            json={"path": path, "password": password, "days": days},
        )
        return json.dumps(data, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def list_shares(page: int = 1, per_page: int = 50) -> str:
        """List all existing share links."""
        import json

        client = await get_client()
        data = await client.request(
            "GET",
            "share/list",
            params={"page": page, "per_page": per_page},
        )
        return json.dumps(data, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def cancel_share(share_key: str, confirm: bool = False) -> str:
        """Cancel (disable) an existing share link.

        Args:
            share_key: The unique key of the share to cancel.
            confirm: Must be true to actually cancel the share. Defaults to false.
        """
        if not confirm:
            return "Share cancellation not performed. Re-run with confirm=true to cancel it."
        client = await get_client()
        await client.request("POST", "share/cancel", json={"share_key": share_key})
        return f"Share cancelled successfully: {share_key}"

    @mcp.tool()
    async def delete_share(share_key: str, confirm: bool = False) -> str:
        """Delete a share link permanently.

        Args:
            share_key: The unique key of the share to delete.
            confirm: Must be true to actually delete the share. Defaults to false.
        """
        if not confirm:
            return "Share deletion not performed. Re-run with confirm=true to delete it."
        client = await get_client()
        await client.request("POST", "share/delete", json={"share_key": share_key})
        return f"Share deleted successfully: {share_key}"
