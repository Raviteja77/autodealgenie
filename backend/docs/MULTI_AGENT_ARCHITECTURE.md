# Multi-Agent System Architecture

## Overview

AutoDealGenie uses a sophisticated multi-agent system where specialized AI agents collaborate to guide users through the car-buying process. Each agent has a distinct personality, expertise, and role in the workflow.

## Agent Roles & Personalities

### 1. Vehicle Research Agent (Market Analyst)

**Personality**: Neutral, analytical, data-driven, objective  
**Role**: Market intelligence and vehicle discovery  
**Mission**: Find the best vehicle options through comprehensive market analysis

**Core Expertise**:
- Market Intelligence: Real-time pricing trends, inventory analysis, regional variations
- Hidden Value Detection: Identifying underpriced vehicles through anomaly detection
- Vehicle Scoring & Ranking: Multi-factor algorithms considering value, condition, features, reliability
- Reliability Analytics: Deep knowledge of Consumer Reports, J.D. Power ratings, common issues
- Inventory Curation: Sophisticated matching algorithms prioritizing user preferences

**Key Functions**:
1. Market Scanning: Analyze multiple data sources (dealers, private sales, auctions)
2. Vehicle Discovery: Identify top 3-5 vehicles with optimal value proposition
3. Comparative Analysis: Benchmark against market averages and comparable listings
4. Risk Flagging: Detect pricing anomalies, high mileage, accident indicators, title issues
5. Data Enrichment: Add reliability scores, expert reviews, market positioning, ownership costs

**Output**: Structured JSON with ranked vehicles, pros/cons, reliability scores, review summaries

---

### 2. Loan & Insurance Agent (Trusted Advisor)

**Personality**: Thoughtful, educational, transparent, buyer-focused  
**Role**: Financial counseling and loan analysis  
**Mission**: Help buyers secure best financing while prioritizing long-term financial health

**Core Expertise**:
- Financing Market Intelligence: Current rates, APR ranges by credit tier, seasonal trends
- Loan Structure Analysis: Evaluating terms beyond APR—penalties, rate discounts, flexibility
- Credit Optimization: Credit score improvement guidance, timing strategies, DTI management
- Total Cost Modeling: Calculating total interest, comparing terms, projecting ownership costs
- Lender Matching: Analyzing offerings against buyer's credit profile and goals
- Dealer Financing Analysis: Comparing dealer offers vs. external lenders, detecting markups

**Key Functions**:
1. Financing Options Analysis: Comprehensive guidance on market financing based on credit profile
2. Lender Recommendation Interpretation: When data available, explain APR ranges, match scores, features
3. Monthly Payment Calculation: Accurate payments with affordability stress-testing
4. Interest Cost Transparency: Show total interest paid across different terms and APRs
5. Affordability Assessment: Evaluate fit using DTI ratios and responsible lending guidelines
6. Financing Strategy Development: Recommend optimal loan structure aligned with goals

**Output**: Structured JSON with financing options, affordability assessment, strategy guidance, red flags

---

### 3. Negotiation Agent (Advocate)

**Personality**: Aggressive, strategic, empowering, buyer-loyal  
**Role**: Buyer's champion in price negotiation  
**Mission**: Help buyers achieve LOWEST price and BEST terms through dealer-level intelligence

**Core Expertise**:
- Dealer Psychology & Tactics: Understanding incentives, profit margins, commission structures
- Strategic Pricing: Calculating optimal opening offers, counter-offers, walk-away thresholds
- Negotiation Leverage: Identifying and exploiting leverage points (days on market, external financing)
- Communication Strategies: Crafting persuasive talking points, handling objections, psychological tactics
- Dealer Trap Avoidance: Protecting from 4-square method, yo-yo financing, payment packing, add-ons
- Financing as Leverage: Using pre-approved financing to strengthen position and eliminate markup

**Key Functions**:
1. Strategic Negotiation Planning: Multi-round strategy with price targets, talking points, contingencies
2. Opening Offer Formulation: Aggressive but defensible offers (10-15% below target)
3. Counter-Offer Guidance: Specific dollar amounts and justifications for each round
4. Leverage Identification: Finding and articulating buyer's leverage points
5. Dealer Tactic Defense: Educating on tactics and providing specific counter-responses
6. Add-On & Fee Negotiation: Strategies for declining or negotiating down unnecessary costs
7. Walk-Away Threshold Setting: Defining clear price point where negotiation should stop

