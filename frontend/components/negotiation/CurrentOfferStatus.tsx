/**
 * CurrentOfferStatus Component
 * 
 * Displays a prominent card showing the current offer status in the negotiation,
 * including the last offer amount, source, timestamp, status, comparison to target,
 * and a timeline of recent offers.
 */

"use client";

import {
  Box,
  Typography,
  Chip,
  Paper,
  Stack,
  Divider,
  LinearProgress,
} from "@mui/material";
import {
  TrendingUp,
  TrendingDown,
  AccessTime,
  CheckCircle,
  HourglassEmpty,
  Cancel,
  AttachMoney,
} from "@mui/icons-material";
import { Card } from "@/components/ui/Card";
import type { CurrentOfferStatus as CurrentOfferStatusType } from "@/lib/hooks/useNegotiationState";

interface CurrentOfferStatusProps {
  offerStatus: CurrentOfferStatusType;
  vehiclePrice: number;
}

export function CurrentOfferStatus({
  offerStatus,
  vehiclePrice,
}: CurrentOfferStatusProps) {
  const { lastOffer, status, comparisonToTarget, offerHistory } = offerStatus;

  // Status configuration
  const statusConfig = {
    waiting_for_response: {
      label: "Waiting for Response",
      color: "warning" as const,
      icon: <HourglassEmpty />,
      bgColor: "warning.light",
      textColor: "warning.dark",
    },
    user_turn: {
      label: "Your Turn",
      color: "info" as const,
      icon: <AccessTime />,
      bgColor: "info.light",
      textColor: "info.dark",
    },
    completed: {
      label: "Deal Completed",
      color: "success" as const,
      icon: <CheckCircle />,
      bgColor: "success.light",
      textColor: "success.dark",
    },
    cancelled: {
      label: "Cancelled",
      color: "error" as const,
      icon: <Cancel />,
      bgColor: "error.light",
      textColor: "error.dark",
    },
  };

  const currentStatus = statusConfig[status];

  // Source label mapping
  const sourceLabels = {
    user: "You",
    dealer: "Dealer",
    ai: "AI Assistant",
  };

  if (!lastOffer) {
    return (
      <Card shadow="md">
        <Card.Body>
          <Typography variant="h6" gutterBottom>
            Current Offer Status
          </Typography>
          <Typography variant="body2" color="text.secondary">
            No offers yet. Start negotiating to see offer details here.
          </Typography>
        </Card.Body>
      </Card>
    );
  }

  return (
    <Card shadow="md">
      <Card.Body>
        <Box sx={{ mb: 2 }}>
          <Typography variant="h6" gutterBottom>
            Current Offer Status
          </Typography>
          <Chip
            label={currentStatus.label}
            color={currentStatus.color}
            icon={currentStatus.icon}
            size="small"
          />
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* Last Offer Details */}
        <Box sx={{ mb: 3 }}>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 1,
            }}
          >
            <Typography variant="caption" color="text.secondary">
              Last Offer
            </Typography>
            <Chip
              label={sourceLabels[lastOffer.source]}
              size="small"
              variant="outlined"
            />
          </Box>
          <Box
            sx={{
              display: "flex",
              alignItems: "baseline",
              gap: 1,
              mb: 0.5,
            }}
          >
            <AttachMoney sx={{ color: "primary.main", fontSize: 28 }} />
            <Typography variant="h4" color="primary.main" fontWeight="bold">
              {lastOffer.price.toLocaleString()}
            </Typography>
          </Box>
          <Typography variant="caption" color="text.secondary">
            Round {lastOffer.roundNumber} •{" "}
            {new Date(lastOffer.timestamp).toLocaleString([], {
              month: "short",
              day: "numeric",
              hour: "2-digit",
              minute: "2-digit",
            })}
          </Typography>
        </Box>

        {/* Comparison to Target */}
        {comparisonToTarget && (
          <>
            <Divider sx={{ my: 2 }} />
            <Box sx={{ mb: 3 }}>
              <Typography variant="caption" color="text.secondary" gutterBottom>
                Comparison to Your Target
              </Typography>
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  gap: 1,
                  mt: 1,
                }}
              >
                {comparisonToTarget.isAboveTarget ? (
                  <TrendingUp sx={{ color: "error.main" }} />
                ) : (
                  <TrendingDown sx={{ color: "success.main" }} />
                )}
                <Typography
                  variant="body2"
                  color={
                    comparisonToTarget.isAboveTarget
                      ? "error.main"
                      : "success.main"
                  }
                  fontWeight="medium"
                >
                  ${Math.abs(comparisonToTarget.amount).toLocaleString()}{" "}
                  {comparisonToTarget.isAboveTarget ? "above" : "below"} target
                </Typography>
              </Box>
              <Box sx={{ mt: 1 }}>
                <LinearProgress
                  variant="determinate"
                  value={Math.max(
                    0,
                    Math.min(
                      100,
                      comparisonToTarget.isAboveTarget
                        ? 100
                        : 100 - Math.abs(comparisonToTarget.percentage)
                    )
                  )}
                  color={
                    comparisonToTarget.isAboveTarget ? "error" : "success"
                  }
                  sx={{ height: 6, borderRadius: 1 }}
                />
              </Box>
            </Box>
          </>
        )}

        {/* Offer Timeline */}
        {offerHistory.length > 1 && (
          <>
            <Divider sx={{ my: 2 }} />
            <Box>
              <Typography
                variant="caption"
                color="text.secondary"
                gutterBottom
                display="block"
              >
                Recent Offers
              </Typography>
              <Stack spacing={1} sx={{ mt: 1 }}>
                {[...offerHistory].reverse().map((offer, index) => (
                  <Paper
                      key={offer.messageId}
                      elevation={0}
                      sx={{
                        p: 1.5,
                        bgcolor:
                          index === 0 ? "primary.light" : "background.default",
                        border: 1,
                        borderColor: index === 0 ? "primary.main" : "divider",
                      }}
                    >
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                        }}
                      >
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            ${offer.price.toLocaleString()}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {sourceLabels[offer.source]} • Round{" "}
                            {offer.roundNumber}
                          </Typography>
                        </Box>
                        <Box sx={{ textAlign: "right" }}>
                          <Typography variant="caption" color="text.secondary">
                            {new Date(offer.timestamp).toLocaleTimeString([], {
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </Typography>
                          {index === 0 && (
                            <Chip
                              label="Latest"
                              size="small"
                              color="primary"
                              sx={{ ml: 1, height: 20, fontSize: "0.65rem" }}
                            />
                          )}
                        </Box>
                      </Box>
                    </Paper>
                  ))}
              </Stack>
            </Box>
          </>
        )}

        {/* Savings Indicator */}
        {lastOffer.price < vehiclePrice && (
          <>
            <Divider sx={{ my: 2 }} />
            <Box
              sx={{
                p: 1.5,
                bgcolor: "success.light",
                borderRadius: 1,
              }}
            >
              <Typography
                variant="body2"
                color="success.dark"
                fontWeight="medium"
                sx={{ display: "flex", alignItems: "center", gap: 1 }}
              >
                <CheckCircle fontSize="small" />
                Potential Savings: $
                {(vehiclePrice - lastOffer.price).toLocaleString()}
              </Typography>
            </Box>
          </>
        )}
      </Card.Body>
    </Card>
  );
}
