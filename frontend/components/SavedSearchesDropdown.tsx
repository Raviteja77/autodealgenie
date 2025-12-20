'use client';

import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import Badge from '@mui/material/Badge';
import Divider from '@mui/material/Divider';
import ListItemText from '@mui/material/ListItemText';
import ListItemSecondaryAction from '@mui/material/ListItemSecondaryAction';
import BookmarkIcon from '@mui/icons-material/Bookmark';
import DeleteIcon from '@mui/icons-material/Delete';
import Chip from '@mui/material/Chip';
import { Button } from '@/components';
import { SavedSearch } from '@/lib/api';
import { useRouter } from 'next/navigation';

interface SavedSearchesDropdownProps {
  searches: SavedSearch[];
  totalNewMatches: number;
  onDelete: (searchId: number) => void;
}

export const SavedSearchesDropdown: React.FC<SavedSearchesDropdownProps> = ({
  searches,
  totalNewMatches,
  onDelete,
}) => {
  const router = useRouter();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const isOpen = Boolean(anchorEl);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleSearchClick = (search: SavedSearch) => {
    // Build URL with saved search criteria
    const params = new URLSearchParams();
    
    if (search.make) params.set('make', search.make);
    if (search.model) params.set('model', search.model);
    if (search.budget_min) params.set('budgetMin', search.budget_min.toString());
    if (search.budget_max) params.set('budgetMax', search.budget_max.toString());
    if (search.car_type) params.set('carType', search.car_type);
    if (search.year_min) params.set('yearMin', search.year_min.toString());
    if (search.year_max) params.set('yearMax', search.year_max.toString());
    if (search.mileage_max) params.set('mileageMax', search.mileage_max.toString());
    if (search.fuel_type) params.set('fuelType', search.fuel_type);
    if (search.transmission) params.set('transmission', search.transmission);
    if (search.user_priorities) params.set('userPriorities', search.user_priorities);

    router.push(`/dashboard/results?${params.toString()}`);
    handleClose();
  };

  const handleDelete = (searchId: number, event: React.MouseEvent) => {
    event.stopPropagation();
    onDelete(searchId);
  };

  return (
    <>
      <IconButton onClick={handleClick} color="inherit">
        <Badge badgeContent={totalNewMatches} color="error">
          <BookmarkIcon />
        </Badge>
      </IconButton>

      <Menu
        anchorEl={anchorEl}
        open={isOpen}
        onClose={handleClose}
        PaperProps={{
          sx: { width: 350, maxHeight: 400 },
        }}
      >
        <Box sx={{ p: 2, pb: 1 }}>
          <Typography variant="h6" fontWeight={600}>
            Saved Searches
          </Typography>
        </Box>

        <Divider />

        {searches.length === 0 ? (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              No saved searches yet
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Save your current search to quickly access it later
            </Typography>
          </Box>
        ) : (
          <>
            {searches.map((search) => (
              <MenuItem
                key={search.id}
                onClick={() => handleSearchClick(search)}
                sx={{ py: 2 }}
              >
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body2" fontWeight={600}>
                        {search.name}
                      </Typography>
                      {search.new_matches_count > 0 && (
                        <Chip
                          label={`${search.new_matches_count} new`}
                          size="small"
                          color="error"
                        />
                      )}
                    </Box>
                  }
                  secondary={
                    <Typography variant="caption" color="text.secondary">
                      {[
                        search.make && `Make: ${search.make}`,
                        search.model && `Model: ${search.model}`,
                        search.budget_max &&
                          `Budget: $${search.budget_max.toLocaleString()}`,
                      ]
                        .filter(Boolean)
                        .join(' • ')}
                    </Typography>
                  }
                />
                <ListItemSecondaryAction>
                  <IconButton
                    edge="end"
                    size="small"
                    onClick={(e) => handleDelete(search.id, e)}
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </ListItemSecondaryAction>
              </MenuItem>
            ))}
          </>
        )}
      </Menu>
    </>
  );
};
