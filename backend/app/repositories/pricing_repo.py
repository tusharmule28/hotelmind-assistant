from __future__ import annotations
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.orm.pricing import PricingSnapshot
from app.repositories.base import BaseRepository


class PricingRepository(BaseRepository[PricingSnapshot]):
    model = PricingSnapshot

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_latest_for_hotel(self, hotel_id: int) -> PricingSnapshot | None:
        result = await self.db.execute(
            select(PricingSnapshot)
            .where(PricingSnapshot.hotel_id == hotel_id)
            .order_by(PricingSnapshot.timestamp.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_history(self, hotel_id: int, limit: int = 30) -> List[PricingSnapshot]:
        result = await self.db.execute(
            select(PricingSnapshot)
            .where(PricingSnapshot.hotel_id == hotel_id)
            .order_by(PricingSnapshot.timestamp.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def record(self, hotel_id: int, price: float) -> PricingSnapshot:
        return await self.create({"hotel_id": hotel_id, "price": price})
