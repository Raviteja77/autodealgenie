/**
 * Negotiation Chat Context Provider
 * 
 * Manages state for the chat interface during negotiation sessions,
 * including messages, typing indicators, and error handling.
 */

"use client";

import {
  createContext,
  useContext,
  useState,
  useCallback,
  ReactNode,
  useEffect,
} from "react";
import {
  apiClient,
  type NegotiationMessage,
  type ChatMessageRequest,
  type DealerInfoRequest,
} from "@/lib/api";

interface ChatState {
  messages: NegotiationMessage[];
  isTyping: boolean;
  isSending: boolean;
  error: string | null;
  sessionId: number | null;
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
  });

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
    });
  }, []);

  const sendChatMessage = useCallback(
    async (message: string, messageType: string = "general") => {
      if (!state.sessionId) {
        setState((prev) => ({
          ...prev,
          error: "No active negotiation session",
        }));
        return;
      }

      try {
        setState((prev) => ({ ...prev, isSending: true, isTyping: true, error: null }));

        const request: ChatMessageRequest = {
          message,
          message_type: messageType,
        };

        const response = await apiClient.sendChatMessage(state.sessionId, request);

        // Add both user and agent messages to the chat
        setState((prev) => ({
          ...prev,
          messages: [...prev.messages, response.user_message, response.agent_message],
          isSending: false,
          isTyping: false,
        }));
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
          isTyping: false,
        }));

        // Clear error after 5 seconds
        setTimeout(() => {
          setState((prev) => ({ ...prev, error: null }));
        }, 5000);
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
        setState((prev) => ({ ...prev, isSending: true, isTyping: true, error: null }));

        const request: DealerInfoRequest = {
          info_type: infoType,
          content,
          price_mentioned: priceMentioned || null,
          metadata: null,
        };

        const response = await apiClient.submitDealerInfo(state.sessionId, request);

        // Add both user and agent messages to the chat
        setState((prev) => ({
          ...prev,
          messages: [...prev.messages, response.user_message, response.agent_message],
          isSending: false,
          isTyping: false,
        }));
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
          isTyping: false,
        }));

        // Clear error after 5 seconds
        setTimeout(() => {
          setState((prev) => ({ ...prev, error: null }));
        }, 5000);
      }
    },
    [state.sessionId]
  );

  // Auto-clear errors after 5 seconds
  useEffect(() => {
    if (state.error) {
      const timer = setTimeout(() => {
        setState((prev) => ({ ...prev, error: null }));
      }, 5000);
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
