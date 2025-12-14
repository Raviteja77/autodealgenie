"""
Car Recommendation Service with LLM Integration
Analyzes and ranks vehicle listings based on user criteria
"""

import json
from typing import Any

from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.tools.marketcheck_client import marketcheck_client


class CarRecommendationService:
    """Service for recommending cars using LLM analysis"""

    SYSTEM_PROMPT = """You are an expert automotive advisor helping customers find their ideal vehicle.

Your role is to:
1. Analyze vehicle listings from the MarketCheck API
2. Evaluate each vehicle based on multiple factors: value, condition, features, mileage, and reliability
3. Select the top 5 vehicles that best match the user's criteria
4. Provide clear reasoning for each recommendation

Evaluation Criteria:
- **Value**: Price relative to market value, features, and condition
- **Condition**: Mileage, age, ownership history (clean title, single owner)
- **Features**: Trim level, drivetrain, technology packages
- **Reliability**: Known reliability ratings for the make/model/year
- **Market Position**: Days on market, price trends, dealer reputation

For each recommended vehicle, provide:
1. A confidence score (1-10) indicating how well it matches the criteria
2. Key highlights (top 3 reasons to consider this vehicle)
3. A brief recommendation summary

Be objective, data-driven, and focus on helping the user make an informed decision."""

    def __init__(self):
        if not settings.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not set. Car recommendation features will be limited.")
            self.llm = None
        else:
            self.llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                openai_api_key=settings.OPENAI_API_KEY,
                temperature=0.3,  # Lower temperature for more consistent recommendations
            )

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
    ) -> dict[str, Any]:
        """
        Search for cars and get LLM recommendations

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

        Returns:
            Dictionary with search criteria and top vehicle recommendations
        """
        # Search MarketCheck API
        api_response = await marketcheck_client.search_cars(
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

        # Parse listings
        listings = api_response.get("listings", [])
        num_found = api_response.get("num_found", 0)

        if not listings:
            return {
                "search_criteria": self._build_search_criteria(
                    make,
                    model,
                    budget_min,
                    budget_max,
                    car_type,
                    year_min,
                    year_max,
                    mileage_max,
                ),
                "top_vehicles": [],
                "total_found": num_found,
                "message": "No vehicles found matching your criteria.",
            }

        # Parse listings to standardized format
        parsed_listings = [marketcheck_client.parse_listing(listing) for listing in listings]

        # Get LLM recommendations
        if self.llm:
            top_vehicles = await self._get_llm_recommendations(
                parsed_listings, make, model, car_type, user_priorities
            )
        else:
            # Fallback: simple sorting by price and mileage
            top_vehicles = self._fallback_recommendations(parsed_listings)

        return {
            "search_criteria": self._build_search_criteria(
                make, model, budget_min, budget_max, car_type, year_min, year_max, mileage_max
            ),
            "top_vehicles": top_vehicles[:5],  # Limit to top 5
            "total_found": num_found,
            "total_analyzed": len(listings),
        }

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

        prompt = f"""Analyze these {len(listings_summary)} vehicles and select the TOP 5 that best match the user's criteria.

User Criteria:
{json.dumps(user_criteria, indent=2)}

Available Vehicles:
{json.dumps(listings_summary, indent=2)}

Provide a JSON response with EXACTLY this structure:
{{
  "recommendations": [
    {{
      "index": 0,
      "score": 9.5,
      "highlights": ["Excellent value at $X under market", "Low mileage for year", "Clean Carfax, single owner"],
      "summary": "This {make} {model} offers exceptional value with verified low mileage and clean history."
    }}
  ]
}}

Select exactly 5 vehicles and rank them by score (highest first). Be specific with highlights and summaries."""

        try:
            messages = [
                SystemMessage(content=self.SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]

            response = await self.llm.ainvoke(messages)
            llm_output = response.content

            # Parse LLM response - extract JSON from markdown code blocks
            if "```json" in llm_output:
                json_start = llm_output.find("```json") + 7
                json_end = llm_output.find("```", json_start)
                if json_end != -1:
                    llm_output = llm_output[json_start:json_end].strip()
            elif "```" in llm_output:
                json_start = llm_output.find("```") + 3
                json_end = llm_output.find("```", json_start)
                if json_end != -1:
                    llm_output = llm_output[json_start:json_end].strip()

            try:
                recommendations_data = json.loads(llm_output)
            except json.JSONDecodeError as parse_error:
                print(f"Failed to parse LLM JSON response: {parse_error}")
                print(f"LLM output: {llm_output}")
                return self._fallback_recommendations(listings)

            recommendations = recommendations_data.get("recommendations", [])

            # Build final output with full vehicle data
            top_vehicles = []
            for rec in recommendations:
                idx = rec.get("index")
                if idx is not None and 0 <= idx < len(listings):
                    vehicle = listings[idx].copy()
                    vehicle["recommendation_score"] = rec.get("score")
                    vehicle["highlights"] = rec.get("highlights", [])
                    vehicle["recommendation_summary"] = rec.get("summary", "")
                    top_vehicles.append(vehicle)

            return top_vehicles

        except Exception as e:
            print(f"LLM recommendation error: {e}")
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
