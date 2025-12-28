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
  Security
} from "@mui/icons-material";
import Link from "next/link";
import { useStepper } from "@/app/context";
import { Button, Card, Spinner, InsuranceRecommendations } from "@/components";
import { apiClient } from "@/lib/api";

interface VehicleInfo {
  vin?: string;
  make: string;
  model: string;
  year: number;
  price: number;
  mileage: number;
  fuelType: string;
  condition?: string;
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
  const { completeStep } = useStepper();
  
  const hasEvaluatedRef = useRef(false);
  const evaluationInProgressRef = useRef(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [evaluation, setEvaluation] = useState<DealEvaluationResult | null>(null);
  // Driver age for insurance calculation - currently using default
  const driverAge = 30;

  // Extract vehicle data from URL params
  const vehicleData: VehicleInfo | null = useMemo(() => {
    try {
      const vin = searchParams.get("vin") || undefined;
      const make = searchParams.get("make");
      const model = searchParams.get("model");
      const yearStr = searchParams.get("year");
      const priceStr = searchParams.get("price");
      const mileageStr = searchParams.get("mileage");
      const fuelType = searchParams.get("fuelType");
      const condition = searchParams.get("condition");

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
        fuelType: fuelType || "Unknown",
        condition: condition || "good",
      };
    } catch (err) {
      console.error("Error parsing vehicle data:", err);
      return null;
    }
  }, [searchParams]);

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
      });

      setEvaluation(data);
      
      // Mark as evaluated
      hasEvaluatedRef.current = true;
      
      // Complete the evaluation step
      completeStep(3, {
        status: 'completed',
        vehicleData: vehicleData,
        evaluation: data,
        timestamp: new Date().toISOString(),
      });
    } catch (err: unknown) {
      console.error("Error evaluating deal:", err);
      const errorMessage = err instanceof Error ? err.message : "Failed to evaluate deal";
      setError(errorMessage);
      
      // Reset in progress flag on error so user can retry
      evaluationInProgressRef.current = false;
    } finally {
      setLoading(false);
    }
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
    if (score >= 6.5) return "Good Deal - Recommended with Minor Considerations";
    if (score >= 5) return "Fair Deal - Proceed with Caution";
    return "Poor Deal - Consider Other Options";
  };

  const shouldSearchMore = (score: number) => score < 5.0;

  const priceDifference = evaluation && vehicleData
    ? vehicleData.price - evaluation.fair_value
    : 0;

  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <Box sx={{ bgcolor: "background.default", flexGrow: 1, py: 4 }}>
        <Container maxWidth="lg">
          <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
            Deal Evaluation Report
          </Typography>

          {/* Error Alert */}
          {error && (
            <Alert severity="error" sx={{ mb: 3 }} icon={<Warning />}>
              <Typography variant="h6" gutterBottom>
                Evaluation Error
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                {error}
              </Typography>
              <Button variant="primary" size="sm" onClick={() => evaluateDeal(vehicleData)}>
                Retry Evaluation
              </Button>
            </Alert>
          )}

          {/* Invalid Vehicle Data */}
          {!vehicleData && (
            <Alert severity="error" sx={{ mb: 3 }} icon={<Warning />}>
              <Typography variant="h6" gutterBottom>
                Unable to Load Vehicle Data
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                Invalid vehicle data. Please select a vehicle from the search results.
              </Typography>
              <Link href="/dashboard/search" style={{ textDecoration: "none" }}>
                <Button variant="success" size="sm">
                  Back to Search
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
                    Evaluating Deal...
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Analyzing pricing, market value, and vehicle condition
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
                    <Chip icon={<Speed />} label={`${vehicleData.mileage.toLocaleString()} miles`} />
                    <Chip icon={<AttachMoney />} label={`$${vehicleData.price.toLocaleString()}`} />
                  </Stack>
                  {vehicleData.vin && (
                    <Typography variant="caption" color="text.secondary">
                      VIN: {vehicleData.vin}
                    </Typography>
                  )}
                </Card.Body>
              </Card>

              {/* Overall Score */}
              <Card shadow="lg" sx={{ mb: 3 }}>
                <Card.Body>
                  <Box sx={{ textAlign: "center", py: 2 }}>
                    <Box sx={{ display: "flex", justifyContent: "center", mb: 2 }}>
                      {getScoreIcon(evaluation.score)}
                    </Box>
                    <Typography variant="h2" component="div" gutterBottom>
                      {evaluation.score.toFixed(1)}
                      <Typography variant="h5" component="span" color="text.secondary">
                        /10
                      </Typography>
                    </Typography>
                    <Chip 
                      label={getRecommendation(evaluation.score)}
                      color={getScoreColor(evaluation.score)}
                      sx={{ mt: 1, fontSize: "1rem", py: 2 }}
                    />
                  </Box>
                </Card.Body>
              </Card>

              {/* Price Analysis */}
              <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} md={6}>
                  <Card>
                    <Card.Body>
                      <Typography variant="h6" gutterBottom sx={{ display: "flex", alignItems: "center" }}>
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
                      <Typography variant="h6" gutterBottom sx={{ display: "flex", alignItems: "center" }}>
                        <Security sx={{ mr: 1 }} />
                        Fair Market Value
                      </Typography>
                      <Typography variant="h4">
                        ${evaluation.fair_value.toLocaleString()}
                      </Typography>
                      {priceDifference !== 0 && (
                        <Box sx={{ mt: 1, display: "flex", alignItems: "center" }}>
                          {priceDifference > 0 ? (
                            <>
                              <TrendingUp color="error" sx={{ mr: 0.5 }} />
                              <Typography variant="body2" color="error">
                                ${Math.abs(priceDifference).toLocaleString()} above market
                              </Typography>
                            </>
                          ) : (
                            <>
                              <TrendingDown color="success" sx={{ mr: 0.5 }} />
                              <Typography variant="body2" color="success">
                                ${Math.abs(priceDifference).toLocaleString()} below market
                              </Typography>
                            </>
                          )}
                        </Box>
                      )}
                    </Card.Body>
                  </Card>
                </Grid>
              </Grid>

              {/* Key Insights */}
              {evaluation.insights.length > 0 && (
                <Card sx={{ mb: 3 }}>
                  <Card.Body>
                    <Typography variant="h6" gutterBottom>
                      Key Insights
                    </Typography>
                    <Divider sx={{ mb: 2 }} />
                    <Stack spacing={1.5}>
                      {evaluation.insights.map((insight, index) => (
                        <Box key={index} sx={{ display: "flex", alignItems: "start" }}>
                          <CheckCircle color="primary" sx={{ mr: 1.5, mt: 0.2, fontSize: 20 }} />
                          <Typography variant="body1">{insight}</Typography>
                        </Box>
                      ))}
                    </Stack>
                  </Card.Body>
                </Card>
              )}

              {/* Negotiation Strategy */}
              {/* {evaluation.talking_points.length > 0 && (
                <Card sx={{ mb: 3 }}>
                  <Card.Body>
                    <Typography variant="h6" gutterBottom>
                      Negotiation Strategy
                    </Typography>
                    <Divider sx={{ mb: 2 }} />
                    <Stack spacing={1.5}>
                      {evaluation.talking_points.map((point, index) => (
                        <Box key={index} sx={{ display: "flex", alignItems: "start" }}>
                          <Typography 
                            variant="body2" 
                            sx={{ 
                              minWidth: 24, 
                              height: 24,
                              borderRadius: "50%",
                              bgcolor: "primary.main",
                              color: "white",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              mr: 1.5,
                              mt: 0.2,
                              fontWeight: "bold"
                            }}
                          >
                            {index + 1}
                          </Typography>
                          <Typography variant="body1">{point}</Typography>
                        </Box>
                      ))}
                    </Stack>
                  </Card.Body>
                </Card>
              )} */}

              {/* Insurance Recommendations */}
              <Card sx={{ mb: 3 }}>
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
              </Card>

              {/* Action Buttons */}
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
                  onClick={() => router.back()}
                >
                  Go Back
                </Button>
                <Box sx={{ display: "flex", gap: 2 }}>
                  {shouldSearchMore(evaluation.score) ? (
                    <>
                      <Button
                        variant="danger"
                        size="lg"
                        onClick={() => router.push("/deals")}
                      >
                        Skip This Deal
                      </Button>
                      <Button
                        variant="primary"
                        size="lg"
                        onClick={() => router.push("/dashboard/search")}
                      >
                        Search More Vehicles
                      </Button>
                    </>
                  ) : (
                    <>
                      <Button
                        variant="success"
                        size="lg"
                        onClick={() => router.push("/dashboard/search")}
                      >
                        View More Options
                      </Button>
                      {/* <Button
                        variant="success"
                        size="lg"
                        onClick={() => router.push("/deals")}
                      >
                        Proceed with This Deal
                      </Button> */}
                    </>
                  )}
                </Box>
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
    <Suspense fallback={
      <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
        <Spinner size="lg" />
        <Typography sx={{ ml: 2 }}>Loading evaluation...</Typography>
      </Box>
    }>
      <EvaluationContent />
    </Suspense>
  );
}
