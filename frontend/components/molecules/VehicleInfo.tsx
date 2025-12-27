import React from 'react';
import Image from 'next/image';
import { Box, Typography, Grid } from '@mui/material';
import {
  DirectionsCar,
  LocalGasStation,
  Speed,
  CalendarToday,
  LocationOn,
} from '@mui/icons-material';
import {
  VehicleDetailsProps,
  VehicleTitleProps,
  VehicleImageProps,
} from './VehicleInfo.types';

/**
 * Vehicle title display
 */
export const VehicleTitle: React.FC<VehicleTitleProps> = ({
  make,
  model,
  year,
  variant = 'h6',
}) => {
  return (
    <Typography variant={variant} gutterBottom fontWeight={600}>
      {year} {make} {model}
    </Typography>
  );
};

/**
 * Vehicle details display (mileage, fuel type, condition, location)
 */
export const VehicleDetails: React.FC<VehicleDetailsProps> = ({
  mileage,
  fuelType,
  condition,
  location,
  compact = false,
}) => {
  const gridSpacing = compact ? 0.5 : 1;
  const gridItemSize = compact ? 12 : 6;

  return (
    <Grid container spacing={gridSpacing}>
      <Grid item xs={gridItemSize}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <Speed fontSize="small" color="action" />
          <Typography variant="body2" color="text.secondary">
            {mileage.toLocaleString()} mi
          </Typography>
        </Box>
      </Grid>
      
      {fuelType && (
        <Grid item xs={gridItemSize}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <LocalGasStation fontSize="small" color="action" />
            <Typography variant="body2" color="text.secondary">
              {fuelType}
            </Typography>
          </Box>
        </Grid>
      )}
      
      {condition && (
        <Grid item xs={gridItemSize}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <CalendarToday fontSize="small" color="action" />
            <Typography variant="body2" color="text.secondary">
              {condition}
            </Typography>
          </Box>
        </Grid>
      )}
      
      {location && (
        <Grid item xs={gridItemSize}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <LocationOn fontSize="small" color="action" />
            <Typography variant="body2" color="text.secondary">
              {location}
            </Typography>
          </Box>
        </Grid>
      )}
    </Grid>
  );
};

/**
 * Vehicle image with optional badges and actions
 */
export const VehicleImage: React.FC<VehicleImageProps> = ({
  image,
  make,
  model,
  year,
  badges = [],
  actions = [],
}) => {
  return (
    <Box
      sx={{
        width: '100%',
        height: 180,
        backgroundColor: 'grey.200',
        borderRadius: 1,
        mb: 2,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {image ? (
        <Image
          fill
          src={image}
          alt={`${year} ${make} ${model}`}
          style={{ objectFit: 'cover' }}
          sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
        />
      ) : (
        <DirectionsCar sx={{ fontSize: 64, color: 'grey.400' }} />
      )}

      {/* Actions (top right) */}
      {actions.length > 0 && (
        <Box
          sx={{
            position: 'absolute',
            top: 8,
            right: 8,
            display: 'flex',
            gap: 1,
          }}
        >
          {actions}
        </Box>
      )}

      {/* Badges (bottom left and top left) */}
      {badges.length > 0 && (
        <>
          {badges.map((badge, index) => (
            <Box
              key={index}
              sx={{
                position: 'absolute',
                ...(index === 0 ? { top: 8, left: 8 } : { bottom: 8, left: 8 }),
              }}
            >
              {badge}
            </Box>
          ))}
        </>
      )}
    </Box>
  );
};
