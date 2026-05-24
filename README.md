## Installation

### From source

```bash
# Clone the repository
git clone https://github.com/hbestm/openlist-mcp-server.git
cd openlist-mcp-server

# (Recommended) Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install the package and its dependencies
pip install -e .
```

### From release zip

Download the latest release from [GitHub Releases](https://github.com/hbestm/openlist-mcp-server/releases), then:

```bash
unzip openlist-mcp-server-*.zip
cd openlist-mcp-server-release
pip install -e .
```

### Verify installation

```bash
openlist-mcp --help
# Should show: "OPENLIST_URL is required" — that means the tool is installed correctly.
```

## Prerequisites

Before using this MCP server, you need:

1. **A running OpenList instance** — this server is a client for OpenList, not a standalone service. You need an existing OpenList deployment (e.g., https://your-openlist-instance.example.com).
2. **Python 3.10 or later** installed on your system.

## Configuration

### Option A: Environment variables (recommended)

Set these before running the server:

```bash
export OPENLIST_URL="https://your-openlist-instance.example.com"
export OPENLIST_USERNAME="your_username"
export OPENLIST_PASSWORD="your_password"
```

You can also use a `.env` file for local development (requires `python-dotenv`):

```bash
pip install python-dotenv
```

Create a `.env` file in the project root:

```env
OPENLIST_URL=https://your-openlist-instance.example.com
OPENLIST_USERNAME=your_username
OPENLIST_PASSWORD=your_password
```

**Never commit `.env` to version control.** The repository's `.gitignore` already excludes it.

### Option B: MCP client config

Configure your MCP client (Claude Desktop, SOLO, etc.) with these credentials.

### Security notes

- **Use HTTPS** in production. Credentials are sent in plain text over HTTP.
- **Protect your config file.** If using Claude Desktop, ensure `claude_desktop_config.json` is readable only by you (`chmod 600` on Linux/macOS).

## Usage

### Claude Desktop

1. Open Claude Desktop settings.
2. Go to the **MCP Servers** section.
3. Add a new server with the following configuration:

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

> **Config file location:**
> - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
> - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
> - Linux: `~/.config/Claude/claude_desktop_config.json`

4. **Restart Claude Desktop** to load the new MCP server.
5. Verify the server is connected — look for a green status indicator or try asking Claude to list files.

### Direct stdio (for testing)

```bash
export OPENLIST_URL="https://your-openlist-instance.example.com"
export OPENLIST_USERNAME="your_username"
export OPENLIST_PASSWORD="your_password"
openlist-mcp
```

Then send MCP protocol messages via stdin/stdout. This is mainly for debugging.

### SOLO / Other MCP clients

The same configuration format works for any MCP-compatible client:

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

## Troubleshooting

| Problem | Likely cause | Solution |
|---------|-------------|----------|
| `OPENLIST_URL is required` | Environment variables not set | Set `OPENLIST_URL`, `OPENLIST_USERNAME`, `OPENLIST_PASSWORD` |
| `password is incorrect` | Wrong credentials | Verify your OpenList username and password |
| `Connection refused` | OpenList instance is down | Check that your OpenList server is running and reachable |
| Tool not found after install | PATH not updated or venv not activated | Re-activate your virtual environment or reinstall |
| MCP client shows "disconnected" | Claude Desktop needs restart | Restart Claude Desktop after adding the server config |
| `search not available` | Backend doesn't support search | This depends on your OpenList storage provider |
| Non-JSON response on task API | OpenList version mismatch | Some admin endpoints may not be exposed in your deployment |

## Uninstall

```bash
pip uninstall openlist-mcp-server -y
rm -rf venv  # if using a virtual environment
```## Uninstall

```bash
pip uninstall openlist-mcp-server -y
rm -rf venv  # if using a virtual environment
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

---

## Community & Support

<p align="center">
  <a href="docs/qr-community.jpg">
    <img src="docs/qr-community.jpg" alt="QQ Community" width="200">
  </a>
  <a href="docs/qr-sponsor.png">
    <img src="docs/qr-sponsor.png" alt="Sponsor" width="200">
  </a>
</p>

<p align="center">
  <strong>QQ 交流群</strong>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <strong>微信赞助</strong>
</p>

## License

MIT