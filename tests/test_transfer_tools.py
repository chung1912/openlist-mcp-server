"""Behavior tests for transfer MCP tools."""

import pytest


@pytest.mark.asyncio
async def test_upload_file_validates_file_name(transfer_tools) -> None:
    tools, client = transfer_tools

    with pytest.raises(ValueError, match="path separators"):
        await tools["upload_file"]("/docs", "bad/name.txt", "aGVsbG8=")

    assert client.uploads == []


@pytest.mark.asyncio
async def test_upload_file_sends_decoded_content(transfer_tools) -> None:
    tools, client = transfer_tools

    result = await tools["upload_file"]("/docs", "note.txt", "aGVsbG8=", as_task=False)

    assert result == "File uploaded successfully: /docs/note.txt"
    assert client.uploads == [
        {
            "path": "/docs",
            "file_content": b"hello",
            "file_name": "note.txt",
            "as_task": False,
        }
    ]
