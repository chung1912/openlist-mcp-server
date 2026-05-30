# OpenList MCP Server — AI Agent Guide

> Copy this entire document and paste it to your AI assistant (Claude, etc.) to teach it how to install, configure, and use the OpenList MCP Server.

---

## Overview

OpenList MCP Server is a tool that lets AI agents manage files on an [OpenList](https://github.com/OpenListTeam/OpenList) instance. OpenList is a self-hosted file management platform that supports local storage, cloud drives (OneDrive, Google Drive, etc.), and more.

**32 tools available** across 7 categories:
- Browse: `list_files`, `list_dirs`, `get_file_info`, `search_files`
- Manage: `create_folder`, `rename`, `batch_rename`, `copy`, `move`, `remove`, `recursive_move`
- Transfer: `upload_file`, `upload_local_file`, `get_download_url`
- Auth: `login`, `get_public_settings`, `get_me`, `get_capabilities`, `logout`
- Tasks: `list_tasks`, `get_task_info`, `retry_task`, `cancel_task`, `delete_task`
- Shares: `create_share`, `list_shares`, `cancel_share`, `delete_share`
- Advanced: `offline_download`, `decompress_archive`, `list_archive_files`, `list_download_tools`

---

## For the Human: How to Install

Tell the user to follow these steps:

### 1. Prerequisites
- Python 3.10+
- An OpenList server (self-hosted, running and accessible)
- OpenList admin credentials (username + password)

### 2. Install the MCP Server

```bash
# Option A: From GitHub
git clone https://github.com/hbestm/openlist-mcp-server.git
cd openlist-mcp-server
python3 -m venv venv
source venv/bin/activate
pip install -e .

# Option B: From source archive
# Download ZIP from https://github.com/hbestm/openlist-mcp-server
unzip openlist-mcp-server-main.zip
cd openlist-mcp-server-main
pip install -e .
```

### 3. Verify

```bash
openlist-mcp
# Should print: "OpenList MCP Server v0.2.7 installed successfully."
```

### 4. Configure for Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "openlist": {
      "command": "openlist-mcp",
      "env": {
        "OPENLIST_URL": "https://your-openlist.example.com",
        "OPENLIST_USERNAME": "admin",
        "OPENLIST_PASSWORD": "your_password",
        "OPENLIST_READONLY": "false",
        "OPENLIST_ALLOWED_PATHS": "",
        "OPENLIST_TOTP_SECRET": "your_totp_secret"
      }
    }
  }
}
```

> `OPENLIST_TOTP_SECRET` is optional — only needed if the OpenList account has 2FA enabled.

Linux: `~/.config/Claude/claude_desktop_config.json`
macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
Windows: `%APPDATA%\Claude\claude_desktop_config.json`

### 5. Optional: Enable local file uploads

```bash
export OPENLIST_LOCAL_UPLOAD_ROOTS="/tmp:/path/to/allowed/dirs"
```

### 6. Optional: Restrict AI access

```bash
export OPENLIST_READONLY="true"
export OPENLIST_ALLOWED_PATHS="/mcp-dev-test,/public"
```

`OPENLIST_READONLY=true` blocks write/high-impact tools. `OPENLIST_ALLOWED_PATHS`
restricts OpenList path operations to comma-separated path prefixes.

### 7. Optional: Enable aria2 for faster offline downloads

```bash
# On the OpenList server:
apt install aria2
aria2c --enable-rpc --rpc-listen-all=true --rpc-allow-origin-all -D
```

### 8. Optional: Auto 2FA with TOTP

If the OpenList account has 2FA enabled, set the TOTP secret so the MCP server generates codes automatically:

```bash
export OPENLIST_TOTP_SECRET="your_totp_secret_key"
```

No manual TOTP entry needed after this — the server handles it.

---

## For the AI: How to Use the Tools

### First Step: Always Login First

```python
# The MCP server auto-logs in on first API call.

# If 2FA is enabled and OPENLIST_TOTP_SECRET is configured,
# the TOTP code is generated automatically — no manual input needed.
# Just call login() without arguments:
login()

# If 2FA is enabled but no TOTP secret is configured,
# ask the user for their TOTP code:
login(otp_code="123456")
```

### File Operations

```python
# List files in a directory
list_files(path="/")

