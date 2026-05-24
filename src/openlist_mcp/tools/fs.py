"""File system tools for OpenList MCP Server."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..client import get_client


def register_fs_tools(mcp: FastMCP) -> None:
    """Register file system operation MCP tools."""

    @mcp.tool()
    async def list_files(
        path: str = "/",
        page: int = 1,
        per_page: int = 50,
        password: str = "",
    ) -> str:
        """List files and folders in a directory on OpenList.

        Args:
            path: Directory path to list. Use "/" for root. Defaults to "/".
            page: Page number for pagination. Defaults to 1.
            per_page: Number of items per page (max 200). Defaults to 50.
            password: Password if the directory is password-protected. Defaults to "".

        Returns:
            JSON string containing file list with name, size, type, modified time, etc.
        """
        import json

        client = await get_client()
        data = await client.request(
            "POST",
            "fs/list",
            json={
                "path": path,
                "page": page,
                "per_page": per_page,
                "password": password,
            },
        )
        return json.dumps(data, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def get_file_info(
        path: str,
        password: str = "",
    ) -> str:
        """Get detailed information about a specific file or folder.

        Args:
            path: Full path to the file or folder.
            password: Password if the path is password-protected. Defaults to "".

        Returns:
            JSON string with file details including size, type, provider, raw_url, etc.
        """
        import json

        client = await get_client()
        data = await client.request(
            "POST",
            "fs/get",
            json={
                "path": path,
                "password": password,
            },
        )
        return json.dumps(data, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def search_files(
        path: str = "/",
        keyword: str = "",
        page: int = 1,
        per_page: int = 50,
        password: str = "",
    ) -> str:
        """Search for files and folders by keyword.

        Args:
            path: Directory path to search in. Use "/" for root. Defaults to "/".
            keyword: Search keyword to match against file/folder names.
            page: Page number for pagination. Defaults to 1.
            per_page: Number of items per page. Defaults to 50.
            password: Password if the directory is password-protected. Defaults to "".

        Returns:
            JSON string containing matching files and folders.
        """
        import json

        client = await get_client()
        data = await client.request(
            "POST",
            "fs/search",
            json={
                "path": path,
                "keyword": keyword,
                "page": page,
                "per_page": per_page,
                "password": password,
            },
        )
        return json.dumps(data, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def create_folder(
        path: str,
    ) -> str:
        """Create a new folder (directory) on OpenList.

        Args:
            path: Full path of the new folder to create (e.g. "/photos/2024").

        Returns:
            Success or error message.
        """
        client = await get_client()
        await client.request(
            "POST",
            "fs/mkdir",
            json={"path": path},
        )
        return f"Folder created successfully: {path}"

    @mcp.tool()
    async def rename(
        path: str,
        name: str,
    ) -> str:
        """Rename a file or folder.

        Args:
            path: Full path to the file or folder to rename.
            name: New name (not full path, just the new file/folder name).

        Returns:
            Success or error message.
        """
        client = await get_client()
        await client.request(
            "POST",
            "fs/rename",
            json={"path": path, "name": name},
        )
        return f"Renamed successfully: {path} -> {name}"

    @mcp.tool()
    async def copy(
        src_dir: str,
        dst_dir: str,
        names: str,
    ) -> str:
        """Copy files or folders to another directory.

        Args:
            src_dir: Source directory path containing the items to copy.
            dst_dir: Destination directory path.
            names: Comma-separated list of file/folder names to copy (e.g. "file1.txt,file2.pdf").

        Returns:
            Success or error message with task info if processed asynchronously.
        """
        import json

        client = await get_client()
        name_list = [n.strip() for n in names.split(",") if n.strip()]
        data = await client.request(
            "POST",
            "fs/copy",
            json={
                "src_dir": src_dir,
                "dst_dir": dst_dir,
                "names": name_list,
            },
        )
        if data:
            return f"Copy task created: {json.dumps(data, ensure_ascii=False)}"
        return f"Copied successfully: {names} -> {dst_dir}"

    @mcp.tool()
    async def move(
        src_dir: str,
        dst_dir: str,
        names: str,
    ) -> str:
        """Move files or folders to another directory.

        Args:
            src_dir: Source directory path containing the items to move.
            dst_dir: Destination directory path.
            names: Comma-separated list of file/folder names to move (e.g. "file1.txt,file2.pdf").

        Returns:
            Success or error message with task info if processed asynchronously.
        """
        import json

        client = await get_client()
        name_list = [n.strip() for n in names.split(",") if n.strip()]
        data = await client.request(
            "POST",
            "fs/move",
            json={
                "src_dir": src_dir,
                "dst_dir": dst_dir,
                "names": name_list,
            },
        )
        if data:
            return f"Move task created: {json.dumps(data, ensure_ascii=False)}"
        return f"Moved successfully: {names} -> {dst_dir}"

    @mcp.tool()
    async def remove(
        dir: str,
        names: str,
        confirm: bool = False,
    ) -> str:
        """Delete files or folders.

        Args:
            dir: Directory path containing the items to delete.
            names: Comma-separated list of file/folder names to delete (e.g. "file1.txt,old_folder").
            confirm: Must be true to actually delete items. Defaults to false.

        Returns:
            Success or confirmation-required message.
        """
        if not confirm:
            return "Deletion not performed. Re-run with confirm=true to delete these items."
        client = await get_client()
        name_list = [n.strip() for n in names.split(",") if n.strip()]
        await client.request(
            "POST",
            "fs/remove",
            json={"dir": dir, "names": name_list},
        )
        return f"Deleted successfully: {names} from {dir}"
