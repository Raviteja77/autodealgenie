# Copilot Instructions for AutoDealGenie

## Project Overview

AutoDealGenie is a car-buying assistant web application that guides users through a multi-step process: car preference input, vehicle discovery, negotiation simulation, and deal evaluation.

**Architecture:**
- **Backend**: Python FastAPI with async support (vehicle research and external APIs)
- **Frontend**: Next.js 14+ single-page application with App Router and server-side rendering
- **Databases**: 
  - PostgreSQL (primary relational database for users, deals, loan applications)
  - MongoDB (unstructured data: search history, negotiation conversations, vehicle cache)
- **Infrastructure**: Redis for caching, Kafka for messaging
- **AI Integration**: LangChain with OpenAI for intelligent features
- **Authentication**: JWT tokens stored in HTTP-only cookies
- **Containerization**: Docker and Docker Compose for development

**Current Maturity**: MVP/Early Development - core flows are functional, but error handling, test coverage, and production hardening are incomplete.

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
- For LLM operations: services → llm module (prompts, schemas, client)

### Frontend (TypeScript)
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5
- **UI Libraries**: Material-UI (@mui/material) and Tailwind CSS (limited usage)
- **Styling**: Emotion v11+ for CSS-in-JS
- **Linter**: ESLint (next lint with next/core-web-vitals, TypeScript, react-hooks rules)
- **Validation**: Zod and Yup for runtime type validation (forms, API payloads)

Always:
- Use TypeScript for all new files with explicit types (no `any` unless documented and justified)
- Follow Next.js 14 App Router conventions
- **Always use custom UI components from `components/ui/` for consistency** (Button, Input, Card, Modal, Spinner)
- Prefer Material-UI components for layouts and data display (Grid, Box, Typography, etc.)
- When creating new reusable UI components, add them to `components/ui/` directory
- Use Tailwind CSS for utility-based styling (limited usage)
- Validate API data with Zod schemas
- Use async/await for API calls
- Handle errors gracefully with user-friendly messages
- Use React Context Providers for state management (AuthProvider, FormProvider, CarFormProvider)
- Expose public interfaces via custom hooks (`useAuth`, `useSearch`, `useNegotiation`)
- Avoid importing low-level clients (direct DB clients, FastAPI URLs) from React components

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
│   ├── llm/              # Centralized LLM module
│   │   ├── llm_client.py # AsyncOpenAI client with error handling
│   │   ├── prompts.py    # Prompt template registry
│   │   └── schemas.py    # LLM request/response schemas
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
│   ├── api/              # Next.js API routes
│   │   ├── auth/         # JWT auth routes (login, logout, refresh)
│   │   ├── user/         # User CRUD (PostgreSQL DAL)
│   │   ├── deals/        # Deals management (PostgreSQL DAL)
│   │   ├── loan-applications/  # Loan applications (PostgreSQL DAL)
│   │   ├── research/     # Proxy to FastAPI backend
│   │   ├── history/      # Search history (MongoDB DAL)
│   │   └── negotiation/  # Negotiation conversations (MongoDB DAL)
│   ├── context/          # React Context Providers
│   │   ├── AuthProvider.tsx        # JWT-backed auth state
│   │   ├── FormProvider.tsx        # Search criteria state
│   │   └── CarFormProvider.tsx     # Selected vehicle state
│   ├── dashboard/        # Protected dashboard routes
│   │   ├── search/       # Car search page
│   │   └── results/      # Search results page
│   ├── deals/            # Deals feature pages
│   ├── search/           # Public search pages
│   ├── layout.tsx        # Root layout
│   └── page.tsx          # Home page
├── components/           # Reusable React components
│   ├── Header.tsx
│   ├── Footer.tsx
│   ├── ProgressStepper.tsx
│   ├── forms/            # Form components (CarPreferenceForm, LoanForm)
│   ├── cards/            # Display components (CarCard, CarSelection)
│   └── auth/             # Auth components (AuthLayout, Login, Signup)
├── lib/                  # Utilities and helpers
│   ├── api.ts            # API client configuration
│   ├── auth/             # Auth utilities
│   ├── hooks/            # Custom React hooks
│   ├── theme/            # MUI theme configuration
│   └── errors.ts         # Error handling utilities
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
- **Target**: ~80% coverage for business logic modules and critical UI pieces
- **E2E Testing**: Use Playwright for critical user flows
- **Testing Libraries**: Testing Library and Jest for unit/integration tests

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

