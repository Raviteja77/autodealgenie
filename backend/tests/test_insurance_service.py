"""
Unit tests for Insurance Recommendation Service
"""

from app.schemas.insurance_schemas import InsuranceRecommendationRequest
from app.services.insurance_recommendation_service import InsuranceRecommendationService


class TestVehicleAgeFactor:
    """Test vehicle age factor calculation"""

    def test_new_vehicle(self):
        """Test factor for new vehicle"""
        factor = InsuranceRecommendationService._get_vehicle_age_factor(0)
        assert factor == 1.3  # New cars cost more to insure

    def test_mid_age_vehicle(self):
        """Test factor for mid-age vehicle"""
        factor = InsuranceRecommendationService._get_vehicle_age_factor(3)
        assert factor == 1.0  # Sweet spot

    def test_old_vehicle(self):
        """Test factor for old vehicle"""
        factor = InsuranceRecommendationService._get_vehicle_age_factor(10)
        assert factor == 0.8  # Older cars cost less

    def test_very_old_vehicle(self):
        """Test factor for very old vehicle (uses max bracket)"""
        factor = InsuranceRecommendationService._get_vehicle_age_factor(15)
        assert factor == 0.8  # Should use 10+ bracket


class TestDriverAgeFactor:
    """Test driver age factor calculation"""

    def test_young_driver(self):
        """Test factor for young driver"""
        factor = InsuranceRecommendationService._get_driver_age_factor(18)
        assert factor == 2.0  # High risk

    def test_standard_driver(self):
        """Test factor for standard age driver"""
        factor = InsuranceRecommendationService._get_driver_age_factor(25)
        assert factor == 1.0  # Standard rate

    def test_experienced_driver(self):
        """Test factor for experienced driver"""
        factor = InsuranceRecommendationService._get_driver_age_factor(50)
        assert factor == 0.9  # Lower risk

    def test_senior_driver(self):
        """Test factor for senior driver"""
        factor = InsuranceRecommendationService._get_driver_age_factor(75)
        assert factor == 1.2  # Increased risk


class TestFilterProviders:
    """Test insurance provider filtering"""

    def test_filter_providers_standard_case(self):
        """Test filtering with standard criteria"""
        providers = InsuranceRecommendationService.filter_providers(
            vehicle_value=25000.0,
            coverage_type="full",
            driver_age=30,
        )
        assert len(providers) > 0
        # All returned providers should accept this vehicle value
        for provider in providers:
            assert 25000.0 >= provider.min_vehicle_value
            assert 25000.0 <= provider.max_vehicle_value
            assert "full" in provider.coverage_types

    def test_filter_providers_high_value_vehicle(self):
        """Test filtering with high-value vehicle"""
        providers = InsuranceRecommendationService.filter_providers(
            vehicle_value=100000.0,
            coverage_type="full",
            driver_age=40,
        )
        # Should have at least one provider for high-value vehicles
        assert len(providers) > 0
        for provider in providers:
            assert 100000.0 <= provider.max_vehicle_value

    def test_filter_providers_young_driver(self):
        """Test filtering with young driver"""
        providers = InsuranceRecommendationService.filter_providers(
            vehicle_value=15000.0,
            coverage_type="liability",
            driver_age=18,
        )
        # Should have providers accepting young drivers
        assert len(providers) > 0
        for provider in providers:
            assert 18 >= provider.min_driver_age
            assert "liability" in provider.coverage_types

    def test_filter_providers_senior_driver(self):
        """Test filtering with senior driver"""
        providers = InsuranceRecommendationService.filter_providers(
            vehicle_value=20000.0,
            coverage_type="comprehensive",
            driver_age=70,
        )
        # Should have providers accepting senior drivers
        assert len(providers) > 0
        for provider in providers:
            assert 70 <= provider.max_driver_age
            assert "comprehensive" in provider.coverage_types

    def test_filter_providers_liability_only(self):
        """Test filtering for liability coverage only"""
        providers = InsuranceRecommendationService.filter_providers(
            vehicle_value=10000.0,
            coverage_type="liability",
            driver_age=25,
        )
        assert len(providers) > 0
        for provider in providers:
            assert "liability" in provider.coverage_types

    def test_filter_providers_no_matches_extreme_value(self):
        """Test filtering with extremely high vehicle value"""
        providers = InsuranceRecommendationService.filter_providers(
            vehicle_value=500000.0,  # Very high value
            coverage_type="full",
            driver_age=30,
        )
        # May have no matches for extreme values
        assert isinstance(providers, list)


class TestCalculateEstimatedPremium:
    """Test premium calculation"""

    def test_calculate_premium_liability(self):
        """Test premium calculation for liability coverage"""
        provider = InsuranceRecommendationService.PARTNER_PROVIDERS[0]
        premium = InsuranceRecommendationService.calculate_estimated_premium(
            provider=provider,
            vehicle_value=20000.0,
            vehicle_age=3,
            coverage_type="liability",
            driver_age=30,
        )
        # Should be within provider's range
        assert premium >= provider.premium_range_min
        assert premium <= provider.premium_range_max

    def test_calculate_premium_full_coverage(self):
        """Test premium calculation for full coverage"""
        provider = InsuranceRecommendationService.PARTNER_PROVIDERS[0]
        premium_full = InsuranceRecommendationService.calculate_estimated_premium(
            provider=provider,
            vehicle_value=20000.0,
            vehicle_age=3,
            coverage_type="full",
            driver_age=30,
        )
        premium_liability = InsuranceRecommendationService.calculate_estimated_premium(
            provider=provider,
            vehicle_value=20000.0,
            vehicle_age=3,
            coverage_type="liability",
            driver_age=30,
        )
        # Full coverage should cost more than liability
        assert premium_full > premium_liability

    def test_calculate_premium_young_driver_costs_more(self):
        """Test that young drivers pay more"""
        provider = InsuranceRecommendationService.PARTNER_PROVIDERS[0]
        premium_young = InsuranceRecommendationService.calculate_estimated_premium(
            provider=provider,
            vehicle_value=20000.0,
            vehicle_age=3,
            coverage_type="liability",
            driver_age=18,
        )
        premium_experienced = InsuranceRecommendationService.calculate_estimated_premium(
            provider=provider,
            vehicle_value=20000.0,
            vehicle_age=3,
            coverage_type="liability",
            driver_age=30,
        )
        # Young driver should pay more
        assert premium_young > premium_experienced


