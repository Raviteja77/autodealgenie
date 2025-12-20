'use client';

import React from 'react';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import Slider from '@mui/material/Slider';
import FormControl from '@mui/material/FormControl';
import FormLabel from '@mui/material/FormLabel';
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import Chip from '@mui/material/Chip';
import Stack from '@mui/material/Stack';
import IconButton from '@mui/material/IconButton';
import CloseIcon from '@mui/icons-material/Close';
import { Button } from '@/components';
import { useFilters, FilterState } from '@/lib/hooks/useFilters';

interface FilterPanelProps {
  isOpen: boolean;
  onClose: () => void;
  vehicleCount?: number;
}

const FUEL_TYPES = ['Gasoline', 'Diesel', 'Electric', 'Hybrid', 'Plug-in Hybrid'];
const TRANSMISSIONS = ['Automatic', 'Manual', 'CVT'];
const CONDITIONS = ['New', 'Used', 'Certified Pre-Owned'];
const COMMON_FEATURES = [
  'Sunroof',
  'Leather Seats',
  'Navigation',
  'Backup Camera',
  'Bluetooth',
  'Apple CarPlay',
  'Android Auto',
  'Heated Seats',
  'Remote Start',
  'Parking Sensors',
];

export const FilterPanel: React.FC<FilterPanelProps> = ({
  isOpen,
  onClose,
  vehicleCount = 0,
}) => {
  const {
    filters,
    updateFilter,
    resetFilters,
    applyFilters,
    activeFilterCount,
  } = useFilters();

  const handlePriceChange = (_event: Event, newValue: number | number[]) => {
    const [min, max] = newValue as number[];
    updateFilter('priceMin', min);
    updateFilter('priceMax', max);
  };

  const handleMileageChange = (_event: Event, newValue: number | number[]) => {
    const [min, max] = newValue as number[];
    updateFilter('mileageMin', min);
    updateFilter('mileageMax', max);
  };

  const handleYearChange = (_event: Event, newValue: number | number[]) => {
    const [min, max] = newValue as number[];
    updateFilter('yearMin', min);
    updateFilter('yearMax', max);
  };

  const handleFuelTypeToggle = (fuelType: string) => {
    const currentTypes = filters.fuelTypes || [];
    const newTypes = currentTypes.includes(fuelType)
      ? currentTypes.filter((t) => t !== fuelType)
      : [...currentTypes, fuelType];
    updateFilter('fuelTypes', newTypes);
  };

  const handleConditionToggle = (condition: string) => {
    const currentConditions = filters.conditions || [];
    const newConditions = currentConditions.includes(condition)
      ? currentConditions.filter((c) => c !== condition)
      : [...currentConditions, condition];
    updateFilter('conditions', newConditions);
  };

  const handleFeatureToggle = (feature: string) => {
    const currentFeatures = filters.features || [];
    const newFeatures = currentFeatures.includes(feature)
      ? currentFeatures.filter((f) => f !== feature)
      : [...currentFeatures, feature];
    updateFilter('features', newFeatures);
  };

  const handleApply = () => {
    applyFilters();
    onClose();
  };

  const handleReset = () => {
    resetFilters();
  };

  return (
    <Drawer anchor="left" open={isOpen} onClose={onClose}>
      <Box sx={{ width: 350, height: '100%', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Box
          sx={{
            p: 2,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            borderBottom: 1,
            borderColor: 'divider',
          }}
        >
          <Typography variant="h6" fontWeight={600}>
            Filter Results
            {activeFilterCount > 0 && (
              <Chip
                label={activeFilterCount}
                size="small"
                color="primary"
                sx={{ ml: 1 }}
              />
            )}
          </Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>

        {/* Filters */}
        <Box sx={{ flexGrow: 1, overflowY: 'auto', p: 2 }}>
          {/* Price Range */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" fontWeight={600} gutterBottom>
              Price Range
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              ${(filters.priceMin || 5000).toLocaleString()} - $
              {(filters.priceMax || 100000).toLocaleString()}
            </Typography>
            <Slider
              value={[filters.priceMin || 5000, filters.priceMax || 100000]}
              onChange={handlePriceChange}
              valueLabelDisplay="auto"
              min={5000}
              max={100000}
              step={1000}
              valueLabelFormat={(value) => `$${value.toLocaleString()}`}
            />
          </Box>

          <Divider sx={{ my: 2 }} />

          {/* Mileage Range */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" fontWeight={600} gutterBottom>
              Mileage Range
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              {(filters.mileageMin || 0).toLocaleString()} -{' '}
              {(filters.mileageMax || 200000).toLocaleString()} miles
            </Typography>
            <Slider
              value={[filters.mileageMin || 0, filters.mileageMax || 200000]}
              onChange={handleMileageChange}
              valueLabelDisplay="auto"
              min={0}
              max={200000}
              step={5000}
              valueLabelFormat={(value) => `${value.toLocaleString()} mi`}
            />
          </Box>

          <Divider sx={{ my: 2 }} />

          {/* Year Range */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" fontWeight={600} gutterBottom>
              Year Range
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              {filters.yearMin || 2000} - {filters.yearMax || 2024}
            </Typography>
            <Slider
              value={[filters.yearMin || 2000, filters.yearMax || 2024]}
              onChange={handleYearChange}
              valueLabelDisplay="auto"
              min={2000}
              max={2024}
              step={1}
            />
          </Box>

          <Divider sx={{ my: 2 }} />

          {/* Fuel Type */}
          <Box sx={{ mb: 3 }}>
            <FormControl component="fieldset">
              <FormLabel component="legend">
                <Typography variant="subtitle2" fontWeight={600}>
                  Fuel Type
                </Typography>
              </FormLabel>
              <FormGroup>
                {FUEL_TYPES.map((fuelType) => (
                  <FormControlLabel
                    key={fuelType}
                    control={
                      <Checkbox
                        checked={filters.fuelTypes.includes(fuelType)}
                        onChange={() => handleFuelTypeToggle(fuelType)}
                      />
                    }
                    label={fuelType}
                  />
                ))}
              </FormGroup>
            </FormControl>
          </Box>

          <Divider sx={{ my: 2 }} />

          {/* Transmission */}
          <Box sx={{ mb: 3 }}>
            <FormControl component="fieldset">
              <FormLabel component="legend">
                <Typography variant="subtitle2" fontWeight={600}>
                  Transmission
                </Typography>
              </FormLabel>
              <RadioGroup
                value={filters.transmission || ''}
                onChange={(e) => updateFilter('transmission', e.target.value || undefined)}
              >
                <FormControlLabel value="" control={<Radio />} label="Any" />
                {TRANSMISSIONS.map((transmission) => (
                  <FormControlLabel
                    key={transmission}
                    value={transmission}
                    control={<Radio />}
                    label={transmission}
                  />
                ))}
              </RadioGroup>
            </FormControl>
          </Box>

          <Divider sx={{ my: 2 }} />

          {/* Condition */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" fontWeight={600} gutterBottom>
              Condition
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ gap: 1 }}>
              {CONDITIONS.map((condition) => (
                <Chip
                  key={condition}
                  label={condition}
                  onClick={() => handleConditionToggle(condition)}
                  color={filters.conditions.includes(condition) ? 'primary' : 'default'}
                  variant={filters.conditions.includes(condition) ? 'filled' : 'outlined'}
                />
              ))}
            </Stack>
          </Box>

          <Divider sx={{ my: 2 }} />

          {/* Features */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" fontWeight={600} gutterBottom>
              Features
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ gap: 1 }}>
              {COMMON_FEATURES.map((feature) => (
                <Chip
                  key={feature}
                  label={feature}
                  onClick={() => handleFeatureToggle(feature)}
                  color={filters.features.includes(feature) ? 'primary' : 'default'}
                  variant={filters.features.includes(feature) ? 'filled' : 'outlined'}
                  size="small"
                />
              ))}
            </Stack>
          </Box>
        </Box>

        {/* Footer */}
        <Box
          sx={{
            p: 2,
            borderTop: 1,
            borderColor: 'divider',
            display: 'flex',
            gap: 1,
          }}
        >
          <Button variant="outline" fullWidth onClick={handleReset}>
            Reset
          </Button>
          <Button variant="primary" fullWidth onClick={handleApply}>
            Apply ({vehicleCount})
          </Button>
        </Box>
      </Box>
    </Drawer>
  );
};
