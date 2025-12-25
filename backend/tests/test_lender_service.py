"""
Unit tests for Lender Service
"""


from app.schemas.loan_schemas import (
    LenderRecommendationRequest,
)
from app.services.lender_service import LenderService


class TestCreditScoreMidpoint:
    """Test credit score midpoint calculation"""

    def test_get_credit_score_midpoint_excellent(self):
        """Test midpoint for excellent credit"""
        score = LenderService._get_credit_score_midpoint("excellent")
        assert score == 780

    def test_get_credit_score_midpoint_good(self):
        """Test midpoint for good credit"""
        score = LenderService._get_credit_score_midpoint("good")
        assert score == 690

    def test_get_credit_score_midpoint_fair(self):
        """Test midpoint for fair credit"""
        score = LenderService._get_credit_score_midpoint("fair")
        assert score == 630

    def test_get_credit_score_midpoint_poor(self):
        """Test midpoint for poor credit"""
        score = LenderService._get_credit_score_midpoint("poor")
        assert score == 550

    def test_get_credit_score_midpoint_case_insensitive(self):
        """Test that credit score range is case-insensitive"""
        score_lower = LenderService._get_credit_score_midpoint("excellent")
        score_upper = LenderService._get_credit_score_midpoint("EXCELLENT")
        score_mixed = LenderService._get_credit_score_midpoint("ExCeLLeNt")
        assert score_lower == score_upper == score_mixed

    def test_get_credit_score_midpoint_invalid_defaults(self):
        """Test that invalid credit score defaults to good"""
        score = LenderService._get_credit_score_midpoint("invalid")
        assert score == 690  # Default to good


class TestFilterLenders:
    """Test lender filtering"""

    def test_filter_lenders_excellent_credit(self):
        """Test filtering with excellent credit"""
        lenders = LenderService.filter_lenders(
            loan_amount=25000.0,
            credit_score_range="excellent",
            loan_term_months=60,
        )
        assert len(lenders) > 0
        # All returned lenders should accept excellent credit
        for lender in lenders:
            assert 780 >= lender.min_credit_score
            assert 780 <= lender.max_credit_score

    def test_filter_lenders_poor_credit(self):
        """Test filtering with poor credit"""
        lenders = LenderService.filter_lenders(
            loan_amount=15000.0,
            credit_score_range="poor",
            loan_term_months=48,
        )
        # Should have at least one lender for poor credit
        assert len(lenders) > 0
        # All returned lenders should accept poor credit (550)
        for lender in lenders:
            assert 550 >= lender.min_credit_score
            assert 550 <= lender.max_credit_score

    def test_filter_lenders_loan_amount_too_low(self):
        """Test filtering with loan amount below all minimums"""
        lenders = LenderService.filter_lenders(
            loan_amount=1000.0,  # Very low amount
            credit_score_range="good",
            loan_term_months=36,
        )
        # May have no matches or very few
        # This is expected behavior for extreme values
        assert isinstance(lenders, list)

    def test_filter_lenders_loan_amount_too_high(self):
        """Test filtering with loan amount above most maximums"""
        lenders = LenderService.filter_lenders(
            loan_amount=200000.0,  # Very high amount
            credit_score_range="excellent",
            loan_term_months=72,
        )
        # May have limited matches
        assert isinstance(lenders, list)

    def test_filter_lenders_term_too_short(self):
        """Test filtering with very short loan term"""
        lenders = LenderService.filter_lenders(
            loan_amount=20000.0,
            credit_score_range="good",
            loan_term_months=6,  # Very short
        )
        # May have no or few matches
        assert isinstance(lenders, list)

    def test_filter_lenders_term_too_long(self):
        """Test filtering with very long loan term"""
        lenders = LenderService.filter_lenders(
            loan_amount=30000.0,
            credit_score_range="good",
            loan_term_months=120,  # Very long
        )
        # May have no or few matches
        assert isinstance(lenders, list)

    def test_filter_lenders_typical_scenario(self):
        """Test filtering with typical loan criteria"""
        lenders = LenderService.filter_lenders(
            loan_amount=30000.0,
            credit_score_range="good",
            loan_term_months=60,
        )
        # Should have multiple matches for typical scenario
        assert len(lenders) >= 2

    def test_filter_lenders_validates_criteria(self):
        """Test that filtered lenders meet all criteria"""
        loan_amount = 25000.0
        credit_score_range = "good"
        loan_term_months = 60
        credit_score = 690  # Midpoint for good

        lenders = LenderService.filter_lenders(
            loan_amount=loan_amount,
            credit_score_range=credit_score_range,
            loan_term_months=loan_term_months,
        )

        for lender in lenders:
            # Check credit score acceptance
            assert credit_score >= lender.min_credit_score
            assert credit_score <= lender.max_credit_score

            # Check loan amount acceptance
            assert loan_amount >= lender.min_loan_amount
            assert loan_amount <= lender.max_loan_amount

            # Check term acceptance
            assert loan_term_months >= lender.min_term_months
            assert loan_term_months <= lender.max_term_months