**Output**: Structured JSON with target prices, add-on recommendations, fee strategies, comprehensive negotiation summary (400-600 words)

---

### 4. Deal Evaluator Agent (Financial Detective)

**Personality**: Skeptical, thorough, analytical, consumer-focused  
**Role**: Forensic auditor and fraud detector  
**Mission**: Perform comprehensive audit protecting buyers from bad deals and hidden traps

**Core Expertise**:
- Price Validation: Cross-referencing against multiple market data sources (NADA, KBB, Edmunds)
- Fraud Detection: Spotting title washing, odometer rollback, salvage concealment, VIN cloning
- Total Cost Analysis (TCO): Calculating true ownership costs over 5 years
- Fee Auditing: Identifying junk fees, dealer markups, unnecessary add-ons
- Financing Forensics: Analyzing APR vs. effective rate, dealer financing vs. external lenders
- Risk Assessment: Evaluating deal risk factors (condition, pricing, financing, dealer reputation)

**Key Functions**:
1. Comprehensive Deal Audit: Line-by-line review of all components
2. Go/No-Go Recommendation: Clear, evidence-based recommendation with confidence level
3. Hidden Cost Identification: Uncovering costs not immediately obvious
4. Comparative Financing Analysis: Evaluating all options with total cost differences
5. Data Integrity Verification: Validating vehicle history, title status, accident claims
6. Fraud Indicator Detection: Identifying title fraud, odometer tampering, pricing anomalies

**Output**: Detailed markdown report with GO/NO-GO/GO WITH CAUTION recommendation, TCO calculation, financing comparison, risk assessment

---

### 5. Quality Assurance Agent (Validator)

**Personality**: Detail-oriented, systematic, logical, uncompromising on accuracy  
**Role**: Final quality gate before customer delivery  
**Mission**: Ensure every recommendation is accurate, consistent, complete, and clear

**Core Expertise**:
- Logical Consistency Verification: Cross-referencing narrative against structured data
- Completeness Auditing: Ensuring all required sections present, questions answered, gaps identified
- Clarity & Readability Assessment: Evaluating language accessibility for non-expert buyers
- Data Integrity Checking: Validating numeric consistency across all report sections
- Recommendation Coherence: Ensuring Go/No-Go logically follows from evidence
- Risk Flag Validation: Confirming red flags appropriately weighted in final recommendations

**Key Functions**:
1. Consistency Cross-Check: Compare narrative against structured data to detect mismatches
2. Math Verification: Validate all calculations (monthly payments, total interest, TCO, percentages)
3. Clarity Review: Identify confusing language, unexplained jargon, ambiguous statements
4. Completeness Check: Ensure all expected sections exist with proper evidence
5. Logic Audit: Verify conclusions follow logically from evidence—no contradictions
6. Evidence Validation: Confirm every claim supported by data or explicitly marked as estimate

**Output**: Structured JSON with is_valid flag, severity-labeled issues, suggested revision, quality score, recommendations

---

## Agent Coordination & Data Flow

### Sequential Pipeline Architecture

Agents operate in a sequential pipeline where each agent builds upon previous agents' outputs:

```
User Input → Research → Financing → Negotiation → Evaluation → QA → Final Report
```

### Example Usage

```python
from app.llm.agent_coordination import create_vehicle_research_pipeline, DataEnricher

# Create pipeline
pipeline = create_vehicle_research_pipeline()

# Prepare user input
user_input = {
    "make": "Honda",
    "model": "Civic",
    "price_max": 30000,
    "location": "Seattle, WA",
    "down_payment": 5000,
    "loan_term_months": 60,
}

# Execute pipeline
result = pipeline.execute(user_input)

# Access outputs
research = result.research_output
financing = result.financing_output
negotiation = result.negotiation_output
evaluation = result.evaluation_output
qa = result.qa_output
```

For complete documentation, see `/backend/docs/MULTI_AGENT_ARCHITECTURE.md`
