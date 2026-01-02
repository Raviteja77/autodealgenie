"use client";

import {
  Suspense,
  useMemo,
  useState,
  useEffect,
  useRef,
  useCallback,
} from "react";
import { useSearchParams, useRouter } from "next/navigation";
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Avatar,
  Grid,
  Divider,
  Alert,
  LinearProgress,
  Chip,
  Stack,
  AlertTitle,
  Collapse,
  IconButton,
  Tabs,
  Tab,
} from "@mui/material";
import {
  SmartToy,
  Person,
  AttachMoney,
  DirectionsCar,
  Speed,
  LocalGasStation,
  Warning,
  CheckCircle,
  Cancel,
  TrendingUp,
  TrendingDown,
  ExpandMore,
  ExpandLess,
  Chat as ChatIcon,
} from "@mui/icons-material";
import Link from "next/link";
import {
  useStepper,
  useNegotiationChat,
  NegotiationChatProvider,
} from "@/app/context";
import { Button, Card, Modal, Spinner } from "@/components";
import {
  ChatInput,
  ConnectionStatusIndicator,
  FinancingComparisonModal,
  NegotiationCompletedScreen,
  NegotiationCancelledScreen,
} from "@/components";
import { useNegotiationState } from "@/lib/hooks";
import {
  apiClient,
  type NegotiationMessage,
  type LenderMatch,
} from "@/lib/api";
import { formatPrice, formatTimestamp } from "@/lib/utils/formatting";
import {
  getLatestNegotiatedPrice,
  validateNegotiatedPrice,
} from "@/lib/utils/negotiation";

interface VehicleInfo {
  vin?: string;
  make: string;
  model: string;
  year: number;
  price: number;
  mileage: number;
  fuelType: string;
  zipCode?: string;
  dealId?: string;
}

function NegotiationContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { completeStep, canNavigateToStep, getStepData, setStepData } = useStepper();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContext = useNegotiationChat();
  const hasInitializedRef = useRef(false);
  const initializationInProgressRef = useRef(false);

  // Local state for vehicle data and target price (derived from URL)
  const [vehicleData, setVehicleData] = useState<VehicleInfo | null>(null);
  const [targetPrice, setTargetPrice] = useState<number | null>(null);

  // Get evaluation data from stepper context (step 2 - evaluation now comes before negotiation)
  const evaluationStepData = getStepData<{
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

  // Use centralized negotiation state hook
  const {
    state: negotiationState,
    financingOptions,
    cashSavings,
    setSessionId,
    setStatus,
    setMessages,
    addMessages,
    setLoading,
    setError,
    setTyping,
    setCurrentRound,
  } = useNegotiationState(targetPrice, {
    maxRounds: 10,
  });

  // Extract latest price info from messages
  // This returns an object with price, source, round, and timestamp
  const latestPrice = useMemo(() => {
    return getLatestNegotiatedPrice(negotiationState.messages);
  }, [negotiationState.messages]);

  // Extract AI metadata from latest message for UI display
  const aiMetadata = useMemo(() => {
    if (negotiationState.messages.length === 0) {
      return {
        recommendedAction: null,
        strategyAdjustments: null,
        dealerConcessionRate: null,
        negotiationVelocity: null,
        marketComparison: null,
      };
    }

    const latestMsg =
      negotiationState.messages[negotiationState.messages.length - 1];
    const metadata = latestMsg.metadata || {};

    return {
      recommendedAction:
        typeof metadata.recommended_action === "string"
          ? metadata.recommended_action
          : null,
      strategyAdjustments:
        typeof metadata.strategy_adjustments === "string"
          ? metadata.strategy_adjustments
          : null,
      dealerConcessionRate:
        typeof metadata.dealer_concession_rate === "number"
          ? metadata.dealer_concession_rate
          : null,
      negotiationVelocity:
        typeof metadata.negotiation_velocity === "number"
          ? metadata.negotiation_velocity
          : null,
      marketComparison:
        typeof metadata.market_comparison === "string"
          ? metadata.market_comparison
          : null,
    };
  }, [negotiationState.messages]);

  // Computed confidence score based on negotiation progress
  const confidence = useMemo(() => {
    // Base confidence if we don't have enough data yet
    if (targetPrice == null || latestPrice == null) {
      return 0.5;
    }

    // How far along we are in the negotiation (earlier rounds generally lower confidence)
    const currentRound = negotiationState.currentRound;
    const maxRounds = negotiationState.maxRounds;
    const roundProgress = Math.min(Math.max(currentRound - 1, 0), maxRounds);
    const roundFactor = 1 - roundProgress / maxRounds; // 1.0 at start, decreases over time

    // How close the latest offer is to the user's target price
    const priceDiffRatio = Math.min(
      1,
      Math.abs(targetPrice - latestPrice.price) / Math.max(targetPrice, 1)
    );
    const priceFactor = 1 - priceDiffRatio; // 1.0 when equal, lower as we move away

    // Blend factors into a confidence score between 0 and 1
    const rawConfidence = 0.3 + 0.7 * (roundFactor * 0.5 + priceFactor * 0.5);
    const clamped = Math.min(Math.max(rawConfidence, 0), 1);

    // Round to two decimals for stable display
    return Number(clamped.toFixed(2));
  }, [
    targetPrice,
    latestPrice,
    negotiationState.currentRound,
    negotiationState.maxRounds,
  ]);

  // UI state
  const [showCounterOfferModal, setShowCounterOfferModal] = useState(false);
  const [counterOfferValue, setCounterOfferValue] = useState("");
  const [showAcceptDialog, setShowAcceptDialog] = useState(false);
  const [showRejectDialog, setShowRejectDialog] = useState(false);
  const [expandedRounds, setExpandedRounds] = useState<Set<number>>(
    new Set([1])
  );
  const [showFinancingPanel, setShowFinancingPanel] = useState(true);
  const [lenderRecommendations, setLenderRecommendations] = useState<
    LenderMatch[] | null
  >(null);
  const [loadingLenders, setLoadingLenders] = useState(false);
  const [chatTabValue, setChatTabValue] = useState(0); // 0 = Negotiation Actions, 1 = Free Chat
  const [notification, setNotification] = useState<{
    type: "success" | "warning" | "info" | "error";
    message: string;
  } | null>(null);
  const [showFinancingComparison, setShowFinancingComparison] = useState(false);

  // Extract vehicle data from URL params - effect to set vehicle data state
  useEffect(() => {
    try {
      const vin = searchParams.get("vin") || undefined;
      const make = searchParams.get("make");
      const model = searchParams.get("model");
      const yearStr = searchParams.get("year");
      const priceStr = searchParams.get("price");
      const mileageStr = searchParams.get("mileage");
      const fuelType = searchParams.get("fuelType");
      const zipCode =
        searchParams.get("zipCode") || searchParams.get("zip_code");
      const dealId = searchParams.get("dealId") || undefined;

      if (!make || !model || !yearStr || !priceStr || !mileageStr) {
        setVehicleData(null);
        return;
      }

      const year = parseInt(yearStr);
      const price = parseFloat(priceStr);
      const mileage = parseInt(mileageStr);

      if (isNaN(year) || isNaN(price) || isNaN(mileage)) {
        setVehicleData(null);
        return;
      }

      const parsedVehicleData = {
        vin,
        make,
        model,
        year,
        price,
        mileage,
        fuelType: fuelType || "Unknown",
        zipCode: zipCode || undefined,
        dealId,
      };

      setVehicleData(parsedVehicleData);
      setTargetPrice(price * 0.9);
    } catch (err) {
      console.error("Error parsing vehicle data:", err);
      setVehicleData(null);
    }
  }, [searchParams]);

  // Save query parameters to step data when page loads with valid vehicle data
  useEffect(() => {
    if (vehicleData && searchParams.toString()) {
      const existingData = getStepData(3) || {};
      // Only update if queryString is different or missing
      const existingQueryString = existingData && typeof existingData === 'object' && 'queryString' in existingData
        ? (existingData as { queryString?: string }).queryString
        : undefined;
      if (!existingQueryString || existingQueryString !== searchParams.toString()) {
        setStepData(3, {
          ...existingData,
          queryString: searchParams.toString(),
        });
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [vehicleData, searchParams]);

  // Memoize validation result to avoid unnecessary recalculations
  const isPriceValid = useMemo(() => {
    if (!latestPrice || !vehicleData) return false;
    return validateNegotiatedPrice(
      latestPrice.price,
      vehicleData.price,
      targetPrice
    ).isValid;
  }, [latestPrice, vehicleData, targetPrice]);

  // Check if user can access this step
  useEffect(() => {
    if (!canNavigateToStep(3)) {
      router.push("/dashboard/search");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Run once on mount, canNavigateToStep and router are stable

  // Mark step as in-progress (separate effect)
  useEffect(() => {
    if (vehicleData) {
      completeStep(3, {
        status: "in-progress",
        vehicleData: vehicleData,
        timestamp: new Date().toISOString(),
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [vehicleData]); // completeStep is stable from context

  // Initialize negotiation session
  useEffect(() => {
    // Guard clauses to prevent duplicate calls
    if (hasInitializedRef.current || initializationInProgressRef.current) {
      return;
    }

    if (!vehicleData || !targetPrice || negotiationState.sessionId !== null) {
      return;
    }

    const initializeNegotiation = async () => {
      initializationInProgressRef.current = true;

      try {
        setLoading(true);
        setError(null);

        // Assuming deal already exists at this point, fetch deal id
        const dealId: number = parseInt(searchParams.get("dealId")!) || 0;

        const response = await apiClient.createNegotiation({
          deal_id: dealId,
          user_target_price: targetPrice,
          strategy: "moderate",
          evaluation_data: evaluationStepData?.evaluation,
        });

        const session = await apiClient.getNegotiationSession(
          response.session_id
        );

        // Update negotiation state
        setSessionId(session.id);
        setStatus(session.status);
        setCurrentRound(session.current_round);
        setMessages(session.messages);
        setLoading(false);

        // Initialize chat context
        chatContext.setSessionId(session.id);
        chatContext.setMessages(session.messages);

        // Mark as initialized
        hasInitializedRef.current = true;

        setNotification({
          type: "success",
          message: "Negotiation session started! Let's get you the best deal.",
        });
      } catch (err) {
        console.error("Failed to initialize negotiation:", err);
        const errorMessage =
          err instanceof Error
            ? err.message
            : "Failed to initialize negotiation session";
        setError(errorMessage);
        setLoading(false);

        // Reset in progress flag on error so user can retry
        initializationInProgressRef.current = false;
      }
    };

    initializeNegotiation();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [vehicleData, targetPrice]); // Other dependencies are stable (setters, user, chatContext)

  // Auto-scroll to bottom when messages change
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  // Effect: Sync chat messages and typing indicator
  useEffect(() => {
    // Sync messages from chat context
    if (chatContext.messages.length > 0) {
      addMessages(chatContext.messages);
    }

    // Sync typing indicator
    // if (chatContext.isTyping) {
    //   setTyping(true);
    // }
  }, [chatContext.messages, addMessages, setTyping]);

  // Effect: Auto-scroll when messages change
  useEffect(() => {
    scrollToBottom();
  }, [negotiationState.messages, scrollToBottom]);

  // Clear notifications after 5 seconds
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  // Handle accept offer
  const handleAcceptOffer = useCallback(async () => {
    if (!negotiationState.sessionId || !vehicleData) return;

    // Validate the latest price before accepting
    const priceToAccept = latestPrice?.price;
    if (!priceToAccept) {
      setNotification({
        type: "error",
        message: "No valid price available to accept",
      });
      return;
    }

    const validation = validateNegotiatedPrice(
      priceToAccept,
      vehicleData.price,
      targetPrice
    );

    if (!validation.isValid) {
      setNotification({
        type: "error",
        message: validation.error || "Cannot accept offer with invalid price",
      });
      return;
    }

    // Show warning if price is above target
    if (validation.error && targetPrice) {
      const shouldContinue = window.confirm(
        `${validation.error}\n\nDo you want to continue with accepting this offer?`
      );
      if (!shouldContinue) {
        setShowAcceptDialog(false);
        return;
      }
    }

    try {
      setLoading(true);
      setTyping(true);
      setShowAcceptDialog(false);

      await apiClient.processNextRound(negotiationState.sessionId, {
        user_action: "confirm",
      });

      // Fetch updated session
      const session = await apiClient.getNegotiationSession(
        negotiationState.sessionId
      );

      setStatus("completed");
      setCurrentRound(session.current_round);
      setMessages(session.messages);
      setLoading(false);
      setTyping(false);

      setNotification({
        type: "success",
        message: `Congratulations! You've accepted the offer at ${formatPrice(
          priceToAccept
        )}!`,
      });

      // Fetch lender recommendations with loading state
      setLoadingLenders(true);
      try {
        // Use financing options from state if available, otherwise use defaults
        const preferredTerm =
          financingOptions && financingOptions.length > 0
            ? financingOptions.find((opt) => opt.loan_term_months === 60)
                ?.loan_term_months || 60
            : 60;

        const lenderRecs = await apiClient.getNegotiationLenderRecommendations(
          negotiationState.sessionId,
          preferredTerm,
          "good"
        );
        setLenderRecommendations(lenderRecs.recommendations);
      } catch (lenderErr) {
        console.error("Failed to fetch lender recommendations:", lenderErr);
        setNotification({
          type: "warning",
          message:
            "Financing options are temporarily unavailable. Your deal is still complete!",
        });
      } finally {
        setLoadingLenders(false);
      }
    } catch (err) {
      console.error("Failed to accept offer:", err);
      const errorMessage =
        err instanceof Error ? err.message : "Failed to accept offer";
      setError(errorMessage);
      setLoading(false);
      setTyping(false);
    }
  }, [
    negotiationState.sessionId,
    vehicleData,
    latestPrice,
    targetPrice,
    financingOptions,
    setLoading,
    setTyping,
    setStatus,
    setCurrentRound,
    setMessages,
    setError,
  ]);

  // Handle reject offer
  const handleRejectOffer = useCallback(async () => {
    if (!negotiationState.sessionId) return;

    try {
      setLoading(true);
      setTyping(true);
      setShowRejectDialog(false);

      await apiClient.processNextRound(negotiationState.sessionId, {
        user_action: "reject",
      });

      // Fetch updated session
      const session = await apiClient.getNegotiationSession(
        negotiationState.sessionId
      );

      setStatus("cancelled");
      setCurrentRound(session.current_round);
      setMessages(session.messages);
      setLoading(false);
      setTyping(false);

      setNotification({
        type: "info",
        message: "Negotiation cancelled. You can start a new one anytime.",
      });
    } catch (err) {
      console.error("Failed to reject offer:", err);
      const errorMessage =
        err instanceof Error ? err.message : "Failed to reject offer";
      setError(errorMessage);
      setLoading(false);
      setTyping(false);
    }
  }, [
    negotiationState.sessionId,
    setLoading,
    setTyping,
    setStatus,
    setCurrentRound,
    setMessages,
    setError,
  ]);

  // Handle counter offer
  const handleCounterOffer = useCallback(async () => {
    if (!negotiationState.sessionId || !counterOfferValue) return;

    const counterPrice = parseFloat(counterOfferValue);
    if (isNaN(counterPrice) || counterPrice <= 0) {
      setNotification({
        type: "error",
        message: "Please enter a valid price",
      });
      return;
    }

    try {
      setLoading(true);
      setTyping(true);
      setShowCounterOfferModal(false);
      setCounterOfferValue("");

      const response = await apiClient.processNextRound(
        negotiationState.sessionId,
        {
          user_action: "counter",
          counter_offer: counterPrice,
        }
      );

      // Fetch updated session
      const session = await apiClient.getNegotiationSession(
        negotiationState.sessionId
      );

      setCurrentRound(session.current_round);
      setMessages(session.messages);
      setLoading(false);
      setTyping(false);

      // Expand the new round
      setExpandedRounds((prev) => new Set(prev).add(response.current_round));

      setNotification({
        type: "info",
        message: `Counter offer of ${formatPrice(counterPrice)} submitted!`,
      });
    } catch (err) {
      console.error("Failed to submit counter offer:", err);
      const errorMessage =
        err instanceof Error ? err.message : "Failed to submit counter offer";
      setError(errorMessage);
      setLoading(false);
      setTyping(false);
    }
  }, [
    negotiationState.sessionId,
    counterOfferValue,
    setLoading,
    setTyping,
    setCurrentRound,
    setMessages,
    setError,
  ]);

  // Toggle round expansion
  const toggleRoundExpansion = useCallback((round: number) => {
    setExpandedRounds((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(round)) {
        newSet.delete(round);
      } else {
        newSet.add(round);
      }
      return newSet;
    });
  }, []);

  // Handle chat message
  const handleChatMessage = useCallback(
    async (message: string, messageType?: string) => {
      await chatContext.sendChatMessage(message, messageType);
    },
    [chatContext]
  );

  // Handle dealer info
  const handleDealerInfo = useCallback(
    async (infoType: string, content: string, priceMentioned?: number) => {
      await chatContext.sendDealerInfo(infoType, content, priceMentioned);
    },
    [chatContext]
  );

  // Group messages by round
  const messagesByRound = useMemo(() => {
    const grouped: Record<number, NegotiationMessage[]> = {};
    negotiationState.messages.forEach((msg) => {
      if (!grouped[msg.round_number]) {
        grouped[msg.round_number] = [];
      }
      grouped[msg.round_number].push(msg);
    });
    return grouped;
  }, [negotiationState.messages]);

  // Calculate progress
  const progress =
    (negotiationState.currentRound / negotiationState.maxRounds) * 100;
  const priceProgress =
    vehicleData && latestPrice?.price
      ? ((vehicleData.price - latestPrice.price) /
          (vehicleData.price - (targetPrice || vehicleData.price * 0.9))) *
        100
      : 0;

  // Render deal outcome screens
  if (negotiationState.status === "completed") {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Card shadow="lg">
          <Card.Body>
            <Box sx={{ textAlign: "center", py: 4 }}>
              <CheckCircle
                sx={{ fontSize: 80, color: "success.main", mb: 2 }}
              />
              <Typography variant="h4" gutterBottom>
                Congratulations!
              </Typography>
              <Typography variant="body1" color="text.secondary" paragraph>
                You&apos;ve successfully negotiated the deal for your{" "}
                {vehicleData?.year} {vehicleData?.make} {vehicleData?.model}!
              </Typography>
              <Divider sx={{ my: 3 }} />
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Original Price
                  </Typography>
                  <Typography variant="h6">
                    {formatPrice(vehicleData?.price || 0)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Final Price
                  </Typography>
                  <Typography variant="h6" color="success.main">
                    {formatPrice(latestPrice?.price || 0)}
                  </Typography>
                </Grid>
              </Grid>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                You saved{" "}
                {formatPrice(
                  (vehicleData?.price || 0) - (latestPrice?.price || 0)
                )}
                !
              </Typography>

              {/* Lender Recommendations */}
              {loadingLenders && (
                <>
                  <Divider sx={{ my: 3 }} />
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "center",
                      alignItems: "center",
                      py: 4,
                    }}
                  >
                    <Spinner size="md" />
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ ml: 2 }}
                    >
                      Finding the best financing options for you...
                    </Typography>
                  </Box>
                </>
              )}
              {!loadingLenders &&
                lenderRecommendations &&
                lenderRecommendations.length > 0 && (
                  <>
                    <Divider sx={{ my: 3 }} />
                    <Typography
                      variant="h6"
                      gutterBottom
                      sx={{ textAlign: "left" }}
                    >
                      Financing Options
                    </Typography>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      paragraph
                      sx={{ textAlign: "left" }}
                    >
                      Top lenders matched to your profile
                    </Typography>
                    <Stack spacing={2} sx={{ mb: 3 }}>
                      {lenderRecommendations.slice(0, 3).map((match) => (
                        <Paper
                          key={match.lender.lender_id}
                          elevation={2}
                          sx={{
                            p: 2,
                            border: match.rank === 1 ? 2 : 1,
                            borderColor:
                              match.rank === 1 ? "primary.main" : "divider",
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
                  </>
                )}

              <Stack
                direction="row"
                spacing={2}
                justifyContent="center"
                sx={{ mt: 3 }}
              >
                <Button
                  variant="success"
                  onClick={() => {
                    if (vehicleData) {
                      const finalPrice =
                        latestPrice?.price || vehicleData.price;

                      const vehicleParams = new URLSearchParams({
                        vin: vehicleData.vin || "",
                        make: vehicleData.make,
                        model: vehicleData.model,
                        year: vehicleData.year.toString(),
                        price: finalPrice.toString(),
                        mileage: vehicleData.mileage.toString(),
                        fuelType: vehicleData.fuelType || "",
                        dealId: vehicleData.dealId || ""
                      });

                      // Add zipCode if available
                      if (vehicleData.zipCode) {
                        vehicleParams.set("zipCode", vehicleData.zipCode);
                      }

                      // Complete negotiation step with final data
                      completeStep(3, {
                        status: "completed",
                        finalPrice,
                        negotiatedPrice: finalPrice,
                        savings: vehicleData.price - finalPrice,
                        timestamp: new Date().toISOString(),
                        queryString: vehicleParams.toString()
                      });

                      router.push(
                        `/dashboard/finalize?${vehicleParams.toString()}`
                      );
                    }
                  }}
                >
                  Proceed to Final Summary
                </Button>
                <Link
                  href="/dashboard/search"
                  style={{ textDecoration: "none" }}
                >
                  <Button variant="outline">Search More Vehicles</Button>
                </Link>
              </Stack>
            </Box>
          </Card.Body>
        </Card>
      </Container>
    );
  }

  if (negotiationState.status === "cancelled" && vehicleData) {
    return <NegotiationCancelledScreen vehicleData={vehicleData} />;
  }

  // Main negotiation UI
  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <Box sx={{ bgcolor: "background.default", flexGrow: 1, py: 3 }}>
        <Container maxWidth="xl">
          {/* Notification */}
          <Collapse in={!!notification}>
            <Alert
              severity={notification?.type || "info"}
              onClose={() => setNotification(null)}
              sx={{ mb: 3 }}
            >
              {notification?.message}
            </Alert>
          </Collapse>

          {/* Error Alert */}
          {negotiationState.error && (
            <Alert severity="error" sx={{ mb: 3 }} icon={<Warning />}>
              <AlertTitle>Unable to Load Negotiation</AlertTitle>
              <Typography variant="body2" sx={{ mb: 2 }}>
                {negotiationState.error}
              </Typography>
              <Link
                href="/dashboard/results"
                style={{ textDecoration: "none" }}
              >
                <Button variant="primary" size="sm">
                  Back to Results
                </Button>
              </Link>
            </Alert>
          )}

          {/* Loading State */}
          {negotiationState.isLoading &&
            negotiationState.messages.length === 0 && (
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  py: 8,
                }}
              >
                <Spinner size="lg" />
                <Typography variant="h6" sx={{ ml: 2 }}>
                  Starting your negotiation...
                </Typography>
              </Box>
            )}

          {/* Main Content */}
          {vehicleData && negotiationState.messages.length > 0 && (
            <Grid container spacing={3}>
              {/* Current Offer Status - Top Banner */}
              {/* <Grid item xs={12}>
                <CurrentOfferStatus
                  offerStatus={currentOfferStatus}
                  vehiclePrice={vehicleData.price}
                />
              </Grid> */}

              {/* Price Tracking Panel - Left Sidebar */}
              <Grid item xs={12} md={3}>
                <Card shadow="md" sx={{ position: "sticky", top: 16 }}>
                  <Card.Body>
                    <Typography variant="h6" gutterBottom>
                      Vehicle Details
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Box
                        sx={{ display: "flex", alignItems: "center", mb: 1 }}
                      >
                        <DirectionsCar
                          sx={{ mr: 1, color: "primary.main", fontSize: 20 }}
                        />
                        <Typography variant="body2" fontWeight="medium">
                          {vehicleData.year} {vehicleData.make}{" "}
                          {vehicleData.model}
                        </Typography>
                      </Box>
                      {vehicleData.vin && (
                        <Typography
                          variant="caption"
                          color="text.secondary"
                          display="block"
                          sx={{ ml: 3 }}
                        >
                          VIN: {vehicleData.vin}
                        </Typography>
                      )}
                    </Box>

                    {/* Evaluation Score Indicator */}
                    {evaluationStepData?.evaluation?.score && (
                      <>
                        <Divider sx={{ my: 2 }} />
                        <Box
                          sx={{
                            p: 2,
                            bgcolor: "success.50",
                            borderRadius: 2,
                            border: "1px solid",
                            borderColor: "success.200",
                          }}
                        >
                          <Typography
                            variant="caption"
                            color="text.secondary"
                            display="block"
                            sx={{ mb: 0.5 }}
                          >
                            AI Evaluation Score
                          </Typography>
                          <Typography
                            variant="h5"
                            fontWeight="bold"
                            color="success.dark"
                          >
                            {evaluationStepData.evaluation.score.toFixed(1)}/10
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {evaluationStepData.evaluation.score >= 8
                              ? "Excellent Deal"
                              : evaluationStepData.evaluation.score >= 6.5
                              ? "Good Deal"
                              : "Fair Deal"}
                          </Typography>
                        </Box>
                      </>
                    )}

                    <Divider sx={{ my: 2 }} />

                    <Typography variant="subtitle2" gutterBottom>
                      Price Tracking
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          mb: 1,
                        }}
                      >
                        <Typography variant="caption" color="text.secondary">
                          Asking Price
                        </Typography>
                        <Typography variant="body2" fontWeight="medium">
                          {formatPrice(vehicleData.price)}
                        </Typography>
                      </Box>
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          mb: 1,
                        }}
                      >
                        <Typography variant="caption" color="text.secondary">
                          Your Target
                        </Typography>
                        <Typography variant="body2" color="primary.main">
                          {formatPrice(targetPrice || 0)}
                        </Typography>
                      </Box>
                      {latestPrice && (
                        <Box
                          sx={{
                            display: "flex",
                            justifyContent: "space-between",
                            mb: 1,
                          }}
                        >
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              gap: 0.5,
                            }}
                          >
                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              Current Offer
                            </Typography>
                            {latestPrice.source === "ai" && (
                              <Chip
                                label="AI"
                                size="small"
                                sx={{ height: 16, fontSize: "0.65rem" }}
                              />
                            )}
                            {latestPrice.source === "dealer" && (
                              <Chip
                                label="Dealer"
                                color="secondary"
                                size="small"
                                sx={{ height: 16, fontSize: "0.65rem" }}
                              />
                            )}
                            {latestPrice.source === "user" && (
                              <Chip
                                label="You"
                                color="info"
                                size="small"
                                sx={{ height: 16, fontSize: "0.65rem" }}
                              />
                            )}
                          </Box>
                          <Typography
                            variant="body2"
                            color="success.main"
                            fontWeight="bold"
                          >
                            {formatPrice(latestPrice.price)}
                          </Typography>
                        </Box>
                      )}
                    </Box>

                    {/* Price Progress */}
                    <Box sx={{ mb: 2 }}>
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          mb: 0.5,
                        }}
                      >
                        <Typography variant="caption">Progress</Typography>
                        <Typography variant="caption">
                          {Math.round(priceProgress)}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={Math.min(priceProgress, 100)}
                        sx={{ height: 8, borderRadius: 1 }}
                      />
                    </Box>

                    <Divider sx={{ my: 2 }} />

                    <Typography variant="subtitle2" gutterBottom>
                      Negotiation Progress
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          mb: 0.5,
                        }}
                      >
                        <Typography variant="caption">
                          Round {negotiationState.currentRound} of{" "}
                          {negotiationState.maxRounds}
                        </Typography>
                        <Typography variant="caption">
                          {Math.round(progress)}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={progress}
                        color={progress > 80 ? "warning" : "primary"}
                        sx={{ height: 6, borderRadius: 1 }}
                      />
                    </Box>

                    <Divider sx={{ my: 2 }} />

                    <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                      <Speed
                        sx={{ mr: 1, color: "text.secondary", fontSize: 18 }}
                      />
                      <Typography variant="caption">
                        {vehicleData.mileage.toLocaleString()} miles
                      </Typography>
                    </Box>
                    <Box sx={{ display: "flex", alignItems: "center" }}>
                      <LocalGasStation
                        sx={{ mr: 1, color: "text.secondary", fontSize: 18 }}
                      />
                      <Typography variant="caption">
                        {vehicleData.fuelType}
                      </Typography>
                    </Box>
                  </Card.Body>
                </Card>
              </Grid>

              {/* Chat Interface - Center */}
              <Grid item xs={12} md={6}>
                <Paper
                  elevation={3}
                  sx={{
                    height: "700px",
                    display: "flex",
                    flexDirection: "column",
                  }}
                >
                  {/* Header with Tabs */}
                  <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
                    <Box
                      sx={{
                        px: 2,
                        pt: 2,
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                      }}
                    >
                      <Box>
                        <Typography variant="h6">Negotiation Chat</Typography>
                        <Typography variant="caption" color="text.secondary">
                          Communicate with the AI negotiation assistant
                        </Typography>
                      </Box>
                      {/* WebSocket Connection Status */}
                      <ConnectionStatusIndicator
                        status={chatContext.connectionStatus}
                        reconnectAttempts={chatContext.reconnectAttempts}
                        maxReconnectAttempts={5}
                        messageQueueSize={chatContext.messageQueue.length}
                        isUsingHttpFallback={chatContext.isUsingHttpFallback}
                        onManualReconnect={chatContext.manualReconnect}
                      />
                    </Box>
                    <Tabs
                      value={chatTabValue}
                      onChange={(_, v) => setChatTabValue(v)}
                    >
                      <Tab
                        label="Actions"
                        icon={<AttachMoney />}
                        iconPosition="start"
                      />
                      <Tab
                        label="Chat"
                        icon={<ChatIcon />}
                        iconPosition="start"
                      />
                    </Tabs>
                  </Box>

                  {/* Messages Area */}
                  <Box
                    sx={{
                      flexGrow: 1,
                      overflow: "auto",
                      p: 2,
                      display: "flex",
                      flexDirection: "column",
                      gap: 2,
                      bgcolor: "grey.50",
                    }}
                  >
                    {Object.entries(messagesByRound).map(
                      ([round, roundMessages]) => (
                        <Box key={round}>
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "space-between",
                              mb: 1,
                            }}
                          >
                            <Chip
                              label={`Round ${round}`}
                              size="small"
                              color="primary"
                              variant="outlined"
                            />
                            <IconButton
                              size="small"
                              onClick={() =>
                                toggleRoundExpansion(Number(round))
                              }
                            >
                              {expandedRounds.has(Number(round)) ? (
                                <ExpandLess />
                              ) : (
                                <ExpandMore />
                              )}
                            </IconButton>
                          </Box>

                          <Collapse in={expandedRounds.has(Number(round))}>
                            <Stack spacing={1.5}>
                              {roundMessages.map((message) => (
                                <Box
                                  key={message.id}
                                  sx={{
                                    display: "flex",
                                    justifyContent:
                                      message.role === "user"
                                        ? "flex-end"
                                        : "flex-start",
                                    gap: 1,
                                  }}
                                >
                                  {message.role === "agent" && (
                                    <Avatar
                                      sx={{
                                        bgcolor: "primary.main",
                                        width: 36,
                                        height: 36,
                                      }}
                                    >
                                      <SmartToy fontSize="small" />
                                    </Avatar>
                                  )}
                                  <Paper
                                    elevation={2}
                                    sx={{
                                      p: 1.5,
                                      maxWidth: "75%",
                                      bgcolor:
                                        message.role === "user"
                                          ? "primary.main"
                                          : "white",
                                      color:
                                        message.role === "user"
                                          ? "primary.contrastText"
                                          : "text.primary",
                                      borderRadius: 2,
                                    }}
                                  >
                                    {message.metadata?.message_type ===
                                      "dealer_info" && (
                                      <Chip
                                        label={
                                          message.metadata?.info_type
                                            ? `${message.metadata.info_type}`
                                            : "Dealer Info"
                                        }
                                        size="small"
                                        color="info"
                                        sx={{ mb: 1 }}
                                      />
                                    )}
                                    <Typography
                                      variant="body2"
                                      sx={{ whiteSpace: "pre-wrap" }}
                                    >
                                      {message.content}
                                    </Typography>
                                    {typeof message.metadata
                                      ?.suggested_price === "number" && (
                                      <Typography
                                        variant="caption"
                                        sx={{
                                          display: "block",
                                          mt: 0.5,
                                          fontWeight: "bold",
                                          color:
                                            message.role === "user"
                                              ? "inherit"
                                              : "success.main",
                                        }}
                                      >
                                        Suggested:{" "}
                                        {formatPrice(
                                          message.metadata.suggested_price
                                        )}
                                      </Typography>
                                    )}
                                    {message.metadata?.recommended_action ? (
                                      <Chip
                                        label={`Recommended: ${message.metadata.recommended_action}`}
                                        size="small"
                                        color="success"
                                        sx={{ mt: 1 }}
                                      />
                                    ) : (
                                      ""
                                    )}
                                    <Typography
                                      variant="caption"
                                      sx={{
                                        display: "block",
                                        mt: 0.5,
                                        opacity: 0.7,
                                      }}
                                    >
                                      {new Date(
                                        message.created_at
                                      ).toLocaleTimeString([], {
                                        hour: "2-digit",
                                        minute: "2-digit",
                                      })}
                                    </Typography>
                                  </Paper>
                                  {message.role === "user" && (
                                    <Avatar
                                      sx={{
                                        bgcolor: "secondary.main",
                                        width: 36,
                                        height: 36,
                                      }}
                                    >
                                      <Person fontSize="small" />
                                    </Avatar>
                                  )}
                                </Box>
                              ))}
                            </Stack>
                          </Collapse>
                        </Box>
                      )
                    )}

                    {/* {negotiationState.isTyping && (
                      <Box
                        sx={{
                          display: "flex",
                          gap: 1,
                          alignItems: "flex-start",
                        }}
                      >
                        <Avatar
                          sx={{
                            bgcolor: "primary.main",
                            width: 36,
                            height: 36,
                          }}
                        >
                          <SmartToy fontSize="small" />
                        </Avatar>
                        <Paper elevation={2} sx={{ p: 1.5, borderRadius: 2 }}>
                          <Typography variant="body2">
                            AI is thinking...
                          </Typography>
                        </Paper>
                      </Box>
                    )} */}
                    <div ref={messagesEndRef} />
                  </Box>

                  {/* Chat Error Display */}
                  {chatContext.error && (
                    <Alert
                      severity="error"
                      onClose={chatContext.clearError}
                      sx={{ m: 1 }}
                    >
                      {chatContext.error}
                    </Alert>
                  )}

                  {/* Action Buttons or Chat Input */}
                  {chatTabValue === 0 && (
                    <Box
                      sx={{
                        p: 2,
                        borderTop: 1,
                        borderColor: "divider",
                        bgcolor: "background.paper",
                      }}
                    >
                      <Typography
                        variant="caption"
                        color="text.secondary"
                        gutterBottom
                        display="block"
                      >
                        Choose your negotiation action:
                      </Typography>
                      <Stack
                        direction={{ xs: "column", sm: "row" }}
                        spacing={1}
                      >
                        <Button
                          variant="success"
                          size="sm"
                          fullWidth
                          leftIcon={<CheckCircle />}
                          onClick={() => setShowAcceptDialog(true)}
                          disabled={negotiationState.isLoading || !isPriceValid}
                        >
                          Accept Offer
                        </Button>
                        <Button
                          variant="primary"
                          size="sm"
                          fullWidth
                          leftIcon={<AttachMoney />}
                          onClick={() => setShowCounterOfferModal(true)}
                          disabled={
                            negotiationState.isLoading ||
                            negotiationState.currentRound >=
                              negotiationState.maxRounds
                          }
                        >
                          Counter Offer
                        </Button>
                        <Button
                          variant="danger"
                          size="sm"
                          fullWidth
                          leftIcon={<Cancel />}
                          onClick={() => setShowRejectDialog(true)}
                          disabled={negotiationState.isLoading}
                        >
                          Reject
                        </Button>
                      </Stack>
                    </Box>
                  )}

                  {chatTabValue === 1 && (
                    <Box
                      sx={{
                        p: 2,
                        borderTop: 1,
                        borderColor: "divider",
                        bgcolor: "background.paper",
                      }}
                    >
                      <ChatInput
                        onSendMessage={handleChatMessage}
                        onSendDealerInfo={handleDealerInfo}
                        disabled={
                          negotiationState.isLoading || chatContext.isSending
                        }
                        placeholder="Ask me anything about this negotiation..."
                        maxLength={2000}
                      />
                    </Box>
                  )}
                </Paper>
              </Grid>

              {/* AI Assistant Panel - Right Sidebar */}
              <Grid item xs={12} md={3}>
                <Card shadow="md" sx={{ position: "sticky", top: 16 }}>
                  <Card.Body>
                    <Typography variant="h6" gutterBottom>
                      AI Insights
                    </Typography>

                    {/* Confidence Score */}
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Deal Confidence
                      </Typography>
                      <Box
                        sx={{ display: "flex", alignItems: "center", gap: 1 }}
                      >
                        <LinearProgress
                          variant="determinate"
                          value={(confidence || 0) * 100}
                          sx={{ flexGrow: 1, height: 8, borderRadius: 1 }}
                          color={
                            (confidence || 0) > 0.7
                              ? "success"
                              : (confidence || 0) > 0.5
                              ? "warning"
                              : "error"
                          }
                        />
                        <Typography variant="caption" fontWeight="bold">
                          {Math.round((confidence || 0) * 100)}%
                        </Typography>
                      </Box>
                    </Box>

                    <Divider sx={{ my: 2 }} />

                    {/* Recommendations */}
                    <Typography variant="subtitle2" gutterBottom>
                      Recommendations
                    </Typography>
                    <Stack spacing={1} sx={{ mb: 3 }}>
                      {/* AI Recommended Action */}
                      {aiMetadata.recommendedAction && (
                        <Alert
                          severity={
                            aiMetadata.recommendedAction === "accept"
                              ? "success"
                              : aiMetadata.recommendedAction === "counter"
                              ? "info"
                              : "warning"
                          }
                          icon={
                            aiMetadata.recommendedAction === "accept" ? (
                              <CheckCircle />
                            ) : (
                              <TrendingDown />
                            )
                          }
                          sx={{ py: 0.5 }}
                        >
                          <Typography variant="caption" fontWeight="bold">
                            AI Suggests:{" "}
                            {aiMetadata.recommendedAction.toUpperCase()}
                          </Typography>
                        </Alert>
                      )}

                      {latestPrice &&
                        targetPrice &&
                        latestPrice.price <= targetPrice && (
                          <Alert
                            severity="success"
                            icon={<TrendingDown />}
                            sx={{ py: 0.5 }}
                          >
                            <Typography variant="caption">
                              You&apos;re below your target! Consider accepting.
                            </Typography>
                          </Alert>
                        )}
                      {negotiationState.currentRound >
                        negotiationState.maxRounds * 0.7 && (
                        <Alert
                          severity="warning"
                          icon={<Warning />}
                          sx={{ py: 0.5 }}
                        >
                          <Typography variant="caption">
                            Approaching max rounds. Consider finalizing soon.
                          </Typography>
                        </Alert>
                      )}
                      {latestPrice && vehicleData.price && (
                        <Alert
                          severity="info"
                          icon={<TrendingUp />}
                          sx={{ py: 0.5 }}
                        >
                          <Typography variant="caption">
                            Current savings:{" "}
                            {formatPrice(vehicleData.price - latestPrice.price)}
                          </Typography>
                        </Alert>
                      )}
                    </Stack>

                    {/* Enhanced Negotiation Analytics */}
                    {(aiMetadata.dealerConcessionRate !== null ||
                      aiMetadata.negotiationVelocity !== null ||
                      aiMetadata.marketComparison) && (
                      <>
                        <Divider sx={{ my: 2 }} />
                        <Typography variant="subtitle2" gutterBottom>
                          Negotiation Analytics
                        </Typography>
                        <Stack spacing={1.5} sx={{ mb: 3 }}>
                          {/* Dealer Concession Rate */}
                          {aiMetadata.dealerConcessionRate !== null && (
                            <Paper
                              elevation={1}
                              sx={{ p: 1.5, bgcolor: "background.default" }}
                            >
                              <Box
                                sx={{
                                  display: "flex",
                                  justifyContent: "space-between",
                                  alignItems: "center",
                                }}
                              >
                                <Typography
                                  variant="caption"
                                  color="text.secondary"
                                >
                                  Dealer Flexibility
                                </Typography>
                                <Chip
                                  label={`${(
                                    aiMetadata.dealerConcessionRate * 100
                                  ).toFixed(1)}%`}
                                  size="small"
                                  color={
                                    aiMetadata.dealerConcessionRate > 0.05
                                      ? "success"
                                      : aiMetadata.dealerConcessionRate > 0.02
                                      ? "warning"
                                      : "default"
                                  }
                                />
                              </Box>
                              <Typography
                                variant="caption"
                                color="text.secondary"
                                sx={{ display: "block", mt: 0.5 }}
                              >
                                {aiMetadata.dealerConcessionRate > 0.05
                                  ? "Dealer is very flexible"
                                  : aiMetadata.dealerConcessionRate > 0.02
                                  ? "Moderate negotiation room"
                                  : "Dealer holding firm"}
                              </Typography>
                            </Paper>
                          )}

                          {/* Negotiation Velocity */}
                          {aiMetadata.negotiationVelocity !== null && (
                            <Paper
                              elevation={1}
                              sx={{ p: 1.5, bgcolor: "background.default" }}
                            >
                              <Box
                                sx={{
                                  display: "flex",
                                  justifyContent: "space-between",
                                  alignItems: "center",
                                }}
                              >
                                <Typography
                                  variant="caption"
                                  color="text.secondary"
                                >
                                  Price Movement
                                </Typography>
                                <Chip
                                  label={
                                    formatPrice(
                                      Math.abs(aiMetadata.negotiationVelocity)
                                    ) + "/round"
                                  }
                                  size="small"
                                  color="info"
                                />
                              </Box>
                              <Typography
                                variant="caption"
                                color="text.secondary"
                                sx={{ display: "block", mt: 0.5 }}
                              >
                                Average price change per round
                              </Typography>
                            </Paper>
                          )}

                          {/* Market Comparison */}
                          {aiMetadata.marketComparison && (
                            <Alert severity="info" sx={{ py: 0.5 }}>
                              <Typography variant="caption">
                                {aiMetadata.marketComparison}
                              </Typography>
                            </Alert>
                          )}
                        </Stack>
                      </>
                    )}

                    {/* Strategy Adjustments */}
                    {aiMetadata.strategyAdjustments && (
                      <>
                        <Divider sx={{ my: 2 }} />
                        <Typography variant="subtitle2" gutterBottom>
                          AI Strategy Tip
                        </Typography>
                        <Alert
                          severity="info"
                          icon={<SmartToy />}
                          sx={{ mb: 3 }}
                        >
                          <Typography variant="caption">
                            {aiMetadata.strategyAdjustments}
                          </Typography>
                        </Alert>
                      </>
                    )}

                    <Divider sx={{ my: 2 }} />

                    {/* Financing Options */}
                    {financingOptions &&
                      financingOptions.length > 0 &&
                      showFinancingPanel && (
                        <>
                          <Box
                            sx={{
                              display: "flex",
                              justifyContent: "space-between",
                              alignItems: "center",
                              mb: 1,
                            }}
                          >
                            <Typography variant="subtitle2">
                              Financing Options
                            </Typography>
                            <IconButton
                              size="small"
                              onClick={() => setShowFinancingPanel(false)}
                            >
                              <ExpandLess />
                            </IconButton>
                          </Box>
                          <Stack spacing={1} sx={{ mb: 2 }}>
                            {financingOptions.slice(0, 2).map((option) => (
                              <Paper
                                key={option.loan_term_months}
                                elevation={1}
                                sx={{ p: 1.5, bgcolor: "background.default" }}
                              >
                                <Box
                                  sx={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                    mb: 0.5,
                                  }}
                                >
                                  <Typography
                                    variant="caption"
                                    fontWeight="bold"
                                  >
                                    {option.loan_term_months} months
                                  </Typography>
                                  <Typography
                                    variant="caption"
                                    color="primary.main"
                                    fontWeight="bold"
                                  >
                                    {formatPrice(
                                      option.monthly_payment_estimate
                                    )}
                                    /mo
                                  </Typography>
                                </Box>
                                <Box
                                  sx={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                  }}
                                >
                                  <Typography
                                    variant="caption"
                                    color="text.secondary"
                                  >
                                    {(option.estimated_apr * 100).toFixed(2)}%
                                    APR
                                  </Typography>
                                  <Typography
                                    variant="caption"
                                    color="text.secondary"
                                  >
                                    Total: {formatPrice(option.total_cost)}
                                  </Typography>
                                </Box>
                              </Paper>
                            ))}
                          </Stack>
                          {cashSavings && cashSavings > 0 && (
                            <Alert severity="info" sx={{ py: 0.5, mb: 1 }}>
                              <Typography variant="caption">
                                Save {formatPrice(cashSavings)} by paying cash
                                vs 60-mo loan
                              </Typography>
                            </Alert>
                          )}
                          <Button
                            variant="outline"
                            size="sm"
                            fullWidth
                            onClick={() => setShowFinancingComparison(true)}
                            sx={{ mt: 1 }}
                          >
                            Compare All Options
                          </Button>
                          <Divider sx={{ my: 2 }} />
                        </>
                      )}
                    {financingOptions &&
                      financingOptions.length > 0 &&
                      !showFinancingPanel && (
                        <>
                          <Box
                            sx={{
                              display: "flex",
                              justifyContent: "space-between",
                              alignItems: "center",
                              mb: 1,
                            }}
                          >
                            <Box
                              sx={{
                                display: "flex",
                                alignItems: "center",
                                gap: 1,
                              }}
                            >
                              <Typography variant="subtitle2">
                                Financing Options
                              </Typography>
                              <Chip
                                label="Available"
                                size="small"
                                color="info"
                              />
                            </Box>
                            <IconButton
                              size="small"
                              onClick={() => setShowFinancingPanel(true)}
                            >
                              <ExpandMore />
                            </IconButton>
                          </Box>
                          <Typography
                            variant="caption"
                            color="text.secondary"
                            sx={{ display: "block", mb: 2 }}
                          >
                            Click to view financing details
                          </Typography>
                          <Divider sx={{ my: 2 }} />
                        </>
                      )}

                    {/* Strategy Tips */}
                    <Typography variant="subtitle2" gutterBottom>
                      Strategy Tips
                    </Typography>
                    <Stack spacing={1} sx={{ mb: 2 }}>
                      <Typography variant="caption" color="text.secondary">
                        • Be patient and don&apos;t rush
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        • Counter with realistic offers
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        • Know your walk-away price
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        • Ask about additional perks
                      </Typography>
                    </Stack>

                    {/* Evaluation Insights */}
                    {evaluationStepData?.evaluation?.talking_points &&
                      evaluationStepData.evaluation.talking_points.length >
                        0 && (
                        <>
                          <Divider sx={{ my: 2 }} />
                          <Typography variant="subtitle2" gutterBottom>
                            💡 Evaluation Talking Points
                          </Typography>
                          <Stack spacing={1}>
                            {evaluationStepData.evaluation.talking_points
                              .slice(0, 3)
                              .map((point, idx) => (
                                <Alert
                                  key={idx}
                                  severity="info"
                                  sx={{ py: 0.5 }}
                                >
                                  <Typography variant="caption">
                                    {point}
                                  </Typography>
                                </Alert>
                              ))}
                          </Stack>
                        </>
                      )}
                  </Card.Body>
                </Card>
              </Grid>
            </Grid>
          )}
        </Container>
      </Box>

      {/* Counter Offer Modal */}
      <Modal
        isOpen={showCounterOfferModal}
        onClose={() => {
          setShowCounterOfferModal(false);
          setCounterOfferValue("");
        }}
        title="Make Counter Offer"
        size="sm"
      >
        <Box sx={{ p: 2 }}>
          <Typography variant="body2" color="text.secondary" paragraph>
            Enter your counter offer price. Be realistic and strategic to keep
            the negotiation moving forward.
          </Typography>
          <TextField
            fullWidth
            label="Counter Offer Price"
            type="number"
            value={counterOfferValue}
            onChange={(e) => setCounterOfferValue(e.target.value)}
            placeholder="Enter price"
            InputProps={{
              startAdornment: "$",
            }}
            sx={{ mb: 2 }}
          />
          {latestPrice && (
            <Typography variant="caption" color="text.secondary">
              Current offer: ${latestPrice.price.toLocaleString()}
            </Typography>
          )}
          <Stack direction="row" spacing={2} sx={{ mt: 3 }}>
            <Button
              variant="outline"
              fullWidth
              onClick={() => setShowCounterOfferModal(false)}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              fullWidth
              onClick={handleCounterOffer}
              disabled={!counterOfferValue || negotiationState.isLoading}
            >
              Submit Offer
            </Button>
          </Stack>
        </Box>
      </Modal>

      {/* Accept Offer Dialog */}
      <Modal
        isOpen={showAcceptDialog}
        onClose={() => setShowAcceptDialog(false)}
        title="Accept Offer?"
        size="sm"
      >
        <Box sx={{ p: 2 }}>
          <Typography variant="body2" paragraph>
            Are you sure you want to accept the current offer?
          </Typography>

          {/* Price Details */}
          {latestPrice && vehicleData && (
            <Box
              sx={{
                p: 2,
                mb: 2,
                bgcolor: "grey.50",
                borderRadius: 1,
                border: "1px solid",
                borderColor: "divider",
              }}
            >
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  mb: 1,
                }}
              >
                <Typography variant="h6" color="success.main">
                  {formatPrice(latestPrice.price)}
                </Typography>
                {latestPrice.source === "ai" && (
                  <Chip label="AI Suggested" color="primary" size="small" />
                )}
                {latestPrice.source === "dealer" && (
                  <Chip label="Dealer Price" color="secondary" size="small" />
                )}
                {latestPrice.source === "user" && (
                  <Chip label="Your Counter" color="info" size="small" />
                )}
              </Box>
              <Typography variant="caption" color="text.secondary">
                From Round {latestPrice.round} •{" "}
                {formatTimestamp(latestPrice.timestamp)}
              </Typography>

              <Divider sx={{ my: 1.5 }} />

              <Grid container spacing={1}>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Original Price
                  </Typography>
                  <Typography variant="body2">
                    {formatPrice(vehicleData.price)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    You Save
                  </Typography>
                  <Typography variant="body2" color="success.main">
                    {formatPrice(vehicleData.price - latestPrice.price)}
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          )}

          <Typography variant="body2" color="text.secondary" paragraph>
            This will complete the negotiation and move forward with the deal.
          </Typography>

          <Stack direction="row" spacing={2}>
            <Button
              variant="outline"
              fullWidth
              onClick={() => setShowAcceptDialog(false)}
            >
              Cancel
            </Button>
            <Button
              variant="success"
              fullWidth
              onClick={handleAcceptOffer}
              disabled={negotiationState.isLoading}
            >
              Yes, Accept
            </Button>
          </Stack>
        </Box>
      </Modal>

      {/* Reject Offer Dialog */}
      <Modal
        isOpen={showRejectDialog}
        onClose={() => setShowRejectDialog(false)}
        title="Cancel Negotiation?"
        size="sm"
      >
        <Box sx={{ p: 2 }}>
          <Typography variant="body2" paragraph>
            Are you sure you want to cancel this negotiation?
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            This will end the current negotiation session. You can always start
            a new one later.
          </Typography>
          <Stack direction="row" spacing={2}>
            <Button
              variant="outline"
              fullWidth
              onClick={() => setShowRejectDialog(false)}
            >
              Go Back
            </Button>
            <Button
              variant="danger"
              fullWidth
              onClick={handleRejectOffer}
              disabled={negotiationState.isLoading}
            >
              Yes, Cancel
            </Button>
          </Stack>
        </Box>
      </Modal>

      {/* Financing Comparison Modal */}
      {financingOptions && financingOptions.length > 0 && (
        <FinancingComparisonModal
          isOpen={showFinancingComparison}
          onClose={() => setShowFinancingComparison(false)}
          financingOptions={financingOptions}
          purchasePrice={latestPrice?.price || vehicleData?.price || 0}
          onPriceChange={(newPrice) => {
            // You could add logic here to update the negotiation with new price
            console.log("Price changed to:", newPrice);
          }}
        />
      )}
    </Box>
  );
}

export default function NegotiationPage() {
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
          <Typography sx={{ ml: 2 }}>Loading negotiation...</Typography>
        </Box>
      }
    >
      <NegotiationChatProvider>
        <NegotiationContent />
      </NegotiationChatProvider>
    </Suspense>
  );
}
