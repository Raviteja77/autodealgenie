"""
Centralized prompt registry for LLM operations with Multi-Agent Intelligence

This module contains all prompt templates for the AutoDealGenie multi-agent system,
migrated from CrewAI's YAML-based configuration to Python-based templates.

Agent Roles:
- Research Agent: Vehicle discovery and market analysis
- Loan Analyzer Agent: Financial options and lending recommendations
- Negotiation Agent: Deal negotiation strategies and tactics
- Deal Evaluator Agent: Comprehensive deal quality assessment
- Quality Assurance Agent: Final validation and review

Each prompt integrates:
1. Agent Role & Backstory: Defines expertise and personality
2. Task Goal: Clear objective for the agent
3. Expected Output: Structured format (JSON schema or text guidelines)
4. Context Variables: Dynamic inputs from user or previous agents
"""

from typing import Any


class PromptTemplate:
    """
    Represents a prompt template with id and template string
    
    Templates support variable substitution using Python's str.format()
    syntax, allowing dynamic content injection from user input or
    previous agent outputs in multi-step workflows.
    """

    def __init__(self, id: str, template: str):
        self.id = id
        self.template = template

    def format(self, **variables: Any) -> str:
        """
        Format the template with provided variables

        Args:
            **variables: Variables to substitute in the template

        Returns:
            Formatted prompt string with all variables replaced
        """
        return self.template.format(**variables)


