from sqlalchemy import Column, Integer, String, Float, JSON
from sqlalchemy.orm import relationship
from app.models.database import Base


class Hotel(Base):
    """Hotel catalogue entry."""

    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    city = Column(String(120), nullable=False, index=True)
    rating = Column(Float, nullable=False, default=0.0)
    # e.g. ["Pool", "Free WiFi", "Gym"]
    amenities = Column(JSON, nullable=False, default=list)

    # Relationships
    rooms = relationship("Room", back_populates="hotel", lazy="noload")
    bookings = relationship("Booking", back_populates="hotel", lazy="noload")
    reviews = relationship("Review", back_populates="hotel", lazy="noload")
    pricing_snapshots = relationship(
        "PricingSnapshot", back_populates="hotel", lazy="noload"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Hotel id={self.id} name={self.name!r} city={self.city!r}>"
