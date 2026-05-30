"""Authentication tools for OpenList MCP Server."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..client import OpenList2FAError, OpenListError, _generate_totp, get_client
from ..config import get_config


def register_auth_tools(mcp: FastMCP) -> None:
    """Register authentication-related MCP tools."""

    @mcp.tool()
    async def login(otp_code: str = "") -> str:
        """Login to OpenList server using configured credentials.

        If OPENLIST_TOTP_SECRET is configured, the TOTP code will be generated
        automatically and you do not need to provide otp_code.

        If the OpenList account has two-factor authentication (2FA) enabled
        and no OPENLIST_TOTP_SECRET is set, you must provide the TOTP code
        from your authenticator app.

        Args:
            otp_code: TOTP code for 2FA. Leave empty if OPENLIST_TOTP_SECRET
                      is configured or 2FA is not enabled.

        Returns:
            A success message with user info if login is successful.
        """
        config = get_config()
        client = await get_client()
        resolved_otp = otp_code.strip() or None
        if resolved_otp is None and config.has_totp_secret:
            resolved_otp = _generate_totp(config.totp_secret)
        try:
            await client.login(otp_code=resolved_otp)
            return "Login successful. Token acquired."
        except OpenList2FAError:
            if config.has_totp_secret:
                return (
                    "Auto-generated TOTP code was rejected. "
                    "Please check your OPENLIST_TOTP_SECRET value."
                )
            return (
                "2FA is enabled on this OpenList account. "
                "Please re-run login with your TOTP code:\n\n"
                'login(otp_code="123456")'
            )
        except OpenListError as exc:
            return f"Login failed: {exc.message}"


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
