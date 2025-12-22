/**
 * Chat Input Component for Negotiation Page
 * 
 * Provides a text input field for sending messages during negotiation
 * with validation and proper error handling.
 */

import { useState, KeyboardEvent, ChangeEvent } from "react";
import { Box, TextField, InputAdornment, IconButton, CircularProgress } from "@mui/material";
import { Send, AttachFile } from "@mui/icons-material";
import { Button } from "@/components/ui/Button";

interface ChatInputProps {
  onSendMessage: (message: string, type?: string) => Promise<void>;
  onSendDealerInfo?: (type: string, content: string, price?: number) => Promise<void>;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
}

export function ChatInput({
  onSendMessage,
  onSendDealerInfo,
  disabled = false,
  placeholder = "Type your message...",
  maxLength = 2000,
}: ChatInputProps) {
  const [message, setMessage] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [showDealerInfo, setShowDealerInfo] = useState(false);
  const [dealerInfoType, setDealerInfoType] = useState("price_quote");
  const [dealerPrice, setDealerPrice] = useState("");

  const handleSendMessage = async () => {
    if (!message.trim() || isSending || disabled) return;

    try {
      setIsSending(true);
      await onSendMessage(message.trim(), "general");
      setMessage("");
    } catch (error) {
      console.error("Failed to send message:", error);
    } finally {
      setIsSending(false);
    }
  };

  const handleSendDealerInfo = async () => {
    if (!message.trim() || isSending || disabled || !onSendDealerInfo) return;

    try {
      setIsSending(true);
      const price = dealerPrice ? parseFloat(dealerPrice) : undefined;
      await onSendDealerInfo(dealerInfoType, message.trim(), price);
      setMessage("");
      setDealerPrice("");
      setShowDealerInfo(false);
    } catch (error) {
      console.error("Failed to send dealer info:", error);
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLDivElement>) => {
    // Prevent submission when disabled or sending
    if (disabled || isSending) return;
    
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (showDealerInfo && onSendDealerInfo) {
        handleSendDealerInfo();
      } else {
        handleSendMessage();
      }
    }
  };

  const handleChange = (e: ChangeEvent<HTMLTextAreaElement | HTMLInputElement>) => {
    const value = e.target.value;
    if (value.length <= maxLength) {
      setMessage(value);
    }
  };

  return (
    <Box sx={{ width: "100%" }}>
      {showDealerInfo && onSendDealerInfo && (
        <Box sx={{ mb: 1, p: 1, bgcolor: "background.paper", borderRadius: 1 }}>
          <Box sx={{ display: "flex", gap: 1, mb: 1 }}>
            <TextField
              select
              size="small"
              value={dealerInfoType}
              onChange={(e) => setDealerInfoType(e.target.value)}
              SelectProps={{ native: true }}
              sx={{ minWidth: 150 }}
            >
              <option value="price_quote">Price Quote</option>
              <option value="inspection_report">Inspection Report</option>
              <option value="additional_offer">Additional Offer</option>
              <option value="other">Other</option>
            </TextField>
            <TextField
              size="small"
              type="number"
              placeholder="Price (optional)"
              value={dealerPrice}
              onChange={(e) => setDealerPrice(e.target.value)}
              sx={{ flex: 1 }}
            />
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setShowDealerInfo(false);
                setDealerPrice("");
              }}
            >
              Cancel
            </Button>
          </Box>
        </Box>
      )}

      <Box sx={{ display: "flex", alignItems: "flex-end", gap: 1 }}>
        {onSendDealerInfo && !showDealerInfo && (
          <IconButton
            onClick={() => setShowDealerInfo(true)}
            disabled={disabled || isSending}
            color="primary"
            sx={{ mb: 0.5 }}
          >
            <AttachFile />
          </IconButton>
        )}

        <TextField
          fullWidth
          multiline
          maxRows={4}
          value={message}
          onChange={handleChange}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
          disabled={disabled || isSending}
          helperText={`${message.length}/${maxLength}`}
          sx={{
            "& .MuiOutlinedInput-root": {
              borderRadius: 2,
            },
          }}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  onClick={showDealerInfo && onSendDealerInfo ? handleSendDealerInfo : handleSendMessage}
                  disabled={!message.trim() || disabled || isSending}
                  color="primary"
                >
                  {isSending ? (
                    <CircularProgress size={24} />
                  ) : (
                    <Send />
                  )}
                </IconButton>
              </InputAdornment>
            ),
          }}
        />
      </Box>
    </Box>
  );
}
