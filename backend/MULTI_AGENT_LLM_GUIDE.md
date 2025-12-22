# Multi-Agent LLM System Guide

## Overview

AutoDealGenie uses a custom multi-agent LLM system that replaces CrewAI's heavy orchestration with direct OpenAI API integration. This guide explains the architecture, agent roles, and how to use the system effectively.

## Migration from CrewAI

### Why Replace CrewAI?

1. **Simpler Deployment**: Synchronous client is easier to deploy and debug
2. **Direct Control**: Full control over prompts, context passing, and error handling
3. **Cost Optimization**: Fine-grained control over token usage and model selection
4. **Flexibility**: Easier to customize agent behaviors and add new capabilities
5. **Performance**: Reduced overhead from orchestration framework

### Key Differences

| Aspect | CrewAI | Custom LLM Client |
|--------|---------|-------------------|
| Client | Async orchestration framework | Synchronous OpenAI client |
| Configuration | YAML files (agents.yaml, tasks.yaml) | Python templates in prompts.py |
| JSON Output | Custom parsing | OpenAI's response_format=json_object |
| Agent Context | Framework-managed | Explicit variable passing |
| Error Handling | Framework-level | Granular per-call error handling |

## Architecture

### Core Components

```
backend/app/llm/
├── llm_client.py      # Synchronous OpenAI client with multi-agent support
├── prompts.py         # Centralized prompt registry with agent templates
├── schemas.py         # Pydantic models for structured outputs
└── __init__.py        # Public API exports
```

### Agent Roles

The system implements 5 specialized agents, each with distinct expertise:

#### 1. Research Agent
**Role**: Senior Vehicle Discovery Specialist

**Backstory**: Expert automotive researcher with deep knowledge of vehicle markets, pricing trends, and availability. Excels at finding hidden gems and identifying best deals.

**Capabilities**:
- Comprehensive market analysis across multiple sources
- Identification of undervalued vehicles
- Expert knowledge of reliability ratings
- Data-driven recommendations

**Prompt ID**: `research_vehicles`

**Output Schema**: VehicleReport (JSON)

**Example Usage**:
```python
from app.llm import generate_structured_json
from app.llm.schemas import VehicleReport

result = generate_structured_json(
    prompt_id="research_vehicles",
    variables={
        "make": "Honda",
        "model": "Civic",
        "price_min": 20000,
        "price_max": 30000,
        "condition": "used",
        "year_min": 2019,
        "year_max": 2023,
        "mileage_max": 50000,
        "location": "Seattle, WA"
    },
    response_model=VehicleReport,
    agent_role="research"
)
```

#### 2. Loan Analyzer Agent
**Role**: Senior Auto Financial Specialist

**Backstory**: Seasoned financial advisor specializing in auto loans with extensive knowledge of lending practices, credit optimization, and negotiating with financial institutions.

**Capabilities**:
- Comprehensive financing options analysis
- APR comparison and TCO calculations
- Credit optimization strategies
- Dealer vs. external lending comparison

**Prompt ID**: `analyze_financing`

**Output Schema**: FinancingReport (JSON)

**Example Usage**:
```python
result = generate_structured_json(
    prompt_id="analyze_financing",
    variables={
        "vehicle_report_json": json.dumps(vehicle_report),
        "loan_term_months": 60,
        "down_payment": 5000,
        "interest_rate": 4.5
    },
    response_model=FinancingReport,
    agent_role="loan"
)
```

#### 3. Negotiation Agent
**Role**: Expert Car Deal Negotiator

**Backstory**: Master negotiator with background in automotive sales and purchasing. Spent years on both sides of the table, learning every trick in the dealer's playbook. Persuasive, persistent, and unflappable.

**Capabilities**:
- Strategic pricing and counter-offer tactics
- Understanding of dealer incentives
- Effective communication strategies
- Leverage identification (DOM, inventory, financing)

**Prompt ID**: `negotiate_deal`

**Output Schema**: NegotiatedDeal (JSON)

