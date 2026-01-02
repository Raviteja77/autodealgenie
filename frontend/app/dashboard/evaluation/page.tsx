"use client";

import { useState, Suspense, useEffect, useRef, useMemo } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  Box,
  Container,
  Typography,
  Alert,
  Divider,
  Grid,
  LinearProgress,
  Stack,
  Chip,
} from "@mui/material";
import {
  CheckCircle,
  Warning,
  Cancel,
  TrendingUp,
  TrendingDown,
  AttachMoney,
  Speed,
  Security,
} from "@mui/icons-material";
import Link from "next/link";
import { useStepper } from "@/app/context";
import { Button, Card, Spinner } from "@/components";
import { DealCreate, apiClient } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { NotFoundError } from "@/lib/errors";
import { 
  DEFAULT_VIN, 
  FUEL_TYPE, 
  VEHICLE_CONDITION, 
  STEPPER_STEPS,
  EVALUATION_TEXT,
  ROUTES,
} from "@/lib/constants";

interface VehicleInfo {
  vin?: string;
  make: string;
  model: string;
  year: number;
  price: number;
  mileage: number;
  fuelType: string;
  condition?: string;
  zipCode?: string;
}

interface DealEvaluationResult {
  fair_value: number;
  score: number;
  insights: string[];
  talking_points: string[];
}

function EvaluationContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { completeStep, getStepData, setStepData, goToPreviousStep } =
    useStepper();

  const { user } = useAuth();
  const hasEvaluatedRef = useRef(false);
  const hasInitializedDealRef = useRef(false);
  const evaluationInProgressRef = useRef(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [evaluation, setEvaluation] = useState<DealEvaluationResult | null>(
    null
  );
  const [dealId, setDealId] = useState<number | null>(null);
  // Driver age for insurance calculation - currently using default
  // const driverAge = 30;

  // Extract vehicle data from URL params
  const vehicleData: VehicleInfo | null = useMemo(() => {
    try {
      const vin = searchParams.get("vin") || DEFAULT_VIN;
      const make = searchParams.get("make");
      const model = searchParams.get("model");
      const yearStr = searchParams.get("year");
      const priceStr = searchParams.get("price");
      const mileageStr = searchParams.get("mileage");
      const fuelType = searchParams.get("fuelType");
      const condition = searchParams.get("condition");
      const zipCode =
        searchParams.get("zipCode") || searchParams.get("zip_code");

      if (!make || !model || !yearStr || !priceStr || !mileageStr) {
        return null;
      }

      const year = parseInt(yearStr);
      const price = parseFloat(priceStr);
      const mileage = parseInt(mileageStr);

      if (isNaN(year) || isNaN(price) || isNaN(mileage)) {
        return null;
      }

      return {
        vin,
        make,
        model,
        year,
        price,
        mileage,
        fuelType: fuelType || FUEL_TYPE.DEFAULT,
        condition: condition || VEHICLE_CONDITION.DEFAULT,
        zipCode: zipCode || undefined,
      };
    } catch (err) {
      console.error("Error parsing vehicle data:", err);
      return null;
    }
  }, [searchParams]);

  // Save query parameters to step data when page loads with valid vehicle data
  useEffect(() => {
    if (vehicleData && searchParams.toString()) {
      const existingData = getStepData(STEPPER_STEPS.EVALUATION) || {};
      // Only update if queryString is different or missing
      const existingQueryString =
        existingData &&
        typeof existingData === "object" &&
        "queryString" in existingData
          ? (existingData as { queryString?: string }).queryString
          : undefined;
      if (
        !existingQueryString ||
        existingQueryString !== searchParams.toString()
      ) {
        setStepData(STEPPER_STEPS.EVALUATION, {
          ...existingData,
          queryString: searchParams.toString(),
        });
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [vehicleData, searchParams]);

  // Initialize negotiation session
  useEffect(() => {
    // Guard clauses to prevent duplicate calls
    if (hasInitializedDealRef.current) {
      return;
    }

    if (!vehicleData) {
      return;
    }

    const createOrGetDeal = async () => {
      // initializationInProgressRef.current = true;

      setLoading(true);
      setError(null);

      // Check if deal already exists
      let dealId: number;
      const customerEmail = user?.email || "guest@autodealgenie.com";
      const vehicleVin = vehicleData?.vin || DEFAULT_VIN;

      try {
        const existingDeal = await apiClient.getDealByEmailAndVin(
          customerEmail,
          vehicleVin
        );
        dealId = existingDeal.id;
        setDealId(dealId);
      } catch (error: unknown) {
        // Check if this is a legitimate 404 (deal not found) or another error
        // Use the proper type guard from the errors module
        if (error instanceof NotFoundError) {
          // Deal not found (404), create new one
          const dealData: DealCreate = {
            customer_name: user?.full_name || user?.username || "Guest User",
            customer_email: customerEmail,
            vehicle_make: vehicleData.make,
            vehicle_model: vehicleData.model,
            vehicle_year: vehicleData.year,
            vehicle_mileage: vehicleData.mileage,
            vehicle_vin: vehicleVin,
            asking_price: vehicleData.price,
            status: "pending",
            notes: `Negotiation started for ${vehicleData.year} ${vehicleData.make} ${vehicleData.model}`,
          };

          const newDeal = await apiClient.createDeal(dealData);
          dealId = newDeal.id;
          setDealId(dealId);
        } else {
          // This is not a "deal not found" error - it could be network, auth, etc.
          console.error("Unexpected error checking for existing deal:", error);
          throw error; // Re-throw to be caught by outer catch
        }
      }

      setLoading(false);

      // Mark as initialized
      hasInitializedDealRef.current = true;
    };

    createOrGetDeal();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [vehicleData, user]); // Other dependencies are stable (setters, user, chatContext)

  const evaluateDeal = async (vehicleData: VehicleInfo | null) => {
    // Mark as in progress
    evaluationInProgressRef.current = true;
    setLoading(true);
    setError(null);

    try {
      if (!vehicleData) {
        throw new Error("Invalid vehicle data for evaluation");
      }
      const data = await apiClient.evaluateDeal({
        vehicle_vin: vehicleData.vin || "UNKNOWN",
        asking_price: vehicleData.price,
        condition: vehicleData.condition || "good",
        mileage: vehicleData.mileage,
        make: vehicleData.make,
        model: vehicleData.model,
        year: vehicleData.year,
        zip_code: vehicleData.zipCode, // Pass zipCode to backend for MarketCheck API
      });

      setEvaluation(data);

      // Mark as evaluated
      hasEvaluatedRef.current = true;

      // Complete the evaluation step (step 2 - evaluation now comes before negotiation)
      completeStep(STEPPER_STEPS.EVALUATION, {
        status: "completed",
        vehicleData: vehicleData,
        evaluation: data,
        timestamp: new Date().toISOString(),
        queryString: searchParams.toString(),
      });
    } catch (err: unknown) {
      console.error("Error evaluating deal:", err);
      const errorMessage =
        err instanceof Error ? err.message : "Failed to evaluate deal";
      setError(errorMessage);

      // Reset in progress flag on error so user can retry
      evaluationInProgressRef.current = false;
    } finally {
      setLoading(false);
    }
  };

  const handleVehicleSelection = async (
    vehicle: VehicleInfo,
    targetPath: string
  ) => {
    // Navigate to the target page with all vehicle data
    const vehicleParams = new URLSearchParams({
      vin: vehicle.vin || "",
      make: vehicle.make,
      model: vehicle.model,
      year: vehicle.year.toString(),
      price: vehicle.price.toString(),
      mileage: vehicle.mileage.toString(),
      fuelType: vehicle.fuelType || "",
      dealId: dealId ? dealId.toString() : "",
    });

    // Add zipCode if available
    if (vehicle.zipCode) {
      vehicleParams.set("zipCode", vehicle.zipCode);
    }

    if (dealId !== null) {
      await apiClient.updateDeal(dealId, { status: "in_progress" });
    }

    // Store the selected vehicle data for use in subsequent steps
    const existingData = getStepData(STEPPER_STEPS.EVALUATION) || {};
    setStepData(STEPPER_STEPS.EVALUATION, {
      ...existingData,
      selectedVehicle: vehicle,
      queryString: vehicleParams.toString(),
    });

    router.push(`${targetPath}?${vehicleParams.toString()}`);
  };

  useEffect(() => {
    // Guard: Don't run if already evaluated or in progress
    if (hasEvaluatedRef.current || evaluationInProgressRef.current) {
      return;
    }

    // Guard: Need vehicle data
    if (!vehicleData) {
      return;
    }

    // Guard: Already have evaluation
    if (evaluation) {
      return;
    }

    evaluateDeal(vehicleData);

    // No cleanup needed as we use refs
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [vehicleData, evaluation]);

  const getScoreColor = (score: number) => {
    if (score >= 8) return "success";
    if (score >= 6.5) return "info";
    if (score >= 5) return "warning";
    return "error";
  };

  const getScoreIcon = (score: number) => {
    if (score >= 8) return <CheckCircle color="success" />;
    if (score >= 6.5) return <TrendingUp color="info" />;
    if (score >= 5) return <Warning color="warning" />;
    return <Cancel color="error" />;
  };

  const getRecommendation = (score: number) => {
    if (score >= 8) return "Excellent Deal - Highly Recommended";
    if (score >= 6.5)
      return "Good Deal - Recommended with Minor Considerations";
    if (score >= 5) return "Fair Deal - Proceed with Caution";
    return "Poor Deal - Consider Other Options";
  };

  const shouldSearchMore = (score: number) => score < 5.0;

  const priceDifference =
    evaluation && vehicleData ? vehicleData.price - evaluation.fair_value : 0;

  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <Box sx={{ bgcolor: "background.default", flexGrow: 1, py: 4 }}>
        <Container maxWidth="lg">
          {/* Error Alert */}
          {error && (
            <Alert severity="error" sx={{ mb: 3 }} icon={<Warning />}>
              <Typography variant="h6" gutterBottom>
                {EVALUATION_TEXT.TITLES.EVALUATION_ERROR}
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                {error}
              </Typography>
              <Button
                variant="primary"
                size="sm"
                onClick={() => evaluateDeal(vehicleData)}
              >
                {EVALUATION_TEXT.ACTIONS.RETRY_EVALUATION}
              </Button>
            </Alert>
          )}

          {/* Invalid Vehicle Data */}
          {!vehicleData && (
            <Alert severity="error" sx={{ mb: 3 }} icon={<Warning />}>
              <Typography variant="h6" gutterBottom>
                {EVALUATION_TEXT.TITLES.INVALID_VEHICLE_DATA}
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                {EVALUATION_TEXT.DESCRIPTIONS.INVALID_DATA}
              </Typography>
              <Link href={ROUTES.SEARCH} style={{ textDecoration: "none" }}>
                <Button variant="success" size="sm">
                  {EVALUATION_TEXT.ACTIONS.BACK_TO_SEARCH}
                </Button>
              </Link>
            </Alert>
          )}

          {/* Loading State */}
          {loading && vehicleData && (
            <Card>
              <Card.Body>
                <Box sx={{ textAlign: "center", py: 4 }}>
                  <Spinner size="lg" />
                  <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                    {EVALUATION_TEXT.TITLES.EVALUATING}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {EVALUATION_TEXT.DESCRIPTIONS.ANALYZING}
                  </Typography>
                  <Box sx={{ mt: 3, maxWidth: 400, mx: "auto" }}>
                    <LinearProgress />
                  </Box>
                </Box>
              </Card.Body>
            </Card>
          )}

          {/* Evaluation Results */}
          {evaluation && vehicleData && !loading && (
            <Box>
              {/* Vehicle Summary */}
              <Card shadow="md" sx={{ mb: 3 }}>
                <Card.Body>
                  <Typography variant="h5" gutterBottom>
                    {vehicleData.year} {vehicleData.make} {vehicleData.model}
                  </Typography>
                  <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
                    <Chip
                      icon={<Speed />}
                      label={`${vehicleData.mileage.toLocaleString()} miles`}
                    />
                    <Chip
                      icon={<AttachMoney />}
                      label={`$${vehicleData.price.toLocaleString()}`}
                    />
                  </Stack>
                  {vehicleData.vin && (
                    <Typography variant="caption" color="text.secondary">
                      VIN: {vehicleData.vin}
                    </Typography>
                  )}
                </Card.Body>
              </Card>

              <Card shadow="lg" sx={{ mb: 3 }}>
                <Card.Body>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{ display: "flex", alignItems: "center", gap: 1 }}
                  >
                    <TrendingUp color="primary" />
                    {EVALUATION_TEXT.TITLES.MARKET_ANALYSIS}
                  </Typography>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mb: 2 }}
                  >
                    {EVALUATION_TEXT.DESCRIPTIONS.MARKET_ANALYSIS}
                  </Typography>
                  <Divider sx={{ my: 2 }} />

                  <Grid container spacing={3}>
                    {/* Price Comparison Visual */}
                    <Grid item xs={12} md={6}>
                      <Box
                        sx={{
                          background:
                            "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                          borderRadius: 2,
                          p: 3,
                          color: "white",
                        }}
                      >
                        <Typography variant="subtitle2" sx={{ opacity: 0.9, mb: 1 }}>
                          {EVALUATION_TEXT.LABELS.MARKET_POSITION}
                        </Typography>
                        <Typography
                          variant="h3"
                          sx={{ fontWeight: "bold", mb: 2 }}
                        >
                          {priceDifference > 0 
                            ? EVALUATION_TEXT.LABELS.ABOVE_MARKET 
                            : EVALUATION_TEXT.LABELS.BELOW_MARKET}
                        </Typography>
                        <Typography variant="h4" sx={{ fontWeight: "bold" }}>
                          ${Math.abs(priceDifference).toLocaleString()}
                        </Typography>
                        <Typography variant="caption" sx={{ opacity: 0.8 }}>
                          {(
                            (Math.abs(priceDifference) / vehicleData.price) *
                            100
                          ).toFixed(1)}
                          % difference
                        </Typography>
                      </Box>
                    </Grid>

                    {/* Quick Stats */}
                    <Grid item xs={12} md={6}>
                      <Stack spacing={2}>
                        <Box sx={{ p: 2, bgcolor: "grey.50", borderRadius: 1 }}>
                          <Typography variant="caption" color="text.secondary">
                            Days on Market
                          </Typography>
                          <Typography variant="h6" fontWeight="bold">
                            32 days
                          </Typography>
                          <Typography variant="caption" color="success.main">
                            Faster than average
                          </Typography>
                        </Box>
                        <Box sx={{ p: 2, bgcolor: "grey.50", borderRadius: 1 }}>
                          <Typography variant="caption" color="text.secondary">
                            Similar Vehicles
                          </Typography>
                          <Typography variant="h6" fontWeight="bold">
                            12 in your area
                          </Typography>
                          <Typography variant="caption" color="primary.main">
                            Average: ${vehicleData.price.toLocaleString()}
                          </Typography>
                        </Box>
                      </Stack>
                    </Grid>
                  </Grid>

                  {/* Negotiation Leverage Indicator */}
                  <Box
                    sx={{
                      mt: 3,
                      p: 3,
                      bgcolor: "success.50",
                      borderRadius: 2,
                      border: "1px solid",
                      borderColor: "success.200",
                    }}
                  >
                    <Box
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 1,
                        mb: 1,
                      }}
                    >
                      <CheckCircle color="success" />
                      <Typography
                        variant="subtitle1"
                        fontWeight="bold"
                        color="success.dark"
                      >
                        Strong Negotiation Position
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      This vehicle is priced{" "}
                      {priceDifference > 0 ? "above" : "competitively with"}{" "}
                      similar listings. You have good leverage to negotiate{" "}
                      {priceDifference > 0 ? "down" : "for additional value"}.
                    </Typography>
                  </Box>
                </Card.Body>
              </Card>

              {/* Overall Score with Enhanced Visual */}
              <Card
                shadow="lg"
                sx={{
                  mb: 3,
                  border: "2px solid",
                  borderColor:
                    getScoreColor(evaluation.score) === "success"
                      ? "success.main"
                      : getScoreColor(evaluation.score) === "error"
                      ? "error.main"
                      : "warning.main",
                }}
              >
                <Card.Body>
                  <Box sx={{ textAlign: "center", py: 3 }}>
                    <Typography
                      variant="overline"
                      color="text.secondary"
                      sx={{ letterSpacing: 2 }}
                    >
                      Deal Quality Score
                    </Typography>
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "center",
                        mb: 3,
                        mt: 2,
                      }}
                    >
                      {getScoreIcon(evaluation.score)}
                    </Box>
                    <Typography
                      variant="h1"
                      component="div"
                      gutterBottom
                      sx={{ fontWeight: "bold" }}
                    >
                      {evaluation.score.toFixed(1)}
                      <Typography
                        variant="h4"
                        component="span"
                        color="text.secondary"
                        sx={{ ml: 1 }}
                      >
                        /10
                      </Typography>
                    </Typography>
                    <Chip
                      label={getRecommendation(evaluation.score)}
                      color={getScoreColor(evaluation.score)}
                      sx={{
                        mt: 2,
                        fontSize: "1.1rem",
                        py: 3,
                        px: 2,
                        fontWeight: "bold",
                      }}
                    />

                    {/* Score Breakdown */}
                    <Box
                      sx={{
                        mt: 4,
                        textAlign: "left",
                        bgcolor: "grey.50",
                        p: 3,
                        borderRadius: 2,
                      }}
                    >
                      <Typography
                        variant="subtitle2"
                        gutterBottom
                        sx={{ mb: 2 }}
                      >
                        Score Breakdown
                      </Typography>
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Box
                            sx={{
                              textAlign: "center",
                              p: 2,
                              bgcolor: "white",
                              borderRadius: 1,
                            }}
                          >
                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              Price Competitiveness
                            </Typography>
                            <Typography
                              variant="h6"
                              color="success.main"
                              sx={{ fontWeight: "bold" }}
                            >
                              {evaluation.score >= 8
                                ? "Excellent"
                                : evaluation.score >= 6.5
                                ? "Good"
                                : evaluation.score >= 5
                                ? "Fair"
                                : "Poor"}
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={6}>
                          <Box
                            sx={{
                              textAlign: "center",
                              p: 2,
                              bgcolor: "white",
                              borderRadius: 1,
                            }}
                          >
                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              Market Position
                            </Typography>
                            <Typography
                              variant="h6"
                              color="primary.main"
                              sx={{ fontWeight: "bold" }}
                            >
                              {priceDifference > 0 ? "Above" : "Below"}
                            </Typography>
                          </Box>
                        </Grid>
                      </Grid>
                    </Box>
                  </Box>
                </Card.Body>
              </Card>

              {/* Price Analysis */}
              <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} md={6}>
                  <Card>
                    <Card.Body>
                      <Typography
                        variant="h6"
                        gutterBottom
                        sx={{ display: "flex", alignItems: "center" }}
                      >
                        <AttachMoney sx={{ mr: 1 }} />
                        Asking Price
                      </Typography>
                      <Typography variant="h4">
                        ${vehicleData.price.toLocaleString()}
                      </Typography>
                    </Card.Body>
                  </Card>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Card>
                    <Card.Body>
                      <Typography
                        variant="h6"
                        gutterBottom
                        sx={{ display: "flex", alignItems: "center" }}
                      >
                        <Security sx={{ mr: 1 }} />
                        Fair Market Value
                      </Typography>
                      <Typography variant="h4">
                        ${evaluation.fair_value.toLocaleString()}
                      </Typography>
                      {priceDifference !== 0 && (
                        <Box
                          sx={{ mt: 1, display: "flex", alignItems: "center" }}
                        >
                          {priceDifference > 0 ? (
                            <>
                              <TrendingUp color="error" sx={{ mr: 0.5 }} />
                              <Typography variant="body2" color="error">
                                ${Math.abs(priceDifference).toLocaleString()}{" "}
                                above market
                              </Typography>
                            </>
                          ) : (
                            <>
                              <TrendingDown color="success" sx={{ mr: 0.5 }} />
                              <Typography variant="body2" color="success">
                                ${Math.abs(priceDifference).toLocaleString()}{" "}
                                below market
                              </Typography>
                            </>
                          )}
                        </Box>
                      )}
                    </Card.Body>
                  </Card>
                </Grid>
              </Grid>

              {/* Key Insights - Enhanced */}
              {evaluation.insights.length > 0 && (
                <Card
                  sx={{
                    mb: 3,
                    bgcolor: "primary.50",
                    border: "1px solid",
                    borderColor: "primary.200",
                  }}
                >
                  <Card.Body>
                    <Typography
                      variant="h6"
                      gutterBottom
                      sx={{ color: "primary.dark" }}
                    >
                      📊 Key Market Insights
                    </Typography>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ mb: 2 }}
                    >
                      Important factors influencing this vehicle&apos;s value
                    </Typography>
                    <Divider sx={{ mb: 2 }} />
                    <Stack spacing={2}>
                      {evaluation.insights.map((insight, index) => (
                        <Box
                          key={index}
                          sx={{
                            display: "flex",
                            alignItems: "start",
                            p: 2,
                            bgcolor: "white",
                            borderRadius: 2,
                            boxShadow: 1,
                          }}
                        >
                          <CheckCircle
                            color="success"
                            sx={{ mr: 2, mt: 0.2, fontSize: 24, flexShrink: 0 }}
                          />
                          <Typography variant="body1" sx={{ fontWeight: 500 }}>
                            {insight}
                          </Typography>
                        </Box>
                      ))}
                    </Stack>
                  </Card.Body>
                </Card>
              )}

              {/* Negotiation Talking Points - Now Visible */}
              {evaluation.talking_points &&
                evaluation.talking_points.length > 0 && (
                  <Card
                    sx={{
                      mb: 3,
                      border: "2px solid",
                      borderColor: "primary.main",
                    }}
                  >
                    <Card.Body>
                      <Typography
                        variant="h6"
                        gutterBottom
                        sx={{ display: "flex", alignItems: "center", gap: 1 }}
                      >
                        <TrendingUp color="primary" />
                        Negotiation Talking Points
                      </Typography>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mb: 2 }}
                      >
                        Use these points to strengthen your negotiation position
                      </Typography>
                      <Divider sx={{ mb: 2 }} />
                      <Stack spacing={2}>
                        {evaluation.talking_points.map((point, index) => (
                          <Box
                            key={index}
                            sx={{
                              display: "flex",
                              alignItems: "start",
                              p: 2,
                              bgcolor: "grey.50",
                              borderRadius: 2,
                              border: "1px solid",
                              borderColor: "grey.200",
                            }}
                          >
                            <Typography
                              variant="body2"
                              sx={{
                                minWidth: 32,
                                height: 32,
                                borderRadius: "50%",
                                bgcolor: "primary.main",
                                color: "white",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                mr: 2,
                                flexShrink: 0,
                                fontWeight: "bold",
                                fontSize: "1rem",
                              }}
                            >
                              {index + 1}
                            </Typography>
                            <Typography
                              variant="body1"
                              sx={{ fontWeight: 500 }}
                            >
                              {point}
                            </Typography>
                          </Box>
                        ))}
                      </Stack>
                    </Card.Body>
                  </Card>
                )}

              {/* Insurance Recommendations */}
              {/* <Card sx={{ mb: 3 }}>
                <Card.Body>
                  <Typography variant="h6" gutterBottom sx={{ mb: 3 }}>
                    Insurance Options
                  </Typography>
                  <InsuranceRecommendations
                    vehicleValue={vehicleData.price}
                    vehicleAge={new Date().getFullYear() - vehicleData.year}
                    vehicleMake={vehicleData.make}
                    vehicleModel={vehicleData.model}
                    driverAge={driverAge}
                    coverageType="full"
                    showApplyButton={true}
                    compact={false}
                  />
                </Card.Body>
              </Card> */}

              {/* Action Buttons with Clear CTAs */}
              <Box
                sx={{
                  mt: 4,
                  p: 3,
                  bgcolor: "grey.50",
                  borderRadius: 2,
                  border: "1px solid",
                  borderColor: "grey.200",
                }}
              >
                <Typography variant="h6" gutterBottom sx={{ mb: 3 }}>
                  What would you like to do next?
                </Typography>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    flexWrap: "wrap",
                    gap: 2,
                  }}
                >
                  <Button
                    variant="outline"
                    size="lg"
                    onClick={() => goToPreviousStep()}
                  >
                    ← Go Back
                  </Button>
                  <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
                    {shouldSearchMore(evaluation.score) ? (
                      <>
                        <Button
                          variant="danger"
                          size="lg"
                          onClick={() => router.push("/")}
                        >
                          Skip This Deal
                        </Button>
                        <Button
                          variant="primary"
                          size="lg"
                          onClick={() => router.push("/dashboard/search")}
                        >
                          Search More Vehicles →
                        </Button>
                      </>
                    ) : (
                      <>
                        <Button
                          variant="success"
                          size="lg"
                          onClick={() =>
                            handleVehicleSelection(
                              vehicleData,
                              "/dashboard/negotiation"
                            )
                          }
                          sx={{ fontSize: "1.1rem", px: 4 }}
                        >
                          🤝 Start Negotiation
                        </Button>
                      </>
                    )}
                  </Box>
                </Box>
                {!shouldSearchMore(evaluation.score) && (
                  <Alert severity="info" sx={{ mt: 3 }} icon={<TrendingUp />}>
                    <Typography variant="body2">
                      <strong>Next Step:</strong> Our AI negotiation assistant
                      will help you get the best possible price. You&apos;ll
                      receive talking points and real-time guidance throughout
                      the negotiation process.
                    </Typography>
                  </Alert>
                )}
              </Box>
            </Box>
          )}
        </Container>
      </Box>
    </Box>
  );
}

export default function EvaluationPage() {
  return (
    <Suspense
      fallback={
        <Box
          sx={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            minHeight: "100vh",
          }}
        >
          <Spinner size="lg" />
          <Typography sx={{ ml: 2 }}>Loading evaluation...</Typography>
        </Box>
      }
    >
      <EvaluationContent />
    </Suspense>
  );
}
