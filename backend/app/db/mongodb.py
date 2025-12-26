"""
MongoDB connection setup with Motor
"""

import logging

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings

logger = logging.getLogger(__name__)


class MongoDB:
    """MongoDB connection manager"""

    client: AsyncIOMotorClient = None

    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB"""
        try:
            cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
            # Verify connection by pinging the database
            await cls.client.admin.command("ping")
            logger.info(f"Successfully connected to MongoDB at {settings.MONGODB_URL}")
            logger.info(f"Using database: {settings.MONGODB_DB_NAME}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            logger.info("MongoDB connection closed")

    @classmethod
    def get_database(cls):
        """Get database instance"""
        if cls.client is None:
            raise RuntimeError(
                "MongoDB client is not initialized. Call connect_db() first."
            )
        return cls.client[settings.MONGODB_DB_NAME]

    @classmethod
    def get_collection(cls, collection_name: str):
        """Get collection from database"""
        if cls.client is None:
            raise RuntimeError(
                "MongoDB client is not initialized. Call connect_db() first."
            )
        db = cls.get_database()
        return db[collection_name]


mongodb = MongoDB()
