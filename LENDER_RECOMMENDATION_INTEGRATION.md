# Lender Recommendation Integration

This document describes the lender recommendation feature integration across the AutoDealGenie application, connecting financing options to the vehicle search, negotiation, and evaluation workflows.

## Overview

The lender recommendation system provides personalized financing options throughout the car-buying journey by:

1. **Curating Partner Lenders**: Managing a database of trusted partner lenders with detailed eligibility criteria
2. **Smart Matching**: Scoring and ranking lenders based on user credit profile, loan amount, and term preferences
3. **AI Integration**: Enhancing AI agents with lender data to provide context-aware financing advice
4. **Seamless UI**: Displaying lender recommendations at key decision points in the user journey

## Architecture

### Backend Components

#### 1. Lender Service (`app/services/lender_service.py`)

**Purpose**: Core business logic for lender matching and scoring

**Key Features**:
- Partner lender database with 6 curated lenders
- Multi-factor scoring algorithm (APR competitiveness, loan fit, credit fit, term flexibility, features)
- Credit score range mapping (excellent, good, fair, poor)
- Eligibility filtering by credit score, loan amount, and term

**Key Methods**:
```python
LenderService.filter_lenders(loan_amount, credit_score_range, loan_term_months)
LenderService.score_lenders(lenders, loan_amount, credit_score_range, loan_term_months)
LenderService.get_recommendations(request, max_results=5)
```

**Scoring Algorithm**:
- **APR Competitiveness** (40% weight): Lower APR = higher score
- **Loan Amount Fit** (20% weight): Prefers lenders where loan is mid-range
- **Credit Score Fit** (20% weight): Prefers lenders where credit is mid-to-upper range
- **Term Flexibility** (10% weight): Rewards wider term ranges
- **Features & Benefits** (10% weight): Rewards comprehensive offerings

#### 2. API Endpoints

##### `/api/v1/loans/lenders` (POST)
**Purpose**: Get personalized lender recommendations

**Request Body**:
```json
{
  "loan_amount": 25000.0,
  "credit_score_range": "good",
  "loan_term_months": 60
}
```

**Response**:
```json
{
  "recommendations": [
    {
      "lender": {
        "lender_id": "capital_auto_finance",
        "name": "Capital Auto Finance",
        "description": "...",
        "min_credit_score": 680,
        "apr_range_min": 0.039,
        "apr_range_max": 0.079,
        "features": ["Pre-approval in minutes", "No prepayment penalties"],
        "benefits": ["Same-day funding", "Rate discounts for autopay"],
        "affiliate_url": "https://capitalautofin.com/apply",
        "referral_code": "ADG_CAF_001"
      },
      "match_score": 87.5,
      "estimated_apr": 0.0495,
      "estimated_monthly_payment": 469.82,
      "recommendation_reason": "Excellent rates • Strong credit profile for this lender",
      "rank": 1
    }
  ],
  "total_matches": 4,
  "request_summary": {
    "loan_amount": 25000.0,
    "credit_score_range": "good",
    "loan_term_months": 60
  }
}
```

##### `/api/v1/negotiations/{session_id}/lender-recommendations` (GET)
**Purpose**: Get lender recommendations for a completed negotiation

**Query Parameters**:
- `loan_term_months` (optional, default: 60)
- `credit_score_range` (optional, default: "good")

**Response**: Same as `/api/v1/loans/lenders`

#### 3. AI Agent Enhancements (`app/llm/agent_system_prompts.py`)

**Loan Agent**:
- Analyzes lender match scores, APR ranges, and features
- Explains how each lender aligns with customer profile
- Recommends best overall value considering APR, flexibility, and benefits
- Highlights strengths and trade-offs of top-ranked lenders

**Negotiation Agent**:
- Uses pre-approved financing as leverage
- Guides buyers to mention competitive lender APRs to dealers
- Factors total cost (vehicle + financing) into counter-offers
- Highlights when lender benefits add negotiation value

**Evaluator Agent**:
- Calculates total costs across different lenders
- Evaluates APR competitiveness and terms
- Assesses lender features' impact on long-term value
- Compares cash payment vs. top financing options
- Identifies concerning lender terms or fees

### Frontend Components

#### 1. LenderRecommendations Component (`components/LenderRecommendations.tsx`)

**Purpose**: Reusable component for displaying lender recommendations

**Features**:
- Responsive Material-UI cards with lender details
- Sort by: match score, APR, payment, or term
- Expandable sections for features, benefits, and loan details
- Apply now buttons with affiliate tracking
- Loan term selector to refresh recommendations
- Top match highlighting with badge

**Props**:
```typescript
interface LenderRecommendationsProps {
  loanAmount: number;
  creditScore: "excellent" | "good" | "fair" | "poor";
  loanTermMonths?: number;
  onLenderSelect?: (lender: LenderMatch) => void;
  showApplyButton?: boolean;
  compact?: boolean;
}
```

