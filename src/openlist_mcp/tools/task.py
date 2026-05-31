"""Task management tools for OpenList MCP Server."""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from ..client import get_client
from . import enforce_writable, validate_pagination

TASK_TYPES = {
    "upload",
    "copy",
    "offline_download",
    "offline_download_transfer",
    "decompress",
    "decompress_upload",
}

TASK_LIST_STATUSES = {"done", "undone"}


def _validate_task_type(task_type: str) -> str:
    task_type = task_type.strip()
    if task_type not in TASK_TYPES:
        raise ValueError(
            f"Unsupported task_type: {task_type}. Supported values: {', '.join(sorted(TASK_TYPES))}"
        )
    return task_type


def _task_params(task_id: str) -> dict[str, str]:
    task_id = task_id.strip()
    if not task_id:
        raise ValueError("task_id must not be empty")
    return {"tid": task_id}


def register_task_tools(mcp: FastMCP) -> None:
    """Register task management MCP tools."""

    @mcp.tool()
    async def list_tasks(
        task_type: str = "offline_download",
        status: str = "undone",
        page: int = 1,
        per_page: int = 50,
    ) -> str:
        """List asynchronous tasks by OpenList task type and status.

        OpenList v4 exposes task APIs as `/api/task/{task_type}/{status}`.
        Common task types include offline_download, upload, copy, and decompress.

        Args:
            task_type: Task category, e.g. offline_download, upload, copy.
            status: Task list status: "undone" for running/pending or "done" for completed.
            page: Page number for deployments that support pagination.
            per_page: Page size for deployments that support pagination.

        Returns:
            JSON string with task list data, or a structured compatibility error
            if this OpenList deployment does not expose the selected list endpoint.
        """

        task_type = _validate_task_type(task_type)
        status = status.strip()
        if status not in TASK_LIST_STATUSES:
            raise ValueError(
                f"Unsupported status: {status}. "
                f"Supported values: {', '.join(sorted(TASK_LIST_STATUSES))}"
            )
        validate_pagination(page, per_page)
        client = await get_client()
        data = await client.request(
            "POST",
            f"task/{task_type}/{status}",
            params={"page": page, "per_page": per_page},
        )
        return json.dumps(data, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def get_task_info(
        task_id: str,
        task_type: str = "offline_download",
    ) -> str:
        """Get one task by ID using OpenList's typed task API.

        Args:
            task_id: The task ID returned by OpenList.
            task_type: Task category, e.g. offline_download, upload, copy.

        Returns:
            JSON string with task details.
        """
        task_type = _validate_task_type(task_type)
        client = await get_client()
        data = await client.request(
            "POST",
            f"task/{task_type}/info",
            params=_task_params(task_id),
        )
        return json.dumps(data, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def delete_task(
        task_id: str,
        task_type: str = "offline_download",
        confirm: bool = False,
    ) -> str:
        """Delete a completed or failed task.

        Args:
            task_id: The ID of the task to delete.
            task_type: Task category, e.g. offline_download, upload, copy.
            confirm: Must be true to actually delete the task. Defaults to false.
        """
        if not confirm:
            return "Task deletion not performed. Re-run with confirm=true to delete it."
        task_type = _validate_task_type(task_type)
        enforce_writable("delete_task")
        client = await get_client()
        await client.request(
            "POST",
            f"task/{task_type}/delete",
            params=_task_params(task_id),
        )
        return f"Task deleted successfully: {task_id}"

    @mcp.tool()
    async def retry_task(
        task_id: str,
        task_type: str = "offline_download",
    ) -> str:
        """Retry a failed task."""
        task_type = _validate_task_type(task_type)
        enforce_writable("retry_task")
        client = await get_client()
        await client.request(
            "POST",
            f"task/{task_type}/retry",
            params=_task_params(task_id),
        )
        return f"Task retry submitted: {task_id}"

    @mcp.tool()
    async def cancel_task(
        task_id: str,
        task_type: str = "offline_download",
        confirm: bool = False,
    ) -> str:
        """Cancel a running task.

        Args:
            task_id: The ID of the running task to cancel.
            task_type: Task category, e.g. offline_download, upload, copy.
            confirm: Must be true to actually cancel the task. Defaults to false.
        """
        if not confirm:
            return "Task cancellation not performed. Re-run with confirm=true to cancel it."
        task_type = _validate_task_type(task_type)
        enforce_writable("cancel_task")
        client = await get_client()
        await client.request(
            "POST",
            f"task/{task_type}/cancel",
            params=_task_params(task_id),
        )
        return f"Task cancelled: {task_id}"
