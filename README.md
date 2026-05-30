# OpenList MCP Server

<p align="center">
  <img src="docs/og-image.png" alt="OpenList MCP Server" width="800">
</p>

<p align="center">
  <a href="README.md">English</a> · <a href="README-zh.md">中文</a>
</p>

---

MCP Server for [OpenList](https://github.com/OpenListTeam/OpenList) — an open-source file management system (similar to Alist). Enables MCP-compatible AI agents to browse, upload, download, search, and manage files via the OpenList REST API.

```
┌────────────────┐     ┌────────────────────┐     ┌──────────────┐     ┌───────────────┐
│ Claude Desktop │────▶│ openlist-mcp-server │────▶│ OpenList API │────▶│ Storage (S3,  │
│   (or SOLO)    │ MCP │   (this project)    │ HTTP │   (your     │     │  SMB, Local,  │
└────────────────┘     └────────────────────┘     │   server)   │     │  ...)         │
                                                    └──────────────┘     └───────────────┘
```

## Features

- File browsing: list directories, get file details, search files
- File management: create folders, rename, copy, move, delete
- File transfer: upload base64 content, upload local files accessible to the MCP server, get download URLs
- Share management: create, list, cancel, delete share links
- Task management: list, retry, cancel, delete async tasks
- Auto authentication: JWT login and retry after token expiration
- **NEW v0.2.5** 2FA / TOTP support: login with optional OTP code
- **NEW v0.2.5** Local file upload: `upload_local_file` tool (disabled by default, requires `OPENLIST_LOCAL_UPLOAD_ROOTS`)
- **NEW v0.2.6** Advanced: offline download, archive decompression, recursive move

## Requirements

- Python 3.10+ (check with `python3 --version`)
- A running OpenList instance — this is a client, not a standalone service

## Quick Start

### For AI Assistants

Copy the contents of [`AI_GUIDE.md`](AI_GUIDE.md) and paste it to your AI assistant (Claude, etc.). The AI will know how to install, configure, and use all 26 tools.

### For Human Users

Follow the instructions below to install manually.

### From GitHub source

```bash
git clone https://github.com/hbestm/openlist-mcp-server.git
cd openlist-mcp-server

# (Recommended) Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

pip install -e .
```

### From source archive

If you do not use Git, download the repository source archive from GitHub's **Code → Download ZIP**, then:

```bash
unzip openlist-mcp-server-main.zip
cd openlist-mcp-server-main
pip install -e .
```

> Note: GitHub Releases may contain only tags unless release assets are explicitly uploaded. Use the source installation method above if no release zip asset is available.

### Verify installation

```bash
openlist-mcp
# Expected output:
# "OpenList MCP Server v0.2.7 installed successfully.
#  Set OPENLIST_URL, OPENLIST_USERNAME, and OPENLIST_PASSWORD to get started."
```

## Configuration

### Environment variables

```bash
export OPENLIST_URL="https://your-openlist-instance.example.com"
export OPENLIST_USERNAME="your_username"
export OPENLIST_PASSWORD="your_password"

# Required to enable upload_local_file (disabled by default).
export OPENLIST_LOCAL_UPLOAD_ROOTS="/tmp:/path/to/uploads"
```

You can also use a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
# Edit .env with your credentials
pip install python-dotenv   # required for .env support
```

The server automatically loads `.env` when `python-dotenv` is installed. **Never commit `.env` to Git** — the repository's `.gitignore` already excludes it.

### Security notes

- **Use HTTPS in production** — credentials are sent in plain text over HTTP.
- **Protect your MCP config file**:
  - Linux/macOS: `chmod 600 claude_desktop_config.json`
  - Windows: Right-click the file → Properties → Security → Remove all users except yourself.
- **Restrict local file uploads when possible**. `upload_local_file` is disabled by default; set `OPENLIST_LOCAL_UPLOAD_ROOTS` to one or more allowed directories to enable it.

## Usage

### Claude Desktop

1. Open Claude Desktop → Settings → **MCP Servers**.
2. Add a new server:

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

> **Config file locations:**
> - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
> - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
> - Linux: `~/.config/Claude/claude_desktop_config.json`

3. **Restart Claude Desktop** to load the new server.
4. Try a prompt: *"List the files on my OpenList server."*

### Example prompts to get started

| Goal | Prompt |
|------|--------|
| List root directory | *"List files in the root directory of my OpenList."* |
| Search files | *"Search for files named 'report' on OpenList."* |
| Upload a file | *"Upload this file to /documents on OpenList."* (Claude will ask for the file) |
| Get download link | *"Give me the download URL for /documents/report.pdf."* |
| Create a folder | *"Create a folder called 'archive' under /documents on OpenList."* |

### Direct stdio (debugging)

```bash
export OPENLIST_URL="https://your-openlist-instance.example.com"
export OPENLIST_USERNAME="your_username"
export OPENLIST_PASSWORD="your_password"
openlist-mcp
```

### SOLO / Other MCP clients

Same config format:

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
| `search not available` | Search index is disabled or backend doesn't support search | Enable OpenList search/indexing in admin settings first; storage backend must support search |
| `2FA code is required` | 2FA is enabled on your OpenList account | Call `login(otp_code="your_totp_code")` with a TOTP code from your authenticator app |
| `Invalid 2FA code` | The TOTP code was incorrect or expired | Generate a new code from your authenticator app and re-run login with the correct `otp_code` |
| Non-JSON response on task API | OpenList version mismatch | Some admin endpoints may not be exposed in your deployment |

**Enable debug logging:**

```bash
OPENLIST_URL=... OPENLIST_USERNAME=... OPENLIST_PASSWORD=... openlist-mcp 2>&1 | head -20
```

## Uninstall

```bash
pip uninstall openlist-mcp-server -y
rm -rf venv
```

## Tools

### Note for local file uploads

`upload_local_file` uploads a file from a path that the MCP server process can read. It is useful for local agents or server-side deployments.

**By default, this tool is disabled for security.** You must set the `OPENLIST_LOCAL_UPLOAD_ROOTS` environment variable to one or more allowed parent directories separated by your OS path separator (`:` on Linux/macOS, `;` on Windows). Without this variable, `upload_local_file` will reject all file paths.

If the MCP server cannot access the user's local filesystem, use `upload_file` with base64 content instead.

### Authentication and public API

| Tool | Description |
|---|---|
| `login` | Login using configured credentials. Pass `otp_code` if 2FA is enabled on your account. Token is not printed by the server. |
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
| `upload_local_file` | Upload a local file path readable by the MCP server process. |

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

> **Note on `names` parameter**: The `copy`, `move`, and `remove` tools use comma-separated file names. If a filename contains a comma, the tool cannot distinguish it — rename the file before operation.

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

## Changelog

### v0.2.7

- **`list_download_tools`**: New tool to query available offline download tools (aria2, Transmission, qBittorrent, etc.) configured on the server.
- **`offline_download`**: Docstring updated to document all supported tools.
- **`validate_path` fix**: Component-level `..` detection — no longer rejects legitimate filenames like `backup..2024.tar.gz`.
- **Startup guide**: Updated to reflect 27 tools.

### v0.2.6

- **Advanced tools**: New `tools/advanced.py` module added.
- **`offline_download`**: Download files from a remote URL directly to the OpenList server (requires a download tool like aria2 configured on the server).
- **`decompress_archive`**: Decompress archive files (zip, rar, 7z, tar.gz, etc.) on the server.
- **`get_me`**: Get current authenticated user's profile information (username, role, 2FA status, permissions).
- **`logout`**: Logout and invalidate the current authentication token.
- **`recursive_move`**: Recursively move an entire directory tree to a new location without listing individual file names.
- **Startup guide**: Printed usage help now includes all 26 tools with categories.

### v0.2.5

- **2FA / TOTP support**: `login()` tool now accepts an optional `otp_code` parameter. When the OpenList account has 2FA enabled, the agent will prompt the user to provide a TOTP code.
- **Local file upload**: New `upload_local_file` tool. Upload a local file path directly without base64 encoding. Configure `OPENLIST_LOCAL_UPLOAD_ROOTS` to restrict allowed directories.
- **Improved large file uploads**: Async chunked streaming instead of single `read_bytes()`. Write timeout increased to 120s.
- **Security hardening**: Base64 decode exception narrowed to `ValueError, binascii.Error`. Added `OPENLIST_LOCAL_UPLOAD_ROOTS` restriction for local file uploads.
- **Release workflow**: Removed automatic PyPI publishing. Tag push creates a GitHub Release with build artifacts only.
- **Version unification**: `__version__`, `pyproject.toml`, and `server.py` all consistent at v0.2.5. `__version__` now reads from package metadata at runtime.
- **Documentation fixes**: Installation guide corrected for source archive; `search_files` notes now clarify that OpenList search/indexing must be enabled.
- **Name validation fix**: `validate_name()` now correctly allows filenames containing `..` (e.g. `backup..tar.gz`, `..hidden_file`), only rejecting `.` and `..` as complete directory names. Empty names also properly rejected.

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

For bugs, feature requests, or questions, please [open a GitHub Issue](https://github.com/hbestm/openlist-mcp-server/issues).

## License

MIT
