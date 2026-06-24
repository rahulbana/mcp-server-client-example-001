"""Data-access layer — all DB queries live here."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from server.orm_models import InventoryItem
from shared.models import ItemCreate, ItemOut, ItemUpdate


def _to_out(row: InventoryItem) -> ItemOut:
    return ItemOut.model_validate(row)


class InventoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: ItemCreate) -> ItemOut:
        item = InventoryItem(
            name=data.name,
            category=data.category.value,
            quantity=data.quantity,
            unit=data.unit.value,
            price_per_unit=data.price_per_unit,
            notes=data.notes,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self._session.add(item)
        await self._session.flush()
        await self._session.refresh(item)
        return _to_out(item)

    async def get_by_id(self, item_id: int) -> Optional[ItemOut]:
        result = await self._session.execute(
            select(InventoryItem).where(InventoryItem.id == item_id)
        )
        row = result.scalar_one_or_none()
        return _to_out(row) if row else None

    async def list_items(
        self,
        category: Optional[str] = None,
        name_contains: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[ItemOut], int]:
        query = select(InventoryItem)
        count_query = select(func.count()).select_from(InventoryItem)

        if category:
            query = query.where(InventoryItem.category == category)
            count_query = count_query.where(InventoryItem.category == category)
        if name_contains:
            like = f"%{name_contains.lower()}%"
            query = query.where(InventoryItem.name.like(like))
            count_query = count_query.where(InventoryItem.name.like(like))

        total = (await self._session.execute(count_query)).scalar_one()
        rows = (
            await self._session.execute(query.order_by(InventoryItem.name).limit(limit).offset(offset))
        ).scalars().all()

        return [_to_out(r) for r in rows], total

    async def update(self, item_id: int, data: ItemUpdate) -> Optional[ItemOut]:
        patch = {k: v for k, v in data.model_dump(exclude_none=True).items()}
        if not patch:
            return await self.get_by_id(item_id)

        patch["updated_at"] = datetime.now(timezone.utc)
        await self._session.execute(
            update(InventoryItem).where(InventoryItem.id == item_id).values(**patch)
        )
        return await self.get_by_id(item_id)

    async def delete(self, item_id: int) -> bool:
        result = await self._session.execute(
            delete(InventoryItem).where(InventoryItem.id == item_id)
        )
        return result.rowcount > 0

    async def upsert_by_name(self, data: ItemCreate) -> ItemOut:
        """Add quantity if item with same name+unit already exists."""
        result = await self._session.execute(
            select(InventoryItem).where(
                InventoryItem.name == data.name,
                InventoryItem.unit == data.unit.value,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.quantity += data.quantity
            existing.updated_at = datetime.now(timezone.utc)
            await self._session.flush()
            await self._session.refresh(existing)
            return _to_out(existing)
        return await self.create(data)
