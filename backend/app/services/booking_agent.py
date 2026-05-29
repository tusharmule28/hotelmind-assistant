from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from datetime import date

from app.repositories.booking_repo import BookingRepository
from app.repositories.room_repo import RoomRepository
from app.repositories.user_repo import UserRepository
from app.repositories.hotel_repo import HotelRepository
from app.models.orm.booking import BookingStatus


class BookingAgentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.booking_repo = BookingRepository(db)
        self.room_repo = RoomRepository(db)
        self.user_repo = UserRepository(db)
        self.hotel_repo = HotelRepository(db)

    async def get_availability(self, hotel_id: int) -> List[Dict[str, Any]]:
        """Returns room availability for a specific hotel."""
        rooms = await self.room_repo.get_available_rooms(hotel_id)
        
        return [
            {
                "id": r.id,
                "room_type": r.type,
                "available_rooms": 1 if r.availability else 0,
                "total_rooms": 1,
                "price": r.price
            }
            for r in rooms
        ]

    async def hold_booking(
        self, 
        hotel_id: int, 
        room_type: str, 
        user_id_str: str = "guest",
        check_in: Optional[date] = None,
        check_out: Optional[date] = None
    ) -> Dict[str, Any]:
        """Holds a room for 15 minutes if available."""
        # 1. Resolve or create user from string identifier
        email = f"{user_id_str.replace(' ', '_').lower()}@hotelmind.ai"
        user = await self.user_repo.get_or_create(name=user_id_str, email=email)

        # 2. Find an available room of the requested type
        room = await self.room_repo.find_room(hotel_id, room_type)
        if not room:
            return {"success": False, "message": f"No {room_type} rooms available"}

        # 3. Temporarily mark room as unavailable (hold)
        await self.room_repo.set_availability(room.id, False)

        # 4. Create the booking under HOLD status
        booking = await self.booking_repo.create_hold(
            hotel_id=hotel_id,
            room_id=room.id,
            user_id=user.id,
            check_in=check_in,
            check_out=check_out
        )
        
        # Commit transactional changes
        await self.db.commit()

        return {
            "success": True,
            "booking_id": booking.id,
            "status": booking.status.value,
            "room_type": room.type,
            "price": room.price,
            "expires_at": booking.expires_at.isoformat() if booking.expires_at else None
        }

    async def confirm_booking(self, booking_id: int) -> Dict[str, Any]:
        """Confirms a HOLD booking."""
        booking = await self.booking_repo.confirm(booking_id)
        if not booking:
            # Check if booking exists but hold expired
            existing = await self.booking_repo.get(booking_id)
            if existing and existing.status == BookingStatus.HOLD:
                # Release the room back to inventory
                await self.room_repo.set_availability(existing.room_id, True)
                await self.booking_repo.cancel(booking_id)
                await self.db.commit()
                return {"success": False, "message": "Booking hold expired and room has been released."}
            return {"success": False, "message": "Booking not found or cannot be confirmed."}
            
        await self.db.commit()
        return {
            "success": True, 
            "booking_id": booking.id, 
            "status": booking.status.value
        }

    async def cancel_booking(self, booking_id: int) -> Dict[str, Any]:
        """Cancels a booking and releases inventory."""
        booking = await self.booking_repo.get(booking_id)
        if not booking:
            return {"success": False, "message": "Booking not found"}
            
        if booking.status == BookingStatus.CANCELLED:
            return {"success": False, "message": "Booking already cancelled"}
            
        # Return room back to available inventory
        await self.room_repo.set_availability(booking.room_id, True)
        
        # Mark booking as cancelled
        await self.booking_repo.cancel(booking_id)
        await self.db.commit()
        
        return {"success": True, "message": "Booking cancelled successfully and room inventory released."}
