from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timezone
from app.models.database import Base

class BookingStatus(str, enum.Enum):
    HOLD = "HOLD"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"

class Hotel(Base):
    __tablename__ = "hotels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String, index=True)
    price_per_night = Column(Float)
    rating = Column(Float)
    amenities = Column(JSON)
    recency_score = Column(Float)
    
    rooms = relationship("RoomInventory", back_populates="hotel")
    bookings = relationship("Booking", back_populates="hotel")

class RoomInventory(Base):
    __tablename__ = "room_inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"))
    room_type = Column(String)
    total_rooms = Column(Integer)
    available_rooms = Column(Integer)
    
    hotel = relationship("Hotel", back_populates="rooms")
    bookings = relationship("Booking", back_populates="room")

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"))
    room_id = Column(Integer, ForeignKey("room_inventory.id"))
    status = Column(Enum(BookingStatus), default=BookingStatus.HOLD)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime)
    
    hotel = relationship("Hotel", back_populates="bookings")
    room = relationship("RoomInventory", back_populates="bookings")

class HitlTicket(Base):
    __tablename__ = "hitl_tickets"

    id = Column(Integer, primary_key=True, index=True)
    trigger_type = Column(String)
    severity = Column(String)
    ai_draft = Column(String)
    status = Column(String, default="PENDING")
    confidence_score = Column(Float, nullable=True)
    booking_amount = Column(Float, nullable=True)
    fraud_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class GuestMemory(Base):
    __tablename__ = "guest_memory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, unique=True)
    preferences = Column(JSON, default=dict)
    booking_history_cache = Column(JSON, default=list)

