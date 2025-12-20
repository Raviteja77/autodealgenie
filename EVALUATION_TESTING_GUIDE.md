# Evaluation Pipeline Testing Guide

## Pre-Testing Setup

### Backend Setup (Real API)

1. Start the backend server:
```bash
cd backend
uvicorn app.main:app --reload
```

2. Apply database migrations:
```bash
cd backend
alembic upgrade head
```

3. Verify backend is running:
```bash
curl http://localhost:8000/api/v1/health
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Configure environment (choose one):

**Option A: Real Backend**
```env
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_USE_MOCK=false
```

**Option B: Mock Services**
```env
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_USE_MOCK=true
```

3. Start frontend dev server:
```bash
cd frontend
npm run dev
```

4. Open browser to: http://localhost:3000

## Test Scenarios

### Scenario 1: Complete Evaluation Flow (Happy Path)

**Steps:**
1. Navigate to search page
2. Perform a car search
3. Select a vehicle from results
4. Click "Evaluate Deal" button
5. Observe evaluation page loads

**Expected Results:**
- Progress indicator shows 5 steps
- Current step is highlighted (Vehicle Condition)
- Score card displays with overall score
- Either questions are shown OR condition assessment is displayed
- Loading states work correctly
- No console errors

**Verification Points:**
- [ ] Progress indicator renders correctly
- [ ] Score card shows overall score (if available)
- [ ] Step content renders (questions or assessment)
- [ ] Insights panel shows relevant information
- [ ] "Continue" or "Submit" button is visible
- [ ] Loading spinner shows during API calls

### Scenario 2: Question/Answer Flow

**Steps:**
1. Start evaluation (as above)
2. If questions are presented, fill out the form
3. Submit answers
4. Wait for next step

**Expected Results:**
- Questions render with appropriate input types
- Validation works (required fields)
- Submit button is disabled while loading
- Success: Advances to next step
- Error: Shows error message with retry option

**Verification Points:**
- [ ] Text inputs work correctly
- [ ] Radio buttons work correctly
- [ ] Number inputs work correctly
- [ ] Validation prevents empty required fields
- [ ] Error messages display clearly
- [ ] Loading state during submission
- [ ] Successful submission advances step

### Scenario 3: Multi-Step Progression

**Steps:**
1. Complete Vehicle Condition step
2. Click "Continue to Next Step"
3. Review Price Analysis
4. Click "Continue to Next Step"
5. Answer Financing questions (if asked)
6. Click "Continue to Next Step"
7. Review Risk Assessment
8. Click "Continue to Next Step"
9. Review Final Recommendation

**Expected Results:**
- Each step displays unique content
- Progress indicator updates as steps complete
- Score card updates with new scores
- Insights change based on step
- Navigation works smoothly

**Verification Points:**
- [ ] Vehicle Condition shows condition score and notes
- [ ] Price Analysis shows fair value and talking points
- [ ] Financing shows payment calculator
- [ ] Risk Assessment shows risk factors
- [ ] Final Report shows comprehensive summary
- [ ] Progress indicator marks completed steps
- [ ] Scores update appropriately

### Scenario 4: Score Display

**Steps:**
1. Complete evaluation to Final Report
2. Observe score breakdown

**Expected Results:**
- Overall score displays prominently
- Score breakdown shows all categories
- Color coding matches score level
- Progress bars fill correctly

**Verification Points:**
- [ ] Overall score is visible (0-10 scale)
- [ ] Condition score displays
- [ ] Price score displays
- [ ] Risk score displays (lower is better noted)
- [ ] Color coding: Green (8+), Yellow (6-8), Red (<6)
- [ ] Progress bars animate/fill correctly

### Scenario 5: Final Report Actions

**Steps:**
1. Complete evaluation to Final Report
2. Check action items checkboxes
3. Try export buttons (PDF, Email, Share)

**Expected Results:**
- Action items are interactive
- Checkboxes work and strike through completed items
- Export buttons show "coming soon" alerts
- Final recommendation displays clearly

**Verification Points:**
- [ ] Action items checklist works
- [ ] Checkboxes toggle correctly
- [ ] Completed items strike through
- [ ] Export buttons are clickable
- [ ] Recommendation text is clear
- [ ] Overall score matches calculation

### Scenario 6: Error Handling

**Steps:**
1. Start evaluation
2. Simulate network error (disconnect internet or stop backend)
3. Try to submit answers or continue

**Expected Results:**
- Error message displays clearly
- Retry button is available
- User can recover from error

**Verification Points:**
- [ ] Network errors show user-friendly message
- [ ] Retry button works
- [ ] Error doesn't crash the page
- [ ] Previous data is preserved

### Scenario 7: Navigation

**Steps:**
1. Start evaluation
2. Click "Go Back" button
3. Return to evaluation
4. Verify state is preserved

**Expected Results:**
- Back button works
- State is maintained (if implemented)
- Can resume evaluation

**Verification Points:**
- [ ] Back button navigates correctly
- [ ] Browser back button works
- [ ] State persists (or restarts cleanly)

### Scenario 8: Mobile Responsiveness

**Steps:**
1. Open evaluation page on mobile device or use browser dev tools
2. Test all steps on mobile viewport

**Expected Results:**
- Layout adapts to mobile screen
- All elements are accessible
- Touch interactions work
- Text is readable

**Verification Points:**
- [ ] Progress indicator works on mobile
- [ ] Score card is readable
- [ ] Forms work with touch
- [ ] Buttons are tap-friendly
- [ ] No horizontal scroll
- [ ] Text size is appropriate

## API Testing

### Test Mock Endpoints

With `NEXT_PUBLIC_USE_MOCK=true`:

**Test 1: Start Evaluation**
```bash
curl -X POST http://localhost:8000/mock/evaluation/pipeline/1/evaluation \
  -H "Content-Type: application/json" \
  -d '{"answers": null}'
