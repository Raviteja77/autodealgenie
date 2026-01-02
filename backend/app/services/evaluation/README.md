# Deal Evaluation Service Package

This package provides modular deal evaluation functionality following the orchestrator pattern established in the Negotiation Service.

## Architecture

The Deal Evaluation Service follows a **modular orchestrator pattern** where specialized evaluators handle specific aspects of deal analysis:

```
DealEvaluationService (Orchestrator)
├── ConditionEvaluator   - Vehicle condition assessment
├── PricingEvaluator     - Market pricing and value analysis  
├── FinancingEvaluator   - Affordability metrics
└── RiskEvaluator        - Risk factor evaluation
```

## Files

### Core Files

- **`core.py`** - Main orchestrator that coordinates all evaluators
- **`__init__.py`** - Package initialization with backward-compatible imports

### Evaluator Modules

- **`condition.py`** - Assesses vehicle condition using LLM with evaluator agent role
- **`pricing.py`** - Integrates MarketCheck API and provides unified pricing strategy
- **`financing.py`** - Implements affordability metrics (payment-to-income calculations)
- **`risk.py`** - Factors age, mileage, and price-delta risk scoring

### Configuration

- **`app/core/evaluation_config.py`** - Centralized constants (scores, thresholds, weights)

## Usage

### Quick Evaluation

```python
from app.services.evaluation import deal_evaluation_service

# Evaluate a deal
result = await deal_evaluation_service.evaluate_deal(
    vehicle_vin="1HGBH41JXMN109186",
    asking_price=25000.00,
    condition="good",
    mileage=50000,
    make="Honda",
    model="Accord", 
    year=2020,
    zip_code="90210"
)

# Returns: {
#   "fair_value": 24500.00,
#   "score": 7.5,
#   "insights": [...],
#   "talking_points": [...],
#   "market_data": {...}  # If MarketCheck available
# }
```

### Pipeline Evaluation

```python
from app.services.evaluation import DealEvaluationService

service = DealEvaluationService(db)

# Process step-by-step evaluation
step_result = await service.process_evaluation_step(
    db=db,
    evaluation_id=123,
    user_answers={"vin": "1HGBH41JXMN109186", "condition_description": "excellent"}
)
```

## Evaluator Details

### ConditionEvaluator

**Purpose**: Assess vehicle condition based on VIN, description, and mileage

**Methods**:
- `evaluate()` - LLM-powered condition assessment
- `get_mileage_assessment()` - Mileage-based scoring
- `get_condition_adjustment()` - Condition-based score adjustment

**Returns**:
```python
{
    "condition_score": 8.5,
    "condition_notes": ["Excellent condition", "Well maintained"],
    "recommended_inspection": False
}
```

### PricingEvaluator

**Purpose**: Evaluate pricing using MarketCheck API and LLM insights

**Strategy**:
1. Try MarketCheck ML price prediction
2. Use LLM evaluation with market context (if available)
3. Fallback to heuristic evaluation

**Error Handling**: Uses `MarketDataError` for pricing integration failures with graceful fallback

**Methods**:
- `evaluate()` - Unified pricing evaluation
- `_get_market_data()` - Fetch MarketCheck data with error handling
- `_llm_evaluation()` - LLM-powered evaluation
- `_marketcheck_evaluation()` - Market data-based evaluation
- `_heuristic_evaluation()` - Fallback evaluation

### FinancingEvaluator

**Purpose**: Calculate affordability metrics and financing recommendations

**Methods**:
- `evaluate()` - Main financing evaluation
- `_evaluate_cash()` - Cash purchase assessment
- `_evaluate_loan()` - Loan financing assessment

**Features**:
- Payment-to-income ratio calculations
- Interest cost analysis
- Financing vs. cash recommendations
- Affordability scoring (1-10)

### RiskEvaluator

**Purpose**: Assess risk factors (age, mileage, price premium)

**Risk Factors**:
- High mileage (>100k miles)
- Vehicle age (>10 years)
- Missing inspection
- Price premium over fair value

**Returns**:
```python
{
    "risk_score": 6.5,  # 1-10 scale (lower is better)
    "risk_factors": ["High mileage increases maintenance risk"],
    "recommendation": "Moderate risk - proceed with caution"
}
```

## Configuration

