'use client';

import React from 'react';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';
import ToggleButton from '@mui/material/ToggleButton';
import Tooltip from '@mui/material/Tooltip';
import ViewModuleIcon from '@mui/icons-material/ViewModule';
import ViewListIcon from '@mui/icons-material/ViewList';
import ViewCompactIcon from '@mui/icons-material/ViewComfy';
import { ViewMode } from '@/lib/hooks/useViewMode';

interface ViewModeToggleProps {
  value: ViewMode;
  onChange: (value: ViewMode) => void;
}

export const ViewModeToggle: React.FC<ViewModeToggleProps> = ({ value, onChange }) => {
  const handleChange = (_event: React.MouseEvent<HTMLElement>, newValue: ViewMode | null) => {
    if (newValue !== null) {
      onChange(newValue);
    }
  };

  return (
    <ToggleButtonGroup
      value={value}
      exclusive
      onChange={handleChange}
      size="small"
      aria-label="view mode"
    >
      <ToggleButton value="grid" aria-label="grid view">
        <Tooltip title="Grid View">
          <ViewModuleIcon />
        </Tooltip>
      </ToggleButton>
      <ToggleButton value="list" aria-label="list view">
        <Tooltip title="List View">
          <ViewListIcon />
        </Tooltip>
      </ToggleButton>
      <ToggleButton value="compact" aria-label="compact view">
        <Tooltip title="Compact View">
          <ViewCompactIcon />
        </Tooltip>
      </ToggleButton>
    </ToggleButtonGroup>
  );
};
