# OpenList MCP Server

MCP Server for [OpenList](https://github.com/OpenListTeam/OpenList). It lets MCP-compatible AI agents browse, upload, download, search, and manage files through the OpenList REST API.

## Features

- File browsing: list directories, get file details, search files
- File management: create folders, rename, copy, move, delete
- File transfer: upload base64 content, get download URLs
- Share management: create, list, cancel, delete share links
- Task management: list, retry, cancel, delete async tasks
- Auto authentication: JWT login and retry after token expiration

## Requirements

- Python 3.10+
- A running OpenList instance

## Installation

```bash
cd openlist-mcp-server
pip install -e .
```

## Configuration

Set environment variables before running:

```bash
export OPENLIST_URL="https://your-openlist-instance.example.com"
export OPENLIST_USERNAME="your_username"
export OPENLIST_PASSWORD="your_password"
```

Do not commit real credentials. Use `.env.example` as a template only.

## Usage

### Claude Desktop / MCP Client

```json
{
  "mcpServers": {
    "openlist": {
      "command": "openlist-mcp",
      "env": {
        "OPENLIST_URL": "https://your-openlist-instance.example.com",
        "OPENLIST_USERNAME": "your_username",
        "OPENLIST_PASSWORD": "your_password"
      }
    }
  }
}
```

### Direct stdio run

```bash
openlist-mcp
```

## Tools

### Authentication and public API

| Tool | Description |
|---|---|
| `login` | Login using configured credentials. Token is not printed. |
| `get_public_settings` | Get public OpenList settings without authentication. |

### File system

| Tool | Description |
|---|---|
| `list_files` | List files and folders in a directory. |
| `get_file_info` | Get detailed info for a file or folder. |
| `search_files` | Search files by keyword. Availability depends on OpenList storage/search support. |
| `create_folder` | Create a directory. |
| `rename` | Rename a file or folder. |
| `copy` | Copy files/folders to another directory. |
| `move` | Move files/folders to another directory. |
| `remove` | Delete files/folders. Requires `confirm=true`. |

### Transfer

| Tool | Description |
|---|---|
| `get_download_url` | Get direct/proxy download URL for a file. |
| `upload_file` | Upload base64-encoded file content. |

### Tasks

| Tool | Description |
|---|---|
| `list_tasks` | List async tasks. Endpoint availability depends on OpenList version. |
| `delete_task` | Delete a task. Requires `confirm=true`. |
| `retry_task` | Retry a failed task. |
| `cancel_task` | Cancel a running task. Requires `confirm=true`. |

### Shares

| Tool | Description |
|---|---|
| `create_share` | Create a share link. |
| `list_shares` | List share links. |
| `cancel_share` | Disable a share link. Requires `confirm=true`. |
| `delete_share` | Permanently delete a share link. Requires `confirm=true`. |

## Integration tests

```bash
export OPENLIST_URL="https://your-openlist-instance.example.com"
export OPENLIST_USERNAME="your_username"
export OPENLIST_PASSWORD="your_password"
export OPENLIST_TEST_DIR="/"
PYTHONPATH=src python3 test_integration.py
```

The integration test creates a temporary directory under `OPENLIST_TEST_DIR` and removes it after the test. It never prints the password or token.

## Notes

- Search support depends on the OpenList backend/storage. Some servers return `search not available`.
- Some admin task endpoints may differ between OpenList versions and deployments.
- Destructive tools require an explicit `confirm=true` parameter to reduce accidental operations by AI agents.

## License

MIT
