# AutoDealGenie — Architecture & AI Context Reference

> **Purpose**: This document provides the architectural blueprint for AutoDealGenie. It is designed to be given directly to AI assistants (Copilot, ChatGPT, Claude, etc.) so they can understand the system and generate accurate, context-aware code. It also serves as a reference for developers making architectural decisions.

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Module Dependency Map](#2-module-dependency-map)
3. [Data Flow Diagrams](#3-data-flow-diagrams)
4. [Design Patterns](#4-design-patterns)
5. [Configuration Reference](#5-configuration-reference)
6. [Coding Conventions](#6-coding-conventions)
7. [Extension Points](#7-extension-points)
8. [Common Tasks for AI Assistants](#8-common-tasks-for-ai-assistants)

---

## 1. System Architecture

### 1.1 Deployment Topology

```
                    ┌─────────────────────────┐
                    │     Load Balancer /      │
                    │     GCP Cloud Run        │
                    └──────────┬──────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                 ▼
     ┌────────────┐   ┌────────────┐   ┌──────────────┐
     │  Frontend   │   │  Backend   │   │  Monitoring  │
     │  (Next.js)  │   │  (FastAPI) │   │  (Prometheus │
     │  Port 3000  │   │  Port 8000 │   │   + Grafana) │
     └────────────┘   └─────┬──────┘   └──────────────┘
                            │
           ┌────────────────┼────────────────┐
           ▼                ▼                ▼
     ┌──────────┐    ┌──────────┐    ┌──────────┐
     │PostgreSQL│    │ MongoDB  │    │  Redis   │
     │ Port 5432│    │Port 27017│    │Port 6379 │
     └──────────┘    └──────────┘    └──────────┘
                                           │
                                     ┌──────────┐
                                     │ RabbitMQ │
                                     │Port 5672 │
                                     └──────────┘
```

### 1.2 Backend Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FASTAPI APPLICATION                       │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                    MIDDLEWARE STACK                         │  │
│  │  ErrorHandler → SecurityHeaders → CORS → RequestID         │  │
│  └────────────────────────────────────────────────────────────┘  │
│                              │                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                    API LAYER (Endpoints)                    │  │
│  │  auth │ cars │ deals │ evaluations │ negotiations │ ...    │  │
│  │                                                            │  │
│  │  Responsibilities:                                         │  │
│  │  • HTTP request/response handling                          │  │
│  │  • Input validation (Pydantic schemas)                     │  │
│  │  • Authentication checks (FastAPI dependencies)            │  │
│  │  • Rate limiting                                           │  │
│  │  • Response serialization                                  │  │
│  └──────────────────────────┬─────────────────────────────────┘  │
│                              │                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                   SERVICE LAYER                             │  │
│  │  deal_evaluation │ negotiation │ car_recommendation │ ...  │  │
│  │                                                            │  │
│  │  Responsibilities:                                         │  │
│  │  • Business logic and orchestration                        │  │
│  │  • LLM integration (via app/llm module only)               │  │
│  │  • External API calls (MarketCheck)                        │  │
│  │  • Caching strategy (Redis → in-memory fallback)           │  │
│  │  • Event publishing (RabbitMQ)                             │  │
│  └──────────────────────────┬─────────────────────────────────┘  │
│                              │                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                   REPOSITORY LAYER (DAL)                    │  │
│  │  deal │ user │ evaluation │ negotiation │ favorites │ ...  │  │
│  │                                                            │  │
│  │  Responsibilities:                                         │  │
│  │  • Database queries (SQLAlchemy for PG, Motor for Mongo)   │  │
│  │  • Data mapping (ORM models ↔ domain objects)              │  │
│  │  • Transaction management                                  │  │
│  │  • No business logic — pure data access                    │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                      LLM MODULE                             │  │
│  │  llm_client.py │ prompts.py │ schemas.py                   │  │
│  │                                                            │  │
│  │  Responsibilities:                                         │  │
│  │  • Single OpenAI client instance                           │  │
│  │  • Prompt template management and substitution             │  │
│  │  • Structured JSON output with Pydantic validation         │  │
│  │  • Multi-agent role system (5 agents)                      │  │
│  │  • Error handling and retry logic                          │  │
│  └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Frontend Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      NEXT.JS APPLICATION                         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                   PROVIDER STACK (layout.tsx)               │  │
│  │  ThemeRegistry → ErrorBoundary → AuthProvider → Stepper    │  │
│  └──────────────────────────┬─────────────────────────────────┘  │
│                              │                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                      PAGES (App Router)                     │  │
│  │  /auth/*  │  /dashboard/*  │  /deals  │  /                 │  │
│  │                                                            │  │
│  │  Each page:                                                │  │
│  │  • Consumes context via hooks (useAuth, useStepper, etc.)  │  │
│  │  • Composes organisms + molecules + atoms                  │  │
│  │  • Calls apiClient for data fetching                       │  │
│  └──────────────────────────┬─────────────────────────────────┘  │
│                              │                                   │
│  ┌──────────────────┐ ┌──────────────────┐ ┌────────────────┐  │
│  │ ORGANISMS (12)    │ │ MOLECULES (13)   │ │  ATOMS (5)     │  │
│  │ VehicleCard       │ │ PriceDisplay     │ │  Button        │  │
│  │ FilterPanel       │ │ VehicleDetails   │ │  Input         │  │
│  │ FinancingOptions  │ │ SearchSidebar    │ │  Card          │  │
│  │ LenderRecs        │ │ BudgetSlider     │ │  Modal         │  │
│  │ InsuranceRecs     │ │ SortDropdown     │ │  Spinner       │  │
│  │ ChatInput         │ │ ...              │ └────────────────┘  │
│  │ ComparisonModal   │ └──────────────────┘                     │
│  │ ...               │                                          │
│  └──────────────────┘                                           │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                    SHARED LIBRARIES (lib/)                  │  │
│  │  api.ts      — Singleton HTTP client (25+ methods)         │  │
│  │  errors.ts   — Error class hierarchy                       │  │
│  │  hooks/      — 11 custom React hooks                       │  │
│  │  validation/ — Zod schemas for form validation             │  │
│  │  theme/      — MUI theme configuration                     │  │
│  └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Module Dependency Map

### 2.1 Backend Dependencies

```
Endpoints (api/v1/endpoints/)
    │
    ├── imports ──▶ Schemas (schemas/)           # Request/response validation
    ├── imports ──▶ Services (services/)          # Business logic
    ├── imports ──▶ Core (core/)                  # Config, security, rate limiter
    └── uses    ──▶ DB Sessions (db/)             # FastAPI dependency injection
                       │
Services (services/)   │
    │                  │
    ├── imports ──▶ LLM Module (llm/)            # AI operations
    ├── imports ──▶ Repositories (repositories/)  # Data access
    ├── imports ──▶ Schemas (schemas/)            # Data validation
    ├── imports ──▶ Tools (tools/)               # External API clients
    └── uses    ──▶ DB Sessions (db/)            # Injected from endpoints
                       │
Repositories (repositories/)
    │
    ├── imports ──▶ Models (models/)             # ORM models
    └── uses    ──▶ DB Sessions (db/)            # SQLAlchemy/Motor sessions

LLM Module (llm/)
    │
    ├── uses ──▶ OpenAI SDK                      # API calls
    └── uses ──▶ Core Config                     # API keys, model selection
```

**Rule**: Dependencies flow downward. Endpoints never import from Repositories directly. Services never import from Endpoints. LLM module is self-contained.

### 2.2 Frontend Dependencies

```
Pages (app/)
    │
    ├── imports ──▶ Organisms (components/organisms/)
    ├── imports ──▶ Molecules (components/molecules/)
    ├── imports ──▶ Atoms (components/atoms/)
    ├── uses    ──▶ Context Hooks (useAuth, useStepper, etc.)
    └── uses    ──▶ API Client (lib/api.ts)

Organisms
    │
    ├── imports ──▶ Molecules
    ├── imports ──▶ Atoms
    └── uses    ──▶ Custom Hooks (lib/hooks/)

Molecules
    │
    └── imports ──▶ Atoms

API Client (lib/api.ts)
    │
    └── imports ──▶ Error Classes (lib/errors.ts)
```

**Rule**: Atoms never import from Molecules or Organisms. Data always flows through props or context. The API client is only called from pages and hooks, never from atoms or molecules.

---

## 3. Data Flow Diagrams

### 3.1 Car Search Flow

```
User fills search form
        │
        ▼
SearchFormSchema (Zod) validates input
        │
        ▼
apiClient.searchCars(request)
        │
        ▼ POST /api/v1/cars/search
        │
Backend: cars endpoint
        │
        ├── Check Redis cache (key: car_search:{hash})
        │     │
        │     ├── HIT → Return cached results
        │     │
        │     └── MISS ─▶ CarRecommendationService
        │                       │
        │                       ├── Call MarketCheck API (retry x3)
        │                       │
        │                       ├── LLM ranks and summarizes results
        │                       │     (Research Agent role)
        │                       │
        │                       ├── Cache results (Redis, 15 min TTL)
        │                       │
        │                       ├── Log to search_history (MongoDB)
        │                       │
        │                       └── Check webhook subscriptions
        │
        ▼
Results displayed in VehicleCard grid
User can: save favorite, compare, start negotiation/evaluation
```

### 3.2 Deal Evaluation Flow

```
User selects vehicle → clicks "Evaluate"
        │
        ▼
apiClient.startEvaluation(request)
        │
        ▼ POST /api/v1/evaluations/
        │
Backend: evaluations endpoint
        │
        ▼
DealEvaluationService.start_pipeline(deal_id)
        │
        ▼ Step 1: VEHICLE_CONDITION
        │   └── LLM assesses condition → returns questions
        │
        ▼ User answers questions
        │
        ▼ Step 2: PRICE
        │   └── LLM compares asking price to fair market value
        │
        ▼ Step 3: FINANCING
        │   └── LLM evaluates financing options
        │
        ▼ Step 4: RISK (future: INSURANCE)
        │   └── LLM assesses purchase risk factors
        │
        ▼ Step 5: FINAL
        │   └── Aggregate score (1-10), insights, recommendation
        │
        ▼
Frontend displays: Score, Fair Value, Price Diff, Insights
Optionally: Lender + Insurance recommendations
```

### 3.3 Negotiation Flow

```
User selects vehicle → clicks "Negotiate"
        │
        ▼
apiClient.createNegotiation(session)
        │
        ▼ POST /api/v1/negotiations/
        │
Backend creates NegotiationSession
        │
        ▼
Frontend connects WebSocket
(ws://host/api/v1/negotiations/ws/{session_id})
        │
        ▼ Fallback: HTTP if WebSocket fails after 5 retries
        │
        ▼
User sends message / submits dealer info
        │
        ▼
NegotiationService processes round:
        ├── Generate AI counter-offer (Negotiation Agent)
        ├── Calculate metrics (discount %, confidence)
        ├── Persist messages to database
        └── Broadcast via WebSocket to all session participants
        │
        ▼
User can: Accept, Reject, Counter-offer
        │
        ▼ On Accept:
        │
Deal created/updated with final negotiated price
```

### 3.4 Lender & Insurance Recommendation Flow

```
Deal evaluation completes with score ≥ threshold
        │
        ▼
apiClient.getEvaluationLenders(evalId)
        │
        ▼ GET /api/v1/evaluations/{id}/lenders
        │
Backend: LenderService.get_recommendations(
    loan_amount, credit_score, term
)
        │
        ├── Filter 6 hardcoded partner lenders by:
        │     • Credit score range
        │     • Loan amount range
        │     • Supported terms
        │
        ├── Score each lender (5 components):
        │     40% APR competitiveness
        │     20% Loan amount fit
        │     20% Credit score fit
        │     10% Term flexibility
        │     10% Feature richness
        │
        ├── Calculate estimated APR + monthly payment
        │
        └── Return sorted by score (descending)
        │
        ▼
InsuranceService.get_recommendations(vehicle, driver)
        │
        ├── Filter 6 hardcoded insurer partners
        ├── Calculate premiums (4 factors)
        ├── Score and rank
        └── Return sorted recommendations
```

---

## 4. Design Patterns

### 4.1 Backend Patterns

| Pattern | Where Used | Description |
|---------|-----------|-------------|
| Repository | `app/repositories/` | Abstracts all data access behind typed interfaces |
| Service Layer | `app/services/` | Encapsulates business logic, orchestrates repos + LLM |
| Dependency Injection | FastAPI `Depends()` | DB sessions, auth, rate limiting injected into endpoints |
| Strategy | LLM multi-agent | Different agent roles for different AI tasks |
| Template Method | Evaluation pipeline | Fixed step sequence with overridable step implementations |
| Cache-Aside | Redis + services | Check cache → miss → compute → store → return |
| Circuit Breaker | MarketCheck client | Retry with exponential backoff, fallback on failure |
| Observer | Webhook service | Notify subscribers when matching vehicles found |
| Message Queue | RabbitMQ | Decouple deal events from processing |

### 4.2 Frontend Patterns

| Pattern | Where Used | Description |
|---------|-----------|-------------|
| Atomic Design | `components/` | Atoms → Molecules → Organisms hierarchy |
| Provider Pattern | `context/` | React Context for global state (auth, stepper, forms) |
| HOC Pattern | `withAuth`, `withPublic` | Route protection via higher-order components |
| Custom Hook | `lib/hooks/` | Encapsulate stateful logic for reuse |
| Singleton | `apiClient` | Single API client instance across the app |
| Facade | `lib/api.ts` | Unified interface to all backend endpoints |
| Observer | WebSocket in NegotiationChatProvider | Real-time updates via event-driven messaging |

### 4.3 Graceful Degradation

The system is designed to work with or without external services:

```
Redis available?
  ├── YES → Use Redis for caching and rate limiting
  └── NO  → Fall back to in-memory cachetools (TTLCache)

RabbitMQ available?
  ├── YES → Use RabbitMQ for async messaging
  └── NO  → Fall back to in-memory asyncio.Queue

MarketCheck API available?
  ├── YES → Real vehicle data
  └── NO  → Fallback mock recommendations from LLM

WebSocket available?
  ├── YES → Real-time negotiation chat
  └── NO  → HTTP polling fallback (after 5 retry attempts)

Mock mode enabled? (ENABLE_MOCK_SERVICES=true)
  ├── YES → Mock endpoints return test data
  └── NO  → Real service calls
```

---

## 5. Configuration Reference

### 5.1 Backend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | — | JWT signing key (min 32 chars) |
| `POSTGRES_SERVER` | Yes | localhost | PostgreSQL host |
| `POSTGRES_PORT` | No | 5432 | PostgreSQL port |
| `POSTGRES_USER` | Yes | — | PostgreSQL user |
| `POSTGRES_PASSWORD` | Yes | — | PostgreSQL password |
| `POSTGRES_DB` | Yes | — | PostgreSQL database name |
| `MONGODB_URL` | No | mongodb://localhost:27017 | MongoDB connection string |
| `REDIS_HOST` | No | localhost | Redis host |
| `REDIS_PORT` | No | 6379 | Redis port |
| `USE_REDIS` | No | true | Enable Redis (false = in-memory) |
| `USE_RABBITMQ` | No | true | Enable RabbitMQ (false = in-memory) |
| `RABBITMQ_HOST` | No | localhost | RabbitMQ host |
| `OPENAI_API_KEY` | Yes* | — | OpenAI/OpenRouter API key |
| `LLM_MODEL` | No | gpt-4 | LLM model name |
| `OPENAI_BASE_URL` | No | — | Custom LLM base URL (OpenRouter) |
| `MARKETCHECK_API_KEY` | Yes* | — | MarketCheck vehicle data API |
| `ENVIRONMENT` | No | development | development/staging/production |
| `CORS_ORIGINS` | No | * | Allowed CORS origins |
| `ACCESS_TOKEN_EXPIRE` | No | 30 | JWT access token expiry (minutes) |
| `REFRESH_TOKEN_EXPIRE` | No | 10080 | JWT refresh token expiry (minutes) |
| `ENABLE_MOCK_SERVICES` | No | false | Enable mock API endpoints |

*Required for AI and vehicle search features.

### 5.2 Frontend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | http://localhost:8000 | Backend API URL |
| `NEXT_PUBLIC_WS_URL` | No | ws://localhost:8000 | WebSocket URL |
| `NEXT_PUBLIC_MOCK_API` | No | false | Use mock endpoints |

---

## 6. Coding Conventions

### 6.1 Backend (Python)

```python
# File: app/services/my_service.py

from app.llm import generate_structured_json       # ✅ Use LLM module
from app.repositories.my_repo import MyRepository  # ✅ Use repository
from app.schemas.my_schema import MyRequest        # ✅ Use Pydantic schemas

# ❌ NEVER do this in a service:
# from openai import OpenAI                       # Use app/llm instead
# from sqlalchemy import text                     # Use repository instead

class MyService:
    """Service docstring explaining responsibility."""

    async def my_method(self, db: AsyncSession, request: MyRequest) -> MyResponse:
        """Method docstring."""
        # Business logic here
        repo = MyRepository()
        data = await repo.get(db, request.id)

        result = await generate_structured_json(
            prompt_id="my_prompt",
            variables={"input": data.value},
            response_model=MyLLMResponse,
        )
        return MyResponse(score=result.score)
```

**Rules:**
- Line length: 100 characters (Black + Ruff)
- Always use `async/await` for I/O
- Type hints on all function signatures
- Pydantic schemas for all request/response boundaries
- FastAPI `Depends()` for dependency injection

### 6.2 Frontend (TypeScript)

```tsx
// File: components/organisms/MyFeature.tsx

import { Button, Card } from '@/components/atoms';  // ✅ Use atoms
import { useApi } from '@/lib/hooks/useApi';         // ✅ Use custom hooks
import { apiClient } from '@/lib/api';               // ✅ Use API client

// ❌ NEVER do this:
// import { Pool } from 'pg';                       // No DB access in frontend
// fetch('http://localhost:8000/...')                // Use apiClient instead

interface MyFeatureProps {
  vehicleId: string;
  onComplete: (result: Result) => void;
}

export default function MyFeature({ vehicleId, onComplete }: MyFeatureProps) {
  const { data, loading, error, execute } = useApi(
    () => apiClient.getVehicle(vehicleId)
  );
  // Component logic
}
```

**Rules:**
- No `any` types unless documented and justified
- Use `components/atoms/` for all interactive elements
- Max 5 props per component; use hooks for complex logic
- Context providers for state shared across 2+ components
- Zod schemas for all form validation

---

## 7. Extension Points

### 7.1 Adding a New Backend Feature

```
1. Define schema:     app/schemas/my_feature_schemas.py
2. Define model:      app/models/my_feature.py (if DB needed)
3. Create migration:  alembic revision --autogenerate -m "Add my_feature"
4. Create repository: app/repositories/my_feature_repository.py
5. Create service:    app/services/my_feature_service.py
6. Create endpoint:   app/api/v1/endpoints/my_feature.py
7. Register route:    app/api/v1/api.py (add router)
8. Add tests:         tests/test_my_feature.py
```

### 7.2 Adding a New Frontend Feature

```
1. Create atoms:      components/atoms/NewAtom.tsx (if needed)
2. Create molecules:  components/molecules/NewMolecule.tsx
3. Create organism:   components/organisms/NewOrganism.tsx
4. Add API methods:   lib/api.ts (add to apiClient)
5. Create hook:       lib/hooks/useNewFeature.ts (if complex state)
6. Create page:       app/dashboard/new-feature/page.tsx
7. Update stepper:    app/context/StepperProvider.tsx (if workflow step)
8. Add tests:         __tests__/NewOrganism.test.tsx
```

### 7.3 Adding a New LLM Prompt

```
1. Add template:      app/llm/prompts.py → PROMPTS["my_prompt"]
2. Add schema:        app/llm/schemas.py → class MyResponse(BaseModel)
3. Export:             app/llm/__init__.py → add to __all__
4. Use in service:    await generate_structured_json(prompt_id="my_prompt", ...)
5. Add tests:         tests/llm/test_schemas.py → test_my_response_schema
```

### 7.4 Adding a Partner Integration (Lender/Insurer)

```
Currently: Partners are hardcoded in service files.
Future: Partner data should move to a database table.

To add a new partner now:
1. Edit app/services/lender_service.py (or insurance_recommendation_service.py)
2. Add partner to the LENDERS or INSURERS list
3. Define: name, min/max rates, credit score range, features, terms
4. The scoring algorithm will automatically rank the new partner

To move to dynamic partners (recommended):
1. Create Partner model in app/models/partner.py
2. Create migration for partners table
3. Create PartnerRepository
4. Create admin endpoint to manage partners
5. Update services to query from DB instead of hardcoded lists
```

---

## 8. Common Tasks for AI Assistants

When providing this document to an AI assistant, use these task templates:

### Task Template: Bug Fix
```
Context: See ARCHITECTURE.md for system architecture.
Task: Fix [describe bug] in [file path].
The file is in the [endpoint/service/repository] layer.
It interacts with [list dependencies].
Expected behavior: [describe expected].
Actual behavior: [describe actual].
```

### Task Template: New Feature
```
Context: See ARCHITECTURE.md for system architecture.
Task: Add [feature name].
Follow the extension pattern in Section 7.
Layer: [endpoint/service/repository/frontend component].
Data: [describe what data is needed].
AI: [describe if LLM integration is needed].
Tests: Write tests following existing patterns in tests/.
```

### Task Template: Refactor
```
Context: See ARCHITECTURE.md for module dependencies (Section 2).
Task: Refactor [component/module].
Constraints:
- Do not change the public API/interface
- Maintain backward compatibility
- Follow coding conventions in Section 6
- Dependency direction must flow downward (Section 2.1)
```

### Quick Reference for AI: Key File Locations

| Need to... | Look at... |
|------------|-----------|
| Understand the full user flow | `PROJECT_GUIDE.md` Section 2 |
| Add a backend endpoint | `app/api/v1/endpoints/` + `app/api/v1/api.py` |
| Add business logic | `app/services/` |
| Add database queries | `app/repositories/` + `app/models/` |
| Add AI features | `app/llm/prompts.py` + `app/llm/schemas.py` |
| Add frontend pages | `frontend/app/dashboard/` |
| Add UI components | `frontend/components/` (atoms → molecules → organisms) |
| Add API calls | `frontend/lib/api.ts` |
| Add form validation | `frontend/lib/validation/` |
| Add state management | `frontend/app/context/` |
| Configure environment | `backend/.env.example` + `frontend/.env.example` |
| Run tests | `backend/tests/` + `frontend/__tests__/` |
| Create DB migration | `backend/alembic/` |
| Check CI/CD | `.github/workflows/ci-cd.yml` |
| Configure monitoring | `monitoring/` |
