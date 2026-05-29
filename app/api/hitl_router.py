from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from pydantic import BaseModel
from app.models.database import get_db
from app.models.schema import HitlTicket
from app.services.websocket_manager import manager
from app.services.hitl_service import resolve_ticket

router = APIRouter(prefix="/hitl", tags=["hitl"])

class ResolveRequest(BaseModel):
    ticket_id: int
    action: str  # "APPROVE", "REJECT", "EDIT"
    new_draft: str = None

@router.get("/tickets")
async def get_tickets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(HitlTicket).order_by(HitlTicket.created_at.desc()))
    tickets = result.scalars().all()
    return tickets

@router.post("/resolve")
async def resolve_hitl_ticket(request: ResolveRequest, db: AsyncSession = Depends(get_db)):
    try:
        ticket = await resolve_ticket(request.ticket_id, request.action, request.new_draft, db)
        return {"status": "success", "ticket_id": ticket.id, "new_status": ticket.status}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # In a real app we might handle client messages here. For now, it just listens.
    except WebSocketDisconnect:
        manager.disconnect(websocket)
