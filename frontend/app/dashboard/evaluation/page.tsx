"use client";

import { useState, Suspense, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  Box,
  Container,
  Typography,
  Alert,
} from "@mui/material";
import { Warning } from "@mui/icons-material";
import Link from "next/link";
import { useStepper } from "@/app/context";
import { Button } from "@/components";
import {
  apiClient,
  PipelineStep,
  EvaluationStepResult,
  EvaluationStatus,
} from "@/lib/api";
import {
  ProgressIndicator,
  ScoreCard,
  InsightsPanel,
  QuestionForm,
  ConditionStep,
  PriceStep,
  FinancingStep,
  RiskStep,
  FinalStep,
} from "./components";

interface VehicleInfo {
  vin?: string;
  make: string;
  model: string;
  year: number;
  price: number;
  mileage: number;
  fuelType: string;
}

interface EvaluationState {
  evaluationId: number | null;
  dealId: number;
  status: EvaluationStatus;
  currentStep: PipelineStep;
  stepResult: any;
  resultJson: Record<string, any> | null;
  completedSteps: PipelineStep[];
}

function EvaluationContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { canNavigateToStep, completeStep, isStepCompleted } = useStepper();
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [evaluationState, setEvaluationState] = useState<EvaluationState | null>(null);

  // Extract and validate vehicle data from URL params
  const vehicleData: VehicleInfo | null = (() => {
    try {
      const vin = searchParams.get("vin") || undefined;
      const make = searchParams.get("make");
      const model = searchParams.get("model");
      const yearStr = searchParams.get("year");
      const priceStr = searchParams.get("price");
      const mileageStr = searchParams.get("mileage");
      const fuelType = searchParams.get("fuelType");

      // Validate required fields
      if (!make || !model || !yearStr || !priceStr || !mileageStr) {
        return null;
      }

      const year = parseInt(yearStr);
      const price = parseFloat(priceStr);
      const mileage = parseInt(mileageStr);

      // Validate parsed values
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
      };
    } catch (err) {
      console.error("Error parsing vehicle data:", err);
      return null;
    }
  })();

  // Mock deal ID - in production, this would come from backend
  const dealId = 1;

  // Check if user can access this step
  useEffect(() => {
    if (!canNavigateToStep(3)) {
      router.push("/dashboard/search");
    } else if (!isStepCompleted(3)) {
      completeStep(3, {
        status: 'in-progress',
        vehicleData: vehicleData,
        timestamp: new Date().toISOString(),
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [canNavigateToStep, router, vehicleData]);

  // Start evaluation on mount
  useEffect(() => {
    if (vehicleData && !evaluationState) {
      startEvaluation();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [vehicleData]);

  const startEvaluation = async () => {
    if (!vehicleData) return;

    setLoading(true);
    setError(null);

    try {
      // Initial answers with VIN if available
      const initialAnswers: Record<string, string | number> = {};
      if (vehicleData.vin) {
        initialAnswers.vin = vehicleData.vin;
      }

      const response = await apiClient.startEvaluation(dealId, {
        answers: Object.keys(initialAnswers).length > 0 ? initialAnswers : null,
      });

      updateEvaluationState(response);
    } catch (err: any) {
      console.error("Error starting evaluation:", err);
      setError(err.message || "Failed to start evaluation");
    } finally {
      setLoading(false);
    }
  };

  const submitAnswers = async (answers: Record<string, string | number>) => {
    if (!evaluationState) return;

    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.submitEvaluationAnswers(
        evaluationState.dealId,
        evaluationState.evaluationId!,
        { answers }
      );

      updateEvaluationState(response);
    } catch (err: any) {
      console.error("Error submitting answers:", err);
      setError(err.message || "Failed to submit answers");
    } finally {
      setLoading(false);
    }
  };

  const updateEvaluationState = (response: EvaluationStepResult) => {
    const completedSteps: PipelineStep[] = [];
    
    // Add completed steps based on result_json
    if (response.result_json) {
      if (response.result_json.vehicle_condition?.completed) {
        completedSteps.push('vehicle_condition');
      }
      if (response.result_json.price?.completed) {
        completedSteps.push('price');
      }
      if (response.result_json.financing?.completed) {
        completedSteps.push('financing');
      }
      if (response.result_json.risk?.completed) {
        completedSteps.push('risk');
      }
      if (response.status === 'completed') {
        completedSteps.push('final');
      }
    }

    setEvaluationState({
      evaluationId: response.evaluation_id,
      dealId: response.deal_id,
      status: response.status,
      currentStep: response.current_step,
      stepResult: response.step_result,
      resultJson: response.result_json,
      completedSteps,
    });
  };

  const handleFinalize = async () => {
    completeStep(3, {
      vehicleData: vehicleData,
      evaluationState: evaluationState,
      timestamp: new Date().toISOString(),
    });
    router.push("/deals");
  };

  // Calculate scores from results
  const getScores = () => {
    if (!evaluationState?.resultJson) {
      return { overall: 0 };
    }

    const conditionScore =
      evaluationState.resultJson.vehicle_condition?.assessment?.condition_score || 0;
    const priceScore = evaluationState.resultJson.price?.assessment?.score || 0;
    const riskScore = evaluationState.resultJson.risk?.assessment?.risk_score || 0;
    
    // Calculate overall score from final if available, otherwise calculate
    let overall = 0;
    if (evaluationState.resultJson.final?.assessment?.overall_score) {
      overall = evaluationState.resultJson.final.assessment.overall_score;
    } else if (conditionScore || priceScore || riskScore) {
      // Weighted average: condition 20%, price 50%, risk 30% (inverted)
      overall = (conditionScore * 0.2) + (priceScore * 0.5) + ((10 - riskScore) * 0.3);
    }

    return {
      overall,
      condition: conditionScore,
      price: priceScore,
      risk: riskScore,
    };
  };

  const scores = getScores();

  // Generate insights based on current step
  const getInsights = () => {
    const insights: Array<{ type: 'success' | 'warning' | 'info'; message: string }> = [];

    if (!evaluationState?.stepResult) return insights;

    const { assessment } = evaluationState.stepResult;

    if (assessment?.insights) {
      assessment.insights.forEach((insight: string) => {
        insights.push({ type: 'info', message: insight });
      });
    }

    if (assessment?.condition_notes) {
      assessment.condition_notes.forEach((note: string) => {
        insights.push({ type: 'success', message: note });
      });
    }

    if (assessment?.recommended_inspection) {
      insights.push({
        type: 'warning',
        message: 'Professional inspection recommended before purchase',
      });
    }

    return insights.slice(0, 5); // Limit to 5 insights
  };

  const renderStepContent = () => {
    if (!evaluationState) return null;

    const { currentStep, stepResult, resultJson, status } = evaluationState;

    // If awaiting input, show question form
    if (status === 'awaiting_input' && stepResult?.questions) {
      const questions = stepResult.questions.map((q: string, index: number) => {
        const fieldId = stepResult.required_fields?.[index] || `field_${index}`;
        
        // Determine question type based on content
        let type: 'text' | 'radio' | 'number' = 'text';
        let options: string[] | undefined;

        if (q.toLowerCase().includes('vin')) {
          type = 'text';
        } else if (
          q.toLowerCase().includes('condition') &&
          !q.toLowerCase().includes('description')
        ) {
          type = 'radio';
          options = ['Excellent', 'Good', 'Fair', 'Poor'];
        } else if (q.toLowerCase().includes('financing')) {
          type = 'radio';
          options = ['cash', 'loan', 'lease'];
        } else if (
          q.toLowerCase().includes('rate') ||
          q.toLowerCase().includes('payment')
        ) {
          type = 'number';
        }

        return {
          id: fieldId,
          label: q,
          type,
          options,
          required: true,
        };
      });

      return (
        <QuestionForm
          questions={questions}
          onSubmit={submitAnswers}
          loading={loading}
          error={error}
        />
      );
    }

    // Show step results
    if (stepResult?.assessment) {
      const { assessment } = stepResult;

      switch (currentStep) {
        case 'vehicle_condition':
          return <ConditionStep assessment={assessment} />;
        case 'price':
          return (
            <PriceStep
              assessment={assessment}
              askingPrice={vehicleData?.price || 0}
            />
          );
        case 'financing':
          return (
            <FinancingStep
              assessment={assessment}
              purchasePrice={vehicleData?.price || 0}
            />
          );
        case 'risk':
          return <RiskStep assessment={assessment} />;
        case 'final':
          return (
            <FinalStep
              assessment={assessment}
              vehicleInfo={{
                make: vehicleData?.make || '',
                model: vehicleData?.model || '',
                year: vehicleData?.year || 0,
              }}
            />
          );
        default:
          return null;
      }
    }

    return null;
  };

  const handleContinue = async () => {
    if (!evaluationState) return;

    setLoading(true);
    setError(null);

    try {
      // Continue with empty answers to advance to next step
      const response = await apiClient.startEvaluation(evaluationState.dealId, {
        answers: null,
      });

      updateEvaluationState(response);
    } catch (err: any) {
      console.error("Error continuing evaluation:", err);
      setError(err.message || "Failed to continue evaluation");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <Box sx={{ bgcolor: "background.default", flexGrow: 1, py: 4 }}>
        <Container maxWidth="lg">
          <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
            Deal Evaluation
          </Typography>

          {/* Error Alert */}
          {error && (
            <Alert severity="error" sx={{ mb: 3 }} icon={<Warning />}>
              <Typography variant="h6" gutterBottom>
                Error
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                {error}
              </Typography>
              <Button variant="primary" size="sm" onClick={startEvaluation}>
                Retry
              </Button>
            </Alert>
          )}

          {!vehicleData && (
            <Alert severity="error" sx={{ mb: 3 }} icon={<Warning />}>
              <Typography variant="h6" gutterBottom>
                Unable to Load Vehicle Data
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                Invalid vehicle data. Please select a vehicle from the search results.
              </Typography>
              <Link href="/dashboard/results" style={{ textDecoration: "none" }}>
                <Button variant="success" size="sm">
                  Back to Results
                </Button>
              </Link>
            </Alert>
          )}

          {vehicleData && evaluationState && (
            <Box>
              {/* Progress Indicator */}
              <ProgressIndicator
                currentStep={evaluationState.currentStep}
                completedSteps={evaluationState.completedSteps}
              />

              {/* Score Card */}
              {scores.overall > 0 && (
                <Box sx={{ mb: 3 }}>
                  <ScoreCard
                    overallScore={scores.overall}
                    conditionScore={scores.condition}
                    priceScore={scores.price}
                    riskScore={scores.risk}
                  />
                </Box>
              )}

              {/* Step Content */}
              <Box sx={{ mb: 3 }}>{renderStepContent()}</Box>

              {/* Insights Panel */}
              {getInsights().length > 0 && (
                <Box sx={{ mb: 3 }}>
                  <InsightsPanel insights={getInsights()} />
                </Box>
              )}

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
                  {evaluationState.status === 'completed' ? (
                    <>
                      <Button
                        variant="danger"
                        size="lg"
                        onClick={() => router.push("/dashboard/results")}
                      >
                        Reject Deal
                      </Button>
                      <Button
                        variant="success"
                        size="lg"
                        disabled={loading}
                        onClick={handleFinalize}
                      >
                        {loading ? "Finalizing..." : "Accept & Finalize Deal"}
                      </Button>
                    </>
                  ) : (
                    evaluationState.status === 'analyzing' &&
                    evaluationState.stepResult?.assessment && (
                      <Button
                        variant="primary"
                        size="lg"
                        disabled={loading}
                        isLoading={loading}
                        onClick={handleContinue}
                      >
                        Continue to Next Step
                      </Button>
                    )
                  )}
                </Box>
              </Box>
            </Box>
          )}

          {/* Loading State */}
          {!evaluationState && vehicleData && !error && (
            <Box sx={{ textAlign: "center", py: 8 }}>
              <Typography variant="h6" gutterBottom>
                Starting Evaluation...
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Analyzing vehicle data and generating insights
              </Typography>
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
        <Typography>Loading evaluation...</Typography>
      </Box>
    }>
      <EvaluationContent />
    </Suspense>
  );
}

