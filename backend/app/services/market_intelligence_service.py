"""
Market Intelligence Service

Provides real-time market data and pricing intelligence for negotiations.
Leverages MarketCheck API to provide comparative analysis, pricing trends,
and market positioning data.
"""

import logging
from datetime import datetime
from typing import Any

from app.services.marketcheck_service import MarketCheckService
from app.utils.error_handler import ApiError

logger = logging.getLogger(__name__)


class MarketIntelligenceService:
    """
    Service for market intelligence and pricing analysis

    Provides:
    - Real-time comparable vehicle pricing
    - Historical price trends
    - Market demand indicators
    - Competitive positioning analysis
    """

    def __init__(self, marketcheck_service: MarketCheckService | None = None):
        """
        Initialize MarketIntelligenceService

        Args:
            marketcheck_service: Optional MarketCheckService instance
        """
        self.marketcheck_service = marketcheck_service or MarketCheckService()

    async def get_real_time_comps(
        self,
        make: str,
        model: str,
        year: int,
        mileage: int,
        zip_code: str | None = None,
        radius: int = 50,
        max_results: int = 10,
    ) -> dict[str, Any]:
        """
        Get real-time comparable vehicle listings

        Args:
            make: Vehicle make
            model: Vehicle model
            year: Vehicle year
            mileage: Current mileage
            zip_code: Optional location for search
            radius: Search radius in miles
            max_results: Maximum number of comparables to return

        Returns:
            Dictionary with comparable listings and market analysis:
            {
                "comparables": list[dict],
                "average_price": float,
                "median_price": float,
                "price_range": {"min": float, "max": float},
                "total_found": int,
                "market_summary": str,
                "last_updated": str
            }
        """
        logger.info(
            f"Getting real-time comps for {year} {make} {model}, "
            f"mileage: {mileage}, location: {zip_code}"
        )

        if not self.marketcheck_service.is_available():
            logger.warning("MarketCheck API not available, returning limited data")
            return self._get_fallback_comps()

        try:
            # Search for comparable vehicles
            # Allow +/- 10,000 miles and +/- 1 year
            search_result = await self.marketcheck_service.search_vehicles(
                make=make,
                model=model,
                min_year=year - 1,
                max_year=year + 1,
                max_mileage=mileage + 10000,
                car_type="used",
                zip_code=zip_code,
                radius=radius,
                rows=max_results,
                sort_by="price",
                use_cache=True,
            )

            comparables = search_result.get("listings", [])
            total_found = search_result.get("num_found", 0)

            if not comparables:
                logger.warning("No comparable vehicles found")
                return self._get_fallback_comps()

            # Calculate statistics
            prices = [comp["price"] for comp in comparables if comp.get("price")]

            if not prices:
                logger.warning("No prices found in comparables")
                return self._get_fallback_comps()

            average_price = sum(prices) / len(prices)
            median_price = sorted(prices)[len(prices) // 2]
            min_price = min(prices)
            max_price = max(prices)

            # Generate market summary
            market_summary = self._generate_market_summary(
                total_found=total_found,
                average_price=average_price,
                median_price=median_price,
                price_range=(min_price, max_price),
            )

            return {
                "comparables": comparables,
                "average_price": round(average_price, 2),
                "median_price": round(median_price, 2),
                "price_range": {
                    "min": round(min_price, 2),
                    "max": round(max_price, 2),
                },
                "total_found": total_found,
                "market_summary": market_summary,
                "last_updated": datetime.utcnow().isoformat(),
            }

        except ApiError:
            raise
        except Exception as e:
            logger.error(f"Error getting real-time comps: {e}", exc_info=True)
            return self._get_fallback_comps()

    async def get_price_trend(
        self,
        make: str,
        model: str,
        year: int,
        zip_code: str | None = None,
    ) -> dict[str, Any]:
        """
        Get historical price trend data for a vehicle

        Args:
            make: Vehicle make
            model: Vehicle model
            year: Vehicle year
            zip_code: Optional location for regional trends

        Returns:
            Dictionary with price trend analysis:
            {
                "trend_direction": str,  # "increasing", "decreasing", "stable"
                "price_change_percent": float,
                "demand_level": str,  # "high", "medium", "low"
                "market_days_supply": float,
                "recommendation": str,
                "last_updated": str
            }
        """
        logger.info(f"Getting price trend for {year} {make} {model}")

        if not self.marketcheck_service.is_available():
            logger.warning("MarketCheck API not available, returning limited data")
            return self._get_fallback_trend()

        try:
            # Get Market Days Supply (MDS) as an indicator of demand
            mds_data = await self.marketcheck_service.get_market_days_supply(
                make=make,
                model=model,
                year=year,
                zip_code=zip_code,
                use_cache=True,
            )

            demand_level = mds_data.get("demand_level", "medium")
            mds_value = mds_data.get("mds", 45)
            trend = mds_data.get("trend", "stable")

            # Map trend to direction
            trend_direction = self._map_trend_to_direction(trend)

            # Estimate price change based on MDS and demand
            price_change_percent = self._estimate_price_change(demand_level, mds_value)

            # Generate recommendation
            recommendation = self._generate_price_trend_recommendation(
                trend_direction=trend_direction,
                demand_level=demand_level,
                price_change_percent=price_change_percent,
            )

            return {
                "trend_direction": trend_direction,
                "price_change_percent": round(price_change_percent, 2),
                "demand_level": demand_level,
                "market_days_supply": round(mds_value, 1),
                "recommendation": recommendation,
                "last_updated": datetime.utcnow().isoformat(),
            }

        except ApiError:
            raise
        except Exception as e:
            logger.error(f"Error getting price trend: {e}", exc_info=True)
            return self._get_fallback_trend()

    def _get_fallback_comps(self) -> dict[str, Any]:
        """Return fallback comparable data when MarketCheck is unavailable"""
        return {
            "comparables": [],
            "average_price": 0.0,
            "median_price": 0.0,
            "price_range": {"min": 0.0, "max": 0.0},
            "total_found": 0,
            "market_summary": "Market data temporarily unavailable. Using historical averages.",
            "last_updated": datetime.utcnow().isoformat(),
        }

    def _get_fallback_trend(self) -> dict[str, Any]:
        """Return fallback trend data when MarketCheck is unavailable"""
        return {
            "trend_direction": "stable",
            "price_change_percent": 0.0,
            "demand_level": "medium",
            "market_days_supply": 45.0,
            "recommendation": "Market data temporarily unavailable. Proceed with standard negotiation strategy.",
            "last_updated": datetime.utcnow().isoformat(),
        }

    def _generate_market_summary(
        self,
        total_found: int,
        average_price: float,
        median_price: float,
        price_range: tuple[float, float],
    ) -> str:
        """Generate a human-readable market summary"""
        min_price, max_price = price_range
        price_spread = max_price - min_price
        spread_percent = (price_spread / average_price * 100) if average_price > 0 else 0

        summary = f"Found {total_found} comparable vehicles. "
        summary += f"Average price: ${average_price:,.0f}, Median: ${median_price:,.0f}. "

        if spread_percent > 20:
            summary += "Wide price variation indicates diverse market conditions."
        elif spread_percent > 10:
            summary += "Moderate price variation - typical competitive market."
        else:
            summary += "Narrow price range - highly consistent market pricing."

        return summary

    def _map_trend_to_direction(self, trend: str) -> str:
        """Map MarketCheck trend to simplified direction"""
        trend_lower = trend.lower()
        if "increas" in trend_lower or "ris" in trend_lower:
            return "increasing"
        elif "decreas" in trend_lower or "fall" in trend_lower or "declin" in trend_lower:
            return "decreasing"
        else:
            return "stable"

    def _estimate_price_change(self, demand_level: str, mds_value: float) -> float:
        """
        Estimate price change percentage based on demand and MDS

        Lower MDS = higher demand = increasing prices
        Higher MDS = lower demand = decreasing prices
        """
        if demand_level == "high" and mds_value < 30:
            return 2.5  # Prices increasing 2.5%
        elif demand_level == "high":
            return 1.0  # Prices increasing 1%
        elif demand_level == "low" and mds_value > 60:
            return -2.0  # Prices decreasing 2%
        elif demand_level == "low":
            return -1.0  # Prices decreasing 1%
        else:
            return 0.0  # Stable

    def _generate_price_trend_recommendation(
        self,
        trend_direction: str,
        demand_level: str,
        price_change_percent: float,
    ) -> str:
        """Generate actionable recommendation based on trend analysis"""
        if trend_direction == "increasing" and demand_level == "high":
            return (
                "Prices are trending upward with high demand. "
                "Consider negotiating quickly to lock in current pricing."
            )
        elif trend_direction == "decreasing" and demand_level == "low":
            return (
                "Prices are trending downward with low demand. "
                "You have strong negotiating leverage - aim for aggressive discounts."
            )
        elif trend_direction == "stable":
            return (
                "Market is stable. "
                "Negotiate strategically with standard discount expectations (5-10% off)."
            )
        else:
            return (
                "Mixed market signals. "
                "Focus on vehicle-specific factors and comparable pricing in your negotiation."
            )


# Singleton instance
market_intelligence_service = MarketIntelligenceService()
