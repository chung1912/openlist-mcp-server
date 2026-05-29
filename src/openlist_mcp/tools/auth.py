"""Authentication tools for OpenList MCP Server."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..client import OpenList2FAError, get_client


def register_auth_tools(mcp: FastMCP) -> None:
    """Register authentication-related MCP tools."""

    @mcp.tool()
    async def login(otp_code: str = "") -> str:
        """Login to OpenList server using configured credentials.

        If the OpenList account has two-factor authentication (2FA) enabled,
        you must provide the TOTP code from your authenticator app.

        Args:
            otp_code: TOTP code for 2FA. Leave empty if 2FA is not enabled.

        Returns:
            A success message with user info if login is successful.
        """
        client = await get_client()
        try:
            await client.login(otp_code=otp_code.strip() or None)
            return "Login successful. Token acquired."
        except OpenList2FAError:
            return (
                "2FA is enabled on this OpenList account. "
                "Please re-run login with your TOTP code:\n\n"
                'login(otp_code="123456")'
            )


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
