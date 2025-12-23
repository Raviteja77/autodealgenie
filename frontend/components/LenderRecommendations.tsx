"use client";

import { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Grid,
  Divider,
  Chip,
  Stack,
  Paper,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  Collapse,
  IconButton,
} from "@mui/material";
import {
  AccountBalance as BankIcon,
  TrendingDown,
  CheckCircle,
  ExpandMore,
  ExpandLess,
  Star,
} from "@mui/icons-material";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import { apiClient, type LenderMatch, type LenderRecommendationResponse } from "@/lib/api";
import { formatPrice } from "@/lib/utils/formatting";

interface LenderRecommendationsProps {
  loanAmount: number;
  creditScore: "excellent" | "good" | "fair" | "poor";
  loanTermMonths?: number;
  onLenderSelect?: (lender: LenderMatch) => void;
  showApplyButton?: boolean;
  compact?: boolean;
}

type SortOption = "match_score" | "apr_low" | "payment_low" | "term_short";

export function LenderRecommendations({
  loanAmount,
  creditScore,
  loanTermMonths = 60,
  onLenderSelect,
  showApplyButton = true,
  compact = false,
}: LenderRecommendationsProps) {
  const [lenders, setLenders] = useState<LenderMatch[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<SortOption>("match_score");
  const [expandedLenders, setExpandedLenders] = useState<Set<string>>(new Set());
  const [selectedTerm, setSelectedTerm] = useState(loanTermMonths);

  useEffect(() => {
    const fetchLenders = async () => {
      if (loanAmount <= 0) {
        setError("Loan amount must be greater than $0. Please adjust your search criteria.");
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(null);

        const response: LenderRecommendationResponse = await apiClient.request(
          `/api/v1/loans/lenders`,
          {
            method: "POST",
            body: JSON.stringify({
              loan_amount: loanAmount,
              credit_score_range: creditScore,
              loan_term_months: selectedTerm,
            }),
          }
        );

        setLenders(response.recommendations || []);
      } catch (err) {
        console.error("Error fetching lenders:", err);
        
        // Provide specific error messages based on error type
        if (err instanceof TypeError && err.message.includes("fetch")) {
          setError(
            "Network error: Unable to connect to lender service. Please check your connection."
          );
        } else if (
          err &&
          typeof err === "object" &&
          "status" in err &&
          (err as { status?: number }).status === 401
        ) {
          setError("Authentication error: Please log in to view lender recommendations.");
        } else if (
          err &&
          typeof err === "object" &&
          "status" in err &&
          (err as { status?: number }).status === 400
        ) {
          setError("Invalid loan criteria. Please adjust your search parameters.");
        } else {
          setError(
            err instanceof Error
              ? err.message
              : "Failed to load lender recommendations. Please try again."
          );
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchLenders();
  }, [loanAmount, creditScore, selectedTerm]);

  // Handle auto-expand logic separately to avoid unnecessary API calls
  useEffect(() => {
    if (!compact && lenders.length > 0) {
      const topLenders = new Set(
        lenders
          .slice(0, 2)
          .map((l) => l.lender_id)
      );
      setExpandedLenders(topLenders);
    } else if (compact) {
      // Collapse all in compact mode
      setExpandedLenders(new Set());
    }
  }, [compact, lenders]);

  const handleSortChange = (event: SelectChangeEvent<SortOption>) => {
    setSortBy(event.target.value as SortOption);
  };

  const handleTermChange = (event: SelectChangeEvent<number>) => {
    setSelectedTerm(Number(event.target.value));
  };

  const toggleLenderExpansion = (lenderId: string) => {
    setExpandedLenders((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(lenderId)) {
        newSet.delete(lenderId);
      } else {
        newSet.add(lenderId);
      }
      return newSet;
    });
  };

  // Sort lenders based on selected criteria
  const sortedLenders = [...lenders].sort((a, b) => {
    switch (sortBy) {
      case "apr_low":
        return a.estimated_apr - b.estimated_apr;
      case "payment_low":
        return a.estimated_monthly_payment - b.estimated_monthly_payment;
      case "term_short":
        return (
          a.lender.min_term_months - b.lender.min_term_months
        );
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
              Finding the best lenders for you...
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

  if (lenders.length === 0) {
    return (
      <Card shadow="md">
        <Card.Body>
          <Alert severity="info">
            <Typography variant="body2">
              No lenders available for your criteria. Try adjusting your loan amount or term.
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
            Lender Recommendations
          </Typography>
          <Chip
            label={`${lenders.length} Matches`}
            color="primary"
            size="small"
          />
        </Box>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Top lenders matched to your credit profile and loan needs
        </Typography>
      </Box>

      {/* Controls */}
      <Card shadow="sm" sx={{ mb: 3 }}>
        <Card.Body>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth size="small">
                <InputLabel>Sort By</InputLabel>
                <Select value={sortBy} label="Sort By" onChange={handleSortChange}>
                  <MenuItem value="match_score">Best Match</MenuItem>
                  <MenuItem value="apr_low">Lowest APR</MenuItem>
                  <MenuItem value="payment_low">Lowest Payment</MenuItem>
                  <MenuItem value="term_short">Shortest Term</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth size="small">
                <InputLabel>Loan Term</InputLabel>
                <Select
                  value={selectedTerm}
                  label="Loan Term"
                  onChange={handleTermChange}
                >
                  <MenuItem value={36}>36 months</MenuItem>
                  <MenuItem value={48}>48 months</MenuItem>
                  <MenuItem value={60}>60 months</MenuItem>
                  <MenuItem value={72}>72 months</MenuItem>
                  <MenuItem value={84}>84 months</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </Card.Body>
      </Card>

      {/* Lender List */}
      <Stack spacing={2}>
        {sortedLenders.map((match) => {
          const isExpanded = expandedLenders.has(match.lender.lender_id);
          const isTopMatch = match.rank === 1;

          // Using Paper directly instead of custom Card component to support
          // dynamic elevation and border styling based on match rank
          return (
            <Paper
              key={match.lender.lender_id}
              elevation={isTopMatch ? 4 : 2}
              sx={{
                p: 2,
                border: isTopMatch ? 2 : 1,
                borderColor: isTopMatch ? "primary.main" : "divider",
                transition: "all 0.3s ease",
                "&:hover": {
                  boxShadow: 4,
                },
              }}
            >
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
                    <BankIcon color="primary" />
                    <Typography variant="h6" fontWeight="bold">
                      {match.lender.name}
                    </Typography>
                    {isTopMatch && (
                      <Chip
                        icon={<Star />}
                        label="Best Match"
                        color="primary"
                        size="small"
                      />
                    )}
                  </Box>
                  <Typography variant="caption" color="text.secondary">
                    {match.recommendation_reason}
                  </Typography>
                </Box>

                <Box sx={{ textAlign: "right" }}>
                  <Typography variant="h5" color="primary.main" fontWeight="bold">
                    {(match.estimated_apr * 100).toFixed(2)}%
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    APR
                  </Typography>
                </Box>
              </Box>

              {/* Key Metrics */}
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={4}>
                  <Typography variant="caption" color="text.secondary">
                    Est. Payment
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {formatPrice(match.estimated_monthly_payment)}/mo
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
                    onClick={() => toggleLenderExpansion(match.lender.lender_id)}
                    aria-label={isExpanded ? "Collapse lender details" : "Expand lender details"}
                    aria-expanded={isExpanded}
                    sx={{ 
                      display: "flex", 
                      alignItems: "center",
                      gap: 0.5,
                      textTransform: "none",
                      color: "text.primary",
                      "&:hover": {
                        backgroundColor: "action.hover"
                      }
                    }}
                  >
                    <Typography variant="subtitle2">
                      View Details
                    </Typography>
                    {isExpanded ? <ExpandLess /> : <ExpandMore />}
                  </IconButton>
                </Box>

                <Collapse in={isExpanded}>
                  <Divider sx={{ my: 2 }} />

                  {/* Description */}
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {match.lender.description}
                  </Typography>

                  {/* Features */}
                  {match.lender.features && match.lender.features.length > 0 && (
                    <Box sx={{ mb: 2 }}>
                      <Typography
                        variant="subtitle2"
                        gutterBottom
                        fontWeight={600}
                      >
                        Features
                      </Typography>
                      <Stack direction="row" spacing={1} flexWrap="wrap">
                        {match.lender.features.map((feature, idx) => (
                          <Chip
                            key={idx}
                            icon={<CheckCircle />}
                            label={feature}
                            size="small"
                            variant="outlined"
                            color="success"
                          />
                        ))}
                      </Stack>
                    </Box>
                  )}

                  {/* Benefits */}
                  {match.lender.benefits && match.lender.benefits.length > 0 && (
                    <Box sx={{ mb: 2 }}>
                      <Typography
                        variant="subtitle2"
                        gutterBottom
                        fontWeight={600}
                      >
                        Benefits
                      </Typography>
                      <Stack direction="row" spacing={1} flexWrap="wrap">
                        {match.lender.benefits.map((benefit, idx) => (
                          <Chip
                            key={idx}
                            icon={<TrendingDown />}
                            label={benefit}
                            size="small"
                            variant="outlined"
                            color="info"
                          />
                        ))}
                      </Stack>
                    </Box>
                  )}

                  {/* Loan Details */}
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom fontWeight={600}>
                      Loan Details
                    </Typography>
                    <Grid container spacing={1}>
                      <Grid item xs={6}>
                        <Typography variant="caption" color="text.secondary">
                          APR Range
                        </Typography>
                        <Typography variant="body2">
                          {(match.lender.apr_range_min * 100).toFixed(2)}% -{" "}
                          {(match.lender.apr_range_max * 100).toFixed(2)}%
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="caption" color="text.secondary">
                          Loan Amount Range
                        </Typography>
                        <Typography variant="body2">
                          {formatPrice(match.lender.min_loan_amount)} -{" "}
                          {formatPrice(match.lender.max_loan_amount)}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="caption" color="text.secondary">
                          Term Range
                        </Typography>
                        <Typography variant="body2">
                          {match.lender.min_term_months} -{" "}
                          {match.lender.max_term_months} months
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="caption" color="text.secondary">
                          Credit Score Range
                        </Typography>
                        <Typography variant="body2">
                          {match.lender.min_credit_score} -{" "}
                          {match.lender.max_credit_score}
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
                    variant="primary"
                    size="sm"
                    fullWidth
                    onClick={() => {
                      // Validate URL with strict checks
                      const url = match.lender.affiliate_url;
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
                        
                        // Optional: Validate against trusted domains (can be expanded)
                        // For now, just ensure it's a valid URL with proper protocol
                        window.open(url, "_blank", "noopener,noreferrer");
                      } catch (error) {
                        console.error("Invalid affiliate URL:", url, error);
                        alert(
                          "We're sorry, but this lender link is currently unavailable. " +
                            "Please try another lender or contact support."
                        );
                      }
                    }}
                    aria-label="Apply now, opens in new tab"
                  >
                    Apply Now
                  </Button>
                )}
                {onLenderSelect && (
                  <Button
                    variant="outline"
                    size="sm"
                    fullWidth
                    onClick={() => onLenderSelect(match)}
                  >
                    Select Lender
                  </Button>
                )}
              </Box>
            </Paper>
          );
        })}
      </Stack>

      {/* Footer Info */}
      <Alert severity="info" sx={{ mt: 3 }}>
        <Typography variant="caption">
          <strong>Note:</strong> APRs and payments shown are estimates. Actual rates depend
          on your credit profile and may vary. Apply directly with lenders for final offers.
        </Typography>
      </Alert>
    </Box>
  );
}
