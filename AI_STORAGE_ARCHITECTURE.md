# AI Response Storage Architecture

## Overview

AutoDealGenie now implements comprehensive storage for all AI-generated responses across the platform. This ensures full traceability of AI interactions throughout the deal lifecycle and enables powerful analytics capabilities.

## Storage Strategy

### PostgreSQL (Structured Data)
Used for simpler, structured AI responses that benefit from relational integrity and queryability:

1. **Loan Recommendations** (`loan_recommendations` table)
   - Calculated loan options with terms, APR, monthly payments
   - Links to deals and users via foreign keys
   - Enables historical comparison and trend analysis

2. **Insurance Recommendations** (`insurance_recommendations` table)
   - Provider matches with scores and premiums
   - Full provider details and reasoning
   - Tracks all recommendations for a deal

3. **Negotiation Messages** (`negotiation_messages` table) *existing*
   - Multi-round negotiation conversations
   - Agent responses with metadata (pricing, suggestions)

4. **Deal Evaluations** (`deal_evaluations` table) *existing*
   - Multi-step evaluation pipeline results
   - Condition, price, financing, risk assessments

### MongoDB (Flexible Data)
Used for complex AI responses and comprehensive logging:

1. **AI Responses** (`ai_responses` collection) *new*
   - **Purpose**: Comprehensive logging of all AI interactions
   - **Captures**: Feature, prompt used, variables, response content, metadata
   - **Benefits**: 
     - Deal lifecycle tracking
     - Platform-wide analytics
     - Token usage monitoring
     - LLM vs fallback analysis

2. **Search History** (`search_history` collection) *existing*
   - Car search queries and results
   - Top vehicle recommendations

## Data Models

### PostgreSQL Models

#### LoanRecommendation
```python
{
    "id": Integer,
    "deal_id": Integer (FK → deals.id),
    "user_id": Integer (FK → users.id),
    "loan_amount": Float,
    "down_payment": Float,
    "loan_term_months": Integer,
    "credit_score_range": String,
    "monthly_payment": Float,
    "apr": Float,
    "total_interest": Float,
    "total_amount": Float,
    "additional_data": JSON,  # Optional: amortization schedule
    "created_at": DateTime
}
```

#### InsuranceRecommendation
```python
{
    "id": Integer,
    "deal_id": Integer (FK → deals.id),
    "user_id": Integer (FK → users.id),
    "vehicle_value": Float,
    "vehicle_age": Integer,
    "coverage_type": String,
    "driver_age": Integer,
    "provider_id": String,
    "provider_name": String,
    "match_score": Float,
    "estimated_monthly_premium": Float,
    "estimated_annual_premium": Float,
    "recommendation_reason": String,
    "rank": Integer,
    "full_recommendation_data": JSON,  # Full provider details
    "created_at": DateTime
}
```

### MongoDB Collections

#### ai_responses
```javascript
{
    "_id": ObjectId,
    "feature": String,  // "negotiation", "deal_evaluation", "car_recommendation", etc.
    "user_id": Integer | null,  // User ID or null for anonymous
    "deal_id": Integer | null,  // Deal ID if associated
    "prompt_id": String,  // Prompt template ID used
    "prompt_variables": Object,  // Variables substituted in prompt
    "response_content": String | Object,  // AI-generated response
    "response_metadata": Object,  // Additional metadata (scores, suggestions, etc.)
    "model_used": String | null,  // OpenAI model used
    "tokens_used": Integer | null,  // Tokens consumed
    "temperature": Float | null,  // Temperature parameter
    "llm_used": Boolean,  // True if LLM, false for fallback
    "timestamp": DateTime
}
```

## API Endpoints

### AI Response History

#### Get Deal AI History
```http
GET /api/v1/ai-responses/history/{deal_id}?limit=100&skip=0
```
Returns all AI interactions for a specific deal.

**Response:**
```json
{
    "deal_id": 123,
    "count": 15,
    "responses": [
        {
            "_id": "...",
            "feature": "negotiation",
            "prompt_id": "negotiation_initial",
            "response_content": "...",
            "timestamp": "2025-12-25T14:00:00Z"
        }
    ]
}
```

#### Get User AI History
```http
GET /api/v1/ai-responses/history/user/{user_id}?limit=100&skip=0
```
Returns all AI interactions for a specific user. Users can only access their own history unless superuser.

#### Get Feature AI History
```http
GET /api/v1/ai-responses/history/feature/{feature}?user_id=123&limit=100
```
Returns AI interactions for a specific feature (e.g., "negotiation", "deal_evaluation").

