"""
MarketCheck API Client for fetching vehicle listings
"""

from typing import Any

import httpx

from app.core.config import settings


class MarketCheckAPIClient:
    """Client for interacting with MarketCheck API"""

    BASE_URL = "https://api.marketcheck.com/v2"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.MARKET_CHECK_API_KEY
        if not self.api_key:
            raise ValueError("MARKET_CHECK_API_KEY is required")

    async def search_cars(
        self,
        make: str | None = None,
        model: str | None = None,
        car_type: str | None = None,
        min_price: int | None = None,
        max_price: int | None = None,
        min_year: int | None = None,
        max_year: int | None = None,
        max_mileage: int | None = None,
        rows: int = 50,
    ) -> dict[str, Any]:
        """
        Search for cars using MarketCheck API

        Args:
            make: Vehicle make (e.g., 'toyota')
            model: Vehicle model (e.g., 'rav4')
            car_type: Type of car ('new', 'used', 'certified')
            min_price: Minimum price
            max_price: Maximum price
            min_year: Minimum year
            max_year: Maximum year
            max_mileage: Maximum mileage
            rows: Number of results to return (default 50)

        Returns:
            Dictionary with search results including num_found and listings
        """
        endpoint = f"{self.BASE_URL}/search/car/active"

        # Build query parameters
        params = {
            "api_key": self.api_key,
            "rows": rows,
            "min_photo_links": 3,
            "photo_links": "true",
        }

        # Add optional parameters
        if make:
            params["make"] = make.lower()
        if model:
            params["model"] = model.lower()
        if car_type:
            params["car_type"] = car_type.lower()
        if min_price:
            params["min_price"] = min_price
        if max_price:
            params["max_price"] = max_price
        if min_year:
            params["year"] = f"{min_year}-{max_year}" if max_year else str(min_year)
        elif max_year:
            params["year"] = str(max_year)
        if max_mileage:
            params["miles"] = f"0-{max_mileage}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise ValueError(
                f"MarketCheck API error: {e.response.status_code} - {e.response.text}"
            ) from e
        except httpx.RequestError as e:
            raise ConnectionError(f"Request to MarketCheck API failed: {str(e)}") from e

    def parse_listing(self, listing: dict[str, Any]) -> dict[str, Any]:
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
marketcheck_client = MarketCheckAPIClient()
