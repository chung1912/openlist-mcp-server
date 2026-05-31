"""Read-only system administration tools for OpenList MCP Server.

Provides read-only access to storage, driver, setting, and index info.
All tools in this module are GET-only — no state modification.
"""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from ..client import get_client
from . import validate_pagination


def register_admin_tools(mcp: FastMCP) -> None:
    """Register read-only admin/system MCP tools."""

    @mcp.tool()
    async def list_storages() -> str:
        """List all configured storage backends on the OpenList server.

        Returns details about each storage including mount path, driver type,
        status, total space, and free space. Read-only — no modification.

        Returns:
            JSON string with storage list.
        """
        client = await get_client()
        data = await client.request("GET", "admin/storage/list")
        return json.dumps(data, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def get_storage_info(storage_id: int) -> str:
        """Get detailed information about a specific storage backend.

        Args:
            storage_id: The numeric ID of the storage to query. Use list_storages
                       to see available IDs.

        Returns:
            JSON string with storage details.
        """
        client = await get_client()
        data = await client.request(
            "GET", "admin/storage/get", params={"id": storage_id}
        )
        return json.dumps(data, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def list_drivers() -> str:
        """List all registered storage driver names on the server.

        Shows what storage backend types are available (Local, S3, OneDrive,
        **************, etc.).

        Returns:
            JSON list of driver names.
        """
        client = await get_client()
        data = await client.request("GET", "admin/driver/names")
        return json.dumps(data, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def get_driver_info(driver: str) -> str:
        """Get detailed information about a specific storage driver.

        Shows the driver's configuration fields and their types.

        Args:
            driver: Driver name (e.g. "Local", "S3", "189PC"). Use list_drivers
                   to see available names.

        Returns:
            JSON string with driver info.
        """
        client = await get_client()
        data = await client.request(
            "GET", "admin/driver/info", params={"driver": driver}
        )
        return json.dumps(data, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def get_settings() -> str:
        """List all global settings on the OpenList server.

        Returns all configuration key-value pairs including site title,
        pagination settings, preview options, etc. Read-only.

        Returns:
            JSON string with all settings.
        """
        client = await get_client()
        data = await client.request("GET", "admin/setting/list")
        return json.dumps(data, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def get_setting(key: str) -> str:
        """Get a single global setting by its key.

        Args:
            key: The setting key (e.g. "site_title", "pagination_type",
                "logo", "favicon"). Use get_settings to see all keys.

        Returns:
            JSON string with the setting value.
        """
        client = await get_client()
        data = await client.request(
            "GET", "admin/setting/get", params={"key": key}
        )
        return json.dumps(data, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def get_index_progress() -> str:
        """Get the current search index building progress.

        Useful for determining whether search results are up to date.

        Returns:
            JSON string with index progress info.
        """
        client = await get_client()
        data = await client.request("GET", "admin/index/progress")
        return json.dumps(data, indent=2, ensure_ascii=False)
