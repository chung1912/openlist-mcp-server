"""Behavior tests for registered MCP tools."""

from __future__ import annotations

import pytest

from openlist_mcp.tools.advanced import register_advanced_tools
from openlist_mcp.tools.fs import register_fs_tools
from openlist_mcp.tools.task import register_task_tools
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
        if path == "public/settings":
            return {"title": "OpenList Test"}
        if path == "me":
            return {"username": "admin", "role": 2}
        if path == "public/offline_download_tools":
            return ["aria2"]
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

    monkeypatch.setenv("OPENLIST_URL", "https://openlist.example")
    monkeypatch.delenv("OPENLIST_READONLY", raising=False)
    monkeypatch.delenv("OPENLIST_ALLOWED_PATHS", raising=False)
    monkeypatch.setattr("openlist_mcp.config._config", None)
    monkeypatch.setattr("openlist_mcp.tools.fs.get_client", fake_get_client)
    register_fs_tools(recorder)
    return recorder.tools, client


@pytest.fixture
def transfer_tools(monkeypatch):
    recorder = ToolRecorder()
    client = FakeClient()

    async def fake_get_client():
        return client

    monkeypatch.setenv("OPENLIST_URL", "https://openlist.example")
    monkeypatch.delenv("OPENLIST_READONLY", raising=False)
    monkeypatch.delenv("OPENLIST_ALLOWED_PATHS", raising=False)
    monkeypatch.setattr("openlist_mcp.config._config", None)
    monkeypatch.setattr("openlist_mcp.tools.transfer.get_client", fake_get_client)
    register_transfer_tools(recorder)
    return recorder.tools, client


@pytest.fixture
def task_tools(monkeypatch):
    recorder = ToolRecorder()
    client = FakeClient()

    async def fake_get_client():
        return client

    monkeypatch.setenv("OPENLIST_URL", "https://openlist.example")
    monkeypatch.delenv("OPENLIST_READONLY", raising=False)
    monkeypatch.setattr("openlist_mcp.config._config", None)
    monkeypatch.setattr("openlist_mcp.tools.task.get_client", fake_get_client)
    register_task_tools(recorder)
    return recorder.tools, client


@pytest.fixture
def advanced_tools(monkeypatch):
    recorder = ToolRecorder()
    client = FakeClient()

    async def fake_get_client():
        return client

    monkeypatch.setenv("OPENLIST_URL", "https://openlist.example")
    monkeypatch.setenv("OPENLIST_USERNAME", "admin")
    monkeypatch.setenv("OPENLIST_PASSWORD", "secret")
    monkeypatch.delenv("OPENLIST_READONLY", raising=False)
    monkeypatch.delenv("OPENLIST_ALLOWED_PATHS", raising=False)
    monkeypatch.delenv("OPENLIST_LOCAL_UPLOAD_ROOTS", raising=False)
    monkeypatch.setattr("openlist_mcp.config._config", None)
    monkeypatch.setattr("openlist_mcp.tools.advanced.get_client", fake_get_client)
    register_advanced_tools(recorder)
    return recorder.tools, client


@pytest.mark.asyncio
async def test_list_tasks_uses_typed_task_endpoint(task_tools) -> None:
    tools, client = task_tools

    result = await tools["list_tasks"](
        task_type="offline_download",
        status="done",
        page=2,
        per_page=25,
    )

    assert result == "{}"
    assert client.requests == [
        (
            "POST",
            "task/offline_download/done",
            {"params": {"page": 2, "per_page": 25}},
        )
    ]


@pytest.mark.asyncio
async def test_get_task_info_uses_tid_query_param(task_tools) -> None:
    tools, client = task_tools

    result = await tools["get_task_info"]("task-123", task_type="offline_download")

    assert result == "{}"
    assert client.requests == [
        (
            "POST",
            "task/offline_download/info",
            {"params": {"tid": "task-123"}},
        )
    ]


@pytest.mark.asyncio
async def test_task_tools_validate_task_type(task_tools) -> None:
    tools, client = task_tools

    with pytest.raises(ValueError, match="Unsupported task_type"):
        await tools["get_task_info"]("task-123", task_type="bad")

    assert client.requests == []


