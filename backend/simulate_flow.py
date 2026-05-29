import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000/api"
MOCK_USER_ID = "simulated_user_1"

async def simulate_chat(client, message):
    print(f"\n[User] {message}")
    response = await client.post(f"{BASE_URL}/chat", json={"message": message, "user_id": MOCK_USER_ID})
    data = response.json()
    print(f"[AI] {data.get('reply')}")
    if "results" in data:
        print(f"     => Found {len(data['results'])} hotels")
    if "booking" in data:
        print(f"     => Booking ID: {data['booking']['booking_id']}")
    if "hitl_ticket_id" in data:
        print(f"     => 🔥 HITL Escalation! Ticket ID: {data['hitl_ticket_id']}")
    return data

async def run_simulation():
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("--- STARTING SIMULATION ---")
        
        # 1. Search Flow
        await simulate_chat(client, "I need a hotel in Pune under 4000 rupees with a pool.")
        
        # 2. Booking Flow
        # We need to simulate the booking of a specific hotel to trigger the hold
        await simulate_chat(client, "Book a deluxe room at the Grand Hyatt Pune.")
        
        # 3. Confirmation
        # The user confirms the booking
        await simulate_chat(client, "Yes, confirm the reservation.")
        
        # 4. HITL Escalation (Intent confusion / high value / unknown)
        print("\n--- TRIGGERING HITL ESCALATION ---")
        await simulate_chat(client, "I want to complain about a charge of 50000 rupees on my card from last week! I didn't authorize this!")

if __name__ == "__main__":
    asyncio.run(run_simulation())
