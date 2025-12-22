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
const MESSAGE_QUEUE_RETRY_DELAY_MS = 2000; // 2 seconds
const MAX_MESSAGE_QUEUE_SIZE = 50; // Maximum queued messages

// Connection status types
type ConnectionStatus = "connected" | "connecting" | "disconnected" | "error" | "reconnecting";

// Queued message interface
interface QueuedMessage {
  id: string;
  message: string;
  messageType?: string;
  timestamp: number;
  retries: number;
}

interface ChatState {
  messages: NegotiationMessage[];
  isTyping: boolean;
  isSending: boolean;
  error: string | null;
  sessionId: number | null;
  wsConnected: boolean;
  connectionStatus: ConnectionStatus;
  reconnectAttempts: number;
  messageQueue: QueuedMessage[];
  isUsingHttpFallback: boolean;
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
  manualReconnect: () => void;
  clearMessageQueue: () => void;
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
    connectionStatus: "disconnected",
    reconnectAttempts: 0,
    messageQueue: [],
    isUsingHttpFallback: false,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const lastSyncTimestampRef = useRef<string | null>(null);
  const retryQueueTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const setSessionId = useCallback((id: number) => {
    setState((prev) => ({ ...prev, sessionId: id }));
  }, []);

  const setMessages = useCallback((messages: NegotiationMessage[]) => {
    setState((prev) => ({ ...prev, messages }));
  }, []);

  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  // Sync missed messages from server
  const syncMissedMessages = useCallback(async (sessionId: number) => {
    try {
      console.log("Syncing missed messages from server...");
      const response = await apiClient.getNegotiationSession(sessionId);
      
      setState((prev) => {
        // Get the timestamp of the last message we have
        const lastLocalTimestamp = prev.messages.length > 0
          ? prev.messages[prev.messages.length - 1].created_at
          : lastSyncTimestampRef.current;
        
        // Filter server messages to only those newer than our last message
        const missedMessages = response.messages.filter((msg) => {
          if (!lastLocalTimestamp) return true;
          return new Date(msg.created_at) > new Date(lastLocalTimestamp);
        });
        
        if (missedMessages.length > 0) {
          console.log(`Synced ${missedMessages.length} missed messages`);
          const newMessages = [...prev.messages, ...missedMessages];
          // Update last sync timestamp
          lastSyncTimestampRef.current = newMessages[newMessages.length - 1].created_at;
          return { ...prev, messages: newMessages };
        }
        
        return prev;
      });
    } catch (error) {
      console.error("Failed to sync missed messages:", error);
    }
  }, []);

  // Process queued messages
  const processMessageQueue = useCallback(async () => {
    if (!state.sessionId || state.messageQueue.length === 0 || state.isSending) {
      return;
    }
    
    const message = state.messageQueue[0];
    
    try {
      console.log("Processing queued message:", message);
      setState((prev) => ({ ...prev, isSending: true }));
      
      const request: ChatMessageRequest = {
        message: message.message,
        message_type: message.messageType || "general",
      };
      
      const response = await apiClient.sendChatMessage(state.sessionId, request);
      
      // Message sent successfully, remove from queue
      setState((prev) => {
        const newQueue = prev.messageQueue.slice(1);
        const newMessages = [...prev.messages];
        
        // Add messages if not already present
        const userExists = newMessages.some((msg) => msg.id === response.user_message.id);
        const agentExists = newMessages.some((msg) => msg.id === response.agent_message.id);
        
        if (!userExists) newMessages.push(response.user_message);
        if (!agentExists) newMessages.push(response.agent_message);
        
        return {
          ...prev,
          messages: newMessages,
          messageQueue: newQueue,
          isSending: false,
        };
      });
      
      // Process next message if any
      if (state.messageQueue.length > 1) {
        retryQueueTimeoutRef.current = setTimeout(() => {
          processMessageQueue();
        }, 500);
      }
    } catch (error) {
      console.error("Failed to send queued message:", error);
      
      // Increment retry count
      setState((prev) => {
        const newQueue = [...prev.messageQueue];
        const updatedMessage = { ...newQueue[0], retries: newQueue[0].retries + 1 };
        
        if (updatedMessage.retries >= 3) {
          // Remove message after 3 retries
          console.log("Message failed after 3 retries, removing from queue");
          newQueue.shift();
          return {
            ...prev,
            messageQueue: newQueue,
            isSending: false,
            error: "Failed to send message after 3 attempts",
          };
        } else {
          // Update retry count and try again
          newQueue[0] = updatedMessage;
          retryQueueTimeoutRef.current = setTimeout(() => {
            processMessageQueue();
          }, MESSAGE_QUEUE_RETRY_DELAY_MS);
          
          return {
            ...prev,
            messageQueue: newQueue,
            isSending: false,
          };
        }
      });
    }
  }, [state.sessionId, state.messageQueue, state.isSending]);

