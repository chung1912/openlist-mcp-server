"""Behavior tests for registered MCP tools."""

from __future__ import annotations

import pytest

from openlist_mcp.tools.fs import register_fs_tools
from openlist_mcp.tools.transfer import register_transfer_tools


class ToolRecorder:
    """Minimal FastMCP-like recorder for registered tool functions."""

    def __init__(self) -> None:
        self.tools = {}

    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func

        return decorator


class FakeClient:
    def __init__(self) -> None:
        self.requests = []
        self.uploads = []

    async def request(self, method: str, path: str, **kwargs):
        self.requests.append((method, path, kwargs))
        return {}

    async def upload(self, **kwargs):
        self.uploads.append(kwargs)
        return {}


@pytest.fixture
def fs_tools(monkeypatch):
    recorder = ToolRecorder()
    client = FakeClient()

    async def fake_get_client():
        return client

    monkeypatch.setattr("openlist_mcp.tools.fs.get_client", fake_get_client)
    register_fs_tools(recorder)
    return recorder.tools, client


@pytest.fixture
def transfer_tools(monkeypatch):
    recorder = ToolRecorder()
    client = FakeClient()

    async def fake_get_client():
        return client

    monkeypatch.setattr("openlist_mcp.tools.transfer.get_client", fake_get_client)
    register_transfer_tools(recorder)
    return recorder.tools, client


@pytest.mark.asyncio
async def test_create_folder_uses_mkdir_without_name_validation(fs_tools) -> None:
    tools, client = fs_tools

    result = await tools["create_folder"]("/projects/new")

    assert result == "Folder created successfully: /projects/new"
    assert client.requests == [("POST", "fs/mkdir", {"json": {"path": "/projects/new"}})]


@pytest.mark.asyncio
async def test_rename_validates_new_name(fs_tools) -> None:
    tools, client = fs_tools

    with pytest.raises(ValueError, match="path separators"):
        await tools["rename"]("/projects/old", "../bad")

    assert client.requests == []


@pytest.mark.asyncio
async def test_rename_sends_expected_payload(fs_tools) -> None:
    tools, client = fs_tools

    result = await tools["rename"]("/projects/old", "new")

    assert result == "Renamed successfully: /projects/old -> new"
    assert client.requests == [
        ("POST", "fs/rename", {"json": {"path": "/projects/old", "name": "new"}})
    ]


@pytest.mark.asyncio
async def test_copy_validates_each_name(fs_tools) -> None:
    tools, client = fs_tools

    with pytest.raises(ValueError, match="path separators"):
        await tools["copy"]("/src", "/dst", ["good.txt", "bad/name.txt"])

    assert client.requests == []


@pytest.mark.asyncio
async def test_upload_file_validates_file_name(transfer_tools) -> None:
    tools, client = transfer_tools

    with pytest.raises(ValueError, match="path separators"):
        await tools["upload_file"]("/docs", "bad/name.txt", "aGVsbG8=")

    assert client.uploads == []


@pytest.mark.asyncio
async def test_upload_file_sends_decoded_content(transfer_tools) -> None:
    tools, client = transfer_tools

    result = await tools["upload_file"]("/docs", "note.txt", "aGVsbG8=", as_task=False)

    assert result == "File uploaded successfully: /docs/note.txt"
    assert client.uploads == [
        {
            "path": "/docs",
            "file_content": b"hello",
            "file_name": "note.txt",
            "as_task": False,
        }
    ]