class TestScoreProviders:
    """Test provider scoring"""

    def test_score_providers_returns_sorted_list(self):
        """Test that scoring returns a sorted list"""
        providers = InsuranceRecommendationService.filter_providers(
            vehicle_value=25000.0,
            coverage_type="full",
            driver_age=30,
        )
        scored = InsuranceRecommendationService.score_providers(
            providers=providers,
            vehicle_value=25000.0,
            vehicle_age=3,
            coverage_type="full",
            driver_age=30,
        )
        # Should return list of tuples
        assert len(scored) == len(providers)
        # Should be sorted by score (descending)
        for i in range(len(scored) - 1):
            assert scored[i][1] >= scored[i + 1][1]

    def test_score_providers_includes_all_fields(self):
        """Test that scoring includes all required fields"""
        providers = InsuranceRecommendationService.filter_providers(
            vehicle_value=25000.0,
            coverage_type="comprehensive",
            driver_age=30,
        )
        scored = InsuranceRecommendationService.score_providers(
            providers=providers,
            vehicle_value=25000.0,
            vehicle_age=5,
            coverage_type="comprehensive",
            driver_age=30,
        )
        for provider, score, premium, reason in scored:
            assert provider is not None
            assert score >= 0
            assert premium > 0
            assert len(reason) > 0


class TestGetRecommendations:
    """Test the main recommendation endpoint"""

    def test_get_recommendations_standard_case(self):
        """Test getting recommendations with standard criteria"""
        request = InsuranceRecommendationRequest(
            vehicle_value=25000.0,
            vehicle_age=3,
            vehicle_make="Toyota",
            vehicle_model="Camry",
            coverage_type="full",
            driver_age=30,
        )
        response = InsuranceRecommendationService.get_recommendations(request, max_results=5)

        assert response.total_matches > 0
        assert len(response.recommendations) > 0
        assert len(response.recommendations) <= 5

        # Check that recommendations are properly ranked
        for i, rec in enumerate(response.recommendations):
            assert rec.rank == i + 1
            assert rec.match_score >= 0
            assert rec.estimated_monthly_premium > 0
            assert rec.estimated_annual_premium > 0
            assert len(rec.recommendation_reason) > 0

    def test_get_recommendations_liability_coverage(self):
        """Test recommendations for liability coverage"""
        request = InsuranceRecommendationRequest(
            vehicle_value=15000.0,
            vehicle_age=7,
            vehicle_make="Honda",
            vehicle_model="Civic",
            coverage_type="liability",
            driver_age=25,
        )
        response = InsuranceRecommendationService.get_recommendations(request, max_results=3)

        assert len(response.recommendations) <= 3
        # All recommendations should support liability coverage
        for rec in response.recommendations:
            assert "liability" in rec.provider.coverage_types

    def test_get_recommendations_high_value_vehicle(self):
        """Test recommendations for high-value vehicle"""
        request = InsuranceRecommendationRequest(
            vehicle_value=80000.0,
            vehicle_age=1,
            vehicle_make="BMW",
            vehicle_model="5 Series",
            coverage_type="full",
            driver_age=45,
        )
        response = InsuranceRecommendationService.get_recommendations(request, max_results=5)

        assert response.total_matches > 0
        # Premiums should be higher for expensive vehicles
        for rec in response.recommendations:
            assert rec.estimated_monthly_premium >= 100.0

    def test_get_recommendations_young_driver(self):
        """Test recommendations for young driver"""
        request = InsuranceRecommendationRequest(
            vehicle_value=20000.0,
            vehicle_age=5,
            vehicle_make="Ford",
            vehicle_model="Focus",
            coverage_type="comprehensive",
            driver_age=19,
        )
        response = InsuranceRecommendationService.get_recommendations(request, max_results=5)

        # Should have providers accepting young drivers
        assert response.total_matches > 0
        for rec in response.recommendations:
            assert rec.provider.min_driver_age <= 19

    def test_get_recommendations_no_matches(self):
        """Test recommendations when no providers match"""
        request = InsuranceRecommendationRequest(
            vehicle_value=1000000.0,  # Extremely high value
            vehicle_age=0,
            vehicle_make="Ferrari",
            vehicle_model="F8",
            coverage_type="full",
            driver_age=100,  # Very old driver
        )
        response = InsuranceRecommendationService.get_recommendations(request, max_results=5)

        assert response.total_matches == 0
        assert len(response.recommendations) == 0
        assert "vehicle_value" in response.request_summary

    def test_get_recommendations_request_summary(self):
        """Test that request summary is included in response"""
        request = InsuranceRecommendationRequest(
            vehicle_value=25000.0,
            vehicle_age=3,
            vehicle_make="Toyota",
            vehicle_model="Camry",
            coverage_type="full",
            driver_age=30,
        )
        response = InsuranceRecommendationService.get_recommendations(request)

        assert "vehicle_value" in response.request_summary
        assert "vehicle_age" in response.request_summary
        assert "coverage_type" in response.request_summary
        assert "driver_age" in response.request_summary
        assert response.request_summary["vehicle_value"] == 25000.0
