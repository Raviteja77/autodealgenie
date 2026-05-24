---
paths: backend/**/*.py
---

# Backend Coding Principles (auto-loaded for Python files)

You are writing production Python for AutoDealGenie's FastAPI backend.
Follow these principles — they exist so the code doesn't break when someone
modifies it six months from now (including you).

---

## SOLID Principles (applied to this codebase)

### S — Single Responsibility
Each function does ONE thing. Each class has ONE reason to change.
```python
# ❌ Wrong: one function doing three jobs
async def process_deal(db, deal_id, user_id):
    deal = await db.execute(select(Deal).where(Deal.id == deal_id))  # fetch
    if deal.user_id != user_id:                                        # auth check
        raise HTTPException(403)
    result = await openai_client.chat(...)                             # AI call
    deal.score = result["score"]
    await db.commit()

# ✅ Right: split by responsibility
# router.py  → auth check (FastAPI dependency)
# service.py → orchestrate: call repo + call LLM
# repository.py → DB query
# app/llm/   → OpenAI call
```

### D — Dependency Inversion
Depend on the abstraction (the function signature / interface), not the
concrete implementation. This is why LLM calls go through `app/llm/` and
DB calls go through repositories — services don't know the details.
```python
# ❌ Wrong: service depends on concrete OpenAI detail
from openai import AsyncOpenAI
client = AsyncOpenAI()
response = await client.chat.completions.create(...)

# ✅ Right: service depends on the abstraction
from app.llm import generate_structured_json
result = await generate_structured_json(prompt_id="evaluate_deal", ...)
```

### O — Open/Closed
Add new behavior by adding new code, not by modifying working code.
New evaluation step = new method + new prompt, not rewriting the existing pipeline.

---

## Clean Code Rules

### Naming
```python
# Names must be honest about what they do
# ❌ Bad names
def process(d, u):        # what is d? what is u?
def get_data(id):         # what data?
def handle_thing():       # what thing?

# ✅ Good names
async def score_vehicle_deal(deal_id: UUID, user_id: UUID) -> DealScore:
async def get_evaluation_by_deal_id(deal_id: UUID) -> Evaluation | None:
async def send_negotiation_counter_offer(session_id: UUID, amount: float) -> Message:
```

### Function Size and Focus
```python
# Target: 15-25 lines per function. If it's longer, it probably does too much.
# Every function should be summarizable in one sentence.

# ✅ Good — one clear job, reads top to bottom
async def run_price_evaluation_step(
    db: AsyncSession,
    evaluation_id: UUID,
    vehicle: VehicleDetails,
) -> PriceStepResult:
    """Compare asking price to fair market value using AI analysis."""
    market_context = await vehicle_cache.get_market_data(vehicle.vin)
    ai_result = await generate_structured_json(
        prompt_id="evaluate_price",
        variables={"asking": vehicle.asking_price, "market": market_context},
        response_model=PriceEvaluationResponse,
    )
    await evaluation_repo.save_step_result(db, evaluation_id, "price", ai_result)
    return PriceStepResult(
        verdict=ai_result.verdict,
        fair_value_min=ai_result.fair_value_min,
        fair_value_max=ai_result.fair_value_max,
        reasons=ai_result.reasons,
    )
```

### Comments — WHY, not WHAT
```python
# ❌ Wrong: comment says what the code already says
# Get the user by id
user = await user_repo.get_by_id(db, user_id)

# ✅ Right: comment explains non-obvious reasoning
# MarketCheck caches aggressively — we add a jitter to avoid
# all users hitting the cache at the same second after expiry
cache_ttl = 900 + random.randint(0, 60)

# ✅ Right: comment explains a business rule
# Credit scores below 580 disqualify from most lender programs.
# This is a hard industry cutoff, not an arbitrary choice.
if credit_score < 580:
    return []
```

---

## Defensive Programming

### Validate at Every Boundary
```python
# Pydantic handles request validation automatically in FastAPI.
# But validate business rules explicitly in the service layer:

async def create_negotiation_session(
    db: AsyncSession,
    deal_id: UUID,
    user_id: UUID,
) -> NegotiationSession:
    """Start a new negotiation. Raises ValueError if deal not found or wrong user."""
    deal = await deal_repo.get_by_id(db, deal_id)
    if deal is None:
        raise ValueError(f"Deal {deal_id} does not exist")
    if deal.user_id != user_id:
        raise PermissionError(f"User {user_id} does not own deal {deal_id}")
    if deal.status == DealStatus.COMPLETED:
        raise ValueError("Cannot negotiate a completed deal")
    # ... rest of creation
```

### Fail Fast with Clear Messages
```python
# ❌ Silent failure — swallowed exception, impossible to debug
try:
    result = await marketcheck_client.search(query)
except Exception:
    result = []

# ✅ Explicit failure with context
try:
    result = await marketcheck_client.search(query)
except httpx.TimeoutException:
    logger.warning(f"MarketCheck timeout for query: {query.make} {query.model}")
    raise ServiceUnavailableError("Vehicle search is temporarily unavailable. Try again.")
except httpx.HTTPStatusError as e:
    logger.error(f"MarketCheck HTTP {e.response.status_code}", exc_info=True)
    raise ExternalServiceError(f"Vehicle data service error: {e.response.status_code}")
```

### Never Let Raw Exceptions Reach the HTTP Layer
```python
# FastAPI exception handlers in main.py convert these cleanly:
# ValueError          → 400 Bad Request
# PermissionError     → 403 Forbidden
# ServiceUnavailable  → 503 Service Unavailable
# Anything else       → 500 with logged stack trace

# In services: raise semantic exceptions
# In endpoints: let them bubble — the handler formats the response
```

---

## DRY — With Nuance

**DRY is about knowledge duplication, not code that looks similar.**

```python
# These look similar but represent DIFFERENT knowledge — keep them separate:
def calculate_lender_score(lender, loan_request):
    # lender scoring algorithm
    pass

def calculate_insurer_score(insurer, insurance_request):
    # insurer scoring algorithm
    pass
# ❌ Don't merge them into one "calculate_partner_score" — they'll diverge

# These represent the SAME knowledge — extract:
# If you write the same DB boilerplate in 3+ repositories:
async def get_by_id(db, model_class, id):
    result = await db.execute(select(model_class).where(model_class.id == id))
    return result.scalar_one_or_none()
# ✅ Extract to a BaseRepository — genuinely shared logic
```

**The rule: abstract when you have 3+ concrete uses of the same concept AND the same intent. Not before.**

---

## YAGNI — Don't Build What You Don't Need

```python
# ❌ Wrong: adding a plugin system "for future extensibility"
class EvaluationStep:
    def __init__(self, plugins: list[EvaluationPlugin] = None): ...

# ✅ Right: write the step directly. Add a plugin system when you need one.
async def run_condition_step(db, evaluation_id, vehicle): ...
async def run_price_step(db, evaluation_id, vehicle): ...
```

---

## Type Safety Rules
- Type hints on EVERY function parameter and return value
- Use `X | None` not `Optional[X]` (Python 3.10+ style)
- Use `UUID` for all primary keys — never `int`
- Use `Literal["pending", "active", "done"]` for fixed string sets — never raw `str`
- Pydantic models for all request/response boundaries (FastAPI handles this if you define them)

## MUST pass before "done"
```bash
black .              # formatting
ruff check . --fix   # linting
mypy .               # type checking
pytest               # all tests green
```