**Example Usage**:
```python
result = generate_structured_json(
    prompt_id="negotiate_deal",
    variables={
        "vehicle_report_json": json.dumps(vehicle_report),
        "financing_report_json": json.dumps(financing_report),
        "days_on_market": 45,
        "fair_market_price": 24500,
        "sales_stats": "Low inventory, 3 units sold this month"
    },
    response_model=NegotiatedDeal,
    agent_role="negotiation"
)
```

#### 4. Deal Evaluator Agent
**Role**: Meticulous Deal Evaluator

**Backstory**: Former financial auditor who transitioned into consumer advocacy in automotive space. Eagle eye for fine print and passion for numbers. Believes a good deal is about total value and transparency.

**Capabilities**:
- Comprehensive financial analysis
- Vehicle history verification
- Market value comparison
- Hidden cost identification

**Prompt ID**: `evaluate_deal`

**Output Format**: Markdown Report

**Example Usage**:
```python
result = generate_text(
    prompt_id="evaluate_deal",
    variables={
        "negotiated_deal_json": json.dumps(negotiated_deal),
        "financing_report_json": json.dumps(financing_report),
        "fair_market_value": 24500,
        "vehicle_history_summary": "Clean title, 1 owner, no accidents",
        "safety_recalls_summary": "No open recalls",
        "days_on_market": 45
    },
    agent_role="evaluator"
)
```

#### 5. Quality Assurance Agent
**Role**: Deal Quality Assurance Reviewer

**Backstory**: Final line of defense before customer sees a recommendation. Sharp eye for missing context, contradictory statements, and math inconsistencies. Never invents facts or alters numbers.

**Capabilities**:
- Cross-checking narrative against data
- Identifying logical inconsistencies
- Ensuring clarity for non-experts
- Validating recommendations

**Prompt ID**: `review_final_report`

**Output Schema**: QAReport (JSON)

**Example Usage**:
```python
result = generate_structured_json(
    prompt_id="review_final_report",
    variables={
        "deal_evaluation_report": evaluation_report,
        "vehicle_report_json": json.dumps(vehicle_report),
        "financing_report_json": json.dumps(financing_report),
        "negotiated_deal_json": json.dumps(negotiated_deal)
    },
    response_model=QAReport,
    agent_role="qa"
)
```

## Multi-Agent Workflow Example

### Complete Car Buying Workflow

```python
from app.llm import generate_structured_json, generate_text
from app.llm.schemas import VehicleReport, FinancingReport, NegotiatedDeal, QAReport
import json

# Step 1: Research Agent - Find vehicles
vehicles = generate_structured_json(
    prompt_id="research_vehicles",
    variables={
        "make": "Honda",
        "model": "Civic",
        "price_min": 20000,
        "price_max": 30000,
        "condition": "used",
        "year_min": 2019,
        "year_max": 2023,
        "mileage_max": 50000,
        "location": "Seattle, WA"
    },
    response_model=VehicleReport,
    agent_role="research"
)

# Step 2: Loan Analyzer - Find best financing
financing = generate_structured_json(
    prompt_id="analyze_financing",
    variables={
        "vehicle_report_json": vehicles.model_dump_json(),
        "loan_term_months": 60,
        "down_payment": 5000,
        "interest_rate": 4.5
    },
    response_model=FinancingReport,
    agent_role="loan"
)

# Step 3: Negotiation Agent - Negotiate deal
deal = generate_structured_json(
    prompt_id="negotiate_deal",
    variables={
        "vehicle_report_json": vehicles.model_dump_json(),
        "financing_report_json": financing.model_dump_json(),
        "days_on_market": 45,
        "fair_market_price": 24500,
        "sales_stats": "Low inventory"
    },
    response_model=NegotiatedDeal,
    agent_role="negotiation"
)

# Step 4: Deal Evaluator - Comprehensive evaluation
evaluation = generate_text(
    prompt_id="evaluate_deal",
    variables={
        "negotiated_deal_json": deal.model_dump_json(),
        "financing_report_json": financing.model_dump_json(),
        "fair_market_value": 24500,
        "vehicle_history_summary": "Clean title",
        "safety_recalls_summary": "No recalls",
        "days_on_market": 45
    },
    agent_role="evaluator"
)

# Step 5: QA Agent - Final review
qa_result = generate_structured_json(
    prompt_id="review_final_report",
    variables={
        "deal_evaluation_report": evaluation,
        "vehicle_report_json": vehicles.model_dump_json(),
        "financing_report_json": financing.model_dump_json(),
        "negotiated_deal_json": deal.model_dump_json()
    },
    response_model=QAReport,
    agent_role="qa"
)

# Use final report
if qa_result.is_valid:
    final_report = evaluation
else:
    final_report = qa_result.suggested_revision
```

