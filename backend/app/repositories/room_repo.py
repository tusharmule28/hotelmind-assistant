from __future__ import annotations
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.orm.room import Room
from app.repositories.base import BaseRepository


class RoomRepository(BaseRepository[Room]):
    model = Room

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_available_rooms(self, hotel_id: int) -> List[Room]:
        """Return all available rooms for a hotel."""
        result = await self.db.execute(
            select(Room).where(Room.hotel_id == hotel_id, Room.availability == True)
        )
        return list(result.scalars().all())

    async def find_room(self, hotel_id: int, room_type: str) -> Optional[Room]:
        """Find first available room matching the type (case-insensitive)."""
        result = await self.db.execute(
            select(Room).where(
                Room.hotel_id == hotel_id,
                Room.type.ilike(f"%{room_type}%"),
                Room.availability == True,
            ).limit(1)
        )
        return result.scalar_one_or_none()

    async def set_availability(self, room_id: int, available: bool) -> Optional[Room]:
        """Flip the availability flag on a single room."""
        room = await self.get(room_id)
        if room:
            room.availability = available
            self.db.add(room)
            await self.db.flush()
        return room
