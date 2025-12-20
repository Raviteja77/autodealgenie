'use client';

import React from 'react';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import Stack from '@mui/material/Stack';
import Chip from '@mui/material/Chip';
import CloseIcon from '@mui/icons-material/Close';
import CompareArrowsIcon from '@mui/icons-material/CompareArrows';
import { Button } from '@/components';
import { ComparisonVehicle } from '@/lib/hooks/useComparison';

interface ComparisonBarProps {
  selectedVehicles: ComparisonVehicle[];
  onRemove: (vin: string) => void;
  onCompare: () => void;
  onClear: () => void;
  maxCount: number;
  canCompare: boolean;
}

export const ComparisonBar: React.FC<ComparisonBarProps> = ({
  selectedVehicles,
  onRemove,
  onCompare,
  onClear,
  maxCount,
  canCompare,
}) => {
  if (selectedVehicles.length === 0) {
    return null;
  }

  return (
    <Paper
      elevation={8}
      sx={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        zIndex: 1200,
        borderRadius: 0,
        borderTop: 2,
        borderColor: 'primary.main',
      }}
    >
      <Box sx={{ p: 2 }}>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mb: 1,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CompareArrowsIcon color="primary" />
            <Typography variant="h6" fontWeight={600}>
              Compare Vehicles
            </Typography>
            <Chip
              label={`${selectedVehicles.length}/${maxCount}`}
              size="small"
              color="primary"
            />
          </Box>
          <Button variant="outline" size="sm" onClick={onClear}>
            Clear All
          </Button>
        </Box>

        <Stack direction="row" spacing={2} sx={{ mb: 2, flexWrap: 'wrap', gap: 1 }}>
          {selectedVehicles.map((vehicle) => (
            <Chip
              key={vehicle.vin}
              label={`${vehicle.year} ${vehicle.make} ${vehicle.model}`}
              onDelete={() => onRemove(vehicle.vin)}
              deleteIcon={<CloseIcon />}
              color="primary"
              variant="outlined"
            />
          ))}
        </Stack>

        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
          <Button
            variant="primary"
            leftIcon={<CompareArrowsIcon />}
            onClick={onCompare}
            disabled={!canCompare}
          >
            Compare {selectedVehicles.length > 0 ? `(${selectedVehicles.length})` : ''}
          </Button>
        </Box>
      </Box>
    </Paper>
  );
};
