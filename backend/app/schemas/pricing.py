from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class PricingSnapshotCreate(BaseModel):
    hotel_id: int
    price: float = Field(gt=0)


class PricingSnapshotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hotel_id: int
    price: float
    timestamp: datetime
