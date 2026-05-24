---
paths: backend/**/*.py
---

# Backend Rules (Auto-loaded for Python files)

You are working in the **FastAPI Python backend** of AutoDealGenie.

## Layer You're In
Before writing code, identify which layer this file belongs to:
- `api/v1/endpoints/` → API layer: HTTP only, no business logic
- `services/` → Service layer: business logic + LLM calls
- `repositories/` → Data layer: DB queries only, no business logic
- `llm/` → AI layer: prompts + OpenAI SDK only
- `tools/` → External APIs (MarketCheck etc)
- `models/` → SQLAlchemy ORM models
- `schemas/` → Pydantic request/response DTOs

## Code Template by Layer

### Endpoint
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.schemas.my_schemas import MyRequest, MyResponse
from app.services.my_service import MyService

router = APIRouter()

@router.post("/", response_model=MyResponse, status_code=201)
async def create_something(
    request: MyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MyResponse:
    """One-line description of what this does."""
    service = MyService()
    return await service.create(db, request, current_user.id)
```

### Service
```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.llm import generate_structured_json  # ONLY way to call LLM
from app.repositories.my_repo import MyRepository
from app.schemas.my_schemas import MyRequest, MyResponse
from app.llm.schemas import MyLLMResponse
import logging

logger = logging.getLogger(__name__)

class MyService:
    """One sentence: what this service is responsible for."""

    async def do_thing(self, db: AsyncSession, request: MyRequest) -> MyResponse:
        """One sentence: what this method does."""
        repo = MyRepository()
        data = await repo.get_by_id(db, request.id)
        if not data:
            raise ValueError(f"Item {request.id} not found")

        result = await generate_structured_json(
            prompt_id="my_prompt",
            variables={"input": data.value},
            response_model=MyLLMResponse,
        )
        return MyResponse(score=result.score, insights=result.insights)
```

### Repository
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.my_model import MyModel

class MyRepository:
    """Data access for MyModel. No business logic here."""

    async def get_by_id(self, db: AsyncSession, item_id: str) -> MyModel | None:
        result = await db.execute(select(MyModel).where(MyModel.id == item_id))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, data: dict) -> MyModel:
        item = MyModel(**data)
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item
```

## Rules
- Line length: 100 chars (Black + Ruff enforced)
- All async/await for ANY I/O operation
- Type hints on ALL function signatures
- Docstring on every class and public method (one sentence is enough)
- `logger.error(..., exc_info=True)` for exceptions you catch
- No bare `except:` — always catch specific exceptions
- Use `UUID` not `int` for primary keys
