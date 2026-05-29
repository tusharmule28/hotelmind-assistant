import asyncio
import json
import random
import chromadb
from sentence_transformers import SentenceTransformer
from app.models.database import engine, Base, AsyncSessionLocal
from app.models.schema import Hotel, RoomInventory
from app.config import settings
import os

# Sample data pools for generation
LOCATIONS = ["Koregaon Park", "Viman Nagar", "Hinjewadi", "Baner", "Shivajinagar", "Kalyani Nagar", "Deccan Gymkhana", "Magarpatta"]
AMENITIES_POOL = ["Pool", "Free WiFi", "Gym", "Spa", "Restaurant", "Bar", "Room Service", "Parking", "Air Conditioning", "Breakfast Included"]
HOTEL_PREFIXES = ["The Grand", "Royal", "Oasis", "Urban", "Tech", "Sunset", "Emerald", "Platinum", "Cozy", "Luxury"]
HOTEL_SUFFIXES = ["Inn", "Resort", "Hotel", "Suites", "Lodge", "Retreat", "Residency"]

def generate_hotels(n=50):
    hotels = []
    for i in range(1, n + 1):
        name = f"{random.choice(HOTEL_PREFIXES)} {random.choice(HOTEL_SUFFIXES)} {random.choice(LOCATIONS)}"
        location = f"{random.choice(LOCATIONS)}, Pune"
        price = random.randint(1500, 15000)
        rating = round(random.uniform(3.0, 5.0), 1)
        amenities = random.sample(AMENITIES_POOL, k=random.randint(3, 8))
        recency = round(random.uniform(0.1, 1.0), 2)
        hotels.append({
            "id": i,
            "name": name,
            "location": location,
            "price_per_night": float(price),
            "rating": rating,
            "amenities": amenities,
            "recency_score": recency
        })
    return hotels

async def seed_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    hotels_data = generate_hotels(50)
    
    async with AsyncSessionLocal() as session:
        for h_data in hotels_data:
            hotel = Hotel(
                id=h_data["id"],
                name=h_data["name"],
                location=h_data["location"],
                price_per_night=h_data["price_per_night"],
                rating=h_data["rating"],
                amenities=h_data["amenities"],
                recency_score=h_data["recency_score"]
            )
            session.add(hotel)
            
            # Add rooms
            for r_type in ["Standard", "Deluxe", "Suite"]:
                total = random.randint(5, 20)
                room = RoomInventory(
                    hotel_id=hotel.id,
                    room_type=r_type,
                    total_rooms=total,
                    available_rooms=random.randint(2, total)
                )
                session.add(room)
        await session.commit()
    
    print("SQLite Database seeded successfully with 50 hotels and rooms.")
    
    # ChromaDB Seeding
    print("Initializing ChromaDB and SentenceTransformer...")
    # Ensure directory exists
    os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    
    # Delete collection if exists for clean seeding
    try:
        chroma_client.delete_collection("hotels")
    except Exception:
        pass
        
    collection = chroma_client.create_collection("hotels")
    model = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)
    
    documents = []
    metadatas = []
    ids = []
    
    for h in hotels_data:
        # Create a rich text document for semantic search
        amenities_str = ", ".join(h["amenities"])
        doc = f"Hotel {h['name']} located in {h['location']}. Price is {h['price_per_night']} rupees per night. Rating: {h['rating']} stars. Amenities include: {amenities_str}."
        
        documents.append(doc)
        metadatas.append({
            "id": h["id"],
            "name": h["name"],
            "location": h["location"],
            "price_per_night": h["price_per_night"],
            "rating": h["rating"],
            "recency_score": h["recency_score"]
        })
        ids.append(str(h["id"]))
        
    print("Generating embeddings and inserting into ChromaDB...")
    embeddings = model.encode(documents).tolist()
    
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )
    
    print("ChromaDB seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_db())
