# Migration Guide: CrewAI to Custom LLM Client

## Overview

This guide provides step-by-step instructions for migrating from CrewAI's orchestration framework to AutoDealGenie's custom multi-agent LLM system.

## Table of Contents

1. [Why Migrate?](#why-migrate)
2. [Key Differences](#key-differences)
3. [Migration Steps](#migration-steps)
4. [Code Examples](#code-examples)
5. [Testing Changes](#testing-changes)
6. [Troubleshooting](#troubleshooting)

## Why Migrate?

### Advantages of Custom LLM Client

1. **Simpler Architecture**: Synchronous client reduces complexity
2. **Better Control**: Direct API access allows fine-tuning
3. **Cost Optimization**: Explicit token usage tracking
4. **Easier Debugging**: Clear error messages and logging
5. **Flexibility**: Easy to customize and extend
6. **Production Ready**: Less dependencies, easier deployment

### Trade-offs

- **No Built-in Orchestration**: Manual workflow management
- **Explicit Context Passing**: Must handle agent-to-agent data flow
- **More Boilerplate**: Service layer requires more code

## Key Differences

### Configuration

**Before (CrewAI)**:
```yaml
# agents.yaml
car_researcher:
  role: Senior Vehicle Discovery Specialist
  goal: Find top vehicles matching criteria
  backstory: Expert automotive researcher...

# tasks.yaml
research_vehicles:
  description: Research and identify best vehicles
  expected_output: JSON object with vehicle list
```

**After (Custom Client)**:
```python
# prompts.py
PROMPTS["research_vehicles"] = PromptTemplate(
    id="research_vehicles",
    template="""ROLE: Senior Vehicle Discovery Specialist
GOAL: Find top vehicles matching criteria

TASK DESCRIPTION:
Research and identify best vehicles...

EXPECTED OUTPUT (JSON):
{
  "top_vehicles": [...]
}
"""
)
```

### Client Usage

**Before (CrewAI)**:
```python
from crewai import Agent, Task, Crew

# Define agent
researcher = Agent(
    role='Senior Vehicle Discovery Specialist',
    goal='Find top vehicles',
    backstory='Expert automotive researcher...',
    verbose=True
)

# Define task
research_task = Task(
    description='Research vehicles with {make} {model}...',
    expected_output='JSON object',
    agent=researcher
)

# Create crew and execute
crew = Crew(
    agents=[researcher],
    tasks=[research_task],
    verbose=True
)

result = crew.kickoff(inputs={"make": "Honda", "model": "Civic"})
```

**After (Custom Client)**:
```python
from app.llm import generate_structured_json
from app.llm.schemas import VehicleReport

# Direct API call with agent role
result = generate_structured_json(
    prompt_id="research_vehicles",
    variables={"make": "Honda", "model": "Civic"},
    response_model=VehicleReport,
    agent_role="research"
)
```

### Async vs Sync

**Before (CrewAI)**:
```python
# Async crew execution
result = await crew.kickoff_async(inputs=...)
```

**After (Custom Client)**:
```python
# Synchronous execution
result = generate_structured_json(...)
```

### Error Handling

**Before (CrewAI)**:
```python
try:
    result = crew.kickoff(inputs=...)
except Exception as e:
    # Generic exception handling
    logger.error(f"Crew execution failed: {e}")
```

**After (Custom Client)**:
```python
from app.utils.error_handler import ApiError

try:
    result = generate_structured_json(...)
except ApiError as e:
    # Specific error types with status codes
    if e.status_code == 429:
        # Rate limit - retry with backoff
        pass
    elif e.status_code == 500:
        # Validation error - log details
        logger.error(f"Validation failed: {e.details}")
```

## Migration Steps

### Step 1: Inventory Your Agents

List all CrewAI agents in your application:

```bash
# In CrewAI repo
cat src/autodealgenie/config/agents.yaml
```

Map each agent to the new system:

| CrewAI Agent | New Agent Role | Prompt ID |
|--------------|---------------|-----------|
| car_researcher | research | research_vehicles |
| loan_analyzer | loan | analyze_financing |
| negotiation_agent | negotiation | negotiate_deal |
| deal_evaluator | evaluator | evaluate_deal |
| quality_assurance_agent | qa | review_final_report |

### Step 2: Migrate Prompts

For each task in `tasks.yaml`:

1. **Extract key components**:
   - Description
   - Input variables
   - Expected output format
   - Context from previous tasks

2. **Create PromptTemplate** in `prompts.py`:

```python
PROMPTS["your_task_id"] = PromptTemplate(
    id="your_task_id",
    template="""ROLE: [From agents.yaml]
GOAL: [From agents.yaml]

TASK DESCRIPTION:
[From tasks.yaml description]

INPUT VARIABLES:
- variable1: {variable1}
- variable2: {variable2}

EXPECTED OUTPUT (JSON):
{
  "field1": "value",
  "field2": []
}
"""
)
```

### Step 3: Create Pydantic Schemas

For each structured output:

```python
# schemas.py
class YourTaskResponse(BaseModel):
    """Response from your task"""
    
    field1: str = Field(..., description="Description")
    field2: list[str] = Field(..., description="List of items")
    
    class Config:
        json_schema_extra = {
            "example": {
                "field1": "example value",
                "field2": ["item1", "item2"]
            }
        }
```

### Step 4: Update Service Layer

Replace CrewAI crew execution with direct LLM calls:

**Before**:
```python
# service.py
from crewai import Crew

class VehicleResearchService:
    def research_vehicles(self, make: str, model: str):
        crew = Crew(agents=[...], tasks=[...])
        result = crew.kickoff(inputs={"make": make, "model": model})
        return result
```

**After**:
```python
# service.py
from app.llm import generate_structured_json
from app.llm.schemas import VehicleReport

class VehicleResearchService:
    def research_vehicles(self, make: str, model: str) -> VehicleReport:
        result = generate_structured_json(
            prompt_id="research_vehicles",
            variables={"make": make, "model": model},
            response_model=VehicleReport,
            agent_role="research"
        )
        return result
```

### Step 5: Handle Multi-Agent Workflows

CrewAI automatically passes context between tasks. With the custom client, you must do this explicitly:

**Before (CrewAI)**:
```python
# CrewAI handles context automatically
crew = Crew(
    agents=[researcher, loan_analyzer, negotiator],
    tasks=[research_task, analyze_task, negotiate_task],
    process=Process.sequential
)
result = crew.kickoff(inputs=initial_input)
```

**After (Custom Client)**:
```python
# Explicit context passing
# Step 1: Research
vehicles = generate_structured_json(
    prompt_id="research_vehicles",
    variables={"make": "Honda"},
    response_model=VehicleReport,
    agent_role="research"
)

# Step 2: Financing (uses research output)
financing = generate_structured_json(
    prompt_id="analyze_financing",
    variables={
        "vehicle_report_json": vehicles.model_dump_json(),
        "loan_term_months": 60,
        "down_payment": 5000
    },
    response_model=FinancingReport,
    agent_role="loan"
)

# Step 3: Negotiation (uses both previous outputs)
deal = generate_structured_json(
    prompt_id="negotiate_deal",
    variables={
        "vehicle_report_json": vehicles.model_dump_json(),
        "financing_report_json": financing.model_dump_json()
    },
    response_model=NegotiatedDeal,
    agent_role="negotiation"
)
```

### Step 6: Update Tests

Replace CrewAI test mocks with OpenAI mocks:

**Before (CrewAI)**:
```python
@patch('crewai.Crew.kickoff')
def test_research(mock_kickoff):
    mock_kickoff.return_value = {...}
    service = VehicleResearchService()
    result = service.research_vehicles("Honda", "Civic")
    assert result is not None
```

**After (Custom Client)**:
```python
from unittest.mock import MagicMock, patch
import json

def test_research(mock_openai_client, mock_response):
    # Setup mock
    mock_response.choices[0].message.content = json.dumps({
        "top_vehicles": [...]
    })
    mock_openai_client.chat.completions.create.return_value = mock_response
    
    with patch("app.llm.llm_client.OpenAI", return_value=mock_openai_client):
        service = VehicleResearchService()
        result = service.research_vehicles("Honda", "Civic")
        
        assert isinstance(result, VehicleReport)
        assert len(result.top_vehicles) > 0
```

### Step 7: Update Dependencies

```bash
# Remove CrewAI
pip uninstall crewai crewai-tools

# Ensure OpenAI is installed
pip install openai==1.6.1
```

Update `requirements.txt`:
```diff
- crewai==0.x.x
- crewai-tools==0.x.x
+ # Already included: openai==1.6.1
```

### Step 8: Update Configuration

**Before (.env)**:
```bash
# CrewAI configuration
OPENAI_API_KEY=your-key
CREWAI_LOG_LEVEL=INFO
CREWAI_VERBOSE=True
```

**After (.env)**:
```bash
# Custom LLM client configuration
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo
LOG_LEVEL=INFO
```

## Code Examples

### Example 1: Simple Agent Call

**CrewAI**:
```python
from crewai import Agent, Task, Crew

agent = Agent(
    role="Pricing Analyst",
    goal="Analyze vehicle pricing",
    backstory="Expert in automotive pricing...",
)

task = Task(
    description="Analyze price of {vin}",
    agent=agent,
    expected_output="Price analysis report"
)

crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff(inputs={"vin": "12345"})
```

**Custom Client**:
```python
from app.llm import generate_text

result = generate_text(
    prompt_id="price_analysis",
    variables={"vin": "12345"},
    agent_role="evaluator"
)
```

### Example 2: Structured JSON Output

**CrewAI**:
```python
task = Task(
    description="Find vehicles",
    expected_output="""JSON object:
    {
      "vehicles": [...]
    }""",
    agent=researcher
)

result = crew.kickoff()
data = json.loads(result.raw)  # Manual parsing
```

**Custom Client**:
```python
from app.llm import generate_structured_json
from app.llm.schemas import VehicleReport

result = generate_structured_json(
    prompt_id="research_vehicles",
    variables={...},
    response_model=VehicleReport,  # Automatic validation
    agent_role="research"
)

# result is already a validated Pydantic model
print(result.top_vehicles[0].make)
```

### Example 3: Error Handling

**CrewAI**:
```python
try:
    result = crew.kickoff()
except Exception as e:
    # Limited error context
    logger.error(f"Crew failed: {e}")
    return None
```

**Custom Client**:
```python
from app.utils.error_handler import ApiError

try:
    result = generate_structured_json(...)
except ApiError as e:
    # Rich error context
    if e.status_code == 429:
        logger.warning("Rate limited, retrying...")
        time.sleep(int(e.details.get('retry_after', 60)))
        result = generate_structured_json(...)
    elif e.status_code == 500:
        logger.error(f"Validation failed: {e.details['validation_errors']}")
        return None
    else:
        raise
```

### Example 4: Sequential Workflow

**CrewAI**:
```python
crew = Crew(
    agents=[agent1, agent2, agent3],
    tasks=[task1, task2, task3],
    process=Process.sequential
)
result = crew.kickoff()  # Tasks execute in sequence
```

**Custom Client**:
```python
# Step 1
result1 = generate_structured_json(
    prompt_id="task1",
    variables={...},
    response_model=Task1Output,
    agent_role="agent1"
)

# Step 2 (uses result1)
result2 = generate_structured_json(
    prompt_id="task2",
    variables={"context": result1.model_dump_json()},
    response_model=Task2Output,
    agent_role="agent2"
)

# Step 3 (uses result1 and result2)
result3 = generate_structured_json(
    prompt_id="task3",
    variables={
        "context1": result1.model_dump_json(),
        "context2": result2.model_dump_json()
    },
    response_model=Task3Output,
    agent_role="agent3"
)
```

## Testing Changes

### Unit Testing

Create fixtures for OpenAI mocks:

```python
# conftest.py
import pytest
from unittest.mock import MagicMock
import json

@pytest.fixture
def mock_openai_client():
    """Mock synchronous OpenAI client"""
    return MagicMock()

@pytest.fixture
def mock_json_response():
    """Mock OpenAI response with JSON content"""
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_usage = MagicMock()
    
    mock_message.content = json.dumps({"key": "value"})
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_usage.total_tokens = 100
    mock_response.usage = mock_usage
    
    return mock_response
```

### Integration Testing

Mark integration tests that require real API:

```python
@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Requires OpenAI API key"
)
def test_real_workflow():
    """Test with real OpenAI API"""
    result = generate_structured_json(...)
    assert result is not None
```

Run tests:
```bash
# Unit tests only (fast)
pytest -m "not integration"

# All tests including integration
pytest
```

## Troubleshooting

### Issue: Import Errors

**Problem**: `ModuleNotFoundError: No module named 'crewai'`

**Solution**: Remove old imports:
```python
# Remove these
from crewai import Agent, Task, Crew, Process
from crewai_tools import Tool

# Add these
from app.llm import generate_structured_json, generate_text
from app.llm.schemas import YourSchema
```

### Issue: Async/Await Errors

**Problem**: `SyntaxError: 'await' outside async function`

**Solution**: Remove async/await:
```python
# Before
async def my_function():
    result = await generate_structured_json(...)
    
# After
def my_function():
    result = generate_structured_json(...)
```

### Issue: Context Not Passed

**Problem**: Agent doesn't have access to previous agent's output

**Solution**: Explicitly pass context:
```python
# Pass previous output as JSON string
result2 = generate_structured_json(
    prompt_id="task2",
    variables={
        "previous_result": result1.model_dump_json()
    },
    response_model=Task2Output,
    agent_role="agent2"
)
```

### Issue: Validation Errors

**Problem**: `Response validation failed`

**Solution**: Check Pydantic model matches JSON structure:
```python
# Log raw response to debug
try:
    result = generate_structured_json(...)
except ApiError as e:
    logger.error(f"Raw content: {e.details.get('raw_content')}")
    logger.error(f"Validation errors: {e.details.get('validation_errors')}")
```

### Issue: Rate Limits

**Problem**: `OpenAI API rate limit exceeded`

**Solution**: Implement retry with exponential backoff:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60)
)
def resilient_call():
    return generate_structured_json(...)
```

## Performance Considerations

### Token Usage

Monitor and optimize:

```python
# Log token usage per call
# Output: "OpenAI tokens: 1523 (prompt: 1200, completion: 323)"

# Optimize prompts to reduce tokens
# - Remove redundancy
# - Use concise language
# - Limit context length
```

### Temperature Settings

Choose appropriately:

```python
# Factual/Deterministic (0.0-0.3)
evaluation = generate_structured_json(
    ...,
    temperature=0.2,  # Consistent evaluations
    agent_role="evaluator"
)

# Balanced (0.4-0.7)
research = generate_structured_json(
    ...,
    temperature=0.7,  # Default
    agent_role="research"
)

# Creative (0.8-1.0)
marketing = generate_text(
    ...,
    temperature=0.9,  # Varied recommendations
    agent_role="research"
)
```

## Rollback Plan

If migration fails, you can rollback:

1. **Restore CrewAI dependencies**:
   ```bash
   git checkout main
   pip install -r requirements.txt
   ```

2. **Keep both systems** during transition:
   ```python
   # Feature flag
   USE_CREWAI = os.getenv("USE_CREWAI", "false").lower() == "true"
   
   if USE_CREWAI:
       result = crew.kickoff(...)
   else:
       result = generate_structured_json(...)
   ```

## Success Checklist

- [ ] All agents mapped to new system
- [ ] All prompts migrated to prompts.py
- [ ] Pydantic schemas created for structured outputs
- [ ] Service layer updated with direct LLM calls
- [ ] Multi-agent workflows handle context explicitly
- [ ] Tests updated with OpenAI mocks
- [ ] CrewAI dependencies removed
- [ ] Configuration updated (.env)
- [ ] Documentation updated
- [ ] Team trained on new architecture
- [ ] Performance baseline established
- [ ] Error monitoring configured
- [ ] Rollback plan documented

## Next Steps

After successful migration:

1. **Optimize Prompts**: A/B test variations
2. **Add Monitoring**: Track token usage and costs
3. **Enhance Error Handling**: Custom retry logic
4. **Add Caching**: Cache common responses
5. **Document Patterns**: Create team playbook
6. **Train Team**: Workshop on new system

## Resources

- [Multi-Agent LLM Guide](./MULTI_AGENT_LLM_GUIDE.md) - Complete system documentation
- [OpenAI API Docs](https://platform.openai.com/docs/api-reference) - API reference
- [Pydantic Docs](https://docs.pydantic.dev/) - Schema validation
- [CrewAI Repo](https://github.com/Raviteja77/autodealgenie-crewai) - Original implementation for reference

## Support

For questions or issues:

1. Check [Troubleshooting](#troubleshooting) section
2. Review [Multi-Agent LLM Guide](./MULTI_AGENT_LLM_GUIDE.md)
3. Check logs for detailed error messages
4. Create GitHub issue with error details
