"""
Centralized configuration for deal evaluation logic and thresholds.
"""


class EvaluationConfig:
    """Configuration constants for deal evaluation service."""

    # Scoring and Insights
    MAX_INSIGHTS = 5  # Maximum number of insights/talking points to return

    # Affordability thresholds (payment-to-income ratio percentages)
    AFFORDABILITY_EXCELLENT = 10  # ≤ 10% is excellent
    AFFORDABILITY_GOOD = 15  # ≤ 15% is good
    AFFORDABILITY_MODERATE = 20  # ≤ 20% is moderate

    # Deal quality thresholds
    EXCELLENT_DEAL_SCORE = 8.0  # >= 8.0 is excellent deal
    GOOD_DEAL_SCORE = 6.5  # >= 6.5 is good deal
    LENDER_RECOMMENDATION_MIN_SCORE = 6.5  # Minimum score for lender recommendations

    # Interest rate thresholds for financing recommendations
    LOW_INTEREST_RATE = 4.0  # ≤ 4% is considered low/excellent
    REASONABLE_INTEREST_RATE = 5.0  # ≤ 5% is considered reasonable/good
    HIGH_INTEREST_THRESHOLD = 20  # Interest cost > 20% of purchase price is high

    # Default loan parameters
    DEFAULT_DOWN_PAYMENT_RATIO = 0.2  # 20% down payment
    DEFAULT_LOAN_TERM_MONTHS = 60  # 5-year term

    # Cache settings
    CACHE_TTL = 3600  # Cache evaluation results for 1 hour (in seconds)
    CACHE_KEY_PREFIX = "deal_eval"  # Prefix for cache keys

    # Condition scoring adjustments
    CONDITION_EXCELLENT_BONUS = 1.5
    CONDITION_VERY_GOOD_BONUS = 0.5
    CONDITION_FAIR_PENALTY = -0.5
    CONDITION_POOR_PENALTY = -1.5

    # Mileage thresholds and scoring
    MILEAGE_EXCEPTIONALLY_LOW = 30000  # < 30k miles
    MILEAGE_LOW = 60000  # < 60k miles
    MILEAGE_MODERATE = 100000  # < 100k miles
    MILEAGE_HIGH = 150000  # < 150k miles
    MILEAGE_VERY_HIGH = 150000  # >= 150k miles

    MILEAGE_EXCEPTIONALLY_LOW_BONUS = 1.0
    MILEAGE_LOW_BONUS = 0.5
    MILEAGE_HIGH_PENALTY = -0.5
    MILEAGE_VERY_HIGH_PENALTY = -1.0

    # Price scoring thresholds (percentage differences)
    PRICE_EXCELLENT_DISCOUNT = -15  # 15% or more below market
    PRICE_GREAT_DISCOUNT = -10  # 10-15% below market
    PRICE_GOOD_DISCOUNT = -5  # 5-10% below market
    PRICE_AT_MARKET = 0  # At or slightly below market
    PRICE_SLIGHT_PREMIUM = 5  # 0-5% above market
    PRICE_MODERATE_PREMIUM = 10  # 5-10% above market
    PRICE_HIGH_PREMIUM = 15  # 10-15% above market

    # Price score mappings
    PRICE_SCORE_EXCELLENT = 9.5
    PRICE_SCORE_GREAT = 9.0
    PRICE_SCORE_GOOD = 8.0
    PRICE_SCORE_AT_MARKET = 7.0
    PRICE_SCORE_SLIGHT_PREMIUM = 6.0
    PRICE_SCORE_MODERATE_PREMIUM = 5.0
    PRICE_SCORE_HIGH_PREMIUM = 4.0
    PRICE_SCORE_VERY_HIGH_PREMIUM = 3.0

    # MarketCheck confidence adjustments
    MARKETCHECK_LOW_CONFIDENCE_PENALTY = -0.3

    # Risk scoring
    RISK_BASE_SCORE = 5.0  # Base risk score (1-10, lower is better)
    RISK_HIGH_MILEAGE_THRESHOLD = 100000
    RISK_MODERATE_MILEAGE_THRESHOLD = 75000
    RISK_HIGH_MILEAGE_PENALTY = 1.5
    RISK_MODERATE_MILEAGE_PENALTY = 0.5

    RISK_OLD_AGE_THRESHOLD = 10  # years
    RISK_MODERATE_AGE_THRESHOLD = 7  # years
    RISK_OLD_AGE_PENALTY = 1.0
    RISK_MODERATE_AGE_PENALTY = 0.5

    RISK_INSPECTION_RECOMMENDED_PENALTY = 1.5
    RISK_PRICE_PREMIUM_THRESHOLD = 2000  # dollars
    RISK_PRICE_PREMIUM_PENALTY = 1.0

    RISK_LOW_THRESHOLD = 4.0  # < 4 is low risk
    RISK_MODERATE_THRESHOLD = 7.0  # < 7 is moderate risk

    # Final evaluation weights
    WEIGHT_CONDITION = 0.2  # 20%
    WEIGHT_PRICE = 0.5  # 50%
    WEIGHT_RISK = 0.3  # 30% (inverted)

    # Final score thresholds
    FINAL_HIGHLY_RECOMMENDED = 8.0
    FINAL_RECOMMENDED = 6.5
    FINAL_FAIR = 5.0
