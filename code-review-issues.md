# OpenList MCP Server 代码审查问题报告

**审查版本**: `21bfa7c`（含 `05b4d42` 修复）  
**工具数**: 64  
**审查日期**: 2026-05-31

---

## 修复状态

| 问题 | 状态 |
|------|------|
| 🔴 `OpenListError` 未导入 | ✅ 已修复 |
| 🔴 `_human_size()` 未定义 | ✅ 已修复 |
| 🔴 `task.py` json 参数类型不匹配 | ✅ 已修复 |
| 🟡 7 个 mypy 错误 | ✅ 全部修复（0 error） |
| 🟢 8 个文件格式 | ✅ 全部已格式化 |

---

## 🔴 运行时崩溃（3 个）

### 1. `advanced.py` — `OpenListError` 未导入

**文件**: `src/openlist_mcp/tools/advanced.py:305`

```python
except OpenListError:
```

`OpenListError` 在当前模块未 import，调用该段逻辑时会触发 `NameError: name 'OpenListError' is not defined`。

**修复**: 在文件顶部添加 `from ..client import OpenListError`。

---

### 2. `advanced.py` — `_human_size()` 函数未定义

**文件**: `src/openlist_mcp/tools/advanced.py:324,350`

```python
# line 324
_human_size                    # 无意义的表达式，不是函数调用
key = f"size:{size}"

# line 350
"size_human": _human_size(v[0]["size"]),
```

`_human_size()` 函数在模块中未定义，调用时触发 `NameError`。第 324 行仅为表达式 `_human_size`（无括号调用），属于无意义代码。

**修复**: 补全 `_human_size()` 函数或删除相关引用。

---

### 3. `task.py` — `json=` 参数类型不匹配

**文件**: `src/openlist_mcp/tools/task.py:197,227,253`

```python
data = await client.request("POST", f"task/{task_type}/delete", json=task_ids)
```

`OpenListClient.request()` 的 `json` 参数类型为 `dict[str, Any] | None`，但此处传入 `list[str]`，导致 `mypy` 报错且运行时请求体格式错误。

**修复**: 改为 `json={"ids": task_ids}`。

---

## 🟡 静态分析错误

### Ruff Lint（19 个）

| 数量 | 类型 | 文件 |
|------|------|------|
| 1 | `F821` Undefined name `OpenListError` | `advanced.py:305` |
| 1 | `F821` Undefined name `_human_size` | `advanced.py:324,350` |
| 1 | `B018` Useless expression `_human_size` | `advanced.py:324` |
| 1 | `F841` Unused variable `addr` | `advanced.py:59` |
| 1 | `F401` Unused import `__version__` | `server.py:23` |
| 1 | `F401` Unused import `validate_pagination` | `admin.py:14` |
| 2 | `I001` Import block unsorted | `server.py`, `advanced.py` |
| 1 | `SIM108` Use ternary operator | `fs.py:659` |
| 9 | `F841` Unused variable `result` | `test_*_tools.py` (多文件) |

### Mypy（7 个）

| 数量 | 类型 | 文件 |
|------|------|------|
| 3 | `arg-type` json 参数类型不匹配 | `task.py:197,227,253` |
| 1 | `arg-type` `_is_private_ip` 参数类型 | `advanced.py:82` |
| 1 | `name-defined` `OpenListError` | `advanced.py:305` |
| 2 | `name-defined` `_human_size` | `advanced.py:324,350` |

### Ruff Format（8 个文件需格式化）

`admin.py`, `advanced.py`, `auth.py`, `fs.py`, `tests/conftest.py`, `test_admin_tools.py`, `test_share_tools.py`, `test_task_tools.py`

---

## 汇总

| 严重度 | 数量 |
|--------|------|
| 🔴 运行时崩溃 | 3 |
| 🟡 Lint/类型错误 | 26 |
| 🟢 格式问题 | 8 文件 |
