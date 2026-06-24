"""Seed the database with sample inventory items."""
from __future__ import annotations

import asyncio

from server.database import get_session, init_db
from server.repository import InventoryRepository
from shared.models import Category, ItemCreate, Unit

SEED_ITEMS = [
    ItemCreate(name="apple", category=Category.FRUIT, quantity=10.0, unit=Unit.KG, price_per_unit=1.5),
    ItemCreate(name="banana", category=Category.FRUIT, quantity=3.0, unit=Unit.DOZEN, price_per_unit=0.8),
    ItemCreate(name="mango", category=Category.FRUIT, quantity=5.0, unit=Unit.KG, price_per_unit=2.0),
    ItemCreate(name="orange", category=Category.FRUIT, quantity=6.0, unit=Unit.KG, price_per_unit=1.2),
    ItemCreate(name="tomato", category=Category.VEGETABLE, quantity=4.0, unit=Unit.KG, price_per_unit=0.9),
    ItemCreate(name="potato", category=Category.VEGETABLE, quantity=20.0, unit=Unit.KG, price_per_unit=0.5),
    ItemCreate(name="onion", category=Category.VEGETABLE, quantity=15.0, unit=Unit.KG, price_per_unit=0.6),
    ItemCreate(name="basmati rice", category=Category.GROCERY, quantity=25.0, unit=Unit.KG, price_per_unit=1.8),
    ItemCreate(name="whole wheat flour", category=Category.GROCERY, quantity=10.0, unit=Unit.KG, price_per_unit=0.9),
    ItemCreate(name="sunflower oil", category=Category.GROCERY, quantity=5.0, unit=Unit.LITRE, price_per_unit=1.4),
    ItemCreate(name="whole milk", category=Category.DAIRY, quantity=10.0, unit=Unit.LITRE, price_per_unit=1.1),
    ItemCreate(name="butter", category=Category.DAIRY, quantity=2.0, unit=Unit.KG, price_per_unit=4.5),
    ItemCreate(name="orange juice", category=Category.BEVERAGE, quantity=6.0, unit=Unit.LITRE, price_per_unit=1.3),
    ItemCreate(name="mineral water", category=Category.BEVERAGE, quantity=12.0, unit=Unit.LITRE, price_per_unit=0.4),
    ItemCreate(name="eggs", category=Category.DAIRY, quantity=5.0, unit=Unit.DOZEN, price_per_unit=2.5),
]


async def main() -> None:
    await init_db()
    async with get_session() as session:
        repo = InventoryRepository(session)
        for item in SEED_ITEMS:
            created = await repo.upsert_by_name(item)
            print(f"  [{created.id:>3}] {created.name:<22} {created.quantity} {created.unit}")
    print(f"\nSeeded {len(SEED_ITEMS)} items.")


if __name__ == "__main__":
    asyncio.run(main())
