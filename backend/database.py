from motor.motor_asyncio import AsyncIOMotorClient
from config import get_settings

settings = get_settings()

client: AsyncIOMotorClient = None

async def connect_db():
    global client
    client = AsyncIOMotorClient(settings.mongodb_uri)
    print(f"[DB] Connected to MongoDB Atlas — database: '{settings.mongodb_db_name}'")

async def close_db():
    global client
    if client:
        client.close()
        print("[DB] MongoDB connection closed.")

def get_db():
    """Return the database instance. Use inside route dependencies."""
    return client[settings.mongodb_db_name]
