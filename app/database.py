import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

db_manager = DatabaseManager()

async def connect_to_mongo():
    """Establish async connection to MongoDB and create indexes."""
    try:
        db_manager.client = AsyncIOMotorClient(settings.MONGODB_URL)
        db_manager.db = db_manager.client[settings.DATABASE_NAME]
        
        # Ping the database to verify connection
        await db_manager.client.admin.command('ping')
        logger.info(f"Connected to MongoDB at {settings.MONGODB_URL}, Database: {settings.DATABASE_NAME}")
        
        # Ensure unique index on email
        users_collection = db_manager.db["users"]
        await users_collection.create_index("email", unique=True)
        logger.info("Unique index on 'email' ensured for 'users' collection.")
    except Exception as e:
        logger.warning(f"Could not connect to MongoDB at startup: {e}. Please ensure MongoDB is running.")

async def close_mongo_connection():
    """Close MongoDB connection pool."""
    if db_manager.client:
        db_manager.client.close()
        logger.info("MongoDB connection closed.")

def get_database() -> AsyncIOMotorDatabase:
    """Dependency helper to get the database instance."""
    if db_manager.db is None:
        # Fallback if connection wasn't initialized in lifespan
        db_manager.client = AsyncIOMotorClient(settings.MONGODB_URL)
        db_manager.db = db_manager.client[settings.DATABASE_NAME]
    return db_manager.db

def get_user_collection():
    """Helper to get users collection."""
    db = get_database()
    return db["users"]
