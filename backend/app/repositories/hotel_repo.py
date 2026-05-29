from __future__ import annotations
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.orm.hotel import Hotel
from app.repositories.base import BaseRepository


class HotelRepository(BaseRepository[Hotel]):
    model = Hotel

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_by_city(self, city: str) -> List[Hotel]:
        result = await self.db.execute(
            select(Hotel).where(Hotel.city.ilike(f"%{city}%"))
        )
        return list(result.scalars().all())

    async def search(self, query: str) -> List[Hotel]:
        """Loose name/city search — ChromaDB handles semantic search."""
        result = await self.db.execute(
            select(Hotel).where(
                Hotel.name.ilike(f"%{query}%") | Hotel.city.ilike(f"%{query}%")
            )
        )
        return list(result.scalars().all())
