# MCP Inventory — Server + Client

A production-grade example of an **MCP (Model Context Protocol) server** and **MCP client** for managing grocery/fruit inventory backed by **PostgreSQL** and driven by an **OpenAI** tool-calling agent.

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│  client/main.py  (Typer CLI)                    │
│    └── InventoryAgent  (OpenAI tool-calling)    │
│          └── mcp_session  (MCP ClientSession)   │
│                │  stdio transport               │
│                ▼                                │
│  server/main.py  (FastMCP server)               │
│    └── tools.py  (7 MCP tools)                  │
│          └── repository.py  (async queries)     │
│                └── PostgreSQL (asyncpg)         │
└─────────────────────────────────────────────────┘
```

## Project layout

```
├── server/
│   ├── main.py          # MCP server entry-point (stdio transport)
│   ├── tools.py         # 7 MCP tool definitions (FastMCP)
│   ├── repository.py    # All DB queries (async SQLAlchemy)
│   ├── orm_models.py    # SQLAlchemy ORM model
│   └── database.py      # Engine, session factory, init_db
├── client/
│   ├── main.py          # Interactive CLI (Typer + Rich)
│   ├── llm_agent.py     # OpenAI tool-calling loop
│   └── mcp_session.py   # MCP ClientSession wrapper
├── shared/
│   ├── config.py        # Pydantic settings (env vars)
│   └── models.py        # Shared Pydantic schemas (Unit, Category …)
├── migrations/          # Alembic async migrations
├── scripts/seed.py      # Seed sample data
├── tests/               # Pytest async tests (SQLite in-memory)
├── docker-compose.yml   # PostgreSQL service
└── pyproject.toml
```

## Supported units & categories

| Units | Categories |
|-------|-----------|
| `kg`, `gram`, `litre`, `ml` | `fruit`, `vegetable`, `grocery` |
| `dozen`, `piece`, `pack`, `box` | `dairy`, `beverage`, `other` |

## Quick start

### 1. Start PostgreSQL

```bash
docker-compose up -d
```

### 2. Install dependencies

```bash
pip install -e ".[dev]"
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env — set DATABASE_URL and OPENAI_API_KEY
```

### 4. Run database migrations

```bash
alembic upgrade head
```

### 5. (Optional) Seed sample data

```bash
python scripts/seed.py
```

### 6. Start the interactive client

```bash
python -m client.main
```

The client spawns the MCP server as a subprocess automatically.

### Example conversation

```
You: Add 10 kg of apples at 1.5 per kg
You: Show me all fruits
You: Update apple quantity to 8 kg
You: Delete item 3
You: What grocery items do we have?
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `add_item` | Add / upsert an item (accumulates quantity if same name+unit) |
| `get_item` | Fetch a single item by ID |
| `list_items` | List with optional category / name filters + pagination |
| `update_item` | Patch quantity, unit, price, or notes |
| `delete_item` | Permanently remove an item |
| `list_units` | Enumerate valid unit values |
| `list_categories` | Enumerate valid category values |

## Running tests

```bash
pip install aiosqlite  # in-memory SQLite for tests
pytest -v
```

## Run the MCP server standalone (e.g. for Claude Desktop)

```bash
python -m server.main
```

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "inventory": {
      "command": "python",
      "args": ["-m", "server.main"],
      "env": { "DATABASE_URL": "postgresql+asyncpg://..." }
    }
  }
}
```