**Usage Example**:
```tsx
<LenderRecommendations
  loanAmount={25000}
  creditScore="good"
  loanTermMonths={60}
  onLenderSelect={(lender) => console.log("Selected:", lender)}
  showApplyButton={true}
/>
```

#### 2. Results Page Integration (`app/dashboard/results/page.tsx`)

**When Displayed**: When `paymentMethod === "finance"` and `loanAmount > 0`

**Location**: Between "Applied Filters" and "Results Grid" sections

**Data Flow**:
1. Extract financing parameters from search URL params
2. Calculate loan amount (budgetMax - downPayment)
3. Get credit score and loan term from params
4. Pass to `LenderRecommendations` component
5. Display recommendations with vehicle results

**User Benefits**:
- See financing options alongside vehicle search results
- Compare vehicles and lenders in one view
- Make informed decisions about both vehicle and financing

#### 3. Negotiation Page Integration (`app/dashboard/negotiation/page.tsx`)

**When Displayed**: After successfully accepting a negotiated offer

**Location**: In the "Congratulations" modal after deal completion

**Data Flow**:
1. On offer acceptance, trigger lender API call
2. Use negotiated price as loan amount
3. Get financing options (default term: 60 months, credit: "good")
4. Display top 3 lender matches
5. Show estimated payment and APR for each

**UI Features**:
- Compact view showing top 3 lenders
- Best match highlighted with badge
- Direct "Apply Now" buttons
- Seamless transition to deal evaluation

## User Journey

### 1. Search Phase
**Page**: `/dashboard/search`

**User Action**: Selects "Finance" payment method and enters:
- Budget range (e.g., $20,000 - $30,000)
- Down payment (e.g., $5,000)
- Loan term (e.g., 60 months)
- Credit score (e.g., "good")

**System**: Stores financing criteria in search params

### 2. Results Phase
**Page**: `/dashboard/results`

**System Behavior**:
1. Detects financing mode from URL params
2. Calculates loan amount: `budgetMax - downPayment`
3. Fetches lender recommendations via API
4. Displays `LenderRecommendations` component above vehicle results

**User Experience**:
- Sees both vehicle options and financing options
- Can sort/filter lenders by different criteria
- Can expand lenders to see full details
- Can apply directly via affiliate links

### 3. Negotiation Phase
**Page**: `/dashboard/negotiation`

**AI Agent Behavior**:
- Suggests using pre-approved financing as leverage
- Recommends mentioning competitive APRs to dealer
- Factors financing into total deal cost advice

**User Experience**:
- Receives AI guidance on financing leverage
- Negotiates vehicle price with financing confidence

### 4. Deal Acceptance
**Page**: `/dashboard/negotiation` (completion modal)

**System Behavior**:
1. User accepts final negotiated price
2. System triggers lender recommendation API
3. Displays top 3 lenders with estimated payments
4. Shows total savings and financing options

**User Experience**:
- Immediate access to financing options
- Can apply with lenders directly
- Clear path to complete purchase

### 5. Evaluation Phase
**Page**: `/dashboard/evaluation`

**AI Agent Behavior**:
- Compares total cost across lenders
- Evaluates APR competitiveness
- Identifies best overall deal (vehicle + financing)

**User Experience**:
- Comprehensive deal analysis including financing
- Clear recommendation on best lender choice

## Testing

### Backend Tests

**File**: `backend/tests/llm/test_agent_system_prompts.py`

**Coverage**:
- ✅ All agent roles have prompts
- ✅ Loan agent includes lender guidance
- ✅ Negotiation agent includes financing leverage
- ✅ Evaluator agent includes lender comparison
- ✅ JSON output format handling
- ✅ Unknown role fallback
- ✅ Agent personality preservation
- ✅ Prompt structure and comprehensiveness

**Run Tests**:
```bash
cd backend
pytest tests/llm/test_agent_system_prompts.py -v
```

### Manual Testing Checklist

#### Results Page
- [ ] Lender section appears when financing selected
- [ ] Lenders load correctly with valid parameters
- [ ] Sort dropdown changes lender order
- [ ] Term selector refreshes recommendations
- [ ] Expand/collapse works for lender details
- [ ] Apply now buttons open affiliate URLs
- [ ] No lenders shown when paymentMethod is "cash"

#### Negotiation Page
- [ ] Lenders appear after accepting offer
- [ ] Top 3 lenders displayed with correct data
- [ ] APRs and payments calculated correctly
- [ ] Apply now buttons work
- [ ] Loading state shows while fetching lenders

#### API Integration
- [ ] `/api/v1/loans/lenders` returns valid data
- [ ] Match scores calculated correctly
- [ ] Lenders filtered by eligibility criteria
- [ ] Estimated APR and payment calculated correctly
- [ ] Error handling for invalid parameters

## Configuration

### Partner Lenders

**Location**: `backend/app/services/lender_service.py` → `PARTNER_LENDERS`

