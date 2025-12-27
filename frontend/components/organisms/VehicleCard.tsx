"use client";

import { useState } from "react";
import Image from "next/image";
import {
  Box,
  Typography,
  Grid,
  Chip,
  IconButton,
  Divider,
  ToggleButtonGroup,
  ToggleButton,
  Tooltip,
} from "@mui/material";
import {
  DirectionsCar as DirectionsCarIcon,
  LocalGasStation as LocalGasStationIcon,
  Speed as SpeedIcon,
  CalendarToday as CalendarTodayIcon,
  LocationOn as LocationOnIcon,
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon,
  AttachMoney as AttachMoneyIcon,
  AccountBalance as AccountBalanceIcon,
} from "@mui/icons-material";
import { Card, Button } from "@/components";

export interface VehicleDisplayProps {
  vehicle: {
    vin?: string;
    make: string;
    model: string;
    year: number;
    price: number;
    mileage: number;
    fuelType?: string;
    location?: string;
    color?: string;
    condition?: string;
    image?: string;
    highlights?: string[];
    recommendation_score?: number | null;
    recommendation_summary?: string | null;
    dealer_name?: string | null;
    vdp_url?: string | null;
  };
  displayMode?: "cash" | "monthly" | "both";
  financingParams?: {
    downPayment: number;
    loanTerm: number;
    creditScore: string;
    interestRate: number;
  };
  isFavorite?: boolean;
  isInComparison?: boolean;
  budgetMax?: number;
  onViewDetails?: () => void;
  onToggleFavorite?: () => void;
  onToggleComparison?: () => void;
  onViewFinancing?: () => void;
}