## API Reference

### LLMClient Class

#### `generate_structured_json()`
Generate validated JSON output with Pydantic model.

**Parameters**:
- `prompt_id` (str): Prompt template identifier
- `variables` (dict): Template variable substitutions
- `response_model` (Type[BaseModel]): Pydantic model for validation
- `temperature` (float): Sampling temperature (0.0-2.0), default 0.7
- `max_tokens` (int, optional): Maximum tokens to generate
- `agent_role` (str, optional): Agent role for specialized prompts

**Returns**: Instance of response_model with validated data

**Raises**: ApiError with appropriate status code

#### `generate_text()`
Generate unstructured text output.

**Parameters**:
- `prompt_id` (str): Prompt template identifier
- `variables` (dict): Template variable substitutions
- `temperature` (float): Sampling temperature (0.0-2.0), default 0.7
- `max_tokens` (int, optional): Maximum tokens to generate
- `agent_role` (str, optional): Agent role for specialized prompts

**Returns**: Generated text string

**Raises**: ApiError with appropriate status code

### Convenience Functions

Module-level functions for direct usage:

```python
from app.llm import generate_structured_json, generate_text

# These are wrappers around llm_client singleton
result = generate_structured_json(...)
text = generate_text(...)
```

## Prompt Management

### Adding New Prompts

1. **Define the prompt in prompts.py**:

```python
PROMPTS["new_agent_task"] = PromptTemplate(
    id="new_agent_task",
    template="""ROLE: [Agent Role]
GOAL: [Clear objective]

TASK DESCRIPTION:
[Detailed instructions]

EXPECTED OUTPUT (JSON/Markdown):
[Schema or format specification]
"""
)
```

2. **Create Pydantic schema in schemas.py** (if JSON output):

```python
class NewAgentResponse(BaseModel):
    """Response from new agent"""
    
    field1: str = Field(..., description="Field description")
    field2: list[str] = Field(..., description="List of items")
```

3. **Export schema from __init__.py**:

```python
from app.llm.schemas import NewAgentResponse

__all__ = [
    # ... existing exports
    "NewAgentResponse",
]
```

4. **Add tests in tests/llm/test_schemas.py**.

### Prompt Best Practices

1. **Clear Structure**: Use consistent sections (ROLE, GOAL, TASK DESCRIPTION, EXPECTED OUTPUT)
2. **Explicit Variables**: Document all template variables with types
3. **JSON Schemas**: Provide exact JSON structure when expecting structured output
4. **Examples**: Include examples for complex formats
5. **Constraints**: Specify any constraints (length, format, required fields)

## Error Handling

The LLM client provides comprehensive error handling:

### Error Types

| Status Code | Error Type | Description |
|-------------|-----------|-------------|
| 400 | Invalid Request | Invalid prompt_id or missing variables |
| 401 | Authentication | Invalid OpenAI API key |
| 429 | Rate Limit | OpenAI rate limit exceeded |
| 500 | Validation Error | Response doesn't match Pydantic schema |
| 500 | JSON Parse Error | Invalid JSON in response |
| 502 | API Error | OpenAI API error |
| 503 | Service Unavailable | OPENAI_API_KEY not configured |
| 504 | Timeout | Request timed out |

### Error Logging

All errors are logged with context:

```python
# Example log output
ERROR: OpenAI authentication error: Invalid API key
ERROR: Response validation failed for DealEvaluation: [validation errors]
ERROR: Failed to parse JSON from LLM response: Expecting value: line 1 column 1 (char 0)
```

### Handling Errors

```python
from app.utils.error_handler import ApiError

try:
    result = generate_structured_json(
        prompt_id="research_vehicles",
        variables={...},
        response_model=VehicleReport,
        agent_role="research"
    )
except ApiError as e:
    logger.error(f"LLM error: {e.message}")
    logger.error(f"Status: {e.status_code}, Details: {e.details}")
    # Handle gracefully
```

