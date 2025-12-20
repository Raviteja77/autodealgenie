# Interactive Deal Evaluation Pipeline

## Overview

The Interactive Deal Evaluation Pipeline is a comprehensive, multi-step wizard that guides users through evaluating a car deal. It integrates with the backend API to provide AI-powered insights at each step of the evaluation process.

## Features

### 1. Multi-Step Wizard (5 Steps)

The evaluation is broken down into 5 distinct steps:

1. **Vehicle Condition Assessment** - Evaluates the physical condition of the vehicle
2. **Price Analysis** - Compares asking price to fair market value
3. **Financing Assessment** - Calculates monthly payments and total cost
4. **Risk Assessment** - Identifies potential risk factors
5. **Final Recommendation** - Provides comprehensive evaluation report

### 2. Dynamic Progress Tracking

- Visual progress indicator shows current step and completed steps
- Users can see their progress through the evaluation at a glance
- Step icons change based on completion status

### 3. Real-Time Score Display

- Overall deal score calculated from all evaluation criteria
- Score breakdown by category (Condition, Price, Risk)
- Color-coded scoring (green for good, yellow for fair, red for poor)
- Score updates as evaluation progresses

### 4. AI-Powered Insights

- Each step generates contextual insights based on the data
- Insights are displayed in an easy-to-read format
- Warnings and recommendations highlighted appropriately

### 5. Interactive Question Forms

- System asks for missing information when needed
- Smart question types (text, radio, number) based on context
- Field validation with error messages
- Option to skip optional questions

### 6. Comprehensive Final Report

The final step provides:
- Executive summary with overall recommendation
- Detailed score breakdown
- Interactive action items checklist
- Export options (PDF, Email, Share - placeholders)

## Component Architecture

### Main Page Component

**Location**: `frontend/app/dashboard/evaluation/page.tsx`

The main evaluation page handles:
- State management for the evaluation flow
- API integration for starting and continuing evaluations
- Dynamic step rendering based on backend response
- Navigation between steps

### UI Components

**Location**: `frontend/app/dashboard/evaluation/components/`

#### Core Components

1. **ProgressIndicator.tsx** - Displays step progress with icons
2. **ScoreCard.tsx** - Shows overall score and breakdown
3. **InsightsPanel.tsx** - Displays AI-generated insights
4. **QuestionForm.tsx** - Reusable form for user input

#### Step Components

**Location**: `frontend/app/dashboard/evaluation/components/steps/`

1. **ConditionStep.tsx** - Shows vehicle condition assessment
2. **PriceStep.tsx** - Displays price analysis and talking points
3. **FinancingStep.tsx** - Shows payment calculator results
4. **RiskStep.tsx** - Displays risk factors and recommendations
5. **FinalStep.tsx** - Comprehensive final report with export options

## API Integration

### Endpoints Used

1. **POST `/api/v1/deals/{deal_id}/evaluation`**
   - Starts a new evaluation or continues existing one
   - Body: `{ answers?: Record<string, string | number> }`
   - Returns: Evaluation state with step result

2. **GET `/api/v1/deals/{deal_id}/evaluation/{evaluation_id}`**
   - Gets current evaluation status
   - Returns: Full evaluation object

3. **POST `/api/v1/deals/{deal_id}/evaluation/{evaluation_id}/answers`**
   - Submits answers to evaluation questions
   - Body: `{ answers: Record<string, string | number> }`
   - Returns: Updated evaluation state

### API Client Extension

**Location**: `frontend/lib/api.ts`

Added types and methods:
- `EvaluationStatus`, `PipelineStep` types
- `EvaluationResponse`, `EvaluationStepResult` interfaces
- `startEvaluation()`, `getEvaluation()`, `submitEvaluationAnswers()` methods

## Mock Services

For development without the backend, mock evaluation endpoints are available:

**Location**: `backend/app/api/mock/mock_services.py`

### Mock Endpoints

