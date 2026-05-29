from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from typing import List, Dict, Any
from app.models.schema import Hotel, RoomInventory, Booking, BookingStatus
import random
import string
from datetime import datetime, timedelta, timezone

class BookingAgentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_availability(self, hotel_id: int) -> List[Dict[str, Any]]:
        """Returns room availability for a specific hotel."""
        stmt = select(RoomInventory).where(RoomInventory.hotel_id == hotel_id)
        result = await self.db.execute(stmt)
        rooms = result.scalars().all()
        
        return [
            {
                "id": r.id,
                "room_type": r.room_type,
                "available_rooms": r.available_rooms,
                "total_rooms": r.total_rooms
            }
            for r in rooms
        ]

    async def hold_booking(self, hotel_id: int, room_type: str, user_id: str = "guest") -> Dict[str, Any]:
        """Holds a room for 15 minutes if available."""
        # Find room
        stmt = select(RoomInventory).where(
            RoomInventory.hotel_id == hotel_id,
            RoomInventory.room_type.ilike(f"%{room_type}%")
        )
        result = await self.db.execute(stmt)
        room = result.scalars().first()
        
        if not room or room.available_rooms <= 0:
            return {"success": False, "message": "No rooms available"}
            
        # Decrease availability
        room.available_rooms -= 1
        
        # Create booking in HOLD status
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        booking = Booking(
            user_id=user_id,
            hotel_id=hotel_id,
            room_id=room.id,
            status=BookingStatus.HOLD,
            expires_at=expires_at
        )
        self.db.add(booking)
        await self.db.commit()
        await self.db.refresh(booking)
        
        return {
            "success": True,
            "booking_id": booking.id,
            "status": booking.status,
            "expires_at": booking.expires_at.isoformat()
        }

    async def confirm_booking(self, booking_id: int) -> Dict[str, Any]:
        """Confirms a HOLD booking."""
        stmt = select(Booking).where(Booking.id == booking_id)
        result = await self.db.execute(stmt)
        booking = result.scalars().first()
        
        if not booking:
            return {"success": False, "message": "Booking not found"}
            
        if booking.status != BookingStatus.HOLD:
            return {"success": False, "message": f"Booking is in {booking.status} state, cannot confirm."}
            
        if booking.expires_at and booking.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            return {"success": False, "message": "Booking hold expired"}
            
        booking.status = BookingStatus.CONFIRMED
        await self.db.commit()
        
        return {"success": True, "booking_id": booking.id, "status": booking.status}

    async def cancel_booking(self, booking_id: int) -> Dict[str, Any]:
        """Cancels a booking and releases inventory."""
        stmt = select(Booking).where(Booking.id == booking_id)
        result = await self.db.execute(stmt)
        booking = result.scalars().first()
        
        if not booking:
            return {"success": False, "message": "Booking not found"}
            
        if booking.status == BookingStatus.CANCELLED:
            return {"success": False, "message": "Booking already cancelled"}
            
        # Return inventory
        stmt_room = select(RoomInventory).where(RoomInventory.id == booking.room_id)
        result_room = await self.db.execute(stmt_room)
        room = result_room.scalars().first()
        
        if room:
            room.available_rooms += 1
            
        booking.status = BookingStatus.CANCELLED
        await self.db.commit()
        
        return {"success": True, "message": "Booking cancelled"}
