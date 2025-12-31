"""
Centralized configuration for negotiation logic and thresholds.
"""


class NegotiationConfig:
    # History and Flow
    MAX_CONVERSATION_HISTORY = 4
    DEFAULT_TARGET_PRICE_RATIO = 0.9  # 90% of asking price
    INITIAL_OFFER_MULTIPLIER = 0.87  # 13% below target price

    # Financing Defaults
    DEFAULT_DOWN_PAYMENT_PERCENT = 0.10
    DEFAULT_CREDIT_SCORE_RANGE = "good"
    DEFAULT_LOAN_TERM_MONTHS = 60

    # Strategy Thresholds
    EXCELLENT_DISCOUNT_THRESHOLD = 10.0  # 10% off asking
    GOOD_DISCOUNT_THRESHOLD = 5.0  # 5% off asking

    # Counter-offer Adjustments
    HOLD_FIRM_ADJUSTMENT = 1.01  # 1% increase
    SMALL_INCREASE_ADJUSTMENT = 1.02  # 2% increase
    AGGRESSIVE_DECREASE_ADJUSTMENT = 0.98  # 2% decrease
