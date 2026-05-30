# OpenList MCP Server 中文

<p align="center">
  <img src="docs/og-image.png" alt="OpenList MCP Server" width="800">
</p>

<p align="center">
  <a href="README.md">English</a> · <a href="README-zh.md">中文</a>
</p>

---

[OpenList](https://github.com/OpenListTeam/OpenList) 的 MCP 服务端。[OpenList](https://github.com/OpenListTeam/OpenList) 是一个开源的文件管理系统（类似 Alist）。本服务让支持 MCP 协议的 AI 智能体（Claude、SOLO 等）通过 OpenList REST API 浏览、上传、下载、搜索和管理文件。

```
┌────────────────┐     ┌────────────────────┐     ┌──────────────┐     ┌───────────────┐
│ Claude Desktop │────▶│ openlist-mcp-server │────▶│ OpenList API │────▶│ 存储后端 (S3, │
│   (或 SOLO)    │ MCP │   (本项目)          │ HTTP │   (你的服务器)│     │  SMB, 本地,   │
└────────────────┘     └────────────────────┘     └──────────────┘     │  ...)         │
                                                                        └───────────────┘
```

## 功能特性

- **文件浏览** — 列出目录、查看文件详情、搜索文件
- **文件管理** — 创建目录、重命名、复制、移动、删除
- **文件传输** — Base64 上传文件、上传 MCP Server 可访问的本地文件、获取下载链接
- **分享管理** — 创建、列出、取消、删除分享链接
- **任务管理** — 查看、重试、取消、删除异步任务
- **自动认证** — JWT 自动登录与 token 过期重试
- **NEW v0.2.5** 双因素认证 (2FA/TOTP)：支持带 OTP 验证码登录
- **NEW v0.2.5** 本地文件上传：新增 `upload_local_file` 工具（默认禁用，需配置 `OPENLIST_LOCAL_UPLOAD_ROOTS`）
- **NEW v0.2.6** 高级功能：离线下载、在线解压、递归移动

## 环境要求

- **Python 3.10+**（检查版本：`python3 --version`）
- **一个运行中的 OpenList 实例**（本服务是 OpenList 的客户端，不是独立服务）

## 快速开始

### 给 AI 助手使用

将 [`AI_GUIDE.md`](AI_GUIDE.md) 的内容复制粘贴给你的 AI 助手（Claude 等），AI 就能知道如何安装、配置和使用全部 26 个工具。

### 给人类用户使用

按以下步骤手动安装。

### 从 GitHub 源码安装

```bash
git clone https://github.com/hbestm/openlist-mcp-server.git
cd openlist-mcp-server

# （推荐）创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

pip install -e .
```

### 从源码压缩包安装

如果你不使用 Git，可以在 GitHub 仓库页面点击 **Code → Download ZIP** 下载源码压缩包，然后：

```bash
unzip openlist-mcp-server-main.zip
cd openlist-mcp-server-main
pip install -e .
```

> 注意：GitHub Releases 页面可能只有标签；除非额外上传了 release assets，否则那里不一定有可下载的 zip 发布包。没有 release zip 时，请使用上面的源码安装方式。

### 验证安装

```bash
openlist-mcp
# 期望输出：
# "OpenList MCP Server v0.2.7 installed successfully.
#  Set OPENLIST_URL, OPENLIST_USERNAME, and OPENLIST_PASSWORD to get started."
```

## 配置

### 环境变量

```bash
export OPENLIST_URL="https://你的-openlist-地址.com"
export OPENLIST_USERNAME="你的用户名"
export OPENLIST_PASSWORD="你的密码"

# 必需：upload_local_file 默认禁用，设置此变量后才可启用
export OPENLIST_LOCAL_UPLOAD_ROOTS="/tmp:/path/to/uploads"
```

也可以使用 `.env` 文件（从 `.env.example` 复制）：

```bash
cp .env.example .env
# 编辑 .env 填入你的凭据
pip install python-dotenv   # .env 支持需要此包
```

服务启动时如果安装了 `python-dotenv`，会自动加载 `.env` 文件。**切勿将 `.env` 提交到 Git 仓库**，项目自带的 `.gitignore` 已排除该文件。

### 安全提醒

- **生产环境请使用 HTTPS**，否则密码会在网络上明文传输。
- **保护好 MCP 配置文件**：
  - Linux/macOS：`chmod 600 claude_desktop_config.json`
  - Windows：右键文件 → 属性 → 安全 → 仅保留自己的权限。
- **尽量限制本地文件上传目录**。`upload_local_file` 默认禁用，设置 `OPENLIST_LOCAL_UPLOAD_ROOTS` 配置一个或多个允许目录后才可启用。

## 使用方式

### Claude Desktop

1. 打开 Claude Desktop → 设置 → **MCP Servers**。
2. 添加新服务器：

```json
{
  "mcpServers": {
    "openlist": {
      "command": "openlist-mcp",
      "env": {
        "OPENLIST_URL": "https://你的-openlist-地址.com",
        "OPENLIST_USERNAME": "你的用户名",
        "OPENLIST_PASSWORD": "你的密码"
      }
    }
  }
}
```

> **配置文件路径：**
> - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
> - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
> - Linux: `~/.config/Claude/claude_desktop_config.json`

3. **重启 Claude Desktop** 使配置生效。
4. 试试这个 prompt：*"列出我 OpenList 根目录的文件。"*

### 快速上手 Prompt 示例

| 目标 | 可以说 |
|------|--------|
| 列根目录 | "列出我 OpenList 上的文件。" |
| 搜索文件 | "在 OpenList 上搜索包含'报告'的文件。" |
| 上传文件 | "把这个文件上传到 OpenList 的 /documents 目录。"（Claude 会问你要哪个文件） |
| 获取下载链接 | "给我 /documents/report.pdf 的下载链接。" |
| 创建目录 | "在 /documents 下创建一个叫 archive 的文件夹。" |

### 直接 stdio 运行（调试用）

```bash
export OPENLIST_URL="https://你的-openlist-地址.com"
export OPENLIST_USERNAME="你的用户名"
export OPENLIST_PASSWORD="你的密码"
openlist-mcp
```

### SOLO / 其他 MCP 客户端

配置格式与其他 MCP 客户端通用：

```json
{
  "mcpServers": {
    "openlist": {
      "command": "openlist-mcp",
      "env": {
        "OPENLIST_URL": "https://你的-openlist-地址.com",
        "OPENLIST_USERNAME": "你的用户名",
        "OPENLIST_PASSWORD": "你的密码"
      }
    }
  }
}
```

## 故障排查

| 问题 | 可能原因 | 解决方案 |
|------|---------|----------|
| `OPENLIST_URL is required` | 未设置环境变量 | 设置 `OPENLIST_URL`、`OPENLIST_USERNAME`、`OPENLIST_PASSWORD` |
| `password is incorrect` | 密码错误 | 检查 OpenList 的用户名和密码 |
| `Connection refused` | OpenList 未启动 | 检查 OpenList 服务器是否运行并可访问 |
| 安装后找不到命令 | PATH 未更新或虚拟环境未激活 | 重新激活虚拟环境或重装 |
| MCP 客户端显示"已断开" | 需要重启 Claude Desktop | 添加配置后重启 Claude Desktop |
| `search not available` | 搜索索引未开启或后端不支持搜索 | 先在 OpenList 管理后台开启搜索/索引功能，并确认存储后端支持搜索 |
| `2FA code is required` | 开启了双因素认证 | 调用 `login(otp_code="你的验证码")` 传入认证器 App 的 TOTP 码 |
| `Invalid 2FA code` | TOTP 验证码错误或过期 | 从认证器 App 生成新码后重新调用 login 传入正确的 `otp_code` |

**开启调试日志：**

```bash
OPENLIST_URL=... OPENLIST_USERNAME=... OPENLIST_PASSWORD=... openlist-mcp 2>&1 | head -20
```

## 卸载

```bash
pip uninstall openlist-mcp-server -y
rm -rf venv
```

## 工具列表

### 本地文件上传说明

`upload_local_file` 会从 MCP Server 进程可读取的本地路径上传文件。它适合本地智能体或服务端部署场景。

**安全考虑：该工具默认禁用。** 你必须设置 `OPENLIST_LOCAL_UPLOAD_ROOTS` 环境变量，用系统路径分隔符配置一个或多个允许读取的父目录（Linux/macOS 使用 `:`，Windows 使用 `;`）。未设置该变量时，所有本地上传请求都会被拒绝。

如果 MCP Server 不能访问用户本地文件系统，请改用 `upload_file` 的 Base64 上传方式。

### 认证与公开接口

| 工具 | 说明 |
|---|---|
| `login` | 使用配置的凭据登录。如果账户已开启 2FA，可传入 `otp_code` 参数。Token 不会被 MCP Server 打印。 |
| `get_public_settings` | 无需认证获取公开设置。 |

### 文件系统

| 工具 | 说明 |
|---|---|
| `list_files` | 列出目录中的文件和文件夹。 |
| `get_file_info` | 获取文件或文件夹详情。 |
| `search_files` | 按关键词搜索文件。是否可用取决于 OpenList 后端存储。 |
| `create_folder` | 创建目录。 |
| `rename` | 重命名文件或文件夹。 |
| `copy` | 复制文件/文件夹到其他目录。 |
| `move` | 移动文件/文件夹到其他目录。 |
| `remove` | 删除文件/文件夹。需传 `confirm=true`。 |

### 文件传输

| 工具 | 说明 |
|---|---|
| `get_download_url` | 获取文件的直接/代理下载链接。 |
| `upload_file` | 上传 Base64 编码的文件内容。 |
| `upload_local_file` | 上传 MCP Server 进程可读取的本地文件路径。 |

### 任务管理

| 工具 | 说明 |
|---|---|
| `list_tasks` | 列出异步任务。接口可用性取决于 OpenList 版本。 |
| `delete_task` | 删除任务。需传 `confirm=true`。 |
| `retry_task` | 重试失败的任务。 |
| `cancel_task` | 取消运行中的任务。需传 `confirm=true`。 |

### 分享管理

| 工具 | 说明 |
|---|---|
| `create_share` | 创建分享链接。 |
| `list_shares` | 列出分享链接。 |
| `cancel_share` | 禁用分享链接。需传 `confirm=true`。 |
| `delete_share` | 永久删除分享链接。需传 `confirm=true`。 |

> **关于 `names` 参数**：`copy`、`move`、`remove` 工具使用逗号分隔文件名。如果文件名本身包含逗号，工具无法区分——操作前请先重命名该文件。

## 集成测试

```bash
export OPENLIST_URL="https://你的-openlist-地址.com"
export OPENLIST_USERNAME="你的用户名"
export OPENLIST_PASSWORD="你的密码"
export OPENLIST_TEST_DIR="/"
PYTHONPATH=src python3 test_integration.py
```

测试脚本会在 `OPENLIST_TEST_DIR` 下创建临时目录，测试完成后自动删除。不会输出密码或 Token。

## 注意事项

- 搜索功能取决于 OpenList 后端存储支持，部分服务器可能返回 `search not available`。
- 管理后台任务接口可能因 OpenList 版本和部署方式不同有所差异。
- 所有破坏性操作都需要显式传 `confirm=true` 参数，防止 AI 智能体误操作。

---

## 更新日志

### v0.2.7

- **`list_download_tools`**：新增工具，查询 OpenList 服务端配置的可用下载工具（aria2、Transmission、qBittorrent 等）。
- **`offline_download`**：工具说明更新，列出所有支持的下载工具。
- **`validate_path` 修复**：改为组件级精确检测 `..`，不再误杀 `backup..2024.tar.gz` 等合法文件名。
- **启动指南**：更新为 27 个工具。

### v0.2.6

- **高级工具模块**：新增 `tools/advanced.py` 模块。
- **`offline_download`**：从远程 URL 直接下载文件到 OpenList 服务端（需服务端已配置 aria2 等下载工具）。
- **`decompress_archive`**：服务端在线解压压缩文件（zip、rar、7z、tar.gz 等）。
- **`get_me`**：获取当前登录用户信息（用户名、角色、2FA 状态、权限）。
- **`logout`**：登出并使当前认证 token 失效。
- **`recursive_move`**：递归移动整个目录树到新位置，无需逐个列出文件名。
- **启动指南**：未配置时的使用帮助已更新，列出全部 26 个分类工具。

### v0.2.5

- **双因素认证 (2FA/TOTP)**：`login` 工具现在接受可选的 `otp_code` 参数。如果 OpenList 账户开启了 2FA，智能体会提示用户提供 TOTP 验证码。
- **本地文件上传**：新增 `upload_local_file` 工具，可直接上传本地路径文件，无需 base64 编码。可设置 `OPENLIST_LOCAL_UPLOAD_ROOTS` 限制允许读取的目录。
- **大文件上传优化**：改为异步分块流式上传，不再整文件读入内存。写入超时放宽到 120 秒。
- **安全加固**：Base64 解码异常从 `except Exception` 收窄为 `ValueError, binascii.Error`。增加 `OPENLIST_LOCAL_UPLOAD_ROOTS` 目录限制。
- **发布流程**：移除自动 PyPI 发布。打 tag 后仅创建 GitHub Release 并上传构建产物。
- **版本统一**：`__version__`、`pyproject.toml`、`server.py` 统一为 v0.2.5。`__version__` 改为运行时从包元数据读取。
- **文档修复**：安装说明改为源码方式；`search_files` 备注明确需开启 OpenList 搜索索引。
- **名称校验修复**：`validate_name()` 现在正确处理包含连续双点的文件名（如 `backup..tar.gz`、`..hidden_file`），仅拒绝 `.` 和 `..` 完整目录名。空字符串也会被拒绝。

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

如有 Bug、功能建议或疑问，欢迎[提交 GitHub Issue](https://github.com/hbestm/openlist-mcp-server/issues)。

## License

MIT
