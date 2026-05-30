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
- **NEW v0.2.7** Auto TOTP: `OPENLIST_TOTP_SECRET` — auto-generate 2FA codes during login
- **NEW v0.2.7** Download tool management: `list_download_tools` — query available download tools (aria2, Transmission, qBittorrent)

## Requirements

- Python 3.10+ (check with `python3 --version`)
- A running OpenList instance — this is a client, not a standalone service

## Quick Start

### For AI Assistants

Copy the contents of [`AI_GUIDE.md`](AI_GUIDE.md) and paste it to your AI assistant (Claude, etc.). The AI will know how to install, configure, and use all 32 tools.

### Example Prompts

Once configured, just say these to your AI:

| What you want to do | Say to the AI |
|--------------------|--------------|
| **List files** | "List files in the root directory of my OpenList." |
| **Search files** | "Search for files named 'report' on OpenList." |
| **Upload a file** | "Upload this file to /documents on OpenList." |
| **Get download link** | "Give me the download URL for /documents/report.pdf." |
| **Create a folder** | "Create a folder called 'archive' under /documents on OpenList." |
| **Download a file** | "Download this file to /downloads: https://example.com/file.zip" |
| **BT download** | "Download this torrent: magnet:?xt=..." |
| **Check download tools** | "What download tools are available on my server?" |
| **Extract an archive** | "Extract data.zip in /downloads to the data folder" |
| **Download + extract** | "Download this archive and extract it to the project directory" |
| **Batch clean up** | "Delete all .tmp files in /downloads" |
| **Check identity** | "What user am I logged in as?" |

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
# Without OPENLIST_URL, this prints the setup guide and exits.
# With OPENLIST_URL configured, it starts the MCP stdio server.
```

## Configuration

### Environment variables

```bash
export OPENLIST_URL="https://your-openlist-instance.example.com"
export OPENLIST_USERNAME="your_username"
export OPENLIST_PASSWORD="your_password"

# Optional MCP safety controls.
export OPENLIST_READONLY="false"
export OPENLIST_ALLOWED_PATHS="/mcp-dev-test,/public"

# Required to enable upload_local_file (disabled by default).
export OPENLIST_LOCAL_UPLOAD_ROOTS="/tmp:/path/to/uploads"

# Optional: auto-generate TOTP codes for 2FA login.
export OPENLIST_TOTP_SECRET="your_totp_secret_key"
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
- **Use a dedicated low-privilege OpenList account** for MCP access. Avoid using the
  `admin` account for daily AI-agent operations.
- **Limit the account to the smallest useful storage scope**. Do not expose your
  server home directory, root filesystem, shell history, Docker config, SSH keys,
  or other system paths through OpenList.
- **Use MCP-side safety controls for AI agents**. Set `OPENLIST_READONLY=true`
  to block write/high-impact tools, and set `OPENLIST_ALLOWED_PATHS` to a
  comma-separated list such as `/mcp-dev-test,/public` to keep all OpenList path
  operations inside approved directories.
- **Protect your MCP config file**:
  - Linux/macOS: `chmod 600 claude_desktop_config.json`
  - Windows: Right-click the file → Properties → Security → Remove all users except yourself.
- **Restrict local file uploads when possible**. `upload_local_file` is disabled by default; set `OPENLIST_LOCAL_UPLOAD_ROOTS` to one or more allowed directories to enable it.
- **Ask for explicit user confirmation before high-impact actions** such as creating
  public shares, generating download URLs, starting offline downloads, or moving
  large directory trees. These operations can expose data or consume significant
  bandwidth/storage even though they do not delete files.

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

> A complete example with all optional settings (local file upload, auto TOTP) can be found at [`mcp-config.example.json`](mcp-config.example.json).

> **Config file locations:**
> - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
> - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
> - Linux: `~/.config/Claude/claude_desktop_config.json`

3. **Restart Claude Desktop** to load the new server.
4. Try a prompt: *"List the files on my OpenList server."*

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
| `upload_local_file` rejected | `OPENLIST_LOCAL_UPLOAD_ROOTS` not set | Set the env var to one or more allowed directories (e.g. `/tmp:/path/to/uploads`) |
| `Auto-generated TOTP code was rejected` | Wrong `OPENLIST_TOTP_SECRET` value | Verify the TOTP secret matches the one set in your authenticator app |
| `.env` file not loading | `python-dotenv` not installed | Run `pip install python-dotenv` |
| `recursive_move` returns `object not found` | OpenList v4.2.x may not support the native recursive move endpoint | The MCP server attempts a fallback using `rename` or `move` + `rename`; if the fallback also fails, the original error is reported |
| Offline download task created but not progressing | The selected download tool (e.g. aria2) is not running on the OpenList server | Check the download tool's service status on the server. For aria2: run `aria2c --enable-rpc --rpc-listen-all=true --rpc-allow-origin-all -D`. For other tools, verify the service is active and the RPC port is accessible |
| `Guest user is disabled, login please` | Token expired or invalid | Login again — the server handles this automatically on the next API call |
| Transmission/qBittorrent downloads not working | Download tool not properly configured on server | Check: (1) Is the service installed and running? (2) Is the WebUI/RPC port accessible? (3) Are the credentials in OpenList admin settings correct? Run `list_download_tools` to verify the server can detect the tool |
| Non-JSON response on task API | The selected task list endpoint returns the OpenList web UI instead of JSON | If you have a task ID, use `get_task_info(task_id, task_type)`; otherwise check the OpenList version/deployment |
| `pip install` fails | Python version too old or missing dependencies | Use Python 3.10+ and ensure `pip` is up to date: `pip install --upgrade pip` |
| `list_download_tools` returns few tools | Download tools not installed/configured on server | Run `list_download_tools` to see what's available; install and configure aria2, Transmission, etc. on the OpenList server |
| HTTP warning about plain text credentials | Using HTTP instead of HTTPS | Use HTTPS in production, or accept the warning for local/internal network use |

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
| `login` | Login using configured credentials. If 2FA is enabled and `OPENLIST_TOTP_SECRET` is set, the TOTP code is generated automatically. Otherwise, pass `otp_code` manually. |
| `get_public_settings` | Get public OpenList settings without authentication. |
| `get_me` | Get current user profile (username, role, permissions, 2FA status). |
| `get_capabilities` | Summarize server settings, current user, available download tools, and MCP safety configuration. |
| `logout` | Logout and invalidate the current token. |

