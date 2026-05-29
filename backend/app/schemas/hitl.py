from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.orm.hitl_ticket import HITLStatus, HITLPriority


class HITLTicketCreate(BaseModel):
    type: str
    reason: Optional[str] = None
    priority: HITLPriority = HITLPriority.LOW
    ai_draft: Optional[str] = None
    confidence_score: Optional[float] = None
    booking_amount: Optional[float] = None
    fraud_score: Optional[float] = None


class HITLTicketUpdate(BaseModel):
    status: Optional[HITLStatus] = None
    ai_draft: Optional[str] = None


class HITLTicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    reason: Optional[str]
    status: HITLStatus
    priority: HITLPriority
    ai_draft: Optional[str]
    confidence_score: Optional[float]
    booking_amount: Optional[float]
    fraud_score: Optional[float]
    created_at: datetime


class ResolveRequest(BaseModel):
    ticket_id: int
    action: str   # "APPROVE" | "REJECT" | "EDIT"
    new_draft: Optional[str] = None
