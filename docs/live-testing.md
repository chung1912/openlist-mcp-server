# Live OpenList Testing

This project has two test layers:

- Unit tests in `tests/` use fake clients and do not call a real OpenList server.
- Live smoke scripts in `scripts/` call a real OpenList server using environment variables.

## Required environment

Set these variables before running a live script:

```bash
export OPENLIST_URL="https://your-openlist.example.com"
export OPENLIST_USERNAME="your_username"
export OPENLIST_PASSWORD="your_password"
export OPENLIST_TEST_DIR="/mcp-dev-test"
```

For Windows PowerShell:

```powershell
$env:OPENLIST_URL = "https://your-openlist.example.com"
$env:OPENLIST_USERNAME = "your_username"
$env:OPENLIST_PASSWORD = "your_password"
$env:OPENLIST_TEST_DIR = "/mcp-dev-test"
```

Use a dedicated test directory when possible. Avoid running live write tests against `/`
or against user data directories.

## Scripts

Run a basic directory listing:

```bash
PYTHONPATH=src python scripts/explore_openlist.py
```

Run a live integration smoke test:

```bash
PYTHONPATH=src python scripts/live_integration.py
```

Check whether the typed task list endpoint is available on the target server:

```bash
PYTHONPATH=src python scripts/check_task_api.py
```

## What the integration script does

`scripts/live_integration.py` verifies:

- login succeeds without printing the token
- file listing works for `OPENLIST_TEST_DIR`
- a temporary folder can be created and fetched
- public settings are readable
- share listing is reachable
- typed offline download task listing is reachable

The script creates a folder named `mcp-test-<timestamp>` under `OPENLIST_TEST_DIR`
and attempts to delete it during cleanup.

## Safety controls

The MCP server supports these environment-level safety controls:

- `OPENLIST_READONLY=true` blocks write and high-impact tools.
- `OPENLIST_ALLOWED_PATHS=/mcp-dev-test,/public` restricts OpenList path operations.
- `OPENLIST_LOCAL_UPLOAD_ROOTS=/safe/local/path` restricts local files that can be uploaded.

Do not use production admin credentials for routine live testing. Use a test account
with the minimum OpenList permissions required for the scenario.
