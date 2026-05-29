from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class RoomCreate(BaseModel):
    hotel_id: int
    type: str
    price: float = Field(gt=0)
    availability: bool = True


class RoomUpdate(BaseModel):
    type: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    availability: Optional[bool] = None


class RoomRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hotel_id: int
    type: str
    price: float
    availability: bool
