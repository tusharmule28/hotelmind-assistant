from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.orm.booking import Booking, BookingStatus
from app.repositories.base import BaseRepository


class BookingRepository(BaseRepository[Booking]):
    model = Booking

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_by_user(self, user_id: int) -> List[Booking]:
        result = await self.db.execute(
            select(Booking)
            .where(Booking.user_id == user_id)
            .order_by(Booking.created_at.desc())
        )
        return list(result.scalars().all())

    async def create_hold(
        self,
        hotel_id: int,
        room_id: int,
        user_id: Optional[int] = None,
        check_in=None,
        check_out=None,
        hold_minutes: int = 15,
    ) -> Booking:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=hold_minutes)
        return await self.create(
            {
                "hotel_id": hotel_id,
                "room_id": room_id,
                "user_id": user_id,
                "check_in": check_in,
                "check_out": check_out,
                "status": BookingStatus.HOLD,
                "expires_at": expires_at,
            }
        )

    async def confirm(self, booking_id: int) -> Optional[Booking]:
        booking = await self.get(booking_id)
        if not booking or booking.status != BookingStatus.HOLD:
            return None
        # Guard against expired hold
        if booking.expires_at:
            exp = booking.expires_at
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if exp < datetime.now(timezone.utc):
                return None
        booking.status = BookingStatus.CONFIRMED
        self.db.add(booking)
        await self.db.flush()
        await self.db.refresh(booking)
        return booking

    async def cancel(self, booking_id: int) -> Optional[Booking]:
        booking = await self.get(booking_id)
        if not booking or booking.status == BookingStatus.CANCELLED:
            return None
        booking.status = BookingStatus.CANCELLED
        self.db.add(booking)
        await self.db.flush()
        await self.db.refresh(booking)
        return booking
