"""
End-to-end tests for OpenList MCP Server.

These tests exercise the full MCP tool stack against a real OpenList instance.
They are not run by default — use `pytest -m e2e` to execute.

Required environment variables:
    OPENLIST_URL       - http(s)://your-openlist-instance:port
    OPENLIST_USERNAME  - admin username
    OPENLIST_PASSWORD  - admin password
    OPENLIST_ALLOW_HTTP=true  (required for HTTP URLs)
"""

import asyncio
import json
import os
import time
from pathlib import Path

import pytest

from openlist_mcp.client import OpenListClient

pytestmark = pytest.mark.e2e

SKIP = pytest.mark.skipif(
    not os.environ.get("OPENLIST_URL"),
    reason="OPENLIST_URL not set — skipping E2E tests",
)

BASE = "/mcp-e2e-" + time.strftime("%Y%m%d-%H%M%S")
SAMPLE = Path("/tmp/mcp-e2e-sample.txt")
SAMPLE.write_text("OpenList MCP E2E test\n中文内容\n", encoding="utf-8")


def _req(name: str, client, method: str, path: str, **kwargs):
    """Wrap client.request with step naming for test reporting."""
    return client.request(method, path, **kwargs)


@pytest.mark.asyncio
@SKIP
async def test_e2e_full_user_flow():
    """Simulate a complete user workflow on a real OpenList instance."""
    c = OpenListClient()
    results = []

    async def step(name, coro, required=True):
        for attempt in range(1, 4):
            try:
                data = await coro
                results.append({"step": name, "ok": True, "attempt": attempt})
                return data
            except Exception as e:
                err = str(e)
                if "SQLITE_BUSY" in err and attempt < 3:
                    await asyncio.sleep(attempt * 2)
                    continue
                if attempt < 3:
                    await asyncio.sleep(1)
                    continue
                results.append({"step": name, "ok": False, "error": err[:300]})
                if required:
                    pytest.fail(f"{name} required step failed: {err[:300]}")
                return None

    try:
        # Auth
        await step("login", c.login())
        await step("public_settings", c.request("GET", "public/settings", require_auth=False))
        await step("get_me", c.request("GET", "me"))

        # File browsing
        await step("list_root", c.request("POST", "fs/list", json={"path": "/", "page": 1, "per_page": 20, "password": ""}))

        # Create folders
        await step("create_folder_base", c.request("POST", "fs/mkdir", json={"path": BASE}))
        await step("create_folder_docs", c.request("POST", "fs/mkdir", json={"path": BASE + "/docs"}))
        await step("list_dirs", c.request("POST", "fs/dirs", json={"path": BASE, "password": "", "force_root": False}))

        # Upload
        up = await c.upload(BASE + "/docs", SAMPLE.read_bytes(), "sample.txt", as_task=False)
        results.append({"step": "upload_file", "ok": True, "attempt": 1})

        # File info
        await step("get_file_info", c.request("POST", "fs/get", json={"path": BASE + "/docs/sample.txt", "password": ""}))

        # Rename
        await step("rename_file", c.request("POST", "fs/rename", json={"path": BASE + "/docs/sample.txt", "name": "renamed.txt"}))

        # Copy
        await step("create_folder_moved", c.request("POST", "fs/mkdir", json={"path": BASE + "/moved"}))
        await step("copy_file", c.request("POST", "fs/copy", json={"src_dir": BASE + "/docs", "dst_dir": BASE, "names": ["renamed.txt"]}))

        # Move
        await step("move_file", c.request("POST", "fs/move", json={"src_dir": BASE, "dst_dir": BASE + "/moved", "names": ["renamed.txt"]}))

        # Download link
        await step("get_download_link", c.request("POST", "fs/link", json={"path": BASE + "/docs/renamed.txt", "password": ""}), required=False)

        # Shares
        share = await step("create_share", c.request("POST", "share/create", json={"files": [BASE + "/docs/renamed.txt"], "remark": "e2e"}), required=False)
        sid = None
        if share and isinstance(share, dict):
            d = share.get("data") or share
            if isinstance(d, dict):
                sid = d.get("id") or d.get("share_id")
        await step("list_shares", c.request("GET", "share/list", params={"page": 1, "per_page": 20}), required=False)
        if sid:
            await step("disable_share", c.request("POST", "share/disable", json={"id": sid}), required=False)
            await step("enable_share", c.request("POST", "share/enable", json={"id": sid}), required=False)
            await step("delete_share", c.request("POST", "share/delete", params={"id": sid}), required=False)

        # Tasks
        await step("list_tasks", c.request("GET", "task/copy/done", params={"page": 1, "per_page": 20}), required=False)

        # Misc
        await step("list_download_tools", c.request("GET", "public/offline_download_tools", require_auth=False), required=False)

    finally:
        # Cleanup
        try:
            parent = BASE.rsplit("/", 1)[0] or "/"
            name = BASE.rsplit("/", 1)[1]
            await c.request("POST", "fs/remove", json={"dir": parent, "names": [name]})
        except Exception:
            pass
        await c.close()

    # Report
    oks = sum(1 for r in results if r["ok"])
    total = len(results)
    failures = [r for r in results if not r["ok"]]
    print(f"\nE2E results: {oks}/{total} passed")
    for f in failures:
        print(f"  ❌ {f['step']}: {f.get('error', '?')}")

    assert oks == total, f"{len(failures)} step(s) failed"
