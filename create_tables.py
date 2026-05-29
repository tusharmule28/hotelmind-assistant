import asyncio
from app.models.database import engine, Base
from app.models.schema import *

async def init_db():
    async with engine.begin() as conn:
        # Create all tables (this will skip existing ones if they exist, but for sqlite we might want to drop if we changed schemas, but let's just create)
        # Actually, if we just create, sqlite might not update. We will create tables only. 
        # If it complains, we will have to use Alembic or drop/create.
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully.")

if __name__ == "__main__":
    asyncio.run(init_db())
