# AutoDealGenie
AI-powered car-buying assistant. Users search vehicles, get AI deal scores,
negotiate with an AI coach, and get lender + insurance recommendations.

<!-- Architecture: feature-based folders. One feature = one folder. Max 3-5 files
     per task. See DECISIONS.md for every major choice and its reasoning. -->

## Stack
- **Frontend**: Next.js 14 (App Router), TypeScript strict, shadcn/ui, Tailwind, Zod
- **Backend**: Python FastAPI, SQLAlchemy 2.0 async, Pydantic v2, Alembic
- **AI**: OpenAI SDK only (no LangChain), all calls centralized in `backend/app/llm/`
- **DBs**: PostgreSQL only (JSONB for flexible data), Redis (cache only)
- **Async**: FastAPI BackgroundTasks (no RabbitMQ)
- **Deploy**: Docker Compose locally → GCP Cloud Run

## Commands
```bash
# Backend
cd backend && uvicorn app.main:app --reload   # start (port 8000)
cd backend && pytest                           # all tests
cd backend && pytest -k "test_name" -v        # one test
cd backend && black . && ruff check . --fix   # format + lint
cd backend && mypy .                           # type check
cd backend && alembic upgrade head             # run migrations
cd backend && alembic revision --autogenerate -m "desc"  # new migration

# Frontend
cd frontend && npm run dev                     # start (port 3000)
cd frontend && npm test                        # jest
cd frontend && npm run lint && npx tsc --noEmit  # lint + type check

# Docker
docker-compose up -d && docker-compose logs -f backend
```

## Architecture Rules (NEVER violate)
```
Backend:  router.py → service.py → (models.py + schemas.py)
                           ↓
                      app/llm/  ← ONLY place OpenAI is called
                      app/tools/ ← ONLY place MarketCheck is called

Frontend: page.tsx → components/[feature]/ → components/ui/
                ↓
            lib/api.ts ← ONLY place fetch() is called
            store/     ← ONLY place global state lives (Zustand)
```

## Memory System (READ before starting any task)
- What we're building & current status → @.claude/memory/PROGRESS.md
- Architecture decisions and WHY → @.claude/memory/DECISIONS.md
- Project-specific mistakes to avoid → @.claude/memory/GOTCHAS.md

## Skills (load on demand — never auto-load all)
- Planning a feature → @.claude/skills/architect.md
- Backend Python work → @.claude/skills/fastapi-python.md
- Frontend TypeScript work → @.claude/skills/nextjs-frontend.md
- Code review → @.claude/skills/senior-dev.md
- Testing / QA → @.claude/skills/qa-expert.md

## Code Quality Standard
Write code that a competent developer can understand, modify safely, and extend
without fear. This means following industry standards — not oversimplifying, not
over-engineering. Detailed principles auto-load per file type via `.claude/rules/`.

The short version:
- **Clear intent**: names say what things do; functions do one thing
- **Right abstractions**: use established patterns (repository, service layer, hooks)
  but only add a new abstraction when you have a concrete reason, not in advance
- **Fail loudly**: validate at every boundary; never swallow errors silently
- **No dead code**: if it's not used, delete it
- **No `any`** in TypeScript; no untyped functions in Python
- **Tests prove it works**: every feature ships with at least one test

## Task Workflow
1. **Plan first** — 3+ step tasks get a written plan in `tasks/todo.md` first
2. **Check in** — confirm the plan before coding
3. **Track** — check off items as you go
4. **Verify** — prove it works before calling it done ("would a staff engineer approve this?")
5. **Capture** — after any correction, update `tasks/lessons.md` and `GOTCHAS.md`

## Session Start / End
- Start: read `tasks/lessons.md` for patterns relevant to today's work
- End: update `PROGRESS.md` and `tasks/lessons.md` (ask Claude to do this)
- `/compact` at ~50% context: "preserve task, files changed, open decisions"
- `/clear` when switching to a completely different task

## Hard Rules (no exceptions)
- NEVER commit `.env` files or any secrets
- All LLM calls through `app/llm/` only — no direct OpenAI imports in services
- All API calls through `lib/api.ts` only — no raw fetch() in components
- All base UI through `components/ui/` — no raw HTML buttons/inputs in pages
- Bug fix = find root cause, not patch symptom. Write the regression test after.
