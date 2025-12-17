"""
Centralized prompt registry for LLM operations
"""

from typing import Any


class PromptTemplate:
    """Represents a prompt template with id and template string"""

    def __init__(self, id: str, template: str):
        self.id = id
        self.template = template

    def format(self, **variables: Any) -> str:
        """
        Format the template with provided variables

        Args:
            **variables: Variables to substitute in the template

        Returns:
            Formatted prompt string
        """
        return self.template.format(**variables)


# Prompt registry - centralized storage for all prompt templates
PROMPTS: dict[str, PromptTemplate] = {
    "car_recommendation": PromptTemplate(
        id="car_recommendation",
        template="""You are an expert automotive advisor helping users find their ideal vehicle.

User Preferences:
- Budget: ${budget}
- Body Type: {body_type}
- Preferred Makes: {preferred_makes}
- Required Features: {required_features}
- Usage: {usage_type}

Based on these preferences, recommend 3-5 vehicles that would be a great fit.
For each vehicle, include:
1. Make and Model
2. Estimated Price Range
3. Key Features
4. Why it matches their needs
5. Potential considerations or trade-offs

Provide practical, actionable recommendations tailored to the user's specific needs.""",
    ),
    "negotiation": PromptTemplate(
        id="negotiation",
        template="""You are an expert automotive negotiation advisor.

Vehicle Details:
- Make: {make}
- Model: {model}
- Year: {year}
- Asking Price: ${asking_price}
- Mileage: {mileage} miles
- Condition: {condition}

Market Context:
- Fair Market Value: ${fair_value}
- Deal Score: {score}/10

Provide a negotiation strategy including:
1. Opening offer recommendation
2. Key talking points to justify lower price
3. Common dealer tactics to watch for
4. Walk-away price threshold
5. Additional value items to negotiate (warranty, maintenance, etc.)

Be specific with dollar amounts and actionable strategies.""",
    ),
    "evaluation": PromptTemplate(
        id="evaluation",
        template="""You are an expert automotive pricing analyst.

Vehicle Details:
- VIN: {vin}
- Make: {make}
- Model: {model}
- Year: {year}
- Mileage: {mileage} miles
- Condition: {condition}
- Asking Price: ${asking_price}

Provide a comprehensive evaluation in JSON format with:
{{
  "fair_value": <estimated fair market value>,
  "score": <deal quality score 1-10>,
  "insights": [<3-5 key observations>],
  "talking_points": [<3-5 specific negotiation strategies>]
}}

Base your analysis on:
- Current market conditions
- Vehicle age and mileage
- Condition assessment
- Comparable vehicle pricing
- Regional market factors

Be objective and data-driven in your assessment.""",
    ),
    "deal_summary": PromptTemplate(
        id="deal_summary",
        template="""Generate a concise deal summary for this automotive transaction:

Deal Information:
{deal_data}

Create a professional summary (2-3 paragraphs) that includes:
1. Vehicle overview
2. Pricing analysis
3. Deal highlights
4. Recommended next steps

Keep the tone informative and helpful.""",
    ),
    "vehicle_comparison": PromptTemplate(
        id="vehicle_comparison",
        template="""Compare these vehicles and help the user make an informed decision:

Vehicle A:
{vehicle_a}

Vehicle B:
{vehicle_b}

Provide a side-by-side comparison covering:
1. Value proposition
2. Features and capabilities
3. Reliability and ownership costs
4. Resale value considerations
5. Which vehicle better suits: {user_needs}

Conclude with a recommendation based on the user's specific needs.""",
    ),
    "car_selection_from_list": PromptTemplate(
        id="car_selection_from_list",
        template="""You are an expert automotive advisor helping customers find their ideal vehicle.

Your role is to:
1. Analyze the provided vehicle listings.
2. Evaluate each vehicle based on multiple factors: value, condition, features, mileage, and reliability.
3. Select the top 5 vehicles that best match the user's criteria.
4. Provide clear reasoning for each recommendation.

User Criteria:
{user_criteria}

Available Vehicles:
{listings_summary}

Evaluation Criteria:
- **Value**: Price relative to market value, features, and condition
- **Condition**: Mileage, age, ownership history (clean title, single owner)
- **Features**: Trim level, drivetrain, technology packages
- **Reliability**: Known reliability ratings for the make/model/year
- **Market Position**: Days on market, price trends, dealer reputation

Select exactly 5 vehicles and rank them by score (highest first). Be specific with highlights and summaries.""",
    ),
}


def get_prompt(prompt_id: str) -> PromptTemplate:
    """
    Retrieve a prompt template by ID

    Args:
        prompt_id: Unique identifier for the prompt

    Returns:
        PromptTemplate object

    Raises:
        KeyError: If prompt_id is not found in registry
    """
    if prompt_id not in PROMPTS:
        available_prompts = ", ".join(PROMPTS.keys())
        raise KeyError(f"Prompt '{prompt_id}' not found. Available prompts: {available_prompts}")
    return PROMPTS[prompt_id]


def list_prompts() -> list[str]:
    """
    List all available prompt IDs

    Returns:
        List of prompt IDs
    """
    return list(PROMPTS.keys())