# Get details about a specific file or folder
get_file_info(path="/downloads/report.pdf")

# Search for files by keyword
search_files(path="/", keyword="report")

# Create a folder
create_folder(path="/projects/new-project")

# Rename a file or folder
rename(path="/projects/old-name", name="new-name")

# Copy files to another directory
copy(src_dir="/photos", dst_dir="/backup/photos", names=["vacation.jpg", "family.png"])

# Move files to another directory
move(src_dir="/downloads", dst_dir="/archive", names=["file1.pdf", "file2.txt"])

# Delete files or folders (requires confirm=true)
remove(directory="/tmp", names=["old-file.txt"], confirm=True)

# Recursively move an entire directory tree
recursive_move(src_dir="/projects/old", dst_dir="/projects/new")
```

> **Safety note**: `remove` requires `confirm=True`. The AI must explain what will be deleted and get user approval before passing `confirm=True`.

### File Transfer

```python
# Upload a file from a remote URL (server downloads it)
offline_download(url="https://example.com/file.pdf", path="/downloads")
# Default download tool is aria2. Specify a different tool:
offline_download(url="https://...", path="/downloads", tool="aria2")

# Upload file content from the conversation
upload_file(path="/docs", file_name="note.txt", file_content_base64="base64_encoded_content")

# Upload a file from the local machine (if enabled by admin)
upload_local_file(local_path="/home/user/report.pdf", remote_dir="/docs")

# Get a direct download URL for sharing
get_download_url(path="/shared/file.zip")
```

### Archive Operations

```python
# Decompress an archive (zip, rar, 7z, tar.gz, etc.)
decompress_archive(
    src_dir="/downloads",
    names="data.zip",
    dst_dir="/downloads/data",
    overwrite=True,
    put_into_new_dir=True
)
```

### Download Tools

```python
# List available download tools on the OpenList server
list_download_tools()
# Returns: ["aria2", "Transmission", "qBittorrent", ...]

# Download with a specific tool
offline_download(url="https://example.com/file.iso", path="/downloads", tool="Transmission")
offline_download(url="https://example.com/file.zip", path="/downloads", tool="qBittorrent")
```

### Authentication

```python
# Login (auto-handled, only use for explicit re-login or 2FA)
login(otp_code="")  # Provide TOTP code if 2FA is enabled

# Get current user info (check your identity and permissions)
get_me()

# Get public server settings
get_public_settings()

# Logout (invalidate current token)
logout()
```

### Task Management

```python
# List typed async tasks when the OpenList deployment exposes list endpoints
list_tasks(task_type="offline_download", status="undone")
list_tasks(task_type="offline_download", status="done")

# Get one task by ID. This is the most reliable way to check a task returned by offline_download.
get_task_info(task_id="task_id_here", task_type="offline_download")

# Retry a failed task
retry_task(task_id="task_id_here", task_type="offline_download")

# Cancel a running task
cancel_task(task_id="task_id_here", task_type="offline_download", confirm=True)

# Delete a task record
delete_task(task_id="task_id_here", task_type="offline_download", confirm=True)
```

### Share Management

```python
# Create a share link for a file or folder
create_share(path="/shared/file.pdf")

# List all existing share links
list_shares()

# Cancel a share
cancel_share(share_key="share_key_here", confirm=True)

# Delete a share
delete_share(share_key="share_key_here", confirm=True)
```

---

## Quick Prompt Examples

Copy and paste these prompts to your AI assistant:

| What you want to do | Say to the AI |
|--------------------|--------------|
| **下载文件** | "帮我把这个文件下载到 downloads 目录：https://example.com/file.zip" |
| **用指定工具下载** | "用 Transmission 下载这个 BT 链接：magnet:?xt=..." |
| **查可用的下载工具** | "看看我这个服务器上有哪些下载工具可以用" |
| **BT 下载** | "帮我把这个种子下载下来" |
| **解压文件** | "把 downloads 目录下的 data.zip 解压到 data 文件夹" |
| **下载+解压** | "把这个压缩包下载下来然后解压到项目目录" |
| **批量操作** | "把 downloads 目录里所有 .tmp 文件删掉" |
| **查自己是谁** | "我现在是以什么身份登录的？" |
| **查存储空间** | "看看我这个 OpenList 服务器上挂载了哪些存储" |

## Common Workflows (AI Recommendations)

### Workflow 1: Download + Extract Archive

When the user says "download this dataset and extract it":

```python
# Step 1: Offline download the archive
offline_download(url="https://example.com/dataset.zip", path="/downloads")
# Inform the user: "I've started downloading the archive. It will be saved to /downloads."

