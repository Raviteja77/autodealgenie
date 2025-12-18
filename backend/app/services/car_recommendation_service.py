"""
Car Recommendation Service with LLM Integration
Enhanced with caching, rate limiting, retry logic, search history, and webhooks
"""

import hashlib
import json
import logging
from typing import Any

from app.llm import generate_structured_json
from app.llm.llm_client import llm_client
from app.llm.schemas import CarSelectionResponse
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings
from app.db.redis import redis_client
from app.repositories.search_history_repository import search_history_repository
from app.repositories.webhook_repository import WebhookRepository
from app.services.webhook_service import webhook_service
from app.tools.marketcheck_client import marketcheck_client

logger = logging.getLogger(__name__)

# Cache TTL in seconds (15 minutes)
CACHE_TTL = 900


class CarRecommendationService:
    """Service for recommending cars using LLM analysis with caching and webhooks"""

    def __init__(self):
        pass

    def _generate_cache_key(
        self,
        make: str | None = None,
        model: str | None = None,
        budget_min: int | None = None,
        budget_max: int | None = None,
        car_type: str | None = None,
        year_min: int | None = None,
        year_max: int | None = None,
        mileage_max: int | None = None,
        user_priorities: str | None = None,
    ) -> str:
        """
        Generate a cache key for search parameters

        Args:
            Search parameters

        Returns:
            Cache key string
        """
        # Create a consistent string representation of search params
        params = {
            "make": make,
            "model": model,
            "budget_min": budget_min,
            "budget_max": budget_max,
            "car_type": car_type,
            "year_min": year_min,
            "year_max": year_max,
            "mileage_max": mileage_max,
            "user_priorities": user_priorities,
        }
        # Sort keys for consistency
        params_str = json.dumps(params, sort_keys=True)
        # Generate hash
        hash_obj = hashlib.md5(params_str.encode())
        return f"car_search:{hash_obj.hexdigest()}"

    async def _get_cached_result(self, cache_key: str) -> dict[str, Any] | None:
        """
        Get cached search result from Redis

        Args:
            cache_key: Cache key

        Returns:
            Cached result or None
        """
        client = redis_client.get_client()
        if not client:
            return None

        try:
            cached_data = await client.get(cache_key)
            if cached_data:
                logger.info(f"Cache hit for key: {cache_key}")
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Error reading from cache: {e}")

        return None

    async def _set_cached_result(self, cache_key: str, result: dict[str, Any]) -> None:
        """
        Cache search result in Redis

        Args:
            cache_key: Cache key
            result: Result to cache
        """
        client = redis_client.get_client()
        if not client:
            return

        try:
            await client.setex(cache_key, CACHE_TTL, json.dumps(result))
            logger.info(f"Cached result with key: {cache_key}, TTL: {CACHE_TTL}s")
        except Exception as e:
            logger.error(f"Error writing to cache: {e}")

    @retry(
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def _search_marketcheck_with_retry(
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
        Search MarketCheck API with retry logic for transient errors

        Args:
            Search parameters

        Returns:
            API response

        Raises:
            Exception after 3 failed attempts
        """
        logger.info("Calling MarketCheck API (with retry logic)")
        return await marketcheck_client.search_cars(
            make=make,
            model=model,
            car_type=car_type,
            min_price=min_price,
            max_price=max_price,
            min_year=min_year,
            max_year=max_year,
            max_mileage=max_mileage,
            rows=rows,
        )

    async def _trigger_webhooks(self, vehicles: list[dict[str, Any]], db_session=None) -> None:
        """
        Trigger webhooks for matching vehicle alerts

        Args:
            vehicles: List of vehicles to check
            db_session: Database session (optional, for webhook lookups)
        """
        if not db_session or not vehicles:
            return

        try:
            from datetime import datetime

            webhook_repo = WebhookRepository(db_session)

            # Process each vehicle
            for vehicle in vehicles:
                # Find matching subscriptions
                matching_subs = webhook_repo.get_matching_subscriptions(
                    make=vehicle.get("make"),
                    model=vehicle.get("model"),
                    price=vehicle.get("price"),
                    year=vehicle.get("year"),
                    mileage=vehicle.get("mileage"),
                )

                if matching_subs:
                    # Send webhooks asynchronously
                    result = await webhook_service.send_vehicle_alerts(matching_subs, vehicle)
                    logger.info(
                        f"Sent vehicle alert webhooks: {result['success']} succeeded, "
                        f"{result['failed']} failed"
                    )

                    # Update subscription statuses
                    for sub in matching_subs:
                        webhook_repo.update(sub.id, {"last_triggered": datetime.utcnow()})

        except Exception as e:
            logger.error(f"Error triggering webhooks: {e}")

    async def search_and_recommend(
        self,
        make: str | None = None,
        model: str | None = None,
        budget_min: int | None = None,
        budget_max: int | None = None,
        car_type: str | None = None,
        year_min: int | None = None,
        year_max: int | None = None,
        mileage_max: int | None = None,
        user_priorities: str | None = None,
        user_id: int | None = None,
        db_session=None,
    ) -> dict[str, Any]:
        """
        Search for cars and get LLM recommendations with caching and history tracking

        Args:
            make: Vehicle make
            model: Vehicle model
            budget_min: Minimum budget
            budget_max: Maximum budget
            car_type: Type (new, used, certified)
            year_min: Minimum year
            year_max: Maximum year
            mileage_max: Maximum mileage
            user_priorities: User's specific priorities or preferences
            user_id: User ID for history tracking (optional)
            db_session: Database session for webhook operations (optional)

        Returns:
            Dictionary with search criteria and top vehicle recommendations
        """
        # Generate cache key
        cache_key = self._generate_cache_key(
            make,
            model,
            budget_min,
            budget_max,
            car_type,
            year_min,
            year_max,
            mileage_max,
            user_priorities,
        )

        # Check cache first
        cached_result = await self._get_cached_result(cache_key)
        if cached_result:
            # Still log to search history even for cached results
            try:
                await search_history_repository.create_search_record(
                    user_id=user_id,
                    search_criteria=cached_result.get("search_criteria", {}),
                    result_count=cached_result.get("total_found", 0),
                    top_vehicles=cached_result.get("top_vehicles", []),
                )
            except Exception as e:
                logger.error(f"Error logging cached search to history: {e}")

            return cached_result

        # Search MarketCheck API with retry logic
        try:
            api_response = await self._search_marketcheck_with_retry(
                make=make,
                model=model,
                car_type=car_type,
                min_price=budget_min,
                max_price=budget_max,
                min_year=year_min,
                max_year=year_max,
                max_mileage=mileage_max,
                rows=50,  # Get up to 50 results for LLM analysis
            )
        except Exception as e:
            logger.error(f"MarketCheck API failed after retries: {e}")
            raise

        # Parse listings
        listings = api_response.get("listings", [])
        num_found = api_response.get("num_found", 0)

        search_criteria = self._build_search_criteria(
            make, model, budget_min, budget_max, car_type, year_min, year_max, mileage_max
        )

        if not listings:
            result = {
                "search_criteria": search_criteria,
                "top_vehicles": [],
                "total_found": num_found,
                "message": "No vehicles found matching your criteria.",
            }

            # Cache empty result
            await self._set_cached_result(cache_key, result)

            # Log to history
            try:
                await search_history_repository.create_search_record(
                    user_id=user_id,
                    search_criteria=search_criteria,
                    result_count=0,
                    top_vehicles=[],
                )
            except Exception as e:
                logger.error(f"Error logging search to history: {e}")

            return result

        # Parse listings to standardized format
        parsed_listings = [marketcheck_client.parse_listing(listing) for listing in listings]

        # Get LLM recommendations
        if llm_client.is_available():
            top_vehicles = await self._get_llm_recommendations(
                parsed_listings, make, model, car_type, user_priorities
            )
        else:
            # Fallback: simple sorting by price and mileage
            top_vehicles = self._fallback_recommendations(parsed_listings)

        result = {
            "search_criteria": search_criteria,
            "top_vehicles": top_vehicles[:5],  # Limit to top 5
            "total_found": num_found,
            "total_analyzed": len(listings),
        }

        # Cache result
        await self._set_cached_result(cache_key, result)

        # Log to search history
        try:
            await search_history_repository.create_search_record(
                user_id=user_id,
                search_criteria=search_criteria,
                result_count=num_found,
                top_vehicles=top_vehicles[:5],
            )
        except Exception as e:
            logger.error(f"Error logging search to history: {e}")

        # Trigger webhooks for new vehicles
        try:
            await self._trigger_webhooks(top_vehicles[:5], db_session)
        except Exception as e:
            logger.error(f"Error triggering webhooks: {e}")

        return result

    async def _get_llm_recommendations(
        self,
        listings: list[dict[str, Any]],
        make: str | None,
        model: str | None,
        car_type: str | None,
        user_priorities: str | None,
    ) -> list[dict[str, Any]]:
        """Use LLM to analyze and recommend top vehicles"""

        # Prepare data for LLM
        listings_summary = []
        for idx, listing in enumerate(listings):
            summary = {
                "index": idx,
                "make": listing.get("make"),
                "model": listing.get("model"),
                "year": listing.get("year"),
                "trim": listing.get("trim"),
                "price": listing.get("price"),
                "mileage": listing.get("mileage"),
                "location": listing.get("location"),
                "exterior_color": listing.get("exterior_color"),
                "drivetrain": listing.get("drivetrain"),
                "carfax_1_owner": listing.get("carfax_1_owner"),
                "carfax_clean_title": listing.get("carfax_clean_title"),
                "days_on_market": listing.get("days_on_market"),
                "inventory_type": listing.get("inventory_type"),
            }
            listings_summary.append(summary)

        # Build prompt
        user_criteria = {
            "make": make,
            "model": model,
            "car_type": car_type,
            "priorities": user_priorities or "Best overall value and reliability",
        }

        try:
            # Use the LLM module to generate structured recommendations
            response = await generate_structured_json(
                prompt_id="car_selection_from_list",
                variables={
                    "user_criteria": json.dumps(user_criteria, indent=2),
                    "listings_summary": json.dumps(listings_summary, indent=2),
                },
                response_model=CarSelectionResponse,
                temperature=0.3,  # Lower temperature for more consistent recommendations
            )

            recommendations = response.recommendations


            # Build final output with full vehicle data
            top_vehicles = []
            for rec in recommendations:
                idx = rec.index
                if idx is not None and 0 <= idx < len(listings):
                    vehicle = listings[idx].copy()
                    vehicle["recommendation_score"] = rec.score
                    vehicle["highlights"] = rec.highlights
                    vehicle["recommendation_summary"] = rec.summary
                    top_vehicles.append(vehicle)

            return top_vehicles

        except Exception as e:
            logger.error(f"LLM recommendation error: {e}")
            # Fallback to simple sorting
            return self._fallback_recommendations(listings)

    def _fallback_recommendations(self, listings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Fallback recommendation logic when LLM is not available"""
        # Simple scoring based on price, mileage, and condition
        scored_listings = []

        for listing in listings:
            score = 5.0  # Base score

            # Bonus for clean title
            if listing.get("carfax_clean_title"):
                score += 1.0

            # Bonus for single owner
            if listing.get("carfax_1_owner"):
                score += 0.5

            # Bonus for lower mileage (relative)
            mileage = listing.get("mileage") or 999999
            if mileage < 30000:
                score += 1.5
            elif mileage < 50000:
                score += 1.0
            elif mileage < 75000:
                score += 0.5

            # Bonus for newer cars
            year = listing.get("year") or 2000
            if year >= 2023:
                score += 1.5
            elif year >= 2020:
                score += 1.0
            elif year >= 2018:
                score += 0.5

            listing["recommendation_score"] = round(score, 1)
            listing["highlights"] = self._generate_fallback_highlights(listing)
            listing["recommendation_summary"] = "Good option based on condition and features."
            scored_listings.append(listing)

        # Sort by score
        scored_listings.sort(key=lambda x: x["recommendation_score"], reverse=True)
        return scored_listings[:5]

    def _generate_fallback_highlights(self, listing: dict[str, Any]) -> list[str]:
        """Generate highlights when LLM is not available"""
        highlights = []

        if listing.get("carfax_clean_title"):
            highlights.append("Clean title verified")
        if listing.get("carfax_1_owner"):
            highlights.append("Single owner vehicle")

        mileage = listing.get("mileage")
        if mileage and mileage < 50000:
            highlights.append(f"Low mileage: {mileage:,} miles")

        year = listing.get("year")
        if year and year >= 2022:
            highlights.append(f"Recent model: {year}")

        if not highlights:
            highlights.append("Available for viewing")

        return highlights[:3]

    def _build_search_criteria(
        self,
        make: str | None,
        model: str | None,
        budget_min: int | None,
        budget_max: int | None,
        car_type: str | None,
        year_min: int | None,
        year_max: int | None,
        mileage_max: int | None,
    ) -> dict[str, Any]:
        """Build search criteria object for response"""
        return {
            "make": make,
            "model": model,
            "price_min": budget_min,
            "price_max": budget_max,
            "condition": car_type,
            "year_min": year_min,
            "year_max": year_max,
            "mileage_max": mileage_max,
            "location": None,  # Can be added later
        }


# Singleton instance
car_recommendation_service = CarRecommendationService()
