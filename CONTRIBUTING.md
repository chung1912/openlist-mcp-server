# 贡献指南

感谢您对 OpenList MCP Server 的兴趣！我们欢迎各种形式的贡献。

## 如何贡献

### 报告问题

如果您发现了 bug 或有功能建议，请通过 [GitHub Issues](https://github.com/hbestm/openlist-mcp-server/issues) 提交。

提交 issue 时请包含：
- 问题的清晰描述
- 复现步骤（如果是 bug）
- 期望行为与实际行为
- 环境信息（Python 版本、操作系统等）

### 提交代码

1. **Fork 仓库** 并克隆到本地
2. **创建分支**: `git checkout -b feature/your-feature-name`
3. **安装开发依赖**:
   ```bash
   pip install -e ".[dev]"
   ```
4. **编写代码** 并添加测试
5. **运行测试**:
   ```bash
   pytest tests/
   ```
6. **提交更改**: `git commit -m "feat: add your feature"`
7. **推送分支**: `git push origin feature/your-feature-name`
8. **创建 Pull Request**

### 代码规范

- 使用 Python 3.10+ 类型注解
- 遵循 PEP 8 风格
- 添加适当的 docstring
- 保持测试覆盖率

### 提交信息规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `test:` 测试相关
- `refactor:` 代码重构
- `chore:` 构建/工具相关

示例：
```
feat: add batch upload support
fix: handle token expiration correctly
docs: update installation guide
```

## 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/hbestm/openlist-mcp-server.git
cd openlist-mcp-server

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 安装开发模式
pip install -e .

# 验证安装
openlist-mcp
```

## 测试

### 运行单元测试
```bash
pytest tests/
```

### 运行集成测试（需要 OpenList 实例）
```bash
export OPENLIST_URL="https://your-openlist.example.com"
export OPENLIST_USERNAME="your_username"
export OPENLIST_PASSWORD="your_password"
python scripts/live_integration.py
```

## 许可证

通过提交贡献，您同意您的代码将在 MIT 许可证下发布。
