/**
 * PriceComparison Component
 * 
 * Shows side-by-side comparison of asking price vs fair market value
 */

import { Grid, Typography, Box } from "@mui/material";
import { AttachMoney, Security, TrendingUp, TrendingDown } from "@mui/icons-material";
import { Card } from "@/components";

interface PriceComparisonProps {
  askingPrice: number;
  fairValue: number;
}

export function PriceComparison({ askingPrice, fairValue }: PriceComparisonProps) {
  const priceDifference = askingPrice - fairValue;

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <Card.Body>
            <Typography
              variant="h6"
              gutterBottom
              sx={{ display: "flex", alignItems: "center" }}
            >
              <AttachMoney sx={{ mr: 1 }} />
              Asking Price
            </Typography>
            <Typography variant="h4">
              ${askingPrice.toLocaleString()}
            </Typography>
          </Card.Body>
        </Card>
      </Grid>
      <Grid item xs={12} md={6}>
        <Card>
          <Card.Body>
            <Typography
              variant="h6"
              gutterBottom
              sx={{ display: "flex", alignItems: "center" }}
            >
              <Security sx={{ mr: 1 }} />
              Fair Market Value
            </Typography>
            <Typography variant="h4">
              ${fairValue.toLocaleString()}
            </Typography>
            {priceDifference !== 0 && (
              <Box sx={{ mt: 1, display: "flex", alignItems: "center" }}>
                {priceDifference > 0 ? (
                  <>
                    <TrendingUp color="error" sx={{ mr: 0.5 }} />
                    <Typography variant="body2" color="error">
                      ${Math.abs(priceDifference).toLocaleString()} above market
                    </Typography>
                  </>
                ) : (
                  <>
                    <TrendingDown color="success" sx={{ mr: 0.5 }} />
                    <Typography variant="body2" color="success">
                      ${Math.abs(priceDifference).toLocaleString()} below market
                    </Typography>
                  </>
                )}
              </Box>
            )}
          </Card.Body>
        </Card>
      </Grid>
    </Grid>
  );
}
