# AutoDealGenie — Architecture Decisions

> **Rule**: Every significant technical decision lives here with its WHY.
> Before arguing against any of these, read the reasoning first.
> To change a decision: add a new entry that supersedes the old one.

---

## The Guiding Principle for ALL Decisions
**"One feature = one folder."**
When you work on a feature, you should only need to open ONE folder,
read 3-5 files, and be done. If a small change touches 10+ files,
the architecture is the problem — not the developer.

---

## Backend Decisions

### Feature-Based Folder Structure (NOT type-based)
**Decision**: Backend organized by feature, not by type.
```
# ✅ How it looks
app/features/
    auth/
        router.py      ← HTTP endpoints
        service.py     ← business logic
        models.py      ← SQLAlchemy models
        schemas.py     ← Pydantic request/response types
    deals/
        router.py
        service.py
        models.py
        schemas.py
    evaluations/
        router.py
        service.py
        models.py
        schemas.py
app/core/              ← shared: config, security, DB connections
app/llm/               ← shared: all AI/OpenAI calls
app/tools/             ← shared: external APIs (MarketCheck)
```
**Why**: Working on deals = read `app/features/deals/` (4 files). Old way
required jumping across 5 separate directories. Cuts Claude's context window
usage ~60% for typical tasks. You stay focused. Claude stays focused.
**What we rejected**: Type-based folders (/endpoints/, /services/, /repositories/).
They organize by what code IS, not what it DOES. Makes feature work painful.

### PostgreSQL Only — No MongoDB
**Decision**: One database: PostgreSQL. Use JSONB columns for flexible data.
```sql
-- Search history (was MongoDB)
CREATE TABLE search_history (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    query JSONB,        -- flexible search params
    results JSONB,      -- cached vehicle results
    created_at TIMESTAMPTZ
);
```
**Why**: MongoDB was added for "flexibility" — PostgreSQL JSONB does the same.
Two databases = double the connection logic, double the mental overhead, double
the things that can break. Claude also had to decide "Postgres or Mongo?" on
every query — wasted context. One DB means one mental model.
**What we rejected**: Keeping MongoDB. We can add it back if JSONB proves too
slow at scale. That is not a problem we have today.

### No RabbitMQ — Use FastAPI Background Tasks
**Decision**: Remove RabbitMQ. Use FastAPI's BackgroundTasks for async work.
```python
@router.post("/evaluations/")
async def start_evaluation(
    request: EvaluationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    evaluation = await service.create(db, request)
    background_tasks.add_task(service.run_pipeline, evaluation.id)
    return evaluation
```
**Why**: RabbitMQ needs a running broker, connection management, retry logic,
dead-letter queues, and fallback code when it goes down. FastAPI BackgroundTasks
handles 95% of our async needs today. Add a real queue (Celery or pg-boss) only
when you hit a concrete scaling problem.
**What we rejected**: Keeping RabbitMQ "for scale." Premature complexity.

### LLM Calls Stay Centralized in app/llm/
**Decision**: All OpenAI calls go through app/llm/. Services call
generate_structured_json() — never import OpenAI SDK in services directly.
```
app/llm/
    client.py      ← single OpenAI client, retry logic, cost logging
    prompts.py     ← all prompt templates
    schemas.py     ← all LLM response Pydantic models
    __init__.py    ← exports: generate_structured_json, generate_text
```
**Why**: One place to change models, add logging, handle retries, monitor costs.
Switch providers = change one file. No LangChain — removed, too much abstraction.
**What we rejected**: Calling OpenAI in services directly. Spreads AI everywhere.

### Keep Redis (Caching Only)
**Decision**: Keep Redis, but ONLY for caching. Not for sessions, not queuing.
- Cache: search results (15 min TTL), evaluations (1 hr TTL)
- Sessions: HTTP-only JWT cookies handle this — no Redis needed
- Queuing: replaced by BackgroundTasks
**Why**: Redis for caching is a clear win. Limiting its role keeps it simple.
Graceful in-memory fallback already built for when Redis is down.

