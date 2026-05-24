# AutoDealGenie — Gotchas & Project-Specific Rules

> **Purpose**: Things Claude has gotten wrong in this project before, or
> project-specific rules that override Claude's defaults. Claude reads this
> to avoid repeating mistakes. Add to this file whenever Claude makes a
> mistake you have to correct.

---

## Backend Gotchas

### LLM / AI
- ❌ DO NOT import `from openai import OpenAI` in service files
- ✅ Use `from app.llm import generate_structured_json, generate_text`
- ❌ DO NOT use LangChain — it was removed from this project
- ❌ DO NOT forget `await` on `generate_structured_json()` — it's async

### Database / ORM
- All DB sessions are **async** — use `AsyncSession`, never sync `Session`
- Always use `await db.commit()` and `await db.refresh(obj)` after creates/updates
- PostgreSQL for structured data (users, deals, evaluations, negotiations)
- MongoDB for documents (search history, vehicle cache, chat history)
- Never do direct SQL — use SQLAlchemy ORM or repository methods

### API Patterns
- All endpoints return Pydantic models — never raw dicts
- FastAPI `Depends()` for: database session, current user, rate limiter
- Rate limiting is applied at the endpoint level, not in services
- Auth check: use `current_user: User = Depends(get_current_user)` as parameter
- Protected route = add `current_user` dependency. Public route = omit it.

### Error Handling
- Raise `HTTPException` in endpoints for HTTP errors
- Raise `ServiceException` (custom) in services for business logic errors
- Never let raw Python exceptions bubble up to the HTTP layer
- Log errors with `logger.error(f"...", exc_info=True)` to capture stack trace

---

## Frontend Gotchas

### Components
- ❌ DO NOT use raw `<button>` or `<input>` HTML in pages or organisms
- ✅ Use `<Button>` from `components/atoms/Button`
- ❌ DO NOT call API endpoints directly in page components with `fetch()`
- ✅ Use `apiClient.[method]()` from `lib/api.ts`
- ❌ DO NOT add `"use client"` by default — Next.js App Router is Server-first
- ✅ Add `"use client"` ONLY when you need: useState, useEffect, event handlers, browser APIs

### State Management
- Auth state → `useAuth()` hook (from AuthProvider)
- Multi-step form state → `useStepper()` hook (from StepperProvider)
- Car search form state → `useCarForm()` hook (from CarFormProvider)
- WebSocket / negotiation state → `useNegotiationChat()` (from NegotiationChatProvider)
- Local component state only → `useState()`

### TypeScript
- No `any` types — use `unknown` and narrow it, or define a proper type
- All API response types are in `lib/types.ts` or inline Zod schemas in `lib/validation/`
- Form validation uses Zod — schema in `lib/validation/`, not inline in components

### Routing
- All authenticated pages live under `/dashboard/` or `/deals/`
- Route protection uses `withAuth` HOC or middleware — never check auth manually in page components
- Auth pages (`/auth/*`) use `withPublic` HOC to redirect if already logged in

---

## Architecture Gotchas

### What Goes Where
| You want to... | Put it in... |
|---------------|-------------|
| HTTP request handling + validation | `app/api/v1/endpoints/` |
| Business logic + LLM calls | `app/services/` |
| Database queries | `app/repositories/` |
| OpenAI calls | `app/llm/` ONLY |
| External API calls (MarketCheck etc) | `app/tools/` |
| React state logic | `lib/hooks/` |
| API calls | `lib/api.ts` |
| Shared TypeScript types | `lib/types.ts` |
| Form validation schemas | `lib/validation/` |

### File Naming (Python)
- Endpoints: `app/api/v1/endpoints/my_feature.py`
- Services: `app/services/my_feature_service.py`
- Repositories: `app/repositories/my_feature_repository.py`
- Models: `app/models/my_feature.py`
- Schemas: `app/schemas/my_feature_schemas.py`

### File Naming (TypeScript)
- Components: `PascalCase.tsx` (e.g., `VehicleCard.tsx`)
- Hooks: `useCamelCase.ts` (e.g., `useVehicleSearch.ts`)
- Utilities: `camelCase.ts` (e.g., `formatCurrency.ts`)
- Types: `PascalCase` interface/type (e.g., `VehicleResult`)

---

## Correction Log
> Add to this section when you correct Claude's mistake, so it doesn't happen again.
> Format: **[Date] — What was wrong → What is correct**

- [Add corrections here as you encounter them]
