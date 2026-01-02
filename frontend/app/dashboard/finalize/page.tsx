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
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Paper,
  Tabs,
  Tab,
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
  CheckCircle,
  AccountBalance,
  Info,
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
  type LenderRecommendationResponse,
  type LenderMatch,
} from "@/lib/api";
import { formatPrice } from "@/lib/utils/formatting";

interface VehicleInfo {
  make: string;
  model: string;
  year: string;
  price: string;
  mileage: string;
  vin?: string;
  zipCode?: string;
  dealId?: string;
}

function FinalizeDealContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { completeStep, getStepData, goToPreviousStep, setStepData } = useStepper();
  const { user } = useAuth();

  const [vehicleInfo, setVehicleInfo] = useState<VehicleInfo | null>(null);
  const [activeTab, setActiveTab] = useState(0); // 0 = Insurance, 1 = Financing
  
  const hasFetchedInsuranceRef = useRef(false);
  const hasFetchedLendersRef = useRef(false);

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

  const {
    data: lenderRecommendations,
    isLoading: lendersLoading,
    error: lendersError,
    execute: fetchLenders,
  } = useApi<LenderRecommendationResponse>();

  // Parse vehicle info from URL params
  useEffect(() => {
    const make = searchParams.get("make");
    const model = searchParams.get("model");
    const year = searchParams.get("year");
    const price = searchParams.get("price");
    const mileage = searchParams.get("mileage");
    const vin = searchParams.get("vin");
    const zipCode = searchParams.get("zipCode") || searchParams.get("zip_code");
    const dealId = searchParams.get("dealId");

    if (make && model && year && price && mileage) {
      setVehicleInfo({
        make,
        model,
        year,
        price,
        mileage,
        vin: vin || undefined,
        zipCode: zipCode || undefined,
        dealId: dealId || undefined,
      });
    }
  }, [searchParams]);

  // Save query parameters to step data when page loads with valid vehicle data
  useEffect(() => {
    if (vehicleInfo && searchParams.toString()) {
      const existingData = getStepData(4) || {};
      // Only update if queryString is different or missing
      const existingQueryString = existingData && typeof existingData === 'object' && 'queryString' in existingData
        ? (existingData as { queryString?: string }).queryString
        : undefined;
      if (!existingQueryString || existingQueryString !== searchParams.toString()) {
        setStepData(4, {
          ...existingData,
          queryString: searchParams.toString(),
        });
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [vehicleInfo, searchParams]);

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
        30 // Default driver age
      )
    );
  }, [vehicleInfo, user, negotiationData, fetchInsurance]);

  // Fetch lender recommendations
  useEffect(() => {
    if (hasFetchedLendersRef.current || !vehicleInfo || !user) {
      return;
    }

    hasFetchedLendersRef.current = true;

    const finalPrice = negotiationData?.finalPrice || parseFloat(vehicleInfo.price);
    const downPayment = finalPrice * 0.2; // 20% down payment
    const loanAmount = finalPrice - downPayment;

    fetchLenders(() =>
      apiClient.getLenderRecommendations(
        loanAmount,
        "good", // Default credit score range
        60 // 60 months loan term
      )
    );
  }, [vehicleInfo, user, negotiationData, fetchLenders]);

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
      {/* Header with breadcrumb-like context */}
      <Box sx={{ mb: 4 }}>
        <Chip 
          label="Step 4 of 4" 
          size="small" 
          color="primary" 
          sx={{ mb: 2 }} 
        />
        <Typography variant="h4" gutterBottom fontWeight="bold" sx={{ color: "primary.dark" }}>
          🎉 Final Deal Summary
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Review your deal details and explore financing & insurance options before finalizing
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
          {/* Vehicle Information - Enhanced */}
          <Card sx={{ mb: 3, border: "2px solid", borderColor: "primary.main" }}>
            <Box sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight="bold" sx={{ color: "primary.dark" }}>
                <DirectionsCar sx={{ mr: 1, verticalAlign: "middle" }} />
                Your Vehicle
              </Typography>
              <Divider sx={{ mb: 2 }} />

              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Box sx={{ 
                    p: 2, 
                    bgcolor: "primary.50", 
                    borderRadius: 2,
                    border: "1px solid",
                    borderColor: "primary.200"
                  }}>
                    <Typography variant="h5" fontWeight="bold" sx={{ color: "primary.dark" }}>
                      {vehicleInfo.year} {vehicleInfo.make} {vehicleInfo.model}
                    </Typography>
                  </Box>
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
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Year
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {vehicleInfo.year}
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
                      sx={{ fontFamily: "monospace", fontSize: "0.9rem" }}
                    >
                      {vehicleInfo.vin}
                    </Typography>
                  </Grid>
                )}
              </Grid>
            </Box>
          </Card>

          {/* Price Breakdown - Enhanced */}
          <Card sx={{ mb: 3, boxShadow: 3 }}>
            <Box sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight="bold" sx={{ color: "primary.dark" }}>
                <AttachMoney sx={{ mr: 1, verticalAlign: "middle" }} />
                Complete Price Breakdown
              </Typography>
              <Divider sx={{ mb: 3 }} />

              <Stack spacing={2.5}>
                <Box
                  display="flex"
                  justifyContent="space-between"
                  alignItems="center"
                  sx={{ 
                    p: 2, 
                    bgcolor: "success.50", 
                    borderRadius: 2,
                    border: "2px solid",
                    borderColor: "success.main"
                  }}
                >
                  <Typography variant="h6" fontWeight="bold">
                    Negotiated Vehicle Price
                  </Typography>
                  <Typography variant="h5" fontWeight="bold" color="success.dark">
                    {formatPrice(finalPrice)}
                  </Typography>
                </Box>

                {savings > 0 && (
                  <Box
                    display="flex"
                    justifyContent="space-between"
                    alignItems="center"
                    sx={{ px: 2 }}
                  >
                    <Typography variant="body1" color="success.main" sx={{ display: "flex", alignItems: "center" }}>
                      <TrendingUp
                        sx={{ fontSize: 20, mr: 1 }}
                      />
                      <strong>Your Savings vs Fair Market Value</strong>
                    </Typography>
                    <Typography
                      variant="h6"
                      color="success.main"
                      fontWeight="bold"
                    >
                      {formatPrice(savings)}
                    </Typography>
                  </Box>
                )}

                <Divider />

                <Typography variant="subtitle2" color="text.secondary" sx={{ px: 2 }}>
                  Additional Costs & Fees
                </Typography>

                <Box display="flex" justifyContent="space-between" sx={{ px: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Sales Tax (8%)
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {formatPrice(salesTax)}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" sx={{ px: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Registration Fee
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {formatPrice(registrationFee)}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" sx={{ px: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Documentation Fee
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {formatPrice(documentFee)}
                  </Typography>
                </Box>

                <Divider sx={{ mt: 2 }} />

                <Box
                  display="flex"
                  justifyContent="space-between"
                  alignItems="center"
                  sx={{ 
                    p: 2.5, 
                    bgcolor: "primary.50", 
                    borderRadius: 2,
                    border: "2px solid",
                    borderColor: "primary.main"
                  }}
                >
                  <Typography variant="h5" fontWeight="bold" sx={{ color: "primary.dark" }}>
                    Total Out-the-Door Price
                  </Typography>
                  <Typography variant="h4" fontWeight="bold" color="primary.main">
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

        {/* Right Column - Insurance & Financing Recommendations */}
        <Grid item xs={12} md={5}>
          <Card>
            <Box sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                <Shield sx={{ mr: 1, verticalAlign: "middle" }} />
                Recommendations
              </Typography>
              <Divider sx={{ mb: 2 }} />

              {/* Tabs for Insurance and Financing */}
              <Tabs
                value={activeTab}
                onChange={(_, newValue) => setActiveTab(newValue)}
                sx={{ mb: 2, borderBottom: 1, borderColor: "divider" }}
              >
                <Tab label="Insurance" icon={<Shield />} iconPosition="start" />
                <Tab label="Financing" icon={<AccountBalance />} iconPosition="start" />
              </Tabs>

              {/* Insurance Tab Content */}
              {activeTab === 0 && (
                <Box>
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
                              transition: "all 0.2s",
                              "&:hover": {
                                boxShadow: 3,
                                transform: "translateY(-2px)",
                              },
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

                              <List dense sx={{ py: 0 }}>
                                {match.recommendation_reason.split(" . ").slice(0, 2).map((reason, idx) => (
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
                              </List>

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
                      <Alert severity="info" icon={<Info />}>
                        No insurance recommendations available at this time.
                      </Alert>
                    )
                  )}
                </Box>
              )}

              {/* Financing Tab Content */}
              {activeTab === 1 && (
                <Box>
                  {lendersLoading && (
                    <Box display="flex" justifyContent="center" py={4}>
                      <Spinner size="md" />
                    </Box>
                  )}

                  {lendersError && (
                    <Alert severity="warning" sx={{ mb: 2 }}>
                      Unable to load financing options. You can explore financing later.
                    </Alert>
                  )}

                  {lenderRecommendations &&
                  lenderRecommendations.recommendations.length > 0 ? (
                    <Stack spacing={2}>
                      {lenderRecommendations.recommendations
                        .slice(0, 3)
                        .map((match: LenderMatch) => (
                          <Paper
                            key={match.lender.lender_id}
                            elevation={2}
                            sx={{
                              p: 2,
                              border: match.rank === 1 ? 2 : 1,
                              borderColor:
                                match.rank === 1 ? "primary.main" : "divider",
                              transition: "all 0.2s",
                              "&:hover": {
                                boxShadow: 3,
                                transform: "translateY(-2px)",
                              },
                            }}
                          >
                            <Box
                              sx={{
                                display: "flex",
                                justifyContent: "space-between",
                                alignItems: "start",
                                mb: 1,
                              }}
                            >
                              <Box>
                                {match.rank === 1 && (
                                  <Chip
                                    label="Best Match"
                                    color="primary"
                                    size="small"
                                    icon={<Star />}
                                    sx={{ mb: 1 }}
                                  />
                                )}
                                <Typography variant="subtitle1" fontWeight="bold">
                                  {match.lender.name}
                                </Typography>
                                <Typography
                                  variant="caption"
                                  color="text.secondary"
                                >
                                  {match.recommendation_reason}
                                </Typography>
                              </Box>
                              <Typography variant="h6" color="primary.main">
                                {(match.estimated_apr * 100).toFixed(2)}% APR
                              </Typography>
                            </Box>
                            <Divider sx={{ my: 1 }} />
                            <Grid container spacing={2}>
                              <Grid item xs={6}>
                                <Typography
                                  variant="caption"
                                  color="text.secondary"
                                >
                                  Estimated Payment
                                </Typography>
                                <Typography variant="body2" fontWeight="medium">
                                  {formatPrice(match.estimated_monthly_payment)}
                                  /mo
                                </Typography>
                              </Grid>
                              <Grid item xs={6}>
                                <Typography
                                  variant="caption"
                                  color="text.secondary"
                                >
                                  Match Score
                                </Typography>
                                <Typography variant="body2" fontWeight="medium">
                                  {match.match_score.toFixed(0)}/100
                                </Typography>
                              </Grid>
                            </Grid>
                            <Button
                              variant="outline"
                              size="sm"
                              fullWidth
                              sx={{ mt: 2 }}
                              onClick={() =>
                                window.open(match.lender.affiliate_url, "_blank")
                              }
                            >
                              Apply Now
                            </Button>
                          </Paper>
                        ))}
                    </Stack>
                  ) : (
                    !lendersLoading && (
                      <Alert severity="info" icon={<Info />}>
                        No financing options available at this time.
                      </Alert>
                    )
                  )}
                </Box>
              )}
            </Box>
          </Card>
        </Grid>
      </Grid>

      {/* Action Buttons - Enhanced */}
      <Box sx={{ 
        mt: 4, 
        p: 3, 
        bgcolor: "grey.50", 
        borderRadius: 2,
        border: "1px solid",
        borderColor: "grey.200"
      }}>
        <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
          Ready to finalize your deal?
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          By finalizing, you&apos;re confirming your interest in this vehicle at the agreed-upon price.
          You can review financing and insurance options before completing your purchase.
        </Typography>
        <Box sx={{ display: "flex", justifyContent: "space-between", gap: 2, flexWrap: "wrap" }}>
          <Button variant="outline" onClick={() => goToPreviousStep()}>
            ← Back to Negotiation
          </Button>
          <Button variant="success" size="lg" onClick={handleFinalizeDeal} sx={{ px: 4 }}>
            ✓ Finalize This Deal
          </Button>
        </Box>
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
