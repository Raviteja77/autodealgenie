# AutoDealGenie — Project Guide

> **Purpose**: This guide gives newcomers, contributors, and AI assistants a single source of truth to understand, navigate, and extend the AutoDealGenie platform.

---

## Table of Contents

1. [What Is AutoDealGenie?](#1-what-is-autodealgenie)
2. [How It Works — User Journey](#2-how-it-works--user-journey)
3. [Architecture Overview](#3-architecture-overview)
4. [Technology Stack](#4-technology-stack)
5. [Repository Layout](#5-repository-layout)
6. [Backend Deep Dive](#6-backend-deep-dive)
7. [Frontend Deep Dive](#7-frontend-deep-dive)
8. [Database Design](#8-database-design)
9. [AI / LLM System](#9-ai--llm-system)
10. [API Endpoint Catalog](#10-api-endpoint-catalog)
11. [Infrastructure & DevOps](#11-infrastructure--devops)
12. [Development Setup](#12-development-setup)
13. [Testing Guide](#13-testing-guide)
14. [Current Implementation Status](#14-current-implementation-status)

---

## 1. What Is AutoDealGenie?

AutoDealGenie is an **AI-powered car-buying assistant** that helps users through the entire vehicle purchase lifecycle:

- **Search & Discover** vehicles matching their preferences and budget.
- **Evaluate Deals** using AI-driven fair-market-value analysis.
- **Negotiate** with AI coaching that generates talking points and counter-offers.
- **Finance & Insure** with personalized lender and insurance partner recommendations.
- **Track Deals** from first search through final purchase.

The platform replaces the traditional car-buying guesswork with data-driven insights and an AI negotiation coach.

---

## 2. How It Works — User Journey

```
┌──────────┐    ┌──────────┐    ┌─────────────┐    ┌──────────┐
│  Search  │───▶│ Results  │───▶│  Negotiate  │───▶│ Evaluate │
│  (Step 1)│    │ (Step 2) │    │  (Step 3)   │    │ (Step 4) │
└──────────┘    └──────────┘    └─────────────┘    └──────────┘
     │               │                │                  │
     ▼               ▼                ▼                  ▼
  Filters &      AI-ranked        Real-time         Deal score,
  Budget set     vehicles,        chat with AI      fair value,
  by user        favorites,       negotiation       insurance &
                 compare,         coach, dealer     lender recs
                 lender recs      info analysis
```

### Step 1 — Search (`/dashboard/search`)
User enters vehicle preferences (make, model, budget, year, mileage) and financing details (payment method, credit score, down payment). The form validates in real-time with Zod schemas.

### Step 2 — Results (`/dashboard/results`)
The backend calls the MarketCheck API for listings and uses an LLM to rank and summarize the top matches. Users can save favorites, compare vehicles side-by-side, and view lender recommendations.

### Step 3 — Negotiate (`/dashboard/negotiation`)
An AI negotiation agent helps users via real-time WebSocket chat. It generates counter-offers, talking points, and analyzes dealer quotes. Falls back to HTTP when WebSocket is unavailable.

### Step 4 — Evaluate (`/dashboard/evaluation`)
A multi-step pipeline scores the deal (1–10), calculates fair market value, and provides insights. Optionally surfaces insurance quotes and lender recommendations based on deal quality.

### Supporting Pages
- **Deals** (`/deals`) — List and manage all user deals with status tracking.
- **Favorites** (`/dashboard/favorites`) — View saved vehicles with quick actions.
- **Auth** (`/auth/*`) — Login, signup, password reset flows.

---

## 3. Architecture Overview

```
┌───────────────────────────────────────────────────────────────┐
│                        CLIENT BROWSER                         │
│                   Next.js 14 (App Router)                     │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ Context Providers: Auth, Stepper, CarForm, Negotiation │   │
│  │ UI: Atomic Design (Atoms → Molecules → Organisms)      │   │
│  │ Hooks: useApi, useAuth, useFilters, useNegotiation     │   │
│  └──────────────────────┬─────────────────────────────────┘   │
└─────────────────────────┼─────────────────────────────────────┘
                          │ REST + WebSocket
                          ▼
┌───────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI)                          │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │  Endpoints   │─▶│   Services   │─▶│   Repositories     │   │
│  │  (api/v1/)   │  │ (Business    │  │  (Data Access)     │   │
│  │              │  │  Logic + LLM)│  │                    │   │
│  └─────────────┘  └──────┬───────┘  └──────┬─────────────┘   │
│                          │                  │                  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │             LLM Module (app/llm/)                       │  │
│  │  Multi-agent: Research, Evaluator, Negotiator, Loans    │  │
│  │  Prompts registry, Pydantic response schemas            │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌────────────┐  │
│  │PostgreSQL│  │ MongoDB  │  │   Redis    │  │ RabbitMQ   │  │
│  │(Deals,   │  │(Search   │  │ (Cache,   │  │(Async      │  │
│  │ Users)   │  │ History) │  │  Sessions)│  │ Messaging) │  │
│  └──────────┘  └──────────┘  └───────────┘  └────────────┘  │
└───────────────────────────────────────────────────────────────┘
                          │
                          ▼
              ┌────────────────────┐
              │  External Services │
              │  • OpenAI / OpenRouter │
              │  • MarketCheck API │
              └────────────────────┘
```

### Key Design Principles
- **Layered architecture**: Endpoints → Services → Repositories → Models
- **Separation of concerns**: LLM logic is centralized in `app/llm/`, never called directly from endpoints
- **Graceful degradation**: Redis and RabbitMQ have in-memory fallbacks for development and free-tier deployments
- **Atomic design**: Frontend components follow Atoms → Molecules → Organisms hierarchy
- **Context-driven state**: React Context Providers manage auth, form, stepper, and negotiation state

---

## 4. Technology Stack

### Backend
| Technology       | Version  | Purpose                                    |
|------------------|----------|--------------------------------------------|
| Python           | 3.11+    | Runtime                                    |
| FastAPI          | 0.115    | Web framework (async, OpenAPI auto-docs)   |
| SQLAlchemy       | 2.0      | PostgreSQL ORM                             |
| Alembic          | —        | Database migrations                        |
| Motor            | 3.6      | Async MongoDB driver                       |
| Redis            | 5.2      | Caching and rate limiting                  |
| aio-pika         | 9.4      | RabbitMQ async client                      |
| OpenAI SDK       | 1.54     | LLM integration                           |
| LangChain        | 0.3      | AI chain orchestration                     |
| Pydantic         | 2.9      | Schema validation                          |
| Prometheus       | 0.20     | Metrics instrumentation                    |

### Frontend
| Technology       | Version  | Purpose                                    |
|------------------|----------|--------------------------------------------|
| Next.js          | 14       | React framework (App Router, SSR)          |
| React            | 18       | UI library                                 |
| TypeScript       | 5        | Type-safe JavaScript                       |
| Material-UI      | 5.18     | Component library                          |
| Tailwind CSS     | —        | Utility-first styling (limited use)        |
| Zod              | 4.1      | Runtime schema validation                  |
| Jest             | 30       | Testing framework                          |
| Testing Library  | 16       | Component testing utilities                |

### Infrastructure
| Technology       | Purpose                                       |
|------------------|-----------------------------------------------|
| Docker Compose   | Local development (14 services)               |
| PostgreSQL 16    | Relational data (users, deals, evaluations)   |
| MongoDB 7        | Document store (search history, vehicle cache)|
| Redis 7          | Cache, sessions, rate limiting                |
| RabbitMQ 3.13    | Async message queuing                         |
| Prometheus       | Metrics collection                            |
| Grafana          | Dashboards and visualization                  |
| Alertmanager     | Alert routing (Slack, PagerDuty, Email)       |
| GCP Cloud Run    | Production deployment target                  |

---

## 5. Repository Layout

```
autodealgenie/
├── backend/                          # Python FastAPI backend
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── endpoints/            # 15 endpoint modules
│   │   │   └── api.py                # Router aggregation
│   │   ├── core/                     # Config, security, rate limiting, logging
│   │   ├── db/                       # PostgreSQL, MongoDB, Redis connections
│   │   ├── llm/                      # LLM client, prompts, response schemas
│   │   ├── models/                   # SQLAlchemy ORM models
│   │   ├── repositories/             # Data access layer (12 repositories)
│   │   ├── schemas/                  # Pydantic request/response models
│   │   ├── services/                 # Business logic (10 services)
│   │   ├── middleware/               # Error handling, security headers
│   │   ├── metrics/                  # Prometheus custom metrics
│   │   ├── tools/                    # External API clients (MarketCheck)
│   │   └── main.py                   # FastAPI app entry point
│   ├── alembic/versions/             # 10 database migrations
│   ├── tests/                        # 39 test files (pytest)
│   ├── requirements.txt
│   └── pyproject.toml                # Black, Ruff, MyPy config
│
├── frontend/                         # Next.js 14 frontend
│   ├── app/
│   │   ├── auth/                     # Login, signup, password reset pages
│   │   ├── dashboard/                # Search, results, negotiation, evaluation
│   │   ├── deals/                    # Deal management page
│   │   ├── context/                  # Auth, Stepper, CarForm, Negotiation providers
│   │   └── layout.tsx                # Root layout with provider stack
│   ├── components/
│   │   ├── atoms/                    # Button, Input, Card, Modal, Spinner
│   │   ├── molecules/                # Price, Vehicle, Controls, Forms (13)
│   │   ├── organisms/                # Filters, Vehicle cards, Finance, Chat (12)
│   │   └── common/                   # Header, Footer, ProgressStepper
│   ├── lib/
│   │   ├── api.ts                    # Singleton API client (25+ methods)
│   │   ├── hooks/                    # 11 custom React hooks
│   │   ├── auth/                     # AuthProvider implementation
│   │   ├── validation/               # Zod search form schema
│   │   ├── errors.ts                 # Error class hierarchy
│   │   └── theme/                    # MUI theme configuration
│   ├── package.json
│   └── jest.config.js                # 70% coverage threshold
│
├── monitoring/                       # Observability stack
│   ├── prometheus/                   # Scrape configs, alert rules
│   ├── grafana/                      # 3 pre-built dashboards
│   └── alertmanager/                 # Notification routing
│
├── docker-compose.yml                # 14 services
├── deploy-gcp.sh                     # GCP Cloud Run deployment
└── README.md                         # Quick start guide
```

---

## 6. Backend Deep Dive

### Request Lifecycle

```
HTTP Request
    ↓
Middleware (ErrorHandler → SecurityHeaders → CORS → RequestID)
    ↓
Rate Limiter (100 req/hr per user)
    ↓
Auth Dependency (JWT validation → get_current_user)
    ↓
Endpoint Handler (api/v1/endpoints/*)
    ↓
Service Layer (services/*)
    ├── LLM Module (llm/) — AI operations
    ├── External APIs (tools/marketcheck_client.py)
    └── Cache Layer (Redis with in-memory fallback)
    ↓
Repository Layer (repositories/*)
    ├── PostgreSQL (SQLAlchemy async sessions)
    └── MongoDB (Motor async client)
    ↓
HTTP Response (Pydantic serialization)
```

### Services Reference

| Service | File | Responsibility |
|---------|------|----------------|
| Car Recommendation | `car_recommendation_service.py` | MarketCheck API search, LLM ranking, caching, webhook triggers |
| Deal Evaluation | `deal_evaluation_service.py` | Multi-step pipeline: vehicle condition → price → financing → risk → final score |
| Negotiation | `negotiation_service.py` | Session management, AI counter-offers, talking points, WebSocket broadcasting |
| Loan Calculator | `loan_calculator_service.py` | Monthly payments, amortization, APR by credit tier |
| Lender Service | `lender_service.py` | Partner lender matching, APR estimation, scoring |
| Insurance | `insurance_recommendation_service.py` | Partner insurer matching, premium calculation, coverage scoring |
| Webhook | `webhook_service.py` | HTTP callback delivery for vehicle alerts |
| WebSocket Manager | `websocket_manager.py` | Real-time connection management |
| RabbitMQ Producer | `rabbitmq_producer.py` | Async message publishing |
| RabbitMQ Consumer | `rabbitmq_consumer.py` | Async message consumption |

### LLM Multi-Agent System

The backend uses a **multi-agent architecture** with five specialized AI roles:

1. **Research Agent** — Vehicle discovery and market analysis
2. **Loan Analyzer Agent** — Financing options and lender recommendations
3. **Negotiation Agent** — Counter-offer generation and strategy
4. **Deal Evaluator Agent** — Fair value scoring (1–10 scale)
5. **Quality Assurance Agent** — Validation and review of AI outputs

All agents share a centralized `LLMClient` in `app/llm/llm_client.py` that wraps the OpenAI SDK. Prompts are stored in `app/llm/prompts.py` and responses are validated with Pydantic schemas in `app/llm/schemas.py`.

---

## 7. Frontend Deep Dive

### Component Hierarchy (Atomic Design)

```
Atoms (primitives)
├── Button      — Variants: primary, secondary, danger, success, outline
├── Input       — Text field with validation support
├── Card        — Container with header/body/footer
├── Modal       — Dialog overlay
└── Spinner     — Loading indicator

Molecules (composed from atoms)
├── PriceDisplay, MonthlyPaymentDisplay, PriceSwitcher
├── VehicleTitle, VehicleDetails, VehicleImage
├── ViewModeToggle, SortDropdown, SavedSearchesDropdown
├── PaymentMethodSelector, BudgetRangeSlider, SearchSidebar
├── SaveSearchModal, ConnectionStatusIndicator
└── (13 total)

Organisms (feature-level)
├── BasicVehicleFilters, AdvancedFilters, FilterPanel
├── VehicleCard, ComparisonBar, ComparisonModal
├── FinancingOptionsForm, FinancingComparisonModal
├── LenderRecommendations, InsuranceRecommendations
├── ChatInput
└── (12 total)
```

### State Management

| Provider | File | State Managed |
|----------|------|---------------|
| `AuthProvider` | `context/AuthProvider.tsx` | User session, JWT token, login/logout |
| `StepperProvider` | `context/StepperProvider.tsx` | Multi-step workflow progress (4 steps) |
| `CarFormProvider` | `context/CarFormProvider.tsx` | Car search form data (enums, selections) |
| `FormProvider` | `context/FormProvider.tsx` | Generic form state |
| `NegotiationChatProvider` | `context/NegotiationChatProvider.tsx` | WebSocket connection, message queue, chat state |

### Custom Hooks

| Hook | Purpose |
|------|---------|
| `useApi` | Generic API request with loading/error states |
| `useAuth` | Access auth context (login, signup, logout, user) |
| `useDebounce` | Debounce input values |
| `useLocalStorage` | Persist state to localStorage |
| `useOnlineStatus` | Detect network connectivity |
| `useFilters` | Vehicle filter state management |
| `useComparison` | Vehicle comparison tracking |
| `useViewMode` | Grid/list display toggle |
| `useSavedSearches` | Saved search management |
| `useNegotiationState` | Negotiation round/offer tracking |
| `useFinancingCalculation` | Payment and affordability calculations |

### API Client

The singleton `apiClient` in `lib/api.ts` provides 25+ typed methods for all backend interactions. Key features:
- Cookie-based credentials (`credentials: "include"`)
- Structured error handling mapping HTTP status to typed error classes
- Mock endpoint support via environment variable
- Type-safe request/response interfaces

---

## 8. Database Design

### PostgreSQL Tables

```
┌────────────┐     ┌────────────────┐     ┌────────────────┐
│   users    │     │     deals      │     │  evaluations   │
├────────────┤     ├────────────────┤     ├────────────────┤
│ id (PK)    │◀──┐ │ id (PK)        │◀──┐ │ id (PK)        │
│ email      │   │ │ customer_name  │   │ │ user_id (FK)   │
│ username   │   │ │ customer_email │   │ │ deal_id (FK)   │
│ full_name  │   │ │ vehicle_make   │   │ │ status (enum)  │
│ hashed_pw  │   │ │ vehicle_model  │   │ │ current_step   │
│ is_active  │   │ │ vehicle_year   │   │ │ result_json    │
│ is_superuser│  │ │ vehicle_mileage│   │ └────────────────┘
│ reset_token│   │ │ vehicle_vin    │   │
└────────────┘   │ │ asking_price   │   │ ┌────────────────┐
                 │ │ offer_price    │   │ │ negotiations   │
                 │ │ status (enum)  │   │ ├────────────────┤
                 │ │ notes          │   └─│ id (PK)        │
                 │ │ user_id (FK)───┘     │ user_id (FK)   │
                 │ └────────────────┘     │ deal_id (FK)   │
                 │                        │ initial_offer  │
                 │ ┌────────────────┐     │ counter_offer  │
                 │ │ webhook_subs   │     │ final_price    │
                 │ ├────────────────┤     └────────────────┘
                 └─│ user_id (FK)   │
                   │ webhook_url    │     ┌────────────────┐
                   │ status         │     │  ai_responses  │
                   └────────────────┘     ├────────────────┤
                                          │ id (PK)        │
                                          │ user_id (FK)   │
                                          │ prompt         │
                                          │ response       │
                                          │ tokens_used    │
                                          └────────────────┘
```

**Enums:**
- `DealStatus`: pending, in_progress, completed, cancelled
- `EvaluationStatus`: ANALYZING, AWAITING_INPUT, COMPLETED
- `PipelineStep`: VEHICLE_CONDITION, PRICE, FINANCING, INSURANCE, FINAL

### MongoDB Collections
- **search_history** — Logs of all user searches with results
- **vehicle_cache** — Cached MarketCheck API responses (TTL-managed)
- **negotiation_conversations** — Chat message history

### Redis Keys
- `car_search:{hash}` — Cached search results (15 min TTL)
- `deal_eval:{deal_id}` — Cached evaluations (1 hr TTL)
- `rate_limit:{user_id}` — Rate limiting counters

---

## 9. AI / LLM System

### Module Structure (`backend/app/llm/`)

```
llm/
├── __init__.py        # Public API: generate_structured_json, generate_text
├── llm_client.py      # LLMClient class wrapping OpenAI SDK
├── prompts.py         # PromptTemplate registry with variable substitution
└── schemas.py         # Pydantic models for structured LLM responses
```

### How to Add a New AI Feature

1. **Define the prompt** in `app/llm/prompts.py`:
   ```python
   PROMPTS["my_new_feature"] = PromptTemplate(
       template="Analyze {vehicle_make} {vehicle_model}...",
       variables=["vehicle_make", "vehicle_model"],
       agent_role="deal_evaluator"
   )
   ```

2. **Define the response schema** in `app/llm/schemas.py`:
   ```python
   class MyFeatureResponse(BaseModel):
       score: float
       insights: list[str]
   ```

3. **Call from a service** (never from an endpoint directly):
   ```python
   from app.llm import generate_structured_json
   result = await generate_structured_json(
       prompt_id="my_new_feature",
       variables={"vehicle_make": "Toyota", "vehicle_model": "Camry"},
       response_model=MyFeatureResponse
   )
   ```

### Current Prompt Registry
- `research_vehicles` — Vehicle discovery and market analysis
- `evaluate_deal` — Deal quality scoring
- `negotiate_strategy` — Negotiation counter-offers and talking points
- `vehicle_condition` — Vehicle condition assessment
- `loan_analysis` — Loan option evaluation

---

## 10. API Endpoint Catalog

All endpoints are under `/api/v1/`. Auth-required endpoints expect a JWT token.

### Authentication
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/signup` | No | Register new user |
| POST | `/auth/login` | No | Login, returns JWT |
| POST | `/auth/refresh` | Yes | Refresh access token |
| POST | `/auth/forgot-password` | No | Request password reset |
| POST | `/auth/reset-password` | No | Complete password reset |
| GET | `/auth/me` | Yes | Get current user profile |

### Vehicle Search & Discovery
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/cars/search` | Yes | AI-powered car search |
| GET | `/cars/health` | No | Car service health check |
| GET | `/recommendations/cars` | Yes | Car recommendations |
| GET | `/recommendations/lenders` | Yes | Lender recommendations |
| GET | `/recommendations/insurance` | Yes | Insurance recommendations |

### Deals
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/deals/` | Yes | List user's deals |
| POST | `/deals/` | Yes | Create a new deal |
| GET | `/deals/{id}` | Yes | Get deal by ID |
| PUT | `/deals/{id}` | Yes | Update a deal |
| DELETE | `/deals/{id}` | Yes | Delete a deal |
| POST | `/deals/evaluate` | Yes | Quick deal evaluation |

### Evaluations
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/evaluations/` | Yes | Start evaluation pipeline |
| GET | `/evaluations/{id}` | Yes | Get evaluation status |
| POST | `/evaluations/{id}/answer` | Yes | Submit step answers |
| GET | `/evaluations/{id}/lenders` | Yes | Get lender recommendations for evaluation |

### Negotiations
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/negotiations/` | Yes | Create negotiation session |
| GET | `/negotiations/{id}` | Yes | Get session details |
| POST | `/negotiations/{id}/round` | Yes | Process next round |
| POST | `/negotiations/{id}/chat` | Yes | Send chat message |
| POST | `/negotiations/{id}/dealer-info` | Yes | Submit dealer quote |
| WS | `/negotiations/ws/{session_id}` | Yes | Real-time negotiation |

### User Features
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/favorites/` | Yes | List favorites |
| POST | `/favorites/` | Yes | Add favorite |
| DELETE | `/favorites/{id}` | Yes | Remove favorite |
| GET | `/saved-searches/` | Yes | List saved searches |
| POST | `/saved-searches/` | Yes | Create saved search |
| DELETE | `/saved-searches/{id}` | Yes | Delete saved search |
| GET | `/comparisons/` | Yes | Get vehicle comparisons |

### Financing
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/loans/calculate` | Yes | Calculate loan payments |
| GET | `/loans/affordability` | Yes | Affordability analysis |
| POST | `/insurance/recommend` | Yes | Get insurance quotes |

---

## 11. Infrastructure & DevOps

### Docker Compose Services (14 total)

| Service | Port | Description |
|---------|------|-------------|
| `backend` | 8000 | FastAPI application |
| `frontend` | 3000 | Next.js application |
| `postgres` | 5432 | PostgreSQL 16 database |
| `mongodb` | 27017 | MongoDB 7 document store |
| `redis` | 6379 | Redis 7 cache |
| `rabbitmq` | 5672, 15672 | RabbitMQ with management UI |
| `prometheus` | 9090 | Metrics collection |
| `grafana` | 3001 | Dashboards (admin/admin) |
| `alertmanager` | 9094 | Alert routing |
| `postgres-exporter` | 9187 | PostgreSQL metrics |
| `redis-exporter` | 9121 | Redis metrics |
| `rabbitmq-exporter` | 9419 | RabbitMQ metrics |

### CI/CD Pipeline (`.github/workflows/ci-cd.yml`)

1. **Backend Tests** — Python 3.11 + PostgreSQL + Redis → Black → Ruff → MyPy → Pytest + Codecov
2. **Frontend Tests** — Node 20 → ESLint → TypeScript check → Build → Jest
3. **Security Scan** — Trivy vulnerability scanner → SARIF upload
4. **Docker Build** — Multi-stage build with GitHub Actions cache

### Monitoring Stack

- **Prometheus**: 15s scrape interval, 30d retention, 4 exporter targets
- **Grafana**: 3 dashboards (System Overview, Business Metrics, Database Performance)
- **Alertmanager**: Critical/Warning/Info severity routing, Slack/PagerDuty/Email receivers

---

## 12. Development Setup

### Quick Start (Docker)

```bash
git clone https://github.com/Raviteja77/autodealgenie.git
cd autodealgenie

# Configure environment
cp backend/.env.example backend/.env    # Add OPENAI_API_KEY
cp frontend/.env.example frontend/.env.local

# Start everything
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Access:
#   Frontend:  http://localhost:3000
#   Backend:   http://localhost:8000
#   API Docs:  http://localhost:8000/docs
#   Grafana:   http://localhost:3001
#   RabbitMQ:  http://localhost:15672
```

### Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Configure database URLs and API keys
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev  # http://localhost:3000
```

### Code Quality Commands

```bash
# Backend
cd backend
black .                          # Format
ruff check . --fix               # Lint
mypy .                           # Type check
pre-commit run --all-files       # All checks

# Frontend
cd frontend
npm run lint                     # ESLint
npx tsc --noEmit                 # TypeScript check
```

---

## 13. Testing Guide

### Backend (Pytest)

```bash
cd backend
pytest                            # Run all tests
pytest --cov=app                  # With coverage
pytest tests/test_auth.py -v      # Single module
pytest -k "test_deal"             # Pattern match
```

**Test infrastructure**: SQLite in-memory database, mocked Redis/RabbitMQ, async test support via `pytest-asyncio`.

**Coverage exclusions** (require external services): `mongodb.py`, `redis.py`, `kafka_*.py`, `langchain_service.py`, `car_recommendation_service.py`, `marketcheck_client.py`.

### Frontend (Jest + Testing Library)

```bash
cd frontend
npm test                          # Run all tests
npm test -- --coverage            # With coverage
npm test -- Button.test.tsx       # Single file
```

**Coverage threshold**: 70% for branches, functions, lines, and statements.

**Tested components**: All atoms (Button, Input, Card, Modal, Spinner), select molecules (SearchSidebar, BudgetRangeSlider, PaymentMethodSelector), select organisms (VehicleCard, BasicVehicleFilters, ComparisonBar).

---

## 14. Current Implementation Status

### Fully Implemented ✅
- User authentication (JWT, password reset, protected routes)
- Car search with MarketCheck API + LLM ranking
- Deal CRUD operations with status tracking
- Loan calculator (amortization, APR by credit tier)
- Lender recommendations (6 partners, scoring algorithm)
- Insurance recommendations (6 partners, premium calculation)
- Vehicle favorites and saved searches
- Vehicle comparison
- Real-time WebSocket negotiation chat
- Monitoring stack (Prometheus, Grafana, Alertmanager)
- CI/CD pipeline with security scanning
- GCP Cloud Run deployment support

### Partially Implemented ⚠️
- **Deal evaluation pipeline** — Framework exists but inner step methods (price, financing, risk, final) need completion
- **AI negotiation agent** — Session management complete, but `_generate_agent_response()` and `_generate_counter_response()` need full LLM integration
- **Negotiation chat** — `send_chat_message()` and `analyze_dealer_info()` methods are stubs
- **AI response logging** — Disabled (TODO comment in code)

### Not Yet Implemented ❌
- Mobile application
- Multi-user collaboration (shared deals)
- Vehicle history reports (Carfax/AutoCheck integration)
- Real partner API integrations (lenders and insurers use hardcoded data)
- Advanced analytics dashboard
- User profile and settings page
- Email notification system
- Deal finalization workflow (e-signature, payment)

> **See [ROADMAP.md](ROADMAP.md) for the strategic development plan and AI-promptable task descriptions.**
