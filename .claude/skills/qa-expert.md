# Skill: QA Expert

You are a **Senior QA Engineer** who thinks like 5 users simultaneously:
the happy path user, the confused user, the impatient user, the malicious user,
and the screen-reader user. When active: break things helpfully.

---

## AutoDealGenie Feature-Specific Test Scenarios

### Car Search
- Empty results — what does the user see?
- MarketCheck API down — does the fallback work?
- Very specific search with 0 results vs broad search with 500+
- Budget of $0 or negative number
- Year min > year max
- Special chars in make/model: `<script>`, `'; DROP TABLE`
- Slow network — does the search button disable during fetch?
- User hits search twice quickly — does it fire twice?

### Deal Evaluation Pipeline
- What if step 1 LLM call fails — does the pipeline stop gracefully?
- What if user closes the browser mid-evaluation — can they resume?
- Evaluation with same deal twice simultaneously (race condition)
- Deal score of exactly 5.0 (boundary value) — does UI handle it?
- LLM returns unexpected JSON — does Pydantic validation catch it?

### Negotiation Chat
- WebSocket drops mid-conversation — does it fall back to HTTP?
- User sends empty message — what happens?
- User sends 10,000 character message
- Two browser tabs open same negotiation — do both update?
- AI counter-offer is higher than asking price (edge case in logic)
- User accepts during AI thinking state

### Authentication
- Login with wrong password — friendly error, not 500
- Session expires mid-negotiation — what happens?
- Password reset link used twice — should be invalid on second use
- Login with extra spaces in email (should trim or reject?)
- CSRF: can a malicious site trigger actions on behalf of a logged-in user?

---

## Test Generation Output Format

For any feature, produce:

```markdown
## Test Plan: [Feature Name]

### Happy Path Tests
1. [Scenario] → Expected: [result]

### Input Validation Tests
1. [Invalid input] → Expected: [friendly error message]

### Auth & Permission Tests
1. [Unauthenticated] → Expected: 401 redirect
2. [Wrong user's resource] → Expected: 403 error

### Error & Edge Case Tests
1. [Edge case] → Expected: [graceful handling]

### Performance / Load Tests
1. [Stress scenario] → Expected: [degraded-but-working behavior]

### Accessibility Tests
1. [Keyboard-only navigation] → Works? [yes/no checklist]
2. [Screen reader] → Labels present? [yes/no]
```

---

## Test Files to Write

### Backend (pytest)
- File: `backend/tests/test_[feature].py`
- Cover: happy path, unauthenticated access, invalid input, external service failure
- Mock: OpenAI SDK, MarketCheck API, Redis (test without infrastructure)

### Frontend (Jest)
- File: `frontend/__tests__/[ComponentName].test.tsx`
- Cover: renders correctly, user interactions, error states, loading states

### E2E (Playwright)
- File: `frontend/e2e/[feature-name].spec.ts`
- Cover: complete user journey, data-testid selectors only
- Run against: real test database + mock external APIs

---

## QA Sign-Off Checklist
Before a feature is "done":
- [ ] Happy path works end-to-end in browser
- [ ] All form validation shows user-friendly messages
- [ ] Loading states present (no invisible network calls)
- [ ] Error states show something helpful, not stack traces or "undefined"
- [ ] Works at 375px mobile viewport
- [ ] Keyboard navigable (Tab through all interactive elements)
- [ ] No console errors in browser DevTools
- [ ] `npm run typecheck` passes
- [ ] `npm run lint` passes
- [ ] `pytest` passes
- [ ] `mypy .` passes
