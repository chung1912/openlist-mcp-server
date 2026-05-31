"""Behavior tests for read-only admin MCP tools."""

import pytest


@pytest.mark.asyncio
async def test_list_storages_sends_get_request(admin_tools) -> None:
    tools, client = admin_tools

    result = await tools["list_storages"]()

    assert client.requests == [("GET", "admin/storage/list", {})]


@pytest.mark.asyncio
async def test_get_storage_info_passes_id_param(admin_tools) -> None:
    tools, client = admin_tools

    result = await tools["get_storage_info"](storage_id=2)

    assert client.requests == [
        ("GET", "admin/storage/get", {"params": {"id": 2}})
    ]


@pytest.mark.asyncio
async def test_get_settings_sends_get_request(admin_tools) -> None:
    tools, client = admin_tools

    result = await tools["get_settings"]()

    assert client.requests == [("GET", "admin/setting/list", {})]


@pytest.mark.asyncio
async def test_get_setting_passes_key_param(admin_tools) -> None:
    tools, client = admin_tools

    result = await tools["get_setting"](key="site_title")

    assert client.requests == [
        ("GET", "admin/setting/get", {"params": {"key": "site_title"}})
    ]
