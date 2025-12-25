# **AutoDealGenie - Complete Technical Documentation**

## **Table of Contents**

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Backend Architecture](#backend-architecture)
5. [Frontend Architecture](#frontend-architecture)
6. [Database Design](#database-design)
7. [API Reference](#api-reference)
8. [Security \& Authentication](#security-authentication)
9. [AI/LLM Integration](#ai-llm-integration)
10. [Development Workflow](#development-workflow)
11. [Deployment Guide](#deployment-guide)
12. [Testing Strategy](#testing-strategy)

***

## **1. Executive Summary**

**AutoDealGenie** is an AI-powered automotive deal management platform built with modern web technologies. The system enables users to manage vehicle deals, get AI-powered valuations, negotiate prices, and track automotive transactions efficiently.

### **Key Features**

- User authentication with JWT-based security using HTTP-only cookies
- Deal management (CRUD operations)
- AI-powered vehicle evaluation and market analysis
- Real-time negotiation tracking
- Mock services for development and testing
- Comprehensive API documentation
- Containerized deployment with Docker


### **Project Status**

- ✅ User authentication implemented
- ✅ Deal management system complete
- ✅ Database schema and migrations configured
- ✅ Docker containerization ready
- ⏳ Advanced AI features in development
- ⏳ Real-time WebSocket notifications planned
- ⏳ Mobile application roadmap

***

## **2. System Architecture**

### **High-Level Architecture**

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Layer                        │
│              Next.js 14 (React + TypeScript)            │
│                  Tailwind CSS Styling                    │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ HTTP/REST API
                 │ (JSON)
                 ▼
┌─────────────────────────────────────────────────────────┐
│                   Backend Layer                          │
│              FastAPI (Python 3.11+)                      │
│                                                          │
│  ┌──────────────┬──────────────┬──────────────────┐   │
│  │   API Layer  │ Service Layer│ Repository Layer │   │
│  │  (Endpoints) │ (Business    │ (Data Access)    │   │
│  │              │  Logic)      │                  │   │
│  └──────────────┴──────────────┴──────────────────┘   │
└────────┬─────────────┬──────────────┬──────────────────┘
         │             │              │
         ▼             ▼              ▼
┌────────────┐  ┌──────────┐  ┌──────────────┐
│ PostgreSQL │  │ MongoDB  │  │    Redis     │
│   (RDBMS)  │  │(Documents│  │   (Cache)    │
└────────────┘  └──────────┘  └──────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│       External Services             │
│  - OpenAI API (GPT-4)              │
│  - LangChain Framework             │
│  - Apache Kafka (Event Streaming)  │
└─────────────────────────────────────┘
```


### **Architecture Patterns**

#### **Backend Patterns**

- **Layered Architecture**: API → Service → Repository → Data
- **Repository Pattern**: Abstraction over data access
- **Dependency Injection**: FastAPI's native DI system
- **Middleware Chain**: Request processing pipeline
- **Error Handling**: Centralized exception management


#### **Frontend Patterns**

- **Component-Based Architecture**: Reusable React components
- **Server Components**: Next.js 14 App Router
- **Client-Side State**: React hooks for local state
- **API Client Layer**: Centralized HTTP communication

***

## **3. Technology Stack**

### **Frontend Technologies**

| Technology | Version | Purpose |
| :-- | :-- | :-- |
| Next.js | 14.x | React framework with SSR/SSG |
| React | 18.x | UI library |
| TypeScript | 5.x | Type-safe JavaScript |
| Tailwind CSS | 3.x | Utility-first CSS framework |
| Axios | Latest | HTTP client |

### **Backend Technologies**

| Technology | Version | Purpose |
| :-- | :-- | :-- |
| Python | 3.11+ | Programming language |
| FastAPI | Latest | High-performance web framework |
| SQLAlchemy | 2.x | SQL ORM |
| Alembic | Latest | Database migrations |
| Pydantic | 2.x | Data validation |
| Motor | Latest | Async MongoDB driver |
| Redis-py | Latest | Redis client |
| LangChain | Latest | LLM framework |
| OpenAI | Latest | GPT integration |
| Kafka-Python | Latest | Event streaming |

### **Database \& Infrastructure**

| Technology | Version | Purpose |
| :-- | :-- | :-- |
| PostgreSQL | 16.x | Primary relational database |
| MongoDB | 7.x | Document storage |
| Redis | 7.x | Caching and sessions |
| Apache Kafka | 3.5+ | Message broker |
| Docker | Latest | Containerization |
| Docker Compose | Latest | Multi-container orchestration |

### **Development Tools**

| Tool | Purpose |
| :-- | :-- |
| Black | Python code formatter |
| Ruff | Fast Python linter |
| MyPy | Static type checker |
| Pytest | Testing framework |
| Pre-commit | Git hooks for code quality |
| ESLint | JavaScript/TypeScript linter |


***

## **4. Backend Architecture**

### **Project Structure**

```
backend/
├── alembic/                    # Database migrations
│   ├── versions/              # Migration scripts
│   └── env.py                 # Alembic configuration
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI application entry point
│   ├── api/                   # API endpoints
│   │   ├── v1/
│   │   │   ├── api.py        # API router aggregation
│   │   │   └── endpoints/    # Endpoint modules
│   │   │       ├── auth.py   # Authentication endpoints
│   │   │       ├── deals.py  # Deal management
│   │   │       ├── users.py  # User management
│   │   │       └── ...
│   │   └── mock/             # Mock endpoints for testing
│   ├── core/                  # Core configuration
│   │   ├── config.py         # Settings and environment variables
│   │   ├── security.py       # JWT and password hashing
│   │   ├── logging.py        # Logging configuration
│   │   └── rate_limiter.py   # Rate limiting logic
│   ├── db/                    # Database connections
│   │   ├── postgres.py       # PostgreSQL session management
│   │   ├── mongodb.py        # MongoDB connection
│   │   └── redis.py          # Redis client
│   ├── models/                # SQLAlchemy ORM models
│   │   ├── models.py         # User, Deal models
│   │   ├── evaluation.py     # Vehicle evaluation model
│   │   └── negotiation.py    # Negotiation tracking model
│   ├── schemas/               # Pydantic schemas (DTOs)
│   │   ├── user.py           # User request/response schemas
│   │   ├── deal.py           # Deal schemas
│   │   ├── auth.py           # Auth schemas
│   │   └── ...
│   ├── repositories/          # Data access layer
│   │   ├── user_repository.py
│   │   ├── deal_repository.py
│   │   └── ...
│   ├── services/              # Business logic layer
│   │   ├── auth_service.py   # Authentication logic
│   │   ├── deal_service.py   # Deal business logic
│   │   ├── ai_service.py     # AI/LLM integration
│   │   └── ...
│   ├── middleware/            # Custom middleware
│   │   └── error_middleware.py
│   ├── llm/                   # LLM integration
│   │   ├── agents/           # LangChain agents
│   │   └── prompts/          # Prompt templates
│   ├── tools/                 # Utility tools
│   └── utils/                 # Helper functions
├── tests/                     # Test suite
│   ├── conftest.py           # Pytest configuration
│   ├── test_auth.py
│   ├── test_deals.py
│   └── ...
├── .env.example              # Environment variables template
├── .env.test.example         # Test environment template
├── alembic.ini               # Alembic configuration
├── Dockerfile                # Backend Docker image
├── requirements.txt          # Python dependencies
└── pyproject.toml           # Python project metadata
```


### **Core Components**

#### **1. Main Application (`main.py`)**

The entry point configures FastAPI with:

- **Lifespan Context Manager**: Startup/shutdown event handling
- **CORS Middleware**: Cross-origin resource sharing
- **Error Middleware**: Centralized error handling
- **Request ID Middleware**: Unique request tracking with timing
- **Mock Services**: Conditional mock endpoint registration

```python
Key Features:
- Request ID generation (UUID)
- Processing time tracking
- Conditional mock service activation
- Health check endpoint
- OpenAPI documentation at /docs
```


#### **2. Configuration (`core/config.py`)**

Based on the README and structure, the configuration includes:

```python
Settings (Environment Variables):
- PROJECT_NAME: "AutoDealGenie"
- VERSION: API version
- DESCRIPTION: Project description
- API_V1_STR: "/api/v1"
- POSTGRES_SERVER, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
- MONGODB_URL
- REDIS_HOST, REDIS_PORT
- KAFKA_BOOTSTRAP_SERVERS
- OPENAI_API_KEY
- SECRET_KEY: JWT signing key
- ACCESS_TOKEN_EXPIRE_MINUTES
- BACKEND_CORS_ORIGINS: List of allowed origins
- USE_MOCK_SERVICES: Boolean flag for mock mode
```


#### **3. Security (`core/security.py`)**

Authentication and authorization implementation:

- **Password Hashing**: Bcrypt-based secure hashing
- **JWT Tokens**: HTTP-only cookie-based authentication
- **Token Generation**: Access tokens with expiration
- **Token Verification**: Signature and expiration validation


#### **4. Rate Limiting (`core/rate_limiter.py`)**

Redis-backed rate limiting to prevent abuse:

- Request counting per IP/user
- Configurable limits and time windows
- Automatic cleanup of expired counters


#### **5. Logging (`core/logging.py`)**

Structured logging configuration:

- JSON-formatted logs for production
- Console output for development
- Request ID correlation
- Multiple log levels


### **Data Models**

#### **User Model (`models/models.py`)**

```python
class User:
    id: UUID (Primary Key)
    email: String (Unique, Indexed)
    hashed_password: String
    full_name: String
    is_active: Boolean
    is_superuser: Boolean
    created_at: DateTime
    updated_at: DateTime
```


#### **Deal Model (`models/models.py`)**

```python
class Deal:
    id: UUID (Primary Key)
    user_id: UUID (Foreign Key to User)
    vehicle_make: String
    vehicle_model: String
    vehicle_year: Integer
    asking_price: Decimal
    negotiated_price: Decimal (Optional)
    status: Enum (pending, accepted, rejected, completed)
    notes: Text
    created_at: DateTime
    updated_at: DateTime
```


#### **Evaluation Model (`models/evaluation.py`)**

```python
class Evaluation:
    id: UUID
    deal_id: UUID (Foreign Key)
    market_value: Decimal
    condition_score: Float
    mileage: Integer
    evaluation_date: DateTime
    ai_insights: JSON
    confidence_score: Float
```


#### **Negotiation Model (`models/negotiation.py`)**

```python
class Negotiation:
    id: UUID
    deal_id: UUID (Foreign Key)
    message: Text
    sender_type: Enum (buyer, seller, system)
    offer_amount: Decimal (Optional)
    timestamp: DateTime
    status: Enum (pending, accepted, rejected, countered)
```


### **Repository Layer**

Abstracts database operations:

- `UserRepository`: User CRUD operations
- `DealRepository`: Deal management
- `EvaluationRepository`: Vehicle evaluations
- `NegotiationRepository`: Negotiation history

**Pattern**:

```python
class BaseRepository:
    - get_by_id()
    - get_all()
    - create()
    - update()
    - delete()
    - filter()
```


### **Service Layer**

Business logic implementation:

- `AuthService`: User registration, login, token management
- `DealService`: Deal creation, updates, status transitions
- `AIService`: LLM integration for valuations and insights
- `NotificationService`: User notifications (planned)

***

## **5. Frontend Architecture**

### **Project Structure**

```
frontend/
├── app/                       # Next.js 14 App Router
│   ├── layout.tsx            # Root layout
│   ├── page.tsx              # Home page
│   ├── deals/                # Deals section
│   │   ├── page.tsx          # Deals list
│   │   ├── [id]/            # Dynamic deal details
│   │   └── new/             # Create new deal
│   ├── auth/                 # Authentication pages
│   │   ├── login/
│   │   └── signup/
│   └── api/                  # API routes (if any)
├── components/               # React components
│   ├── ui/                   # UI primitives
│   ├── layout/               # Layout components
│   ├── deals/                # Deal-specific components
│   └── auth/                 # Auth components
├── lib/                      # Utilities
│   ├── api.ts               # API client
│   ├── utils.ts             # Helper functions
│   └── types.ts             # TypeScript types
├── public/                   # Static assets
├── scripts/                  # Build/deployment scripts
├── .env.example             # Environment template
├── next.config.mjs          # Next.js configuration
├── package.json             # Dependencies
├── tailwind.config.ts       # Tailwind CSS config
└── tsconfig.json            # TypeScript config
```


### **Key Components**

#### **API Client (`lib/api.ts`)**

Centralized HTTP client:

```typescript
Features:
- Axios instance configuration
- Base URL from environment
- Request/response interceptors
- Authentication token handling
- Error handling and retry logic
- Cookie-based session management
```


#### **Authentication Flow**

1. User submits credentials to `/api/v1/auth/login`
2. Backend validates and returns JWT in HTTP-only cookie
3. Frontend redirects to dashboard
4. Subsequent requests include cookie automatically
5. Protected routes check authentication status

#### **Deal Management**

- List view with filtering and sorting
- Detail view with evaluation data
- Create/Edit forms with validation
- Real-time status updates

***

## **6. Database Design**

### **PostgreSQL Schema**

#### **Users Table**

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```


#### **Deals Table**

```sql
CREATE TABLE deals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    vehicle_make VARCHAR(100) NOT NULL,
    vehicle_model VARCHAR(100) NOT NULL,
    vehicle_year INTEGER NOT NULL,
    asking_price DECIMAL(12, 2) NOT NULL,
    negotiated_price DECIMAL(12, 2),
    status VARCHAR(50) DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_deals_user_id ON deals(user_id);
CREATE INDEX idx_deals_status ON deals(status);
```


#### **Evaluations Table**

```sql
CREATE TABLE evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
    market_value DECIMAL(12, 2),
    condition_score FLOAT,
    mileage INTEGER,
    evaluation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ai_insights JSONB,
    confidence_score FLOAT
);

CREATE INDEX idx_evaluations_deal_id ON evaluations(deal_id);
```


#### **Negotiations Table**

```sql
CREATE TABLE negotiations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    sender_type VARCHAR(50) NOT NULL,
    offer_amount DECIMAL(12, 2),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending'
);

CREATE INDEX idx_negotiations_deal_id ON negotiations(deal_id);
```


### **MongoDB Collections**

#### **Vehicle History** (Document Store)

```json
{
    "_id": ObjectId,
    "deal_id": "uuid-string",
    "vin": "vehicle-identification-number",
    "history_report": {
        "accidents": [],
        "ownership_history": [],
        "service_records": [],
        "title_info": {}
    },
    "market_data": {
        "comparable_sales": [],
        "price_trends": [],
        "local_inventory": []
    },
    "created_at": ISODate,
    "updated_at": ISODate
}
```


#### **AI Conversation History**

```json
{
    "_id": ObjectId,
    "user_id": "uuid-string",
    "deal_id": "uuid-string",
    "conversation": [
        {
            "role": "user|assistant|system",
            "content": "message content",
            "timestamp": ISODate
        }
    ],
    "metadata": {
        "model": "gpt-4",
        "tokens_used": 1234
    }
}
```


### **Redis Cache Structure**

```
# Session Storage
session:{user_id} -> JSON (user session data, TTL: 24h)

# Rate Limiting
rate_limit:{ip_address}:{endpoint} -> Counter (TTL: 60s)

# Deal Cache
deal:{deal_id} -> JSON (deal data, TTL: 5m)

# User Cache
user:{user_id} -> JSON (user profile, TTL: 1h)
```


***

## **7. API Reference**

### **Base URL**

```
Development: http://localhost:8000/api/v1
Production: https://api.autodealgenie.com/api/v1
```


### **Authentication Endpoints**

#### **POST /auth/signup**

Create a new user account.

**Request Body**:

```json
{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "full_name": "John Doe"
}
```

**Response** (201 Created):

```json
{
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2025-12-24T21:00:00Z"
}
```


#### **POST /auth/login**

Authenticate and receive JWT token in HTTP-only cookie.

**Request Body**:

```json
{
    "email": "user@example.com",
    "password": "SecurePassword123!"
}
```

**Response** (200 OK):

```json
{
    "access_token": "jwt-token-string",
    "token_type": "bearer",
    "user": {
        "id": "uuid",
        "email": "user@example.com",
        "full_name": "John Doe"
    }
}
```

**Cookie Set**: `access_token` (HTTP-only, Secure, SameSite=Lax)

#### **GET /auth/me**

Get current authenticated user.

**Headers**: `Cookie: access_token=...`

**Response** (200 OK):

```json
{
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true
}
```


### **Deal Endpoints**

#### **GET /deals/**

List all deals for authenticated user.

**Query Parameters**:

- `skip`: int (default: 0)
- `limit`: int (default: 100)
- `status`: string (optional filter)

**Response** (200 OK):

```json
[
    {
        "id": "uuid",
        "vehicle_make": "Toyota",
        "vehicle_model": "Camry",
        "vehicle_year": 2022,
        "asking_price": 28000.00,
        "negotiated_price": 26500.00,
        "status": "negotiating",
        "created_at": "2025-12-20T10:00:00Z",
        "updated_at": "2025-12-24T15:30:00Z"
    }
]
```


#### **POST /deals/**

Create a new deal.

**Request Body**:

```json
{
    "vehicle_make": "Honda",
    "vehicle_model": "Accord",
    "vehicle_year": 2023,
    "asking_price": 32000.00,
    "notes": "Excellent condition, low mileage"
}
```

**Response** (201 Created):

```json
{
    "id": "uuid",
    "user_id": "user-uuid",
    "vehicle_make": "Honda",
    "vehicle_model": "Accord",
    "vehicle_year": 2023,
    "asking_price": 32000.00,
    "status": "pending",
    "created_at": "2025-12-24T21:00:00Z"
}
```


#### **GET /deals/{deal_id}**

Get specific deal details.

**Response** (200 OK):

```json
{
    "id": "uuid",
    "vehicle_make": "Honda",
    "vehicle_model": "Accord",
    "vehicle_year": 2023,
    "asking_price": 32000.00,
    "negotiated_price": null,
    "status": "pending",
    "notes": "Excellent condition",
    "evaluation": {
        "market_value": 31500.00,
        "condition_score": 9.2,
        "confidence_score": 0.87
    },
    "negotiations": []
}
```


#### **PUT /deals/{deal_id}**

Update deal information.

**Request Body**:

```json
{
    "negotiated_price": 30000.00,
    "status": "accepted",
    "notes": "Final offer accepted"
}
```


#### **DELETE /deals/{deal_id}**

Delete a deal.

**Response** (204 No Content)

### **Health \& Utility Endpoints**

#### **GET /**

Root endpoint with API information.

#### **GET /health**

Health check endpoint.

**Response** (200 OK):

```json
{
    "status": "healthy"
}
```


***

## **8. Security \& Authentication**

### **Authentication Mechanism**

**JWT-based Authentication with HTTP-only Cookies**

#### **Token Structure**

```json
{
    "sub": "user-uuid",
    "email": "user@example.com",
    "exp": 1735084800,
    "iat": 1735081200
}
```


#### **Security Features**

1. **HTTP-only Cookies**: Prevents XSS attacks
2. **Secure Flag**: HTTPS-only transmission
3. **SameSite**: CSRF protection
4. **Token Expiration**: Configurable (default: 60 minutes)
5. **Password Hashing**: Bcrypt with salt
6. **CORS Configuration**: Restricted origins

### **Authorization**

**Role-Based Access Control (RBAC)**

- `is_active`: User account status
- `is_superuser`: Admin privileges


### **Rate Limiting**

- **Redis-backed**: Distributed rate limiting
- **Per-endpoint limits**: Configurable thresholds
- **IP-based tracking**: Prevent abuse


### **Best Practices Implemented**

- ✅ No credentials in URLs
- ✅ Parameterized queries (SQLAlchemy)
- ✅ Input validation (Pydantic)
- ✅ Error message sanitization
- ✅ HTTPS enforcement in production
- ✅ Environment variable secrets

***

## **9. AI/LLM Integration**

### **LangChain Architecture**

#### **Components**

- **LLM Provider**: OpenAI GPT-4
- **Prompt Templates**: Structured prompts for evaluations
- **Agents**: Autonomous reasoning for complex tasks
- **Tools**: Custom functions for data retrieval
- **Memory**: Conversation history tracking


### **Use Cases**

#### **1. Vehicle Valuation**

```python
Inputs:
- Vehicle make, model, year
- Mileage
- Condition description
- Location

AI Process:
1. Analyze market data
2. Compare similar listings
3. Adjust for condition
4. Generate confidence score

Output:
- Estimated market value
- Price range
- Reasoning explanation
```


#### **2. Negotiation Assistant**

```python
Features:
- Analyze offer history
- Suggest counter-offers
- Identify deal breakers
- Predict acceptance probability
```


#### **3. Market Analysis**

```python
Capabilities:
- Price trend analysis
- Local inventory comparison
- Seasonal adjustments
- Demand forecasting
```


### **Prompt Engineering**

Structured prompts stored in `app/llm/prompts/`:

- `evaluation_prompt.txt`
- `negotiation_prompt.txt`
- `market_analysis_prompt.txt`

***

## **10. Development Workflow**

### **Environment Setup**

#### **With Docker (Recommended)**

```bash
# 1. Clone repository
git clone https://github.com/Raviteja77/autodealgenie.git
cd autodealgenie

# 2. Configure environment
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
# Edit files and add OPENAI_API_KEY

# 3. Start services
docker-compose up -d

# 4. Run migrations
docker-compose exec backend alembic upgrade head

# 5. Access applications
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```


#### **Manual Setup**

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env
alembic upgrade head
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
cp .env.example .env.local
npm run dev
```


### **Code Quality Tools**

#### **Backend**

```bash
# Format code
black .

# Lint
ruff check . --fix

# Type check
mypy .

# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```


#### **Frontend**

```bash
# Lint
npm run lint

# Format
npm run format

# Type check
npm run type-check
```


### **Git Workflow**

```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make changes and commit
git add .
git commit -m "feat: add feature description"

# 3. Push and create PR
git push origin feature/your-feature-name
```


### **Commit Convention**

```
feat: New feature
fix: Bug fix
docs: Documentation changes
style: Code style changes
refactor: Code refactoring
test: Test updates
chore: Build/config changes
```


***

## **11. Deployment Guide**

### **Docker Compose Services**

```yaml
services:
  postgres:
    image: postgres:16
    ports: 5432:5432
    volumes: postgres_data
    
  mongodb:
    image: mongo:7
    ports: 27017:27017
    volumes: mongo_data
    
  redis:
    image: redis:7
    ports: 6379:6379
    
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    
  kafka:
    image: confluentinc/cp-kafka:latest
    ports: 9092:9092
    depends_on: zookeeper
    
  backend:
    build: ./backend
    ports: 8000:8000
    depends_on: [postgres, mongodb, redis, kafka]
    env_file: backend/.env
    
  frontend:
    build: ./frontend
    ports: 3000:3000
    depends_on: backend
    env_file: frontend/.env.local
```


### **Production Deployment**

#### **Environment Variables**

```bash
# Backend
POSTGRES_SERVER=production-db.example.com
POSTGRES_PASSWORD=strong-password
OPENAI_API_KEY=sk-...
SECRET_KEY=cryptographically-strong-secret
BACKEND_CORS_ORIGINS=["https://yourdomain.com"]
USE_MOCK_SERVICES=false

# Frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```


#### **Deployment Steps**

1. Build production images
2. Configure environment variables
3. Set up SSL/TLS certificates
4. Deploy to container orchestration (Kubernetes, ECS, etc.)
5. Configure load balancer
6. Set up monitoring and logging

### **Database Migrations**

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```


***

## **12. Testing Strategy**

### **Backend Testing**

#### **Test Structure**

```
tests/
├── conftest.py              # Fixtures
├── test_auth.py            # Authentication tests
├── test_deals.py           # Deal endpoint tests
├── test_services.py        # Service layer tests
├── test_repositories.py    # Repository tests
└── integration/            # Integration tests
```


#### **Test Categories**

1. **Unit Tests**: Individual functions/methods
2. **Integration Tests**: API endpoints with database
3. **Service Tests**: Business logic validation
4. **Repository Tests**: Data access layer

#### **Example Test**

```python
def test_create_deal(client, auth_headers):
    response = client.post(
        "/api/v1/deals/",
        json={
            "vehicle_make": "Toyota",
            "vehicle_model": "Camry",
            "vehicle_year": 2022,
            "asking_price": 28000.00
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["vehicle_make"] == "Toyota"
```


### **Frontend Testing**

```bash
# Unit tests
npm test

# E2E tests (if configured)
npm run test:e2e
```


### **Test Coverage Goals**

- **Backend**: >80% code coverage
- **Critical paths**: 100% coverage
- **API endpoints**: Full integration testing

***

## **Additional Resources**

### **Documentation Files**

- [README.md](https://github.com/Raviteja77/autodealgenie/blob/main/README.md): Quick start guide
- [SETUP_COMPLETE.md](https://github.com/Raviteja77/autodealgenie/blob/main/SETUP_COMPLETE.md): Detailed setup instructions
- API Documentation: http://localhost:8000/docs (Swagger UI)
- API Documentation: http://localhost:8000/redoc (ReDoc)


### **Repository**

GitHub: [https://github.com/Raviteja77/autodealgenie](https://github.com/Raviteja77/autodealgenie)

### **Support \& Contribution**

- Create GitHub issues for bugs/features
- Follow commit conventions
- Ensure tests pass before PR
- Update documentation for new features

***

## **Appendix: Configuration Reference**

### **Backend Environment Variables**

| Variable | Type | Required | Default | Description |
| :-- | :-- | :-- | :-- | :-- |
| `PROJECT_NAME` | string | No | AutoDealGenie | Project name |
| `VERSION` | string | No | 1.0.0 | API version |
| `POSTGRES_SERVER` | string | Yes | - | PostgreSQL host |
| `POSTGRES_USER` | string | Yes | - | Database user |
| `POSTGRES_PASSWORD` | string | Yes | - | Database password |
| `POSTGRES_DB` | string | Yes | - | Database name |
| `MONGODB_URL` | string | Yes | - | MongoDB connection string |
| `REDIS_HOST` | string | Yes | - | Redis host |
| `REDIS_PORT` | int | No | 6379 | Redis port |
| `KAFKA_BOOTSTRAP_SERVERS` | string | Yes | - | Kafka servers |
| `OPENAI_API_KEY` | string | Yes | - | OpenAI API key |
| `SECRET_KEY` | string | Yes | - | JWT signing key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | int | No | 60 | Token expiration |
| `BACKEND_CORS_ORIGINS` | list | Yes | - | Allowed CORS origins |
| `USE_MOCK_SERVICES` | bool | No | false | Enable mock endpoints |

### **Frontend Environment Variables**

| Variable | Type | Required | Description |
| :-- | :-- | :-- | :-- |
| `NEXT_PUBLIC_API_URL` | string | Yes | Backend API base URL |


***

**End of Documentation**

This comprehensive documentation covers all aspects of the AutoDealGenie platform. For questions or contributions, please refer to the GitHub repository or create an issue.

