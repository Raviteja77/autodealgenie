# Deal Evaluation Pipeline

## Overview

The Deal Evaluation Pipeline is a multi-step process that helps users evaluate car deals comprehensively. It uses a combination of rule-based analysis and AI-powered insights to provide recommendations about vehicle purchases.

## Architecture

### Database Model

The `DealEvaluation` model tracks the state of each evaluation:

```python
class DealEvaluation(Base):
    id: int                    # Unique identifier
    user_id: int              # Foreign key to User
    deal_id: int              # Foreign key to Deal
    status: EvaluationStatus  # Current status (analyzing, awaiting_input, completed)
    current_step: PipelineStep # Current pipeline step
    result_json: dict         # JSON storage for step results
    created_at: datetime
    updated_at: datetime
```

### Pipeline Steps

The evaluation follows these sequential steps:

1. **VEHICLE_CONDITION** - Evaluate the vehicle's condition based on VIN and description
2. **PRICE** - Analyze pricing against fair market value
3. **FINANCING** - Evaluate financing options and costs
4. **RISK** - Assess risk factors (mileage, age, condition)
5. **FINAL** - Compile comprehensive recommendation

### Status Transitions

```
ANALYZING → AWAITING_INPUT → ANALYZING → ... → COMPLETED
```

- **ANALYZING**: Service is processing the current step
- **AWAITING_INPUT**: Service needs user input to continue
- **COMPLETED**: All steps finished, final recommendation available

## API Endpoints

### 1. Start or Continue Evaluation

```http
POST /api/v1/deals/{deal_id}/evaluation
```

**Request Body:**
```json
{
  "answers": {
    "vin": "1HGBH41JXMN109186",
    "condition_description": "Excellent condition"
  }
}
```

**Response:**
```json
{
  "evaluation_id": 1,
  "deal_id": 123,
  "status": "analyzing",
  "current_step": "price",
  "step_result": {
    "assessment": {
      "fair_value": 24500.00,
      "score": 7.5
    }
  },
  "result_json": {...}
}
```

### 2. Get Evaluation State

```http
GET /api/v1/deals/{deal_id}/evaluation/{evaluation_id}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "deal_id": 123,
  "status": "awaiting_input",
  "current_step": "vehicle_condition",
  "result_json": {...},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:05:00Z"
}
```

### 3. Submit Answers

```http
POST /api/v1/deals/{deal_id}/evaluation/{evaluation_id}/answers
```

**Request Body:**
```json
{
  "answers": {
    "financing_type": "loan",
    "interest_rate": 5.5,
    "down_payment": 5000
  }
}
```

## Usage Flow

### Example 1: Complete Evaluation Flow

```python
# 1. Start evaluation
response = client.post(
    f"/api/v1/deals/{deal_id}/evaluation",
    json={"answers": None}
)
evaluation_id = response.json()["evaluation_id"]

# 2. Check if input needed
if response.json()["status"] == "awaiting_input":
    questions = response.json()["step_result"]["questions"]
    
    # 3. Provide answers
    response = client.post(
        f"/api/v1/deals/{deal_id}/evaluation/{evaluation_id}/answers",
        json={
            "answers": {
                "vin": "1HGBH41JXMN109186",
                "condition_description": "Excellent"
            }
        }
    )

# 4. Continue until completed
while response.json()["status"] != "completed":
    # Continue processing or provide more answers
    pass

# 5. Get final results
final_eval = client.get(f"/api/v1/deals/{deal_id}/evaluation/{evaluation_id}")
```

### Example 2: Resume Existing Evaluation

```python
# If an evaluation is in progress, calling the start endpoint
# will continue the existing evaluation
response = client.post(
    f"/api/v1/deals/{deal_id}/evaluation",
    json={"answers": {...}}
)
```

## Step Details

### 1. Vehicle Condition Step

**Required Inputs:**
- `vin`: 17-character Vehicle Identification Number
- `condition_description`: Description of vehicle condition

**Output:**
```json
{
  "assessment": {
    "condition_score": 8.5,
    "condition_notes": ["Well maintained", "Clean interior"],
    "recommended_inspection": true
  }
}
```

