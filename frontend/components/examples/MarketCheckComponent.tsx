/**
 * Example component demonstrating mock Market Check API usage
 * Shows how to search for cars using either real or mock backend
 */

"use client";

import React, { useState } from "react";
import { Box, Typography, CircularProgress, Alert } from "@mui/material";
import { apiClient, CarSearchRequest, CarSearchResponse } from "@/lib/api";
import Button from "../ui/Button";
import Input from "../ui/Input";
import Card from "../ui/Card";

export default function MarketCheckComponent() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<CarSearchResponse | null>(null);
  const [searchParams, setSearchParams] = useState<CarSearchRequest>({
    make: "Honda",
    model: "Accord",
    budget_min: 20000,
    budget_max: 40000,
  });

  const handleSearch = async () => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await apiClient.searchCars(searchParams);
      setResults(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to search cars");
    } finally {
      setLoading(false);
    }
  };

  const useMock = process.env.NEXT_PUBLIC_USE_MOCK === "true";

  return (
    <Box sx={{ maxWidth: 800, mx: "auto", p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Market Check API Example
      </Typography>

      <Alert severity={useMock ? "info" : "success"} sx={{ mb: 3 }}>
        {useMock
          ? "Using MOCK backend - enable with NEXT_PUBLIC_USE_MOCK=true"
          : "Using REAL backend - disable mocks with NEXT_PUBLIC_USE_MOCK=false"}
      </Alert>

      <Card sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Search Parameters
        </Typography>

        <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
          <Input
            label="Make"
            value={searchParams.make || ""}
            onChange={(e) =>
              setSearchParams({ ...searchParams, make: e.target.value })
            }
            placeholder="e.g., Honda, Toyota"
          />

          <Input
            label="Model"
            value={searchParams.model || ""}
            onChange={(e) =>
              setSearchParams({ ...searchParams, model: e.target.value })
            }
            placeholder="e.g., Accord, Camry"
          />

          <Box sx={{ display: "flex", gap: 2 }}>
            <Input
              label="Min Budget"
              type="number"
              value={searchParams.budget_min || ""}
              onChange={(e) =>
                setSearchParams({
                  ...searchParams,
                  budget_min: parseInt(e.target.value) || undefined,
                })
              }
            />

            <Input
              label="Max Budget"
              type="number"
              value={searchParams.budget_max || ""}
              onChange={(e) =>
                setSearchParams({
                  ...searchParams,
                  budget_max: parseInt(e.target.value) || undefined,
                })
              }
            />
          </Box>

          <Button
            onClick={handleSearch}
            disabled={loading}
            variant="primary"
            fullWidth
          >
            {loading ? <CircularProgress size={24} /> : "Search Cars"}
          </Button>
        </Box>
      </Card>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {results && (
        <Card sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Search Results
          </Typography>

          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Found {results.total_found} vehicles (showing top{" "}
            {results.top_vehicles.length})
          </Typography>

          <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            {results.top_vehicles.map((vehicle, index) => (
              <Card key={vehicle.vin || index} variant="outlined" sx={{ p: 2 }}>
                <Typography variant="subtitle1" fontWeight="bold">
                  {vehicle.year} {vehicle.make} {vehicle.model} {vehicle.trim}
                </Typography>

                <Typography variant="h6" color="primary.main">
                  ${vehicle.price?.toLocaleString()}
                </Typography>

                <Typography variant="body2" color="text.secondary">
                  {vehicle.mileage?.toLocaleString()} miles • {vehicle.location}
                </Typography>

                {vehicle.recommendation_score && (
                  <Typography variant="body2" color="success.main">
                    Score: {vehicle.recommendation_score}/10
                  </Typography>
                )}

                {vehicle.highlights && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                      Highlights:
                    </Typography>
                    <ul style={{ margin: "4px 0", paddingLeft: "20px" }}>
                      {vehicle.highlights.map((highlight, idx) => (
                        <li key={idx}>
                          <Typography variant="caption">{highlight}</Typography>
                        </li>
                      ))}
                    </ul>
                  </Box>
                )}
              </Card>
            ))}
          </Box>
        </Card>
      )}
    </Box>
  );
}
