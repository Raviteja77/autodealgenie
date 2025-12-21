# Lender Recommendation Service

## Overview

The Lender Recommendation Service helps users find the best auto loan lenders based on their credit profile and loan requirements. It provides personalized recommendations with estimated rates and payments while maintaining user privacy.

## Features

### Core Functionality

1. **Partner Lender Database**: Curated list of 6 trusted lender partners
2. **Smart Matching**: Filters lenders based on credit score, loan amount, and term
3. **Intelligent Ranking**: Scores lenders using a multi-factor algorithm
4. **Estimated Rates**: Calculates personalized APR estimates for each lender
5. **Payment Calculations**: Provides estimated monthly payments
6. **Affiliate Tracking**: Includes referral codes for commission attribution (no PII)

### Lender Database

The service maintains 6 partner lenders covering different market segments:

1. **Capital Auto Finance** - Excellent credit specialist (680+ credit score)
2. **Premier Credit Union** - Member-focused credit union (640+ credit score)
3. **Nationwide Auto Lending** - All credit levels accepted (550+ credit score)
4. **EasyDrive Financial** - Digital-first lender (620+ credit score)
5. **Second Chance Auto Finance** - Credit rebuilding specialist (500-679 credit score)
6. **Military & Veterans Auto Loans** - Military-exclusive benefits (600+ credit score)

Each lender has:
- Credit score range requirements
- Loan amount limits
- Term length options
- APR ranges
- Features and benefits
- Affiliate tracking URLs

## API Endpoint

### POST `/api/v1/loans/lenders`

Get personalized lender recommendations based on loan criteria.

**Authentication**: Required (JWT token)

**Request Body**:
```json
{
  "loan_amount": 25000.0,
  "credit_score_range": "good",
  "loan_term_months": 60
}
```

**Request Parameters**:
- `loan_amount` (float, required): Desired loan amount (> 0)
- `credit_score_range` (string, required): One of: "excellent", "good", "fair", "poor"
- `loan_term_months` (integer, required): Desired loan term in months (> 0)

**Response**:
```json
{
  "recommendations": [
    {
      "lender": {
        "lender_id": "capital_auto_finance",
        "name": "Capital Auto Finance",
        "description": "Nationwide lender specializing in new and used auto loans...",
        "logo_url": "https://cdn.autodealgenie.com/lenders/capital-auto.png",
        "min_credit_score": 680,
        "max_credit_score": 850,
        "min_loan_amount": 5000.0,
        "max_loan_amount": 100000.0,
        "min_term_months": 24,
        "max_term_months": 84,
        "apr_range_min": 0.039,
        "apr_range_max": 0.079,
        "features": [
          "Pre-approval in minutes",
          "No prepayment penalties",
          "Flexible payment options"
        ],
        "benefits": [
          "Same-day funding available",
          "Rate discounts for autopay",
          "Free credit score monitoring"
        ],
        "affiliate_url": "https://capitalautofin.com/apply",
        "referral_code": "ADG_CAF_001"
      },
      "match_score": 86.67,
      "estimated_apr": 0.0555,
      "estimated_monthly_payment": 573.73,
      "recommendation_reason": "Excellent rates • Comprehensive features",
      "rank": 1
    }
  ],
  "total_matches": 5,
  "request_summary": {
    "loan_amount": 25000.0,
    "credit_score_range": "good",
    "loan_term_months": 60
  }
}
```

**Response Fields**:
- `recommendations`: Array of up to 5 recommended lenders (sorted by rank)
  - `lender`: Lender information and details
  - `match_score`: Match quality score (0-100)
  - `estimated_apr`: Personalized APR estimate (as decimal)
  - `estimated_monthly_payment`: Estimated monthly payment amount
  - `recommendation_reason`: Explanation of why lender is recommended
  - `rank`: Ranking position (1 = best match)
- `total_matches`: Total number of lenders matching criteria
- `request_summary`: Echo of request parameters

## Ranking Algorithm

The service uses a weighted scoring algorithm to rank lenders:

### Scoring Factors (Total: 100 points)

1. **APR Competitiveness (40%)**: Lower rates score higher
2. **Loan Amount Fit (20%)**: How well the loan amount fits lender's range
3. **Credit Score Fit (20%)**: How well user's credit fits lender's range
4. **Term Flexibility (10%)**: Range of terms offered by lender
5. **Features & Benefits (10%)**: Number and quality of lender features

### Special Considerations

- **Credit Rebuilding Specialists**: Get bonus points for fair/poor credit
- **Credit Unions**: Highlighted for member-focused service
- **Military Lenders**: Flagged for military-exclusive benefits
- **Credit Position**: Bonus for being in upper half of lender's range

## Credit Score Ranges

The service maps credit score categories to midpoint values:

| Category  | Range     | Midpoint | Typical APR Range |
|-----------|-----------|----------|-------------------|
| Excellent | 740-850   | 780      | 3.9% - 5.9%       |
| Good      | 670-739   | 690      | 5.9% - 8.9%       |
| Fair      | 580-669   | 630      | 8.9% - 11.9%      |
| Poor      | 300-579   | 550      | 11.9% - 18.9%     |

## Privacy & Tracking

### Anonymous Tracking

The service includes affiliate tracking for commission attribution while maintaining user privacy:

- **Referral Codes**: Unique codes identify traffic source (e.g., `ADG_CAF_001`)
- **Affiliate URLs**: Direct links to lender applications
- **No PII**: No personally identifiable information is included in tracking
- **User Consent**: Users see where they're being redirected
- **Transparency**: Clear disclosure of affiliate partnerships

