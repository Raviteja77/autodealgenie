"""
MarketCheck API Service Layer

This service provides a comprehensive interface to the MarketCheck API,
including vehicle search, price predictions, VIN history, and Market Days Supply (MDS).

Key Features:
- Vehicle search with advanced filtering
- Price prediction using ML models
- VIN history and vehicle details
- Market Days Supply (MDS) analysis
- Comprehensive error handling and retry logic
- Redis caching for performance optimization
- Repository integration for persistent storage
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import Any

import httpx
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings
from app.db.redis import redis_client
from app.utils.error_handler import ApiError

logger = logging.getLogger(__name__)

# Cache TTL settings
SEARCH_CACHE_TTL = 900  # 15 minutes for search results
PRICE_CACHE_TTL = 3600  # 1 hour for price predictions
VIN_CACHE_TTL = 86400  # 24 hours for VIN history
MDS_CACHE_TTL = 3600  # 1 hour for MDS data


class MarketCheckService:
    """
    Service for interacting with MarketCheck API

    This service provides methods for:
    1. Vehicle search with filtering and pagination
    2. Price predictions using ML models
    3. VIN history and vehicle details
    4. Market Days Supply (MDS) analysis
    5. Comparable vehicle listings
    """

    BASE_URL = "https://api.marketcheck.com/v2"

    def __init__(self, api_key: str | None = None):
        """
        Initialize MarketCheck service

        Args:
            api_key: Optional API key, defaults to settings.MARKET_CHECK_API_KEY
        """
        self.api_key = api_key if api_key is not None else settings.MARKET_CHECK_API_KEY
        if not self.api_key:
            logger.warning("MARKET_CHECK_API_KEY not configured, MarketCheck features disabled")

    def is_available(self) -> bool:
        """Check if MarketCheck API is available and configured"""
        return bool(self.api_key)

    def _generate_cache_key(self, prefix: str, params: dict[str, Any]) -> str:
        """
        Generate a deterministic cache key from parameters

        Args:
            prefix: Cache key prefix (e.g., 'search', 'price', 'vin')
            params: Parameters to hash

        Returns:
            Cache key string
        """
        # Sort and serialize params for consistent hashing
        params_json = json.dumps(params, sort_keys=True, separators=(",", ":"))
        params_hash = hashlib.sha256(params_json.encode()).hexdigest()
        return f"marketcheck:{prefix}:{params_hash}"

    async def _get_from_cache(self, cache_key: str) -> dict[str, Any] | None:
        """
        Retrieve cached data from Redis

        Args:
            cache_key: Cache key to retrieve

        Returns:
            Cached data or None if not found
        """
        client = redis_client.get_client()
        if not client:
            return None

        try:
            cached_data = await client.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit: {cache_key}")
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Error reading from cache: {e}")

        return None

    async def _save_to_cache(self, cache_key: str, data: dict[str, Any], ttl: int) -> None:
        """
        Save data to Redis cache

        Args:
            cache_key: Cache key
            data: Data to cache
            ttl: Time to live in seconds
        """
        client = redis_client.get_client()
        if not client:
            return

        try:
            await client.setex(cache_key, ttl, json.dumps(data))
            logger.debug(f"Cached data: {cache_key} (TTL: {ttl}s)")
        except Exception as e:
            logger.error(f"Error writing to cache: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.RequestError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def _make_api_request(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Make HTTP request to MarketCheck API with retry logic

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            API response data

        Raises:
            ApiError: If API call fails after retries
        """
        if not self.is_available():
            raise ApiError(
                status_code=503,
                message="MarketCheck API not configured",
                details={"reason": "MARKET_CHECK_API_KEY not set"},
            )

        url = f"{self.BASE_URL}{endpoint}"
        params["api_key"] = self.api_key

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"MarketCheck API error: {e.response.status_code} - {e.response.text}")
            raise ApiError(
                status_code=e.response.status_code,
                message="MarketCheck API request failed",
                details={
                    "endpoint": endpoint,
                    "status_code": e.response.status_code,
                    "response": e.response.text[:500],
                },
            ) from e

        except httpx.RequestError as e:
            logger.error(f"MarketCheck API request error: {str(e)}")
            raise ApiError(
                status_code=503,
                message="Failed to connect to MarketCheck API",
                details={"error": str(e)},
            ) from e

    async def search_vehicles(
        self,
        make: str | None = None,
        model: str | None = None,
        year: int | None = None,
        min_year: int | None = None,
        max_year: int | None = None,
        min_price: int | None = None,
        max_price: int | None = None,
        max_mileage: int | None = None,
        car_type: str | None = None,
        zip_code: str | None = None,
        radius: int = 50,
        rows: int = 10,
        start: int = 0,
        sort_by: str | None = None,
        use_cache: bool = True,
    ) -> dict[str, Any]:
        """
        Search for vehicles using MarketCheck API

        Args:
            make: Vehicle make (e.g., 'toyota')
            model: Vehicle model (e.g., 'camry')
            year: Specific year
            min_year: Minimum year
            max_year: Maximum year
            min_price: Minimum price in USD
            max_price: Maximum price in USD
            max_mileage: Maximum mileage in miles
            car_type: Type ('new', 'used', 'certified')
            zip_code: ZIP code for location search
            radius: Search radius in miles
            rows: Number of results per page (max 50)
            start: Pagination offset
            sort_by: Sort field (e.g., 'price', 'miles', 'dom')
            use_cache: Whether to use cached results

        Returns:
            Dictionary with search results:
            {
                "num_found": int,
                "listings": list[dict],
                "facets": dict,
            }
        """
        logger.info(
            f"Searching vehicles: make={make}, model={model}, "
            f"year={year}, price={min_price}-{max_price}"
        )

        # Build query parameters
        params: dict[str, Any] = {
            "rows": min(rows, 50),
            "start": start,
            "min_photo_links": 3,
            "photo_links": "true",
        }

        # Add filters
        if make:
            params["make"] = make.lower()
        if model:
            params["model"] = model.lower()
        if year:
            params["year"] = str(year)
        elif min_year or max_year:
            year_range = f"{min_year or ''}-{max_year or ''}"
            params["year"] = year_range.strip("-")
        if min_price:
            params["min_price"] = min_price
        if max_price:
            params["max_price"] = max_price
        if max_mileage:
            params["miles"] = f"0-{max_mileage}"
        if car_type:
            params["car_type"] = car_type.lower()
        if zip_code:
            params["zip"] = zip_code
            params["radius"] = radius
        if sort_by:
            params["sort_by"] = sort_by

        # Check cache
        cache_key = self._generate_cache_key("search", params)
        if use_cache:
            cached_result = await self._get_from_cache(cache_key)
            if cached_result:
                return cached_result

        # Make API request
        try:
            response = await self._make_api_request("/search/car/active", params)

            # Parse and format response
            result = {
                "num_found": response.get("num_found", 0),
                "listings": [
                    self._parse_listing(listing) for listing in response.get("listings", [])
                ],
                "facets": response.get("facets", {}),
            }

            # Cache the result
            if use_cache:
                await self._save_to_cache(cache_key, result, SEARCH_CACHE_TTL)

            logger.info(f"Found {result['num_found']} vehicles")
            return result

        except ApiError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in search_vehicles: {e}", exc_info=True)
            raise ApiError(
                status_code=500,
                message="Failed to search vehicles",
                details={"error": str(e)},
            ) from e

    async def get_price_prediction(
        self,
        vin: str,
        mileage: int,
        zip_code: str | None = None,
        use_cache: bool = True,
    ) -> dict[str, Any]:
        """
        Get price prediction for a vehicle using MarketCheck ML model

        This uses the MarketCheck Price API:
        /v2/predict/car/us/marketcheck_price/comparables

        Args:
            vin: Vehicle Identification Number
            mileage: Current mileage
            zip_code: Optional ZIP code for location-based pricing
            use_cache: Whether to use cached results

        Returns:
            Dictionary with price prediction:
            {
                "vin": str,
                "predicted_price": float,
                "confidence": str,
                "price_range": {"min": float, "max": float},
                "comparables": list[dict],
                "last_updated": str (ISO timestamp)
            }
        """
        logger.info(f"Getting price prediction for VIN: {vin}, mileage: {mileage}")

        params = {
            "vin": vin,
            "miles": mileage,
        }
        if zip_code:
            params["zip"] = zip_code

        # Check cache
        cache_key = self._generate_cache_key("price", params)
        if use_cache:
            cached_result = await self._get_from_cache(cache_key)
            if cached_result:
                return cached_result

        # Make API request
        try:
            response = await self._make_api_request(
                "/predict/car/us/marketcheck_price/comparables", params
            )

            # Parse response
            prediction = response.get("prediction", {})
            comparables = response.get("comparables", [])

            result = {
                "vin": vin,
                "predicted_price": prediction.get("predicted_price"),
                "confidence": prediction.get("confidence", "medium"),
                "price_range": {
                    "min": prediction.get("price_range_min"),
                    "max": prediction.get("price_range_max"),
                },
                "comparables": [self._parse_listing(comp) for comp in comparables[:10]],
                "last_updated": datetime.utcnow().isoformat(),
            }

            # Cache the result
            if use_cache:
                await self._save_to_cache(cache_key, result, PRICE_CACHE_TTL)

            logger.info(
                f"Price prediction: ${result['predicted_price']} "
                f"(confidence: {result['confidence']})"
            )
            return result

        except ApiError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_price_prediction: {e}", exc_info=True)
            raise ApiError(
                status_code=500,
                message="Failed to get price prediction",
                details={"error": str(e), "vin": vin},
            ) from e

    async def get_vin_details(self, vin: str, use_cache: bool = True) -> dict[str, Any]:
        """
        Get detailed vehicle information by VIN

        Args:
            vin: Vehicle Identification Number
            use_cache: Whether to use cached results

        Returns:
            Dictionary with VIN details including history and specifications
        """
        logger.info(f"Getting VIN details: {vin}")

        params = {"vin": vin}

        # Check cache
        cache_key = self._generate_cache_key("vin", params)
        if use_cache:
            cached_result = await self._get_from_cache(cache_key)
            if cached_result:
                return cached_result

        # Make API request
        try:
            response = await self._make_api_request("/vin/decode", params)

            # Parse response
            result = {
                "vin": vin,
                "make": response.get("make"),
                "model": response.get("model"),
                "year": response.get("year"),
                "trim": response.get("trim"),
                "body_type": response.get("body_type"),
                "engine": response.get("engine"),
                "transmission": response.get("transmission"),
                "drivetrain": response.get("drivetrain"),
                "fuel_type": response.get("fuel_type"),
                "msrp": response.get("msrp"),
                "specifications": response.get("specifications", {}),
                "last_updated": datetime.utcnow().isoformat(),
            }

            # Cache the result
            if use_cache:
                await self._save_to_cache(cache_key, result, VIN_CACHE_TTL)

            logger.info(f"VIN details: {result['year']} {result['make']} {result['model']}")
            return result

        except ApiError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_vin_details: {e}", exc_info=True)
            raise ApiError(
                status_code=500,
                message="Failed to get VIN details",
                details={"error": str(e), "vin": vin},
            ) from e

    async def get_market_days_supply(
        self,
        make: str,
        model: str,
        year: int | None = None,
        zip_code: str | None = None,
        use_cache: bool = True,
    ) -> dict[str, Any]:
        """
        Get Market Days Supply (MDS) for a vehicle

        MDS indicates how long it typically takes to sell a vehicle.
        Lower values indicate higher demand.

        Args:
            make: Vehicle make
            model: Vehicle model
            year: Optional year filter
            zip_code: Optional location filter
            use_cache: Whether to use cached results

        Returns:
            Dictionary with MDS data:
            {
                "make": str,
                "model": str,
                "year": int | None,
                "mds": float,  # Days supply
                "demand_level": str,  # "high", "medium", "low"
                "trend": str,  # "increasing", "stable", "decreasing"
                "last_updated": str
            }
        """
        logger.info(f"Getting MDS: {year} {make} {model}")

        params = {
            "make": make.lower(),
            "model": model.lower(),
        }
        if year:
            params["year"] = year
        if zip_code:
            params["zip"] = zip_code

        # Check cache
        cache_key = self._generate_cache_key("mds", params)
        if use_cache:
            cached_result = await self._get_from_cache(cache_key)
            if cached_result:
                return cached_result

        # Make API request
        try:
            response = await self._make_api_request("/mds", params)

            mds_value = response.get("mds", 0)

            # Classify demand level based on MDS
            # Lower MDS = higher demand
            if mds_value < 30:
                demand_level = "high"
            elif mds_value < 60:
                demand_level = "medium"
            else:
                demand_level = "low"

            result = {
                "make": make,
                "model": model,
                "year": year,
                "mds": mds_value,
                "demand_level": demand_level,
                "trend": response.get("trend", "stable"),
                "inventory_count": response.get("inventory_count"),
                "last_updated": datetime.utcnow().isoformat(),
            }

            # Cache the result
            if use_cache:
                await self._save_to_cache(cache_key, result, MDS_CACHE_TTL)

            logger.info(f"MDS: {mds_value} days (demand: {demand_level})")
            return result

        except ApiError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_market_days_supply: {e}", exc_info=True)
            raise ApiError(
                status_code=500,
                message="Failed to get Market Days Supply",
                details={"error": str(e), "make": make, "model": model},
            ) from e

    def _parse_listing(self, listing: dict[str, Any]) -> dict[str, Any]:
        """
        Parse a MarketCheck listing into a standardized format

        Args:
            listing: Raw listing from MarketCheck API

        Returns:
            Parsed listing with relevant fields
        """
        # Extract photo links safely
        photo_links = listing.get("media", {}).get("photo_links", [])[:10]

        return {
            "vin": listing.get("vin"),
            "make": listing.get("build", {}).get("make"),
            "model": listing.get("build", {}).get("model"),
            "year": listing.get("build", {}).get("year"),
            "trim": listing.get("build", {}).get("trim"),
            "mileage": listing.get("miles"),
            "price": listing.get("price"),
            "msrp": listing.get("msrp"),
            "location": self._format_location(listing),
            "dealer_name": listing.get("dealer", {}).get("name"),
            "dealer_contact": self._format_dealer_contact(listing),
            "photo_links": photo_links,
            "vdp_url": listing.get("vdp_url"),
            "exterior_color": listing.get("exterior_color"),
            "interior_color": listing.get("interior_color"),
            "drivetrain": listing.get("build", {}).get("drivetrain"),
            "transmission": listing.get("build", {}).get("transmission"),
            "engine": listing.get("build", {}).get("engine"),
            "fuel_type": listing.get("build", {}).get("fuel_type"),
            "carfax_1_owner": listing.get("carfax_1_owner"),
            "carfax_clean_title": listing.get("carfax_clean_title"),
            "inventory_type": listing.get("inventory_type"),
            "days_on_market": listing.get("dom"),
        }

    def _format_location(self, listing: dict[str, Any]) -> str | None:
        """Format location from listing data"""
        dealer = listing.get("dealer", {})
        city = dealer.get("city")
        state = dealer.get("state")
        if city and state:
            return f"{city}, {state}"
        return None

    def _format_dealer_contact(self, listing: dict[str, Any]) -> str | None:
        """Format dealer contact information"""
        dealer = listing.get("dealer", {})
        street = dealer.get("street")
        city = dealer.get("city")
        state = dealer.get("state")
        zip_code = dealer.get("zip")
        phone = dealer.get("phone")

        parts = []
        if street:
            parts.append(street)
        if city and state:
            location = f"{city}, {state}"
            if zip_code:
                location += f" {zip_code}"
            parts.append(location)
        if phone:
            parts.append(phone)

        return " ".join(parts) if parts else None


# Singleton instance
marketcheck_service = MarketCheckService()
