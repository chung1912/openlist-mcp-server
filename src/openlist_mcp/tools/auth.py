"""Authentication tools for OpenList MCP Server."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..client import get_client


def register_auth_tools(mcp: FastMCP) -> None:
    """Register authentication-related MCP tools."""

    @mcp.tool()
    async def login() -> str:
        """Login to OpenList server using configured credentials.

        This authenticates with the OpenList server using the username and password
        from environment variables. You must call this before any other operations,
        or the system will auto-login on first use.

        Returns:
            A success message with user info if login is successful.
        """
        client = await get_client()
        data = await client.login()
        return f"Login successful. Token acquired."


def register_public_tools(mcp: FastMCP) -> None:
    """Register public (no-auth) MCP tools."""

    @mcp.tool()
    async def get_public_settings() -> str:
        """Get public settings of the OpenList server.

        Returns information about what authentication methods are available,
        share settings, and other public configuration.

        Returns:
            JSON string of public settings.
        """
        import json

        client = await get_client()
        data = await client.request("GET", "public/settings", require_auth=False)
        return json.dumps(data, indent=2, ensure_ascii=False)