### File system

| Tool | Description |
|---|---|
| `list_files` | List files and folders in a directory. |
| `list_dirs` | List child directories under a path for safer destination selection. |
| `get_file_info` | Get detailed info for a file or folder. |
| `search_files` | Search files by keyword. Availability depends on OpenList storage/search support. |
| `create_folder` | Create a directory. |
| `rename` | Rename a file or folder. |
| `batch_rename` | Rename multiple files/folders in the same directory using OpenList's batch rename API. |
| `copy` | Copy files/folders to another directory. |
| `move` | Move files/folders to another directory. |
| `remove` | Delete files/folders. Requires `confirm=true`. |
| `recursive_move` | Move an entire directory tree to a new location (with fallback for OpenList v4.2.x). |

### Transfer

| Tool | Description |
|---|---|
| `get_download_url` | Get direct/proxy download URL for a file. |
| `upload_file` | Upload base64-encoded file content. |
| `upload_local_file` | Upload a local file path readable by the MCP server process. |

### Tasks

| Tool | Description |
|---|---|
| `list_tasks` | List typed async tasks via `/api/task/{task_type}/{status}`. Supports `done` and `undone` when exposed by the OpenList deployment. |
| `get_task_info` | Get one task by ID via `/api/task/{task_type}/info?tid=...`. Useful when list endpoints are unavailable. |
| `delete_task` | Delete a typed task. Requires `confirm=true`. |
| `retry_task` | Retry a failed typed task. |
| `cancel_task` | Cancel a running typed task. Requires `confirm=true`. |

### Shares

| Tool | Description |
|---|---|
| `create_share` | Create a share link. |
| `list_shares` | List share links. |
| `cancel_share` | Disable a share link. Requires `confirm=true`. |
| `delete_share` | Permanently delete a share link. Requires `confirm=true`. |

> **Note on `names` parameter**: The `copy`, `move`, and `remove` tools use comma-separated file names. If a filename contains a comma, the tool cannot distinguish it — rename the file before operation.

### Advanced

| Tool | Description |
|---|---|
| `offline_download` | Download a file from a remote URL directly to the OpenList server. Supports aria2, Transmission, qBittorrent. |
| `decompress_archive` | Decompress archives (zip, rar, 7z, tar.gz, etc.) on the server. |
| `list_archive_files` | List files inside an archive without extracting it. |
| `list_download_tools` | List available download tools configured on the OpenList server. |

## Integration tests

```bash
export OPENLIST_URL="https://your-openlist-instance.example.com"
export OPENLIST_USERNAME="your_username"
export OPENLIST_PASSWORD="your_password"
export OPENLIST_TEST_DIR="/"
PYTHONPATH=src python3 scripts/live_integration.py
```

The integration test creates a temporary directory under `OPENLIST_TEST_DIR` and removes it after the test. It never prints the password or token.

More details:

- [Live OpenList testing](docs/live-testing.md)
- [OpenList API compatibility notes](docs/api-compatibility.md)

## Notes

- Search support depends on the OpenList backend/storage. Some servers return `search not available`.
- Some task list endpoints may differ between OpenList versions and deployments; `get_task_info` is the most reliable way to inspect a known task ID.
- Destructive tools require an explicit `confirm=true` parameter to reduce accidental operations by AI agents.

---

## Changelog

### v0.2.7

- **`list_download_tools`**: New tool to query available offline download tools (aria2, Transmission, qBittorrent, etc.) configured on the server.
- **`offline_download`**: Docstring updated to document all supported tools.
- **`validate_path` fix**: Component-level `..` detection — no longer rejects legitimate filenames like `backup..2024.tar.gz`.
- **Auto TOTP**: New `OPENLIST_TOTP_SECRET` environment variable for automatic TOTP code generation during 2FA login. When configured, the server generates TOTP codes automatically — no manual input needed. (PR #2 by @chung1912)
- **Startup guide**: Updated to reflect 32 tools.

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
