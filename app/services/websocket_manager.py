from typing import List, Dict, Any
from fastapi import WebSocket
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    async def broadcast_ticket(self, ticket_data: Dict[str, Any]):
        message = json.dumps({"type": "NEW_TICKET", "data": ticket_data})
        await self.broadcast(message)

    async def broadcast_resolution(self, ticket_id: int, status: str):
        message = json.dumps({"type": "TICKET_RESOLVED", "data": {"ticket_id": ticket_id, "status": status}})
        await self.broadcast(message)

manager = ConnectionManager()