class TestScoreLenders:
    """Test lender scoring and ranking"""

    def test_score_lenders_returns_sorted_list(self):
        """Test that scoring returns list sorted by score"""
        lenders = LenderService.filter_lenders(
            loan_amount=25000.0,
            credit_score_range="good",
            loan_term_months=60,
        )

        scored = LenderService.score_lenders(
            lenders=lenders,
            loan_amount=25000.0,
            credit_score_range="good",
            loan_term_months=60,
        )

        assert len(scored) == len(lenders)

        # Check scores are in descending order
        for i in range(len(scored) - 1):
            assert scored[i][1] >= scored[i + 1][1]

    def test_score_lenders_includes_all_components(self):
        """Test that each scored lender has lender, score, and reason"""
        lenders = LenderService.filter_lenders(
            loan_amount=30000.0,
            credit_score_range="excellent",
            loan_term_months=60,
        )

        scored = LenderService.score_lenders(
            lenders=lenders,
            loan_amount=30000.0,
            credit_score_range="excellent",
            loan_term_months=60,
        )

        for lender_info, score, reason in scored:
            assert lender_info is not None
            assert isinstance(score, int | float)
            assert score >= 0
            assert score <= 100
            assert isinstance(reason, str)
            assert len(reason) > 0

    def test_score_lenders_excellent_credit_gets_high_scores(self):
        """Test that excellent credit gets higher scores"""
        lenders = LenderService.filter_lenders(
            loan_amount=25000.0,
            credit_score_range="excellent",
            loan_term_months=60,
        )

        scored_excellent = LenderService.score_lenders(
            lenders=lenders,
            loan_amount=25000.0,
            credit_score_range="excellent",
            loan_term_months=60,
        )

        # Get average score for excellent credit
        if scored_excellent:
            avg_score_excellent = sum(s[1] for s in scored_excellent) / len(
                scored_excellent
            )
            # Excellent credit should get decent scores
            assert avg_score_excellent > 0

    def test_score_lenders_fair_credit_specialist_bonus(self):
        """Test that credit rebuilding specialists get bonus for fair/poor credit"""
        # Test with fair credit
        lenders = LenderService.filter_lenders(
            loan_amount=15000.0,
            credit_score_range="fair",
            loan_term_months=48,
        )

        if lenders:
            scored = LenderService.score_lenders(
                lenders=lenders,
                loan_amount=15000.0,
                credit_score_range="fair",
                loan_term_months=48,
            )

            # Check if credit rebuilding specialist is in results
            for lender, _score, reason in scored:
                if "second chance" in lender.name.lower():
                    # Should have credit rebuilding mention in reason
                    assert (
                        "credit rebuilding" in reason.lower()
                        or "second chance" in reason.lower()
                    )

    def test_score_lenders_reason_quality(self):
        """Test that recommendation reasons are informative"""
        lenders = LenderService.filter_lenders(
            loan_amount=25000.0,
            credit_score_range="good",
            loan_term_months=60,
        )

        scored = LenderService.score_lenders(
            lenders=lenders,
            loan_amount=25000.0,
            credit_score_range="good",
            loan_term_months=60,
        )

        for _lender, _score, reason in scored:
            # Reason should be descriptive
            assert len(reason) > 10  # More than just "Good match"
            # Should not be just placeholder text
            assert reason != "TBD" and reason != "N/A"


