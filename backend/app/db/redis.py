"""
Redis connection setup
"""

import logging

import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis connection manager"""

    client: redis.Redis = None

    @classmethod
    async def connect_redis(cls):
        """Connect to Redis"""
        try:
            cls.client = await redis.from_url(
                settings.REDIS_URL, encoding="utf-8", decode_responses=True
            )
            # Verify connection by pinging
            await cls.client.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise

    @classmethod
    async def close_redis(cls):
        """Close Redis connection"""
        if cls.client:
            await cls.client.close()
            logger.info("Redis connection closed")

    @classmethod
    def get_client(cls):
        """Get Redis client"""
        if cls.client is None:
            raise RuntimeError("Redis client is not initialized. Call connect_redis() first.")
        return cls.client


redis_client = RedisClient()
