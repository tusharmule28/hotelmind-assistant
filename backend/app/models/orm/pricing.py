from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.database import Base


class PricingSnapshot(Base):
    """Point-in-time price record for a hotel (time-series tracking)."""

    __tablename__ = "pricing_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(
        Integer,
        ForeignKey("hotels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Price per night in INR at snapshot time
    price = Column(Float, nullable=False)
    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    hotel = relationship("Hotel", back_populates="pricing_snapshots")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<PricingSnapshot id={self.id} hotel_id={self.hotel_id} price={self.price}>"
