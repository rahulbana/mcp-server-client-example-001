"""Unit tests for the repository layer using SQLite in-memory."""
from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from server.database import Base
from server.orm_models import InventoryItem  # noqa: F401
from server.repository import InventoryRepository
from shared.models import Category, ItemCreate, ItemUpdate, Unit

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture()
async def session():
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as s:
        yield s
        await s.rollback()

    await engine.dispose()


@pytest.fixture()
def repo(session: AsyncSession) -> InventoryRepository:
    return InventoryRepository(session)


@pytest.fixture()
def apple() -> ItemCreate:
    return ItemCreate(name="apple", category=Category.FRUIT, quantity=5.0, unit=Unit.KG)


async def test_create_item(repo: InventoryRepository, apple: ItemCreate) -> None:
    item = await repo.create(apple)
    assert item.id is not None
    assert item.name == "apple"
    assert item.quantity == 5.0


async def test_get_by_id(repo: InventoryRepository, apple: ItemCreate) -> None:
    created = await repo.create(apple)
    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id


async def test_get_by_id_not_found(repo: InventoryRepository) -> None:
    assert await repo.get_by_id(99999) is None


async def test_list_items(repo: InventoryRepository, apple: ItemCreate) -> None:
    await repo.create(apple)
    await repo.create(ItemCreate(name="banana", category=Category.FRUIT, quantity=2.0, unit=Unit.DOZEN))
    items, total = await repo.list_items()
    assert total == 2
    assert len(items) == 2


async def test_list_filter_category(repo: InventoryRepository) -> None:
    await repo.create(ItemCreate(name="apple", category=Category.FRUIT, quantity=1.0, unit=Unit.KG))
    await repo.create(ItemCreate(name="rice", category=Category.GROCERY, quantity=5.0, unit=Unit.KG))
    items, total = await repo.list_items(category="fruit")
    assert total == 1
    assert items[0].name == "apple"


async def test_update_item(repo: InventoryRepository, apple: ItemCreate) -> None:
    created = await repo.create(apple)
    updated = await repo.update(created.id, ItemUpdate(quantity=10.0))
    assert updated is not None
    assert updated.quantity == 10.0


async def test_delete_item(repo: InventoryRepository, apple: ItemCreate) -> None:
    created = await repo.create(apple)
    assert await repo.delete(created.id) is True
    assert await repo.get_by_id(created.id) is None


async def test_upsert_adds_quantity(repo: InventoryRepository, apple: ItemCreate) -> None:
    first = await repo.upsert_by_name(apple)
    second = await repo.upsert_by_name(apple)
    assert second.id == first.id
    assert second.quantity == 10.0  # 5 + 5