### 2. Price Step

Uses the existing `evaluate_deal` method to assess pricing.

**Output:**
```json
{
  "assessment": {
    "fair_value": 24500.00,
    "score": 7.5,
    "insights": ["Priced $500 above fair value"],
    "talking_points": ["Mention comparable listings at $24,000"]
  }
}
```

### 3. Financing Step

**Optional Inputs:**
- `financing_type`: "cash", "loan", or "lease"
- `interest_rate`: Interest rate percentage (if financing)
- `down_payment`: Down payment amount (if financing)

**Output:**
```json
{
  "assessment": {
    "financing_type": "loan",
    "loan_amount": 20000.00,
    "estimated_monthly_payment": 377.42,
    "estimated_total_cost": 22645.20,
    "total_interest": 2645.20
  }
}
```

### 4. Risk Step

Automatically evaluates:
- Mileage risk
- Vehicle age risk
- Missing inspection risk
- Price risk

**Output:**
```json
{
  "assessment": {
    "risk_score": 4.5,
    "risk_factors": [
      "Vehicle age warrants thorough inspection"
    ],
    "recommendation": "Moderate risk - proceed with caution"
  }
}
```

### 5. Final Step

Compiles all previous steps into a comprehensive recommendation.

**Output:**
```json
{
  "assessment": {
    "overall_score": 7.2,
    "recommendation": "Recommended - Good deal with minor considerations",
    "summary": {
      "condition_score": 8.5,
      "price_score": 7.5,
      "risk_score": 4.5
    },
    "next_steps": [
      "Schedule a pre-purchase inspection",
      "Use provided talking points for negotiation"
    ],
    "estimated_total_cost": 25000.00
  }
}
```

## Testing

### Running Tests

```bash
# Run all evaluation tests
pytest tests/test_evaluation_*.py -v

# Run repository tests only
pytest tests/test_evaluation_repository.py -v

# Run endpoint tests only
pytest tests/test_evaluation_endpoints.py -v
```

### Manual Testing

A manual test script is available:

```bash
cd backend
python tests/manual_test_evaluation_pipeline.py
```

This script creates a test deal and walks through the entire pipeline.

## Database Migration

Apply the migration to create the `deal_evaluations` table:

```bash
cd backend
alembic upgrade head
```

The migration creates:
- `deal_evaluations` table
- Two enum types: `evaluationstatus` and `pipelinestep`
- Foreign keys to `users` and `deals` tables
- Indexes on `id`, `user_id`, `deal_id`, and `status`

## Implementation Notes

### Service Layer

The `DealEvaluationService` orchestrates the pipeline:
- `process_evaluation_step()`: Main method to process current step
- `_evaluate_vehicle_condition()`: Step 1 logic
- `_evaluate_price()`: Step 2 logic
- `_evaluate_financing()`: Step 3 logic
- `_evaluate_risk()`: Step 4 logic
- `_evaluate_final()`: Step 5 logic
- `_get_next_step()`: Determines next step in pipeline

### Repository Layer

The `EvaluationRepository` provides CRUD operations:
- `create()`: Create new evaluation
- `get()`: Get by ID
- `get_by_deal()`: Get all for a deal
- `get_latest_by_deal()`: Get most recent for a deal
- `update_status()`: Update status only
- `update_step()`: Update step only
- `update_result()`: Update result JSON
- `advance_step()`: Move to next step with results

### AI Integration

When available, the service uses LangChain/OpenAI for:
- Vehicle condition analysis
- Price insights and talking points
- Market comparisons

When LLM is not available, it falls back to rule-based logic.

## Error Handling

- `404`: Deal or evaluation not found
- `400`: Invalid request (e.g., wrong deal_id, not awaiting input)
- `500`: Internal processing error

## Future Enhancements

Potential improvements:
1. Vehicle history report integration (Carfax/AutoCheck)
2. Real-time market data from APIs
3. Insurance cost estimation
4. Maintenance cost predictions
5. Trade-in value analysis
6. Loan pre-approval integration
7. Webhook notifications for completed evaluations
8. Email reports with evaluation results
