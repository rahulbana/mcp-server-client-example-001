"""MCP tool definitions — business logic wired to the repository."""
from __future__ import annotations

import json
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from server.database import get_session
from server.repository import InventoryRepository
from shared.models import Category, ItemCreate, ItemUpdate, Unit

mcp = FastMCP(
    name="inventory-server",
    instructions=(
        "Manage grocery/fruit inventory. "
        "Use these tools to add, update, list, and delete inventory items."
    ),
)


def _json(obj: Any) -> str:
    return json.dumps(obj, default=str, indent=2)


@mcp.tool()
async def add_item(
    name: str,
    category: str,
    quantity: float,
    unit: str,
    price_per_unit: Optional[float] = None,
    notes: Optional[str] = None,
) -> str:
    """
    Add a new inventory item (or increase quantity if the same name+unit already exists).

    Args:
        name: Item name (e.g. 'apple', 'rice').
        category: One of: fruit, vegetable, grocery, dairy, beverage, other.
        quantity: Numeric quantity (must be > 0).
        unit: One of: kg, gram, litre, ml, dozen, piece, pack, box.
        price_per_unit: Optional cost per unit.
        notes: Optional free-text notes.

    Returns:
        JSON representation of the created/updated item.
    """
    data = ItemCreate(
        name=name,
        category=Category(category),
        quantity=quantity,
        unit=Unit(unit),
        price_per_unit=price_per_unit,
        notes=notes,
    )
    async with get_session() as session:
        repo = InventoryRepository(session)
        item = await repo.upsert_by_name(data)
    return _json(item.model_dump())


@mcp.tool()
async def get_item(item_id: int) -> str:
    """
    Retrieve a single inventory item by its ID.

    Args:
        item_id: Integer primary key of the item.

    Returns:
        JSON of the item, or an error message if not found.
    """
    async with get_session() as session:
        repo = InventoryRepository(session)
        item = await repo.get_by_id(item_id)
    if not item:
        return _json({"error": f"Item {item_id} not found"})
    return _json(item.model_dump())


@mcp.tool()
async def list_items(
    category: Optional[str] = None,
    name_contains: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> str:
    """
    List inventory items with optional filters.

    Args:
        category: Filter by category (fruit/vegetable/grocery/dairy/beverage/other).
        name_contains: Case-insensitive substring match on item name.
        limit: Max results to return (default 50).
        offset: Pagination offset (default 0).

    Returns:
        JSON with 'items' array and 'total' count.
    """
    async with get_session() as session:
        repo = InventoryRepository(session)
        items, total = await repo.list_items(
            category=category,
            name_contains=name_contains,
            limit=limit,
            offset=offset,
        )
    return _json({"items": [i.model_dump() for i in items], "total": total})


@mcp.tool()
async def update_item(
    item_id: int,
    quantity: Optional[float] = None,
    unit: Optional[str] = None,
    price_per_unit: Optional[float] = None,
    notes: Optional[str] = None,
) -> str:
    """
    Update quantity, unit, price, or notes for an existing item.

    Args:
        item_id: ID of the item to update.
        quantity: New quantity value.
        unit: New unit string.
        price_per_unit: New price per unit.
        notes: Updated notes.

    Returns:
        JSON of the updated item, or an error if not found.
    """
    patch = ItemUpdate(
        quantity=quantity,
        unit=Unit(unit) if unit else None,
        price_per_unit=price_per_unit,
        notes=notes,
    )
    async with get_session() as session:
        repo = InventoryRepository(session)
        item = await repo.update(item_id, patch)
    if not item:
        return _json({"error": f"Item {item_id} not found"})
    return _json(item.model_dump())


@mcp.tool()
async def delete_item(item_id: int) -> str:
    """
    Permanently delete an inventory item.

    Args:
        item_id: ID of the item to delete.

    Returns:
        JSON with 'deleted' boolean and the item_id.
    """
    async with get_session() as session:
        repo = InventoryRepository(session)
        deleted = await repo.delete(item_id)
    return _json({"deleted": deleted, "item_id": item_id})


@mcp.tool()
async def list_units() -> str:
    """Return all supported unit values."""
    return _json([u.value for u in Unit])


@mcp.tool()
async def list_categories() -> str:
    """Return all supported category values."""
    return _json([c.value for c in Category])