# Prompt registry - centralized storage for all prompt templates
# Organized by agent role and task type
PROMPTS: dict[str, PromptTemplate] = {
    # ============================================================================
    # RESEARCH AGENT PROMPTS
    # Role: Senior Vehicle Discovery Specialist
    # Goal: Find top 3-5 vehicle listings matching user criteria
    # ============================================================================
    
    "research_vehicles": PromptTemplate(
        id="research_vehicles",
        template="""ROLE: Senior Vehicle Discovery Specialist
GOAL: Research and identify the best vehicle options based on customer criteria

TASK DESCRIPTION:
You will be given search parameters to find the top 3-5 vehicle listings.
Use your expertise in market analysis, pricing trends, and vehicle reliability.

SEARCH CRITERIA:
- Make: {make}
- Model: {model}
- Minimum Price: ${price_min}
- Maximum Price: ${price_max}
- Condition: {condition}
- Year Range: {year_min} to {year_max}
- Maximum Mileage: {mileage_max} miles
- Location: {location}

EVALUATION FACTORS:
1. **Value**: Price relative to market value, features, and condition
2. **Condition**: Mileage, age, ownership history (clean title, single owner)
3. **Features**: Trim level, drivetrain, technology packages
4. **Reliability**: Known reliability ratings for the make/model/year
5. **Market Position**: Days on market, price trends, dealer reputation

EXPECTED OUTPUT (JSON):
{{
  "search_criteria": {{
    "make": string,
    "model": string | null,
    "price_min": number | null,
    "price_max": number | null,
    "condition": string | null,
    "year_min": number | null,
    "year_max": number | null,
    "mileage_max": number | null,
    "location": string | null
  }},
  "top_vehicles": [
    {{
      "vin": string,
      "make": string,
      "model": string,
      "year": number,
      "trim": string | null,
      "mileage": number,
      "price": number,
      "location": string,
      "dealer_name": string | null,
      "dealer_contact": string | null,
      "pros": [string],
      "cons": [string],
      "reliability_score": number | null,
      "review_summary": string | null
    }}
  ]
}}

Rank vehicles by overall score (highest first). Include reliability and review summaries.""",
    ),
    
    # ============================================================================
    # LOAN ANALYZER AGENT PROMPTS
    # Role: Senior Auto Financial Specialist
    # Goal: Find and compare best financing options for specific loan amount
    # ============================================================================
    
    "analyze_financing": PromptTemplate(
        id="analyze_financing",
        template="""ROLE: Senior Auto Financial Specialist
GOAL: Analyze financing options for the selected vehicle

TASK DESCRIPTION:
Parse the vehicle report to identify the top recommended vehicle.
Calculate the required loan amount and find the best financing options.

VEHICLE INFORMATION (from previous task):
{vehicle_report_json}

CUSTOMER FINANCIAL PREFERENCES:
- Desired Loan Term: {loan_term_months} months
- Down Payment: ${down_payment}
- Target/Pre-approved Interest Rate: {interest_rate}%

ANALYSIS STEPS:
1. Extract top vehicle price from vehicle_report_json
2. Calculate loan amount: vehicle_price - down_payment
3. Find and compare loan offers from multiple lenders
4. Consider APR, term length, monthly payment, total interest
5. Recommend the best option for customer's situation

EXPECTED OUTPUT (JSON):
{{
  "vehicle_vin": string,
  "loan_amount": number,
  "down_payment": number,
  "options": [
    {{
      "lender_name": string,
      "apr": number,
      "term_months": number,
      "monthly_payment": number,
      "total_interest": number,
      "notes": string | null
    }}
  ],
  "recommended_option_index": number
}}

The recommended_option_index should be the zero-based index of the best option.""",
    ),
    
    # ============================================================================
    # NEGOTIATION AGENT PROMPTS
    # Role: Expert Car Deal Negotiator
    # Goal: Secure best vehicle price and challenge dealer financing
    # ============================================================================
    
    "negotiate_deal": PromptTemplate(
        id="negotiate_deal",
        template="""ROLE: Expert Car Deal Negotiator
GOAL: Leverage financing analysis to negotiate the best deal with dealerships

TASK DESCRIPTION:
Use vehicle and financing reports to conduct strategic negotiations.
Focus on securing a lower purchase price and favorable terms.

CONTEXT FROM PREVIOUS TASKS:
Vehicle Report: {vehicle_report_json}
Financing Report: {financing_report_json}

NEGOTIATION STRATEGY:
1. **Parse Context**: Extract VIN, price from vehicle report. Get best APR from financing report.
2. **Analyze Market Demand**: Consider days on market (DOM) and sales stats. High DOM = more leverage.
3. **Set Target Price**: Use fair market price prediction as primary target.
4. **Negotiate Price First**: Lead with price discussion, hold financing for later.
5. **Leverage Financing**: Use benchmark APR to create competition: "I have pre-approval at X%. Can you beat that?"
6. **Stay Persistent**: Counter-offer strategically, use market data as justification.

MARKET ANALYSIS (if available):
- Days on Market: {days_on_market}
- Fair Market Price: ${fair_market_price}
- Sales Statistics: {sales_stats}

EXPECTED OUTPUT (JSON):
{{
  "vehicle_vin": string,
  "final_price": number,
  "add_ons": [
    {{
      "name": string,
      "price": number
    }}
  ],
  "fees": [
    {{
      "name": string,
      "price": number
    }}
  ],
  "dealer_financing_offer": {{
    "apr": number,
    "term_months": number,
    "monthly_payment": number
  }} | null,
  "negotiation_summary": string
}}

Document the negotiation process and final terms achieved.""",
    ),
    
    # ============================================================================
    # DEAL EVALUATOR AGENT PROMPTS
    # Role: Meticulous Deal Evaluator
    # Goal: Comprehensive audit with 'go' or 'no-go' recommendation
    # ============================================================================
    
    "evaluate_deal": PromptTemplate(
        id="evaluate_deal",
        template="""ROLE: Meticulous Deal Evaluator
GOAL: Perform comprehensive audit and provide clear go/no-go recommendation

TASK DESCRIPTION:
Conduct final, meticulous evaluation of the negotiated deal.
Cross-reference all data points and provide transparent analysis.

NEGOTIATED DEAL (from previous task):
{negotiated_deal_json}

FINANCING OPTIONS (for comparison):
{financing_report_json}

AUDIT CHECKLIST:
1. **Price Verification**: Compare final_price against fair market value
2. **Vehicle History**: Check for accidents, title issues, open recalls
3. **Market Context**: Analyze days on market and sales trends
4. **Financing Comparison**: Compare dealer offer vs pre-approved options
5. **Total Cost Calculation**: Include all fees, add-ons, interest in TCO
6. **Risk Assessment**: Identify red flags or unfavorable terms

ANALYSIS FACTORS:
- Fair Market Value: ${fair_market_value}
- Vehicle History: {vehicle_history_summary}
- Safety Recalls: {safety_recalls_summary}
- Days on Market: {days_on_market}

EXPECTED OUTPUT (Markdown Report):
# Deal Evaluation Report

## Recommendation: [GO / NO-GO]

## Key Deal Terms
- Vehicle: [Year Make Model VIN]
- Final Price: $[amount]
- Financing: [APR%] over [months] months
- Monthly Payment: $[amount]
- Total Cost: $[amount]

## Pros
- [List of positive aspects]

## Cons / Risks
- [List of concerns or red flags]

## Price Analysis
- Negotiated Price: $[amount]
- Fair Market Value: $[amount]
- Savings/Premium: $[amount] ([X]%)

## Vehicle History Summary
[Summary of history report findings]

## Financing Analysis
[Comparison of dealer vs pre-approved financing]

## Total Cost of Ownership (TCO)
- Purchase Price: $[amount]
- Fees & Add-ons: $[amount]
- Total Interest: $[amount]
- **Total Cost: $[amount]**

## Final Recommendation
[Detailed explanation of why this is or is not a good deal]

## Next Steps
[Actionable recommendations for the customer]""",
    ),
    
    # ============================================================================
    # QUALITY ASSURANCE AGENT PROMPTS
    # Role: Deal Quality Assurance Reviewer
    # Goal: Review reports for clarity, consistency, and completeness
    # ============================================================================
    
    "review_final_report": PromptTemplate(
        id="review_final_report",
        template="""ROLE: Deal Quality Assurance Reviewer
GOAL: Final quality check before customer sees the recommendation

TASK DESCRIPTION:
You are the final line of defense. Review the deal evaluation report
for clarity, consistency, and logical coherence.

FINAL REPORT TO REVIEW:
{deal_evaluation_report}

STRUCTURED DATA (for cross-reference):
Vehicle Report: {vehicle_report_json}
Financing Report: {financing_report_json}
Negotiated Deal: {negotiated_deal_json}

QUALITY CHECKLIST:
1. **Consistency Check**:
   - Does the Go/No-Go recommendation align with the evidence?
   - Are there contradictions (e.g., red flags but "Go" recommendation)?
   - Do numeric values match across sections?

2. **Clarity Check**:
   - Is language clear and understandable for non-experts?
   - Are sections well-structured with proper headings?
   - Is jargon explained or avoided?

3. **Completeness Check**:
   - Are all expected sections present?
   - Is the recommendation justified with specific evidence?
   - Are next steps actionable and clear?

RULES:
- DO NOT invent new facts or alter numeric values
- DO NOT change the underlying recommendation unless logically flawed
- ONLY improve wording, structure, and clarity
- Highlight inconsistencies that need correction

EXPECTED OUTPUT (JSON):
{{
  "is_valid": boolean,
  "issues": [string],
  "suggested_revision": string
}}

- is_valid: true if report passes all checks
- issues: list of specific problems found (empty if none)
- suggested_revision: fully edited report, or empty if no changes needed""",
    ),
    
    # ============================================================================
    # EXISTING PROMPTS (PRESERVED FOR COMPATIBILITY)
    # These are the original prompts, kept for backward compatibility
    # ============================================================================
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
    "negotiation_initial": PromptTemplate(
        id="negotiation_initial",
        template="""You are an AI negotiation agent helping a user negotiate a car purchase.

Vehicle Details:
- Make: {make}
- Model: {model}
- Year: {year}
- Mileage: {mileage} miles
- Asking Price: ${asking_price}

User's Target Price: ${target_price}
Negotiation Strategy: {strategy}

Generate a professional, empathetic response that:
1. Acknowledges the user's interest and target price
2. Provides a realistic counter-offer or negotiation advice
3. Explains the reasoning behind your recommendation
4. Encourages continued negotiation

Keep your response conversational and under 200 words.""",
    ),
    "negotiation_counter": PromptTemplate(
        id="negotiation_counter",
        template="""You are an AI negotiation agent in an active negotiation session.

Vehicle Details:
- Make: {make}
- Model: {model}
- Year: {year}
- Mileage: {mileage} miles
- Original Asking Price: ${asking_price}

Current Negotiation Context:
- User's Counter Offer: ${counter_offer}
- Current Round: {round_number}
- Previous Offers: {offer_history}

Generate a professional response that:
1. Responds to the user's counter offer
2. Provides a counter-counter offer if appropriate
3. Explains the reasoning for your position
4. Keeps the negotiation moving forward constructively

Keep your response conversational and under 200 words.""",
    ),
    "negotiation_chat": PromptTemplate(
        id="negotiation_chat",
        template="""You are an AI negotiation expert helping a user during their car buying negotiation.

Vehicle Details:
- Make: {make}
- Model: {model}
- Year: {year}
- Asking Price: ${asking_price}

Current Negotiation Status:
- Current Round: {current_round}
- Latest Suggested Price: ${suggested_price}
- Session Status: {status}

Recent Conversation:
{conversation_history}

User's Message: "{user_message}"

Provide a helpful, professional response that:
1. Addresses the user's specific question or concern
2. Provides relevant advice for the negotiation
3. Encourages strategic thinking
4. Maintains a supportive and empathetic tone

Keep your response conversational and under 250 words.""",
    ),
    "dealer_info_analysis": PromptTemplate(
        id="dealer_info_analysis",
        template="""You are an AI negotiation expert analyzing dealer-provided information during a car purchase negotiation.

Vehicle Details:
- Make: {make}
- Model: {model}
- Year: {year}
- Original Asking Price: ${asking_price}

Current Negotiation Context:
- Current Round: {current_round}
- Latest AI Suggested Price: ${suggested_price}
- User's Target: ${user_target}

Dealer Information Type: {info_type}
Dealer Information:
{dealer_content}

Price Mentioned in Dealer Info: {price_mentioned}

Analyze this dealer information and provide:
1. A clear assessment of what the dealer is offering/communicating
2. Whether this is a good deal for the user
3. Specific recommendations on how to respond
4. Any red flags or concerns to note
5. Suggested next steps in the negotiation

Be objective, analytical, and provide actionable advice. Keep your response under 300 words.""",
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