export function VehicleCard({
  vehicle,
  displayMode = "both",
  financingParams,
  isFavorite = false,
  isInComparison = false,
  budgetMax,
  onViewDetails,
  onToggleFavorite,
  onToggleComparison,
  onViewFinancing,
}: VehicleDisplayProps) {
  const [localDisplayMode, setLocalDisplayMode] = useState<"cash" | "monthly">(
    displayMode === "both" ? "cash" : displayMode
  );

  // Calculate monthly payment if financing params are provided
  const calculateMonthlyPayment = () => {
    if (!financingParams) return null;

    const { downPayment, loanTerm, interestRate } = financingParams;
    const principal = vehicle.price - downPayment;
    const monthlyRate = interestRate / 12;

    if (monthlyRate === 0 || loanTerm === 0) {
      return principal / loanTerm || 0;
    }

    const denominator = Math.pow(1 + monthlyRate, loanTerm) - 1;
    if (denominator === 0) {
      return principal / loanTerm || 0;
    }

    const payment =
      (principal * monthlyRate * Math.pow(1 + monthlyRate, loanTerm)) /
      denominator;

    return Math.round(payment);
  };

  const monthlyPayment = calculateMonthlyPayment();
  const totalCost = monthlyPayment
    ? monthlyPayment * (financingParams?.loanTerm || 0) +
      (financingParams?.downPayment || 0)
    : null;

  // Check affordability
  const isAffordable = budgetMax ? vehicle.price <= budgetMax : true;
  // const monthlyAffordable =
  //   budgetMax && monthlyPayment ? monthlyPayment <= budgetMax : true;

  return (
    <Card
      hover
      shadow="md"
      sx={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        border: !isAffordable ? "2px solid" : undefined,
        borderColor: !isAffordable ? "warning.main" : undefined,
      }}
    >
      <Card.Body sx={{ flexGrow: 1, display: "flex", flexDirection: "column" }}>
        {/* Image placeholder */}
        <Box
          sx={{
            width: "100%",
            height: 180,
            backgroundColor: "grey.200",
            borderRadius: 1,
            mb: 2,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            position: "relative",
            overflow: "hidden",
          }}
        >
          {vehicle.image ? (
            <Image
              fill
              src={vehicle.image}
              alt={`${vehicle.year} ${vehicle.make} ${vehicle.model}`}
              style={{ objectFit: "cover" }}
              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
            />
          ) : (
            <DirectionsCarIcon sx={{ fontSize: 64, color: "grey.400" }} />
          )}

          {/* Favorite and Comparison icons */}
          <Box
            sx={{
              position: "absolute",
              top: 8,
              right: 8,
              display: "flex",
              gap: 1,
            }}
          >
            <IconButton
              size="small"
              onClick={onToggleFavorite}
              sx={{
                backgroundColor: "white",
                "&:hover": { backgroundColor: "grey.100" },
              }}
            >
              {isFavorite ? (
                <FavoriteIcon color="error" />
              ) : (
                <FavoriteBorderIcon />
              )}
            </IconButton>
          </Box>

          {/* Affordability indicator */}
          {budgetMax && (
            <Chip
              label={
                isAffordable
                  ? "Within Budget"
                  : `$${(vehicle.price - budgetMax).toLocaleString()} over`
              }
              color={isAffordable ? "success" : "warning"}
              size="small"
              sx={{
                position: "absolute",
                bottom: 8,
                left: 8,
                fontWeight: 600,
              }}
            />
          )}

          {/* Recommendation Score */}
          {vehicle.recommendation_score !== null &&
            vehicle.recommendation_score !== undefined && (
              <Chip
                label={`${Math.round(vehicle.recommendation_score * 100)}% Match`}
                color="primary"
                size="small"
                sx={{
                  position: "absolute",
                  top: 8,
                  left: 8,
                  fontWeight: 600,
                }}
              />
            )}
        </Box>

        {/* Vehicle Title */}
        <Typography variant="h6" gutterBottom fontWeight={600}>
          {vehicle.year} {vehicle.make} {vehicle.model}
        </Typography>

        {/* Price Display Toggle */}
        {displayMode === "both" && financingParams && (
          <Box sx={{ mb: 2, display: "flex", justifyContent: "center" }}>
            <ToggleButtonGroup
              value={localDisplayMode}
              exclusive
              onChange={(_, value) => value && setLocalDisplayMode(value)}
              size="small"
            >
              <ToggleButton value="cash">
                <AttachMoneyIcon fontSize="small" sx={{ mr: 0.5 }} />
                Cash
              </ToggleButton>
              <ToggleButton value="monthly">
                <AccountBalanceIcon fontSize="small" sx={{ mr: 0.5 }} />
                Monthly
              </ToggleButton>
            </ToggleButtonGroup>
          </Box>
        )}

        {/* Price Display */}
        {localDisplayMode === "cash" || !financingParams ? (
          <Box>
            <Typography
              variant="h4"
              color="primary"
              gutterBottom
              fontWeight={700}
            >
              ${vehicle.price.toLocaleString()}
            </Typography>
            {monthlyPayment && displayMode === "both" && (
              <Typography variant="body2" color="text.secondary">
                or ${monthlyPayment.toLocaleString()}/month
              </Typography>
            )}
          </Box>
        ) : (
          <Box>
            <Box sx={{ display: "flex", alignItems: "baseline", gap: 1 }}>
              <Typography
                variant="h4"
                color="primary"
                gutterBottom
                fontWeight={700}
              >
                ${monthlyPayment?.toLocaleString()}
              </Typography>
              <Typography variant="body1" color="text.secondary">
                /month
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              Cash price: ${vehicle.price.toLocaleString()}
            </Typography>
            {totalCost && (
              <Typography variant="caption" color="text.secondary">
                Total cost: ${totalCost.toLocaleString()} over{" "}
                {financingParams?.loanTerm} months
              </Typography>
            )}
          </Box>
        )}

        {/* Recommendation Summary */}
        {vehicle.recommendation_summary && (
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ mt: 1, mb: 2, fontStyle: "italic" }}
          >
            {vehicle.recommendation_summary}
          </Typography>
        )}

        <Divider sx={{ my: 2 }} />

        {/* Details */}
        <Grid container spacing={1} sx={{ mb: 2 }}>
          <Grid item xs={6}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
              <SpeedIcon fontSize="small" color="action" />
              <Typography variant="body2" color="text.secondary">
                {vehicle.mileage.toLocaleString()} mi
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
              <LocalGasStationIcon fontSize="small" color="action" />
              <Typography variant="body2" color="text.secondary">
                {vehicle.fuelType || "N/A"}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
              <CalendarTodayIcon fontSize="small" color="action" />
              <Typography variant="body2" color="text.secondary">
                {vehicle.condition || "Used"}
              </Typography>
            </Box>
          </Grid>
          {vehicle.location && (
            <Grid item xs={6}>
              <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                <LocationOnIcon fontSize="small" color="action" />
                <Typography variant="body2" color="text.secondary">
                  {vehicle.location}
                </Typography>
              </Box>
            </Grid>
          )}
        </Grid>

        {/* Action Buttons */}
        <Box
          sx={{
            mt: "auto",
            display: "flex",
            flexDirection: "column",
            gap: 1,
          }}
        >
          {financingParams && (
            <Button
              variant="outline"
              size="sm"
              leftIcon={<AccountBalanceIcon />}
              onClick={onViewFinancing}
              fullWidth
            >
              View Financing Options
            </Button>
          )}
          <Box sx={{ display: "flex", gap: 1 }}>
            <Button
              variant="primary"
              size="sm"
              onClick={onViewDetails}
              fullWidth
            >
              View Details
            </Button>
            {onToggleComparison && (
              <Tooltip title={isInComparison ? "Remove from comparison" : "Add to comparison"}>
                <Button
                  variant={isInComparison ? "secondary" : "outline"}
                  size="sm"
                  onClick={onToggleComparison}
                >
                  {isInComparison ? "✓" : "+"}
                </Button>
              </Tooltip>
            )}
          </Box>
        </Box>
      </Card.Body>
    </Card>
  );
}