All constants are centralized in `app/core/evaluation_config.py`:

```python
from app.core.evaluation_config import EvaluationConfig

# Affordability thresholds
EvaluationConfig.AFFORDABILITY_EXCELLENT  # 10%
EvaluationConfig.AFFORDABILITY_GOOD       # 15%
EvaluationConfig.AFFORDABILITY_MODERATE   # 20%

# Deal quality thresholds
EvaluationConfig.EXCELLENT_DEAL_SCORE     # 8.0
EvaluationConfig.GOOD_DEAL_SCORE          # 6.5

# Interest rate thresholds
EvaluationConfig.LOW_INTEREST_RATE        # 4.0%
EvaluationConfig.REASONABLE_INTEREST_RATE # 5.0%

# Mileage thresholds
EvaluationConfig.MILEAGE_EXCEPTIONALLY_LOW  # < 30k
EvaluationConfig.MILEAGE_LOW                # < 60k
EvaluationConfig.MILEAGE_MODERATE           # < 100k
EvaluationConfig.MILEAGE_HIGH               # < 150k

# Risk thresholds
EvaluationConfig.RISK_HIGH_MILEAGE_THRESHOLD  # 100k
EvaluationConfig.RISK_OLD_AGE_THRESHOLD       # 10 years

# Final evaluation weights
EvaluationConfig.WEIGHT_CONDITION  # 20%
EvaluationConfig.WEIGHT_PRICE      # 50%
EvaluationConfig.WEIGHT_RISK       # 30% (inverted)
```

## LLM Integration

All LLM calls use the centralized `app/llm` module with the `evaluator` agent role:

```python
from app.llm import generate_structured_json
from app.llm.schemas import DealEvaluation, VehicleConditionAssessment

# Structured JSON evaluation
evaluation = generate_structured_json(
    prompt_id="evaluation_with_market",  # or "evaluation"
    variables={...},
    response_model=DealEvaluation,
    temperature=0.7,
    agent_role="evaluator"  # Use evaluator role
)
```

**Available Prompts**:
- `evaluation` - Basic deal evaluation
- `evaluation_with_market` - Evaluation with MarketCheck context
- `vehicle_condition` - Condition assessment

## Caching

Results are cached in Redis using deterministic cache keys:

- **Cache Key**: SHA-256 hash of VIN, price, condition, mileage, make, model, year
- **TTL**: 3600 seconds (1 hour)
- **Graceful Degradation**: Works without Redis

## Testing

Comprehensive tests are in `tests/test_evaluation_modules.py`:

```bash
# Run evaluation module tests
pytest tests/test_evaluation_modules.py -v

# Run all evaluation-related tests
pytest tests/test_evaluation*.py -v

# Run with coverage
pytest tests/test_evaluation*.py --cov=app.services.evaluation --cov-report=term
```

## Benefits of Modular Design

1. **Separation of Concerns**: Each evaluator handles one aspect of evaluation
2. **Testability**: Individual modules can be tested independently
3. **Maintainability**: Changes to one aspect don't affect others
4. **Reusability**: Evaluators can be used in different contexts
5. **Consistency**: Pipeline and quick evaluations use same underlying logic
6. **Extensibility**: Easy to add new evaluator modules

## Migration from Old Service

See `MIGRATION.md` for details on migrating from the monolithic service.

**Old Import**:
```python
from app.services.deal_evaluation_service import deal_evaluation_service
```

**New Import** (backward compatible):
```python
from app.services.evaluation import deal_evaluation_service
```

## Error Handling

- **MarketDataError**: Raised for MarketCheck API failures (graceful fallback)
- **ApiError**: Base error for API-level failures
- **ValueError**: Raised for invalid pipeline steps or parameters

All errors are logged and handled gracefully with fallback strategies.

## Performance

- **Cache Hit**: ~10ms (Redis lookup)
- **LLM Evaluation**: ~1-3 seconds (OpenAI API)
- **MarketCheck API**: ~500ms-1s
- **Heuristic Fallback**: <10ms

## Future Enhancements

- [ ] Vehicle history integration (Carfax/AutoCheck)
- [ ] Regional price adjustments
- [ ] Seasonal pricing factors
- [ ] Trade-in value estimation
- [ ] Insurance cost estimation
- [ ] Total cost of ownership (TCO) calculation