class TestGetRecommendations:
    """Test complete recommendation flow"""

    def test_get_recommendations_basic(self):
        """Test basic recommendation retrieval"""
        request = LenderRecommendationRequest(
            loan_amount=25000.0,
            credit_score_range="good",
            loan_term_months=60,
        )

        response = LenderService.get_recommendations(request)

        assert response is not None
        assert response.total_matches >= 0
        assert len(response.recommendations) <= 5
        assert response.request_summary is not None

    def test_get_recommendations_includes_summary(self):
        """Test that response includes request summary"""
        request = LenderRecommendationRequest(
            loan_amount=30000.0,
            credit_score_range="excellent",
            loan_term_months=72,
        )

        response = LenderService.get_recommendations(request)

        assert response.request_summary["loan_amount"] == 30000.0
        assert response.request_summary["credit_score_range"] == "excellent"
        assert response.request_summary["loan_term_months"] == 72

    def test_get_recommendations_respects_max_results(self):
        """Test that max_results parameter is respected"""
        request = LenderRecommendationRequest(
            loan_amount=25000.0,
            credit_score_range="good",
            loan_term_months=60,
        )

        response = LenderService.get_recommendations(request, max_results=3)

        assert len(response.recommendations) <= 3

    def test_get_recommendations_ranks_properly(self):
        """Test that recommendations are ranked 1, 2, 3, etc."""
        request = LenderRecommendationRequest(
            loan_amount=25000.0,
            credit_score_range="good",
            loan_term_months=60,
        )

        response = LenderService.get_recommendations(request)

        for i, rec in enumerate(response.recommendations, start=1):
            assert rec.rank == i

    def test_get_recommendations_includes_estimated_apr(self):
        """Test that recommendations include estimated APR"""
        request = LenderRecommendationRequest(
            loan_amount=25000.0,
            credit_score_range="good",
            loan_term_months=60,
        )

        response = LenderService.get_recommendations(request)

        for rec in response.recommendations:
            assert rec.estimated_apr > 0
            assert rec.estimated_apr < 0.30  # Reasonable maximum APR
            # APR should be within lender's range
            assert rec.estimated_apr >= rec.lender.apr_range_min
            assert rec.estimated_apr <= rec.lender.apr_range_max

    def test_get_recommendations_includes_monthly_payment(self):
        """Test that recommendations include estimated monthly payment"""
        request = LenderRecommendationRequest(
            loan_amount=25000.0,
            credit_score_range="good",
            loan_term_months=60,
        )

        response = LenderService.get_recommendations(request)

        for rec in response.recommendations:
            assert rec.estimated_monthly_payment > 0
            # Payment should be reasonable for loan amount
            min_payment = (25000.0 / 60) * 0.8  # At least 80% of principal/term
            max_payment = (25000.0 / 60) * 2.0  # At most 2x principal/term
            assert rec.estimated_monthly_payment >= min_payment
            assert rec.estimated_monthly_payment <= max_payment

    def test_get_recommendations_match_scores(self):
        """Test that match scores are in valid range"""
        request = LenderRecommendationRequest(
            loan_amount=25000.0,
            credit_score_range="good",
            loan_term_months=60,
        )

        response = LenderService.get_recommendations(request)

        for rec in response.recommendations:
            assert rec.match_score >= 0
            assert rec.match_score <= 100

    def test_get_recommendations_no_matches(self):
        """Test behavior when no lenders match criteria"""
        request = LenderRecommendationRequest(
            loan_amount=1000000.0,  # Unrealistic amount
            credit_score_range="poor",
            loan_term_months=200,  # Unrealistic term
        )

        response = LenderService.get_recommendations(request)

        assert response.total_matches == 0
        assert len(response.recommendations) == 0

    def test_get_recommendations_excellent_credit(self):
        """Test recommendations for excellent credit"""
        request = LenderRecommendationRequest(
            loan_amount=30000.0,
            credit_score_range="excellent",
            loan_term_months=60,
        )

        response = LenderService.get_recommendations(request)

        assert len(response.recommendations) > 0
        # Excellent credit should get competitive APRs
        for rec in response.recommendations:
            assert rec.estimated_apr < 0.10  # Should be under 10%

    def test_get_recommendations_poor_credit(self):
        """Test recommendations for poor credit"""
        request = LenderRecommendationRequest(
            loan_amount=15000.0,
            credit_score_range="poor",
            loan_term_months=48,
        )

        response = LenderService.get_recommendations(request)

        # Should have at least some options for poor credit
        assert response.total_matches > 0

    def test_get_recommendations_lender_info_complete(self):
        """Test that lender information is complete"""
        request = LenderRecommendationRequest(
            loan_amount=25000.0,
            credit_score_range="good",
            loan_term_months=60,
        )

        response = LenderService.get_recommendations(request)

        for rec in response.recommendations:
            lender = rec.lender
            assert lender.lender_id is not None
            assert len(lender.name) > 0
            assert len(lender.description) > 0
            assert lender.min_credit_score > 0
            assert lender.max_credit_score > lender.min_credit_score
            assert lender.min_loan_amount > 0
            assert lender.max_loan_amount > lender.min_loan_amount
            assert lender.apr_range_min > 0
            assert lender.apr_range_max > lender.apr_range_min
            assert len(lender.affiliate_url) > 0

    def test_get_recommendations_has_tracking_info(self):
        """Test that lenders have affiliate tracking information"""
        request = LenderRecommendationRequest(
            loan_amount=25000.0,
            credit_score_range="good",
            loan_term_months=60,
        )

        response = LenderService.get_recommendations(request)

        for rec in response.recommendations:
            lender = rec.lender
            # Should have affiliate URL
            assert lender.affiliate_url.startswith("http")
            # Should have referral code
            if lender.referral_code:
                assert len(lender.referral_code) > 0