```

Expected: Returns evaluation with questions or initial assessment

**Test 2: Submit Answers**
```bash
curl -X POST http://localhost:8000/mock/evaluation/pipeline/1/evaluation/5001/answers \
  -H "Content-Type: application/json" \
  -d '{"answers": {"vin": "123ABC", "condition_description": "good"}}'
```

Expected: Returns updated evaluation with next step

**Test 3: Get Evaluation Status**
```bash
curl http://localhost:8000/mock/evaluation/pipeline/1/evaluation/5001
```

Expected: Returns current evaluation state

### Test Real Endpoints

With backend running and `NEXT_PUBLIC_USE_MOCK=false`:

**Test 1: Start Evaluation (requires auth)**
```bash
curl -X POST http://localhost:8000/api/v1/deals/1/evaluation \
  -H "Content-Type: application/json" \
  -H "Cookie: auth_token=YOUR_TOKEN" \
  -d '{"answers": null}'
```

**Test 2: Submit Answers (requires auth)**
```bash
curl -X POST http://localhost:8000/api/v1/deals/1/evaluation/1/answers \
  -H "Content-Type: application/json" \
  -H "Cookie: auth_token=YOUR_TOKEN" \
  -d '{"answers": {"vin": "123ABC", "condition_description": "good"}}'
```

## Common Issues & Solutions

### Issue: "Failed to start evaluation"
**Solution:** 
- Check backend is running
- Verify API URL in .env.local
- Check browser console for details
- Try mock mode first

### Issue: "Questions not rendering"
**Solution:**
- Check step_result in API response
- Verify QuestionForm component receives questions
- Check console for React errors

### Issue: "Scores not updating"
**Solution:**
- Verify result_json structure in API response
- Check getScores() function logic
- Ensure step assessments include score fields

### Issue: "Progress indicator not updating"
**Solution:**
- Verify completedSteps array is updating
- Check updateEvaluationState() function
- Ensure backend returns completed flags

### Issue: "Mock endpoints not working"
**Solution:**
- Verify NEXT_PUBLIC_USE_MOCK=true
- Check backend has USE_MOCK_SERVICES=true
- Restart both frontend and backend
- Check endpoint mapping in api.ts

## Performance Testing

**Metrics to Check:**
- [ ] Initial page load < 2 seconds
- [ ] API responses < 500ms (mock), < 2s (real with LLM)
- [ ] Step transitions smooth (no lag)
- [ ] Score animations perform well
- [ ] No memory leaks during multiple evaluations

## Accessibility Testing

**Checks:**
- [ ] Keyboard navigation works
- [ ] Screen reader announces steps
- [ ] Focus indicators visible
- [ ] Color contrast sufficient
- [ ] Form labels associated correctly
- [ ] Error messages announced

## Browser Compatibility

Test in:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS)
- [ ] Mobile Chrome (Android)

## Success Criteria

All scenarios pass:
- ✅ Complete evaluation flow works end-to-end
- ✅ All 5 steps render correctly
- ✅ Questions and answers work
- ✅ Scores calculate and display correctly
- ✅ Insights show relevant information
- ✅ Final report is comprehensive
- ✅ Error handling works
- ✅ Mobile responsive
- ✅ No console errors
- ✅ Performance is acceptable

## Reporting Issues

When reporting issues, include:
1. Steps to reproduce
2. Expected behavior
3. Actual behavior
4. Browser and version
5. Console errors (if any)
6. Network tab (API calls)
7. Screenshots or video

## Next Steps After Testing

Once testing is complete:
1. Document any bugs found
2. Create GitHub issues for bugs
3. Screenshot working features
4. Update PR with test results
5. Request code review
