"""
Generic async repository base class.

Usage:
    class HotelRepository(BaseRepository[Hotel, HotelCreate]):
        ...
"""
from __future__ import annotations

from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Thin async data-access layer over a single SQLAlchemy model."""

    model: Type[ModelT]

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Read ─────────────────────────────────────────────────────────────────

    async def get(self, record_id: int) -> Optional[ModelT]:
        """Return a single record by primary key, or None."""
        return await self.db.get(self.model, record_id)

    async def list(self, *, limit: int = 100, offset: int = 0) -> List[ModelT]:
        """Return a paginated list of records."""
        result = await self.db.execute(
            select(self.model).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    # ── Write ────────────────────────────────────────────────────────────────

    async def create(self, obj_in: dict) -> ModelT:
        """Persist a new record from a plain dict of field values."""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.flush()        # get auto-generated id without full commit
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: ModelT, updates: dict) -> ModelT:
        """Apply a dict of updates to an existing ORM instance."""
        for field, value in updates.items():
            if value is not None:
                setattr(db_obj, field, value)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: ModelT) -> None:
        """Hard-delete a record."""
        await self.db.delete(db_obj)
        await self.db.flush()