  const resetChat = useCallback(() => {
    setState({
      messages: [],
      isTyping: false,
      isSending: false,
      error: null,
      sessionId: null,
      wsConnected: false,
      connectionStatus: "disconnected",
      reconnectAttempts: 0,
      messageQueue: [],
      isUsingHttpFallback: false,
    });
    
    // Close WebSocket connection
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    // Clear timeouts
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (retryQueueTimeoutRef.current) {
      clearTimeout(retryQueueTimeoutRef.current);
      retryQueueTimeoutRef.current = null;
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
      setState((prev) => ({ ...prev, connectionStatus: "connecting" }));
      
      // Determine WebSocket URL based on environment
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      // Convert http/https to ws/wss
      const wsUrl = apiUrl.replace(/^https?/, (match) => match === 'https' ? 'wss' : 'ws');
      const wsEndpoint = `${wsUrl}/api/v1/negotiations/${state.sessionId}/ws`;

      console.log("Connecting to WebSocket:", wsEndpoint);
      const ws = new WebSocket(wsEndpoint);

      ws.onopen = async () => {
        console.log("WebSocket connected");
        setState((prev) => ({ 
          ...prev, 
          wsConnected: true, 
          connectionStatus: "connected",
          reconnectAttempts: 0,
          error: null,
          isUsingHttpFallback: false,
        }));
        reconnectAttemptsRef.current = 0;
        
        // Sync missed messages on reconnection
        if (state.sessionId) {
          await syncMissedMessages(state.sessionId);
        }
        
        // Send subscribe message
        ws.send(JSON.stringify({ type: "subscribe" }));
        
        // Process any queued messages
        if (state.messageQueue.length > 0) {
          console.log(`Processing ${state.messageQueue.length} queued messages`);
          processMessageQueue();
        }
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
          connectionStatus: "error",
          error: "Connection error. Retrying...",
        }));
      };

      ws.onclose = () => {
        console.log("WebSocket disconnected");
        setState((prev) => ({ 
          ...prev, 
          wsConnected: false,
          connectionStatus: reconnectAttemptsRef.current >= MAX_RECONNECT_ATTEMPTS ? "error" : "disconnected",
        }));
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
          console.log(`Reconnecting in ${delay}ms... (attempt ${reconnectAttemptsRef.current + 1}/${MAX_RECONNECT_ATTEMPTS})`);
          
          setState((prev) => ({ 
            ...prev, 
            connectionStatus: "reconnecting",
            reconnectAttempts: reconnectAttemptsRef.current + 1,
          }));
          
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++;
            connectWebSocket();
          }, delay);
        } else {
          console.log("Max reconnection attempts reached, switching to HTTP fallback");
          setState((prev) => ({
            ...prev,
            error: "Connection lost. Using HTTP fallback mode.",
            connectionStatus: "error",
            isUsingHttpFallback: true,
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
        connectionStatus: "error",
        error: "Failed to connect to real-time updates",
      }));
    }
  }, [state.sessionId, state.messageQueue, syncMissedMessages, processMessageQueue]);

  const disconnectWebSocket = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }
    
    if (retryQueueTimeoutRef.current) {
      clearTimeout(retryQueueTimeoutRef.current);
      retryQueueTimeoutRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setState((prev) => ({ ...prev, wsConnected: false, connectionStatus: "disconnected" }));
  }, []);

  // Manual reconnection attempt
  const manualReconnect = useCallback(() => {
    console.log("Manual reconnect initiated");
    
    // Reset reconnection attempts
    reconnectAttemptsRef.current = 0;
    
    // Clear existing connection
    disconnectWebSocket();
    
    // Reset error state
    setState((prev) => ({
      ...prev,
      error: null,
      reconnectAttempts: 0,
      isUsingHttpFallback: false,
    }));
    
    // Attempt to reconnect
    setTimeout(() => {
      connectWebSocket();
    }, 500);
  }, [disconnectWebSocket, connectWebSocket]);

  // Clear message queue
  const clearMessageQueue = useCallback(() => {
    setState((prev) => ({
      ...prev,
      messageQueue: [],
    }));
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

      // If WebSocket is disconnected, queue the message
      if (!state.wsConnected || state.isUsingHttpFallback) {
        console.log("WebSocket disconnected, queuing message");
        
        // Check queue size limit
        if (state.messageQueue.length >= MAX_MESSAGE_QUEUE_SIZE) {
          setState((prev) => ({
            ...prev,
            error: "Message queue is full. Please wait for connection to restore.",
          }));
          return;
        }
        
        const queuedMessage: QueuedMessage = {
          id: `${Date.now()}-${Math.random()}`,
          message,
          messageType,
          timestamp: Date.now(),
          retries: 0,
        };
        
        setState((prev) => ({
          ...prev,
          messageQueue: [...prev.messageQueue, queuedMessage],
        }));
        
        // Try to process the queue immediately if using HTTP fallback
        if (state.isUsingHttpFallback && !state.isSending) {
          processMessageQueue();
        }
        
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [state.sessionId, state.wsConnected, state.isUsingHttpFallback, state.messageQueue.length, state.isSending]
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
    manualReconnect,
    clearMessageQueue,
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
