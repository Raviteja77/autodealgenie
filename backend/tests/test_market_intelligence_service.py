"""
Unit tests for MarketIntelligenceService
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.market_intelligence_service import MarketIntelligenceService
from app.services.marketcheck_service import MarketCheckService
from app.utils.error_handler import ApiError


@pytest.fixture
def mock_marketcheck_service():
    """Create a mock MarketCheckService"""
    service = MagicMock(spec=MarketCheckService)
    service.is_available.return_value = True
    return service


@pytest.fixture
def market_intelligence_service(mock_marketcheck_service):
    """Create MarketIntelligenceService with mocked dependencies"""
    return MarketIntelligenceService(marketcheck_service=mock_marketcheck_service)


class TestGetRealTimeComps:
    """Tests for get_real_time_comps method"""

    @pytest.mark.asyncio
    async def test_get_real_time_comps_success(
        self, market_intelligence_service, mock_marketcheck_service
    ):
        """Test successful retrieval of comparable vehicles"""
        # Mock search_vehicles response
        mock_marketcheck_service.search_vehicles = AsyncMock(
            return_value={
                "num_found": 15,
                "listings": [
                    {"price": 25000, "vin": "VIN1", "make": "Toyota", "model": "Camry"},
                    {"price": 26000, "vin": "VIN2", "make": "Toyota", "model": "Camry"},
                    {"price": 24500, "vin": "VIN3", "make": "Toyota", "model": "Camry"},
                    {"price": 25500, "vin": "VIN4", "make": "Toyota", "model": "Camry"},
                    {"price": 27000, "vin": "VIN5", "make": "Toyota", "model": "Camry"},
                ],
                "facets": {},
            }
        )

        result = await market_intelligence_service.get_real_time_comps(
            make="Toyota",
            model="Camry",
            year=2022,
            mileage=15000,
            zip_code="94103",
            max_results=10,
        )

        assert result["total_found"] == 15
        assert len(result["comparables"]) == 5
        assert result["average_price"] == 25600.0
        assert result["median_price"] == 25500.0
        assert result["price_range"]["min"] == 24500.0
        assert result["price_range"]["max"] == 27000.0
        assert "market_summary" in result
        assert "last_updated" in result

    @pytest.mark.asyncio
    async def test_get_real_time_comps_no_results(
        self, market_intelligence_service, mock_marketcheck_service
    ):
        """Test handling of no comparable vehicles found"""
        mock_marketcheck_service.search_vehicles = AsyncMock(
            return_value={"num_found": 0, "listings": [], "facets": {}}
        )

        result = await market_intelligence_service.get_real_time_comps(
            make="Toyota", model="Camry", year=2022, mileage=15000
        )

        # Should return fallback data
        assert result["total_found"] == 0
        assert result["average_price"] == 0.0
        assert "temporarily unavailable" in result["market_summary"].lower()

    @pytest.mark.asyncio
    async def test_get_real_time_comps_api_unavailable(self, mock_marketcheck_service):
        """Test handling when MarketCheck API is unavailable"""
        mock_marketcheck_service.is_available.return_value = False
        service = MarketIntelligenceService(marketcheck_service=mock_marketcheck_service)

        result = await service.get_real_time_comps(
            make="Toyota", model="Camry", year=2022, mileage=15000
        )

        # Should return fallback data
        assert result["average_price"] == 0.0
        assert "temporarily unavailable" in result["market_summary"].lower()

    @pytest.mark.asyncio
    async def test_get_real_time_comps_api_error(
        self, market_intelligence_service, mock_marketcheck_service
    ):
        """Test handling of API errors"""
        mock_marketcheck_service.search_vehicles = AsyncMock(
            side_effect=ApiError(status_code=503, message="Service unavailable")
        )

        # Should not raise, returns fallback
        result = await market_intelligence_service.get_real_time_comps(
            make="Toyota", model="Camry", year=2022, mileage=15000
        )

        assert result["average_price"] == 0.0
        assert "temporarily unavailable" in result["market_summary"].lower()


class TestGetPriceTrend:
    """Tests for get_price_trend method"""

    @pytest.mark.asyncio
    async def test_get_price_trend_high_demand(
        self, market_intelligence_service, mock_marketcheck_service
    ):
        """Test price trend with high demand"""
        mock_marketcheck_service.get_market_days_supply = AsyncMock(
            return_value={
                "mds": 25.0,
                "demand_level": "high",
                "trend": "increasing",
                "inventory_count": 150,
            }
        )

        result = await market_intelligence_service.get_price_trend(
            make="Toyota", model="Camry", year=2022
        )

        assert result["trend_direction"] == "increasing"
        assert result["demand_level"] == "high"
        assert result["market_days_supply"] == 25.0
        assert result["price_change_percent"] == 2.5  # High demand, low MDS
        assert "high demand" in result["recommendation"].lower()

    @pytest.mark.asyncio
    async def test_get_price_trend_low_demand(
        self, market_intelligence_service, mock_marketcheck_service
    ):
        """Test price trend with low demand"""
        mock_marketcheck_service.get_market_days_supply = AsyncMock(
            return_value={
                "mds": 65.0,
                "demand_level": "low",
                "trend": "decreasing",
                "inventory_count": 50,
            }
        )

        result = await market_intelligence_service.get_price_trend(
            make="Toyota", model="Camry", year=2022
        )

        assert result["trend_direction"] == "decreasing"
        assert result["demand_level"] == "low"
        assert result["market_days_supply"] == 65.0
        assert result["price_change_percent"] == -2.0  # Low demand, high MDS
        assert "leverage" in result["recommendation"].lower()

    @pytest.mark.asyncio
    async def test_get_price_trend_stable_market(
        self, market_intelligence_service, mock_marketcheck_service
    ):
        """Test price trend in stable market"""
        mock_marketcheck_service.get_market_days_supply = AsyncMock(
            return_value={
                "mds": 45.0,
                "demand_level": "medium",
                "trend": "stable",
                "inventory_count": 100,
            }
        )

        result = await market_intelligence_service.get_price_trend(
            make="Toyota", model="Camry", year=2022
        )

        assert result["trend_direction"] == "stable"
        assert result["demand_level"] == "medium"
        assert result["price_change_percent"] == 0.0
        assert "stable" in result["recommendation"].lower()

    @pytest.mark.asyncio
    async def test_get_price_trend_api_unavailable(self, mock_marketcheck_service):
        """Test handling when MarketCheck API is unavailable"""
        mock_marketcheck_service.is_available.return_value = False
        service = MarketIntelligenceService(marketcheck_service=mock_marketcheck_service)

        result = await service.get_price_trend(
            make="Toyota", model="Camry", year=2022
        )

        # Should return fallback data
        assert result["trend_direction"] == "stable"
        assert result["demand_level"] == "medium"
        assert result["price_change_percent"] == 0.0


class TestMarketSummaryGeneration:
    """Tests for market summary generation logic"""

    def test_market_summary_wide_spread(self, market_intelligence_service):
        """Test summary for market with wide price variation"""
        summary = market_intelligence_service._generate_market_summary(
            total_found=50,
            average_price=25000,
            median_price=24500,
            price_range=(20000, 30000),
        )

        assert "50 comparable vehicles" in summary
        assert "Wide price variation" in summary

    def test_market_summary_narrow_spread(self, market_intelligence_service):
        """Test summary for market with narrow price range"""
        summary = market_intelligence_service._generate_market_summary(
            total_found=30,
            average_price=25000,
            median_price=25000,
            price_range=(24500, 25500),
        )

        assert "30 comparable vehicles" in summary
        assert "Narrow price range" in summary

    def test_market_summary_moderate_spread(self, market_intelligence_service):
        """Test summary for market with moderate price variation"""
        summary = market_intelligence_service._generate_market_summary(
            total_found=40,
            average_price=25000,
            median_price=25000,
            price_range=(22500, 27500),
        )

        assert "40 comparable vehicles" in summary
        assert "Moderate price variation" in summary


class TestPriceTrendRecommendations:
    """Tests for price trend recommendation logic"""

    def test_recommendation_increasing_high_demand(self, market_intelligence_service):
        """Test recommendation for increasing prices with high demand"""
        recommendation = market_intelligence_service._generate_price_trend_recommendation(
            trend_direction="increasing", demand_level="high", price_change_percent=2.5
        )

        assert "upward" in recommendation.lower()
        assert "quickly" in recommendation.lower()

    def test_recommendation_decreasing_low_demand(self, market_intelligence_service):
        """Test recommendation for decreasing prices with low demand"""
        recommendation = market_intelligence_service._generate_price_trend_recommendation(
            trend_direction="decreasing", demand_level="low", price_change_percent=-2.0
        )

        assert "downward" in recommendation.lower()
        assert "leverage" in recommendation.lower()

    def test_recommendation_stable_market(self, market_intelligence_service):
        """Test recommendation for stable market"""
        recommendation = market_intelligence_service._generate_price_trend_recommendation(
            trend_direction="stable", demand_level="medium", price_change_percent=0.0
        )

        assert "stable" in recommendation.lower()
        assert "strategically" in recommendation.lower()


class TestPriceChangeEstimation:
    """Tests for price change estimation logic"""

    def test_price_change_high_demand_low_mds(self, market_intelligence_service):
        """Test price change for high demand with low MDS"""
        change = market_intelligence_service._estimate_price_change(
            demand_level="high", mds_value=25.0
        )
        assert change == 2.5

    def test_price_change_high_demand_moderate_mds(self, market_intelligence_service):
        """Test price change for high demand with moderate MDS"""
        change = market_intelligence_service._estimate_price_change(
            demand_level="high", mds_value=40.0
        )
        assert change == 1.0

    def test_price_change_low_demand_high_mds(self, market_intelligence_service):
        """Test price change for low demand with high MDS"""
        change = market_intelligence_service._estimate_price_change(
            demand_level="low", mds_value=70.0
        )
        assert change == -2.0

    def test_price_change_low_demand_moderate_mds(self, market_intelligence_service):
        """Test price change for low demand with moderate MDS"""
        change = market_intelligence_service._estimate_price_change(
            demand_level="low", mds_value=50.0
        )
        assert change == -1.0

    def test_price_change_medium_demand(self, market_intelligence_service):
        """Test price change for medium demand"""
        change = market_intelligence_service._estimate_price_change(
            demand_level="medium", mds_value=45.0
        )
        assert change == 0.0
