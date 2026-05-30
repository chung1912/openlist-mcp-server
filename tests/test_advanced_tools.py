"""Behavior tests for advanced MCP tools."""

import pytest


@pytest.mark.asyncio
async def test_get_capabilities_summarizes_server_user_and_tools(advanced_tools) -> None:
    tools, client = advanced_tools

    result = await tools["get_capabilities"]()

    assert '"base_url": "https://openlist.example"' in result
    assert '"uses_https": true' in result
    assert '"username": "admin"' in result
    assert '"offline_download_tools": [\n      "aria2"\n    ]' in result
    assert client.requests == [
        ("GET", "public/settings", {"require_auth": False}),
        ("GET", "me", {}),
        ("GET", "public/offline_download_tools", {"require_auth": False}),
    ]


@pytest.mark.asyncio
async def test_list_archive_files_validates_archive_name(advanced_tools) -> None:
    tools, client = advanced_tools

    with pytest.raises(ValueError, match="path separators"):
        await tools["list_archive_files"]("/archives", "bad/name.zip")

    assert client.requests == []


@pytest.mark.asyncio
async def test_list_archive_files_sends_expected_payload(advanced_tools) -> None:
    tools, client = advanced_tools

    result = await tools["list_archive_files"](
        "/archives",
        "bundle.zip",
        inner_path="/docs",
        archive_pass="secret",
        refresh=True,
    )

    assert result == "{}"
    assert client.requests == [
        (
            "POST",
            "fs/archive/list",
            {
                "json": {
                    "path": "/archives/bundle.zip",
                    "inner_path": "/docs",
                    "refresh": True,
                    "archive_pass": "secret",
                }
            },
        )
    ]
