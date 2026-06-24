"""MCP client session over Streamable HTTP (works across machines)."""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from shared.config import settings


@asynccontextmanager
async def mcp_session(
    url: str | None = None,
) -> AsyncGenerator[ClientSession, None]:
    """Connect to a remote MCP server over HTTP and yield an active ClientSession.

    Args:
        url: Full URL of the server's MCP endpoint, e.g. 'http://192.168.1.10:8765/mcp'.
             Defaults to MCP_SERVER_URL from config / environment.
    """
    target = url or settings.mcp_server_url
    async with streamablehttp_client(target) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


async def call_tool(session: ClientSession, name: str, arguments: dict[str, Any]) -> str:
    result = await session.call_tool(name, arguments=arguments)
    return "".join(
        block.text for block in result.content if hasattr(block, "text")
    )


async def list_tools(session: ClientSession) -> list[dict]:
    response = await session.list_tools()
    return [
        {
            "name": t.name,
            "description": t.description,
            "input_schema": t.inputSchema,
        }
        for t in response.tools
    ]
