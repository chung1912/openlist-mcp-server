# OpenList MCP Server 中文

<p align="center">
  <img src="docs/og-image.png" alt="OpenList MCP Server" width="800">
</p>

<p align="center">
  <a href="README.md">English</a> · <a href="README-zh.md">中文</a>
</p>

---

[OpenList](https://github.com/OpenListTeam/OpenList) 的 MCP 服务端。让支持 MCP 协议的 AI 智能体（Claude、SOLO 等）通过 OpenList REST API 浏览、上传、下载、搜索和管理文件。

## 功能特性

- **文件浏览** — 列出目录、查看文件详情、搜索文件
- **文件管理** — 创建目录、重命名、复制、移动、删除
- **文件传输** — Base64 上传文件、获取下载链接
- **分享管理** — 创建、列出、取消、删除分享链接
- **任务管理** — 查看、重试、取消、删除异步任务
- **自动认证** — JWT 自动登录与 token 过期重试

## 环境要求

- Python 3.10+
- 一个运行中的 OpenList 实例

## 安装

```bash
cd openlist-mcp-server
pip install -e .
```

## 配置

运行前设置环境变量：

```bash
export OPENLIST_URL="https://你的-openlist-地址.com"
export OPENLIST_USERNAME="你的用户名"
export OPENLIST_PASSWORD="你的密码"
```

**不要将真实凭据提交到仓库**，使用 `.env.example` 作为模板。

## 使用方式

### Claude Desktop / MCP 客户端

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

### 直接 stdio 运行

```bash
openlist-mcp
```

## 工具列表

### 认证与公开接口

| 工具 | 说明 |
|---|---|
| `login` | 使用配置的凭据登录。不会打印 Token。 |
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