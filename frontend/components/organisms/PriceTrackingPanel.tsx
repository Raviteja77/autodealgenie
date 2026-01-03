/**
 * PriceTrackingPanel Component
 * 
 * Displays vehicle details, price tracking, and negotiation progress
 * in the left sidebar during negotiation.
 */

import { Box, Typography, Divider, LinearProgress, Chip } from "@mui/material";
import { DirectionsCar, Speed, LocalGasStation } from "@mui/icons-material";
import { Card } from "@/components";
import { formatPrice } from "@/lib/utils/formatting";
import { NEGOTIATION_TEXT } from "@/lib/constants";

interface VehicleInfo {
  year: number;
  make: string;
  model: string;
  price: number;
  mileage: number;
  fuelType: string;
  vin?: string;
}

interface LatestPrice {
  price: number;
  source: string;
  round: number;
}

interface PriceTrackingPanelProps {
  vehicleData: VehicleInfo;
  targetPrice: number;
  latestPrice: LatestPrice | null;
  evaluationScore?: number;
  currentRound: number;
  maxRounds: number;
  priceProgress: number;
  roundProgress: number;
}

export function PriceTrackingPanel({
  vehicleData,
  targetPrice,
  latestPrice,
  evaluationScore,
  currentRound,
  maxRounds,
  priceProgress,
  roundProgress,
}: PriceTrackingPanelProps) {
  const getScoreLabel = (score: number): string => {
    if (score >= 8) return "Excellent Deal";
    if (score >= 6.5) return "Good Deal";
    return "Fair Deal";
  };

  return (
    <Card shadow="md" sx={{ position: "sticky", top: 16 }}>
      <Card.Body>
        <Typography variant="h6" gutterBottom>
          Vehicle Details
        </Typography>
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
            <DirectionsCar
              sx={{ mr: 1, color: "primary.main", fontSize: 20 }}
            />
            <Typography variant="body2" fontWeight="medium">
              {vehicleData.year} {vehicleData.make} {vehicleData.model}
            </Typography>
          </Box>
          {vehicleData.vin && (
            <Typography
              variant="caption"
              color="text.secondary"
              display="block"
              sx={{ ml: 3 }}
            >
              {NEGOTIATION_TEXT.LABELS.VIN}: {vehicleData.vin}
            </Typography>
          )}
        </Box>

        {/* Evaluation Score Indicator */}
        {evaluationScore && (
          <>
            <Divider sx={{ my: 2 }} />
            <Box
              sx={{
                p: 2,
                bgcolor: "success.50",
                borderRadius: 2,
                border: "1px solid",
                borderColor: "success.200",
              }}
            >
              <Typography
                variant="caption"
                color="text.secondary"
                display="block"
                sx={{ mb: 0.5 }}
              >
                AI Evaluation Score
              </Typography>
              <Typography variant="h5" fontWeight="bold" color="success.dark">
                {evaluationScore.toFixed(1)}/10
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {getScoreLabel(evaluationScore)}
              </Typography>
            </Box>
          </>
        )}

        <Divider sx={{ my: 2 }} />

        <Typography variant="subtitle2" gutterBottom>
          {NEGOTIATION_TEXT.LABELS.PRICE_TRACKING}
        </Typography>
        <Box sx={{ mb: 2 }}>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              mb: 1,
            }}
          >
            <Typography variant="caption" color="text.secondary">
              {NEGOTIATION_TEXT.LABELS.ASKING_PRICE}
            </Typography>
            <Typography variant="body2" fontWeight="medium">
              {formatPrice(vehicleData.price)}
            </Typography>
          </Box>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              mb: 1,
            }}
          >
            <Typography variant="caption" color="text.secondary">
              {NEGOTIATION_TEXT.LABELS.TARGET_PRICE}
            </Typography>
            <Typography variant="body2" color="primary.main">
              {formatPrice(targetPrice)}
            </Typography>
          </Box>
          {latestPrice && (
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                mb: 1,
              }}
            >
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  gap: 0.5,
                }}
              >
                <Typography variant="caption" color="text.secondary">
                  {NEGOTIATION_TEXT.LABELS.CURRENT_OFFER}
                </Typography>
                {latestPrice.source === "ai" && (
                  <Chip
                    label="AI"
                    size="small"
                    sx={{ height: 16, fontSize: "0.65rem" }}
                  />
                )}
                {latestPrice.source === "dealer" && (
                  <Chip
                    label="Dealer"
                    color="secondary"
                    size="small"
                    sx={{ height: 16, fontSize: "0.65rem" }}
                  />
                )}
                {latestPrice.source === "user" && (
                  <Chip
                    label="You"
                    color="info"
                    size="small"
                    sx={{ height: 16, fontSize: "0.65rem" }}
                  />
                )}
              </Box>
              <Typography
                variant="body2"
                color="success.main"
                fontWeight="bold"
              >
                {formatPrice(latestPrice.price)}
              </Typography>
            </Box>
          )}
        </Box>

        {/* Price Progress */}
        <Box sx={{ mb: 2 }}>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              mb: 0.5,
            }}
          >
            <Typography variant="caption">Progress</Typography>
            <Typography variant="caption">
              {Math.round(priceProgress)}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={Math.min(priceProgress, 100)}
            sx={{ height: 8, borderRadius: 1 }}
          />
        </Box>

        <Divider sx={{ my: 2 }} />

        <Typography variant="subtitle2" gutterBottom>
          {NEGOTIATION_TEXT.LABELS.NEGOTIATION_PROGRESS}
        </Typography>
        <Box sx={{ mb: 2 }}>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              mb: 0.5,
            }}
          >
            <Typography variant="caption">
              Round {currentRound} of {maxRounds}
            </Typography>
            <Typography variant="caption">
              {Math.round(roundProgress)}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={roundProgress}
            color={roundProgress > 80 ? "warning" : "primary"}
            sx={{ height: 6, borderRadius: 1 }}
          />
        </Box>

        <Divider sx={{ my: 2 }} />

        <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
          <Speed sx={{ mr: 1, color: "text.secondary", fontSize: 18 }} />
          <Typography variant="caption">
            {vehicleData.mileage.toLocaleString()} miles
          </Typography>
        </Box>
        <Box sx={{ display: "flex", alignItems: "center" }}>
          <LocalGasStation
            sx={{ mr: 1, color: "text.secondary", fontSize: 18 }}
          />
          <Typography variant="caption">{vehicleData.fuelType}</Typography>
        </Box>
      </Card.Body>
    </Card>
  );
}
