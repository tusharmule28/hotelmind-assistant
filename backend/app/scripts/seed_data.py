import asyncio
import json
import os
import random
import chromadb
from sentence_transformers import SentenceTransformer

from app.models.database import engine, Base, AsyncSessionLocal
from app.models.orm.hotel import Hotel
from app.models.orm.room import Room
from app.models.orm.user import User
from app.models.orm.pricing import PricingSnapshot
from app.config import settings


async def seed_db():
    print("Connecting to PostgreSQL to drop and recreate database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully.")

    # 1. Load hotels from JSON file
    json_path = os.path.join(os.path.dirname(__file__), "hotels.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            hotels_data = json.load(f)
        print(f"Loaded {len(hotels_data)} hotels from JSON.")
    else:
        # Fallback generator
        print("JSON file not found! Generating random fallback hotels.")
        hotels_data = []
        locations = ["Koregaon Park", "Viman Nagar", "Hinjewadi", "Baner", "Shivajinagar"]
        for i in range(1, 11):
            hotels_data.append({
                "name": f"Hotel Oasis {i}",
                "city": random.choice(locations),
                "rating": round(random.uniform(3.5, 5.0), 1),
                "amenities": ["Pool", "Free WiFi", "Gym", "Restaurant"],
                "base_price": float(random.randint(3000, 10000))
            })

    async with AsyncSessionLocal() as session:
        # 2. Seed Default Users for Guest Memory demonstration
        print("Seeding test users...")
        default_user = User(
            name="default_user",
            email="default_user@hotelmind.ai",
            preferences={"budget": "premium", "amenities": ["Pool", "Spa", "Breakfast Included"]}
        )
        guest_user = User(
            name="guest",
            email="guest@hotelmind.ai",
            preferences={"budget": "mid-range", "amenities": ["Free WiFi", "Air Conditioning"]}
        )
        session.add(default_user)
        session.add(guest_user)
        await session.flush()  # Generate user IDs

        # 3. Seed Hotels, Rooms & Pricing Snapshots
        print("Seeding hotels, rooms, and pricing snapshots...")
        hotel_orm_list = []
        for i, h_data in enumerate(hotels_data, start=1):
            hotel = Hotel(
                id=i,
                name=h_data["name"],
                city=h_data["city"],
                rating=h_data["rating"],
                amenities=h_data["amenities"]
            )
            session.add(hotel)
            hotel_orm_list.append(hotel)
            
            # Seed Room Inventory (Standard, Deluxe, Suite)
            base_p = h_data["base_price"]
            room_configs = [
                {"type": "Standard", "multiplier": 1.0, "avail": True},
                {"type": "Deluxe", "multiplier": 1.4, "avail": True},
                {"type": "Suite", "multiplier": 2.2, "avail": True}
            ]
            
            for config in room_configs:
                price = round(base_p * config["multiplier"], 2)
                # Create a few rooms of each type
                for _ in range(random.randint(2, 5)):
                    room = Room(
                        hotel_id=i,
                        type=config["type"],
                        price=price,
                        availability=config["avail"]
                    )
                    session.add(room)

            # Seed initial PricingSnapshot for time-series record
            pricing_snapshot = PricingSnapshot(
                hotel_id=i,
                price=base_p
            )
            session.add(pricing_snapshot)
            
        await session.commit()
    print("PostgreSQL Database seeded successfully with users, hotels, and inventory.")

    # 4. ChromaDB Seeding for Semantic Search
    print("Initializing ChromaDB and SentenceTransformer...")
    os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)

    # Recreate the collection
    try:
        chroma_client.delete_collection("hotels")
    except Exception:
        pass

    collection = chroma_client.create_collection("hotels")
    model = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)

    documents = []
    metadatas = []
    ids = []

    for i, h in enumerate(hotels_data, start=1):
        amenities_str = ", ".join(h["amenities"])
        doc = (
            f"Hotel {h['name']} located in {h['city']}. "
            f"Starting price is {h['base_price']} INR per night. "
            f"Rating: {h['rating']} stars. "
            f"Amenities include: {amenities_str}."
        )
        documents.append(doc)
        metadatas.append({
            "id": i,
            "name": h["name"],
            "location": f"{h['city']}, Pune", # compatibility key for SearchAgent
            "city": h["city"],
            "price_per_night": float(h["base_price"]), # compatibility key for SearchAgent
            "rating": h["rating"]
        })
        ids.append(str(i))

    print("Generating vector embeddings and inserting into ChromaDB...")
    embeddings = model.encode(documents).tolist()

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )
    print("ChromaDB vector store seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_db())
