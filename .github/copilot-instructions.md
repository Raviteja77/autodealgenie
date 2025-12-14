# Copilot Instructions for AutoDealGenie

## Project Overview

AutoDealGenie is an AI-powered automotive deal management platform with:
- **Backend**: Python FastAPI with async support
- **Frontend**: Next.js 14 with TypeScript, Material-UI, and Tailwind CSS
- **Databases**: PostgreSQL (with SQLAlchemy ORM) and MongoDB (with Motor)
- **Infrastructure**: Redis for caching, Kafka for messaging
- **AI Integration**: LangChain with OpenAI for intelligent features
- **Containerization**: Docker and Docker Compose for development

## Code Style and Standards

### Backend (Python)
- **Python Version**: 3.11+
- **Formatter**: Black (line-length: 100)
- **Linter**: Ruff (line-length: 100)
- **Type Checking**: MyPy (with lenient settings for untyped definitions)
- **Testing**: Pytest with async support
- **Pre-commit Hooks**: Configured in `.pre-commit-config.yaml`

Always:
- Use async/await for I/O operations
- Follow FastAPI best practices with Pydantic schemas
- Use dependency injection for database sessions and services
- Write type hints for function parameters and return values
- Keep line length at 100 characters
- Use SQLAlchemy models for PostgreSQL and Motor for MongoDB
- Organize code in layers: endpoints → services → repositories → models

### Frontend (TypeScript)
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5
- **UI Libraries**: Material-UI (@mui/material) and Tailwind CSS
- **Linter**: ESLint (next lint)
- **Validation**: Zod for runtime type validation

Always:
- Use TypeScript for all new files
- Follow Next.js 14 App Router conventions
- Prefer Material-UI components over custom implementations
- Use Tailwind CSS for utility-based styling
- Validate API data with Zod schemas
- Use async/await for API calls
- Handle errors gracefully with user-friendly messages

## Project Structure

### Backend (`/backend`)
```
backend/
├── alembic/              # Database migrations
│   └── versions/
├── app/
│   ├── api/v1/
│   │   ├── endpoints/    # API route handlers
│   │   └── api.py        # API router configuration
│   ├── core/             # Configuration and settings
│   ├── db/               # Database connections (PostgreSQL, MongoDB, Redis)
│   ├── models/           # SQLAlchemy ORM models
│   ├── repositories/     # Data access layer
│   ├── schemas/          # Pydantic request/response schemas
│   ├── services/         # Business logic layer
│   └── main.py           # FastAPI app entry point
├── tests/                # Test suite
├── .env.example          # Environment variables template
├── pyproject.toml        # Python tooling configuration
└── requirements.txt      # Python dependencies
```

### Frontend (`/frontend`)
```
frontend/
├── app/                  # Next.js 14 app directory (App Router)
│   ├── deals/            # Deals feature pages
│   ├── layout.tsx        # Root layout
│   └── page.tsx          # Home page
├── components/           # Reusable React components
├── lib/                  # Utilities and helpers
│   └── api.ts            # API client configuration
├── .env.example          # Environment variables template
├── next.config.mjs       # Next.js configuration
├── package.json          # Node.js dependencies
├── tailwind.config.ts    # Tailwind CSS configuration
└── tsconfig.json         # TypeScript configuration
```

## Development Workflow

### Running the Application
- **Docker**: `docker-compose up -d` (starts all services)
- **Backend Only**: `cd backend && uvicorn app.main:app --reload`
- **Frontend Only**: `cd frontend && npm run dev`

### Testing
- **Backend**: `cd backend && pytest` (with coverage: `pytest --cov=app`)
- **Frontend**: `cd frontend && npm test`

### Code Quality
- **Backend**: 
  - Format: `cd backend && black .`
  - Lint: `cd backend && ruff check . --fix`
  - Type check: `cd backend && mypy .`
  - Pre-commit: `cd backend && pre-commit run --all-files`
- **Frontend**: 
  - Lint: `cd frontend && npm run lint`

### Database Migrations
- **Create**: `cd backend && alembic revision --autogenerate -m "Description"`
- **Apply**: `cd backend && alembic upgrade head`
- **Rollback**: `cd backend && alembic downgrade -1`

## Key Conventions

### Authentication
- JWT-based authentication with HTTP-only cookies
- See `AUTHENTICATION.md` for detailed documentation
- Use FastAPI dependencies for auth: `get_current_user`, `get_current_active_user`

### API Endpoints
- All endpoints are under `/api/v1/`
- Public endpoints: `/api/v1/health`, `/api/v1/auth/signup`, `/api/v1/auth/login`
- Protected endpoints require authentication
- Use proper HTTP status codes (200, 201, 400, 401, 403, 404, 422, 500)

### Error Handling
- Backend: Use FastAPI's HTTPException for API errors
- Frontend: Handle errors with try-catch and display user-friendly messages

### Environment Variables
- Backend: Configure in `backend/.env` (see `backend/.env.example`)
- Frontend: Configure in `frontend/.env.local` (see `frontend/.env.example`)
- Never commit `.env` files to version control

## Important Notes

### Coverage Exclusions
The following files are excluded from test coverage (as they require external service dependencies and are better suited for integration tests):
- `app/db/mongodb.py` - MongoDB connection handling
- `app/db/redis.py` - Redis cache integration
- `app/services/kafka_consumer.py` - Kafka message consumption
- `app/services/kafka_producer.py` - Kafka message production
- `app/services/langchain_service.py` - LangChain AI integration
- `app/services/car_recommendation_service.py` - AI-powered recommendation engine
- `app/tools/marketcheck_client.py` - External automotive market API client

### Dependencies
- Minimize new dependencies
- When adding dependencies, ensure they're compatible with Python 3.11+ or Node.js 20+
- Update `requirements.txt` (backend) or `package.json` (frontend)

### Documentation
- Update relevant documentation when changing functionality
- Key docs: `README.md`, `AUTHENTICATION.md`, `DEVELOPMENT.md`
- Keep API documentation current (FastAPI auto-generates Swagger docs)

## Suggestions for Copilot

When generating code:
1. Follow the established project structure and patterns
2. Use the existing abstractions (repositories, services, schemas)
3. Write type-safe code with proper type hints
4. Include error handling and validation
5. Consider async operations for I/O-bound tasks
6. Keep code DRY (Don't Repeat Yourself)
7. Write unit tests for new functionality
8. Format code according to project standards before committing
9. Update documentation if adding new features or changing behavior
10. Use Material-UI components for frontend UI elements
