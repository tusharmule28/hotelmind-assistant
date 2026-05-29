from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship
from app.models.database import Base


class User(Base):
    """Registered or guest user with preference storage."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(320), nullable=False, unique=True, index=True)
    # Flexible JSON blob: {"budget": "mid", "amenities": ["Pool", "WiFi"]}
    preferences = Column(JSON, nullable=False, default=dict)

    # Relationships
    bookings = relationship("Booking", back_populates="user", lazy="noload")
    conversations = relationship("Conversation", back_populates="user", lazy="noload")
    reviews = relationship("Review", back_populates="user", lazy="noload")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User id={self.id} email={self.email!r}>"
