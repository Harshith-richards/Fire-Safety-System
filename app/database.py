from pymongo import MongoClient
from .config import Config

try:
    client = MongoClient(Config.MONGO_URI)
    db = client[Config.DB_NAME]
    users_collection = db['users']
    logs_collection = db['logs']
    print("✅ Connected to MongoDB successfully.")
except Exception as e:
    print(f"❌ Error connecting to MongoDB: {e}")
    users_collection = None
    logs_collection = None
