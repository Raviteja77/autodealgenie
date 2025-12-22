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
import {
  apiClient,
  type NegotiationMessage,
  type DealCreate,
  type FinancingOption,
  type LenderMatch,
} from "@/lib/api";
import {
  getLatestNegotiatedPrice,
  validateNegotiatedPrice,
  formatPrice,
  formatTimestamp,
} from "@/lib/negotiation-utils";

interface VehicleInfo {
  vin?: string;
  make: string;
  model: string;
  year: number;
  price: number;
  mileage: number;
  fuelType: string;
}

interface NegotiationState {
  sessionId: number | null;
  status: "idle" | "active" | "completed" | "cancelled";
  dealId: number | null;
  vehicleData: VehicleInfo | null;
  targetPrice: number | null;
  currentRound: number;
  maxRounds: number;
  messages: NegotiationMessage[];
  suggestedPrice: number | null;
  confidence: number | null;
  isLoading: boolean;
  error: string | null;
  isTyping: boolean;
  financingOptions: FinancingOption[] | null;
  cashSavings: number | null;
}

function NegotiationContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { completeStep, canNavigateToStep } = useStepper();
  const { user } = useAuth();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContext = useNegotiationChat();

  // State management
  const [state, setState] = useState<NegotiationState>({
    sessionId: null,
    status: "idle",
    dealId: null,
    vehicleData: null,
    targetPrice: null,
    currentRound: 1,
    maxRounds: 10,
    messages: [],
    suggestedPrice: null,
    confidence: null,
    isLoading: false,
    error: null,
    isTyping: false,
    financingOptions: null,
    cashSavings: null,
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

  // Get latest negotiated price from messages
  const latestPrice = useMemo(() => {
    return getLatestNegotiatedPrice(state.messages);
  }, [state.messages]);

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
      };
    } catch (err) {
      console.error("Error parsing vehicle data:", err);
      return null;
    }
  }, [searchParams]);

  // Memoize validation result to avoid unnecessary recalculations
  const isPriceValid = useMemo(() => {
    if (!latestPrice || !vehicleData) return false;
    return validateNegotiatedPrice(
      latestPrice.price,
      vehicleData.price,
      state.targetPrice
    ).isValid;
  }, [latestPrice, vehicleData, state.targetPrice]);

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
      if (!vehicleData || state.sessionId !== null) return;

      try {
        setState((prev) => ({ ...prev, isLoading: true, error: null }));

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
        const targetPrice = vehicleData.price * 0.9; // 10% below asking price

        const response = await apiClient.createNegotiation({
          deal_id: deal.id,
          user_target_price: targetPrice,
          strategy: "moderate",
        });

        // Fetch full session details
        const session = await apiClient.getNegotiationSession(
          response.session_id
        );

        setState((prev) => ({
          ...prev,
          sessionId: session.id,
          status: session.status,
          dealId: session.deal_id,
          vehicleData,
          targetPrice,
          currentRound: session.current_round,
          maxRounds: session.max_rounds,
          messages: session.messages,
          suggestedPrice: (response.metadata.suggested_price as number) || null,
          financingOptions:
            (response.metadata.financing_options as FinancingOption[]) || null,
          cashSavings: (response.metadata.cash_savings as number) || null,
          confidence: 0.85, // Default confidence
          isLoading: false,
        }));

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
        setState((prev) => ({
          ...prev,
          isLoading: false,
          error: errorMessage,
        }));
      }
    };

    initializeNegotiation();
  }, [vehicleData, state.sessionId, user]);

  // Auto-scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  // Sync chat messages with state messages
  useEffect(() => {
    if (chatContext.messages.length > 0) {
      // Deduplicate messages by ID using a Set for O(n) performance
      const existingIds = new Set(state.messages.map((msg) => msg.id));
      const newMessages = chatContext.messages.filter(
        (msg) => !existingIds.has(msg.id)
      );

      if (newMessages.length > 0) {
        setState((prev) => ({
          ...prev,
          messages: [...prev.messages, ...newMessages],
        }));
      }
    }
    // Only depend on chatContext.messages to avoid re-syncing when state.messages changes
    // This prevents infinite loops while ensuring new chat messages are added
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chatContext.messages]);

  // Update typing indicator from chat context
  useEffect(() => {
    setState((prev) => ({
      ...prev,
      isTyping: chatContext.isTyping || prev.isTyping,
    }));
  }, [chatContext.isTyping]);

  useEffect(() => {
    scrollToBottom();
  }, [state.messages, scrollToBottom, chatContext.messages]);

  // Clear notifications after 5 seconds
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  // Handle accept offer
  const handleAcceptOffer = async () => {
    if (!state.sessionId || !vehicleData) return;

    // Validate the latest price before accepting
    const priceToAccept = latestPrice?.price || state.suggestedPrice;
    const validation = validateNegotiatedPrice(
      priceToAccept,
      vehicleData.price,
      state.targetPrice
    );

    if (!validation.isValid) {
      setNotification({
        type: "error",
        message: validation.error || "Cannot accept offer with invalid price",
      });
      return;
    }

    // Show warning if price is above target
    if (validation.error && state.targetPrice) {
      const shouldContinue = window.confirm(
        `${validation.error}\n\nDo you want to continue with accepting this offer?`
      );
      if (!shouldContinue) {
        setShowAcceptDialog(false);
        return;
      }
    }

    try {
      setState((prev) => ({ ...prev, isLoading: true, isTyping: true }));
      setShowAcceptDialog(false);

      await apiClient.processNextRound(state.sessionId, {
        user_action: "confirm",
      });

      // Fetch updated session
      const session = await apiClient.getNegotiationSession(state.sessionId);

      setState((prev) => ({
        ...prev,
        status: "completed",
        currentRound: session.current_round,
        messages: session.messages,
        isLoading: false,
        isTyping: false,
      }));

      setNotification({
        type: "success",
        message: `Congratulations! You've accepted the offer at ${formatPrice(priceToAccept || 0)}!`,
      });

      // Fetch lender recommendations with loading state
      setLoadingLenders(true);
      try {
        // Use financing options from state if available, otherwise use defaults
        const preferredTerm =
          state.financingOptions && state.financingOptions.length > 0
            ? state.financingOptions.find((opt) => opt.loan_term_months === 60)
                ?.loan_term_months || 60
            : 60;

        const lenderRecs = await apiClient.getNegotiationLenderRecommendations(
          state.sessionId,
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
      setState((prev) => ({
        ...prev,
        isLoading: false,
        isTyping: false,
        error: errorMessage,
      }));
    }
  };

  // Handle reject offer
  const handleRejectOffer = async () => {
    if (!state.sessionId) return;

    try {
      setState((prev) => ({ ...prev, isLoading: true, isTyping: true }));
      setShowRejectDialog(false);

      await apiClient.processNextRound(state.sessionId, {
        user_action: "reject",
      });

      // Fetch updated session
      const session = await apiClient.getNegotiationSession(state.sessionId);

      setState((prev) => ({
        ...prev,
        status: "cancelled",
        currentRound: session.current_round,
        messages: session.messages,
        isLoading: false,
        isTyping: false,
      }));

      setNotification({
        type: "info",
        message: "Negotiation cancelled. You can start a new one anytime.",
      });
    } catch (err) {
      console.error("Failed to reject offer:", err);
      const errorMessage =
        err instanceof Error ? err.message : "Failed to reject offer";
      setState((prev) => ({
        ...prev,
        isLoading: false,
        isTyping: false,
        error: errorMessage,
      }));
    }
  };

  // Handle counter offer
  const handleCounterOffer = async () => {
    if (!state.sessionId || !counterOfferValue) return;

    const counterPrice = parseFloat(counterOfferValue);
    if (isNaN(counterPrice) || counterPrice <= 0) {
      setNotification({
        type: "error",
        message: "Please enter a valid price",
      });
      return;
    }

    try {
      setState((prev) => ({ ...prev, isLoading: true, isTyping: true }));
      setShowCounterOfferModal(false);
      setCounterOfferValue("");

      const response = await apiClient.processNextRound(state.sessionId, {
        user_action: "counter",
        counter_offer: counterPrice,
      });

      // Fetch updated session
      const session = await apiClient.getNegotiationSession(state.sessionId);

      setState((prev) => ({
        ...prev,
        currentRound: session.current_round,
        messages: session.messages,
        suggestedPrice:
          response.metadata.suggested_price || prev.suggestedPrice,
        financingOptions:
          response.metadata.financing_options || prev.financingOptions,
        cashSavings: response.metadata.cash_savings || prev.cashSavings,
        isLoading: false,
        isTyping: false,
      }));

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
      setState((prev) => ({
        ...prev,
        isLoading: false,
        isTyping: false,
        error: errorMessage,
      }));
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
    state.messages.forEach((msg) => {
      if (!grouped[msg.round_number]) {
        grouped[msg.round_number] = [];
      }
      grouped[msg.round_number].push(msg);
    });
    return grouped;
  }, [state.messages]);

  // Calculate progress
  const progress = (state.currentRound / state.maxRounds) * 100;
  const priceProgress =
    state.vehicleData && latestPrice?.price
      ? ((state.vehicleData.price - latestPrice.price) /
          (state.vehicleData.price -
            (state.targetPrice || state.vehicleData.price * 0.9))) *
        100
      : 0;

  // Render deal outcome screens
  if (state.status === "completed") {
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
                {state.vehicleData?.year} {state.vehicleData?.make}{" "}
                {state.vehicleData?.model}!
              </Typography>
              <Divider sx={{ my: 3 }} />
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Original Price
                  </Typography>
                  <Typography variant="h6">
                    ${state.vehicleData?.price.toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Final Price
                  </Typography>
                  <Typography variant="h6" color="success.main">
                    ${(latestPrice?.price || state.suggestedPrice)?.toLocaleString()}
                  </Typography>
                </Grid>
              </Grid>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                You saved $
                {(
                  (state.vehicleData?.price || 0) - (latestPrice?.price || state.suggestedPrice || 0)
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
                    if (state.vehicleData) {
                      const finalPrice = latestPrice?.price || state.suggestedPrice || state.vehicleData.price;
                      const vehicleParams = new URLSearchParams({
                        vin: state.vehicleData.vin || "",
                        make: state.vehicleData.make,
                        model: state.vehicleData.model,
                        year: state.vehicleData.year.toString(),
                        price: finalPrice.toString(),
                        mileage: state.vehicleData.mileage.toString(),
                        fuelType: state.vehicleData.fuelType || "",
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

  if (state.status === "cancelled") {
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
          {state.error && (
            <Alert severity="error" sx={{ mb: 3 }} icon={<Warning />}>
              <AlertTitle>Unable to Load Negotiation</AlertTitle>
              <Typography variant="body2" sx={{ mb: 2 }}>
                {state.error}
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
          {state.isLoading && state.messages.length === 0 && (
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
          {vehicleData && state.messages.length > 0 && (
            <Grid container spacing={3}>
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
                          ${state.targetPrice?.toLocaleString()}
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
                          <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                            <Typography variant="caption" color="text.secondary">
                              Current Offer
                            </Typography>
                            {latestPrice.source === "ai" && (
                              <Chip label="AI" size="small" sx={{ height: 16, fontSize: "0.65rem" }} />
                            )}
                            {latestPrice.source === "dealer" && (
                              <Chip label="Dealer" color="secondary" size="small" sx={{ height: 16, fontSize: "0.65rem" }} />
                            )}
                            {latestPrice.source === "counter" && (
                              <Chip label="You" color="info" size="small" sx={{ height: 16, fontSize: "0.65rem" }} />
                            )}
                          </Box>
                          <Typography
                            variant="body2"
                            color="success.main"
                            fontWeight="bold"
                          >
                            ${latestPrice.price.toLocaleString()}
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
                          Round {state.currentRound} of {state.maxRounds}
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

                    {state.isTyping && (
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
                          disabled={state.isLoading || !isPriceValid}
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
                            state.isLoading ||
                            state.currentRound >= state.maxRounds
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
                          disabled={state.isLoading}
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
                        disabled={state.isLoading || chatContext.isSending}
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
                          value={(state.confidence || 0) * 100}
                          sx={{ flexGrow: 1, height: 8, borderRadius: 1 }}
                          color={
                            (state.confidence || 0) > 0.7
                              ? "success"
                              : (state.confidence || 0) > 0.5
                              ? "warning"
                              : "error"
                          }
                        />
                        <Typography variant="caption" fontWeight="bold">
                          {Math.round((state.confidence || 0) * 100)}%
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
                        state.targetPrice &&
                        latestPrice.price <= state.targetPrice && (
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
                      {state.currentRound > state.maxRounds * 0.7 && (
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
                              vehicleData.price - latestPrice.price
                            ).toLocaleString()}
                          </Typography>
                        </Alert>
                      )}
                    </Stack>

                    <Divider sx={{ my: 2 }} />

                    {/* Financing Options */}
                    {state.financingOptions &&
                      state.financingOptions.length > 0 &&
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
                            {state.financingOptions
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
                          {state.cashSavings && state.cashSavings > 0 && (
                            <Alert severity="info" sx={{ py: 0.5 }}>
                              <Typography variant="caption">
                                Save ${state.cashSavings.toLocaleString()} by
                                paying cash vs 60-mo loan
                              </Typography>
                            </Alert>
                          )}
                          <Divider sx={{ my: 2 }} />
                        </>
                      )}
                    {state.financingOptions &&
                      state.financingOptions.length > 0 &&
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
          {state.suggestedPrice && (
            <Typography variant="caption" color="text.secondary">
              Current offer: ${state.suggestedPrice.toLocaleString()}
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
              disabled={!counterOfferValue || state.isLoading}
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
                {latestPrice.source === "counter" && (
                  <Chip label="Your Counter" color="info" size="small" />
                )}
              </Box>
              <Typography variant="caption" color="text.secondary">
                From Round {latestPrice.round} • {formatTimestamp(latestPrice.timestamp)}
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
              disabled={state.isLoading}
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
              disabled={state.isLoading}
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