#### Get Deal Lifecycle
```http
GET /api/v1/ai-responses/lifecycle/{deal_id}
```
Returns comprehensive lifecycle showing all AI interactions grouped by feature.

**Response:**
```json
{
    "deal_id": 123,
    "features": {
        "car_recommendation": {
            "count": 2,
            "responses": [...]
        },
        "deal_evaluation": {
            "count": 1,
            "responses": [...]
        },
        "negotiation": {
            "count": 8,
            "responses": [...]
        },
        "loan": {
            "count": 3,
            "responses": [...]
        },
        "insurance": {
            "count": 5,
            "responses": [...]
        }
    }
}
```

#### Get AI Analytics
```http
GET /api/v1/ai-responses/analytics?days=30
```
Platform-wide AI analytics (superuser only).

**Response:**
```json
{
    "period_days": 30,
    "features": {
        "negotiation": {
            "total_calls": 1250,
            "llm_calls": 1180,
            "fallback_calls": 70,
            "total_tokens": 485000
        },
        "deal_evaluation": {
            "total_calls": 890,
            "llm_calls": 875,
            "fallback_calls": 15,
            "total_tokens": 312000
        }
    }
}
```

### Updated Endpoints

#### Loan Calculation
```http
POST /api/v1/loans/calculate
```
Now optionally saves recommendations to database if `deal_id` is provided in request.

#### Insurance Recommendations
```http
POST /api/v1/insurance/recommendations
```
Now saves all recommendations to database if `deal_id` is provided in request.

## Integration Points

### Service Layer
All AI-generating services now log responses:

1. **NegotiationService**
   - Logs initial offers and counter responses
   - Captures suggested prices, financing options, AI metrics

2. **DealEvaluationService**
   - Logs evaluation results
   - Captures fair value, scores, insights, talking points

3. **CarRecommendationService**
   - Logs recommendation selections
   - Captures top vehicles, scores, highlights

4. **InsuranceRecommendationService**
   - Stores provider matches in PostgreSQL
   - Links to deals for traceability

5. **LoanCalculatorService** (via endpoints)
   - Stores loan calculations in PostgreSQL
   - Enables historical analysis

### Non-Blocking Design
- All AI response logging is non-blocking
- Failures don't affect user experience
- Errors are logged but don't propagate

## Use Cases

### Deal Lifecycle Tracking
Track complete AI interaction history for any deal:
```python
# Get all AI interactions for a deal
lifecycle = await ai_response_repository.get_deal_lifecycle(deal_id=123)

# Shows: search → evaluation → negotiation → loan → insurance
```

### Analytics & Monitoring
Monitor AI usage across the platform:
```python
# Get 30-day analytics
analytics = await ai_response_repository.get_analytics(days=30)

# Analyze: total calls, LLM vs fallback ratio, token consumption
```

### User History
Retrieve user's AI interaction history:
```python
# Get user's recent AI interactions
history = await ai_response_repository.get_by_user_id(user_id=456, limit=50)
```

### Feature Analysis
Analyze specific feature usage:
```python
# Get all negotiation AI responses
responses = await ai_response_repository.get_by_feature(
    feature="negotiation",
    user_id=456  # Optional filter
)
```

## Database Migration

To apply the new schema changes:

```bash
cd backend
alembic upgrade head
```

This will create:
- `loan_recommendations` table
- `insurance_recommendations` table
- Proper indexes for efficient querying

MongoDB collections are created automatically on first write.

## Environment Configuration

No new environment variables required. Existing MongoDB and PostgreSQL configurations are used:

```env
# Existing configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=autodealgenie
POSTGRES_SERVER=localhost
POSTGRES_DB=autodealgenie
```

## Performance Considerations

1. **Indexing**: MongoDB `ai_responses` collection is indexed on:
   - `deal_id`
   - `user_id`
   - `feature`
   - `timestamp`

2. **Pagination**: All history endpoints support pagination to handle large datasets

3. **Caching**: Deal evaluations continue to use Redis caching to minimize LLM calls

4. **Async Operations**: All MongoDB operations are async for better performance

## Security & Privacy

1. **Authorization**: Users can only access their own AI history
2. **Superuser Analytics**: Platform-wide analytics restricted to superusers
3. **No PII**: AI responses don't contain personally identifiable information
4. **Audit Trail**: Complete audit trail of all AI interactions

## Future Enhancements

1. **Retention Policies**: Implement data retention policies for old AI responses
2. **Export Functionality**: Enable users to export their AI interaction history
3. **Advanced Analytics**: ML-based insights on negotiation patterns
4. **Real-time Monitoring**: Dashboard for real-time AI usage monitoring
5. **A/B Testing**: Framework for testing different prompt strategies
