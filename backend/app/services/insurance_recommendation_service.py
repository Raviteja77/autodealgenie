"""
Insurance Recommendation Service

Provides insurance recommendations based on vehicle and driver criteria including:
- Curated partner insurance provider database
- Vehicle value and age-based filtering
- Coverage type matching
- Intelligent scoring and ranking
- Privacy-focused affiliate tracking (no PII collected)
"""

import logging

from app.schemas.insurance_schemas import (
    InsuranceMatch,
    InsuranceProviderInfo,
    InsuranceRecommendationRequest,
    InsuranceRecommendationResponse,
)

logger = logging.getLogger(__name__)

# Coverage type multipliers for premium calculation
COVERAGE_MULTIPLIERS = {
    "liability": 1.0,  # Base rate
    "comprehensive": 1.5,  # 50% more than liability
    "full": 2.0,  # Double liability
}

# Vehicle age depreciation factors
VEHICLE_AGE_FACTORS = {
    0: 1.3,  # New cars cost more to insure
    1: 1.2,
    2: 1.1,
    3: 1.0,  # Sweet spot
    4: 0.95,
    5: 0.9,
    10: 0.8,  # Older cars
}

# Driver age risk factors
DRIVER_AGE_FACTORS = {
    16: 2.5,  # Highest risk
    18: 2.0,
    21: 1.5,
    25: 1.0,  # Standard rate
    35: 0.95,
    50: 0.9,  # Lowest risk
    65: 1.0,
    75: 1.2,  # Increased risk for seniors
}

# Scoring algorithm constants
MAX_PREMIUM_FOR_SCORING = 500.0  # Maximum monthly premium for scoring
MIN_PREMIUM_FOR_SCORING = 50.0  # Minimum monthly premium for scoring
PREMIUM_SCORING_RANGE = MAX_PREMIUM_FOR_SCORING - MIN_PREMIUM_FOR_SCORING

# Scoring weights (must sum to 100)
WEIGHT_PREMIUM_COMPETITIVENESS = 40
WEIGHT_COVERAGE_FIT = 25
WEIGHT_VEHICLE_VALUE_FIT = 20
WEIGHT_FEATURES_BENEFITS = 15

# Scoring bonuses
BONUS_COMPREHENSIVE_COVERAGE = 5  # Bonus for comprehensive coverage options