**Adding a New Lender**:
```python
LenderInfo(
    lender_id="unique_id",
    name="Lender Name",
    description="Brief description of lender",
    logo_url="https://cdn.autodealgenie.com/lenders/logo.png",
    min_credit_score=640,
    max_credit_score=850,
    min_loan_amount=5000.0,
    max_loan_amount=75000.0,
    min_term_months=24,
    max_term_months=84,
    apr_range_min=0.049,  # 4.9%
    apr_range_max=0.119,  # 11.9%
    features=["Feature 1", "Feature 2", "Feature 3"],
    benefits=["Benefit 1", "Benefit 2", "Benefit 3"],
    affiliate_url="https://lender.com/apply",
    referral_code="ADG_LDR_###",
)
```

### Scoring Algorithm Constants

**Location**: `backend/app/services/lender_service.py`

**Adjustable Parameters**:
```python
# Scoring weights (must sum to 100)
WEIGHT_APR_COMPETITIVENESS = 40  # Emphasis on competitive rates
WEIGHT_LOAN_AMOUNT_FIT = 20      # How well loan fits lender range
WEIGHT_CREDIT_SCORE_FIT = 20     # How well credit fits lender range
WEIGHT_TERM_FLEXIBILITY = 10     # Reward flexible terms
WEIGHT_FEATURES_BENEFITS = 10    # Reward comprehensive offerings

# Special bonuses
BONUS_CREDIT_REBUILDING_SPECIALIST = 5  # For credit rebuilding lenders
```

## Future Enhancements

### Phase 1 (Current Implementation)
- ✅ Lender recommendation engine
- ✅ API endpoints for lender data
- ✅ AI agent integration
- ✅ Results page display
- ✅ Negotiation page display

### Phase 2 (Planned)
- [ ] Real-time rate integration (replace static APR ranges)
- [ ] Lender pre-qualification API integration
- [ ] Save favorite lenders to user profile
- [ ] Compare lenders side-by-side in modal
- [ ] Email lender comparisons to user

### Phase 3 (Future)
- [ ] Track application conversions
- [ ] A/B test lender display strategies
- [ ] Personalized lender recommendations based on past behavior
- [ ] Integration with dealer financing offers
- [ ] Refinancing recommendations for existing loans

## Troubleshooting

### Issue: No lenders displayed
**Possible Causes**:
- `paymentMethod` not set to "finance"
- `loanAmount` is 0 or negative
- No lenders match user criteria

**Solution**:
- Check URL params: `budgetMax`, `downPayment`, `creditScore`, `loanTerm`
- Verify lenders in `PARTNER_LENDERS` match user criteria
- Check browser console for API errors

### Issue: Incorrect APR calculations
**Possible Causes**:
- Credit score mapping incorrect
- APR range not properly interpolated

**Solution**:
- Verify `CREDIT_SCORE_RANGES` in `lender_service.py`
- Check APR calculation logic in `get_recommendations()`

### Issue: Lenders not sorted correctly
**Possible Causes**:
- Sort logic not applied
- Sort option state not updating

**Solution**:
- Check `sortedLenders` logic in `LenderRecommendations.tsx`
- Verify `handleSortChange` updates state correctly

## API Reference Summary

### POST /api/v1/loans/lenders
**Auth**: Required  
**Body**: `LenderRecommendationRequest`  
**Response**: `LenderRecommendationResponse` (up to 5 lenders)

### GET /api/v1/negotiations/{session_id}/lender-recommendations
**Auth**: Required  
**Params**: `loan_term_months`, `credit_score_range`  
**Response**: `LenderRecommendationResponse` (up to 5 lenders)

## Key Files

**Backend**:
- `app/services/lender_service.py` - Lender matching logic
- `app/llm/agent_system_prompts.py` - AI agent prompts
- `app/api/v1/endpoints/loans.py` - Lender API endpoint
- `app/api/v1/endpoints/negotiation.py` - Negotiation lender endpoint
- `app/schemas/loan_schemas.py` - Lender data schemas
- `tests/llm/test_agent_system_prompts.py` - Agent prompt tests

**Frontend**:
- `components/LenderRecommendations.tsx` - Lender display component
- `app/dashboard/results/page.tsx` - Results page integration
- `app/dashboard/negotiation/page.tsx` - Negotiation page (already had lenders)
- `lib/api.ts` - API client with lender types

## Conclusion

The lender recommendation integration provides a seamless financing experience throughout the car-buying journey. By combining smart matching algorithms, AI-powered guidance, and intuitive UI, users can make informed decisions about both vehicle selection and financing options.

The system is designed to be:
- **Extensible**: Easy to add new lenders and update scoring criteria
- **Performant**: Efficient filtering and scoring for fast recommendations
- **User-Friendly**: Clear presentation of complex financial information
- **Privacy-Focused**: Affiliate tracking without collecting user PII
- **AI-Enhanced**: Contextual financing advice from specialized agents
