"""MCP Server entry-point — Streamable HTTP transport for remote clients."""
from __future__ import annotations

import logging

import uvicorn

from server.database import close_db, init_db
from server.tools import mcp
from shared.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


async def _lifespan(app):  # noqa: ANN001
    logger.info("Initialising database…")
    await init_db()
    logger.info("Database ready.")
    yield
    await close_db()


# Build the Starlette ASGI app with the /mcp endpoint
app = mcp.streamable_http_app()

# Attach our DB lifespan to the ASGI app produced by FastMCP
from contextlib import asynccontextmanager  # noqa: E402


@asynccontextmanager
async def lifespan(asgi_app):  # noqa: ANN001
    logger.info("Initialising database…")
    await init_db()
    logger.info("Database ready.")
    yield
    await close_db()


app.router.lifespan_context = lifespan


def run() -> None:
    """Run the MCP server over HTTP (Streamable HTTP transport)."""
    logger.info(
        "Starting inventory MCP server on %s:%s",
        settings.mcp_server_host,
        settings.mcp_server_port,
    )
    uvicorn.run(
        "server.main:app",
        host=settings.mcp_server_host,
        port=settings.mcp_server_port,
        reload=False,
    )


if __name__ == "__main__":
    run()
