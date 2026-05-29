from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.intent_classifier import IntentClassifierService
from app.services.search_agent import SearchAgentService
from app.services.booking_agent import BookingAgentService
from app.models.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.logger import logger
from typing import Any, Dict
from sqlalchemy.future import select
from app.models.schema import GuestMemory
from app.services.hitl_service import evaluate_and_create_ticket, HitlTriggerData

router = APIRouter(prefix="/api", tags=["chat"])

classifier_service = IntentClassifierService()
search_agent = SearchAgentService()

def get_intent_classifier() -> IntentClassifierService:
    return classifier_service

def get_search_agent() -> SearchAgentService:
    return search_agent

@router.post("/chat")
async def chat(
    request: ChatRequest,
    classifier: IntentClassifierService = Depends(get_intent_classifier),
    search_agent: SearchAgentService = Depends(get_search_agent),
    db: AsyncSession = Depends(get_db)
):
    """
    Orchestrates the chat request.
    """
    logger.info("received_chat_request", query_length=len(request.message))
    
    result = await classifier.classify_intent(request.message)
    intent = result["intent"]
    confidence = result["confidence"]
    
    # Fetch Guest Memory
    guest_memory_result = await db.execute(select(GuestMemory).where(GuestMemory.user_id == request.user_id))
    guest_memory_obj = guest_memory_result.scalar_one_or_none()
    guest_memory = None
    if guest_memory_obj:
        guest_memory = {
            "preferences": guest_memory_obj.preferences,
            "booking_history_cache": guest_memory_obj.booking_history_cache
        }
    
    if confidence < settings.CONFIDENCE_THRESHOLD:
        intent = "clarification_required"
        
    response_data: Dict[str, Any] = {
        "intent": intent,
        "confidence": confidence,
        "reply": "I'm not sure how to help with that."
    }
    
    if intent == "SEARCH_HOTEL":
        results = await search_agent.search(request.message, guest_memory=guest_memory)
        response_data["results"] = results
        
        if results:
            reply = "Here are the top hotels I found for you:\n"
            for r in results:
                reply += f"- **{r['name']}** in {r['location']} (Rating: {r['rating']}, Price: ₹{r['price_per_night']}). {r['explanation']}\n"
            response_data["reply"] = reply
        else:
            response_data["reply"] = "I couldn't find any hotels matching your criteria."
            
    elif intent == "BOOK_ROOM":
        # Extract booking params using search agent's parameter extraction (reused for simplicity)
        params = await search_agent.extract_parameters(request.message)
        location_hint = params.get("location")
        
        # We need a hotel to book. Let's do a quick search based on the query to find the best match.
        results = await search_agent.search(request.message, top_k=1)
        if not results:
            response_data["reply"] = "I need to know which hotel you want to book. Please specify a hotel name or location."
        else:
            hotel = results[0]
            # Try to guess room type from query, default to Standard
            room_type = "Standard"
            lower_msg = request.message.lower()
            if "deluxe" in lower_msg:
                room_type = "Deluxe"
            elif "suite" in lower_msg:
                room_type = "Suite"
                
            booking_agent = BookingAgentService(db)
            hold_result = await booking_agent.hold_booking(hotel_id=hotel["id"], room_type=room_type)
            
            if hold_result.get("success"):
                response_data["booking"] = hold_result
                response_data["reply"] = f"Great! I have held a {room_type} room for you at {hotel['name']} for 15 minutes. Booking ID: {hold_result['booking_id']}. Please confirm to proceed."
            else:
                response_data["reply"] = f"Sorry, {room_type} rooms are currently not available at {hotel['name']}."

    elif intent == "clarification_required":
        response_data["reply"] = "I'm not quite sure what you mean. Could you please clarify if you want to search for a hotel or book a room?"
        
    # Evaluate HITL Triggers
    booking_amount = 0.0
    if intent == "BOOK_ROOM" and "booking" in response_data:
        # Dummy value for testing, normally this would be calculated from the booking details
        booking_amount = hotel.get('price_per_night', 0) * 2 # assume 2 nights
        
    hitl_data = HitlTriggerData(
        confidence_score=confidence,
        booking_amount=booking_amount,
        fraud_score=0.8 if booking_amount > 15000 else 0.1, # mock fraud score
        ai_draft=response_data["reply"]
    )
    
    ticket = await evaluate_and_create_ticket(hitl_data, db)
    if ticket:
        response_data["hitl_ticket_id"] = ticket.id
        # Optional: override reply if we want to block the action until staff review
        if ticket.status == "PENDING":
            response_data["reply"] = "Your request has been flagged for staff review and will be processed shortly."
            
    return response_data

