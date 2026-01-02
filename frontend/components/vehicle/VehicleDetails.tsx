/**
 * VehicleDetails Component
 * 
 * Displays detailed vehicle information in a card format.
 * Reusable across evaluation, negotiation, and finalize pages.
 */

import { Box, Typography, Grid, Divider } from "@mui/material";
import { Card } from "@/components";
import { formatNumber, formatPrice } from "@/lib/utils";

export interface VehicleDetailsProps {
  make: string;
  model: string;
  year: number;
  price: number;
  mileage: number;
  fuelType?: string;
  condition?: string;
  vin?: string;
  zipCode?: string;
  color?: string;
  transmission?: string;
  drivetrain?: string;
  bodyType?: string;
}

export function VehicleDetails({
  make,
  model,
  year,
  price,
  mileage,
  fuelType,
  condition,
  vin,
  zipCode,
  color,
  transmission,
  drivetrain,
  bodyType,
}: VehicleDetailsProps) {
  const details = [
    { label: "Make", value: make },
    { label: "Model", value: model },
    { label: "Year", value: year.toString() },
    { label: "Price", value: formatPrice(price) },
    { label: "Mileage", value: `${formatNumber(mileage)} miles` },
    { label: "Fuel Type", value: fuelType },
    { label: "Condition", value: condition },
    { label: "Color", value: color },
    { label: "Transmission", value: transmission },
    { label: "Drivetrain", value: drivetrain },
    { label: "Body Type", value: bodyType },
    { label: "VIN", value: vin },
    { label: "Zip Code", value: zipCode },
  ].filter((detail) => detail.value); // Only show fields with values

  return (
    <Card>
      <Typography variant="h6" gutterBottom>
        Vehicle Details
      </Typography>
      <Divider sx={{ mb: 2 }} />
      <Grid container spacing={2}>
        {details.map((detail, index) => (
          <Grid item xs={12} sm={6} key={index}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                {detail.label}
              </Typography>
              <Typography variant="body1" fontWeight="medium">
                {detail.value}
              </Typography>
            </Box>
          </Grid>
        ))}
      </Grid>
    </Card>
  );
}
