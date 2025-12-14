"use client";

import { useState } from "react";
import Link from "next/link";
import {
  apiClient,
  CarSearchRequest,
  CarSearchResponse,
  VehicleRecommendation,
} from "@/lib/api";

export default function CarSearchPage() {
  const [searchParams, setSearchParams] = useState<CarSearchRequest>({
    make: "",
    model: "",
    budget_min: undefined,
    budget_max: undefined,
    car_type: "used",
    year_min: undefined,
    year_max: undefined,
    mileage_max: undefined,
    user_priorities: "",
  });

  const [results, setResults] = useState<CarSearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Filter out empty values
      const filteredParams: CarSearchRequest = {};
      if (searchParams.make) filteredParams.make = searchParams.make;
      if (searchParams.model) filteredParams.model = searchParams.model;
      if (searchParams.budget_min)
        filteredParams.budget_min = searchParams.budget_min;
      if (searchParams.budget_max)
        filteredParams.budget_max = searchParams.budget_max;
      if (searchParams.car_type)
        filteredParams.car_type = searchParams.car_type;
      if (searchParams.year_min)
        filteredParams.year_min = searchParams.year_min;
      if (searchParams.year_max)
        filteredParams.year_max = searchParams.year_max;
      if (searchParams.mileage_max)
        filteredParams.mileage_max = searchParams.mileage_max;
      if (searchParams.user_priorities)
        filteredParams.user_priorities = searchParams.user_priorities;

      const response = await apiClient.searchCars(filteredParams);
      setResults(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
    } finally {
      setLoading(false);
    }
  };

  const updateParam = (
    key: keyof CarSearchRequest,
    value: string | number | undefined,
  ) => {
    setSearchParams((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              AI-Powered Car Search
            </h1>
            <p className="text-gray-600 dark:text-gray-300 mt-2">
              Find your perfect vehicle with intelligent recommendations
            </p>
          </div>
          <Link
            href="/"
            className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded transition-colors"
          >
            Home
          </Link>
        </div>

        {/* Search Form */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
          <form onSubmit={handleSearch} className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              {/* Make */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Make
                </label>
                <input
                  type="text"
                  placeholder="e.g., Toyota"
                  value={searchParams.make}
                  onChange={(e) => updateParam("make", e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>

              {/* Model */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Model
                </label>
                <input
                  type="text"
                  placeholder="e.g., RAV4"
                  value={searchParams.model}
                  onChange={(e) => updateParam("model", e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>

              {/* Budget Min */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Min Budget ($)
                </label>
                <input
                  type="number"
                  placeholder="e.g., 20000"
                  value={searchParams.budget_min || ""}
                  onChange={(e) =>
                    updateParam(
                      "budget_min",
                      e.target.value ? parseInt(e.target.value) : undefined,
                    )
                  }
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>

              {/* Budget Max */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Max Budget ($)
                </label>
                <input
                  type="number"
                  placeholder="e.g., 40000"
                  value={searchParams.budget_max || ""}
                  onChange={(e) =>
                    updateParam(
                      "budget_max",
                      e.target.value ? parseInt(e.target.value) : undefined,
                    )
                  }
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>

              {/* Car Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Condition
                </label>
                <select
                  value={searchParams.car_type}
                  onChange={(e) => updateParam("car_type", e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                >
                  <option value="">Any</option>
                  <option value="new">New</option>
                  <option value="used">Used</option>
                  <option value="certified">Certified Pre-Owned</option>
                </select>
              </div>

              {/* Year Min */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Min Year
                </label>
                <input
                  type="number"
                  placeholder="e.g., 2020"
                  value={searchParams.year_min || ""}
                  onChange={(e) =>
                    updateParam(
                      "year_min",
                      e.target.value ? parseInt(e.target.value) : undefined,
                    )
                  }
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>

              {/* Year Max */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Max Year
                </label>
                <input
                  type="number"
                  placeholder="e.g., 2024"
                  value={searchParams.year_max || ""}
                  onChange={(e) =>
                    updateParam(
                      "year_max",
                      e.target.value ? parseInt(e.target.value) : undefined,
                    )
                  }
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>

              {/* Max Mileage */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Max Mileage
                </label>
                <input
                  type="number"
                  placeholder="e.g., 50000"
                  value={searchParams.mileage_max || ""}
                  onChange={(e) =>
                    updateParam(
                      "mileage_max",
                      e.target.value ? parseInt(e.target.value) : undefined,
                    )
                  }
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
            </div>

            {/* User Priorities */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Your Priorities (Optional)
              </label>
              <textarea
                placeholder="e.g., I need a reliable family car with good fuel economy"
                value={searchParams.user_priorities}
                onChange={(e) => updateParam("user_priorities", e.target.value)}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold px-6 py-3 rounded-lg transition-colors"
            >
              {loading ? "Searching..." : "Search Cars with AI"}
            </button>
          </form>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-8">
            <p className="font-semibold">Error:</p>
            <p>{error}</p>
            <p className="text-sm mt-2">
              Make sure the backend is running at{" "}
              {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}
              and MARKET_CHECK_API_KEY is configured.
            </p>
          </div>
        )}

        {/* Results */}
        {results && (
          <div>
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                AI-Selected Recommendations
              </h2>
              <p className="text-gray-600 dark:text-gray-300">
                Found {results.total_found} vehicles, analyzed{" "}
                {results.total_analyzed}, showing top{" "}
                {results.top_vehicles.length}
              </p>
            </div>

            {results.top_vehicles.length === 0 ? (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8 text-center">
                <p className="text-gray-600 dark:text-gray-300">
                  {results.message ||
                    "No vehicles found matching your criteria. Try adjusting your search parameters."}
                </p>
              </div>
            ) : (
              <div className="grid gap-6">
                {results.top_vehicles.map((vehicle, index) => (
                  <VehicleCard
                    key={vehicle.vin || index}
                    vehicle={vehicle}
                    rank={index + 1}
                  />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function VehicleCard({
  vehicle,
  rank,
}: {
  vehicle: VehicleRecommendation;
  rank: number;
}) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
      <div className="md:flex">
        {/* Image Gallery */}
        <div className="md:w-2/5">
          {vehicle.photo_links && vehicle.photo_links.length > 0 ? (
            <div className="relative h-64 md:h-full">
              <img
                src={vehicle.photo_links[0]}
                alt={`${vehicle.year} ${vehicle.make} ${vehicle.model}`}
                className="w-full h-full object-cover"
              />
              <div className="absolute top-4 left-4 bg-blue-600 text-white px-3 py-1 rounded-full font-semibold">
                #{rank} AI Pick
              </div>
              {vehicle.recommendation_score && (
                <div className="absolute top-4 right-4 bg-green-600 text-white px-3 py-1 rounded-full font-semibold">
                  Score: {vehicle.recommendation_score.toFixed(1)}/10
                </div>
              )}
            </div>
          ) : (
            <div className="h-64 md:h-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
              <span className="text-gray-400">No image available</span>
            </div>
          )}
        </div>

        {/* Details */}
        <div className="md:w-3/5 p-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                {vehicle.year} {vehicle.make} {vehicle.model}
              </h3>
              {vehicle.trim && (
                <p className="text-gray-600 dark:text-gray-300">
                  {vehicle.trim}
                </p>
              )}
            </div>
            <div className="text-right">
              <p className="text-3xl font-bold text-blue-600">
                ${vehicle.price?.toLocaleString()}
              </p>
              {vehicle.msrp && vehicle.msrp !== vehicle.price && (
                <p className="text-sm text-gray-500 line-through">
                  MSRP: ${vehicle.msrp.toLocaleString()}
                </p>
              )}
            </div>
          </div>

          {/* AI Recommendation */}
          {vehicle.recommendation_summary && (
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-4">
              <p className="text-sm font-semibold text-blue-900 dark:text-blue-300 mb-2">
                🤖 AI Recommendation:
              </p>
              <p className="text-sm text-gray-700 dark:text-gray-300">
                {vehicle.recommendation_summary}
              </p>
            </div>
          )}

          {/* Highlights */}
          {vehicle.highlights && vehicle.highlights.length > 0 && (
            <div className="mb-4">
              <p className="font-semibold text-gray-900 dark:text-white mb-2">
                ✨ Key Highlights:
              </p>
              <ul className="space-y-1">
                {vehicle.highlights.map((highlight, idx) => (
                  <li
                    key={idx}
                    className="text-sm text-gray-600 dark:text-gray-300 flex items-start"
                  >
                    <span className="text-green-600 mr-2">✓</span>
                    {highlight}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Specs Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4 text-sm">
            <div>
              <span className="text-gray-500 dark:text-gray-400">Mileage:</span>
              <p className="font-semibold text-gray-900 dark:text-white">
                {vehicle.mileage?.toLocaleString()} mi
              </p>
            </div>
            {vehicle.drivetrain && (
              <div>
                <span className="text-gray-500 dark:text-gray-400">
                  Drivetrain:
                </span>
                <p className="font-semibold text-gray-900 dark:text-white">
                  {vehicle.drivetrain}
                </p>
              </div>
            )}
            {vehicle.exterior_color && (
              <div>
                <span className="text-gray-500 dark:text-gray-400">Color:</span>
                <p className="font-semibold text-gray-900 dark:text-white">
                  {vehicle.exterior_color}
                </p>
              </div>
            )}
            {vehicle.transmission && (
              <div>
                <span className="text-gray-500 dark:text-gray-400">
                  Transmission:
                </span>
                <p className="font-semibold text-gray-900 dark:text-white">
                  {vehicle.transmission}
                </p>
              </div>
            )}
            {vehicle.fuel_type && (
              <div>
                <span className="text-gray-500 dark:text-gray-400">Fuel:</span>
                <p className="font-semibold text-gray-900 dark:text-white">
                  {vehicle.fuel_type}
                </p>
              </div>
            )}
          </div>

          {/* Badges */}
          <div className="flex flex-wrap gap-2 mb-4">
            {vehicle.carfax_clean_title && (
              <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                Clean Title
              </span>
            )}
            {vehicle.carfax_1_owner && (
              <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                1 Owner
              </span>
            )}
            {vehicle.inventory_type && (
              <span className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded capitalize">
                {vehicle.inventory_type}
              </span>
            )}
          </div>

          {/* Dealer Info */}
          {vehicle.dealer_name && (
            <div className="border-t dark:border-gray-700 pt-4 mb-4">
              <p className="text-sm font-semibold text-gray-900 dark:text-white">
                {vehicle.dealer_name}
              </p>
              {vehicle.location && (
                <p className="text-sm text-gray-600 dark:text-gray-300">
                  📍 {vehicle.location}
                </p>
              )}
              {vehicle.dealer_contact && (
                <p className="text-sm text-gray-600 dark:text-gray-300">
                  📞 {vehicle.dealer_contact}
                </p>
              )}
            </div>
          )}

          {/* Action Button */}
          {vehicle.vdp_url && (
            <a
              href={vehicle.vdp_url}
              target="_blank"
              rel="noopener noreferrer"
              className="block w-full bg-blue-600 hover:bg-blue-700 text-white text-center font-semibold px-6 py-3 rounded-lg transition-colors"
            >
              View Details on Dealer Site →
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
