"use client";

import { Suspense, useState, useEffect, useRef } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import {
  Box,
  Container,
  Typography,
  Grid,
  Divider,
  Alert,
  Chip,
  Stack,
  AlertTitle,
  Card as MuiCard,
  CardContent,
} from "@mui/material";
import {
  TrendingUp,
  AttachMoney,
  DirectionsCar,
  Speed,
  CompareArrows,
  Shield,
  Verified,
  Star,
} from "@mui/icons-material";
import Link from "next/link";
import { useStepper } from "@/app/context";
import { useAuth } from "@/lib/auth/AuthProvider";
import { Button, Card, Spinner } from "@/components";
import { useApi } from "@/lib/hooks";
import {
  apiClient,
  type InsuranceRecommendationResponse,
  type InsuranceMatch,
} from "@/lib/api";
import { formatPrice } from "@/lib/utils/formatting";

interface VehicleInfo {
  make: string;
  model: string;
  year: string;
  price: string;
  mileage: string;
  vin?: string;
}

function FinalizeDealContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { completeStep, getStepData } = useStepper();
  const { user } = useAuth();

  const [vehicleInfo, setVehicleInfo] = useState<VehicleInfo | null>(null);

  const hasFetchedInsuranceRef = useRef(false);

  // Get evaluation data from step 2
  const evaluationData = getStepData<{
    evaluation?: {
      fair_value?: number;
      score?: number;
      insights?: string[];
      talking_points?: string[];
      market_data?: {
        predicted_price?: number;
        confidence?: string;
        price_range?: {
          min: number;
          max: number;
        };
      };
    };
  }>(2);

  // Get negotiation data from step 3
  const negotiationData = getStepData<{
    finalPrice?: number;
    negotiatedPrice?: number;
    savings?: number;
  }>(3);

  const {
    data: insuranceRecommendations,
    isLoading: insuranceLoading,
    error: insuranceError,
    execute: fetchInsurance,
  } = useApi<InsuranceRecommendationResponse>();

  // Parse vehicle info from URL params
  useEffect(() => {
    const make = searchParams.get("make");
    const model = searchParams.get("model");
    const year = searchParams.get("year");
    const price = searchParams.get("price");
    const mileage = searchParams.get("mileage");
    const vin = searchParams.get("vin");

    if (make && model && year && price && mileage) {
      setVehicleInfo({
        make,
        model,
        year,
        price,
        mileage,
        vin: vin || undefined,
      });
    }
  }, [searchParams]);

  // Fetch insurance recommendations
  useEffect(() => {
    if (hasFetchedInsuranceRef.current || !vehicleInfo || !user) {
      return;
    }

    hasFetchedInsuranceRef.current = true;

    const vehicleAge = new Date().getFullYear() - parseInt(vehicleInfo.year);
    const finalPrice =
      negotiationData?.finalPrice || parseFloat(vehicleInfo.price);

    fetchInsurance(() =>
      apiClient.getInsuranceRecommendations(
        finalPrice,
        vehicleAge,
        vehicleInfo.make,
        vehicleInfo.model,
        "full",
        30
      )
    );
  }, [vehicleInfo, user, negotiationData, fetchInsurance]);

  const evaluation = evaluationData?.evaluation;
  const finalPrice =
    negotiationData?.finalPrice ||
    (vehicleInfo ? parseFloat(vehicleInfo.price) : 0);
  const fairValue = evaluation?.fair_value || finalPrice;
  const savings = finalPrice < fairValue ? fairValue - finalPrice : 0;
  const dealScore = evaluation?.score || 0;

  // Calculate total cost breakdown
  const salesTax = finalPrice * 0.08; // 8% sales tax (example)
  const registrationFee = 300; // Example registration fee
  const documentFee = 150; // Example doc fee
  const totalCost = finalPrice + salesTax + registrationFee + documentFee;

  const handleFinalizeDeal = () => {
    // Complete the finalize step
    completeStep(4, {
      status: "completed",
      finalPrice,
      totalCost,
      timestamp: new Date().toISOString(),
    });

    // Navigate to deals page
    router.push("/deals");
  };

  if (!vehicleInfo) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">
          <AlertTitle>Missing Vehicle Information</AlertTitle>
          Vehicle information is required to view the deal summary.
          <Link href="/dashboard/search">
            <Button variant="primary" sx={{ mt: 2 }}>
              Start New Search
            </Button>
          </Link>
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          Final Deal Summary
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Review your deal details and explore insurance options before
          finalizing
        </Typography>
      </Box>

      {/* Deal Score Banner */}
      {dealScore > 0 && (
        <Alert
          severity={
            dealScore >= 8 ? "success" : dealScore >= 6.5 ? "info" : "warning"
          }
          icon={<Verified />}
          sx={{ mb: 3 }}
        >
          <AlertTitle>Deal Quality Score: {dealScore.toFixed(1)}/10</AlertTitle>
          {dealScore >= 8 && "Excellent deal! This is well below market value."}
          {dealScore >= 6.5 &&
            dealScore < 8 &&
            "Good deal! Fair price for this vehicle."}
          {dealScore < 6.5 &&
            "Consider negotiating further or exploring other options."}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Left Column - Vehicle & Price Details */}
        <Grid item xs={12} md={7}>
          {/* Vehicle Information */}
          <Card sx={{ mb: 3 }}>
            <Box sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                <DirectionsCar sx={{ mr: 1, verticalAlign: "middle" }} />
                Vehicle Details
              </Typography>
              <Divider sx={{ mb: 2 }} />

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Make & Model
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {vehicleInfo.year} {vehicleInfo.make} {vehicleInfo.model}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Mileage
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    <Speed
                      sx={{ fontSize: 16, mr: 0.5, verticalAlign: "middle" }}
                    />
                    {parseInt(vehicleInfo.mileage).toLocaleString()} miles
                  </Typography>
                </Grid>
                {vehicleInfo.vin && (
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">
                      VIN
                    </Typography>
                    <Typography
                      variant="body1"
                      fontWeight="medium"
                      sx={{ fontFamily: "monospace" }}
                    >
                      {vehicleInfo.vin}
                    </Typography>
                  </Grid>
                )}
              </Grid>
            </Box>
          </Card>

          {/* Price Breakdown */}
          <Card sx={{ mb: 3 }}>
            <Box sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                <AttachMoney sx={{ mr: 1, verticalAlign: "middle" }} />
                Price Breakdown
              </Typography>
              <Divider sx={{ mb: 2 }} />

              <Stack spacing={2}>
                <Box
                  display="flex"
                  justifyContent="space-between"
                  alignItems="center"
                >
                  <Typography variant="body1">Vehicle Price</Typography>
                  <Typography variant="h6" fontWeight="bold" color="primary">
                    {formatPrice(finalPrice)}
                  </Typography>
                </Box>

                {savings > 0 && (
                  <Box
                    display="flex"
                    justifyContent="space-between"
                    alignItems="center"
                  >
                    <Typography variant="body2" color="success.main">
                      <TrendingUp
                        sx={{ fontSize: 16, mr: 0.5, verticalAlign: "middle" }}
                      />
                      Savings vs Fair Value
                    </Typography>
                    <Typography
                      variant="body1"
                      color="success.main"
                      fontWeight="medium"
                    >
                      {formatPrice(savings)}
                    </Typography>
                  </Box>
                )}

                <Divider />

                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">
                    Sales Tax (8%)
                  </Typography>
                  <Typography variant="body2">
                    {formatPrice(salesTax)}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">
                    Registration Fee
                  </Typography>
                  <Typography variant="body2">
                    {formatPrice(registrationFee)}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">
                    Documentation Fee
                  </Typography>
                  <Typography variant="body2">
                    {formatPrice(documentFee)}
                  </Typography>
                </Box>

                <Divider />

                <Box
                  display="flex"
                  justifyContent="space-between"
                  alignItems="center"
                >
                  <Typography variant="h6" fontWeight="bold">
                    Total Cost
                  </Typography>
                  <Typography variant="h5" fontWeight="bold" color="primary">
                    {formatPrice(totalCost)}
                  </Typography>
                </Box>
              </Stack>
            </Box>
          </Card>

          {/* Market Insights */}
          {evaluation?.market_data && (
            <Card>
              <Box sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom fontWeight="bold">
                  <CompareArrows sx={{ mr: 1, verticalAlign: "middle" }} />
                  Market Insights
                </Typography>
                <Divider sx={{ mb: 2 }} />

                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Market Predicted Price
                    </Typography>
                    <Typography variant="body1" fontWeight="medium">
                      {formatPrice(
                        evaluation.market_data.predicted_price || fairValue
                      )}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Confidence Level
                    </Typography>
                    <Chip
                      label={evaluation.market_data.confidence || "Medium"}
                      size="small"
                      color={
                        evaluation.market_data.confidence === "high"
                          ? "success"
                          : "default"
                      }
                    />
                  </Grid>
                  {evaluation.market_data.price_range && (
                    <Grid item xs={12}>
                      <Typography variant="body2" color="text.secondary">
                        Market Price Range
                      </Typography>
                      <Typography variant="body1" fontWeight="medium">
                        {formatPrice(evaluation.market_data.price_range.min)} -{" "}
                        {formatPrice(evaluation.market_data.price_range.max)}
                      </Typography>
                    </Grid>
                  )}
                </Grid>
              </Box>
            </Card>
          )}
        </Grid>

        {/* Right Column - Insurance Recommendations */}
        <Grid item xs={12} md={5}>
          <Card>
            <Box sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                <Shield sx={{ mr: 1, verticalAlign: "middle" }} />
                Insurance Recommendations
              </Typography>
              <Divider sx={{ mb: 2 }} />

              {insuranceLoading && (
                <Box display="flex" justifyContent="center" py={4}>
                  <Spinner size="md" />
                </Box>
              )}

              {insuranceError && (
                <Alert severity="warning" sx={{ mb: 2 }}>
                  Unable to load insurance recommendations. You can add
                  insurance later.
                </Alert>
              )}

              {insuranceRecommendations &&
              insuranceRecommendations.recommendations.length > 0 ? (
                <Stack spacing={2}>
                  {insuranceRecommendations.recommendations
                    .slice(0, 3)
                    .map((match: InsuranceMatch, index: number) => (
                      <MuiCard
                        key={match.provider.provider_id}
                        variant="outlined"
                        sx={{
                          border: index === 0 ? 2 : 1,
                          borderColor: index === 0 ? "primary.main" : "divider",
                        }}
                      >
                        <CardContent>
                          <Box
                            display="flex"
                            justifyContent="space-between"
                            alignItems="start"
                            mb={1}
                          >
                            <Typography variant="subtitle1" fontWeight="bold">
                              {match.provider.name}
                            </Typography>
                            {index === 0 && (
                              <Chip
                                label="Best Match"
                                size="small"
                                color="primary"
                                icon={<Star />}
                              />
                            )}
                          </Box>

                          <Typography
                            variant="body2"
                            color="text.secondary"
                            mb={1}
                          >
                            {match.provider.description}
                          </Typography>

                          <Box
                            display="flex"
                            justifyContent="space-between"
                            alignItems="center"
                            mb={1}
                          >
                            <Typography variant="body2" color="text.secondary">
                              Estimated Monthly
                            </Typography>
                            <Typography
                              variant="h6"
                              color="primary"
                              fontWeight="bold"
                            >
                              ${match.estimated_monthly_premium.toFixed(0)}
                            </Typography>
                          </Box>

                          <Typography
                            variant="caption"
                            color="text.secondary"
                            display="block"
                            mb={1}
                          >
                            Match Score: {(match.match_score * 100).toFixed(0)}%
                          </Typography>

                          {/* <List dense sx={{ py: 0 }}>
                          {match.recommendation_reasons.slice(0, 2).map((reason, idx) => (
                            <ListItem key={idx} sx={{ px: 0, py: 0.5 }}>
                              <ListItemIcon sx={{ minWidth: 24 }}>
                                <CheckCircle color="success" fontSize="small" />
                              </ListItemIcon>
                              <ListItemText 
                                primary={reason} 
                                primaryTypographyProps={{ variant: 'caption' }}
                              />
                            </ListItem>
                          ))}
                        </List> */}

                          <Button
                            variant="outline"
                            size="sm"
                            fullWidth
                            onClick={() =>
                              window.open(
                                match.provider.affiliate_url,
                                "_blank"
                              )
                            }
                            sx={{ mt: 1 }}
                          >
                            Get Quote
                          </Button>
                        </CardContent>
                      </MuiCard>
                    ))}
                </Stack>
              ) : (
                !insuranceLoading && (
                  <Alert severity="info">
                    No insurance recommendations available at this time.
                  </Alert>
                )
              )}
            </Box>
          </Card>
        </Grid>
      </Grid>

      {/* Action Buttons */}
      <Box sx={{ mt: 4, display: "flex", justifyContent: "space-between" }}>
        <Button variant="outline" onClick={() => router.back()}>
          Back to Negotiation
        </Button>
        <Button variant="success" onClick={handleFinalizeDeal}>
          Finalize Deal
        </Button>
      </Box>
    </Container>
  );
}

export default function FinalizePage() {
  return (
    <Suspense fallback={<Spinner size="lg" />}>
      <FinalizeDealContent />
    </Suspense>
  );
}