# Step 2: Wait for download to complete. Use the task ID returned by offline_download.
get_task_info(task_id="task_id_here", task_type="offline_download")

# Step 3: Decompress
decompress_archive(
    src_dir="/downloads",
    names="dataset.zip",
    dst_dir="/downloads/dataset",
    put_into_new_dir=True
)
```

### Workflow 2: Organize Files

When the user says "clean up my downloads folder":

```python
# Step 1: List the directory
files = list_files(path="/downloads")

# Step 2: Identify files to organize (by date, type, etc.)
# Step 3: Move or remove as appropriate
move(src_dir="/downloads", dst_dir="/archive/2024", names=["old_report.pdf"])

# For large directories, use recursive_move
recursive_move(src_dir="/downloads/messy-folder", dst_dir="/organized/messy-folder")
```

### Workflow 3: Share Files

When the user says "share this file with someone":

```python
# Step 1: Create a share link
share = create_share(path="/shared/report.pdf")
# Step 2: Inform the user of the share link
# "Here's your share link: https://your-openlist.com/s/abc123"
```

---

## Important Notes

1. **Not all features work on all OpenList versions.** OpenList v4.2.2 has a bug where `POST /api/fs/recursive_move` returns an error. The MCP server automatically falls back to `rename` (same directory) or `move` + `rename` (cross-directory) on affected versions.

2. **`search_files` requires search indexing to be enabled** on the OpenList server. If search is disabled, the tool returns a 404.

3. **`offline_download`** supports multiple download tools: `aria2` (default, supports https/http/magnet), `Transmission` (BitTorrent/HTTP), `qBittorrent` (BitTorrent/HTTP), and `SimpleHttp` (http only, may not work on all versions). Run `list_download_tools` to see what's available on the server.

4. **`upload_local_file` is DISABLED by default.** It requires the admin to set `OPENLIST_LOCAL_UPLOAD_ROOTS` environment variable.

5. **All paths start with `/`**, representing the OpenList storage root. The actual filesystem path depends on the storage backend configuration.

6. **The `names` parameter** in `copy`, `move`, and `remove` accepts both a comma-separated string (`"file1.txt,file2.pdf"`) and a JSON array of strings.

7. **Token expiry is handled automatically.** The server re-logs in when it receives a 401 response.

---

## Troubleshooting

| Symptom | Likely Cause | Solution |
|---------|-------------|----------|
| "Login failed: invalid username or password" | Wrong credentials | Ask the user to verify OPENLIST_USERNAME and OPENLIST_PASSWORD |
| "Connection refused" | OpenList server not running | Ask the user to start their OpenList server |
| "Tool not found" when calling offline_download | Selected tool not configured on OpenList server | Run `list_download_tools` to see available tools; install missing ones on the server |
| "Auto-generated TOTP code was rejected" | Wrong OPENLIST_TOTP_SECRET value | Ask the user to verify the TOTP secret in their authenticator app |
| "search not available" | Search indexing disabled | Inform the user, suggest enabling search in OpenList settings |
| "object not found" on recursive_move | OpenList v4.2.2 backend bug | Fallback to rename works automatically; inform user if concerned |
| "upload_local_file" rejected | OPENLIST_LOCAL_UPLOAD_ROOTS not set | Ask the user to set the env var to allowed directories |
| ".env" file not loading | python-dotenv not installed | Ask the user to run `pip install python-dotenv` |
| Offline download task stuck | aria2 RPC not running on the server | Ask the user to start aria2 RPC daemon on the OpenList server |
| "Guest user is disabled" | Token expired or invalid | The server will auto-re-login on next API call — no action needed |
| Transmission/qBittorrent not working | Download tool not properly configured | Check port, credentials, and service status on the OpenList server |
| HTTP warning about plain text | Using HTTP instead of HTTPS | Inform user to use HTTPS in production; safe on local network |
