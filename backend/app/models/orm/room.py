from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.database import Base


class Room(Base):
    """Room inventory record per hotel."""

    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(80), nullable=False)          # Standard | Deluxe | Suite
    price = Column(Float, nullable=False)              # price per night (INR)
    availability = Column(Boolean, nullable=False, default=True)

    # Relationships
    hotel = relationship("Hotel", back_populates="rooms")
    bookings = relationship("Booking", back_populates="room", lazy="noload")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Room id={self.id} hotel_id={self.hotel_id} type={self.type!r}>"