class InsuranceRecommendationService:
    """Service for recommending trusted partner insurance providers"""

    # Curated list of partner insurance providers
    PARTNER_PROVIDERS = [
        InsuranceProviderInfo(
            provider_id="safeguard_auto_insurance",
            name="SafeGuard Auto Insurance",
            description="Nationwide provider offering comprehensive coverage with competitive rates for all driver profiles",
            logo_url=None,
            coverage_types=["liability", "comprehensive", "full"],
            min_vehicle_value=5000.0,
            max_vehicle_value=150000.0,
            min_driver_age=18,
            max_driver_age=85,
            premium_range_min=75.0,
            premium_range_max=350.0,
            features=[
                "24/7 claims support",
                "Roadside assistance included",
                "Accident forgiveness",
            ],
            benefits=[
                "Multi-car discounts",
                "Safe driver rewards",
                "Mobile app for claims",
            ],
            affiliate_url="https://www.progressive.com/auto/",
            referral_code="ADG_SAI_001",
        ),
        InsuranceProviderInfo(
            provider_id="premium_shield_insurance",
            name="Premium Shield Insurance",
            description="Premium coverage for high-value vehicles with personalized service and luxury repair options",
            logo_url=None,
            coverage_types=["comprehensive", "full"],
            min_vehicle_value=30000.0,
            max_vehicle_value=250000.0,
            min_driver_age=25,
            max_driver_age=80,
            premium_range_min=150.0,
            premium_range_max=500.0,
            features=[
                "Original parts guarantee",
                "Concierge claims service",
                "Rental car upgrade options",
            ],
            benefits=[
                "Premium loaner vehicles",
                "Custom coverage options",
                "Diminishing deductible",
            ],
            affiliate_url="https://www.statefarm.com/insurance/auto",
            referral_code="ADG_PSI_002",
        ),
        InsuranceProviderInfo(
            provider_id="value_coverage_insurance",
            name="Value Coverage Insurance",
            description="Budget-friendly insurance focusing on liability and basic coverage for cost-conscious drivers",
            logo_url=None,
            coverage_types=["liability", "comprehensive"],
            min_vehicle_value=2000.0,
            max_vehicle_value=50000.0,
            min_driver_age=18,
            max_driver_age=90,
            premium_range_min=50.0,
            premium_range_max=200.0,
            features=[
                "Online account management",
                "Flexible payment plans",
                "Quick quote process",
            ],
            benefits=[
                "No hidden fees",
                "Low down payment",
                "Month-to-month options",
            ],
            affiliate_url="https://www.geico.com/auto-insurance/",
            referral_code="ADG_VCI_003",
        ),
        InsuranceProviderInfo(
            provider_id="family_first_insurance",
            name="Family First Insurance",
            description="Family-focused coverage with multi-vehicle and teen driver programs",
            logo_url=None,
            coverage_types=["liability", "comprehensive", "full"],
            min_vehicle_value=5000.0,
            max_vehicle_value=100000.0,
            min_driver_age=16,
            max_driver_age=95,
            premium_range_min=80.0,
            premium_range_max=300.0,
            features=[
                "Teen driver monitoring",
                "Multi-vehicle discounts",
                "Good student discounts",
            ],
            benefits=[
                "Family claim assistance",
                "Educational resources",
                "Safe driving rewards",
            ],
            affiliate_url="https://www.allstate.com/auto-insurance",
            referral_code="ADG_FFI_004",
        ),
        InsuranceProviderInfo(
            provider_id="senior_safe_insurance",
            name="Senior Safe Insurance",
            description="Specialized coverage for mature drivers with age-appropriate rates and services",
            logo_url=None,
            coverage_types=["liability", "comprehensive", "full"],
            min_vehicle_value=5000.0,
            max_vehicle_value=80000.0,
            min_driver_age=55,
            max_driver_age=100,
            premium_range_min=70.0,
            premium_range_max=250.0,
            features=[
                "Mature driver discounts",
                "Simplified claims process",
                "Personal claims advocate",
            ],
            benefits=[
                "No age-based rate increases",
                "Retired driver discounts",
                "Defensive driving rewards",
            ],
            affiliate_url="https://www.aarp.org/auto-insurance/",
            referral_code="ADG_SSI_005",
        ),
        InsuranceProviderInfo(
            provider_id="green_driver_insurance",
            name="Green Driver Insurance",
            description="Eco-friendly coverage with special rates for hybrid and electric vehicles",
            logo_url=None,
            coverage_types=["liability", "comprehensive", "full"],
            min_vehicle_value=10000.0,
            max_vehicle_value=120000.0,
            min_driver_age=21,
            max_driver_age=85,
            premium_range_min=85.0,
            premium_range_max=320.0,
            features=[
                "EV/Hybrid discounts",
                "Low mileage rewards",
                "Carbon offset program",
            ],
            benefits=[
                "Green repair options",
                "Paperless policy management",
                "Sustainable practices rewards",
            ],
            affiliate_url="https://www.libertymutual.com/auto-insurance",
            referral_code="ADG_GDI_006",
        ),
    ]

    @staticmethod
    def _get_vehicle_age_factor(vehicle_age: int) -> float:
        """
        Get the insurance rate factor based on vehicle age

        Args:
            vehicle_age: Age of vehicle in years

        Returns:
            Rate factor (1.0 is baseline)
        """
        # Find the closest age bracket
        if vehicle_age <= 0:
            return VEHICLE_AGE_FACTORS[0]
        elif vehicle_age >= 10:
            return VEHICLE_AGE_FACTORS[10]
        else:
            return VEHICLE_AGE_FACTORS.get(vehicle_age, 1.0)

    @staticmethod
    def _get_driver_age_factor(driver_age: int) -> float:
        """
        Get the insurance rate factor based on driver age

        Args:
            driver_age: Age of driver

        Returns:
            Rate factor (1.0 is baseline)
        """
        # Find the closest age bracket
        if driver_age <= 16:
            return DRIVER_AGE_FACTORS[16]
        elif driver_age >= 75:
            return DRIVER_AGE_FACTORS[75]
        elif driver_age >= 65:
            return DRIVER_AGE_FACTORS[65]
        elif driver_age >= 50:
            return DRIVER_AGE_FACTORS[50]
        elif driver_age >= 35:
            return DRIVER_AGE_FACTORS[35]
        elif driver_age >= 25:
            return DRIVER_AGE_FACTORS[25]
        elif driver_age >= 21:
            return DRIVER_AGE_FACTORS[21]
        elif driver_age >= 18:
            return DRIVER_AGE_FACTORS[18]
        else:
            return DRIVER_AGE_FACTORS[16]

    @staticmethod
    def filter_providers(
        vehicle_value: float,
        coverage_type: str,
        driver_age: int,
    ) -> list[InsuranceProviderInfo]:
        """
        Filter insurance providers based on user criteria

        Args:
            vehicle_value: Vehicle value
            coverage_type: Desired coverage type
            driver_age: Driver age

        Returns:
            List of matching insurance providers
        """
        matching_providers = []

        for provider in InsuranceRecommendationService.PARTNER_PROVIDERS:
            # Check if provider accepts this vehicle value
            if (
                vehicle_value < provider.min_vehicle_value
                or vehicle_value > provider.max_vehicle_value
            ):
                continue

            # Check if provider accepts this driver age
            if driver_age < provider.min_driver_age or driver_age > provider.max_driver_age:
                continue

            # Check if provider offers this coverage type
            if coverage_type not in provider.coverage_types:
                continue

            matching_providers.append(provider)

        logger.info(
            f"Filtered {len(matching_providers)} insurance providers for "
            f"vehicle_value=${vehicle_value}, coverage={coverage_type}, "
            f"driver_age={driver_age}"
        )

        return matching_providers

    @staticmethod
    def calculate_estimated_premium(
        provider: InsuranceProviderInfo,
        vehicle_value: float,
        vehicle_age: int,
        coverage_type: str,
        driver_age: int,
    ) -> float:
        """
        Calculate estimated monthly premium for a provider

        Args:
            provider: Insurance provider info
            vehicle_value: Vehicle value
            vehicle_age: Vehicle age in years
            coverage_type: Coverage type
            driver_age: Driver age

        Returns:
            Estimated monthly premium
        """
        # Start with provider's midpoint premium
        midpoint_premium = (provider.premium_range_min + provider.premium_range_max) / 2
        range_width = provider.premium_range_max - provider.premium_range_min

        # Apply coverage type multiplier
        coverage_multiplier = COVERAGE_MULTIPLIERS.get(coverage_type, 1.0)

        # Apply vehicle age factor
        vehicle_age_factor = InsuranceRecommendationService._get_vehicle_age_factor(vehicle_age)

        # Apply driver age factor
        driver_age_factor = InsuranceRecommendationService._get_driver_age_factor(driver_age)

        # Calculate vehicle value factor (higher value = higher premium)
        # Normalize to a reasonable range
        value_factor = 1.0 + (vehicle_value / 100000.0) * 0.3  # Up to 30% increase

        # Combine all factors with scaling to stay within range
        combined_factor = (
            coverage_multiplier * vehicle_age_factor * driver_age_factor * value_factor
        )

        # Calculate deviation from midpoint based on combined factor
        # Scale the deviation to use only a portion of the available range
        deviation = (combined_factor - 1.0) * range_width * 0.4  # Use 40% of range for variation
        estimated_premium = midpoint_premium + deviation

        # Ensure premium is within provider's range
        estimated_premium = max(
            provider.premium_range_min, min(provider.premium_range_max, estimated_premium)
        )

        return round(estimated_premium, 2)

    @staticmethod
    def score_providers(
        providers: list[InsuranceProviderInfo],
        vehicle_value: float,
        vehicle_age: int,
        coverage_type: str,
        driver_age: int,
    ) -> list[tuple[InsuranceProviderInfo, float, float, str]]:
        """
        Score and rank insurance providers based on match quality

        Scoring algorithm considers:
        - Premium competitiveness (40% weight)
        - Coverage fit (25% weight)
        - Vehicle value fit (20% weight)
        - Features and benefits (15% weight)

        Args:
            providers: List of filtered providers
            vehicle_value: Vehicle value
            vehicle_age: Vehicle age in years
            coverage_type: Desired coverage type
            driver_age: Driver age

        Returns:
            List of tuples (provider, score, premium, reason) sorted by score descending
        """
        scored_providers = []

        for provider in providers:
            score = 0.0
            reasons = []

            # Calculate estimated premium for this provider
            estimated_premium = InsuranceRecommendationService.calculate_estimated_premium(
                provider=provider,
                vehicle_value=vehicle_value,
                vehicle_age=vehicle_age,
                coverage_type=coverage_type,
                driver_age=driver_age,
            )

            # 1. Premium Competitiveness (40% weight) - lower is better
            premium_score = (
                max(
                    0,
                    (MAX_PREMIUM_FOR_SCORING - estimated_premium) / PREMIUM_SCORING_RANGE,
                )
                * WEIGHT_PREMIUM_COMPETITIVENESS
            )
            score += premium_score

            if estimated_premium < 100:
                reasons.append("Excellent rates")
            elif estimated_premium < 200:
                reasons.append("Competitive pricing")

            # 2. Coverage Fit (25% weight)
            coverage_score = 0
            if coverage_type in provider.coverage_types:
                # Give higher score if they specialize in this coverage
                if len(provider.coverage_types) == 1:
                    coverage_score = WEIGHT_COVERAGE_FIT  # Specialist
                else:
                    coverage_score = WEIGHT_COVERAGE_FIT * 0.8  # Generalist
            score += coverage_score

            # Bonus for comprehensive coverage options
            if len(provider.coverage_types) >= 3:
                score += BONUS_COMPREHENSIVE_COVERAGE
                reasons.append("Comprehensive coverage options")

            # 3. Vehicle Value Fit (20% weight)
            value_range = provider.max_vehicle_value - provider.min_vehicle_value
            if value_range > 0:
                # Prefer providers where vehicle value is in the middle of their range
                value_position = (vehicle_value - provider.min_vehicle_value) / value_range
                value_score = (1 - abs(0.5 - value_position)) * WEIGHT_VEHICLE_VALUE_FIT
                score += value_score

            # 4. Features and Benefits (15% weight)
            total_features = len(provider.features) + len(provider.benefits)
            features_score = min(total_features / 6, 1.0) * WEIGHT_FEATURES_BENEFITS
            score += features_score

            if total_features >= 6:
                reasons.append("Rich feature set")

            # Special handling for specialized providers
            if "senior" in provider.name.lower() and driver_age >= 55:
                reasons.append("Senior driver specialist")
            if "teen" in provider.description.lower() and driver_age < 21:
                reasons.append("Young driver programs")
            if "family" in provider.name.lower():
                reasons.append("Family-focused benefits")
            if "green" in provider.name.lower() or "eco" in provider.description.lower():
                reasons.append("Eco-friendly options")

            # Create recommendation reason
            if not reasons:
                reasons.append("Good overall match")
            reason = " • ".join(reasons)

            scored_providers.append((provider, round(score, 2), estimated_premium, reason))

        # Sort by score descending
        scored_providers.sort(key=lambda x: x[1], reverse=True)

        return scored_providers

    @staticmethod
    def get_recommendations(
        request: InsuranceRecommendationRequest,
        max_results: int = 5,
        user_id: int | None = None,
        deal_id: int | None = None,
        db_session=None,
    ) -> InsuranceRecommendationResponse:
        """
        Get top insurance provider recommendations for user criteria

        Args:
            request: Insurance recommendation request with vehicle and driver criteria
            max_results: Maximum number of recommendations to return
            user_id: Optional user ID for storing recommendations
            deal_id: Optional deal ID for associating recommendations
            db_session: Optional database session for storing recommendations

        Returns:
            Insurance recommendation response with ranked matches
        """
        # Filter providers by criteria
        matching_providers = InsuranceRecommendationService.filter_providers(
            vehicle_value=request.vehicle_value,
            coverage_type=request.coverage_type,
            driver_age=request.driver_age,
        )

        if not matching_providers:
            logger.warning(f"No matching insurance providers for criteria: {request}")
            return InsuranceRecommendationResponse(
                recommendations=[],
                total_matches=0,
                request_summary={
                    "vehicle_value": request.vehicle_value,
                    "vehicle_age": request.vehicle_age,
                    "coverage_type": request.coverage_type,
                    "driver_age": request.driver_age,
                },
            )

        # Score and rank providers
        scored_providers = InsuranceRecommendationService.score_providers(
            providers=matching_providers,
            vehicle_value=request.vehicle_value,
            vehicle_age=request.vehicle_age,
            coverage_type=request.coverage_type,
            driver_age=request.driver_age,
        )

        # Build recommendations
        recommendations = []
        for rank, (provider, score, monthly_premium, reason) in enumerate(
            scored_providers[:max_results], start=1
        ):
            annual_premium = monthly_premium * 12

            recommendations.append(
                InsuranceMatch(
                    provider=provider,
                    match_score=score,
                    estimated_monthly_premium=round(monthly_premium, 2),
                    estimated_annual_premium=round(annual_premium, 2),
                    recommendation_reason=reason,
                    rank=rank,
                )
            )

        # Store recommendations in PostgreSQL if user and deal IDs are provided
        if user_id and deal_id and db_session:
            from app.repositories.insurance_recommendation_repository import InsuranceRecommendationRepository
            
            insurance_repo = InsuranceRecommendationRepository(db_session)
            
            for rec in recommendations:
                try:
                    insurance_repo.create(
                        deal_id=deal_id,
                        user_id=user_id,
                        vehicle_value=request.vehicle_value,
                        vehicle_age=request.vehicle_age,
                        coverage_type=request.coverage_type,
                        driver_age=request.driver_age,
                        provider_id=rec.provider.provider_id,
                        provider_name=rec.provider.name,
                        match_score=rec.match_score,
                        estimated_monthly_premium=rec.estimated_monthly_premium,
                        estimated_annual_premium=rec.estimated_annual_premium,
                        recommendation_reason=rec.recommendation_reason,
                        rank=rec.rank,
                        full_recommendation_data={
                            "provider": rec.provider.dict(),
                            "request": request.dict(),
                        },
                    )
                    logger.info(
                        f"Stored insurance recommendation for deal {deal_id}, "
                        f"provider {rec.provider.name}, rank {rec.rank}"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to store insurance recommendation for deal {deal_id}: {str(e)}"
                    )
                    # Don't fail the main operation if storage fails

        logger.info(
            f"Generated {len(recommendations)} recommendations from {len(matching_providers)} matches"
        )

        return InsuranceRecommendationResponse(
            recommendations=recommendations,
            total_matches=len(matching_providers),
            request_summary={
                "vehicle_value": request.vehicle_value,
                "vehicle_age": request.vehicle_age,
                "vehicle_make": request.vehicle_make,
                "vehicle_model": request.vehicle_model,
                "coverage_type": request.coverage_type,
                "driver_age": request.driver_age,
            },
        )
