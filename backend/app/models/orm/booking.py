import enum
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Date, DateTime,
    ForeignKey, Enum as SAEnum,
)
from sqlalchemy.orm import relationship
from app.models.database import Base


class BookingStatus(str, enum.Enum):
    HOLD = "HOLD"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class Booking(Base):
    """A reservation record linking user ↔ hotel ↔ room."""

    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)

    # Nullable for backwards-compat with old /reserve endpoint (no dates provided)
    check_in = Column(Date, nullable=True)
    check_out = Column(Date, nullable=True)

    status = Column(SAEnum(BookingStatus), nullable=False, default=BookingStatus.HOLD)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    # Hold expiry (15 min window)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="bookings")
    hotel = relationship("Hotel", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Booking id={self.id} status={self.status} hotel_id={self.hotel_id}>"