---

## Frontend Decisions

### Feature-Based Component Folders (NOT atomic design)
**Decision**: Components organized by feature, not by atomic tier.
```
components/
    ui/              ← shadcn/ui base components (Button, Input, Card...)
                       OWNED code — copied into repo, not a dependency.
    search/          ← all search components in one folder
        VehicleCard.tsx
        SearchFilters.tsx
        SearchResults.tsx
    deals/           ← all deal components
    negotiation/     ← all negotiation components
    evaluation/      ← all evaluation components
    layout/          ← Header, Footer, Sidebar
```
**Why**: Old atomic design (atoms/molecules/organisms) meant changing one
VehicleCard feature touched 3 layers + tests at each layer.
Feature folders = working on search = open components/search/. Done.
**What we rejected**: Atomic design. Good theory, painful for solo dev + AI.
Adding a button variant touched 4-5 files. Now it touches 1.

### shadcn/ui as Base Component Library
**Decision**: shadcn/ui for all base UI components. Not MUI.
**Why**:
- Components are COPIED into your repo (components/ui/) — you own them
- No wrapper layer needed (old setup wrapped MUI in custom "atom" components)
- Adding a Button variant = edit one file. Nothing else changes.
- Tailwind-native, accessible, modern
**What we rejected**: Keeping MUI v5. Required a custom wrapper layer to enforce
consistency. Two layers (MUI + our atoms) where one (shadcn) does the job.

### Zustand for Global State (NOT multiple Context Providers)
**Decision**: Zustand store instead of 5 stacked Context Providers.
```typescript
// Old: 5 providers in layout.tsx
// <ThemeProvider><AuthProvider><StepperProvider><CarFormProvider>...

// New: import what you need, anywhere
import { useAuthStore } from '@/store/auth'
import { useSearchStore } from '@/store/search'

store/
    auth.ts          ← user session, login/logout
    search.ts        ← search form, results
    negotiation.ts   ← negotiation session, messages
    ui.ts            ← modals, loading states
```
**Why**: 5 providers = 5 mental models. Zustand is flat, debuggable, and any
component reads any state it needs directly. No "which context is this from?"
Claude never has to trace through a provider stack to find a value.
**What we rejected**: Keeping Context Providers. Created cognitive overhead.

### JWT in HTTP-only Cookies (NOT localStorage)
**Decision**: JWT in HTTP-only cookies. Never localStorage.
**Why**: localStorage is readable by any JS on the page (XSS risk). HTTP-only
cookies are invisible to JavaScript. Sent automatically with every request.
**What we rejected**: localStorage. Old codebase used this — security risk.

### Server Components by Default
**Decision**: Every component is a Server Component unless it needs interactivity.
Only add "use client" for: useState, useEffect, event handlers, browser APIs.
**Why**: Less JS sent to browser. Simpler data fetching (async functions, no
useEffect chains). Better performance.

---

## API / Integration Decisions

### Single Typed API Client (lib/api.ts)
**Decision**: All frontend→backend calls go through one apiClient object.
Components never call fetch() directly.
**Why**: One place for auth headers, error handling, retry logic. One file
to change when a URL changes. Claude never searches for "where is this called?"

### Partners (Lenders/Insurers) in Database From Day One
**Decision**: Partner data in a partners PostgreSQL table. Never hardcoded.
**Why**: Can't onboard real partners with arrays in code. Need to add/remove
without a code deploy. Build it right from the start.

---

## What We Are NOT Building Yet
Explicitly deferred — add only when core product has real users:
- Real partner API integrations (use scored mock data for now)
- Vehicle history (Carfax/AutoCheck)
- Price prediction engine
- Mobile app
- Email notifications
- Multi-user collaboration

Premature features are the #1 cause of complexity that never gets used.