### Data Access Layer (DAL)
- **PostgreSQL DAL**: All PostgreSQL operations must go through typed DAL modules (e.g., `pgUserRepository`, `pgDealRepository`, `pgLoanApplicationRepository`)
- **MongoDB DAL**: All MongoDB operations must go through separate DAL modules (e.g., `mongoHistoryRepository`, `mongoConversationRepository`, `mongoCacheRepository`)
- **No Direct Queries**: Never use direct SQL queries or direct Mongoose/driver calls from API routes or React components
- **Data Strategy**:
  - PostgreSQL: Users, Deals, Loan Applications (relational data)
  - MongoDB: Search history, Negotiation conversations, Vehicle cache (unstructured/high-variance data)

### LLM Integration (Separation of Concerns)
- **Centralized LLM Module**: All LLM operations must use the centralized `app/llm` module
- **Never use LangChain or OpenAI directly** in service files - use the abstraction layer in `app/llm/`
- **Architecture**:
  - `app/llm/llm_client.py` - Single AsyncOpenAI client instance with error handling
  - `app/llm/prompts.py` - Centralized prompt template registry
  - `app/llm/schemas.py` - Pydantic models for LLM request/response validation
  - `app/llm/__init__.py` - Public API with convenience functions
- **Usage Pattern**:
  ```python
  from app.llm import generate_structured_json, generate_text
  from app.llm.schemas import DealEvaluation
  
  # For structured JSON responses
  result = await generate_structured_json(
      prompt_id="evaluation",
      variables={"vin": vin, "asking_price": price},
      response_model=DealEvaluation,
      temperature=0.7
  )
  
  # For text responses
  text = await generate_text(
      prompt_id="negotiation_initial",
      variables={"make": make, "model": model},
      temperature=0.7
  )
  ```
- **Adding New Prompts**:
  1. Add prompt template to `app/llm/prompts.py` in the PROMPTS registry
  2. If structured output needed, create Pydantic schema in `app/llm/schemas.py`
  3. Export schema from `app/llm/__init__.py`
  4. Add test coverage in `tests/llm/test_schemas.py`
- **Benefits**:
  - Single source of truth for OpenAI configuration
  - Consistent error handling across all LLM calls
  - Easy to mock in tests
  - Prompt versioning and management in one place
  - Type-safe responses with Pydantic validation

### Authentication
- JWT-based authentication with HTTP-only cookies (never use `localStorage` for tokens)
- Tokens must live only in HTTP-only cookies
- See `AUTHENTICATION.md` for detailed documentation
- Use FastAPI dependencies for auth: `get_current_user`, `get_current_active_user`
- Implement robust refresh token handling and clear token expiry behavior
- Frontend reads user state through `AuthProvider` + `useAuth` hook (never from cookies or storage directly)

### API Routes (Next.js)
- Next.js API routes under `app/api/` handle HTTP boundary logic
- Public routes: `/api/auth/login`, `/api/auth/signup`, `/api/auth/logout`
- Protected routes: `/api/user`, `/api/deals`, `/api/loan-applications`, `/api/history`, `/api/negotiation`
- External proxy: `/api/research` (proxies to FastAPI backend)
- Use Zod for request validation; avoid generic error responses
- Wrap external API and DB operations in `try/catch`
- Use shared error helpers like `ApiError` and `handleApiError` with consistent JSON error envelopes

