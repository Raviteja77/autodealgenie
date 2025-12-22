/**
 * Custom Hook: useNegotiationState
 * 
 * Centralizes negotiation state management with efficient deduplication,
 * computed properties, and optimized updates from WebSocket and API sources.
 *
 * Deduplication and optimized updates are applied when using the provided helpers
 * (`setMessages`, `addMessages`, and `updateFromNextRound`). Consumers should
 * treat `state.messages` as effectively readonly and must avoid mutating it
 * directly (e.g., pushing or splicing), as doing so will bypass these guarantees.
 */

import { useState, useCallback, useMemo } from "react";
import type { NegotiationMessage, FinancingOption, MessageRole } from "@/lib/api";

export interface OfferInfo {
  price: number;
  source: "user" | "dealer" | "ai";
  timestamp: string;
  roundNumber: number;
  messageId: number;
}

export interface CurrentOfferStatus {
  lastOffer: OfferInfo | null;
  status: "waiting_for_response" | "user_turn" | "completed" | "cancelled";
  comparisonToTarget: {
    amount: number;
    percentage: number;
    isAboveTarget: boolean;
  } | null;
  offerHistory: OfferInfo[];
}

export interface NegotiationStateData {
  sessionId: number | null;
  status: "idle" | "active" | "completed" | "cancelled";
  messages: NegotiationMessage[];
  isLoading: boolean;
  error: string | null;
  isTyping: boolean;
  currentRound: number;
  maxRounds: number;
}

interface UseNegotiationStateReturn {
  state: NegotiationStateData;
  latestPrice: number | null;
  financingOptions: FinancingOption[] | null;
  cashSavings: number | null;
  currentOfferStatus: CurrentOfferStatus;
  setSessionId: (id: number) => void;
  setStatus: (status: NegotiationStateData["status"]) => void;
  setMessages: (messages: NegotiationMessage[]) => void;
  addMessages: (messages: NegotiationMessage[]) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  setTyping: (isTyping: boolean) => void;
  setCurrentRound: (round: number) => void;
  updateFromNextRound: (metadata: Record<string, unknown>, messages: NegotiationMessage[], round: number) => void;
}

/**
 * Utility: Parse price from message metadata
 */
function parsePriceFromMessage(message: NegotiationMessage): number | null {
  if (!message.metadata) return null;
  
  // Check for suggested_price, counter_offer, or price fields
  const price = 
    message.metadata.suggested_price ||
    message.metadata.counter_offer ||
    message.metadata.price;
  
  return typeof price === "number" ? price : null;
}

/**
 * Type guard: Validate a single financing option
 */
function isFinancingOption(option: unknown): option is FinancingOption {
  if (typeof option !== "object" || option === null) {
    return false;
  }
  const opt = option as Record<string, unknown>;
  return (
    typeof opt.loan_amount === "number" &&
    typeof opt.monthly_payment_estimate === "number" &&
    typeof opt.loan_term_months === "number"
  );
}

/**
 * Utility: Parse financing options from message metadata
 */
function parseFinancingOptions(message: NegotiationMessage): FinancingOption[] | null {
  if (!message.metadata || !message.metadata.financing_options) return null;
  
  const options = message.metadata.financing_options;
  if (!Array.isArray(options)) {
    return null;
  }
  
  const validOptions = options.filter(isFinancingOption);
  return validOptions.length > 0 ? validOptions : null;
}

/**
 * Utility: Parse cash savings from message metadata
 */
function parseCashSavings(message: NegotiationMessage): number | null {
  if (!message.metadata) return null;
  
  const savings = message.metadata.cash_savings;
  return typeof savings === "number" ? savings : null;
}

/**
 * Utility: Deduplicate messages by ID
 */
function deduplicateMessages(messages: NegotiationMessage[]): NegotiationMessage[] {
  const seen = new Set<number>();
  return messages.filter((msg) => {
    if (seen.has(msg.id)) return false;
    seen.add(msg.id);
    return true;
  });
}

/**
 * Utility: Extract offer information from messages
 */
function extractOfferInfo(messages: NegotiationMessage[]): OfferInfo[] {
  const offers: OfferInfo[] = [];
  
  for (const message of messages) {
    const price = parsePriceFromMessage(message);
    if (price !== null) {
      let source: OfferInfo["source"];
      if (message.role === "user") {
        source = "user";
      } else if (message.role === "dealer_sim") {
        source = "dealer";
      } else if (message.role === "agent") {
        source = "ai";
      } else {
        // Fallback for unexpected role values
        source = "ai";
      }
      
      offers.push({
        price,
        source,
        timestamp: message.created_at,
        roundNumber: message.round_number,
        messageId: message.id,
      });
    }
  }
  
  // Sort by timestamp (most recent last)
  return offers.sort((a, b) => 
    new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  );
}

