/**
 * VehicleHeader Component
 * 
 * Displays vehicle basic information header used across evaluation,
 * negotiation, and finalize pages.
 */

import { Box, Typography, Chip, Stack } from "@mui/material";
import {
  DirectionsCar as DirectionsCarIcon,
  Speed as SpeedIcon,
  LocalGasStation as LocalGasStationIcon,
  CalendarToday as CalendarTodayIcon,
} from "@mui/icons-material";
import { formatNumber, formatPrice } from "@/lib/utils";

export interface VehicleHeaderProps {
  make: string;
  model: string;
  year: number;
  price: number;
  mileage: number;
  fuelType?: string;
  condition?: string;
  vin?: string;
  showPrice?: boolean;
  priceLabel?: string;
}

export function VehicleHeader({
  make,
  model,
  year,
  price,
  mileage,
  fuelType,
  condition,
  vin,
  showPrice = true,
  priceLabel = "Asking Price",
}: VehicleHeaderProps) {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        {year} {make} {model}
      </Typography>

      {showPrice && (
        <Typography variant="h5" color="primary" gutterBottom>
          {priceLabel}: {formatPrice(price)}
        </Typography>
      )}

      <Stack direction="row" spacing={2} flexWrap="wrap" gap={1} sx={{ mt: 2 }}>
        <Chip
          icon={<CalendarTodayIcon />}
          label={`${year}`}
          variant="outlined"
          size="medium"
        />
        <Chip
          icon={<SpeedIcon />}
          label={`${formatNumber(mileage)} miles`}
          variant="outlined"
          size="medium"
        />
        {fuelType && (
          <Chip
            icon={<LocalGasStationIcon />}
            label={fuelType}
            variant="outlined"
            size="medium"
          />
        )}
        {condition && (
          <Chip
            icon={<DirectionsCarIcon />}
            label={condition.charAt(0).toUpperCase() + condition.slice(1)}
            variant="outlined"
            size="medium"
            color={condition === "excellent" || condition === "new" ? "success" : "default"}
          />
        )}
      </Stack>

      {vin && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          VIN: {vin}
        </Typography>
      )}
    </Box>
  );
}
