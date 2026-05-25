# 维护者指南

## 项目维护团队

- **当前维护者**: SOLO
- **原创建者**: hbestm

## 维护计划

### Phase 1: 项目熟悉与基础设施（第1-2周）
- [x] 完整阅读代码库，理解架构和实现细节
- [x] 设置本地开发环境，运行测试确保一切正常
- [x] 审查现有 issue 和 PR，建立问题追踪
- [ ] 更新 README，添加维护者信息和贡献指南

### Phase 2: 稳定性与质量保障（第3-6周）
- [ ] 添加 CI/CD 工作流（GitHub Actions）
- [ ] 增加单元测试覆盖率，补充边界情况测试
- [ ] 添加代码质量工具（linting、type checking）
- [ ] 审查错误处理和日志记录，增强健壮性

### Phase 3: 功能完善与优化（第7-10周）
- [ ] 收集用户反馈，确定优先级功能
- [ ] 实现高优先级功能增强
- [ ] 性能优化和代码重构

### Phase 4: 社区与文档（持续）
- [ ] 完善中英文文档，添加使用示例
- [ ] 建立 issue 模板和 PR 模板
- [ ] 发布版本更新日志

## 架构概览

```
openlist-mcp-server/
├── src/openlist_mcp/
│   ├── server.py          # MCP 服务器主入口，注册所有工具
│   ├── client.py          # OpenList API 客户端，处理 JWT 认证
│   ├── config.py          # 环境变量配置管理
│   └── tools/
│       ├── auth.py        # 认证相关工具（login, get_public_settings）
│       ├── fs.py          # 文件系统工具（list, get, search, mkdir, rename, copy, move, remove）
│       ├── transfer.py    # 文件传输工具（upload, download_url）
│       ├── task.py        # 任务管理工具（list, delete, retry, cancel）
│       └── share.py       # 分享管理工具（create, list, cancel, delete）
```

## 关键设计决策

1. **自动认证**: 客户端在首次需要认证时自动登录，token 过期后自动重试
2. **安全确认**: 破坏性操作（delete, cancel）需要显式 `confirm=true` 参数
3. **错误处理**: 统一的 `OpenListError` 异常类，包含 HTTP 状态码和友好错误消息
4. **异步设计**: 所有 API 调用使用 `httpx.AsyncClient` 和 `async/await`

## 发布流程

1. 更新 `pyproject.toml` 中的版本号
2. 更新 `CHANGELOG.md`
3. 创建 git tag: `git tag v0.x.x`
4. 推送 tag: `git push origin v0.x.x`
5. GitHub Actions 会自动构建并发布到 PyPI（待配置）

## 代码规范

- Python 3.10+ 类型注解
- 使用 `from __future__ import annotations` 支持延迟类型评估
- 遵循 PEP 8 风格指南
- 所有公共函数和类必须有 docstring

## 测试策略

- 单元测试：使用 `pytest`，位于 `tests/` 目录
- 集成测试：`test_integration.py` 需要真实 OpenList 实例
- 目标测试覆盖率：> 80%