### FastAPI Backend Endpoints
- All FastAPI endpoints are under `/api/v1/`
- Public endpoints: `/api/v1/health`, `/api/v1/auth/signup`, `/api/v1/auth/login`
- Protected endpoints require authentication
- Use proper HTTP status codes (200, 201, 400, 401, 403, 404, 422, 500)

### Error Handling
- Backend: Use FastAPI's HTTPException for API errors
- Frontend: Handle errors with try-catch and display user-friendly messages
- Add React Error Boundaries around major feature areas
- Integrate centralized error logging (e.g., Sentry) for API routes and client errors

### Component Composition & State Management
- Prefer context and composition over props drilling (>2 levels deep)
- Keep components under ~5 props; use custom hooks to bundle behavior
- Use React Context Providers: `AuthProvider`, `FormProvider`, `CarFormProvider`
- Replace `localStorage` as primary source of truth for multi-step flows; rely on server state + URL parameters

### UI Components & Styling
- **Always use custom UI components** from `components/ui/` for interactive elements (Button, Input, Card, Modal, Spinner)
- Custom components ensure consistency across the application and are built on top of Material-UI
- Available custom components:
  - `Button`: Use for all button interactions with variants (primary, secondary, danger, success, outline)
  - `Input`: Use for text input fields with built-in validation support
  - `Card`: Use for content containers with consistent styling
  - `Modal`: Use for modal dialogs and overlays
  - `Spinner`: Use for loading states
- When creating new reusable UI components, add them to `components/ui/` directory with:
  - TypeScript interfaces for props
  - Material-UI as the base implementation
  - Consistent styling using MUI theme
  - Export from `components/ui/index.ts`
- For one-off UI needs or layouts, use Material-UI components directly (Grid, Box, Typography, Stack, etc.)

### Component Architecture & Organization
- Follow **Atomic Design** principles: Atoms → Molecules → Organisms → Templates → Pages
- **Atoms**: Basic UI elements (Button, Input, Card, Spinner) in `components/atoms/`
- **Molecules**: Combinations of atoms (PriceDisplay, VehicleTitle) in `components/molecules/`
- **Organisms**: Complex UI sections (FilterPanel, VehicleCard) in `components/organisms/`
- **Feature Components**: Page-specific components in `components/{feature}/` (e.g., `components/evaluation/`, `components/negotiation/`)
- **Page Files**: Should be thin orchestration layers (<400 LOC) that compose components
- **No Hardcoded Values**: Extract all magic numbers, strings, and configuration to `lib/constants/`
- **No Hardcoded Text in HTML/JSX**: All UI text, labels, messages, and button text must come from `lib/constants/text.ts`
  - Never use hardcoded strings like "Search", "Loading...", "Error", "Back", etc. in JSX
  - All user-facing text should be defined in constants with descriptive names
  - Group related text by feature/page (e.g., `EVALUATION_TEXT`, `SEARCH_TEXT`, `DEALS_TEXT`)
  - Use constants for: titles, descriptions, button labels, error messages, empty states, tooltips, alerts
  - Example: Instead of `<Button>Start Negotiation</Button>`, use `<Button>{EVALUATION_TEXT.ACTIONS.START_NEGOTIATION}</Button>`
- **Centralize Logic**: Move business logic to custom hooks in `lib/hooks/` or utilities in `lib/utils/`
- **Component Reusability**: If a component is used in 2+ pages, extract it to a shared location
- **Single Responsibility**: Each component should have one clear purpose
- **Composition Over Inheritance**: Build complex UIs by composing simple components

### File Naming Conventions
- Components: `PascalCase.tsx`
- Hooks: `usePascalCase.ts`
- Utilities: `camelCase.ts`
- API routes: `kebab-case/route.ts` under `app/api`

### Environment Configuration
- No hardcoded URLs or keys; use `config/environment.ts` (or equivalent) to centralize env access
- Backend: Configure in `backend/.env` (see `backend/.env.example`)
- Frontend: Configure in `frontend/.env.local` (see `frontend/.env.example`)
- Never commit `.env` files to version control