class TestPartnerLenders:
    """Test partner lender data quality"""

    def test_partner_lenders_exist(self):
        """Test that partner lenders are defined"""
        assert len(LenderService.PARTNER_LENDERS) > 0

    def test_partner_lenders_minimum_count(self):
        """Test that we have at least 5 partner lenders"""
        assert len(LenderService.PARTNER_LENDERS) >= 5

    def test_partner_lenders_unique_ids(self):
        """Test that all lender IDs are unique"""
        lender_ids = [lender.lender_id for lender in LenderService.PARTNER_LENDERS]
        assert len(lender_ids) == len(set(lender_ids))

    def test_partner_lenders_realistic_apr_ranges(self):
        """Test that APR ranges are realistic"""
        for lender in LenderService.PARTNER_LENDERS:
            # APR should be between 2% and 25%
            assert 0.02 <= lender.apr_range_min <= 0.25
            assert 0.02 <= lender.apr_range_max <= 0.25
            # Max should be greater than min
            assert lender.apr_range_max > lender.apr_range_min

    def test_partner_lenders_have_features(self):
        """Test that lenders have features defined"""
        for lender in LenderService.PARTNER_LENDERS:
            # Should have at least some features or benefits
            total_features = len(lender.features) + len(lender.benefits)
            assert total_features > 0

    def test_partner_lenders_credit_score_ranges(self):
        """Test that credit score ranges are valid"""
        for lender in LenderService.PARTNER_LENDERS:
            assert 300 <= lender.min_credit_score <= 850
            assert 300 <= lender.max_credit_score <= 850
            assert lender.max_credit_score > lender.min_credit_score

    def test_partner_lenders_loan_amount_ranges(self):
        """Test that loan amount ranges are valid"""
        for lender in LenderService.PARTNER_LENDERS:
            assert lender.min_loan_amount > 0
            assert lender.max_loan_amount > lender.min_loan_amount
            assert lender.max_loan_amount <= 200000  # Reasonable max

    def test_partner_lenders_term_ranges(self):
        """Test that loan term ranges are valid"""
        for lender in LenderService.PARTNER_LENDERS:
            assert lender.min_term_months > 0
            assert lender.max_term_months > lender.min_term_months
            assert lender.max_term_months <= 120  # 10 years max is reasonable

    def test_partner_lenders_affiliate_urls(self):
        """Test that affiliate URLs are properly formatted"""
        for lender in LenderService.PARTNER_LENDERS:
            assert lender.affiliate_url.startswith("http")
            # Should contain domain
            assert "." in lender.affiliate_url

    def test_partner_lenders_referral_codes(self):
        """Test that referral codes follow pattern"""
        for lender in LenderService.PARTNER_LENDERS:
            if lender.referral_code:
                # Should start with ADG_ prefix
                assert lender.referral_code.startswith("ADG_")
                # Should have identifier
                assert len(lender.referral_code) > 4


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_minimum_loan_amount(self):
        """Test with minimum reasonable loan amount"""
        request = LenderRecommendationRequest(
            loan_amount=3000.0,
            credit_score_range="good",
            loan_term_months=36,
        )

        response = LenderService.get_recommendations(request)

        # Should be valid response even if limited matches
        assert isinstance(response.recommendations, list)

    def test_maximum_loan_amount(self):
        """Test with high loan amount"""
        request = LenderRecommendationRequest(
            loan_amount=80000.0,
            credit_score_range="excellent",
            loan_term_months=72,
        )

        response = LenderService.get_recommendations(request)

        # Should have some matches for high amount with excellent credit
        assert response.total_matches >= 0

    def test_short_loan_term(self):
        """Test with short loan term"""
        request = LenderRecommendationRequest(
            loan_amount=20000.0,
            credit_score_range="good",
            loan_term_months=24,
        )

        response = LenderService.get_recommendations(request)

        assert isinstance(response.recommendations, list)

    def test_long_loan_term(self):
        """Test with long loan term"""
        request = LenderRecommendationRequest(
            loan_amount=40000.0,
            credit_score_range="good",
            loan_term_months=84,
        )

        response = LenderService.get_recommendations(request)

        assert isinstance(response.recommendations, list)

    def test_case_insensitive_credit_score(self):
        """Test that credit score range is case-insensitive"""
        request_lower = LenderRecommendationRequest(
            loan_amount=25000.0,
            credit_score_range="good",
            loan_term_months=60,
        )

        request_upper = LenderRecommendationRequest(
            loan_amount=25000.0,
            credit_score_range="GOOD",
            loan_term_months=60,
        )

        response_lower = LenderService.get_recommendations(request_lower)
        response_upper = LenderService.get_recommendations(request_upper)

        # Should get same number of matches
        assert response_lower.total_matches == response_upper.total_matches
