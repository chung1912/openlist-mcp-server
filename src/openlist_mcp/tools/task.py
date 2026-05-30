"""Task management tools for OpenList MCP Server."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..client import get_client
from . import validate_pagination


def register_task_tools(mcp: FastMCP) -> None:
    """Register task management MCP tools."""

    @mcp.tool()
    async def list_tasks(page: int = 1, per_page: int = 50) -> str:
        """List asynchronous tasks (uploads, copies, moves, downloads, etc.)."""
        import json

        validate_pagination(page, per_page)
        client = await get_client()
        data = await client.request(
            "GET",
            "admin/task",
            params={"page": page, "per_page": per_page},
        )
        return json.dumps(data, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def delete_task(task_id: str, confirm: bool = False) -> str:
        """Delete a completed or failed task.

        Args:
            task_id: The ID of the task to delete.
            confirm: Must be true to actually delete the task. Defaults to false.
        """
        if not confirm:
            return "Task deletion not performed. Re-run with confirm=true to delete it."
        client = await get_client()
        await client.request("POST", "admin/task/delete", json={"task_id": task_id})
        return f"Task deleted successfully: {task_id}"

    @mcp.tool()
    async def retry_task(task_id: str) -> str:
        """Retry a failed task."""
        client = await get_client()
        await client.request("POST", "admin/task/retry", json={"task_id": task_id})
        return f"Task retry submitted: {task_id}"

    @mcp.tool()
    async def cancel_task(task_id: str, confirm: bool = False) -> str:
        """Cancel a running task.

        Args:
            task_id: The ID of the running task to cancel.
            confirm: Must be true to actually cancel the task. Defaults to false.
        """
        if not confirm:
            return "Task cancellation not performed. Re-run with confirm=true to cancel it."
        client = await get_client()
        await client.request("POST", "admin/task/cancel", json={"task_id": task_id})
        return f"Task cancelled: {task_id}"
