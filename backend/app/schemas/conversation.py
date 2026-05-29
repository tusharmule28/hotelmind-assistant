from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class ConversationCreate(BaseModel):
    user_id: Optional[int] = None
    session_id: str


class ConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int]
    session_id: str
    created_at: datetime


# ── Message ──────────────────────────────────────────────────────────────────

class MessageCreate(BaseModel):
    conversation_id: int
    role: str   # "user" | "assistant" | "system"
    content: str


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    role: str
    content: str
    timestamp: datetime


class ConversationWithMessages(ConversationRead):
    messages: List[MessageRead] = []
