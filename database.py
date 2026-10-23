import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# 1. Load environment variables from .env file
load_dotenv()

# 2. Read MongoDB URL and Database name from environment
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "chatbot_db")

# 3. Create asynchronous MongoDB client
client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]

# 4. Helper function to access the 'users' collection
def get_user_collection():
    return db["users"]

# 5. Helper function to access the 'chats' collection
def get_chat_collection():
    return db["chats"]

# 6. Helper function to access the 'messages' collection
def get_message_collection():
    return db["messages"]
