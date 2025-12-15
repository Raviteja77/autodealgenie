# AutoDealGenie Migration Roadmap
## From Prototype (CrewAI) to Production (Direct LLM API)

**Project Status**: Migration from CrewAI-based sequential agents to Direct LLM API with multi-agent loop architecture  
**Architecture Change**: Shift to parallel agents with human-in-the-loop confirmation for negotiation & deal evaluation  
**Timeline**: Progressive feature migration with integration points

---

## Executive Summary

You're migrating from:
- **Current**: CrewAI sequential multi-agent system (prototype in `autodealgenie-crewai` & `autodealgenie-NextJs`)
- **Target**: Direct LLM API calls with async state management (consolidated in `autodealgenie` monorepo)

**Key Architectural Changes**:
1. Replace CrewAI orchestration with direct OpenAI/Claude API calls
2. Implement loop-based agent execution for negotiation & evaluation (not sequential)
3. Move from prototype isolation to monorepo structure (backend/ + frontend/)
4. Establish clear API contracts between frontend and backend
5. Implement persistent state management for multi-turn interactions

---

## Phase Overview

### Phase 1: Foundation & Scaffolding (Week 1)
Backend structure, database models, Pydantic schemas

### Phase 2: LLM Integration (Week 1-2)
LLM service wrapper, prompt manager, base agent class

### Phase 3: Agent Implementation (Week 2-3)
Car recommender, price negotiator (loop), deal evaluator (loop)

### Phase 4: API Integration (Week 3-4)
FastAPI routes, session management, error handling

### Phase 5: Frontend Integration (Week 4)
API client, negotiation loop UI, evaluation loop UI

### Phase 6: Database & Persistence (Ongoing)
Schema extensions, migrations, relationships

### Phase 7: Testing & Validation (Week 5+)
Unit tests, integration tests, E2E tests

### Phase 8: Documentation & Deployment (Week 5-6)
API docs, Docker setup, CI/CD, monitoring

---

## Key Implementation Details

### Human-in-the-Loop for Negotiation
```
Agent proposes: "Counter at $26,500"
System returns: requires_human_input = true
Frontend shows: Proposal with reasoning
User decides: Confirm/Reject/Modify
System continues: Next round with user decision
```

### Human-in-the-Loop for Evaluation
```
Agent assesses: "Vehicle condition good, price fair"
Agent asks: "Any maintenance records?"
System returns: pending_questions with options
User answers: Provides information
System continues: Next round of assessment
```

### State Persistence
- Save state after every user decision
- Database is source of truth
- Resume exactly where left off
- Full conversation history maintained
- All decisions logged with reasoning

---

## Technology Requirements

**Backend**: FastAPI, SQLAlchemy, PostgreSQL, OpenAI API, Pydantic, pytest  
**Frontend**: Next.js, React, TypeScript, Tailwind CSS  
**DevOps**: Docker, PostgreSQL, Redis (optional), GitHub Actions  

---

## Success Metrics

After completion:
- ✅ 100% feature parity with prototypes
- ✅ Negotiation loop with human confirmation working
- ✅ Evaluation loop with clarifying questions working
- ✅ Session persistence across browser sessions
- ✅ >80% test coverage
- ✅ All code type-hinted and documented
- ✅ Production-ready deployment

---

## For Detailed Phase Information

See TASK_PROMPTS.md for ready-to-use AI prompts for each task.

---

**Ready to start? Begin with Phase 1, Task 1.1 in TASK_PROMPTS.md**
