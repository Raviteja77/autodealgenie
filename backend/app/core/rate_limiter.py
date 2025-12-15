"""
Rate limiting utility using Redis
Implements user-based rate limiting with sliding window
"""

import time

from app.db.redis import redis_client


class RateLimiter:
    """Redis-based rate limiter with sliding window"""

    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        """
        Initialize rate limiter

        Args:
            max_requests: Maximum number of requests allowed
            window_seconds: Time window in seconds (default: 3600 = 1 hour)
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def is_allowed(self, user_id: int) -> tuple[bool, int | None]:
        """
        Check if request is allowed for user

        Args:
            user_id: User ID to check rate limit for

        Returns:
            Tuple of (is_allowed, retry_after_seconds)
            - is_allowed: True if request is allowed
            - retry_after_seconds: Seconds to wait before retry (None if allowed)
        """
        client = redis_client.get_client()
        if not client:
            # If Redis is not available, allow request (fail-open)
            return True, None

        key = f"rate_limit:user:{user_id}"
        current_time = int(time.time())

        # Use Redis pipeline for atomic operations
        pipe = client.pipeline()

        # Remove old entries outside the window
        window_start = current_time - self.window_seconds
        pipe.zremrangebyscore(key, 0, window_start)

        # Count requests in current window
        pipe.zcard(key)

        # Add current request timestamp
        pipe.zadd(key, {str(current_time): current_time})

        # Set expiry on key
        pipe.expire(key, self.window_seconds)

        # Execute pipeline
        results = await pipe.execute()
        request_count = results[1]  # Get count result

        if request_count >= self.max_requests:
            # Get oldest request in window to calculate retry time
            oldest = await client.zrange(key, 0, 0, withscores=True)
            if oldest:
                oldest_timestamp = int(oldest[0][1])
                retry_after = oldest_timestamp + self.window_seconds - current_time
                return False, retry_after
            return False, self.window_seconds

        return True, None

    async def get_remaining_requests(self, user_id: int) -> int:
        """
        Get number of remaining requests for user

        Args:
            user_id: User ID to check

        Returns:
            Number of remaining requests
        """
        client = redis_client.get_client()
        if not client:
            return self.max_requests

        key = f"rate_limit:user:{user_id}"
        current_time = int(time.time())
        window_start = current_time - self.window_seconds

        # Remove old entries and count
        pipe = client.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        results = await pipe.execute()
        request_count = results[1]

        return max(0, self.max_requests - request_count)


# Singleton instance for car search rate limiting (100 requests per hour)
car_search_rate_limiter = RateLimiter(max_requests=100, window_seconds=3600)
