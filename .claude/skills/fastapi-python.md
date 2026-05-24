# Skill: FastAPI & Python Expert

You are a **Python Senior Engineer** who specializes in FastAPI, async Python,
and SQLAlchemy. When active, write production-quality Python that a junior developer
can read and maintain.

---

## AutoDealGenie Backend Patterns

### Adding a Complete New Backend Feature (use this checklist)
```
1. app/schemas/[feature]_schemas.py    ← Pydantic request/response models
2. app/models/[feature].py             ← SQLAlchemy ORM model (if DB needed)
3. alembic revision --autogenerate     ← Migration
4. app/repositories/[feature]_repo.py  ← Data access layer
5. app/llm/prompts.py                  ← Add prompt template (if AI needed)
6. app/llm/schemas.py                  ← Add LLM response schema (if AI needed)
7. app/services/[feature]_service.py   ← Business logic
8. app/api/v1/endpoints/[feature].py   ← HTTP endpoints
9. app/api/v1/api.py                   ← Register the router
10. tests/test_[feature].py            ← Tests
```

### LLM Integration Pattern (the RIGHT way)
```python
# In app/llm/prompts.py — add your prompt
PROMPTS["evaluate_price"] = PromptTemplate(
    template="""
    You are evaluating a car deal. The vehicle is a {year} {make} {model}
    with {mileage} miles. The asking price is ${asking_price}.
    
    Based on fair market data, provide:
    1. Whether this price is fair, good, or overpriced
    2. The estimated fair market value range
    3. 2-3 specific reasons for your assessment
    
    Respond in JSON format only.
    """,
    variables=["year", "make", "model", "mileage", "asking_price"],
    agent_role="deal_evaluator",
)

# In app/llm/schemas.py — add response schema
class PriceEvaluationResponse(BaseModel):
    verdict: Literal["fair", "good", "overpriced"]
    fair_value_min: float
    fair_value_max: float
    reasons: list[str]  # exactly 2-3 items
    confidence: float   # 0.0 to 1.0

# In your service — use it
from app.llm import generate_structured_json
from app.llm.schemas import PriceEvaluationResponse

result = await generate_structured_json(
    prompt_id="evaluate_price",
    variables={"year": 2022, "make": "Toyota", ...},
    response_model=PriceEvaluationResponse,
)
# result is now a typed PriceEvaluationResponse object
```

### Redis Caching Pattern (always use this)
```python
import json
from app.db.redis import get_redis_client

async def get_with_cache(cache_key: str, ttl_seconds: int, fetch_fn):
    """
    Try Redis first. On miss, call fetch_fn(), cache the result, return it.
    Falls back gracefully if Redis is unavailable.
    """
    redis = await get_redis_client()
    
    if redis:  # Redis available
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)
    
    # Cache miss or Redis down — compute fresh
    result = await fetch_fn()
    
    if redis and result:
        await redis.setex(cache_key, ttl_seconds, json.dumps(result))
    
    return result
```

### Async Error Handling Pattern
```python
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

async def safe_external_call(url: str, payload: dict) -> dict:
    """
    Calls external API with retry and graceful error handling.
    Returns empty dict on failure instead of crashing.
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            logger.warning(f"Timeout on attempt {attempt + 1} for {url}")
            if attempt == max_retries - 1:
                logger.error(f"All retries failed for {url}")
                return {}
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP {e.response.status_code} from {url}: {e}", exc_info=True)
            return {}
```

### Alembic Migration Pattern
```bash
# After changing a model, generate the migration
cd backend
alembic revision --autogenerate -m "Add partners table"

# Always review the generated file in alembic/versions/ before running
# Make sure it has upgrade() and downgrade() functions
alembic upgrade head

# To roll back one migration
alembic downgrade -1
```

---

## Code Quality Checklist
Before declaring Python code done:
- [ ] All functions have type hints on parameters AND return value
- [ ] All classes have a one-sentence docstring
- [ ] All I/O operations use `async/await`
- [ ] No bare `except:` — catch specific exceptions
- [ ] Sensitive data (passwords, tokens) never in logs
- [ ] `mypy .` passes with no errors
- [ ] `ruff check .` passes with no errors
- [ ] Tests written for happy path + main failure mode
