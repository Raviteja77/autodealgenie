"""
Rate limiting dependency for FastAPI endpoints
"""

from fastapi import HTTPException, Request, status

from app.core.rate_limiter import RateLimiter


class RateLimitMiddleware:
    """
    Dependency to enforce rate limits on endpoints
    """

    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        """
        Initialize rate limit dependency

        Args:
            max_requests: Maximum number of requests allowed
            window_seconds: Time window in seconds
        """
        self.limiter = RateLimiter(max_requests, window_seconds)

    async def __call__(self, request: Request):
        """
        Check rate limit for the request

        Args:
            request: FastAPI request object

        Raises:
            HTTPException: If rate limit is exceeded
        """
        # Get user ID from request state (set by auth dependency)
        user_id = getattr(request.state, "user_id", None)

        # If no user ID, use IP address for anonymous rate limiting
        if not user_id:
            client_ip = request.client.host if request.client else "unknown"
            # Use a hash of IP for anonymous users
            user_id = f"ip:{client_ip}"

        # Check rate limit
        is_allowed, retry_after = await self.limiter.is_allowed(user_id)

        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)} if retry_after else {},
            )

        # Add rate limit info to response headers
        remaining = await self.limiter.get_remaining_requests(user_id)
        request.state.rate_limit_remaining = remaining


# Pre-configured rate limiters for different use cases

# Strict rate limit for authentication endpoints (10 attempts per 15 minutes)
auth_rate_limit = RateLimitMiddleware(max_requests=10, window_seconds=900)

# Moderate rate limit for API endpoints (100 requests per hour)
api_rate_limit = RateLimitMiddleware(max_requests=100, window_seconds=3600)

# Generous rate limit for read-only endpoints (500 requests per hour)
read_rate_limit = RateLimitMiddleware(max_requests=500, window_seconds=3600)

# Strict rate limit for password reset (3 attempts per hour)
password_reset_rate_limit = RateLimitMiddleware(max_requests=3, window_seconds=3600)
