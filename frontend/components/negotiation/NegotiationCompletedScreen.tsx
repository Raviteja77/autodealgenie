/**
 * NegotiationCompletedScreen Component
 * 
 * Displays success screen when negotiation is successfully completed.
 * Shows original vs final price, savings, and financing options.
 */

import { Box, Container, Typography, Divider, Grid } from "@mui/material";
import { CheckCircle } from "@mui/icons-material";
import Link from "next/link";
import { Button, Card, Spinner } from "@/components";
import { formatPrice } from "@/lib/utils/formatting";
import { NEGOTIATION_TEXT, ROUTES } from "@/lib/constants";
import { LenderMatch } from "@/lib/api";

interface VehicleInfo {
  year: number;
  make: string;
  model: string;
  price: number;
  mileage?: number;
  vin?: string;
}

interface LatestPrice {
  price: number;
  source: string;
  round: number;
  timestamp?: string;
}

interface NegotiationCompletedScreenProps {
  vehicleData: VehicleInfo;
  latestPrice: LatestPrice;
  loadingLenders: boolean;
  lenders: LenderMatch[];
}

export function NegotiationCompletedScreen({
  vehicleData,
  latestPrice,
  loadingLenders,
  lenders,
}: NegotiationCompletedScreenProps) {
  const savings = vehicleData.price - latestPrice.price;

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Card shadow="lg">
        <Card.Body>
          <Box sx={{ textAlign: "center", py: 4 }}>
            <CheckCircle
              sx={{ fontSize: 80, color: "success.main", mb: 2 }}
            />
            <Typography variant="h4" gutterBottom>
              {NEGOTIATION_TEXT.TITLES.CONGRATULATIONS}
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              You&apos;ve successfully negotiated the deal for your{" "}
              {vehicleData.year} {vehicleData.make} {vehicleData.model}!
            </Typography>
            <Divider sx={{ my: 3 }} />
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={6}>
                <Typography variant="caption" color="text.secondary">
                  {NEGOTIATION_TEXT.LABELS.ASKING_PRICE}
                </Typography>
                <Typography variant="h6">
                  {formatPrice(vehicleData.price)}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="caption" color="text.secondary">
                  {NEGOTIATION_TEXT.LABELS.CURRENT_PRICE}
                </Typography>
                <Typography variant="h6" color="success.main">
                  {formatPrice(latestPrice.price)}
                </Typography>
              </Grid>
            </Grid>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {NEGOTIATION_TEXT.LABELS.SAVINGS}: {formatPrice(savings)}!
            </Typography>

            {/* Lender Recommendations */}
            {loadingLenders && (
              <>
                <Divider sx={{ my: 3 }} />
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center",
                    py: 2,
                  }}
                >
                  <Spinner size="md" />
                  <Typography variant="body2" sx={{ ml: 2 }}>
                    Finding best financing options...
                  </Typography>
                </Box>
              </>
            )}

            {!loadingLenders && lenders && lenders.length > 0 && (
              <>
                <Divider sx={{ my: 3 }} />
                <Typography variant="h6" gutterBottom>
                  {NEGOTIATION_TEXT.TITLES.FINANCING_OPTIONS}
                </Typography>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  paragraph
                >
                  We found {lenders.length} financing{" "}
                  {lenders.length === 1 ? "option" : "options"} for you
                </Typography>
              </>
            )}

            <Box sx={{ mt: 4 }}>
              <Link
                href={`${ROUTES.FINALIZE}?vin=${vehicleData.vin || ""}&make=${vehicleData.make}&model=${vehicleData.model}&year=${vehicleData.year}&price=${latestPrice.price}&mileage=${vehicleData.mileage || ""}`}
                style={{ textDecoration: "none" }}
              >
                <Button variant="primary" size="lg" fullWidth>
                  {NEGOTIATION_TEXT.ACTIONS.CONTINUE_TO_FINALIZE}
                </Button>
              </Link>
            </Box>
          </Box>
        </Card.Body>
      </Card>
    </Container>
  );
}
