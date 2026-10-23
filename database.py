import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# 1. Load .env file
load_dotenv()

# 2. Get MongoDB URL and Database name from .env
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "chatbot_db")

# 3. Create MongoDB connection client
client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]

# 4. Function to get 'users' collection
def get_user_collection():
    return db["users"]
