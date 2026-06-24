# MCP Inventory — Server + Client

A production-grade example of an **MCP (Model Context Protocol) server** and **MCP client** designed to run on **separate machines**, backed by **PostgreSQL** and driven by an **OpenAI** tool-calling agent.

---

## Architecture

```
  SERVER MACHINE                        CLIENT MACHINE
  ┌──────────────────────────────┐      ┌──────────────────────────────────┐
  │  server/main.py              │      │  client/main.py  (Typer CLI)     │
  │  FastMCP — Streamable HTTP   │◄─────│    └── InventoryAgent (OpenAI)   │
  │  http://0.0.0.0:8765/mcp    │ HTTP │          └── mcp_session         │
  │    └── tools.py (7 tools)   │      │               (HTTP connection)   │
  │          └── repository.py  │      └──────────────────────────────────┘
  │                └── Postgres  │
  └──────────────────────────────┘
```

**Transport:** MCP Streamable HTTP (stateful, bidirectional over a single HTTP connection).  
The client only needs the server's URL — no shared filesystem, no subprocess.

---

## Project layout

```
├── server/
│   ├── main.py          # FastMCP ASGI app, served by uvicorn
│   ├── tools.py         # 7 MCP tool definitions
│   ├── repository.py    # Async SQLAlchemy data-access layer
│   ├── orm_models.py    # InventoryItem ORM model
│   └── database.py      # Engine, session factory, init_db / close_db
├── client/
│   ├── main.py          # Interactive CLI — takes --server-url flag
│   ├── llm_agent.py     # OpenAI tool-calling loop
│   └── mcp_session.py   # streamablehttp_client wrapper
├── shared/
│   ├── config.py        # Pydantic settings (env vars, used by both sides)
│   └── models.py        # Unit, Category enums + Pydantic schemas
├── migrations/          # Alembic async migrations
├── scripts/seed.py      # Seed 15 sample items
├── tests/               # 8 async pytest tests (SQLite in-memory)
├── docker-compose.yml   # PostgreSQL 16
└── pyproject.toml
```

## Supported units & categories

| Units | Categories |
|-------|-----------|
| `kg`, `gram`, `litre`, `ml` | `fruit`, `vegetable`, `grocery` |
| `dozen`, `piece`, `pack`, `box` | `dairy`, `beverage`, `other` |

---

## Quick start

### On the SERVER machine

```bash
# 1. Start PostgreSQL
docker-compose up -d

# 2. Install server dependencies
pip install -e ".[server]"

# 3. Configure
cp .env.example .env
# Set: DATABASE_URL, MCP_SERVER_HOST=0.0.0.0, MCP_SERVER_PORT=8765

# 4. Run migrations
alembic upgrade head

# 5. (Optional) seed sample data
python scripts/seed.py

# 6. Start the MCP server
python -m server.main
# → Listening on http://0.0.0.0:8765/mcp
```

### On the CLIENT machine

```bash
# 1. Install client dependencies (no database, no uvicorn needed)
pip install -e ".[client]"

# 2. Configure
cp .env.example .env
# Set: MCP_SERVER_URL=http://<server-ip>:8765/mcp
#      OPENAI_API_KEY=sk-...

# 3. Start the interactive assistant
python -m client.main
# or with explicit flags:
python -m client.main --server-url http://192.168.1.10:8765/mcp --model gpt-4o-mini
```

### Example session

```
You: Add 10 kg of apples at £1.50 per kg
You: Show me all fruits
You: Update apple quantity to 8 kg
You: Delete item 3
You: What grocery items do we have?
```

---

## MCP Tools

| Tool | Description |
|------|-------------|
| `add_item` | Add / upsert item (accumulates quantity on same name+unit) |
| `get_item` | Fetch single item by ID |
| `list_items` | Filter by category / name substring, with pagination |
| `update_item` | Patch quantity, unit, price, or notes |
| `delete_item` | Permanently remove an item |
| `list_units` | Returns: `kg`, `gram`, `litre`, `ml`, `dozen`, `piece`, `pack`, `box` |
| `list_categories` | Returns: `fruit`, `vegetable`, `grocery`, `dairy`, `beverage`, `other` |

---

## Running tests

Tests run against SQLite in-memory — no server or Postgres needed:

```bash
pip install -e ".[dev]"
pytest -v
```

---

## Connecting Claude Desktop to the server

Add to `claude_desktop_config.json` on the client machine:

```json
{
  "mcpServers": {
    "inventory": {
      "type": "streamable-http",
      "url": "http://<server-ip>:8765/mcp"
    }
  }
}
```

---

## Environment variables

| Variable | Side | Default | Description |
|----------|------|---------|-------------|
| `DATABASE_URL` | Server | `postgresql+asyncpg://postgres:postgres@localhost:5432/inventory` | Postgres connection string |
| `MCP_SERVER_HOST` | Server | `0.0.0.0` | Bind address |
| `MCP_SERVER_PORT` | Server | `8765` | Bind port |
| `MCP_SERVER_URL` | Client | `http://localhost:8765/mcp` | Full URL of the MCP endpoint |
| `OPENAI_API_KEY` | Client | — | OpenAI API key |
| `OPENAI_MODEL` | Client | `gpt-4o-mini` | Model to use |
