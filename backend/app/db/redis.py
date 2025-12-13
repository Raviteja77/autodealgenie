"""
Redis connection setup
"""

import redis.asyncio as redis

from app.core.config import settings


class RedisClient:
    """Redis connection manager"""

    client: redis.Redis = None

    @classmethod
    async def connect_redis(cls):
        """Connect to Redis"""
        cls.client = await redis.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True
        )
        print(f"Connected to Redis at {settings.REDIS_URL}")

    @classmethod
    async def close_redis(cls):
        """Close Redis connection"""
        if cls.client:
            await cls.client.close()
            print("Redis connection closed")

    @classmethod
    def get_client(cls):
        """Get Redis client"""
        return cls.client


redis_client = RedisClient()