### What's NOT Tracked

- User names, emails, or contact information
- Social security numbers or financial account data
- Browsing history or behavioral data
- Device identifiers or IP addresses

### What IS Tracked (by lenders, not us)

- Clicks from AutoDealGenie to lender sites
- Anonymous conversion events (application started/completed)
- Aggregate statistics for performance reporting

## Usage Examples

### Example 1: Excellent Credit

```python
request = LenderRecommendationRequest(
    loan_amount=30000.0,
    credit_score_range="excellent",
    loan_term_months=60
)
response = LenderService.get_recommendations(request, max_results=5)
```

Expected results:
- 5-6 lender matches
- APR estimates: 4-8%
- Monthly payments: ~$550-$615
- Top lenders: Capital Auto Finance, Military & Veterans Auto Loans

### Example 2: Poor Credit

```python
request = LenderRecommendationRequest(
    loan_amount=15000.0,
    credit_score_range="poor",
    loan_term_months=48
)
response = LenderService.get_recommendations(request, max_results=5)
```

Expected results:
- 2-3 lender matches
- APR estimates: 14-19%
- Monthly payments: ~$420-$435
- Top lenders: Second Chance Auto Finance, Nationwide Auto Lending

### Example 3: Large Loan, Good Credit

```python
request = LenderRecommendationRequest(
    loan_amount=50000.0,
    credit_score_range="good",
    loan_term_months=72
)
response = LenderService.get_recommendations(request, max_results=3)
```

Expected results:
- 4-5 lender matches
- APR estimates: 6-9%
- Monthly payments: ~$840-$895
- Top lenders: Military & Veterans Auto Loans, Capital Auto Finance

## Testing

### Unit Tests

Run the comprehensive test suite:

```bash
cd backend
pytest tests/test_lender_service.py -v
```

Coverage: 99% of lender_service.py code

Test coverage includes:
- Credit score midpoint calculation
- Lender filtering by all criteria
- Scoring and ranking algorithm
- Recommendation generation
- Data quality validation
- Edge cases and boundary conditions

### Manual Testing

Run the manual test script to see real output:

```bash
cd backend
python tests/manual_test_lender_service.py
```

This will show:
- Sample recommendations for different scenarios
- Detailed lender information
- Data quality validation results

## Service Architecture

### Components

1. **LenderService** (`app/services/lender_service.py`)
   - Core service class
   - Static methods for filtering, scoring, and recommendations
   - Partner lender database

2. **Schemas** (`app/schemas/loan_schemas.py`)
   - `LenderInfo`: Lender details and criteria
   - `LenderRecommendationRequest`: Request parameters
   - `LenderMatch`: Recommendation with score and details
   - `LenderRecommendationResponse`: Complete response

3. **API Endpoint** (`app/api/v1/endpoints/loans.py`)
   - POST `/api/v1/loans/lenders`
   - Authentication required
   - Request validation
   - Error handling

### Data Flow

```
User Request
    ↓
API Endpoint (validate & authenticate)
    ↓
LenderService.get_recommendations()
    ↓
filter_lenders() → Matching lenders
    ↓
score_lenders() → Ranked lenders
    ↓
Calculate APR & payments for each
    ↓
Return top N recommendations
    ↓
API Response to user
```

## Maintenance

### Adding New Lenders

To add a new partner lender:

1. Create a `LenderInfo` object in `LenderService.PARTNER_LENDERS`
2. Ensure all required fields are populated
3. Use realistic APR ranges and criteria
4. Add unique lender_id and referral_code
5. Run tests to validate data quality

Example:
```python
LenderInfo(
    lender_id="new_lender_bank",
    name="New Lender Bank",
    description="Description of services...",
    logo_url="https://cdn.autodealgenie.com/lenders/new-lender.png",
    min_credit_score=600,
    max_credit_score=850,
    min_loan_amount=5000.0,
    max_loan_amount=75000.0,
    min_term_months=24,
    max_term_months=72,
    apr_range_min=0.059,
    apr_range_max=0.119,
    features=["Feature 1", "Feature 2", "Feature 3"],
    benefits=["Benefit 1", "Benefit 2", "Benefit 3"],
    affiliate_url="https://newlenderbank.com/apply",
    referral_code="ADG_NLB_007",
)
```

### Updating APR Ranges

APR ranges should be reviewed quarterly to ensure competitiveness:

1. Research current market rates
2. Update `apr_range_min` and `apr_range_max` for affected lenders
3. Run tests to ensure ranges are realistic
4. Document changes in version control

### Monitoring & Analytics

Track key metrics:
- Click-through rates by lender
- Conversion rates (applications started)
- User feedback on recommendations
- APR estimate accuracy vs actual rates
- Match quality scores distribution

## Future Enhancements

Planned improvements:

1. **Real-time Rate Updates**: API integration with lenders for live rates
2. **More Lenders**: Expand database to 15-20 partners
3. **Regional Preferences**: Filter by state availability
4. **Pre-qualification**: Soft credit pull for pre-approval
5. **Application Tracking**: Track user applications through funnel
6. **A/B Testing**: Test ranking algorithm variations
7. **Machine Learning**: Improve matching based on historical data
8. **User Feedback**: Collect ratings on lender recommendations

## Support

For questions or issues:
- Review test cases in `tests/test_lender_service.py`
- Check manual test output for debugging
- Verify lender data quality with validation checks
- Contact development team for API integration issues

## License

This feature is part of the AutoDealGenie application.
