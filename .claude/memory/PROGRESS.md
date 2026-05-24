# AutoDealGenie — Project Progress Memory

> **HOW TO USE**: Claude reads this at the start of every session.
> At end of each session, ask Claude: "Update PROGRESS.md with what we did."
> This file is your anti-context-rot weapon. Keep it current.

---

## Current Phase
**MVP 1** — Fix critical bugs → UI redesign → ship core flow

## MVP 1 Scope (in priority order)

### Phase 1A — Critical Bug Fixes ✅ DONE (2026-05-23)
- [x] Fix `generate_structured_json` in `evaluate_deal()`: was using `await` on a sync
      function → TypeError caught silently → always fell back to heuristic. Fixed with
      `asyncio.to_thread()` so the LLM call is now non-blocking AND correct.
- [x] Fix `generate_structured_json` in `_evaluate_vehicle_condition()`: was calling sync
      function directly (blocked event loop). Wrapped in `asyncio.to_thread()`.
- [x] Fix all 4 `generate_text()` calls in `negotiation_service.py`: same pattern —
      sync blocking calls inside async functions. All wrapped in `asyncio.to_thread()`.
- Files changed: `backend/app/services/deal_evaluation_service.py`,
                 `backend/app/services/negotiation_service.py`

### Phase 1B — Design System ✅ RESOLVED (2026-05-24)
- Committed to shadcn/ui + Tailwind for all pages. MUI fully removed.
- All new pages use custom components in `components/ui/`, `components/layout/`.

### Phase 1C — Core UI Redesign ✅ DONE (2026-05-24)
- [x] Auth (login + signup) — real API, username field, HTTP-only cookie auth
- [x] Search — functional, real MarketCheck API
- [x] Results — real API, vehicle cards with AI scores; saves selected vehicle to flowState
- [x] Evaluation — real 5-step pipeline; creates deal, runs all steps, shows real scores/insights/lenders
- [x] Negotiation — real API; creates session, live chat + counter/accept, saves to flowState
- [x] Summary — real API; reads session, shows actual conversation recap + deal figures
- [x] Deals — real API; fetches user's deals, empty state if none, no mock data
- [x] AppShell sidebar — shows real logged-in user (name, email, initials); logout popover

### Phase 1D — Auth ✅ DONE (2026-05-24)
- [x] HTTP-only cookie auth — AuthProvider no longer uses localStorage; always calls
      getCurrentUser() on mount; browser sends cookie automatically
- [x] Login and signup forms — were static stubs; now real API calls via useAuth()
- [x] Signup — added username field (backend requires it); client-side validation

---

## What We Learned About the Backend (2026-05-23)

The ROADMAP's "40% done" for evaluation was misleading. Reality:
- ALL 5 pipeline steps are implemented and have logic
- The ONLY bug was `await` on sync `generate_structured_json()` → TypeError
  → always fell to fallback heuristic. Fix = `asyncio.to_thread()`.
- After fix: evaluation is effectively 95% done (all steps run LLM)

Negotiation service is fully implemented:
- Session creation, counter-offer, chat, dealer info analysis — all done
- Prompts all exist in `app/llm/prompts.py`
- Same `asyncio.to_thread()` fix applied

**What still needs attention in backend:**
- Pre-existing Pyright errors in `process_evaluation_step` (SQLAlchemy Column
  type vs PipelineStep enum mismatch — lines 405-414) — not caused by us
- AI response logging is disabled (TODO in both services) — defer to Phase 2
- Lender/insurer partners are hardcoded — defer to Phase 3

---

## Feature Status

### Backend Services
| Service | Status | Notes |
|---------|--------|-------|
| Authentication | ✅ Done | JWT, password reset, protected routes |
| Car Search | ✅ Done | MarketCheck + LLM ranking, caching |
| Deal CRUD | ✅ Done | Full lifecycle |
| Loan Calculator | ✅ Done | Amortization, APR by credit tier |
| Lender Recommendations | ✅ Done | 6 hardcoded partners, scoring |
| Insurance Recommendations | ✅ Done | 6 hardcoded partners |
| Deal Evaluation Pipeline | ✅ Fixed | asyncio.to_thread fix applied, all 5 steps run LLM |
| AI Negotiation | ✅ Fixed | asyncio.to_thread fix applied, all methods work |
| WebSocket | ✅ Done | Real-time messaging |
| Monitoring | ✅ Done | Prometheus + Grafana |

### Frontend Pages
| Page | Status | Notes |
|------|--------|-------|
| Home | 🔄 Redesign needed | Plain MUI, grey bg — needs new design |
| Auth (login/signup) | ✅ Done | Real API, cookie auth, username field |
| Search | ✅ Done | Real MarketCheck API |
| Results | ✅ Done | Real API; saves vehicle to flowState on "Evaluate deal" |
| Evaluation | ✅ Done | Real 5-step pipeline, real scores, real lenders |
| Negotiation | ✅ Done | Real session, live chat + counter/accept API |
| Summary | ✅ Done | Real session data, empty state if no negotiation |
| Deals | ✅ Done | Real API, empty state if no deals |
| Settings/Profile | ❌ New | Build from scratch |

---

## Open Decisions
- [ ] **Dark mode**: Is dark mode the primary theme? Only landing page not yet redesigned.

## Next Session Should Start With
"Phase 2: [pick one — landing page redesign / settings/profile page / real partner integrations / AI logging]"

---

## Technical Debt (known, deferred)
| Item | File | Priority |
|------|------|----------|
| AI logging disabled | `backend/app/services/deal_evaluation_service.py:225` | Medium |
| AI logging disabled | `backend/app/services/negotiation_service.py:583` | Medium |
| Hardcoded partners | `backend/app/services/lender_service.py` | Phase 3 |
| Pyright errors in process_evaluation_step | `deal_evaluation_service.py:405-414` | Low |
| flowState uses sessionStorage — cleared on tab close | `frontend/lib/flowState.ts` | Medium |
| Deals from "continue"/"evaluate" in deals page don't restore flowState vehicle | `frontend/app/deals/page.tsx` | Medium |

## Infrastructure (dev setup — 2026-05-24)
- Docker compose slimmed to postgres + redis only (removed RabbitMQ, all monitoring services)
- Native Postgres 18 was holding :5432 → stopped it, Docker postgres now owns port
- Backend runs natively: `cd backend && source venv/bin/activate && uvicorn app.main:app --reload`
- DB migration stale ref fixed: `012_add_pgvector_and_embeddings` was in alembic_version but
  file deleted → stamped to `009_add_jsonb_tables`, migrations now clean

---
*Last updated: 2026-05-24 — Wired all pages to real API; removed all mock/hardcoded data; full auth flow working; flowState bridge across search→evaluation→negotiation→summary*
