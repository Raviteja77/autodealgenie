/**
 * Chat Input Component for Negotiation Page
 * 
 * Provides a text input field for sending messages during negotiation
 * with validation and proper error handling.
 */

import { useState, KeyboardEvent, ChangeEvent } from "react";
import { Box, TextField, InputAdornment, IconButton, CircularProgress, Typography, FormHelperText } from "@mui/material";
import { Send, AttachFile } from "@mui/icons-material";
import { Button } from "@/components/ui/Button";

interface ChatInputProps {
  onSendMessage: (message: string, type?: string) => Promise<void>;
  onSendDealerInfo?: (type: string, content: string, price?: number) => Promise<void>;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
}

// Configuration for different dealer info types
interface InfoTypeConfig {
  label: string;
  priceLabel?: string;
  priceRequired: boolean;
  showPrice: boolean;
  contentPlaceholder: string;
  helperText: string;
}

const INFO_TYPE_CONFIG: Record<string, InfoTypeConfig> = {
  counteroffer: {
    label: "Counter Offer",
    priceLabel: "Dealer's Counter Offer",
    priceRequired: true,
    showPrice: true,
    contentPlaceholder: "Enter details about the dealer's counter offer...",
    helperText: "Price is required for counter offers",
  },
  quote: {
    label: "Price Quote",
    priceLabel: "Quoted Price (if mentioned)",
    priceRequired: false,
    showPrice: true,
    contentPlaceholder: "Enter details about the price quote...",
    helperText: "Include the quoted price if mentioned",
  },
  inspection_report: {
    label: "Inspection Report",
    priceRequired: false,
    showPrice: false,
    contentPlaceholder: "Enter inspection report details...",
    helperText: "Provide details from the inspection report",
  },
  additional_offer: {
    label: "Additional Offer",
    priceLabel: "Offer Amount",
    priceRequired: false,
    showPrice: true,
    contentPlaceholder: "Enter details about the additional offer...",
    helperText: "Include the offer amount if applicable",
  },
  other: {
    label: "Other Information",
    priceLabel: "Price (optional)",
    priceRequired: false,
    showPrice: true,
    contentPlaceholder: "Enter other dealer information...",
    helperText: "Provide any other relevant information",
  },
};

export function ChatInput({
  onSendMessage,
  onSendDealerInfo,
  disabled = false,
  placeholder = "Type your message...",
  maxLength = 2000,
}: ChatInputProps) {
  // Default info type for dealer information
  const DEFAULT_INFO_TYPE = "counteroffer";

  const [message, setMessage] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [showDealerInfo, setShowDealerInfo] = useState(false);
  const [dealerInfoType, setDealerInfoType] = useState(DEFAULT_INFO_TYPE);
  const [dealerPrice, setDealerPrice] = useState("");
  const [validationError, setValidationError] = useState<string | null>(null);

  // Get current info type configuration
  const currentConfig = INFO_TYPE_CONFIG[dealerInfoType] || INFO_TYPE_CONFIG.other;

  const validateDealerInfo = (): boolean => {
    setValidationError(null);

    // Check if message is provided
    if (!message.trim()) {
      setValidationError("Please enter information content");
      return false;
    }

    // Check if price is required and provided
    if (currentConfig.priceRequired && !dealerPrice.trim()) {
      setValidationError(`${currentConfig.priceLabel} is required`);
      return false;
    }

    // Validate price format if provided
    if (dealerPrice.trim()) {
      const price = parseFloat(dealerPrice);
      if (isNaN(price) || price <= 0) {
        setValidationError("Please enter a valid price greater than 0");
        return false;
      }
    }

    return true;
  };

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
    if (!onSendDealerInfo || isSending || disabled) return;

    // Validate dealer info before sending
    if (!validateDealerInfo()) {
      return;
    }

    try {
      setIsSending(true);
      setValidationError(null);
      const price = dealerPrice ? parseFloat(dealerPrice) : undefined;
      await onSendDealerInfo(dealerInfoType, message.trim(), price);
      setMessage("");
      setDealerPrice("");
      setShowDealerInfo(false);
    } catch (error) {
      console.error("Failed to send dealer info:", error);
      setValidationError("Failed to send dealer info. Please try again.");
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
        <Box sx={{ mb: 2, p: 2, bgcolor: "background.paper", borderRadius: 1, border: "1px solid", borderColor: "divider" }}>
          <Typography variant="subtitle2" gutterBottom>
            Submit Dealer Information
          </Typography>
          
          {/* Info Type Dropdown */}
          <TextField
            select
            fullWidth
            size="small"
            label="Information Type"
            value={dealerInfoType}
            onChange={(e) => {
              setDealerInfoType(e.target.value);
              setValidationError(null);
            }}
            SelectProps={{ native: true }}
            sx={{ mb: 2 }}
          >
            <option value="counteroffer">Counter Offer</option>
            <option value="quote">Price Quote</option>
            <option value="inspection_report">Inspection Report</option>
            <option value="additional_offer">Additional Offer</option>
            <option value="other">Other</option>
          </TextField>

          {/* Price Field (conditional) */}
          {currentConfig.showPrice && (
            <TextField
              fullWidth
              size="small"
              type="number"
              label={currentConfig.priceLabel}
              placeholder="Enter price amount"
              value={dealerPrice}
              onChange={(e) => {
                setDealerPrice(e.target.value);
                setValidationError(null);
              }}
              required={currentConfig.priceRequired}
              error={validationError !== null && currentConfig.priceRequired && !dealerPrice.trim()}
              InputProps={{
                startAdornment: <InputAdornment position="start">$</InputAdornment>,
              }}
              sx={{ mb: 2 }}
            />
          )}

          {/* Helper Text */}
          <FormHelperText sx={{ mb: 1 }}>
            {currentConfig.helperText}
          </FormHelperText>

          {/* Content Field */}
          <TextField
            fullWidth
            multiline
            rows={3}
            placeholder={currentConfig.contentPlaceholder}
            value={message}
            onChange={handleChange}
            error={validationError !== null && !message.trim()}
            helperText={`${message.length}/${maxLength}`}
            sx={{ mb: 1 }}
          />

          {/* Validation Error */}
          {validationError && (
            <Typography variant="caption" color="error" display="block" sx={{ mb: 1 }}>
              {validationError}
            </Typography>
          )}

          {/* Action Buttons */}
          <Box sx={{ display: "flex", gap: 1, justifyContent: "flex-end" }}>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setShowDealerInfo(false);
                setDealerPrice("");
                setValidationError(null);
              }}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={handleSendDealerInfo}
              disabled={isSending || disabled}
            >
              {isSending ? "Sending..." : "Submit"}
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
            title="Submit dealer information"
          >
            <AttachFile />
          </IconButton>
        )}

        {/* Main chat input - disabled when dealer info form is open to prevent confusion */}
        <TextField
          fullWidth
          multiline
          maxRows={4}
          value={message}
          onChange={handleChange}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
          disabled={disabled || isSending || showDealerInfo}
          helperText={showDealerInfo ? "" : `${message.length}/${maxLength}`}
          sx={{
            "& .MuiOutlinedInput-root": {
              borderRadius: 2,
            },
          }}
          InputProps={{
            endAdornment: !showDealerInfo && (
              <InputAdornment position="end">
                <IconButton
                  onClick={handleSendMessage}
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
