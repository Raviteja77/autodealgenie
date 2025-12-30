"""Configuration constants for negotiation service"""


class NegotiationConfig:
    """Negotiation-specific configuration constants"""

    # Conversation history
    MAX_CONVERSATION_HISTORY = 4  # Number of recent messages to include in context

    # Financial defaults
    DEFAULT_DOWN_PAYMENT_PERCENT = 0.10  # 10% down payment
    DEFAULT_CREDIT_SCORE_RANGE = "good"  # Default credit range for calculations
    DEFAULT_TARGET_PRICE_RATIO = 0.9  # Default target price ratio (90% of asking price)

    # Negotiation strategy
    INITIAL_OFFER_MULTIPLIER = 0.87  # Start 13% below user target price

    # Counter offer strategy constants
    EXCELLENT_DISCOUNT_THRESHOLD = 10.0  # 10% off asking price
    GOOD_DISCOUNT_THRESHOLD = 5.0  # 5% off asking price
    HOLD_FIRM_ADJUSTMENT = 1.01  # 1% increase when holding firm
    SMALL_INCREASE_ADJUSTMENT = 1.02  # 2% increase for moderate discount
    AGGRESSIVE_DECREASE_ADJUSTMENT = 0.98  # 2% decrease to pressure dealer

    # Session limits
    DEFAULT_MAX_ROUNDS = 10  # Default maximum negotiation rounds

    # Financing options
    DEFAULT_LOAN_TERMS = [36, 48, 60, 72]  # Common loan terms in months

    # AI confidence scoring thresholds
    EXCELLENT_DEAL_DISCOUNT = 15.0  # 15%+ off = excellent
    VERY_GOOD_DEAL_DISCOUNT = 10.0  # 10-15% off = very good
    GOOD_DEAL_DISCOUNT = 5.0  # 5-10% off = good
    FAIR_DEAL_DISCOUNT = 2.0  # 2-5% off = fair
    # <2% off = marginal deal

    # ML model integration weights
    ML_CONFIDENCE_WEIGHT = 0.4  # Weight for ML prediction in blended confidence
    RULE_BASED_WEIGHT = 0.6  # Weight for rule-based confidence

    # WebSocket settings
    TYPING_INDICATOR_ENABLED = True
    BROADCAST_ENABLED = True
