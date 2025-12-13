"""
MongoDB connection setup with Motor
"""

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings


class MongoDB:
    """MongoDB connection manager"""

    client: AsyncIOMotorClient = None

    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB"""
        cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
        print(f"Connected to MongoDB at {settings.MONGODB_URL}")

    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            print("MongoDB connection closed")

    @classmethod
    def get_database(cls):
        """Get database instance"""
        return cls.client[settings.MONGODB_DB_NAME]

    @classmethod
    def get_collection(cls, collection_name: str):
        """Get collection from database"""
        db = cls.get_database()
        return db[collection_name]


mongodb = MongoDB()
