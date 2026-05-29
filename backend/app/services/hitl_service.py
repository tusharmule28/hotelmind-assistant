from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel

from app.models.orm.hitl_ticket import HITLTicket, HITLStatus, HITLPriority
from app.repositories.hitl_repo import HITLRepository
from app.services.websocket_manager import manager
from app.logger import logger


class HitlTriggerData(BaseModel):
    confidence_score: float
    booking_amount: Optional[float] = 0.0
    fraud_score: Optional[float] = 0.0
    ai_draft: str


async def evaluate_and_create_ticket(data: HitlTriggerData, db: AsyncSession) -> Optional[HITLTicket]:
    trigger_type = None
    priority = HITLPriority.LOW
    reason = ""
    
    if data.fraud_score and data.fraud_score > 0.7:
        trigger_type = "HIGH_FRAUD_SCORE"
        priority = HITLPriority.HIGH
        reason = f"Booking flagged for potential fraud (Score: {data.fraud_score})"
    elif data.booking_amount and data.booking_amount > 15000:
        trigger_type = "HIGH_VALUE_BOOKING"
        priority = HITLPriority.MEDIUM
        reason = f"High value booking amount (₹{data.booking_amount}) exceeds the alert limit"
    elif data.confidence_score < 0.65:
        trigger_type = "LOW_CONFIDENCE"
        priority = HITLPriority.MEDIUM
        reason = f"Intent classification confidence ({data.confidence_score}) is below threshold"
        
    if trigger_type:
        hitl_repo = HITLRepository(db)
        new_ticket = await hitl_repo.create_ticket(
            ticket_type=trigger_type,
            reason=reason,
            priority=priority,
            ai_draft=data.ai_draft,
            confidence_score=data.confidence_score,
            booking_amount=data.booking_amount,
            fraud_score=data.fraud_score
        )
        
        await db.commit()
        
        # Broadcast the new ticket via WebSocket
        ticket_dict = {
            "id": new_ticket.id,
            "trigger_type": new_ticket.type,  # compatibility mapping for frontend UI
            "severity": new_ticket.priority.value, # compatibility mapping for frontend UI
            "ai_draft": new_ticket.ai_draft,
            "status": new_ticket.status.value,
            "confidence_score": new_ticket.confidence_score,
            "booking_amount": new_ticket.booking_amount,
            "fraud_score": new_ticket.fraud_score,
            "created_at": new_ticket.created_at.isoformat() if new_ticket.created_at else None
        }
        await manager.broadcast_ticket(ticket_dict)
        logger.info(f"Created HITL Ticket ID {new_ticket.id} for trigger {trigger_type}")
        return new_ticket
        
    return None


async def resolve_ticket(ticket_id: int, action: str, new_draft: Optional[str], db: AsyncSession) -> HITLTicket:
    hitl_repo = HITLRepository(db)
    ticket = await hitl_repo.resolve(ticket_id, action, new_draft)
    if not ticket:
        raise ValueError("Ticket not found")
        
    await db.commit()
    await manager.broadcast_resolution(ticket.id, ticket.status.value)
    return ticket
