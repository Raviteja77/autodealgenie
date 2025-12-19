# Mock Services Guide

This guide explains how to use the mock services implementation in AutoDealGenie for development and testing.

## Overview

The mock services provide simulated API endpoints that return realistic data without requiring external API calls or incurring costs. This allows frontend developers to work independently of backend services and external APIs.

## Features

- **Market Check API Mock**: Simulates vehicle search with realistic car listings
- **LLM Service Mock**: Provides text generation and structured JSON responses
- **Negotiation Service Mock**: Simulates multi-round negotiation sessions
- **Deal Evaluation Mock**: Returns vehicle evaluation data and pipeline management

## Configuration

### Backend Setup

1. **Enable Mock Services**
   ```bash
   # In backend/.env
   USE_MOCK_SERVICES=true
   ```

2. **Verify Configuration**
   - When enabled, the backend will print: `"Mock services are ENABLED - using mock endpoints for development"`
   - Mock endpoints are available at: `http://localhost:8000/mock/*`

3. **Swagger Documentation**
   - Access mock API docs at: `http://localhost:8000/docs`
   - Mock endpoints appear under tags: `mock-marketcheck`, `mock-llm`, `mock-negotiation`, `mock-evaluation`

### Frontend Setup

1. **Enable Mock Mode**
   ```bash
   # In frontend/.env.local
   NEXT_PUBLIC_USE_MOCK=true
   ```

2. **API Client Auto-Routing**
   - When `NEXT_PUBLIC_USE_MOCK=true`, the API client automatically routes requests to mock endpoints
   - No code changes needed - just toggle the environment variable

## Mock Endpoints

### Market Check API

**Endpoint**: `POST /mock/marketcheck/search`

**Request Body**:
```json
{
  "make": "Honda",
  "model": "Accord",
  "budget_min": 20000,
  "budget_max": 40000,
  "year_min": 2020,
  "year_max": 2023
}
```

**Response**:
```json
{
  "search_criteria": {...},
  "top_vehicles": [
    {
      "vin": "1HGCM82633A123456",
      "make": "Honda",
      "model": "Accord",
      "year": 2023,
      "price": 28500,
      "mileage": 15000,
      "recommendation_score": 9.0,
      "highlights": [...],
      "recommendation_summary": "..."
    }
  ],
  "total_found": 5,
  "total_analyzed": 5
}
```

### LLM Service

**Text Generation**: `POST /mock/llm/generate`

**Request Body**:
```json
{
  "prompt_id": "negotiation",
  "variables": {
    "round_number": 1,
    "asking_price": 30000
  }
}
```

**Response**:
```json
{
  "content": "Thank you for your interest! The asking price...",
  "prompt_id": "negotiation",
  "model": "mock-gpt-4",
  "tokens_used": 150
}
```

**Structured Generation**: `POST /mock/llm/generate-structured`

**Request Body**:
```json
{
  "prompt_id": "evaluation",
  "variables": {
    "asking_price": 30000,
    "vin": "1HGCM82633A123456"
  }
}
```

**Response**:
```json
{
  "content": {
    "fair_value": 28500,
    "score": 8.5,
    "insights": [...],
    "talking_points": [...]
  },
  "prompt_id": "evaluation",
  "model": "mock-gpt-4",
  "tokens_used": 200
}
```

### Negotiation Service

**Create Session**: `POST /mock/negotiation/create`

**Request Body**:
```json
{
  "deal_id": 1,
  "user_target_price": 28000,
  "strategy": "moderate"
}
```

**Response**:
```json
{
  "session_id": 1000,
  "status": "active",
  "current_round": 1,
  "agent_message": "Welcome! I see you're interested...",
  "metadata": {
    "suggested_price": 29000,
    "asking_price": 30000,
    "user_target": 28000
  }
}
```

**Process Round**: `POST /mock/negotiation/{session_id}/next`

**Request Body**:
```json
{
  "user_action": "counter",
  "counter_offer": 27000
}
```

**Get Session**: `GET /mock/negotiation/{session_id}`

### Deal Evaluation

**Evaluate Deal**: `POST /mock/evaluation/evaluate`

**Request Body**:
```json
{
  "vehicle_vin": "1HGCM82633A123456",
  "asking_price": 30000,
  "condition": "good",
  "mileage": 50000
}
```

**Response**:
```json
{
  "vin": "1HGCM82633A123456",
  "fair_value": 28500,
  "score": 8.0,
  "insights": [...],
  "talking_points": [...],
  "asking_price": 30000,
  "condition": "good",
  "mileage": 50000
}
```

