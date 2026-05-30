# OpenList API Compatibility Notes

This MCP server calls OpenList's HTTP API through `OpenListClient`. Most tools are
thin wrappers over the matching OpenList endpoint, with input validation and optional
MCP-side safety controls.

## Version-sensitive areas

Some OpenList deployments expose task APIs differently. The MCP server uses typed
task endpoints:

- `POST /api/task/{task_type}/{status}` for `list_tasks`
- `POST /api/task/{task_type}/info?tid=...` for `get_task_info`
- `POST /api/task/{task_type}/retry?tid=...` for `retry_task`
- `POST /api/task/{task_type}/cancel?tid=...` for `cancel_task`
- `POST /api/task/{task_type}/delete?tid=...` for `delete_task`

Supported task types are:

- `upload`
- `copy`
- `offline_download`
- `offline_download_transfer`
- `decompress`
- `decompress_upload`

Supported list statuses are `done` and `undone`.

## HTML task responses

If a task list call returns HTML instead of JSON, the target OpenList deployment is
serving a web page or fallback route for that API path. In that case:

- `get_task_info` may still work when the caller has a known task id.
- `list_tasks` returns a structured compatibility error instead of leaking raw HTML.
- The deployment should be checked against its OpenList version, reverse proxy rules,
  and enabled task features.

## Compatibility expectations

The unit tests assert request shapes for the endpoints this project wraps. Live
compatibility still depends on the target OpenList server because storage drivers,
admin permissions, offline download providers, and task endpoints can differ by
deployment.

When adding a new tool:

1. Confirm the endpoint exists in the current OpenList API.
2. Add validation for path, file name, pagination, or destructive confirmation inputs.
3. Add a fake-client unit test that checks request method, path, params, and JSON body.
4. Add or update a live smoke script only when the endpoint can be exercised safely.
5. Document version or deployment caveats here.
