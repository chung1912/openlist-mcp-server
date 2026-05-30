# Repository Structure Review

## Current layout

```text
src/openlist_mcp/      MCP server, config, client, and tool modules
tests/                 Unit tests grouped by source/tool domain
scripts/               Manual and live OpenList smoke-test scripts
docs/                  Review notes, live testing, and API compatibility docs
.github/workflows/     CI and release workflows
```

## Changes made in this cleanup

- Moved manual live scripts out of the repository root and into `scripts/`.
- Renamed live scripts so they no longer look like pytest unit tests.
- Replaced stale `admin/task` smoke-test usage with typed task API paths.
- Split the large tool behavior test file into focused files:
  - `tests/test_fs_tools.py`
  - `tests/test_task_tools.py`
  - `tests/test_transfer_tools.py`
  - `tests/test_advanced_tools.py`
- Added shared test fixtures in `tests/conftest.py`.
- Added live testing and API compatibility documentation.
- Updated CI to lint, format-check, and compile `src/`, `tests/`, and `scripts/`.

## Current assessment

The repository is no longer root-script-heavy, and test ownership is clearer. The
source tool modules still follow a practical domain split:

- `fs.py` contains filesystem operations.
- `transfer.py` contains upload and download operations.
- `task.py` contains task operations.
- `share.py` contains share operations.
- `advanced.py` contains cross-cutting advanced operations.

`fs.py` is the largest module. It is still acceptable because the functions share
the same OpenList filesystem API surface, but future growth should be watched.

## Recommended next refactors

Do these only when new features make the current modules harder to maintain:

1. Split archive helpers out of `advanced.py` into `tools/archive.py`.
2. Split offline-download helpers out of `advanced.py` into `tools/download.py`.
3. Move repeated safety/path checks into a dedicated helper module if duplication
   grows beyond the current simple validators.
4. Add a release checklist before bumping from `0.2.x` to `0.3.x`.

## Verification used

Run these before merging structural changes:

```bash
python -m ruff check src tests scripts
python -m ruff format --check src tests scripts
python -m compileall -q src tests scripts
PYTHONPATH=src python -m pytest tests -q
python -m mypy src/openlist_mcp --ignore-missing-imports
```
