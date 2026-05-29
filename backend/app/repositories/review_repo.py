from __future__ import annotations
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.orm.review import Review
from app.repositories.base import BaseRepository


class ReviewRepository(BaseRepository[Review]):
    model = Review

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_by_hotel(self, hotel_id: int) -> List[Review]:
        result = await self.db.execute(
            select(Review)
            .where(Review.hotel_id == hotel_id)
            .order_by(Review.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_user(self, user_id: int) -> List[Review]:
        result = await self.db.execute(
            select(Review)
            .where(Review.user_id == user_id)
            .order_by(Review.created_at.desc())
        )
        return list(result.scalars().all())
