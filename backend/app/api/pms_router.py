from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.services.booking_agent import BookingAgentService
from pydantic import BaseModel
from typing import Optional
from datetime import date

router = APIRouter(prefix="/api/pms", tags=["pms"])


class ReserveRequest(BaseModel):
    hotel_id: int
    room_type: str
    user_id: Optional[str] = "guest"
    check_in: Optional[date] = None
    check_out: Optional[date] = None


class BookingActionRequest(BaseModel):
    booking_id: int


@router.get("/availability")
async def check_availability(hotel_id: int, db: AsyncSession = Depends(get_db)):
    """Check inventory and rate availability for a hotel."""
    agent = BookingAgentService(db)
    return await agent.get_availability(hotel_id)


@router.post("/reserve")
async def hold_reservation(req: ReserveRequest, db: AsyncSession = Depends(get_db)):
    """Create a temporary (15-min) hold booking on room inventory."""
    agent = BookingAgentService(db)
    result = await agent.hold_booking(
        hotel_id=req.hotel_id, 
        room_type=req.room_type, 
        user_id_str=req.user_id,
        check_in=req.check_in,
        check_out=req.check_out
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.put("/modify")
async def confirm_reservation(req: BookingActionRequest, db: AsyncSession = Depends(get_db)):
    """Confirm a held booking before it expires."""
    agent = BookingAgentService(db)
    result = await agent.confirm_booking(req.booking_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.delete("/cancel")
async def cancel_reservation(booking_id: int, db: AsyncSession = Depends(get_db)):
    """Cancel a booking and release room inventory back."""
    agent = BookingAgentService(db)
    result = await agent.cancel_booking(booking_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result
