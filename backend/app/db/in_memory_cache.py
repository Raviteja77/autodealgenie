"""
In-memory caching implementation using cachetools
Used as a fallback when Redis is not available (e.g., GCP Free Tier)
"""

import logging
from typing import Any

from cachetools import TTLCache

logger = logging.getLogger(__name__)


class InMemoryCache:
    """In-memory cache using cachetools TTLCache"""

    def __init__(self, maxsize: int = 1000, ttl: int = 3600):
        """
        Initialize in-memory cache

        Args:
            maxsize: Maximum number of items to store
            ttl: Time-to-live in seconds (default 1 hour)
        """
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)
        logger.info(f"Initialized in-memory cache (maxsize={maxsize}, ttl={ttl}s)")

    async def get(self, key: str) -> Any | None:
        """Get value from cache"""
        value = self.cache.get(key)
        if value is not None:
            logger.debug(f"Cache hit: {key}")
        else:
            logger.debug(f"Cache miss: {key}")
        return value

    async def set(self, key: str, value: Any, ex: int | None = None) -> None:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ex: Expiry in seconds (Note: Uses cache default TTL, not per-key expiry.
                For per-key TTL support, use Redis with USE_REDIS=true)
        """
        self.cache[key] = value
        logger.debug(f"Cache set: {key}")
        if ex is not None:
            logger.debug(
                "Note: In-memory cache uses default TTL. Per-key expiry requires USE_REDIS=true"
            )

    async def delete(self, key: str) -> None:
        """Delete key from cache"""
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache delete: {key}")

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        return key in self.cache

    async def ping(self) -> bool:
        """Health check - always returns True for in-memory cache"""
        return True

    async def close(self) -> None:
        """Close connection - no-op for in-memory cache"""
        logger.info("In-memory cache closed (no-op)")

    def clear(self) -> None:
        """Clear all cached items"""
        self.cache.clear()
        logger.info("In-memory cache cleared")


# Global in-memory cache instance
in_memory_cache = InMemoryCache()
