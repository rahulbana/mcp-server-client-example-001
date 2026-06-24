"""MCP Server entry-point."""
from __future__ import annotations

import asyncio
import logging

from server.database import close_db, init_db
from server.tools import mcp

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


async def _startup() -> None:
    logger.info("Initialising database…")
    await init_db()
    logger.info("Database ready.")


async def _shutdown() -> None:
    await close_db()


def run() -> None:
    """Run the MCP server over stdio (default MCP transport)."""
    asyncio.run(_startup())
    try:
        mcp.run(transport="stdio")
    finally:
        asyncio.run(_shutdown())


if __name__ == "__main__":
    run()
