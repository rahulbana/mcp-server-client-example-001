"""Thin wrapper around the MCP client session."""
from __future__ import annotations

import asyncio
import json
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@asynccontextmanager
async def mcp_session(server_script: str) -> AsyncGenerator[ClientSession, None]:
    """Spawn the MCP server as a subprocess and yield an active ClientSession."""
    params = StdioServerParameters(command="python", args=["-m", server_script])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


async def call_tool(session: ClientSession, name: str, arguments: dict[str, Any]) -> str:
    result = await session.call_tool(name, arguments=arguments)
    # MCP returns a list of content blocks; join text blocks
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
