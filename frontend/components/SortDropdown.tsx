'use client';

import React from 'react';
import FormControl from '@mui/material/FormControl';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import SortIcon from '@mui/icons-material/Sort';

export type SortOption =
  | 'price_low'
  | 'price_high'
  | 'mileage_low'
  | 'year_new'
  | 'score_high'
  | 'recently_added';

interface SortDropdownProps {
  value: SortOption;
  onChange: (value: SortOption) => void;
}

const SORT_OPTIONS: Array<{ value: SortOption; label: string }> = [
  { value: 'price_low', label: 'Price: Low to High' },
  { value: 'price_high', label: 'Price: High to Low' },
  { value: 'mileage_low', label: 'Mileage: Low to High' },
  { value: 'year_new', label: 'Year: Newest First' },
  { value: 'score_high', label: 'Recommendation Score' },
  { value: 'recently_added', label: 'Recently Added' },
];

export const SortDropdown: React.FC<SortDropdownProps> = ({ value, onChange }) => {
  const handleChange = (event: SelectChangeEvent<SortOption>) => {
    onChange(event.target.value as SortOption);
  };

  return (
    <FormControl size="small" sx={{ minWidth: 200 }}>
      <Select
        value={value}
        onChange={handleChange}
        displayEmpty
        startAdornment={
          <Box sx={{ display: 'flex', alignItems: 'center', mr: 1 }}>
            <SortIcon fontSize="small" />
          </Box>
        }
      >
        {SORT_OPTIONS.map((option) => (
          <MenuItem key={option.value} value={option.value}>
            <Typography variant="body2">{option.label}</Typography>
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};
