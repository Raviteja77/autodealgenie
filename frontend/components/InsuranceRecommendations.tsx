"use client";

import { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Grid,
  Divider,
  Chip,
  Stack,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  Collapse,
  IconButton,
  Snackbar,
} from "@mui/material";
import {
  Shield as ShieldIcon,
  TrendingDown,
  CheckCircle,
  ExpandMore,
  ExpandLess,
  Star,
} from "@mui/icons-material";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import {
  apiClient,
  type InsuranceMatch,
  type InsuranceRecommendationResponse,
  type InsuranceRecommendationRequest,
} from "@/lib/api";
import {
  isApiError,
  isAuthenticationError,
  isNetworkError,
  getUserFriendlyErrorMessage,
} from "@/lib/errors";
import { formatPrice } from "@/lib/utils/formatting";

interface InsuranceRecommendationsProps {
  vehicleValue: number;
  vehicleAge: number;
  vehicleMake: string;
  vehicleModel: string;
  driverAge?: number;
  coverageType?: "liability" | "comprehensive" | "full";
  onProviderSelect?: (provider: InsuranceMatch) => void;
  showApplyButton?: boolean;
  compact?: boolean;
}

type SortOption = "match_score" | "premium_low" | "coverage_broad";

// Trusted insurance provider domains for URL validation
const TRUSTED_DOMAINS = [
  "progressive.com",
  "geico.com",
  "statefarm.com",
  "allstate.com",
  "libertymutual.com",
  "aarp.org",
  "nationwide.com",
  "travelers.com",
  "usaa.com",
  "farmersinsurance.com",
];