**Start Pipeline**: `POST /mock/evaluation/pipeline/start`

**Request Body**:
```json
{
  "deal_id": 1
}
```

**Submit Answers**: `POST /mock/evaluation/pipeline/{evaluation_id}/submit`

**Request Body**:
```json
{
  "answers": {
    "exterior_condition": "Good",
    "interior_condition": "Good"
  }
}
```

## Example Components

Two example React components are provided to demonstrate mock API usage:

1. **MarketCheckComponent** (`frontend/components/examples/MarketCheckComponent.tsx`)
   - Shows how to search for cars using the mock API
   - Includes search filters and results display
   - Example of handling loading states and errors

2. **LLMComponent** (`frontend/components/examples/LLMComponent.tsx`)
   - Demonstrates text and structured JSON generation
   - Shows different prompt types
   - Example of dynamic variable input

### Viewing Examples

Visit `http://localhost:3000/examples` to see the example components in action.

## Mock Data

The mock services include realistic sample data:

- **5 Vehicle Listings**: Honda Accord, Tesla Model 3, Jeep Grand Cherokee, VW Jetta, BMW X5
- **Negotiation State**: Maintains session state for multi-round negotiations
- **Dynamic Responses**: Responses adapt based on input parameters

## Testing

Comprehensive tests are provided in `backend/tests/test_mock_services.py`:

```bash
# Run mock service tests
cd backend
pytest tests/test_mock_services.py -v
```

Test coverage includes:
- Market Check search with various filters
- LLM text and structured generation
- Negotiation session lifecycle
- Deal evaluation with different conditions
- Pipeline management

## Switching Between Mock and Real Services

### Development Workflow

1. **Start with Mocks**
   ```bash
   # Backend
   USE_MOCK_SERVICES=true
   
   # Frontend
   NEXT_PUBLIC_USE_MOCK=true
   ```

2. **Test Integration**
   - Develop and test UI components with mock data
   - Verify data flow and state management
   - Test error handling with predictable responses

3. **Switch to Real Services**
   ```bash
   # Backend
   USE_MOCK_SERVICES=false
   
   # Frontend
   NEXT_PUBLIC_USE_MOCK=false
   ```

4. **Validate Real Integration**
   - Ensure external API credentials are configured
   - Test with real data and rate limits
   - Verify production behavior

### No Code Changes Required

The implementation uses environment variables exclusively - no code changes are needed to switch between mock and real services.

## Benefits

✅ **Cost Savings**: No external API charges during development  
✅ **Faster Development**: No rate limits or network delays  
✅ **Offline Work**: Develop without internet connectivity  
✅ **Predictable Data**: Consistent test data for debugging  
✅ **Independent Development**: Frontend doesn't block on backend/external APIs  
✅ **Easy Testing**: Comprehensive test suite for mock endpoints  

## Troubleshooting

### Mock Endpoints Not Available

**Problem**: 404 errors when calling mock endpoints

**Solution**:
1. Verify `USE_MOCK_SERVICES=true` in `backend/.env`
2. Restart the backend server
3. Check startup logs for "Mock services are ENABLED" message

### Frontend Still Calling Real Endpoints

**Problem**: Frontend makes requests to `/api/v1` instead of `/mock`

**Solution**:
1. Verify `NEXT_PUBLIC_USE_MOCK=true` in `frontend/.env.local`
2. Restart the frontend dev server (Next.js requires restart for env changes)
3. Clear browser cache and reload

### Type Errors in Example Components

**Problem**: TypeScript errors in example components

**Solution**:
1. Ensure `@mui/material` is installed: `npm install @mui/material`
2. Check custom UI components exist in `components/ui/`
3. Run `npm run lint` to identify specific issues

## Best Practices

1. **Use Mocks for UI Development**: Focus on user experience without external dependencies
2. **Test Both Modes**: Verify behavior with both mock and real services
3. **Keep Mocks Realistic**: Update mock data to reflect actual API responses
4. **Document Differences**: Note any behavioral differences between mock and real
5. **Environment Variables Only**: Never hardcode mock/real switching in code

## Additional Resources

- [Backend API Documentation](http://localhost:8000/docs)
- [Frontend Examples](http://localhost:3000/examples)
- [Test Suite](../backend/tests/test_mock_services.py)
- [API Client Implementation](../frontend/lib/api.ts)