@pytest.mark.asyncio
async def test_cancel_task_uses_typed_endpoint(task_tools) -> None:
    tools, client = task_tools

    result = await tools["cancel_task"](
        "task-123",
        task_type="offline_download",
        confirm=True,
    )

    assert result == "Task cancelled: task-123"
    assert client.requests == [
        (
            "POST",
            "task/offline_download/cancel",
            {"params": {"tid": "task-123"}},
        )
    ]


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


@pytest.mark.asyncio
async def test_create_folder_uses_mkdir_without_name_validation(fs_tools) -> None:
    tools, client = fs_tools

    result = await tools["create_folder"]("/projects/new")

    assert result == "Folder created successfully: /projects/new"
    assert client.requests == [("POST", "fs/mkdir", {"json": {"path": "/projects/new"}})]


@pytest.mark.asyncio
async def test_read_only_blocks_write_tools(fs_tools, monkeypatch) -> None:
    tools, client = fs_tools
    monkeypatch.setenv("OPENLIST_READONLY", "true")
    monkeypatch.setattr("openlist_mcp.config._config", None)

    with pytest.raises(PermissionError, match="OPENLIST_READONLY"):
        await tools["create_folder"]("/projects/new")

    assert client.requests == []


@pytest.mark.asyncio
async def test_allowed_paths_blocks_out_of_scope_reads(fs_tools, monkeypatch) -> None:
    tools, client = fs_tools
    monkeypatch.setenv("OPENLIST_ALLOWED_PATHS", "/safe,/team/docs")
    monkeypatch.setattr("openlist_mcp.config._config", None)

    with pytest.raises(PermissionError, match="outside OPENLIST_ALLOWED_PATHS"):
        await tools["list_files"]("/private")

    assert client.requests == []


@pytest.mark.asyncio
async def test_allowed_paths_allows_child_paths(fs_tools, monkeypatch) -> None:
    tools, client = fs_tools
    monkeypatch.setenv("OPENLIST_ALLOWED_PATHS", "/safe")
    monkeypatch.setattr("openlist_mcp.config._config", None)

    await tools["list_files"]("/safe/nested")

    assert client.requests == [
        (
            "POST",
            "fs/list",
            {
                "json": {
                    "path": "/safe/nested",
                    "page": 1,
                    "per_page": 50,
                    "password": "",
                }
            },
        )
    ]


@pytest.mark.asyncio
async def test_list_dirs_sends_expected_payload(fs_tools) -> None:
    tools, client = fs_tools

    result = await tools["list_dirs"]("/projects", password="secret", force_root=True)

    assert result == "{}"
    assert client.requests == [
        (
            "POST",
            "fs/dirs",
            {
                "json": {
                    "path": "/projects",
                    "password": "secret",
                    "force_root": True,
                }
            },
        )
    ]


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
async def test_batch_rename_validates_names(fs_tools) -> None:
    tools, client = fs_tools

    with pytest.raises(ValueError, match="path separators"):
        await tools["batch_rename"](
            "/projects",
            [{"src_name": "good.txt", "new_name": "bad/name.txt"}],
        )

    assert client.requests == []


@pytest.mark.asyncio
async def test_batch_rename_sends_expected_payload(fs_tools) -> None:
    tools, client = fs_tools

    result = await tools["batch_rename"](
        "/projects",
        [
            {"src_name": "old-a.txt", "new_name": "new-a.txt"},
            {"src_name": "old-b.txt", "new_name": "new-b.txt"},
        ],
    )

    assert result.startswith("Batch renamed successfully in /projects")
    assert client.requests == [
        (
            "POST",
            "fs/batch_rename",
            {
                "json": {
                    "src_dir": "/projects",
                    "rename_objects": [
                        {"src_name": "old-a.txt", "new_name": "new-a.txt"},
                        {"src_name": "old-b.txt", "new_name": "new-b.txt"},
                    ],
                }
            },
        )
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
