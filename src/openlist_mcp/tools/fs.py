"""File system tools for OpenList MCP Server."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..client import OpenListError, get_client
from . import normalize_names, validate_name, validate_pagination, validate_path


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

        validate_path(path)
        validate_pagination(page, per_page)
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

        validate_path(path)
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

        validate_path(path)
        validate_pagination(page, per_page)
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
        validate_path(path)
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
        validate_path(path)
        validate_name(name)
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
        names: list[str] | str,
    ) -> str:
        """Copy files or folders to another directory.

        Args:
            src_dir: Source directory path containing the items to copy.
            dst_dir: Destination directory path.
            names: List of file/folder names or comma-separated string to copy (e.g. ["file1.txt", "file2.pdf"] or "file1.txt,file2.pdf").

        Returns:
            Success or error message with task info if processed asynchronously.
        """
        import json

        validate_path(src_dir)
        validate_path(dst_dir)
        client = await get_client()
        name_list = normalize_names(names)

        if not name_list:
            return "No files specified to copy. Please provide at least one file name."
        data = await client.request(
            "POST",
            "fs/copy",
            json={
                "src_dir": src_dir,
                "dst_dir": dst_dir,
                "names": name_list,
            },
        )
        if data is not None and data != {}:
            return f"Copy task created: {json.dumps(data, ensure_ascii=False)}"
        return f"Copied successfully: {name_list} -> {dst_dir}"

    @mcp.tool()
    async def move(
        src_dir: str,
        dst_dir: str,
        names: list[str] | str,
    ) -> str:
        """Move files or folders to another directory.

        Args:
            src_dir: Source directory path containing the items to move.
            dst_dir: Destination directory path.
            names: List of file/folder names or comma-separated string to move (e.g. ["file1.txt", "file2.pdf"] or "file1.txt,file2.pdf").

        Returns:
            Success or error message with task info if processed asynchronously.
        """
        import json

        validate_path(src_dir)
        validate_path(dst_dir)
        client = await get_client()
        name_list = normalize_names(names)

        if not name_list:
            return "No files specified to move. Please provide at least one file name."
        data = await client.request(
            "POST",
            "fs/move",
            json={
                "src_dir": src_dir,
                "dst_dir": dst_dir,
                "names": name_list,
            },
        )
        if data is not None and data != {}:
            return f"Move task created: {json.dumps(data, ensure_ascii=False)}"
        return f"Moved successfully: {name_list} -> {dst_dir}"

    @mcp.tool()
    async def remove(
        directory: str,
        names: list[str] | str,
        confirm: bool = False,
    ) -> str:
        """Delete files or folders.

        Args:
            directory: Directory path containing the items to delete.
            names: List of file/folder names or comma-separated string to delete (e.g. ["file1.txt", "old_folder"] or "file1.txt,old_folder").
            confirm: Must be true to actually delete items. Defaults to false.

        Returns:
            Success or confirmation-required message.
        """
        if not confirm:
            return "Deletion not performed. Re-run with confirm=true to delete these items."
        validate_path(directory)
        client = await get_client()
        name_list = normalize_names(names)

        if not name_list:
            return "No files specified to delete. Please provide at least one file name."
        await client.request(
            "POST",
            "fs/remove",
            json={"dir": directory, "names": name_list},
        )
        return f"Deleted successfully: {name_list} from {directory}"

    @mcp.tool()
    async def recursive_move(
        src_dir: str,
        dst_dir: str,
    ) -> str:
        """Recursively move an entire directory tree to a new location.

        Unlike the move tool, this does not require listing individual file names.
        The entire source directory and all its contents are moved together.

        Args:
            src_dir: Source directory path to move.
            dst_dir: Destination directory path.

        Returns:
            Success message or task info.
        """
        import json
        import posixpath

        validate_path(src_dir)
        validate_path(dst_dir)
        client = await get_client()

        # Try the native API first (OpenList v4.3+)
        try:
            data = await client.request(
                "POST",
                "fs/recursive_move",
                json={"src_dir": src_dir, "dst_dir": dst_dir},
            )
            if data is not None and data != {}:
                return f"Recursive move task created: {json.dumps(data, ensure_ascii=False)}"
            return f"Recursive move completed: {src_dir} -> {dst_dir}"
        except OpenListError as exc:
            message = exc.message.lower()
            if not any(
                marker in message
                for marker in ("not found", "unsupported", "method not allowed", "recursive_move")
            ):
                raise

        # Fallback: OpenList v4.2.x doesn't support fs/recursive_move.
        # Use rename (same parent) or move+rename (different parents).
        src_dir_clean = src_dir.rstrip("/")
        dst_dir_clean = dst_dir.rstrip("/")
        src_name = posixpath.basename(src_dir_clean)
        src_parent = posixpath.dirname(src_dir_clean) or "/"
        dst_parent = posixpath.dirname(dst_dir_clean) or "/"
        dst_name = posixpath.basename(dst_dir_clean)
        validate_name(src_name)
        validate_name(dst_name)

        if src_parent == dst_parent:
            # Same parent directory — just rename
            await client.request(
                "POST",
                "fs/rename",
                json={"path": src_dir_clean, "name": dst_name},
            )
            return f"Recursive move completed (rename): {src_dir} -> {dst_dir}"
        else:
            # Different parents — move then rename
            await client.request(
                "POST",
                "fs/move",
                json={
                    "src_dir": src_parent,
                    "dst_dir": dst_parent,
                    "names": [src_name],
                },
            )
            if src_name != dst_name:
                moved_path = (
                    f"{dst_parent.rstrip('/')}/{src_name}" if dst_parent != "/" else f"/{src_name}"
                )
                await client.request(
                    "POST",
                    "fs/rename",
                    json={"path": moved_path, "name": dst_name},
                )
            return f"Recursive move completed (move+rename): {src_dir} -> {dst_dir}"
