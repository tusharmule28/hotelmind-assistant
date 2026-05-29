# app/models/orm/__init__.py
# Re-export all ORM models so Alembic's autogenerate can discover them.
from app.models.orm.user import User
from app.models.orm.hotel import Hotel
from app.models.orm.room import Room
from app.models.orm.booking import Booking, BookingStatus
from app.models.orm.conversation import Conversation, Message
from app.models.orm.review import Review
from app.models.orm.hitl_ticket import HITLTicket, HITLStatus, HITLPriority
from app.models.orm.pricing import PricingSnapshot

__all__ = [
    "User",
    "Hotel",
    "Room",
    "Booking",
    "BookingStatus",
    "Conversation",
    "Message",
    "Review",
    "HITLTicket",
    "HITLStatus",
    "HITLPriority",
    "PricingSnapshot",
]
