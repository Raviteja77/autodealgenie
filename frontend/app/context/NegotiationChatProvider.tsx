/**
 * Negotiation Chat Context Provider
 * 
 * Manages state for the chat interface during negotiation sessions,
 * including messages, typing indicators, error handling, and real-time
 * WebSocket communication.
 */

"use client";

import {
  createContext,
  useContext,
  useState,
  useCallback,
  ReactNode,
  useEffect,
  useRef,
} from "react";
import {
  apiClient,
  type NegotiationMessage,
  type ChatMessageRequest,
  type DealerInfoRequest,
} from "@/lib/api";

// WebSocket connection constants
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_BASE_DELAY_MS = 1000; // 1 second
const RECONNECT_EXPONENTIAL_BASE = 2;
const RECONNECT_MAX_DELAY_MS = 10000; // 10 seconds
const WEBSOCKET_PING_INTERVAL_MS = 30000; // 30 seconds
const ERROR_DISPLAY_DURATION_MS = 5000; // 5 seconds

interface ChatState {
  messages: NegotiationMessage[];
  isTyping: boolean;
  isSending: boolean;
  error: string | null;
  sessionId: number | null;
  wsConnected: boolean;
}

interface ChatContextType extends ChatState {
  setSessionId: (id: number) => void;
  setMessages: (messages: NegotiationMessage[]) => void;
  sendChatMessage: (message: string, messageType?: string) => Promise<void>;
  sendDealerInfo: (
    infoType: string,
    content: string,
    priceMentioned?: number
  ) => Promise<void>;
  clearError: () => void;
  resetChat: () => void;
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

interface NegotiationChatProviderProps {
  children: ReactNode;
}

export function NegotiationChatProvider({
  children,
}: NegotiationChatProviderProps) {
  const [state, setState] = useState<ChatState>({
    messages: [],
    isTyping: false,
    isSending: false,
    error: null,
    sessionId: null,
    wsConnected: false,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const setSessionId = useCallback((id: number) => {
    setState((prev) => ({ ...prev, sessionId: id }));
  }, []);

  const setMessages = useCallback((messages: NegotiationMessage[]) => {
    setState((prev) => ({ ...prev, messages }));
  }, []);

  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  const resetChat = useCallback(() => {
    setState({
      messages: [],
      isTyping: false,
      isSending: false,
      error: null,
      sessionId: null,
      wsConnected: false,
    });
    
    // Close WebSocket connection
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const connectWebSocket = useCallback(() => {
    if (!state.sessionId || wsRef.current) return;

    // Clear any existing ping interval before creating a new connection
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }

    try {
      // Determine WebSocket URL based on environment
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      // Convert http/https to ws/wss
      const wsUrl = apiUrl.replace(/^https?/, (match) => match === 'https' ? 'wss' : 'ws');
      const wsEndpoint = `${wsUrl}/api/v1/negotiations/${state.sessionId}/ws`;

      console.log("Connecting to WebSocket:", wsEndpoint);
      const ws = new WebSocket(wsEndpoint);

      ws.onopen = () => {
        console.log("WebSocket connected");
        setState((prev) => ({ ...prev, wsConnected: true, error: null }));
        reconnectAttemptsRef.current = 0;
        
        // Send subscribe message
        ws.send(JSON.stringify({ type: "subscribe" }));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log("WebSocket message received:", data);

          switch (data.type) {
            case "new_message":
              // Add new message to state
              setState((prev) => {
                // Check if message already exists to prevent duplicates
                const exists = prev.messages.some((msg) => msg.id === data.message.id);
                if (exists) return prev;
                
                return {
                  ...prev,
                  messages: [...prev.messages, data.message],
                };
              });
              break;

            case "typing_indicator":
              setState((prev) => ({ ...prev, isTyping: data.is_typing }));
              break;

            case "error":
              setState((prev) => ({ ...prev, error: data.error }));
              break;

            case "subscribed":
              console.log("Successfully subscribed to session updates");
              break;

            case "pong":
              // Keep-alive response
              break;

            default:
              console.log("Unknown message type:", data.type);
          }
        } catch (err) {
          console.error("Failed to parse WebSocket message:", err);
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        setState((prev) => ({
          ...prev,
          wsConnected: false,
          error: "Connection error. Retrying...",
        }));
      };

      ws.onclose = () => {
        console.log("WebSocket disconnected");
        setState((prev) => ({ ...prev, wsConnected: false }));
        wsRef.current = null;
        
        // Clear ping interval when connection closes
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }

        // Attempt reconnection with exponential backoff
        if (reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
          const delay = Math.min(
            RECONNECT_BASE_DELAY_MS * Math.pow(RECONNECT_EXPONENTIAL_BASE, reconnectAttemptsRef.current),
            RECONNECT_MAX_DELAY_MS
          );
          console.log(`Reconnecting in ${delay}ms...`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++;
            connectWebSocket();
          }, delay);
        } else {
          setState((prev) => ({
            ...prev,
            error: "Connection lost. Please refresh the page.",
          }));
        }
      };

      wsRef.current = ws;

      // Set up ping interval to keep connection alive
      pingIntervalRef.current = setInterval(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({ type: "ping" }));
        }
      }, WEBSOCKET_PING_INTERVAL_MS);

    } catch (error) {
      console.error("Failed to establish WebSocket connection:", error);
      setState((prev) => ({
        ...prev,
        error: "Failed to connect to real-time updates",
      }));
    }
  }, [state.sessionId]);

  const disconnectWebSocket = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setState((prev) => ({ ...prev, wsConnected: false }));
  }, []);

  // Auto-connect when session ID is set
  useEffect(() => {
    if (state.sessionId && !wsRef.current) {
      connectWebSocket();
    }

    return () => {
      disconnectWebSocket();
    };
    // Only depend on state.sessionId to avoid unnecessary reconnections
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.sessionId]);

  const sendChatMessage = useCallback(
    async (message: string, messageType: string = "general") => {
      console.log("Sending chat message:", message, "Type:", messageType, state);
      if (!state.sessionId) {
        setState((prev) => ({
          ...prev,
          error: "No active negotiation session",
        }));
        return;
      }

      try {
        setState((prev) => ({ ...prev, isSending: true, error: null }));

        const request: ChatMessageRequest = {
          message,
          message_type: messageType,
        };

        // API call will trigger WebSocket broadcast
        const response = await apiClient.sendChatMessage(state.sessionId, request);

        // Messages will come through WebSocket, but add them as fallback
        setState((prev) => {
          const userExists = prev.messages.some((msg) => msg.id === response.user_message.id);
          const agentExists = prev.messages.some((msg) => msg.id === response.agent_message.id);
          
          const newMessages = [...prev.messages];
          if (!userExists) newMessages.push(response.user_message);
          if (!agentExists) newMessages.push(response.agent_message);
          
          return {
            ...prev,
            messages: newMessages,
            isSending: false,
          };
        });
      } catch (error) {
        console.error("Failed to send chat message:", error);
        const errorMessage =
          error instanceof Error
            ? error.message
            : "Failed to send message. Please try again.";

        setState((prev) => ({
          ...prev,
          error: errorMessage,
          isSending: false,
        }));

        // Clear error after 5 seconds
        setTimeout(() => {
          setState((prev) => ({ ...prev, error: null }));
        }, ERROR_DISPLAY_DURATION_MS);
      }
    },
    [state.sessionId]
  );

  const sendDealerInfo = useCallback(
    async (infoType: string, content: string, priceMentioned?: number) => {
      if (!state.sessionId) {
        setState((prev) => ({
          ...prev,
          error: "No active negotiation session",
        }));
        return;
      }

      try {
        setState((prev) => ({ ...prev, isSending: true, error: null }));

        const request: DealerInfoRequest = {
          info_type: infoType,
          content,
          price_mentioned: priceMentioned || null,
          metadata: null,
        };

        // API call will trigger WebSocket broadcast
        const response = await apiClient.submitDealerInfo(state.sessionId, request);

        // Messages will come through WebSocket, but add them as fallback
        setState((prev) => {
          const userExists = prev.messages.some((msg) => msg.id === response.user_message.id);
          const agentExists = prev.messages.some((msg) => msg.id === response.agent_message.id);
          
          const newMessages = [...prev.messages];
          if (!userExists) newMessages.push(response.user_message);
          if (!agentExists) newMessages.push(response.agent_message);
          
          return {
            ...prev,
            messages: newMessages,
            isSending: false,
          };
        });
      } catch (error) {
        console.error("Failed to send dealer info:", error);
        const errorMessage =
          error instanceof Error
            ? error.message
            : "Failed to analyze dealer information. Please try again.";

        setState((prev) => ({
          ...prev,
          error: errorMessage,
          isSending: false,
        }));

        // Clear error after 5 seconds
        setTimeout(() => {
          setState((prev) => ({ ...prev, error: null }));
        }, ERROR_DISPLAY_DURATION_MS);
      }
    },
    [state.sessionId]
  );

  // Auto-clear errors after 5 seconds
  useEffect(() => {
    if (state.error) {
      const timer = setTimeout(() => {
        setState((prev) => ({ ...prev, error: null }));
      }, ERROR_DISPLAY_DURATION_MS);
      return () => clearTimeout(timer);
    }
  }, [state.error]);

  const value: ChatContextType = {
    ...state,
    setSessionId,
    setMessages,
    sendChatMessage,
    sendDealerInfo,
    clearError,
    resetChat,
    connectWebSocket,
    disconnectWebSocket,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

export function useNegotiationChat() {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error(
      "useNegotiationChat must be used within NegotiationChatProvider"
    );
  }
  return context;
}
