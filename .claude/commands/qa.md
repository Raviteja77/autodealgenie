# /qa — Generate Tests & Test Scenarios

Load: @.claude/skills/qa-expert.md

Feature to test: $ARGUMENTS

Steps:
1. Map the feature (inputs, external systems, state changes)
2. Generate the full test scenario list (all categories from QA skill)
3. Write pytest tests → `backend/tests/test_[feature].py`
4. Write Jest tests → `frontend/__tests__/[Feature].test.tsx`
5. Write Playwright e2e → `frontend/e2e/[feature].spec.ts`
6. Run the QA sign-off checklist
