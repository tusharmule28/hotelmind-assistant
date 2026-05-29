from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schema import HitlTicket
from app.services.websocket_manager import manager
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.logger import logger

class HitlTriggerData(BaseModel):
    confidence_score: float
    booking_amount: Optional[float] = 0.0
    fraud_score: Optional[float] = 0.0
    ai_draft: str

async def evaluate_and_create_ticket(data: HitlTriggerData, db: AsyncSession) -> Optional[HitlTicket]:
    trigger_type = None
    severity = "LOW"
    
    if data.fraud_score and data.fraud_score > 0.7:
        trigger_type = "HIGH_FRAUD_SCORE"
        severity = "HIGH"
    elif data.booking_amount and data.booking_amount > 15000:
        trigger_type = "HIGH_VALUE_BOOKING"
        severity = "MEDIUM"
    elif data.confidence_score < 0.65:
        trigger_type = "LOW_CONFIDENCE"
        severity = "MEDIUM"
        
    if trigger_type:
        new_ticket = HitlTicket(
            trigger_type=trigger_type,
            severity=severity,
            ai_draft=data.ai_draft,
            status="PENDING",
            confidence_score=data.confidence_score,
            booking_amount=data.booking_amount,
            fraud_score=data.fraud_score
        )
        db.add(new_ticket)
        await db.commit()
        await db.refresh(new_ticket)
        
        # Broadcast the new ticket via WebSocket
        ticket_dict = {
            "id": new_ticket.id,
            "trigger_type": new_ticket.trigger_type,
            "severity": new_ticket.severity,
            "ai_draft": new_ticket.ai_draft,
            "status": new_ticket.status,
            "confidence_score": new_ticket.confidence_score,
            "booking_amount": new_ticket.booking_amount,
            "fraud_score": new_ticket.fraud_score,
            "created_at": new_ticket.created_at.isoformat() if new_ticket.created_at else None
        }
        await manager.broadcast_ticket(ticket_dict)
        logger.info(f"Created HITL Ticket ID {new_ticket.id} for trigger {trigger_type}")
        return new_ticket
        
    return None

async def resolve_ticket(ticket_id: int, action: str, new_draft: Optional[str], db: AsyncSession) -> HitlTicket:
    ticket = await db.get(HitlTicket, ticket_id)
    if not ticket:
        raise ValueError("Ticket not found")
        
    if action == "APPROVE":
        ticket.status = "APPROVED"
    elif action == "REJECT":
        ticket.status = "REJECTED"
    elif action == "EDIT":
        ticket.status = "EDITED"
        if new_draft:
            ticket.ai_draft = new_draft
            
    await db.commit()
    await db.refresh(ticket)
    
    await manager.broadcast_resolution(ticket.id, ticket.status)
    return ticket