- **POST `/mock/evaluation/pipeline/{deal_id}/evaluation`**
- **POST `/mock/evaluation/pipeline/{deal_id}/evaluation/{evaluation_id}/answers`**
- **GET `/mock/evaluation/pipeline/{deal_id}/evaluation/{evaluation_id}`**

### Using Mock Mode

Set environment variable in `frontend/.env.local`:

```env
NEXT_PUBLIC_USE_MOCK=true
```

The API client will automatically route requests to mock endpoints.

## State Flow

```
Start Evaluation
    ↓
Vehicle Condition
    ↓ (if data missing)
Ask Questions → Submit Answers
    ↓ (if data complete)
Show Assessment → Continue
    ↓
Price Analysis
    ↓
Show Analysis → Continue
    ↓
Financing
    ↓ (if financing type missing)
Ask Questions → Submit Answers
    ↓ (if complete)
Show Calculator → Continue
    ↓
Risk Assessment
    ↓
Show Risks → Continue
    ↓
Final Recommendation
    ↓
Complete (Accept/Reject Deal)
```

## Evaluation Flow

### Question/Answer Pattern

When the backend needs information:
1. API returns `status: "awaiting_input"` with questions
2. Frontend displays `QuestionForm` component
3. User submits answers
4. Answers sent to `/answers` endpoint
5. Backend processes and either:
   - Returns more questions, or
   - Returns assessment and moves to next step

### Step Progression

When a step is complete:
1. Assessment data is stored in `result_json`
2. Backend automatically advances to next step
3. Frontend updates progress indicator
4. Next step content is rendered
5. "Continue" button advances when ready

## Styling

All components use Material-UI with the application theme:
- Consistent spacing and typography
- Responsive design for mobile/desktop
- Color-coded status indicators
- Smooth transitions between steps

## Error Handling

The implementation includes comprehensive error handling:
- Network errors show retry option
- Invalid data shows clear error messages
- Missing vehicle data redirects to search
- API errors display user-friendly messages

## Future Enhancements

Potential improvements:
1. **Real PDF Export** - Generate downloadable PDF reports
2. **Email Integration** - Send reports via email
3. **Social Sharing** - Share evaluations with family/advisors
4. **Comparison Mode** - Compare multiple evaluations side-by-side
5. **Save Drafts** - Resume incomplete evaluations later
6. **Historical Tracking** - View past evaluations
7. **Animations** - Add score counter animations and confetti
8. **Detailed Charts** - Visualize scores with charts
9. **Print Optimization** - Better print layout for reports
10. **Mobile App** - Native mobile experience

## Testing

### Manual Testing Steps

1. Navigate to evaluation page with vehicle parameters
2. Verify progress indicator displays correctly
3. Answer any questions presented
4. Verify scores update after each step
5. Check insights panel shows relevant information
6. Complete all steps to final report
7. Verify action items checklist works
8. Test back navigation
9. Test error handling (invalid input, network errors)
10. Test on mobile devices

### Integration Testing

To test with the backend:
1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Navigate to evaluation page
4. Verify API calls succeed
5. Complete full evaluation flow

To test with mocks:
1. Set `NEXT_PUBLIC_USE_MOCK=true` in `frontend/.env.local`
2. Start frontend: `npm run dev`
3. Mock endpoints will be used automatically

## Deployment

No special deployment steps required. The evaluation pipeline is part of the main application:

1. Build frontend: `cd frontend && npm run build`
2. Deploy as usual

Ensure backend environment variables are set:
- Database connection for storing evaluations
- OpenAI API key for AI-powered insights (optional, falls back to heuristics)

## Related Documentation

- [DEAL_EVALUATION_SUMMARY.md](../DEAL_EVALUATION_SUMMARY.md) - Backend evaluation pipeline
- [UI_COMPONENTS.md](../UI_COMPONENTS.md) - UI component library
- [AUTHENTICATION.md](../AUTHENTICATION.md) - Authentication system

## Support

For issues or questions:
1. Check existing GitHub issues
2. Review backend logs for API errors
3. Check browser console for frontend errors
4. Ensure mock mode is configured correctly if testing without backend
