from __future__ import annotations
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.orm.conversation import Conversation, Message
from app.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    model = Conversation

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_by_session(self, session_id: str) -> Optional[Conversation]:
        result = await self.db.execute(
            select(Conversation).where(Conversation.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create(
        self, session_id: str, user_id: Optional[int] = None
    ) -> Conversation:
        conv = await self.get_by_session(session_id)
        if conv:
            return conv
        return await self.create({"session_id": session_id, "user_id": user_id})


class MessageRepository(BaseRepository[Message]):
    model = Message

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_by_conversation(self, conversation_id: int) -> List[Message]:
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp.asc())
        )
        return list(result.scalars().all())

    async def append(
        self, conversation_id: int, role: str, content: str
    ) -> Message:
        return await self.create(
            {"conversation_id": conversation_id, "role": role, "content": content}
        )
