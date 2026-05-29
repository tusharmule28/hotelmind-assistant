from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.database import Base


class Review(Base):
    """Guest review with AI-assisted response draft."""

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Float, nullable=False)             # 1.0 – 5.0
    text = Column(Text, nullable=False)
    # e.g. "POSITIVE" | "NEGATIVE" | "NEUTRAL" — set by sentiment analysis
    sentiment = Column(String(20), nullable=True)
    # AI-generated draft reply for staff to approve/edit
    ai_draft_response = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", back_populates="reviews")
    hotel = relationship("Hotel", back_populates="reviews")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Review id={self.id} hotel_id={self.hotel_id} rating={self.rating}>"