## Important Notes

### Technical Debt & Known Issues
- **Authentication**: Tokens must live only in HTTP-only cookies; remove any `localStorage` usage for auth
- **Data Layer**: Separate DALs for PostgreSQL (`pg/*`) and MongoDB (`mongo/*`) must be used consistently
- **Error Boundaries**: React Error Boundaries needed around major feature areas
- **Form State**: Replace `localStorage` as primary source of truth for multi-step flows
- **Module Encapsulation**: Avoid importing low-level clients from React components

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
1. Follow the established project structure and patterns (Modified MVC with React Context + service/DAL layers)
2. Use the existing abstractions (repositories, services, schemas, context providers)
3. Write type-safe code with proper type hints (no `any` unless justified)
4. Include error handling and validation (use Zod for request validation)
5. Consider async operations for I/O-bound tasks
6. Keep code DRY (Don't Repeat Yourself)
7. Write unit tests for new functionality (target ~80% coverage)
8. Format code according to project standards before committing
9. Update documentation if adding new features or changing behavior
10. **Always use custom UI components from `components/ui/`** (Button, Input, Card, Modal, Spinner) for consistency
11. Use Material-UI components for layouts and data display (Grid, Box, Typography, etc.)
12. Always use DAL modules for database access (never direct queries)
13. Store auth tokens only in HTTP-only cookies (never `localStorage`)
14. Use React Context Providers and custom hooks for state management
15. Keep components under ~5 props; prefer composition over props drilling
16. When creating new reusable components, add them to `components/ui/` with proper TypeScript interfaces

### Code Quality Best Practices
17. **No Hardcoded Values**: Extract all magic numbers, strings, and configuration to `lib/constants/`
18. **No Hardcoded Text in UI**: All user-facing text must come from `lib/constants/text.ts` - no strings in JSX/HTML
19. **Centralize Logic**: Move business logic to custom hooks (`lib/hooks/`) or utilities (`lib/utils/`)
20. **Component Size**: Keep page files under 400 LOC; extract UI sections to feature components
21. **Atomic Design**: Follow atoms → molecules → organisms → pages hierarchy
22. **Single Responsibility**: Each component should do one thing well
23. **Reusability**: Extract components used in 2+ places to shared locations
24. **Type Safety**: Use TypeScript interfaces for all props and return values
25. **Error Boundaries**: Wrap feature areas with error boundaries for graceful failures
26. **Consistent Naming**: Use PascalCase for components, camelCase for functions/variables, UPPER_CASE for constants
27. **API Layer**: Use custom hooks for API calls, never call apiClient directly from components
28. **URL State**: Use custom hooks (`useVehicleFromParams`, `useQueryParams`) for URL parameter handling
29. **Loading States**: Use `LoadingState`, `ErrorState`, `EmptyState` components for consistent UX
30. **Constants Organization**: Group related constants in feature-specific files under `lib/constants/`
31. **Text Constants**: Group UI text by feature in `lib/constants/text.ts` (e.g., `EVALUATION_TEXT`, `SEARCH_TEXT`)
32. **Utility Functions**: Extract repeated logic to `lib/utils/` with clear function names and JSDoc comments

## Future Roadmap

Features in development or planned:
- **Real-Time Negotiation Agent**: MongoDB for conversation history, PostgreSQL for finalized deals
- **Vehicle History Integration**: Vehicle reports cached in MongoDB, linked to deals in PostgreSQL
- **Loan Pre-Approval Workflow**: Loan applications in PostgreSQL with encrypted sensitive fields
- **Multi-User Collaboration**: Shared searches and permissions in PostgreSQL, activity streams in MongoDB
- **Advanced Search Filters & Saved Searches**: Search definitions in PostgreSQL, history in MongoDB
- **Edge Caching**: Vehicle research results via Redis/KV store and MongoDB cache
- **Client Bundle Optimization**: Dynamic imports and MUI tree-shaking
