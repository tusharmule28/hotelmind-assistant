from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.services.websocket_manager import manager
from app.services.hitl_service import resolve_ticket
from app.repositories.hitl_repo import HITLRepository
from app.schemas.hitl import ResolveRequest

router = APIRouter(prefix="/hitl", tags=["hitl"])


@router.get("/tickets")
async def get_tickets(db: AsyncSession = Depends(get_db)):
    """Retrieve all Human-in-the-Loop tickets, sorted by creation date."""
    hitl_repo = HITLRepository(db)
    tickets = await hitl_repo.list_all()
    
    # Map for frontend compatibility if needed
    compat_tickets = []
    for t in tickets:
        compat_tickets.append({
            "id": t.id,
            "trigger_type": t.type,
            "severity": t.priority.value,
            "ai_draft": t.ai_draft,
            "status": t.status.value,
            "confidence_score": t.confidence_score,
            "booking_amount": t.booking_amount,
            "fraud_score": t.fraud_score,
            "created_at": t.created_at.isoformat() if t.created_at else None
        })
    return compat_tickets


@router.post("/resolve")
async def resolve_hitl_ticket(request: ResolveRequest, db: AsyncSession = Depends(get_db)):
    """Resolve a pending Human-in-the-Loop ticket."""
    try:
        ticket = await resolve_ticket(request.ticket_id, request.action, request.new_draft, db)
        return {"status": "success", "ticket_id": ticket.id, "new_status": ticket.status.value}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time ticket alerts and resolutions."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive; handle potential incoming messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
