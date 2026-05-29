from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class HotelCreate(BaseModel):
    name: str
    city: str
    rating: float = Field(ge=0.0, le=5.0)
    amenities: List[str] = []


class HotelUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    rating: Optional[float] = Field(default=None, ge=0.0, le=5.0)
    amenities: Optional[List[str]] = None


class HotelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    city: str
    rating: float
    amenities: List[str]
