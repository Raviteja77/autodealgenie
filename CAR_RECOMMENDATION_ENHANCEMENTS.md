# Car Recommendation Service Enhancements

This document describes the enhancements made to the car recommendation service to improve performance, reliability, and functionality.

## Overview

The car recommendation service has been enhanced with the following features:

1. **Redis Caching Layer** - Improves response times for frequent searches
2. **Rate Limiting** - Prevents abuse with user-based request limits
3. **Retry Logic** - Handles transient API errors gracefully
4. **Search History** - Stores all searches in MongoDB for analytics
5. **Webhook Notifications** - Alerts users when matching vehicles are found

## 1. Redis Caching Layer

### Implementation

- Cache key is generated from search parameters using MD5 hash
- Results are cached for 15 minutes (900 seconds)
- Cache is automatically populated after successful API calls
- Cache misses trigger fresh API requests

### Benefits

- Reduces load on external MarketCheck API
- Improves response times for popular searches
- Cost savings on API calls

### Cache Key Format

```
car_search:<md5_hash_of_parameters>
```

### Usage

Caching is transparent - no code changes needed. The service automatically:
- Checks cache before making API calls
- Stores results after successful API calls
- Returns cached data when available

## 2. Rate Limiting

### Configuration

- **Limit**: 100 requests per hour per user
- **Window**: Sliding window of 3600 seconds
- **Storage**: Redis sorted sets
- **Behavior**: Fail-open (allows requests if Redis unavailable)

### Implementation Details

- Uses Redis sorted sets with timestamps
- Automatically removes expired entries
- Returns `429 Too Many Requests` when limit exceeded
- Includes `Retry-After` header with wait time

### API Response

When rate limited:
```json
{
  "detail": "Rate limit exceeded. Please retry after 1234 seconds."
}
```

HTTP Status: `429 TOO MANY REQUESTS`

Headers:
```
Retry-After: 1234
```

### Monitoring

Track rate limit usage:
```python
from app.core.rate_limiter import car_search_rate_limiter

remaining = await car_search_rate_limiter.get_remaining_requests(user_id)
```

## 3. Retry Logic

### Configuration

- **Max Attempts**: 3
- **Retry Conditions**: `ConnectionError`, `TimeoutError`
- **Wait Strategy**: Exponential backoff (2s, 4s, 8s)
- **Logging**: Warnings logged before each retry

### Implementation

Uses `tenacity` library with decorator:

```python
@retry(
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    before_sleep=before_sleep_log(logger, logging.WARNING),
)
async def _search_marketcheck_with_retry(...):
    # API call logic
```

### Behavior

1. First attempt fails → Wait 2 seconds → Retry
2. Second attempt fails → Wait 4 seconds → Retry
3. Third attempt fails → Raise exception

Only transient errors are retried. Other errors fail immediately.

## 4. Search History Storage

### Data Model

Stored in MongoDB collection `search_history`:

```json
{
  "_id": "ObjectId",
  "user_id": 123,
  "search_criteria": {
    "make": "Toyota",
    "model": "RAV4",
    "price_min": 20000,
    "price_max": 30000
  },
  "result_count": 25,
  "top_vehicles": [...],
  "timestamp": "2025-12-14T10:30:00Z",
  "session_id": null
}
```

### Features

- **Create Records**: Automatically logs all searches
- **User History**: Retrieve search history for a user
- **Popular Searches**: Aggregate popular makes/models
- **Privacy**: User can delete their own history

### API Usage

```python
from app.repositories.search_history_repository import search_history_repository

# Get user's search history
history = await search_history_repository.get_user_history(
    user_id=1, 
    limit=50, 
    skip=0
)

# Get popular searches (last 7 days)
popular = await search_history_repository.get_popular_searches(
    limit=10, 
    days=7
)

# Delete user history (GDPR compliance)
deleted = await search_history_repository.delete_user_history(user_id=1)
```

## 5. Webhook Notifications

### Overview

Users can subscribe to webhook notifications to receive alerts when new vehicles matching their criteria become available.

### Database Model

PostgreSQL table `webhook_subscriptions`:

```sql
CREATE TABLE webhook_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    webhook_url VARCHAR(512) NOT NULL,
    status VARCHAR(20) NOT NULL,  -- ACTIVE, INACTIVE, FAILED
    
    -- Criteria filters
    make VARCHAR(100),
    model VARCHAR(100),
    price_min FLOAT,
    price_max FLOAT,
    year_min INTEGER,
    year_max INTEGER,
    mileage_max INTEGER,
    
    -- Security & metadata
    secret_token VARCHAR(255),
    last_triggered TIMESTAMP,
    failure_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

### API Endpoints

#### Create Subscription

```
POST /api/v1/webhooks/
Authorization: Bearer <token>