## Performance Optimization

### Token Usage

Monitor token usage through logs:

```
INFO: OpenAI tokens: 1523 (prompt: 1200, completion: 323)
```

### Best Practices

1. **Temperature Settings**:
   - 0.0-0.3: Factual, deterministic (evaluations, calculations)
   - 0.4-0.7: Balanced (research, negotiations)
   - 0.8-1.0: Creative (marketing copy, recommendations)

2. **Prompt Optimization**:
   - Be specific and concise
   - Use bullet points for lists
   - Provide clear examples
   - Avoid redundancy

3. **Caching**:
   - Cache vehicle reports for repeat queries
   - Cache financing calculations for same parameters
   - Implement Redis caching for hot data

4. **Batch Processing**:
   - Process multiple evaluations in sequence
   - Use async operations where appropriate (future enhancement)

## Testing

### Unit Testing

```python
from unittest.mock import MagicMock, patch
import pytest

def test_research_agent(mock_openai_client, mock_response):
    """Test research agent with mocked OpenAI"""
    mock_openai_client.chat.completions.create.return_value = mock_response
    
    with patch("app.llm.llm_client.OpenAI", return_value=mock_openai_client):
        client = LLMClient()
        result = client.generate_structured_json(
            prompt_id="research_vehicles",
            variables={...},
            response_model=VehicleReport,
            agent_role="research"
        )
        
        assert isinstance(result, VehicleReport)
```

### Integration Testing

```python
import pytest

@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Requires real OpenAI API key"
)
def test_full_workflow():
    """Test complete multi-agent workflow with real API"""
    # Step 1: Research
    vehicles = generate_structured_json(...)
    
    # Step 2: Financing
    financing = generate_structured_json(...)
    
    # Step 3: Negotiation
    deal = generate_structured_json(...)
    
    # Verify workflow
    assert len(vehicles.top_vehicles) > 0
    assert financing.loan_amount > 0
    assert deal.final_price > 0
```

## Migration Checklist

When migrating from CrewAI:

- [ ] Review agents.yaml and map to agent_role parameters
- [ ] Review tasks.yaml and migrate to PROMPTS dictionary
- [ ] Update all service calls from async to sync
- [ ] Replace crew.kickoff() with explicit agent workflow
- [ ] Update error handling for new ApiError structure
- [ ] Test token usage and optimize prompts
- [ ] Update documentation and examples
- [ ] Train team on new architecture

## Troubleshooting

### Common Issues

**Issue**: "OPENAI_API_KEY not configured"
- **Solution**: Set environment variable or update .env file

**Issue**: "Invalid prompt_id: xyz"
- **Solution**: Check PROMPTS dictionary in prompts.py for valid IDs

**Issue**: "Response validation failed"
- **Solution**: Check Pydantic model matches expected JSON structure

**Issue**: "Failed to parse JSON from LLM response"
- **Solution**: Ensure response_format=json_object is working; check OpenAI API version

**Issue**: High token usage
- **Solution**: Optimize prompts, reduce variable verbosity, use lower temperature

## Future Enhancements

1. **Async Support**: Optional async client for concurrent operations
2. **Streaming**: Support for streaming responses for long-form content
3. **Model Selection**: Dynamic model selection based on task complexity
4. **Prompt Versioning**: Version control for prompt templates
5. **A/B Testing**: Framework for testing prompt variations
6. **Cost Tracking**: Per-agent cost tracking and optimization
7. **Agent Memory**: Context preservation across sessions
8. **Tool Integration**: Agent access to external tools and APIs

## Contributing

When adding new agents or prompts:

1. Follow the established pattern in prompts.py
2. Add comprehensive docstrings
3. Create Pydantic schemas for structured outputs
4. Write unit tests with mocked OpenAI responses
5. Add integration tests (skipped in CI)
6. Document in this guide
7. Update relevant service layer code

## Resources

- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [CrewAI GitHub (Reference)](https://github.com/joaomdmoura/crewai)
- [AutoDealGenie-CrewAI (Original)](https://github.com/Raviteja77/autodealgenie-crewai)
