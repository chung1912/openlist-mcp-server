"""Behavior tests for task MCP tools."""

import pytest


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
