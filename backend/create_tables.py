import asyncio
from app.models.database import engine, Base
import app.models.orm  # registers all models for metadata creation

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("PostgreSQL tables created successfully.")

if __name__ == "__main__":
    asyncio.run(init_db())
