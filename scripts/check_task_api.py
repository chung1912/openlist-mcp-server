#!/usr/bin/env python3
"""Smoke test for OpenList typed task API."""

import asyncio
import os

from openlist_mcp.client import OpenListError, get_client


async def main() -> int:
    missing = [
        k
        for k in ("OPENLIST_URL", "OPENLIST_USERNAME", "OPENLIST_PASSWORD")
        if not os.environ.get(k)
    ]
    if missing:
        print("Missing required environment variables: " + ", ".join(missing))
        return 2

    client = await get_client()
    await client.login()
    print("Login successful; token acquired but not printed.")
    try:
        data = await client.request("GET", "task/offline_download/done")
        print("Offline download task API response keys:", ", ".join(data.keys()) or "(empty)")
        return 0
    except OpenListError as e:
        print("Task API failed:", e.message)
        return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
