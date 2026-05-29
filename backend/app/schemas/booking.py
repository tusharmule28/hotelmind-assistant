from __future__ import annotations
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.orm.booking import BookingStatus


class BookingCreate(BaseModel):
    hotel_id: int
    room_id: int
    user_id: Optional[int] = None
    check_in: Optional[date] = None
    check_out: Optional[date] = None


class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    check_in: Optional[date] = None
    check_out: Optional[date] = None


class BookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hotel_id: int
    room_id: int
    user_id: Optional[int]
    check_in: Optional[date]
    check_out: Optional[date]
    status: BookingStatus
    created_at: datetime
    expires_at: Optional[datetime]
