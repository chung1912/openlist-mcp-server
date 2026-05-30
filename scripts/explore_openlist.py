#!/usr/bin/env python3
"""Explore an OpenList directory using environment-based credentials."""

import asyncio
import os

from openlist_mcp.client import OpenListError, get_client


async def explore() -> int:
    missing = [
        k
        for k in ("OPENLIST_URL", "OPENLIST_USERNAME", "OPENLIST_PASSWORD")
        if not os.environ.get(k)
    ]
    if missing:
        print("Missing required environment variables: " + ", ".join(missing))
        return 2

    path = os.environ.get("OPENLIST_TEST_DIR", "/")
    client = await get_client()
    await client.login()
    print("Login successful; token acquired but not printed.\n")
    print(f"Directory {path} contents:")
    print("-" * 40)
    try:
        data = await client.request("POST", "fs/list", json={"path": path})
        for item in data.get("content", []):
            name = item.get("name", "N/A")
            marker = "[dir]" if item.get("is_dir", False) else "[file]"
            print(f"  {marker} {name}")
    except OpenListError as e:
        print(f"  Error: {e.message}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(explore()))
