/**
 * MarketPosition Component
 * 
 * Displays vehicle's market position relative to fair value
 */

import { Box, Typography } from "@mui/material";

interface MarketPositionProps {
  askingPrice: number;
  fairValue: number;
}

export function MarketPosition({ askingPrice, fairValue }: MarketPositionProps) {
  const priceDifference = askingPrice - fairValue;
  const percentageDiff = (Math.abs(priceDifference) / askingPrice) * 100;

  return (
    <Box
      sx={{
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        borderRadius: 2,
        p: 3,
        color: "white",
      }}
    >
      <Typography variant="subtitle2" sx={{ opacity: 0.9, mb: 1 }}>
        Market Position
      </Typography>
      <Typography variant="h3" sx={{ fontWeight: "bold", mb: 2 }}>
        {priceDifference > 0 ? "Above" : "Below"} Market
      </Typography>
      <Typography variant="h4" sx={{ fontWeight: "bold" }}>
        ${Math.abs(priceDifference).toLocaleString()}
      </Typography>
      <Typography variant="caption" sx={{ opacity: 0.8 }}>
        {percentageDiff.toFixed(1)}% difference
      </Typography>
    </Box>
  );
}
