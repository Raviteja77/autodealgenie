/**
 * NegotiationCancelledScreen Component
 * 
 * Displays screen when negotiation is cancelled/rejected.
 * Provides option to return to results page.
 */

import { Box, Container, Typography } from "@mui/material";
import { Cancel } from "@mui/icons-material";
import Link from "next/link";
import { Button, Card } from "@/components";
import { NEGOTIATION_TEXT, ROUTES } from "@/lib/constants";

interface VehicleInfo {
  year: number;
  make: string;
  model: string;
}

interface NegotiationCancelledScreenProps {
  vehicleData: VehicleInfo;
}

export function NegotiationCancelledScreen({
  vehicleData,
}: NegotiationCancelledScreenProps) {
  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Card shadow="lg">
        <Card.Body>
          <Box sx={{ textAlign: "center", py: 4 }}>
            <Cancel sx={{ fontSize: 80, color: "error.main", mb: 2 }} />
            <Typography variant="h4" gutterBottom>
              {NEGOTIATION_TEXT.TITLES.NEGOTIATION}
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              You&apos;ve cancelled the negotiation for the {vehicleData.year}{" "}
              {vehicleData.make} {vehicleData.model}. No worries! You can always
              start a new one or search for other vehicles.
            </Typography>
            <Box sx={{ mt: 4 }}>
              <Link href={ROUTES.RESULTS} style={{ textDecoration: "none" }}>
                <Button variant="primary" size="lg">
                  Back to Results
                </Button>
              </Link>
            </Box>
          </Box>
        </Card.Body>
      </Card>
    </Container>
  );
}
