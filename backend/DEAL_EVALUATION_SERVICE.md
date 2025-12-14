# Deal Evaluation Service Documentation

## Overview

The Deal Evaluation Service provides comprehensive analysis of vehicle deals, including fair market value estimation, deal quality scoring, and AI-powered negotiation insights.

## Service Location

`backend/app/services/deal_evaluation_service.py`

## API Endpoint

**POST** `/api/v1/deals/evaluate`

### Authentication

This endpoint requires authentication. Include a valid JWT token in the request.

### Request Schema

```json
{
  "vehicle_vin": "1HGBH41JXMN109186",
  "asking_price": 25000.00,
  "condition": "good",
  "mileage": 45000
}
```

**Fields:**
- `vehicle_vin` (string, required): 17-character Vehicle Identification Number
- `asking_price` (float, required): Asking price in USD (must be positive)
- `condition` (string, required): Vehicle condition (e.g., "excellent", "good", "fair", "poor")
- `mileage` (integer, required): Current mileage in miles (must be non-negative)

### Response Schema

```json
{
  "fair_value": 24500.00,
  "score": 7.5,
  "insights": [
    "This vehicle is priced $500 above market value",
    "The mileage is average for this year",
    "Condition rating suggests proper maintenance"
  ],
  "talking_points": [
    "Point out comparable vehicles priced at $24,500",
    "Request maintenance records to justify the condition rating",
    "Use the mileage as slight negotiation leverage"
  ]
}
```

**Fields:**
- `fair_value` (float): Estimated fair market value in USD
- `score` (float): Deal quality score from 1-10
  - 1-3: Poor deal, significantly overpriced
  - 4-6: Fair deal, close to market value
  - 7-9: Good deal, below market value
  - 10: Excellent deal, significantly underpriced
- `insights` (array): 3-5 key observations about the deal
- `talking_points` (array): 3-5 specific negotiation strategies

## Service Features

### 1. AI-Powered Analysis (Primary Mode)

When LangChain/OpenAI integration is available:
- Uses GPT-4 to analyze vehicle pricing
- Considers VIN, condition, mileage, and market data
- Generates contextual negotiation strategies
- Provides data-driven fair value estimates

### 2. Fallback Analysis (Offline Mode)

When AI services are unavailable:
- Uses heuristic-based evaluation
- Factors in condition and mileage
- Applies industry-standard depreciation curves
- Provides basic negotiation guidance

### Fallback Scoring Logic

**Base Score:** 5.0/10

**Condition Adjustments:**
- Excellent/Like New: +1.5
- Good/Very Good: +0.5
- Fair: -0.5
- Poor: -1.5

**Mileage Adjustments:**
- < 30,000 miles: +1.0 (exceptionally low)
- 30,000-60,000 miles: +0.5 (low)
- 60,000-100,000 miles: 0 (moderate)
- 100,000-150,000 miles: -0.5 (high)
- > 150,000 miles: -1.0 (very high)

**Fair Value Calculation:**
```python
fair_value_adjustment = (score - 5.0) / 10.0
fair_value = asking_price * (1.0 - fair_value_adjustment * 0.1)
```

## Integration with LangChain

The service uses the existing `langchain_service` singleton:

```python
from app.services.langchain_service import langchain_service

# Check if LLM is available
if langchain_service.llm:
    # Use AI-powered evaluation
else:
    # Use fallback heuristics
```

## Example Usage

### Python/FastAPI

```python
from app.services.deal_evaluation_service import deal_evaluation_service

result = await deal_evaluation_service.evaluate_deal(
    vehicle_vin="1HGBH41JXMN109186",
    asking_price=25000.00,
    condition="good",
    mileage=45000
)

print(f"Fair Value: ${result['fair_value']:,.2f}")
print(f"Deal Score: {result['score']}/10")
```

### cURL

```bash
curl -X POST "http://localhost:8000/api/v1/deals/evaluate" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_vin": "1HGBH41JXMN109186",
    "asking_price": 25000.00,
    "condition": "good",
    "mileage": 45000
  }'
```

### JavaScript/Fetch

```javascript
const response = await fetch('http://localhost:8000/api/v1/deals/evaluate', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_JWT_TOKEN',
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    vehicle_vin: '1HGBH41JXMN109186',
    asking_price: 25000.00,
    condition: 'good',
    mileage: 45000
  })
});

const evaluation = await response.json();
console.log('Fair Value:', evaluation.fair_value);
console.log('Score:', evaluation.score);
```

## Testing

### Run Tests

```bash
cd backend
export MARKET_CHECK_API_KEY=test_key
export OPENAI_API_KEY=test_key
export SECRET_KEY=test_secret_key_with_min_32_characters_for_jwt
export POSTGRES_PASSWORD=test_password
pytest tests/test_deal_evaluation.py -v
```

### Test Coverage

The service includes comprehensive tests for:
- AI-powered evaluation with LLM
- Fallback evaluation without LLM
- Edge cases (excellent vs. poor condition)
- Error handling (LLM failures, invalid JSON)
- API endpoint validation
- Authentication requirements
- Input validation (VIN length, price, mileage)

### Test Files

- `tests/test_deal_evaluation.py`: 12 test cases covering service and endpoint

## Error Handling

### Validation Errors (422)

Invalid input will return a 422 status with details:

```json
{
  "detail": [
    {
      "loc": ["body", "vehicle_vin"],
      "msg": "ensure this value has at least 17 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

### Authentication Errors (401)

Missing or invalid token returns 401:

```json
{
  "detail": "Not authenticated"
}
```

### Service Errors

The service handles errors gracefully:
- LLM API failures → falls back to heuristic evaluation
- Invalid JSON from LLM → falls back to heuristic evaluation
- Missing environment variables → logs warning and uses fallback

## Configuration

### Environment Variables

```bash
# Required for AI-powered features
OPENAI_API_KEY=your-openai-api-key

# LLM model selection
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo
```

### Coverage Exclusions

The service is **NOT** excluded from test coverage (unlike some external integrations), as it contains critical business logic that should be tested.

## Future Enhancements

Potential improvements for future iterations:
1. **Historical Data Integration**: Use actual market data for fair value calculation
2. **Vehicle History Reports**: Integrate Carfax/AutoCheck for comprehensive analysis
3. **Comparable Sales**: Pull recent sales data for similar vehicles
4. **Regional Pricing**: Adjust fair value based on geographic location
5. **Depreciation Curves**: Model-specific depreciation rates
6. **Market Trends**: Factor in current market conditions (supply/demand)
7. **Dealer Ratings**: Consider dealer reputation in evaluation

## Performance Considerations

- **LLM Latency**: AI-powered evaluation may take 2-5 seconds
- **Fallback Speed**: Heuristic evaluation is instant (<10ms)
- **Caching**: Consider caching results by VIN for repeated queries
- **Rate Limiting**: OpenAI API has rate limits; implement request throttling for production

## Support

For issues or questions:
- Check logs for LLM-related warnings
- Verify `OPENAI_API_KEY` is set correctly
- Test with fallback mode first (unset `OPENAI_API_KEY`)
- Review test cases for expected behavior
