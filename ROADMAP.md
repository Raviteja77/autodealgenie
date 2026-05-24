# AutoDealGenie — Strategic Roadmap

> **Purpose**: This document lays out the strategic plan to take AutoDealGenie from MVP to a market-ready product. Each section contains prioritized tasks with AI-promptable descriptions that can be given directly to an AI assistant for implementation.

---

## Table of Contents

1. [Vision & Market Position](#1-vision--market-position)
2. [Implementation Status Summary](#2-implementation-status-summary)
3. [Phase 1 — Fix Critical Gaps (Must Do First)](#3-phase-1--fix-critical-gaps)
4. [Phase 2 — Polish Core Experience](#4-phase-2--polish-core-experience)
5. [Phase 3 — Finance & Insurance Partner Ecosystem](#5-phase-3--finance--insurance-partner-ecosystem)
6. [Phase 4 — Differentiation Features](#6-phase-4--differentiation-features)
7. [Phase 5 — Scale & Monetize](#7-phase-5--scale--monetize)
8. [Technical Debt](#8-technical-debt)
9. [AI Task Prompts](#9-ai-task-prompts)

---

## 1. Vision & Market Position

### What Makes AutoDealGenie Different

Most car-buying tools help users *find* cars. AutoDealGenie goes further by:

1. **AI Negotiation Coach** — No other platform provides real-time AI-powered negotiation practice and strategy with counter-offer generation.
2. **End-to-End Deal Intelligence** — From search through financing, everything is scored and ranked by AI.
3. **Partner Ecosystem** — Lender and insurance recommendations embedded in the deal flow, not as separate products.
4. **Transparency** — Deal scores, fair market values, and AI reasoning are shown, not hidden.

### Target Users
- **Primary**: First-time car buyers who feel overwhelmed by the process.
- **Secondary**: Experienced buyers who want data-backed confidence.
- **Tertiary**: Car enthusiasts who want to track deals and compare options.

### Market Differentiation Strategy

```
Traditional Sites       AutoDealGenie            Future Vision
(Cars.com, AutoTrader)  (Current)                (Target)
─────────────────────   ─────────────────────    ─────────────────────
Search listings     →   AI-ranked results     →  Proactive alerts
Compare prices      →   Fair market scoring   →  Price prediction
Contact dealer      →   AI negotiation coach  →  Auto-negotiation bot
Find financing      →   Partner lender recs   →  Pre-approved offers
Buy insurance       →   Partner insurer recs  →  Bundled deal packages
```

---

## 2. Implementation Status Summary

### Backend Services

| Service | Status | Completeness | Notes |
|---------|--------|-------------|-------|
| Authentication | ✅ Complete | 100% | JWT, password reset, protected routes |
| Car Search/Recommendations | ✅ Complete | 95% | MarketCheck + LLM ranking, caching |
| Deal CRUD | ✅ Complete | 100% | Full lifecycle management |
| Loan Calculator | ✅ Complete | 100% | Amortization, APR by credit tier |
| Lender Recommendations | ✅ Complete | 90% | 6 hardcoded partners, scoring algorithm |
| Insurance Recommendations | ✅ Complete | 90% | 6 hardcoded partners, premium calculation |
| Deal Evaluation Pipeline | ⚠️ Partial | 40% | Framework exists, step methods incomplete |
| Negotiation Service | ⚠️ Partial | 60% | Session management done, AI generation stubs |
| WebSocket Manager | ✅ Complete | 90% | Real-time messaging works |
| Monitoring | ✅ Complete | 100% | Prometheus + Grafana + Alertmanager |

### Frontend Pages

| Page | Status | Completeness | Notes |
|------|--------|-------------|-------|
| Home | ✅ Complete | 100% | Hero, stats, quick actions |
| Auth (Login/Signup/Reset) | ✅ Complete | 100% | Full flow with validation |
| Search | ✅ Complete | 95% | Filters, financing, validation |
| Results | ✅ Complete | 90% | Cards, comparison, favorites, lender recs |
| Negotiation | ✅ Complete | 85% | WebSocket chat, HTTP fallback |
| Evaluation | ✅ Complete | 80% | Score display, insights, insurance recs |
| Deals | ✅ Complete | 90% | List, status, basic management |
| Favorites | ✅ Complete | 90% | Save, remove, quick actions |

---

## 3. Phase 1 — Fix Critical Gaps

> **Priority**: HIGH — These block the core user experience.

### 3.1 Complete the Deal Evaluation Pipeline

**What**: The evaluation service has a 5-step pipeline framework, but the inner step methods (`_evaluate_price`, `_evaluate_financing`, `_evaluate_risk`, `_evaluate_final`) are incomplete.

**Why**: Users see a placeholder or error when trying to evaluate deals beyond the first step.

**Files to modify**:
- `backend/app/services/deal_evaluation_service.py`
- `backend/app/llm/prompts.py` (add prompts for each step)
- `backend/app/llm/schemas.py` (add response schemas for each step)
- `backend/tests/test_deal_evaluation.py`

**AI Task Prompt**:
```
Context: See ARCHITECTURE.md and PROJECT_GUIDE.md for project context.

Task: Complete the deal evaluation pipeline in backend/app/services/deal_evaluation_service.py.

The service has a 5-step pipeline: VEHICLE_CONDITION → PRICE → FINANCING → RISK → FINAL.
Step 1 (VEHICLE_CONDITION) is partially implemented. Steps 2-5 need full implementation.

For each step:
1. Add a prompt template in app/llm/prompts.py
2. Add a Pydantic response schema in app/llm/schemas.py
3. Implement the _evaluate_* method in deal_evaluation_service.py
4. Each method should call generate_structured_json with the appropriate prompt
5. Handle errors gracefully with fallback scoring

Step details:
- PRICE: Compare asking price to fair market value using vehicle make/model/year/mileage
- FINANCING: Evaluate the financing terms (rate, down payment, loan term)
- RISK: Assess risk factors (vehicle age, mileage, market trends)
- FINAL: Aggregate all step scores into overall deal score (1-10)

Also fix: line ~472 has generate_structured_json() not awaited (missing await).

Write pytest tests following the pattern in tests/test_deal_evaluation.py.
Follow coding conventions in ARCHITECTURE.md Section 6.
```

### 3.2 Complete the AI Negotiation Agent

**What**: The negotiation service has session management but the AI response generation methods are stubs.

**Why**: Users can start a negotiation but the AI can't generate counter-offers or analyze dealer quotes.

**Files to modify**:
- `backend/app/services/negotiation_service.py`
- `backend/app/llm/prompts.py` (add negotiation prompts)
- `backend/app/llm/schemas.py` (add negotiation response schemas)
- `backend/tests/test_negotiation.py`

**AI Task Prompt**:
```
Context: See ARCHITECTURE.md and PROJECT_GUIDE.md for project context.

Task: Complete the AI negotiation agent in backend/app/services/negotiation_service.py.

The service manages negotiation sessions with multi-round support. These methods need implementation:

1. _generate_agent_response(session, user_message) → str
   - Use the Negotiation Agent role from app/llm/llm_client.py
   - Generate a response considering: current offer, fair market value, round number
   - Include talking points and suggested counter-offer

2. _generate_counter_response(session, user_action, amount) → str
   - Generate AI response to user's counter-offer
   - Consider negotiation strategy (start high, concede gradually)
   - Include reasoning for the counter-offer

3. send_chat_message(session_id, message, db) → Message
   - Process free-form user messages in negotiation
   - Call _generate_agent_response for AI reply
   - Persist both messages to database
   - Broadcast via WebSocket if connected

4. analyze_dealer_info(session_id, dealer_data, db) → Analysis
   - Parse dealer quote/offer information
   - Compare to fair market value
   - Generate insights and recommended response

Add prompts in app/llm/prompts.py for each method.
Add response schemas in app/llm/schemas.py.
Write pytest tests following existing patterns.
```

### 3.3 Re-enable AI Response Logging

**What**: AI response logging is disabled with a TODO comment in the evaluation service.

**Why**: Without logging, there's no audit trail of AI decisions, which is critical for debugging and user trust.

**Files to modify**:
- `backend/app/services/deal_evaluation_service.py` (around line 225)
- `backend/app/repositories/ai_response_repository.py`

**AI Task Prompt**:
```
Context: See ARCHITECTURE.md for project context.

Task: Re-enable AI response logging in backend/app/services/deal_evaluation_service.py.

There's a TODO comment (around line 225) about re-enabling AI response logging with async repository.
The AIResponseRepository exists in app/repositories/ai_response_repository.py.

1. Make the repository calls async-compatible
2. Log all LLM calls with: prompt, response, tokens_used, user_id
3. Ensure it doesn't block the main request flow (fire and forget if needed)
4. Add error handling so logging failures don't break evaluations
```

---

## 4. Phase 2 — Polish Core Experience

> **Priority**: MEDIUM — These make the product feel complete and professional.

### 4.1 Enhance Search Results with AI Summaries

**What**: Each vehicle in search results should have a brief AI-generated summary explaining why it matches the user's criteria.

**Why**: AI summaries differentiate AutoDealGenie from listing sites. Users want to know *why* a car is recommended, not just *that* it is.

**AI Task Prompt**:
```
Context: See ARCHITECTURE.md for project context.

Task: Enhance car search results with per-vehicle AI summaries.

Current state: The car recommendation service returns vehicles with a score and basic highlights.
The CarRecommendationItem schema (app/schemas/car_recommendation.py) already has a "summary" field.

Enhance the LLM ranking step in app/services/car_recommendation_service.py to:
1. Generate a 2-3 sentence natural language summary for each vehicle
2. Explain why this vehicle matches the user's stated priorities
3. Mention any notable pros or cons
4. Reference the user's budget and preferences in the summary

Update the frontend VehicleCard (components/organisms/VehicleCard.tsx) to display the summary.
```

### 4.2 Add Deal Summary Page

**What**: After evaluation, users need a comprehensive summary page showing the deal analysis, recommended actions, and next steps.

**Why**: The current evaluation page shows the score but lacks actionable guidance. A summary page ties together evaluation + negotiation + financing into one clear picture.

**AI Task Prompt**:
```
Context: See ARCHITECTURE.md and PROJECT_GUIDE.md for project context.

Task: Create a Deal Summary page at frontend/app/dashboard/summary/page.tsx.

This page should show:
1. Vehicle details (image, specs, pricing)
2. Deal score (1-10) with visual gauge/meter
3. Fair market value vs. asking price (with bar chart)
4. Key insights from evaluation (bullet points)
5. Negotiation history summary (if negotiated)
6. Recommended lender (top 1 from recommendations)
7. Recommended insurance (top 1 from recommendations)
8. Estimated monthly payment breakdown
9. Clear CTAs: "Start Negotiation", "Save Deal", "Search More"

Use existing components from components/atoms/ and components/molecules/.
Create new organism components as needed in components/organisms/.
Add a new step to the StepperProvider or create as a standalone page.
Fetch data from existing API endpoints (deals, evaluations, lenders, insurance).
```

### 4.3 Improve Negotiation UX

**What**: The negotiation chat needs visual improvements to feel more natural and provide clearer guidance.

**AI Task Prompt**:
```
Context: See ARCHITECTURE.md for project context.

Task: Improve the negotiation chat UX in frontend/app/dashboard/negotiation/page.tsx.

Enhancements:
1. Add a negotiation progress bar showing current offer vs. target price
2. Display AI confidence level for the suggested counter-offer
3. Add quick-action buttons: "Accept", "Counter at [suggested amount]", "Walk Away"
4. Show talking points as collapsible cards instead of inline text
5. Add a deal comparison sidebar showing:
   - Asking price
   - Current offer
   - Fair market value
   - Savings so far
6. Animate new messages with slide-in effect
7. Add sound/haptic feedback option for new messages

Use existing atoms and molecules. Create new components in components/organisms/.
Follow the atomic design pattern.
```

### 4.4 Add User Profile & Settings Page

**What**: Users need a profile page to manage their account and preferences.

**AI Task Prompt**:
```
Context: See ARCHITECTURE.md for project context.

Task: Create a user profile/settings page at frontend/app/dashboard/settings/page.tsx.

Sections:
1. Profile Information (name, email, avatar)
2. Notification Preferences (email, push, in-app)
3. Default Search Preferences (preferred make, budget range, payment method)
4. Credit Score Range (for pre-filled financing calculations)
5. Connected Services (future: dealer accounts, lender pre-approvals)
6. Security (change password, 2FA setup placeholder)

Backend:
- Use existing PUT /api/v1/preferences/ endpoint for saving preferences
- Use existing GET /api/v1/auth/me for profile data
- Add password change endpoint if not exists

Frontend:
- Create page with tabs for each section
- Use atoms (Input, Button, Card) and MUI components
- Add form validation with Zod
- Save preferences with optimistic UI updates
```

---

## 5. Phase 3 — Finance & Insurance Partner Ecosystem

> **Priority**: MEDIUM — These make AutoDealGenie revenue-ready and create partner value.

### 5.1 Dynamic Partner Management

**What**: Move lender and insurer partner data from hardcoded lists to a database-backed system with an admin interface.

**Why**: To onboard real partners, the system needs dynamic partner management, not hardcoded arrays.

**AI Task Prompt**:
```
Context: See ARCHITECTURE.md for project context.

Task: Create a dynamic partner management system.

Backend:
1. Create model: app/models/partner.py
   - Partner (id, name, type [lender/insurer], logo_url, description,
     min_credit_score, max_credit_score, min_amount, max_amount,
     base_apr_min, base_apr_max, terms, features, coverage_types,
     is_active, priority, commission_rate, api_endpoint, api_key_encrypted,
     created_at, updated_at)

2. Create migration: alembic revision --autogenerate -m "Add partners table"

3. Create repository: app/repositories/partner_repository.py
   - CRUD operations + filter by type/credit score/amount

4. Create service: app/services/partner_service.py
   - get_active_lenders(credit_score, loan_amount, term)
   - get_active_insurers(vehicle_value, coverage_type, driver_age)
   - Migrate scoring logic from lender_service.py and insurance_service.py

5. Create admin endpoints: app/api/v1/endpoints/admin_partners.py
   - POST /admin/partners - Create partner
   - PUT /admin/partners/{id} - Update partner
   - GET /admin/partners - List all partners
   - DELETE /admin/partners/{id} - Deactivate partner

6. Create seed data migration with current 12 hardcoded partners

7. Update lender_service.py and insurance_service.py to query from DB

8. Add tests for all new components
```

### 5.2 Partner API Integration Framework

**What**: Create a framework for integrating with real partner APIs for live quotes.

**AI Task Prompt**:
```
Context: See ARCHITECTURE.md for project context.

Task: Create a partner API integration framework.

Create app/services/partner_integrations/ directory with:

1. base_partner_client.py - Abstract base class:
   class BasePartnerClient:
       async def get_quote(self, request: QuoteRequest) -> QuoteResponse
       async def submit_application(self, application: Application) -> ApplicationResult
       async def check_status(self, reference_id: str) -> StatusResponse
       def is_available(self) -> bool

2. mock_partner_client.py - Mock implementation for testing:
   - Returns realistic but fake quotes
   - Simulates processing delays
   - Can be toggled via environment variable

3. partner_client_factory.py - Factory pattern:
   def get_partner_client(partner_id: str) -> BasePartnerClient
   - Returns mock client if no API configured
   - Returns real client if API endpoint is set

4. schemas:
   - QuoteRequest (vehicle_info, driver_info, coverage_type)
   - QuoteResponse (premium, coverage_details, terms, partner_reference)
   - Application (personal_info, vehicle_info, coverage_selection)
   - ApplicationResult (status, reference_id, next_steps)

This framework allows partners to be integrated one at a time without changing the core service layer.
```

### 5.3 Loan Pre-Approval Flow

**What**: Allow users to get pre-approved for a loan directly through the platform.

**AI Task Prompt**:
```
Context: See ARCHITECTURE.md for project context.

Task: Create a loan pre-approval flow.

Backend:
1. Create model: app/models/loan_application.py
   - LoanApplication (id, user_id, partner_id, status [draft/submitted/approved/denied/expired],
     loan_amount, vehicle_vin, credit_score_range, annual_income_range,
     employment_status, approved_amount, approved_apr, approved_term,
     reference_id, expires_at, created_at, updated_at)

2. Create schemas: app/schemas/loan_application_schemas.py
   - LoanApplicationCreate, LoanApplicationResponse, PreApprovalResult

3. Create service: app/services/loan_application_service.py
   - create_application(user_id, partner_id, application_data)
   - submit_to_partner(application_id) → uses partner_client_factory
   - get_status(application_id)
   - get_user_pre_approvals(user_id)

4. Create endpoint: app/api/v1/endpoints/loan_applications.py
   - POST /loan-applications/ - Start application
   - POST /loan-applications/{id}/submit - Submit to partner
   - GET /loan-applications/ - List user's applications
   - GET /loan-applications/{id} - Get status

Frontend:
5. Create pre-approval form component
6. Add pre-approval status to deal evaluation page
7. Show pre-approved amount in negotiation context
```

### 5.4 Insurance Quote Comparison

**What**: Show side-by-side insurance quotes from multiple partners with clear comparison.

**AI Task Prompt**:
```
Context: See ARCHITECTURE.md for project context.

Task: Create an insurance comparison feature.

Backend:
1. Add endpoint: GET /api/v1/insurance/compare
   - Accept: vehicle_vin, driver_age, coverage_type, zip_code
   - Return: Array of InsuranceQuote from multiple partners
   - Cache results for 24 hours

2. Add InsuranceQuote schema with:
   - partner_name, partner_logo, monthly_premium, annual_premium
   - coverage_breakdown (liability, collision, comprehensive, etc.)
   - deductible options with corresponding premiums
   - discounts_available, customer_rating, claims_process_rating

Frontend:
3. Create InsuranceComparisonTable organism component:
   - Side-by-side table comparing up to 4 quotes
   - Highlight best value, lowest premium, best coverage
   - Toggle between monthly and annual pricing
   - Filter by coverage level (basic, standard, premium)
   - "Select" button to attach to deal

4. Integrate into evaluation page as an expandable section
```

---

## 6. Phase 4 — Differentiation Features

> **Priority**: LOW-MEDIUM — These create significant competitive advantage.

### 6.1 Vehicle History Integration

**AI Task Prompt**:
```
Context: See ARCHITECTURE.md for project context.

Task: Integrate vehicle history data into the evaluation pipeline.

1. Create app/tools/vehicle_history_client.py
   - Abstract client that can integrate with Carfax, AutoCheck, or NMVTIS
   - Methods: get_history(vin) → VehicleHistory
   - VehicleHistory: accidents, owners, service_records, title_status, recalls

2. Add vehicle history to evaluation pipeline:
   - In VEHICLE_CONDITION step, factor in accident history
   - In RISK step, factor in title status and owner count
   - Display history timeline on evaluation page

3. Cache history in MongoDB (vehicle_history collection, 30-day TTL)

4. Frontend: Create VehicleHistoryTimeline organism component
   - Visual timeline of ownership, accidents, services
   - Red flags for salvage titles, flood damage, odometer rollback
```

### 6.2 Price Prediction Engine

**AI Task Prompt**:
```
Context: See ARCHITECTURE.md for project context.

Task: Add price prediction to help users know if they should buy now or wait.

1. Create app/services/price_prediction_service.py
   - analyze_price_trend(make, model, year, current_price) → PricePrediction
   - Use LLM with market context to predict 30/60/90-day price trend
   - Consider: seasonality, model year transitions, market conditions

2. PricePrediction schema:
   - current_price, predicted_30d, predicted_60d, predicted_90d
   - trend (rising/stable/declining)
   - confidence (low/medium/high)
   - recommendation (buy_now/wait/strong_buy)
   - reasoning (2-3 sentences)

3. Add to evaluation results as "Market Timing" section
4. Frontend: Create PriceTrendChart component with line graph
```

### 6.3 Proactive Deal Alerts

**AI Task Prompt**:
```
Context: See ARCHITECTURE.md for project context.

Task: Create a proactive deal alert system.

1. Enhance saved searches to run periodically:
   - Add schedule field to saved_searches (daily/weekly/instant)
   - Create app/services/alert_service.py
   - Run saved searches on schedule
   - Compare new results against previous results
   - Notify user of new matches, price drops, and deals that went away

2. Notification channels:
   - In-app notifications (store in PostgreSQL, show badge in header)
   - Email notifications (via SendGrid/SES - future integration point)
   - Push notifications (via web push API - future)

3. Frontend:
   - Add notification bell icon in Header
   - Create NotificationDropdown component
   - Show notification count badge
   - Mark as read/unread
```

### 6.4 Community Deal Ratings

**AI Task Prompt**:
```
Context: See ARCHITECTURE.md for project context.

Task: Add community ratings for completed deals.

1. Create model: app/models/deal_rating.py
   - DealRating (id, deal_id, user_id, overall_score, ease_score,
     value_score, comment, is_verified_purchase, created_at)

2. Create endpoints:
   - POST /deals/{id}/rate - Rate a completed deal
   - GET /deals/community-ratings - Get recent ratings with stats

3. Display aggregated ratings:
   - Average deal score by make/model
   - "How buyers felt about this car" section on results page
   - Trust indicator on evaluation page
```

---

## 7. Phase 5 — Scale & Monetize

> **Priority**: FUTURE — These enable growth and revenue.

### 7.1 Monetization Strategy

1. **Freemium Model**:
   - Free: 5 searches/month, basic evaluation, 1 active negotiation
   - Premium ($9.99/mo): Unlimited searches, full evaluation pipeline, unlimited negotiations, price predictions, deal alerts
   - Pro ($19.99/mo): Everything + vehicle history, priority partner matching, API access

2. **Partner Revenue**:
   - Lead generation fees from lender/insurer referrals
   - Commission on funded loans (0.5-1.5% of loan amount)
   - Insurance policy referral bonuses
   - Premium placement for partner visibility

3. **Data Monetization** (anonymized):
   - Market pricing trends for dealers
   - Consumer preference analytics for manufacturers
   - Regional demand patterns

### 7.2 Scalability Roadmap

```
Current:       Single FastAPI + Single PostgreSQL
                     ↓
Phase 1:       Add read replicas for PostgreSQL
               Separate WebSocket server
                     ↓
Phase 2:       Microservice split:
               - Auth Service
               - Search Service  
               - Evaluation Service
               - Negotiation Service
               - Partner Integration Service
                     ↓
Phase 3:       Event-driven architecture
               RabbitMQ for all inter-service communication
               Kubernetes for orchestration
```

### 7.3 Mobile Application

**AI Task Prompt**:
```
Context: See ARCHITECTURE.md for project context.

Task: Plan the mobile application architecture.

Requirements:
1. React Native or Flutter for cross-platform
2. Reuse backend API (no changes needed)
3. Push notifications for deal alerts
4. Camera integration for VIN scanning
5. Offline mode for saved deals and evaluations
6. Biometric authentication

Deliverable: Create MOBILE_ARCHITECTURE.md with:
- Technology recommendation with reasoning
- Screen flow diagrams
- Shared component strategy with web
- API usage plan
- Push notification architecture
```

---

## 8. Technical Debt

### 8.1 High Priority

| Item | Location | Description |
|------|----------|-------------|
| Auth token in localStorage | `frontend/lib/auth/AuthProvider.tsx` | Move to HTTP-only cookies for security |
| Missing `await` | `backend/app/services/deal_evaluation_service.py:~472` | `generate_structured_json()` call not awaited |
| AI logging disabled | `backend/app/services/deal_evaluation_service.py:~225` | TODO: Re-enable async AI response logging |
| Hardcoded partners | `backend/app/services/lender_service.py`, `insurance_recommendation_service.py` | Move to database-backed partners |

### 8.2 Medium Priority

| Item | Location | Description |
|------|----------|-------------|
| No Error Boundaries | Frontend pages | Add React Error Boundaries around major features |
| Form state in localStorage | Multi-step form flow | Move to server state + URL params |
| No pagination | Several list endpoints | Add cursor-based pagination for deals, favorites, searches |
| Missing frontend tests | Several organisms | Add tests for FilterPanel, FinancingOptionsForm, ChatInput |
| Missing backend tests | Negotiation, evaluation services | Add integration tests for full pipeline flows |

### 8.3 Low Priority

| Item | Location | Description |
|------|----------|-------------|
| Docker image size | `backend/Dockerfile` | Optimize with multi-stage build and slim base |
| No API versioning header | Backend responses | Add `X-API-Version` header |
| MongoDB indexes | Collections | Add indexes for search_history and vehicle_cache |
| Missing rate limiting | Frontend API client | Add client-side rate limiting/queuing |

---

## 9. AI Task Prompts

Below are ready-to-use prompts for delegating work to an AI assistant. Copy the relevant prompt, prepend with the project context documents, and submit.

### Quick-Start Prompt for Any Task

```
I'm working on AutoDealGenie, an AI-powered car-buying platform.

Project context:
- See PROJECT_GUIDE.md for the full project guide including user flows and status
- See ARCHITECTURE.md for architecture, patterns, and coding conventions
- See ROADMAP.md for the strategic plan and feature details

Backend: Python FastAPI (backend/app/)
Frontend: Next.js 14 + TypeScript (frontend/)
AI: OpenAI via centralized LLM module (backend/app/llm/)
DB: PostgreSQL + MongoDB + Redis

[Your specific task here]
```

### Prompt: Complete Core Pipeline

```
Using the project context from PROJECT_GUIDE.md and ARCHITECTURE.md:

Complete the following in priority order:
1. Fix the missing await on generate_structured_json() in deal_evaluation_service.py
2. Implement _evaluate_price() in deal_evaluation_service.py
3. Implement _evaluate_financing() in deal_evaluation_service.py
4. Implement _evaluate_risk() in deal_evaluation_service.py
5. Implement _evaluate_final() in deal_evaluation_service.py
6. Re-enable AI response logging

For each step, add:
- Prompt template in app/llm/prompts.py
- Response schema in app/llm/schemas.py
- Implementation with error handling and fallback scoring
- Pytest tests

Follow the coding conventions in ARCHITECTURE.md Section 6.
```

### Prompt: Add New Partner

```
Using the project context from PROJECT_GUIDE.md and ARCHITECTURE.md:

Add a new [lender/insurer] partner to AutoDealGenie:
- Name: [Partner Name]
- Type: [lender/insurer]
- APR Range: [min]% - [max]%
- Credit Score Range: [min] - [max]
- Loan Amount Range: $[min] - $[max]
- Terms: [12, 24, 36, 48, 60, 72] months
- Special Features: [list features]

Currently partners are hardcoded in:
- backend/app/services/lender_service.py (for lenders)
- backend/app/services/insurance_recommendation_service.py (for insurers)

Add the partner to the appropriate hardcoded list following the existing format.
The scoring algorithm will automatically rank the new partner.
```

### Prompt: Create New Frontend Feature

```
Using the project context from PROJECT_GUIDE.md and ARCHITECTURE.md:

Create a new [feature name] page/component.

Follow these conventions:
1. Use atoms from components/atoms/ (Button, Input, Card, Modal, Spinner)
2. Create new molecules in components/molecules/ if needed
3. Create the main component in components/organisms/
4. Create the page in app/dashboard/[feature]/page.tsx
5. Add API methods to lib/api.ts if new endpoints are needed
6. Add form validation with Zod in lib/validation/ if forms are involved
7. Use TypeScript with explicit types (no 'any')
8. Follow atomic design pattern

The feature should: [describe what it does]
```
