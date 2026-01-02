/**
 * PriceBreakdown Component
 * 
 * Displays price comparison and savings breakdown.
 * Used in evaluation, negotiation, and finalize pages.
 */

import { Box, Typography, Grid, LinearProgress, Stack, Chip } from "@mui/material";
import {
  TrendingUp,
  TrendingDown,
  AttachMoney,
  CheckCircle,
} from "@mui/icons-material";
import { Card } from "@/components";
import { formatPrice, formatSavings, calculateDiscountPercent } from "@/lib/utils";

export interface PriceBreakdownProps {
  askingPrice: number;
  fairValue?: number;
  negotiatedPrice?: number;
  targetPrice?: number;
  showScore?: boolean;
  score?: number;
  showSavings?: boolean;
}

export function PriceBreakdown({
  askingPrice,
  fairValue,
  negotiatedPrice,
  targetPrice,
  showScore = false,
  score,
  showSavings = true,
}: PriceBreakdownProps) {
  const currentPrice = negotiatedPrice || askingPrice;
  const savings = showSavings ? formatSavings(askingPrice, currentPrice) : null;
  const discountPercent = calculateDiscountPercent(askingPrice, currentPrice);

  return (
    <Card>
      <Typography variant="h6" gutterBottom>
        Price Analysis
      </Typography>

      <Grid container spacing={2} sx={{ mt: 1 }}>
        {/* Asking Price */}
        <Grid item xs={12} sm={6}>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Asking Price
            </Typography>
            <Typography variant="h6">{formatPrice(askingPrice)}</Typography>
          </Box>
        </Grid>

        {/* Fair Value */}
        {fairValue && (
          <Grid item xs={12} sm={6}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Fair Market Value
              </Typography>
              <Stack direction="row" alignItems="center" spacing={1}>
                <Typography variant="h6">{formatPrice(fairValue)}</Typography>
                {fairValue < askingPrice ? (
                  <TrendingDown color="success" fontSize="small" />
                ) : (
                  <TrendingUp color="error" fontSize="small" />
                )}
              </Stack>
            </Box>
          </Grid>
        )}

        {/* Negotiated Price */}
        {negotiatedPrice && (
          <Grid item xs={12} sm={6}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Negotiated Price
              </Typography>
              <Stack direction="row" alignItems="center" spacing={1}>
                <Typography variant="h6" color="primary">
                  {formatPrice(negotiatedPrice)}
                </Typography>
                <CheckCircle color="success" fontSize="small" />
              </Stack>
            </Box>
          </Grid>
        )}

        {/* Target Price */}
        {targetPrice && (
          <Grid item xs={12} sm={6}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Your Target Price
              </Typography>
              <Typography variant="h6">{formatPrice(targetPrice)}</Typography>
            </Box>
          </Grid>
        )}

        {/* Savings */}
        {showSavings && savings && (
          <Grid item xs={12}>
            <Box
              sx={{
                p: 2,
                bgcolor: savings.color === "success" ? "success.light" : "grey.100",
                borderRadius: 1,
                mt: 1,
              }}
            >
              <Stack direction="row" alignItems="center" spacing={2}>
                <AttachMoney />
                <Box flex={1}>
                  <Typography variant="body2" color="text.secondary">
                    {savings.text}
                  </Typography>
                  <Typography variant="h6">
                    {discountPercent.toFixed(1)}% discount
                  </Typography>
                </Box>
                <Chip
                  label={savings.text}
                  color={savings.color}
                  size="small"
                />
              </Stack>
            </Box>
          </Grid>
        )}

        {/* Score */}
        {showScore && score !== undefined && (
          <Grid item xs={12}>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Deal Score
              </Typography>
              <Stack direction="row" alignItems="center" spacing={2}>
                <LinearProgress
                  variant="determinate"
                  value={score}
                  sx={{ flex: 1, height: 8, borderRadius: 1 }}
                  color={score >= 75 ? "success" : score >= 60 ? "warning" : "error"}
                />
                <Typography variant="h6" fontWeight="bold">
                  {score}/100
                </Typography>
              </Stack>
            </Box>
          </Grid>
        )}
      </Grid>
    </Card>
  );
}
