"""
Tests for MarketCheck service
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.services.marketcheck_service import MarketCheckService
from app.utils.error_handler import ApiError


@pytest.fixture
def marketcheck_service():
    """Create MarketCheck service with test API key"""
    return MarketCheckService(api_key="test_api_key")


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    with patch("app.services.marketcheck_service.redis_client") as mock:
        mock_client = AsyncMock()
        mock.get_client.return_value = mock_client
        yield mock_client


@pytest.fixture
def sample_listing():
    """Sample MarketCheck listing response"""
    return {
        "vin": "1HGCM82633A123456",
        "build": {
            "make": "Honda",
            "model": "Accord",
            "year": 2020,
            "trim": "EX-L",
            "drivetrain": "FWD",
            "transmission": "Automatic",
            "engine": "1.5L Turbo I4",
            "fuel_type": "Gasoline",
        },
        "miles": 25000,
        "price": 22995,
        "msrp": 31000,
        "dealer": {
            "name": "Test Motors",
            "city": "San Francisco",
            "state": "CA",
            "street": "123 Main St",
            "zip": "94105",
            "phone": "415-555-0100",
        },
        "media": {
            "photo_links": [
                "https://example.com/photo1.jpg",
                "https://example.com/photo2.jpg",
            ]
        },
        "vdp_url": "https://example.com/listing",
        "exterior_color": "Black",
        "interior_color": "Beige",
        "carfax_1_owner": True,
        "carfax_clean_title": True,
        "inventory_type": "used",
        "dom": 15,
    }


class TestMarketCheckService:
    """Test suite for MarketCheckService"""

    def test_is_available_with_key(self, marketcheck_service):
        """Test service availability with API key"""
        assert marketcheck_service.is_available() is True

    def test_is_available_without_key(self):
        """Test service availability without API key"""
        with patch("app.services.marketcheck_service.settings") as mock_settings:
            mock_settings.MARKET_CHECK_API_KEY = None
            service = MarketCheckService(api_key=None)
            assert service.is_available() is False

    def test_generate_cache_key(self, marketcheck_service):
        """Test cache key generation"""
        params = {"make": "honda", "model": "accord", "year": 2020}
        key1 = marketcheck_service._generate_cache_key("search", params)
        key2 = marketcheck_service._generate_cache_key("search", params)

        # Same params should generate same key
        assert key1 == key2
        assert key1.startswith("marketcheck:search:")

        # Different params should generate different key
        params2 = {"make": "toyota", "model": "camry"}
        key3 = marketcheck_service._generate_cache_key("search", params2)
        assert key1 != key3

    @pytest.mark.asyncio
    async def test_get_from_cache_hit(self, marketcheck_service, mock_redis):
        """Test cache hit scenario"""
        cached_data = {"result": "test"}
        mock_redis.get.return_value = json.dumps(cached_data)

        result = await marketcheck_service._get_from_cache("test_key")
        assert result == cached_data
        mock_redis.get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_get_from_cache_miss(self, marketcheck_service, mock_redis):
        """Test cache miss scenario"""
        mock_redis.get.return_value = None

        result = await marketcheck_service._get_from_cache("test_key")
        assert result is None
        mock_redis.get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_save_to_cache(self, marketcheck_service, mock_redis):
        """Test saving to cache"""
        data = {"result": "test"}
        await marketcheck_service._save_to_cache("test_key", data, 3600)

        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == "test_key"
        assert call_args[0][1] == 3600
        assert json.loads(call_args[0][2]) == data

    @pytest.mark.asyncio
    async def test_make_api_request_success(self, marketcheck_service):
        """Test successful API request"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"num_found": 10, "listings": []}

        with patch("httpx.AsyncClient") as mock_client:
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_context

            result = await marketcheck_service._make_api_request(
                "/search/car/active", {"make": "honda"}
            )

            assert result == {"num_found": 10, "listings": []}

    @pytest.mark.asyncio
    async def test_make_api_request_http_error(self, marketcheck_service):
        """Test API request with HTTP error"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"

        with patch("httpx.AsyncClient") as mock_client:
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.HTTPStatusError(
                    "Bad Request", request=MagicMock(), response=mock_response
                )
            )
            mock_client.return_value = mock_context

            with pytest.raises(ApiError) as exc_info:
                await marketcheck_service._make_api_request("/search/car/active", {"make": "honda"})

            assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_make_api_request_without_api_key(self):
        """Test API request without API key"""
        with patch("app.services.marketcheck_service.settings") as mock_settings:
            mock_settings.MARKET_CHECK_API_KEY = None
            service = MarketCheckService(api_key=None)

            with pytest.raises(ApiError) as exc_info:
                await service._make_api_request("/search/car/active", {})

            assert exc_info.value.status_code == 503
            assert "not configured" in exc_info.value.message.lower()

    @pytest.mark.asyncio
    async def test_search_vehicles_basic(self, marketcheck_service, mock_redis, sample_listing):
        """Test basic vehicle search"""
        mock_redis.get.return_value = None  # Cache miss

        api_response = {
            "num_found": 1,
            "listings": [sample_listing],
            "facets": {},
        }

        with patch.object(
            marketcheck_service,
            "_make_api_request",
            new_callable=AsyncMock,
            return_value=api_response,
        ):
            result = await marketcheck_service.search_vehicles(
                make="honda", model="accord", max_price=25000
            )

            assert result["num_found"] == 1
            assert len(result["listings"]) == 1
            assert result["listings"][0]["make"] == "Honda"
            assert result["listings"][0]["model"] == "Accord"
            assert result["listings"][0]["price"] == 22995

    @pytest.mark.asyncio
    async def test_search_vehicles_with_cache(self, marketcheck_service, mock_redis):
        """Test vehicle search with cached results"""
        cached_result = {
            "num_found": 5,
            "listings": [{"vin": "123"}],
            "facets": {},
        }
        mock_redis.get.return_value = json.dumps(cached_result)

        result = await marketcheck_service.search_vehicles(make="honda", use_cache=True)

        assert result == cached_result
        mock_redis.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_price_prediction(self, marketcheck_service, mock_redis):
        """Test price prediction"""
        mock_redis.get.return_value = None  # Cache miss

        api_response = {
            "prediction": {
                "predicted_price": 23500,
                "confidence": "high",
                "price_range_min": 22000,
                "price_range_max": 25000,
            },
            "comparables": [],
        }

        with patch.object(
            marketcheck_service,
            "_make_api_request",
            new_callable=AsyncMock,
            return_value=api_response,
        ):
            result = await marketcheck_service.get_price_prediction(
                vin="1HGCM82633A123456", mileage=25000
            )

            assert result["vin"] == "1HGCM82633A123456"
            assert result["predicted_price"] == 23500
            assert result["confidence"] == "high"
            assert result["price_range"]["min"] == 22000
            assert result["price_range"]["max"] == 25000

    @pytest.mark.asyncio
    async def test_get_vin_details(self, marketcheck_service, mock_redis):
        """Test VIN details lookup"""
        mock_redis.get.return_value = None  # Cache miss

        api_response = {
            "make": "Honda",
            "model": "Accord",
            "year": 2020,
            "trim": "EX-L",
            "body_type": "Sedan",
            "engine": "1.5L Turbo I4",
            "transmission": "Automatic",
            "drivetrain": "FWD",
            "fuel_type": "Gasoline",
            "msrp": 31000,
            "specifications": {"horsepower": 192, "mpg_city": 30},
        }

        with patch.object(
            marketcheck_service,
            "_make_api_request",
            new_callable=AsyncMock,
            return_value=api_response,
        ):
            result = await marketcheck_service.get_vin_details("1HGCM82633A123456")

            assert result["vin"] == "1HGCM82633A123456"
            assert result["make"] == "Honda"
            assert result["model"] == "Accord"
            assert result["year"] == 2020
            assert result["msrp"] == 31000

    @pytest.mark.asyncio
    async def test_get_market_days_supply(self, marketcheck_service, mock_redis):
        """Test Market Days Supply lookup"""
        mock_redis.get.return_value = None  # Cache miss

        api_response = {
            "mds": 45,
            "trend": "stable",
            "inventory_count": 2500,
        }

        with patch.object(
            marketcheck_service,
            "_make_api_request",
            new_callable=AsyncMock,
            return_value=api_response,
        ):
            result = await marketcheck_service.get_market_days_supply(
                make="Honda", model="Accord", year=2020
            )

            assert result["make"] == "Honda"
            assert result["model"] == "Accord"
            assert result["year"] == 2020
            assert result["mds"] == 45
            assert result["demand_level"] == "medium"  # 30-60 days = medium
            assert result["trend"] == "stable"

    def test_parse_listing(self, marketcheck_service, sample_listing):
        """Test listing parsing"""
        parsed = marketcheck_service._parse_listing(sample_listing)

        assert parsed["vin"] == "1HGCM82633A123456"
        assert parsed["make"] == "Honda"
        assert parsed["model"] == "Accord"
        assert parsed["year"] == 2020
        assert parsed["price"] == 22995
        assert parsed["mileage"] == 25000
        assert parsed["location"] == "San Francisco, CA"
        assert parsed["dealer_name"] == "Test Motors"
        assert parsed["carfax_1_owner"] is True
        assert len(parsed["photo_links"]) == 2

    def test_format_location(self, marketcheck_service):
        """Test location formatting"""
        listing = {
            "dealer": {
                "city": "San Francisco",
                "state": "CA",
            }
        }
        location = marketcheck_service._format_location(listing)
        assert location == "San Francisco, CA"

        # Test with missing data
        listing = {"dealer": {"city": "San Francisco"}}
        location = marketcheck_service._format_location(listing)
        assert location is None

    def test_format_dealer_contact(self, marketcheck_service):
        """Test dealer contact formatting"""
        listing = {
            "dealer": {
                "street": "123 Main St",
                "city": "San Francisco",
                "state": "CA",
                "zip": "94105",
                "phone": "415-555-0100",
            }
        }
        contact = marketcheck_service._format_dealer_contact(listing)
        assert "123 Main St" in contact
        assert "San Francisco, CA 94105" in contact
        assert "415-555-0100" in contact

        # Test with minimal data
        listing = {"dealer": {}}
        contact = marketcheck_service._format_dealer_contact(listing)
        assert contact is None