export function InsuranceRecommendations({
  vehicleValue,
  vehicleAge,
  vehicleMake,
  vehicleModel,
  driverAge = 30,
  coverageType = "full",
  onProviderSelect,
  showApplyButton = true,
  compact = false,
}: InsuranceRecommendationsProps) {
  const [providers, setProviders] = useState<InsuranceMatch[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<SortOption>("match_score");
  const [expandedProviders, setExpandedProviders] = useState<Set<string>>(new Set());
  const [selectedCoverage, setSelectedCoverage] = useState(coverageType);
  const [selectedDriverAge, setSelectedDriverAge] = useState(driverAge);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");

  useEffect(() => {
    const fetchProviders = async () => {
      if (vehicleValue <= 0) {
        setError("Vehicle value must be greater than $0. Please adjust your search criteria.");
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(null);

        const request: InsuranceRecommendationRequest = {
          vehicle_value: vehicleValue,
          vehicle_age: vehicleAge,
          vehicle_make: vehicleMake,
          vehicle_model: vehicleModel,
          coverage_type: selectedCoverage,
          driver_age: selectedDriverAge,
        };

        const response: InsuranceRecommendationResponse = await apiClient.getInsuranceRecommendations(
          loanAmount,
          vehicleMake,
          vehicleModel,
          selectedCoverage,
          selectedDriverAge
        );

        setProviders(response.recommendations || []);
      } catch (err) {
        console.error("Error fetching insurance providers:", err);

        // Use centralized error handling
        let errorMessage = getUserFriendlyErrorMessage(err);

        if (isAuthenticationError(err)) {
          errorMessage = "Please log in to view insurance recommendations.";
        } else if (isNetworkError(err)) {
          errorMessage = "Unable to connect to insurance service. Please check your connection.";
        } else if (isApiError(err) && err.statusCode === 400) {
          errorMessage = "Invalid vehicle or driver criteria. Please adjust your parameters.";
        }

        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    fetchProviders();
  }, [vehicleValue, vehicleAge, vehicleMake, vehicleModel, selectedCoverage, selectedDriverAge]);

  // Handle auto-expand logic separately to avoid unnecessary API calls
  useEffect(() => {
    if (!compact && providers.length > 0) {
      const topProviders = new Set(providers.slice(0, 2).map((p) => p.provider.provider_id));
      setExpandedProviders(topProviders);
    } else if (compact) {
      // Collapse all in compact mode
      setExpandedProviders(new Set());
    }
  }, [compact, providers]);

  const handleSortChange = (event: SelectChangeEvent<SortOption>) => {
    setSortBy(event.target.value as SortOption);
  };

  const handleCoverageChange = (event: SelectChangeEvent<string>) => {
    setSelectedCoverage(event.target.value as "liability" | "comprehensive" | "full");
  };

  const handleDriverAgeChange = (event: SelectChangeEvent<number>) => {
    setSelectedDriverAge(Number(event.target.value));
  };

  const toggleProviderExpansion = (providerId: string) => {
    setExpandedProviders((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(providerId)) {
        newSet.delete(providerId);
      } else {
        newSet.add(providerId);
      }
      return newSet;
    });
  };

  // Sort providers based on selected criteria
  const sortedProviders = [...providers].sort((a, b) => {
    switch (sortBy) {
      case "premium_low":
        return a.estimated_monthly_premium - b.estimated_monthly_premium;
      case "coverage_broad":
        return b.provider.coverage_types.length - a.provider.coverage_types.length;
      case "match_score":
      default:
        return b.match_score - a.match_score;
    }
  });

  if (isLoading) {
    return (
      <Card shadow="md">
        <Card.Body>
          <Box
            sx={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              py: 4,
            }}
          >
            <Spinner size="md" />
            <Typography variant="body2" color="text.secondary" sx={{ ml: 2 }}>
              Finding the best insurance providers for you...
            </Typography>
          </Box>
        </Card.Body>
      </Card>
    );
  }

  if (error) {
    return (
      <Card shadow="md">
        <Card.Body>
          <Alert severity="error">
            <Typography variant="body2">{error}</Typography>
          </Alert>
        </Card.Body>
      </Card>
    );
  }

  if (providers.length === 0) {
    return (
      <Card shadow="md">
        <Card.Body>
          <Alert severity="info">
            <Typography variant="body2">
              No insurance providers available for your criteria. Try adjusting your coverage type
              or driver age.
            </Typography>
          </Alert>
        </Card.Body>
      </Card>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 2,
          }}
        >
          <Typography variant="h5" fontWeight={700}>
            Insurance Recommendations
          </Typography>
          <Chip label={`${providers.length} Matches`} color="primary" size="small" />
        </Box>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Top insurance providers matched to your vehicle and driving profile
        </Typography>
      </Box>

      {/* Controls */}
      <Card shadow="sm" sx={{ mb: 3 }}>
        <Card.Body>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Sort By</InputLabel>
                <Select value={sortBy} label="Sort By" onChange={handleSortChange}>
                  <MenuItem value="match_score">Best Match</MenuItem>
                  <MenuItem value="premium_low">Lowest Premium</MenuItem>
                  <MenuItem value="coverage_broad">Most Coverage Options</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Coverage Type</InputLabel>
                <Select
                  value={selectedCoverage}
                  label="Coverage Type"
                  onChange={handleCoverageChange}
                >
                  <MenuItem value="liability">Liability Only</MenuItem>
                  <MenuItem value="comprehensive">Comprehensive</MenuItem>
                  <MenuItem value="full">Full Coverage</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Driver Age</InputLabel>
                <Select
                  value={selectedDriverAge}
                  label="Driver Age"
                  onChange={handleDriverAgeChange}
                >
                  <MenuItem value={18}>18-20 years</MenuItem>
                  <MenuItem value={21}>21-24 years</MenuItem>
                  <MenuItem value={25}>25-34 years</MenuItem>
                  <MenuItem value={35}>35-49 years</MenuItem>
                  <MenuItem value={50}>50-64 years</MenuItem>
                  <MenuItem value={65}>65+ years</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </Card.Body>
      </Card>

      {/* Provider List */}
      <Stack spacing={2}>
        {sortedProviders.map((match) => {
          const isExpanded = expandedProviders.has(match.provider.provider_id);
          const isTopMatch = match.rank === 1;

          return (
            <Card
              key={match.provider.provider_id}
              shadow={isTopMatch ? "lg" : "md"}
              sx={{
                border: isTopMatch ? 2 : 1,
                borderColor: isTopMatch ? "primary.main" : "divider",
                transition: "all 0.3s ease",
                "&:hover": {
                  boxShadow: 6,
                },
              }}
            >
              <Card.Body>
              {/* Header */}
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "start",
                  mb: 2,
                }}
              >
                <Box sx={{ flex: 1 }}>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 0.5 }}>
                    <ShieldIcon color="primary" />
                    <Typography variant="h6" fontWeight="bold">
                      {match.provider.name}
                    </Typography>
                    {isTopMatch && (
                      <Chip icon={<Star />} label="Best Match" color="primary" size="small" />
                    )}
                  </Box>
                  <Typography variant="caption" color="text.secondary">
                    {match.recommendation_reason}
                  </Typography>
                </Box>

                <Box sx={{ textAlign: "right" }}>
                  <Typography variant="h5" color="primary.main" fontWeight="bold">
                    {formatPrice(match.estimated_monthly_premium)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    per month
                  </Typography>
                </Box>
              </Box>

              {/* Key Metrics */}
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={4}>
                  <Typography variant="caption" color="text.secondary">
                    Annual Premium
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {formatPrice(match.estimated_annual_premium)}
                  </Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="caption" color="text.secondary">
                    Match Score
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {match.match_score.toFixed(0)}/100
                  </Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="caption" color="text.secondary">
                    Rank
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    #{match.rank}
                  </Typography>
                </Grid>
              </Grid>

              {/* Expandable Details */}
              <Box>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <IconButton
                    size="small"
                    onClick={() => toggleProviderExpansion(match.provider.provider_id)}
                    aria-label={
                      isExpanded ? "Collapse provider details" : "Expand provider details"
                    }
                    aria-expanded={isExpanded}
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 0.5,
                      textTransform: "none",
                      color: "text.primary",
                      "&:hover": {
                        backgroundColor: "action.hover",
                      },
                    }}
                  >
                    <Typography variant="subtitle2">View Details</Typography>
                    {isExpanded ? <ExpandLess /> : <ExpandMore />}
                  </IconButton>
                </Box>

                <Collapse in={isExpanded}>
                  <Divider sx={{ my: 2 }} />

                  {/* Description */}
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {match.provider.description}
                  </Typography>

                  {/* Coverage Types */}
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom fontWeight={600}>
                      Coverage Options
                    </Typography>
                    <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
                      {match.provider.coverage_types.map((coverage, idx) => (
                        <Chip
                          key={idx}
                          label={coverage.charAt(0).toUpperCase() + coverage.slice(1)}
                          size="small"
                          variant="outlined"
                          color="primary"
                        />
                      ))}
                    </Box>
                  </Box>

                  {/* Features */}
                  {match.provider.features && match.provider.features.length > 0 && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" gutterBottom fontWeight={600}>
                        Features
                      </Typography>
                      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
                        {match.provider.features.map((feature, idx) => (
                          <Chip
                            key={idx}
                            icon={<CheckCircle />}
                            label={feature}
                            size="small"
                            variant="outlined"
                            color="success"
                          />
                        ))}
                      </Box>
                    </Box>
                  )}

                  {/* Benefits */}
                  {match.provider.benefits && match.provider.benefits.length > 0 && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" gutterBottom fontWeight={600}>
                        Benefits
                      </Typography>
                      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
                        {match.provider.benefits.map((benefit, idx) => (
                          <Chip
                            key={idx}
                            icon={<TrendingDown />}
                            label={benefit}
                            size="small"
                            variant="outlined"
                            color="info"
                          />
                        ))}
                      </Box>
                    </Box>
                  )}

                  {/* Provider Details */}
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom fontWeight={600}>
                      Provider Details
                    </Typography>
                    <Grid container spacing={1}>
                      <Grid item xs={6}>
                        <Typography variant="caption" color="text.secondary">
                          Premium Range
                        </Typography>
                        <Typography variant="body2">
                          {formatPrice(match.provider.premium_range_min)} -{" "}
                          {formatPrice(match.provider.premium_range_max)}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="caption" color="text.secondary">
                          Vehicle Value Range
                        </Typography>
                        <Typography variant="body2">
                          {formatPrice(match.provider.min_vehicle_value)} -{" "}
                          {formatPrice(match.provider.max_vehicle_value)}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="caption" color="text.secondary">
                          Driver Age Range
                        </Typography>
                        <Typography variant="body2">
                          {match.provider.min_driver_age} - {match.provider.max_driver_age} years
                        </Typography>
                      </Grid>
                    </Grid>
                  </Box>
                </Collapse>
              </Box>

              {/* Action Buttons */}
              <Box sx={{ display: "flex", gap: 1, mt: 2 }}>
                {showApplyButton && (
                  <Button
                    variant="success"
                    size="sm"
                    fullWidth
                    onClick={() => {
                      const url = match.provider.affiliate_url;
                      try {
                        if (!url) {
                          throw new Error("Missing affiliate URL");
                        }

                        // Use URL constructor to validate structure
                        const urlObj = new URL(url);

                        // Verify it's http or https
                        if (!["http:", "https:"].includes(urlObj.protocol)) {
                          throw new Error("Invalid URL protocol");
                        }

                        // Validate against trusted domains
                        const hostname = urlObj.hostname.toLowerCase();
                        const isTrusted = TRUSTED_DOMAINS.some((domain) =>
                          hostname.endsWith(domain)
                        );

                        if (!isTrusted) {
                          throw new Error("Untrusted domain");
                        }

                        window.open(url, "_blank", "noopener,noreferrer");
                      } catch (error) {
                        console.error("Invalid affiliate URL:", url, error);
                        setSnackbarMessage(
                          "This provider link is currently unavailable. Please try another provider or contact support."
                        );
                        setSnackbarOpen(true);
                      }
                    }}
                    aria-label="Get quote, opens in new tab"
                  >
                    Get Quote
                  </Button>
                )}
                {onProviderSelect && (
                  <Button
                    variant="outline"
                    size="sm"
                    fullWidth
                    onClick={() => onProviderSelect(match)}
                  >
                    Select Provider
                  </Button>
                )}
              </Box>
            </Card.Body>
            </Card>
          );
        })}
      </Stack>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
        message={snackbarMessage}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      />

      {/* Footer Info */}
      <Alert severity="info" sx={{ mt: 3 }}>
        <Typography variant="caption">
          <strong>Note:</strong> Premiums shown are estimates based on vehicle value, age, and
          driver age. Actual rates depend on your complete driving history and may vary. Get quotes
          directly from providers for accurate pricing.
        </Typography>
      </Alert>
    </Box>
  );
}
