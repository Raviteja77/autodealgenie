"""
Tests for rate limiter functionality
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.rate_limiter import RateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_allows_requests_within_limit():
    """Test that requests within limit are allowed"""
    limiter = RateLimiter(max_requests=5, window_seconds=60)

    # Mock Redis client with pipeline methods
    mock_redis = AsyncMock()
    mock_pipeline = AsyncMock()
    mock_pipeline.zremrangebyscore = MagicMock(return_value=mock_pipeline)
    mock_pipeline.zcard = MagicMock(return_value=mock_pipeline)
    mock_pipeline.zadd = MagicMock(return_value=mock_pipeline)
    mock_pipeline.expire = MagicMock(return_value=mock_pipeline)
    mock_pipeline.execute = AsyncMock(return_value=[None, 0, None, None])  # Count is 0
    mock_redis.pipeline.return_value = mock_pipeline

    with patch("app.core.rate_limiter.redis_client.get_client", return_value=mock_redis):
        is_allowed, retry_after = await limiter.is_allowed(user_id=1)

        assert is_allowed is True
        assert retry_after is None


@pytest.mark.asyncio
async def test_rate_limiter_blocks_requests_over_limit():
    """Test that requests over limit are blocked"""
    limiter = RateLimiter(max_requests=5, window_seconds=60)

    # Mock Redis client - simulate 5 requests already made
    mock_redis = AsyncMock()
    mock_pipeline = AsyncMock()
    mock_pipeline.zremrangebyscore = MagicMock(return_value=mock_pipeline)
    mock_pipeline.zcard = MagicMock(return_value=mock_pipeline)
    mock_pipeline.zadd = MagicMock(return_value=mock_pipeline)
    mock_pipeline.expire = MagicMock(return_value=mock_pipeline)
    mock_pipeline.execute = AsyncMock(return_value=[None, 5, None, None])  # Count is 5 (at limit)
    mock_redis.pipeline.return_value = mock_pipeline
    mock_redis.zrange = AsyncMock(return_value=[("timestamp", 1000)])

    with patch("app.core.rate_limiter.redis_client.get_client", return_value=mock_redis):
        is_allowed, retry_after = await limiter.is_allowed(user_id=1)

        assert is_allowed is False
        assert retry_after is not None
        assert retry_after > 0


@pytest.mark.asyncio
async def test_rate_limiter_fail_open_when_redis_unavailable():
    """Test that limiter allows requests when Redis is unavailable (fail-open)"""
    limiter = RateLimiter(max_requests=5, window_seconds=60)

    with patch("app.core.rate_limiter.redis_client.get_client", return_value=None):
        is_allowed, retry_after = await limiter.is_allowed(user_id=1)

        assert is_allowed is True
        assert retry_after is None


@pytest.mark.asyncio
async def test_get_remaining_requests():
    """Test getting remaining request count"""
    limiter = RateLimiter(max_requests=10, window_seconds=60)

    # Mock Redis client - simulate 3 requests made
    mock_redis = AsyncMock()
    mock_pipeline = AsyncMock()
    mock_pipeline.zremrangebyscore = MagicMock(return_value=mock_pipeline)
    mock_pipeline.zcard = MagicMock(return_value=mock_pipeline)
    mock_pipeline.execute = AsyncMock(return_value=[None, 3])  # Count is 3
    mock_redis.pipeline.return_value = mock_pipeline

    with patch("app.core.rate_limiter.redis_client.get_client", return_value=mock_redis):
        remaining = await limiter.get_remaining_requests(user_id=1)

        assert remaining == 7  # 10 - 3


@pytest.mark.asyncio
async def test_rate_limiter_different_users():
    """Test that different users have separate rate limits"""
    limiter = RateLimiter(max_requests=5, window_seconds=60)

    # Mock Redis client
    mock_redis = AsyncMock()
    mock_pipeline = AsyncMock()
    mock_pipeline.zremrangebyscore = MagicMock(return_value=mock_pipeline)
    mock_pipeline.zcard = MagicMock(return_value=mock_pipeline)
    mock_pipeline.zadd = MagicMock(return_value=mock_pipeline)
    mock_pipeline.expire = MagicMock(return_value=mock_pipeline)

    # First user - 2 requests
    mock_pipeline.execute = AsyncMock(return_value=[None, 2, None, None])
    mock_redis.pipeline.return_value = mock_pipeline

    with patch("app.core.rate_limiter.redis_client.get_client", return_value=mock_redis):
        is_allowed_1, _ = await limiter.is_allowed(user_id=1)

        # Second user - 4 requests
        mock_pipeline.execute = AsyncMock(return_value=[None, 4, None, None])
        is_allowed_2, _ = await limiter.is_allowed(user_id=2)

        # Both should be allowed as they're under the limit
        assert is_allowed_1 is True
        assert is_allowed_2 is True
