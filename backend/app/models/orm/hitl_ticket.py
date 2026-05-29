import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Enum as SAEnum
from app.models.database import Base


class HITLStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EDITED = "EDITED"


class HITLPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class HITLTicket(Base):
    """Human-in-the-Loop escalation ticket."""

    __tablename__ = "hitl_tickets"

    id = Column(Integer, primary_key=True, index=True)
    # Machine-readable trigger type: HIGH_FRAUD_SCORE | HIGH_VALUE_BOOKING | LOW_CONFIDENCE
    type = Column(String(60), nullable=False, index=True)
    reason = Column(Text, nullable=True)               # human-readable explanation
    status = Column(
        SAEnum(HITLStatus),
        nullable=False,
        default=HITLStatus.PENDING,
        index=True,
    )
    priority = Column(
        SAEnum(HITLPriority),
        nullable=False,
        default=HITLPriority.LOW,
    )
    # Snapshot of the AI response that triggered this ticket
    ai_draft = Column(Text, nullable=True)

    # Contextual scores
    confidence_score = Column(Float, nullable=True)
    booking_amount = Column(Float, nullable=True)
    fraud_score = Column(Float, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<HITLTicket id={self.id} type={self.type!r} status={self.status}>"
