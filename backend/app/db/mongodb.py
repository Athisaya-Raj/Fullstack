"""
MongoDB connection setup for JurisLink.
Provides database client and collection access.
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from ..core.config import settings


db_client: AsyncIOMotorClient = None


async def connect_to_db():
    """
    Establish connection to MongoDB.
    Called on application startup.
    """
    global db_client
    db_client = AsyncIOMotorClient(settings.MONGODB_URI)
    # Verify connection with a ping
    await db_client.admin.command("ping")
    print("✓ Connected to MongoDB")


async def close_db_connection():
    """
    Close MongoDB connection.
    Called on application shutdown.
    """
    global db_client
    if db_client:
        db_client.close()
        print("✓ Closed MongoDB connection")


def get_database() -> AsyncIOMotorDatabase:
    """
    Get the JurisLink database instance.
    
    Returns:
        AsyncIOMotorDatabase instance for the configured database name
    """
    return db_client[settings.DATABASE_NAME]
