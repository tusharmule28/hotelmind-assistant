from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    user_id: Optional[int] = None
    hotel_id: int
    rating: float = Field(ge=1.0, le=5.0)
    text: str
    sentiment: Optional[str] = None
    ai_draft_response: Optional[str] = None


class ReviewUpdate(BaseModel):
    sentiment: Optional[str] = None
    ai_draft_response: Optional[str] = None


class ReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int]
    hotel_id: int
    rating: float
    text: str
    sentiment: Optional[str]
    ai_draft_response: Optional[str]
    created_at: datetime
