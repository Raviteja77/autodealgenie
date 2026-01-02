/**
 * MarketAnalysisCard Component
 * 
 * Displays market analysis with price comparison visualization
 * and negotiation leverage indicator.
 */

import { Box, Typography, Divider, Grid, Stack } from "@mui/material";
import { TrendingUp, CheckCircle } from "@mui/icons-material";
import { Card } from "@/components";
import { EVALUATION_TEXT } from "@/lib/constants";

interface VehicleInfo {
  price: number;
}

interface MarketAnalysisCardProps {
  vehicleData: VehicleInfo;
  fairValue: number;
}

export function MarketAnalysisCard({
  vehicleData,
  fairValue,
}: MarketAnalysisCardProps) {
  const priceDifference = vehicleData.price - fairValue;

  return (
    <Card shadow="lg" sx={{ mb: 3 }}>
      <Card.Body>
        <Typography
          variant="h6"
          gutterBottom
          sx={{ display: "flex", alignItems: "center", gap: 1 }}
        >
          <TrendingUp color="primary" />
          {EVALUATION_TEXT.TITLES.MARKET_ANALYSIS}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {EVALUATION_TEXT.DESCRIPTIONS.MARKET_ANALYSIS}
        </Typography>
        <Divider sx={{ my: 2 }} />

        <Grid container spacing={3}>
          {/* Price Comparison Visual */}
          <Grid item xs={12} md={6}>
            <Box
              sx={{
                background:
                  "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                borderRadius: 2,
                p: 3,
                color: "white",
              }}
            >
              <Typography variant="subtitle2" sx={{ opacity: 0.9, mb: 1 }}>
                {EVALUATION_TEXT.LABELS.MARKET_POSITION}
              </Typography>
              <Typography variant="h3" sx={{ fontWeight: "bold", mb: 2 }}>
                {priceDifference > 0
                  ? EVALUATION_TEXT.LABELS.ABOVE_MARKET
                  : EVALUATION_TEXT.LABELS.BELOW_MARKET}
              </Typography>
              <Typography variant="h4" sx={{ fontWeight: "bold" }}>
                ${Math.abs(priceDifference).toLocaleString()}
              </Typography>
              <Typography variant="caption" sx={{ opacity: 0.8 }}>
                {((Math.abs(priceDifference) / vehicleData.price) * 100).toFixed(
                  1
                )}
                {EVALUATION_TEXT.MESSAGES.PRICE_DIFFERENCE}
              </Typography>
            </Box>
          </Grid>

          {/* Quick Stats */}
          <Grid item xs={12} md={6}>
            <Stack spacing={2}>
              <Box sx={{ p: 2, bgcolor: "grey.50", borderRadius: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  {EVALUATION_TEXT.LABELS.DAYS_ON_MARKET}
                </Typography>
                <Typography variant="h6" fontWeight="bold">
                  32 days
                </Typography>
                <Typography variant="caption" color="success.main">
                  {EVALUATION_TEXT.MESSAGES.FASTER_THAN_AVERAGE}
                </Typography>
              </Box>
              <Box sx={{ p: 2, bgcolor: "grey.50", borderRadius: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  {EVALUATION_TEXT.LABELS.SIMILAR_VEHICLES}
                </Typography>
                <Typography variant="h6" fontWeight="bold">
                  12 {EVALUATION_TEXT.MESSAGES.IN_YOUR_AREA}
                </Typography>
                <Typography variant="caption" color="primary.main">
                  {EVALUATION_TEXT.MESSAGES.AVERAGE_PREFIX}
                  {vehicleData.price.toLocaleString()}
                </Typography>
              </Box>
            </Stack>
          </Grid>
        </Grid>

        {/* Negotiation Leverage Indicator */}
        <Box
          sx={{
            mt: 3,
            p: 3,
            bgcolor: "success.50",
            borderRadius: 2,
            border: "1px solid",
            borderColor: "success.200",
          }}
        >
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              gap: 1,
              mb: 1,
            }}
          >
            <CheckCircle color="success" />
            <Typography
              variant="subtitle1"
              fontWeight="bold"
              color="success.dark"
            >
              {EVALUATION_TEXT.LABELS.STRONG_POSITION}
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            This vehicle is priced{" "}
            {priceDifference > 0 ? "above" : "competitively with"} similar
            listings. You have good leverage to negotiate{" "}
            {priceDifference > 0 ? "down" : "for additional value"}.
          </Typography>
        </Box>
      </Card.Body>
    </Card>
  );
}