/**
 * Main Hook: useNegotiationState
 */
export function useNegotiationState(
  targetPrice: number | null,
  initialState?: Partial<NegotiationStateData>
): UseNegotiationStateReturn {
  const [state, setState] = useState<NegotiationStateData>({
    sessionId: null,
    status: "idle",
    messages: [],
    isLoading: false,
    error: null,
    isTyping: false,
    currentRound: 1,
    maxRounds: 10,
    ...initialState,
  });

  // Computed: Latest price from messages
  const latestPrice = useMemo(() => {
    if (state.messages.length === 0) return null;
    
    // Search from most recent to oldest
    for (let i = state.messages.length - 1; i >= 0; i--) {
      const price = parsePriceFromMessage(state.messages[i]);
      if (price !== null) return price;
    }
    
    return null;
  }, [state.messages]);

  // Computed: Latest financing options from messages
  const financingOptions = useMemo(() => {
    if (state.messages.length === 0) return null;
    
    // Search from most recent to oldest
    for (let i = state.messages.length - 1; i >= 0; i--) {
      const options = parseFinancingOptions(state.messages[i]);
      if (options !== null) return options;
    }
    
    return null;
  }, [state.messages]);

  // Computed: Latest cash savings from messages
  const cashSavings = useMemo(() => {
    if (state.messages.length === 0) return null;
    
    // Search from most recent to oldest
    for (let i = state.messages.length - 1; i >= 0; i--) {
      const savings = parseCashSavings(state.messages[i]);
      if (savings !== null) return savings;
    }
    
    return null;
  }, [state.messages]);

  // Computed: Current offer status
  const currentOfferStatus = useMemo<CurrentOfferStatus>(() => {
    const offerHistory = extractOfferInfo(state.messages);
    const lastOffer = offerHistory.length > 0 ? offerHistory[offerHistory.length - 1] : null;
    
    // Determine status
    let status: CurrentOfferStatus["status"] = "waiting_for_response";
    if (state.status === "completed") {
      status = "completed";
    } else if (state.status === "cancelled") {
      status = "cancelled";
    } else if (offerHistory.length === 0) {
      // No offers yet - it's the user's turn to start
      status = "user_turn";
    } else if (lastOffer?.source === "ai" || lastOffer?.source === "dealer") {
      status = "user_turn";
    } else if (lastOffer?.source === "user") {
      status = "waiting_for_response";
    }
    
    // Calculate comparison to target
    let comparisonToTarget = null;
    if (lastOffer && targetPrice) {
      const amount = lastOffer.price - targetPrice;
      const percentage = (amount / targetPrice) * 100;
      comparisonToTarget = {
        amount,
        percentage,
        isAboveTarget: amount > 0,
      };
    }
    
    // Get latest 5 offers
    const recentOffers = offerHistory.slice(-5);
    
    return {
      lastOffer,
      status,
      comparisonToTarget,
      offerHistory: recentOffers,
    };
  }, [state.messages, state.status, targetPrice]);

  // Actions
  const setSessionId = useCallback((id: number) => {
    setState((prev) => ({ ...prev, sessionId: id }));
  }, []);

  const setStatus = useCallback((status: NegotiationStateData["status"]) => {
    setState((prev) => ({ ...prev, status }));
  }, []);

  const setMessages = useCallback((messages: NegotiationMessage[]) => {
    setState((prev) => ({ ...prev, messages: deduplicateMessages(messages) }));
  }, []);

  const addMessages = useCallback((newMessages: NegotiationMessage[]) => {
    setState((prev) => ({
      ...prev,
      messages: deduplicateMessages([...prev.messages, ...newMessages]),
    }));
  }, []);

  const setLoading = useCallback((isLoading: boolean) => {
    setState((prev) => ({ ...prev, isLoading }));
  }, []);

  const setError = useCallback((error: string | null) => {
    setState((prev) => ({ ...prev, error }));
  }, []);

  const setTyping = useCallback((isTyping: boolean) => {
    setState((prev) => ({ ...prev, isTyping }));
  }, []);

  const setCurrentRound = useCallback((round: number) => {
    setState((prev) => ({ ...prev, currentRound: round }));
  }, []);

  const updateFromNextRound = useCallback(
    (metadata: Record<string, unknown>, messages: NegotiationMessage[], round: number) => {
      setState((prev) => ({
        ...prev,
        currentRound: round,
        messages: deduplicateMessages([...prev.messages, ...messages]),
        isLoading: false,
        isTyping: false,
      }));
    },
    []
  );

  return {
    state,
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
  };
}
