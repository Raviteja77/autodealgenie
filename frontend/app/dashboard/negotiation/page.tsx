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
import { useAuth } from "@/lib/auth/AuthProvider";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Modal } from "@/components/ui/Modal";
import { Spinner } from "@/components/ui/Spinner";
import { ChatInput } from "@/components/ChatInput";
import { CurrentOfferStatus } from "@/components/negotiation/CurrentOfferStatus";
import { useNegotiationState } from "@/lib/hooks";
import {
  apiClient,
  type NegotiationMessage,
  type DealCreate,
  type LenderMatch,
} from "@/lib/api";

interface VehicleInfo {
  vin?: string;
  make: string;
  model: string;
  year: number;
  price: number;
  mileage: number;
  fuelType: string;
}

function NegotiationContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { completeStep, canNavigateToStep } = useStepper();
  const { user } = useAuth();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContext = useNegotiationChat();

  // Additional state (not managed by useNegotiationState)
  const [, setDealId] = useState<number | null>(null);
  const [vehicleData, setVehicleData] = useState<VehicleInfo | null>(null);
  const [targetPrice, setTargetPrice] = useState<number | null>(null);
  const [confidence] = useState<number>(0.85);

  // Use centralized negotiation state hook
  const {
    state: negotiationState,
    latestPrice,
    financingOptions,
    cashSavings,
    currentOfferStatus,
    setSessionId,
    setStatus,
    setMessages,
    addMessages,
    setLoading,
    setError,
    setTyping,
    setCurrentRound,
    updateFromNextRound,
  } = useNegotiationState(targetPrice, {
    maxRounds: 10,
  });

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
      };
      
      setVehicleData(parsedVehicleData);
      setTargetPrice(price * 0.9); // Set target price to 10% below asking
    } catch (err) {
      console.error("Error parsing vehicle data:", err);
      setVehicleData(null);
    }
  }, [searchParams]);

  // Check if user can access this step
  useEffect(() => {
    if (!canNavigateToStep(2)) {
      router.push("/dashboard/search");
    }
  }, [canNavigateToStep, router]);

  // Mark step as in-progress
  useEffect(() => {
    if (vehicleData) {
      completeStep(2, {
        status: "in-progress",
        vehicleData: vehicleData,
        timestamp: new Date().toISOString(),
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [completeStep, vehicleData]);

  // Initialize negotiation session
  useEffect(() => {
    const initializeNegotiation = async () => {
      if (!vehicleData || !targetPrice || negotiationState.sessionId !== null) return;

      try {
        setLoading(true);
        setError(null);

        // Create a deal for this vehicle first
        const dealData: DealCreate = {
          customer_name: user?.full_name || user?.username || "Guest User",
          customer_email: user?.email || "guest@autodealgenie.com",
          vehicle_make: vehicleData.make,
          vehicle_model: vehicleData.model,
          vehicle_year: vehicleData.year,
          vehicle_mileage: vehicleData.mileage,
          asking_price: vehicleData.price,
          status: "in_progress",
          notes: `Negotiation started for ${vehicleData.year} ${vehicleData.make} ${vehicleData.model}`,
        };

        const deal = await apiClient.createDeal(dealData);
        setDealId(deal.id);

        const response = await apiClient.createNegotiation({
          deal_id: deal.id,
          user_target_price: targetPrice,
          strategy: "moderate",
        });

        // Fetch full session details
        const session = await apiClient.getNegotiationSession(
          response.session_id
        );

        // Update negotiation state using the hook
        setSessionId(session.id);
        setStatus(session.status);
        setCurrentRound(session.current_round);
        setMessages(session.messages);
        setLoading(false);

        // Initialize chat context with session ID and messages
        chatContext.setSessionId(session.id);
        chatContext.setMessages(session.messages);

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
      }
    };

    initializeNegotiation();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [vehicleData, targetPrice, negotiationState.sessionId, user]);

  // Auto-scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  // Consolidated effect: Sync chat messages and typing indicator
  useEffect(() => {
    // Sync messages from chat context
    if (chatContext.messages.length > 0) {
      addMessages(chatContext.messages);
    }

    // Sync typing indicator
    if (chatContext.isTyping) {
      setTyping(true);
    }

    // Auto-scroll when messages change
    scrollToBottom();
  }, [chatContext.messages, chatContext.isTyping, addMessages, setTyping, scrollToBottom]);

  // Clear notifications after 5 seconds
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  // Handle accept offer
  const handleAcceptOffer = async () => {
    if (!negotiationState.sessionId) return;

    try {
      setLoading(true);
      setTyping(true);
      setShowAcceptDialog(false);

      await apiClient.processNextRound(negotiationState.sessionId, {
        user_action: "confirm",
      });

      // Fetch updated session
      const session = await apiClient.getNegotiationSession(negotiationState.sessionId);

      setStatus("completed");
      setCurrentRound(session.current_round);
      setMessages(session.messages);
      setLoading(false);
      setTyping(false);

      setNotification({
        type: "success",
        message: "Congratulations! You've successfully negotiated the deal!",
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
  };

  // Handle reject offer
  const handleRejectOffer = async () => {
    if (!negotiationState.sessionId) return;

    try {
      setLoading(true);
      setTyping(true);
      setShowRejectDialog(false);

      await apiClient.processNextRound(negotiationState.sessionId, {
        user_action: "reject",
      });

      // Fetch updated session
      const session = await apiClient.getNegotiationSession(negotiationState.sessionId);

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
  };

  // Handle counter offer
  const handleCounterOffer = async () => {
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

      await apiClient.processNextRound(negotiationState.sessionId, {
        user_action: "counter",
        counter_offer: counterPrice,
      });

      // Fetch updated session
      const session = await apiClient.getNegotiationSession(negotiationState.sessionId);

      // Use the updateFromNextRound method to efficiently update state
      updateFromNextRound({}, session.messages, session.current_round);

      // Expand the new round
      setExpandedRounds((prev) => new Set(prev).add(session.current_round));

      setNotification({
        type: "info",
        message: `Counter offer of $${counterPrice.toLocaleString()} submitted!`,
      });
    } catch (err) {
      console.error("Failed to submit counter offer:", err);
      const errorMessage =
        err instanceof Error ? err.message : "Failed to submit counter offer";
      setError(errorMessage);
      setLoading(false);
      setTyping(false);
    }
  };

  // Toggle round expansion
  const toggleRoundExpansion = (round: number) => {
    setExpandedRounds((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(round)) {
        newSet.delete(round);
      } else {
        newSet.add(round);
      }
      return newSet;
    });
  };

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
  const progress = (negotiationState.currentRound / negotiationState.maxRounds) * 100;
  const priceProgress =
    vehicleData && latestPrice && targetPrice
      ? ((vehicleData.price - latestPrice) /
          (vehicleData.price - targetPrice)) *
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
                {vehicleData?.year} {vehicleData?.make}{" "}
                {vehicleData?.model}!
              </Typography>
              <Divider sx={{ my: 3 }} />
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Original Price
                  </Typography>
                  <Typography variant="h6">
                    ${vehicleData?.price.toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Final Price
                  </Typography>
                  <Typography variant="h6" color="success.main">
                    ${latestPrice?.toLocaleString()}
                  </Typography>
                </Grid>
              </Grid>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                You saved $
                {(
                  (vehicleData?.price || 0) - (latestPrice || 0)
                ).toLocaleString()}
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
                                $
                                {match.estimated_monthly_payment.toLocaleString()}
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
                  variant="primary"
                  onClick={() => {
                    if (vehicleData) {
                      const vehicleParams = new URLSearchParams({
                        vin: vehicleData.vin || "",
                        make: vehicleData.make,
                        model: vehicleData.model,
                        year: vehicleData.year.toString(),
                        price: (
                          latestPrice || vehicleData.price
                        ).toString(),
                        mileage: vehicleData.mileage.toString(),
                        fuelType: vehicleData.fuelType || "",
                      });
                      router.push(
                        `/dashboard/evaluation?${vehicleParams.toString()}`
                      );
                    }
                  }}
                >
                  Evaluate Deal
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

  if (negotiationState.status === "cancelled") {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Card shadow="lg">
          <Card.Body>
            <Box sx={{ textAlign: "center", py: 4 }}>
              <Cancel sx={{ fontSize: 80, color: "warning.main", mb: 2 }} />
              <Typography variant="h4" gutterBottom>
                Negotiation Cancelled
              </Typography>
              <Typography variant="body1" color="text.secondary" paragraph>
                You&apos;ve cancelled the negotiation for this vehicle.
                Don&apos;t worry, there are plenty of other great deals waiting
                for you!
              </Typography>
              <Stack
                direction="row"
                spacing={2}
                justifyContent="center"
                sx={{ mt: 3 }}
              >
                <Link
                  href="/dashboard/search"
                  style={{ textDecoration: "none" }}
                >
                  <Button variant="primary">Search More Vehicles</Button>
                </Link>
                <Link
                  href="/dashboard/results"
                  style={{ textDecoration: "none" }}
                >
                  <Button variant="outline">Back to Results</Button>
                </Link>
              </Stack>
            </Box>
          </Card.Body>
        </Card>
      </Container>
    );
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
          {negotiationState.isLoading && negotiationState.messages.length === 0 && (
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
              <Grid item xs={12}>
                <CurrentOfferStatus
                  offerStatus={currentOfferStatus}
                  vehiclePrice={vehicleData.price}
                />
              </Grid>

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
                          ${vehicleData.price.toLocaleString()}
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
                          ${targetPrice?.toLocaleString()}
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
                          <Typography variant="caption" color="text.secondary">
                            Current Offer
                          </Typography>
                          <Typography
                            variant="body2"
                            color="success.main"
                            fontWeight="bold"
                          >
                            ${latestPrice.toLocaleString()}
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
                          Round {negotiationState.currentRound} of {negotiationState.maxRounds}
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
                      <Chip
                        label={chatContext.wsConnected ? "Live" : "Offline"}
                        color={chatContext.wsConnected ? "success" : "default"}
                        size="small"
                        sx={{ ml: 1 }}
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
                                        label={`${message.metadata?.info_type} || Dealer Info`}
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
                                        Suggested: $
                                        {message.metadata.suggested_price.toLocaleString()}
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

                    {negotiationState.isTyping && (
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
                    )}
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
                          disabled={negotiationState.isLoading || !latestPrice}
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
                            negotiationState.currentRound >= negotiationState.maxRounds
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
                        disabled={negotiationState.isLoading || chatContext.isSending}
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
                      {latestPrice &&
                        targetPrice &&
                        latestPrice <= targetPrice && (
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
                      {negotiationState.currentRound > negotiationState.maxRounds * 0.7 && (
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
                            Current savings: $
                            {(
                              vehicleData.price - latestPrice
                            ).toLocaleString()}
                          </Typography>
                        </Alert>
                      )}
                    </Stack>

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
                            {financingOptions
                              .slice(0, 2)
                              .map((option) => (
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
                                      $
                                      {option.monthly_payment_estimate.toLocaleString()}
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
                                      Total: $
                                      {option.total_cost.toLocaleString()}
                                    </Typography>
                                  </Box>
                                </Paper>
                              ))}
                          </Stack>
                          {cashSavings && cashSavings > 0 && (
                            <Alert severity="info" sx={{ py: 0.5 }}>
                              <Typography variant="caption">
                                Save ${cashSavings.toLocaleString()} by
                                paying cash vs 60-mo loan
                              </Typography>
                            </Alert>
                          )}
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
                    <Stack spacing={1}>
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
              Current offer: ${latestPrice.toLocaleString()}
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
            Are you sure you want to accept the current offer of{" "}
            <strong>${latestPrice?.toLocaleString()}</strong>?
          </Typography>
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
