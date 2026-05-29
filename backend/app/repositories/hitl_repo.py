from __future__ import annotations
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.orm.hitl_ticket import HITLTicket, HITLStatus, HITLPriority
from app.repositories.base import BaseRepository


class HITLRepository(BaseRepository[HITLTicket]):
    model = HITLTicket

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_pending(self) -> List[HITLTicket]:
        result = await self.db.execute(
            select(HITLTicket)
            .where(HITLTicket.status == HITLStatus.PENDING)
            .order_by(HITLTicket.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_all(self) -> List[HITLTicket]:
        result = await self.db.execute(
            select(HITLTicket).order_by(HITLTicket.created_at.desc())
        )
        return list(result.scalars().all())

    async def create_ticket(
        self,
        ticket_type: str,
        reason: Optional[str],
        priority: HITLPriority,
        ai_draft: Optional[str] = None,
        confidence_score: Optional[float] = None,
        booking_amount: Optional[float] = None,
        fraud_score: Optional[float] = None,
    ) -> HITLTicket:
        return await self.create(
            {
                "type": ticket_type,
                "reason": reason,
                "status": HITLStatus.PENDING,
                "priority": priority,
                "ai_draft": ai_draft,
                "confidence_score": confidence_score,
                "booking_amount": booking_amount,
                "fraud_score": fraud_score,
            }
        )

    async def resolve(
        self,
        ticket_id: int,
        action: str,
        new_draft: Optional[str] = None,
    ) -> Optional[HITLTicket]:
        ticket = await self.get(ticket_id)
        if not ticket:
            return None
        action_map = {
            "APPROVE": HITLStatus.APPROVED,
            "REJECT": HITLStatus.REJECTED,
            "EDIT": HITLStatus.EDITED,
        }
        ticket.status = action_map.get(action, HITLStatus.PENDING)
        if action == "EDIT" and new_draft:
            ticket.ai_draft = new_draft
        self.db.add(ticket)
        await self.db.flush()
        await self.db.refresh(ticket)
        return ticket