{
  "webhook_url": "https://example.com/webhook",
  "secret_token": "my-secret",
  "make": "Toyota",
  "model": "RAV4",
  "price_min": 20000,
  "price_max": 30000,
  "year_min": 2020,
  "mileage_max": 50000
}
```

#### List Subscriptions

```
GET /api/v1/webhooks/
Authorization: Bearer <token>
```

#### Get Subscription

```
GET /api/v1/webhooks/{subscription_id}
Authorization: Bearer <token>
```

#### Update Subscription

```
PATCH /api/v1/webhooks/{subscription_id}
Authorization: Bearer <token>

{
  "status": "INACTIVE",
  "price_max": 35000
}
```

#### Delete Subscription

```
DELETE /api/v1/webhooks/{subscription_id}
Authorization: Bearer <token>
```

### Webhook Payload

When a matching vehicle is found:

```json
{
  "event": "vehicle_alert",
  "timestamp": "2025-12-14T10:30:00Z",
  "subscription_id": 123,
  "vehicle": {
    "vin": "1HGBH41JXMN109186",
    "make": "Toyota",
    "model": "RAV4",
    "year": 2022,
    "price": 28000,
    "mileage": 15000,
    "location": "Los Angeles, CA",
    "dealer_name": "Example Toyota",
    "photo_links": [...]
  },
  "criteria": {
    "make": "Toyota",
    "model": "RAV4",
    "price_min": 20000,
    "price_max": 30000
  }
}
```

### Security

- **Secret Token**: Optional token sent in `X-Webhook-Secret` header
- **HTTPS Only**: Webhook URLs must use HTTPS
- **Automatic Disable**: After 5 consecutive failures, subscription is marked as FAILED

### Reliability

- **Timeout**: 10 seconds per webhook
- **Concurrent Limit**: Maximum 10 concurrent webhooks
- **Retry**: No automatic retries (receiver should be idempotent)
- **Status Tracking**: Track success/failure counts per subscription

## Migration

Database migration for webhook subscriptions:

```bash
cd backend
alembic upgrade head
```

This creates the `webhook_subscriptions` table with proper indexes.

## Testing

Run the test suite:

```bash
cd backend
pytest tests/test_rate_limiter.py
pytest tests/test_search_history_repository.py
pytest tests/test_webhook_repository.py
pytest tests/test_webhook_service.py
pytest tests/test_car_recommendation_service.py
```

## Performance Considerations

### Redis Memory Usage

- Each cache entry: ~5-50KB depending on result size
- 15-minute TTL automatically expires old entries
- Estimate: 1000 cached searches = ~25MB

### MongoDB Storage

- Each search record: ~2-10KB
- Index on `user_id` and `timestamp`
- Consider archiving old records (>1 year)

### Webhook Performance

- Async execution using `asyncio.gather()`
- Semaphore limits concurrent requests
- Failed webhooks don't block others

## Monitoring & Observability

### Logs

All operations are logged at appropriate levels:

- **INFO**: Cache hits, successful webhooks
- **WARNING**: Rate limits, retry attempts
- **ERROR**: API failures, webhook errors

### Metrics to Track

1. Cache hit rate
2. Rate limit violations per user
3. API retry counts
4. Webhook success/failure rates
5. Search history volume

## Configuration

Add to `.env`:

```bash
# Redis (required for caching and rate limiting)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# MongoDB (required for search history)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=autodealgenie

# Rate limiting (optional, defaults shown)
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Cache TTL (optional, defaults shown)
CACHE_TTL_SECONDS=900
```

## Best Practices

### For Developers

1. Always pass `user_id` when available
2. Pass `db_session` for webhook triggering
3. Handle rate limit errors gracefully
4. Log important operations

### For Operations

1. Monitor Redis memory usage
2. Set up alerts for high failure rates
3. Archive old search history regularly
4. Review webhook failure logs

## Future Enhancements

Potential improvements:

1. **Adaptive TTL**: Adjust cache TTL based on search popularity
2. **Smart Rate Limiting**: Higher limits for premium users
3. **Webhook Retry**: Exponential backoff for failed webhooks
4. **Search Analytics**: Dashboard for popular searches
5. **ML Integration**: Learn from search patterns

## Support

For issues or questions:
- GitHub Issues: https://github.com/Raviteja77/autodealgenie/issues
- Documentation: See repository README.md

## License

See LICENSE file in repository root.
