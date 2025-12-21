"""
Lender Recommendation Service

Provides lender recommendations based on user loan criteria including:
- Curated partner lender database
- Credit score-based filtering
- Loan amount and term matching
- Intelligent scoring and ranking
- Privacy-focused affiliate tracking
"""

import logging

from app.schemas.loan_schemas import (
    LenderInfo,
    LenderMatch,
    LenderRecommendationRequest,
    LenderRecommendationResponse,
)
from app.services.loan_calculator_service import LoanCalculatorService

logger = logging.getLogger(__name__)

# Credit score range mappings (midpoint values)
CREDIT_SCORE_RANGES = {
    "excellent": 780,  # 740-850
    "good": 690,  # 670-739
    "fair": 630,  # 580-669
    "poor": 550,  # 300-579
}


class LenderService:
    """Service for recommending trusted partner lenders"""

    # Curated list of partner lenders
    PARTNER_LENDERS = [
        LenderInfo(
            lender_id="capital_auto_finance",
            name="Capital Auto Finance",
            description="Nationwide lender specializing in new and used auto loans with competitive rates for excellent credit",
            logo_url="https://cdn.autodealgenie.com/lenders/capital-auto.png",
            min_credit_score=680,
            max_credit_score=850,
            min_loan_amount=5000.0,
            max_loan_amount=100000.0,
            min_term_months=24,
            max_term_months=84,
            apr_range_min=0.039,  # 3.9%
            apr_range_max=0.079,  # 7.9%
            features=[
                "Pre-approval in minutes",
                "No prepayment penalties",
                "Flexible payment options",
            ],
            benefits=[
                "Same-day funding available",
                "Rate discounts for autopay",
                "Free credit score monitoring",
            ],
            affiliate_url="https://capitalautofin.com/apply",
            referral_code="ADG_CAF_001",
        ),
        LenderInfo(
            lender_id="premier_credit_union",
            name="Premier Credit Union",
            description="Member-focused credit union offering competitive auto loan rates and personalized service",
            logo_url="https://cdn.autodealgenie.com/lenders/premier-cu.png",
            min_credit_score=640,
            max_credit_score=850,
            min_loan_amount=3000.0,
            max_loan_amount=75000.0,
            min_term_months=12,
            max_term_months=72,
            apr_range_min=0.049,  # 4.9%
            apr_range_max=0.099,  # 9.9%
            features=[
                "Local branch support",
                "Skip-a-payment option",
                "GAP insurance available",
            ],
            benefits=[
                "Member dividends and rewards",
                "Free financial counseling",
                "Lower rates for members",
            ],
            affiliate_url="https://premiercu.org/auto-loans",
            referral_code="ADG_PCU_002",
        ),
        LenderInfo(
            lender_id="nationwide_auto_lending",
            name="Nationwide Auto Lending",
            description="Large-scale lender with programs for all credit levels and loan amounts",
            logo_url="https://cdn.autodealgenie.com/lenders/nationwide.png",
            min_credit_score=550,
            max_credit_score=850,
            min_loan_amount=2500.0,
            max_loan_amount=150000.0,
            min_term_months=24,
            max_term_months=96,
            apr_range_min=0.059,  # 5.9%
            apr_range_max=0.169,  # 16.9%
            features=[
                "All credit scores considered",
                "Refinancing options",
                "Extended warranty packages",
            ],
            benefits=[
                "Nationwide dealer network",
                "24/7 online account access",
                "Mobile app for payments",
            ],
            affiliate_url="https://nationwideautolend.com/start",
            referral_code="ADG_NAL_003",
        ),
        LenderInfo(
            lender_id="easydrive_financial",
            name="EasyDrive Financial",
            description="Digital-first lender offering streamlined applications and fast approvals",
            logo_url="https://cdn.autodealgenie.com/lenders/easydrive.png",
            min_credit_score=620,
            max_credit_score=850,
            min_loan_amount=4000.0,
            max_loan_amount=80000.0,
            min_term_months=24,
            max_term_months=75,
            apr_range_min=0.054,  # 5.4%
            apr_range_max=0.119,  # 11.9%
            features=[
                "100% online application",
                "Instant decision technology",
                "Digital document upload",
            ],
            benefits=[
                "No physical paperwork",
                "Fast funding (24-48 hours)",
                "Eco-friendly process",
            ],
            affiliate_url="https://easydrivefinancial.com/apply-now",
            referral_code="ADG_EDF_004",
        ),
        LenderInfo(
            lender_id="second_chance_auto",
            name="Second Chance Auto Finance",
            description="Specialized lender helping customers rebuild credit with auto loans",
            logo_url="https://cdn.autodealgenie.com/lenders/second-chance.png",
            min_credit_score=500,
            max_credit_score=679,
            min_loan_amount=5000.0,
            max_loan_amount=45000.0,
            min_term_months=36,
            max_term_months=72,
            apr_range_min=0.089,  # 8.9%
            apr_range_max=0.189,  # 18.9%
            features=[
                "Credit rebuilding programs",
                "Flexible income verification",
                "Trade-in assistance",
            ],
            benefits=[
                "Improve credit with on-time payments",
                "Graduation to better rates",
                "Financial education resources",
            ],
            affiliate_url="https://secondchanceauto.com/get-started",
            referral_code="ADG_SCA_005",
        ),
        LenderInfo(
            lender_id="military_auto_loans",
            name="Military & Veterans Auto Loans",
            description="Specialized financing for active military, veterans, and their families",
            logo_url="https://cdn.autodealgenie.com/lenders/military-auto.png",
            min_credit_score=600,
            max_credit_score=850,
            min_loan_amount=3000.0,
            max_loan_amount=90000.0,
            min_term_months=24,
            max_term_months=84,
            apr_range_min=0.029,  # 2.9%
            apr_range_max=0.089,  # 8.9%
            features=[
                "Military-exclusive rates",
                "Deployment protection",
                "SCRA benefits included",
            ],
            benefits=[
                "No fees for military members",
                "Flexible deployment options",
                "Dedicated military support team",
            ],
            affiliate_url="https://militaryautoloans.com/apply",
            referral_code="ADG_MAL_006",
        ),
    ]

    @staticmethod
    def _get_credit_score_midpoint(credit_score_range: str) -> int:
        """
        Get the midpoint credit score for a given range

        Args:
            credit_score_range: Credit score range category

        Returns:
            Midpoint credit score value
        """
        return CREDIT_SCORE_RANGES.get(credit_score_range.lower(), 690)

    @staticmethod
    def filter_lenders(
        loan_amount: float,
        credit_score_range: str,
        loan_term_months: int,
    ) -> list[LenderInfo]:
        """
        Filter lenders based on user criteria

        Args:
            loan_amount: Desired loan amount
            credit_score_range: Credit score range category
            loan_term_months: Desired loan term in months

        Returns:
            List of matching lenders
        """
        credit_score = LenderService._get_credit_score_midpoint(credit_score_range)
        matching_lenders = []

        for lender in LenderService.PARTNER_LENDERS:
            # Check if lender accepts this credit score
            if credit_score < lender.min_credit_score or credit_score > lender.max_credit_score:
                continue

            # Check if lender accepts this loan amount
            if loan_amount < lender.min_loan_amount or loan_amount > lender.max_loan_amount:
                continue

            # Check if lender accepts this loan term
            if (
                loan_term_months < lender.min_term_months
                or loan_term_months > lender.max_term_months
            ):
                continue

            matching_lenders.append(lender)

        logger.info(
            f"Filtered {len(matching_lenders)} lenders for "
            f"credit_score={credit_score}, loan_amount=${loan_amount}, "
            f"term={loan_term_months}mo"
        )

        return matching_lenders

    @staticmethod
    def score_lenders(
        lenders: list[LenderInfo],
        loan_amount: float,
        credit_score_range: str,
        loan_term_months: int,
    ) -> list[tuple[LenderInfo, float, str]]:
        """
        Score and rank lenders based on match quality

        Scoring algorithm considers:
        - APR competitiveness (40% weight)
        - Loan amount fit (20% weight)
        - Credit score fit (20% weight)
        - Term flexibility (10% weight)
        - Features and benefits (10% weight)

        Args:
            lenders: List of filtered lenders
            loan_amount: Desired loan amount
            credit_score_range: Credit score range category
            loan_term_months: Desired loan term in months

        Returns:
            List of tuples (lender, score, reason) sorted by score descending
        """
        credit_score = LenderService._get_credit_score_midpoint(credit_score_range)
        scored_lenders = []

        for lender in lenders:
            score = 0.0
            reasons = []

            # 1. APR Competitiveness (40% weight) - lower is better
            apr_midpoint = (lender.apr_range_min + lender.apr_range_max) / 2
            # Best possible score for lowest APR (3%), worst for highest (20%)
            apr_score = max(0, (0.20 - apr_midpoint) / 0.17) * 40
            score += apr_score

            if apr_midpoint < 0.06:
                reasons.append("Excellent rates")
            elif apr_midpoint < 0.10:
                reasons.append("Competitive rates")

            # 2. Loan Amount Fit (20% weight) - how well amount fits their range
            amount_range = lender.max_loan_amount - lender.min_loan_amount
            if amount_range > 0:
                # Prefer lenders where the loan is in the middle of their range
                amount_position = (loan_amount - lender.min_loan_amount) / amount_range
                amount_score = (1 - abs(0.5 - amount_position)) * 20
                score += amount_score

            # 3. Credit Score Fit (20% weight) - how well score fits their range
            credit_range = lender.max_credit_score - lender.min_credit_score
            if credit_range > 0:
                credit_position = (credit_score - lender.min_credit_score) / credit_range
                credit_score_fit = (1 - abs(0.5 - credit_position)) * 20
                score += credit_score_fit

                # Bonus for being in the upper half of their range
                if credit_position > 0.6:
                    reasons.append("Strong credit profile for this lender")

            # 4. Term Flexibility (10% weight)
            term_range = lender.max_term_months - lender.min_term_months
            if term_range > 0:
                term_flexibility_score = min(term_range / 60, 1.0) * 10
                score += term_flexibility_score

            # 5. Features and Benefits (10% weight)
            total_features = len(lender.features) + len(lender.benefits)
            features_score = min(total_features / 6, 1.0) * 10
            score += features_score

            if total_features >= 6:
                reasons.append("Comprehensive features")

            # Special handling for specialized lenders
            if "credit union" in lender.name.lower():
                reasons.append("Member-focused service")
            if "military" in lender.name.lower() or "veterans" in lender.name.lower():
                reasons.append("Military-specialized")
            if (
                "second chance" in lender.name.lower()
                or "credit rebuilding" in lender.description.lower()
            ):
                if credit_score_range in ["fair", "poor"]:
                    score += 5  # Bonus for credit rebuilding specialists
                    reasons.append("Credit rebuilding expertise")

            # Create recommendation reason
            if not reasons:
                reasons.append("Good overall match")
            reason = " • ".join(reasons)

            scored_lenders.append((lender, round(score, 2), reason))

        # Sort by score descending
        scored_lenders.sort(key=lambda x: x[1], reverse=True)

        return scored_lenders

    @staticmethod
    def get_recommendations(
        request: LenderRecommendationRequest, max_results: int = 5
    ) -> LenderRecommendationResponse:
        """
        Get top lender recommendations for user criteria

        Args:
            request: Lender recommendation request with loan criteria
            max_results: Maximum number of recommendations to return

        Returns:
            Lender recommendation response with ranked matches
        """
        # Filter lenders by criteria
        matching_lenders = LenderService.filter_lenders(
            loan_amount=request.loan_amount,
            credit_score_range=request.credit_score_range,
            loan_term_months=request.loan_term_months,
        )

        if not matching_lenders:
            logger.warning(f"No matching lenders for criteria: {request}")
            return LenderRecommendationResponse(
                recommendations=[],
                total_matches=0,
                request_summary={
                    "loan_amount": request.loan_amount,
                    "credit_score_range": request.credit_score_range,
                    "loan_term_months": request.loan_term_months,
                },
            )

        # Score and rank lenders
        scored_lenders = LenderService.score_lenders(
            lenders=matching_lenders,
            loan_amount=request.loan_amount,
            credit_score_range=request.credit_score_range,
            loan_term_months=request.loan_term_months,
        )

        # Build recommendations
        recommendations = []
        for rank, (lender, score, reason) in enumerate(scored_lenders[:max_results], start=1):
            # Estimate APR for this user with this lender
            # Use lender's APR range adjusted for user's credit
            apr_range = lender.apr_range_max - lender.apr_range_min
            credit_score = LenderService._get_credit_score_midpoint(request.credit_score_range)
            credit_normalized = (credit_score - lender.min_credit_score) / (
                lender.max_credit_score - lender.min_credit_score
            )
            # Better credit gets lower APR within lender's range
            estimated_apr = lender.apr_range_max - (credit_normalized * apr_range)
            estimated_apr = round(estimated_apr, 4)

            # Calculate estimated monthly payment
            estimated_payment = LoanCalculatorService.calculate_monthly_payment(
                principal=request.loan_amount,
                annual_rate=estimated_apr,
                term_months=request.loan_term_months,
            )

            recommendations.append(
                LenderMatch(
                    lender=lender,
                    match_score=score,
                    estimated_apr=estimated_apr,
                    estimated_monthly_payment=round(estimated_payment, 2),
                    recommendation_reason=reason,
                    rank=rank,
                )
            )

        logger.info(
            f"Generated {len(recommendations)} recommendations from {len(matching_lenders)} matches"
        )

        return LenderRecommendationResponse(
            recommendations=recommendations,
            total_matches=len(matching_lenders),
            request_summary={
                "loan_amount": request.loan_amount,
                "credit_score_range": request.credit_score_range,
                "loan_term_months": request.loan_term_months,
            },
        )
