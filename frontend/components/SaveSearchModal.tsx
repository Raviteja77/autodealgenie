'use client';

import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import FormControlLabel from '@mui/material/FormControlLabel';
import Switch from '@mui/material/Switch';
import Alert from '@mui/material/Alert';
import { Modal, Input, Button } from '@/components';
import { SavedSearchCreate } from '@/lib/api';

interface SaveSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (search: SavedSearchCreate) => Promise<void>;
  currentSearchCriteria: Partial<SavedSearchCreate>;
}

export const SaveSearchModal: React.FC<SaveSearchModalProps> = ({
  isOpen,
  onClose,
  onSave,
  currentSearchCriteria,
}) => {
  const [name, setName] = useState('');
  const [notificationEnabled, setNotificationEnabled] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSave = async () => {
    if (!name.trim()) {
      setError('Please enter a name for this search');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await onSave({
        name: name.trim(),
        ...currentSearchCriteria,
        notification_enabled: notificationEnabled,
      });
      
      // Reset form
      setName('');
      setNotificationEnabled(true);
      onClose();
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to save search';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    setName('');
    setNotificationEnabled(true);
    setError(null);
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Save This Search" size="md">
      <Box sx={{ p: 3 }}>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Save your current search criteria to quickly access similar results in the future
          and get notified when new matches are found.
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Input
          label="Search Name"
          placeholder="e.g., Affordable Toyota Camry"
          value={name}
          onChange={(e) => setName(e.target.value)}
          fullWidth
          required
          disabled={isLoading}
        />

        <Box sx={{ mt: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={notificationEnabled}
                onChange={(e) => setNotificationEnabled(e.target.checked)}
                disabled={isLoading}
              />
            }
            label="Notify me when new matches are found"
          />
        </Box>

        {/* Display current search criteria */}
        <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
          <Typography variant="caption" color="text.secondary" fontWeight={600}>
            Current Search Criteria:
          </Typography>
          <Box sx={{ mt: 1 }}>
            {currentSearchCriteria.make && (
              <Typography variant="caption" display="block">
                Make: {currentSearchCriteria.make}
              </Typography>
            )}
            {currentSearchCriteria.model && (
              <Typography variant="caption" display="block">
                Model: {currentSearchCriteria.model}
              </Typography>
            )}
            {(currentSearchCriteria.budget_min || currentSearchCriteria.budget_max) && (
              <Typography variant="caption" display="block">
                Budget: ${currentSearchCriteria.budget_min?.toLocaleString() || '0'} - $
                {currentSearchCriteria.budget_max?.toLocaleString() || '∞'}
              </Typography>
            )}
            {(currentSearchCriteria.year_min || currentSearchCriteria.year_max) && (
              <Typography variant="caption" display="block">
                Year: {currentSearchCriteria.year_min || '2000'} -{' '}
                {currentSearchCriteria.year_max || '2024'}
              </Typography>
            )}
          </Box>
        </Box>

        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 3 }}>
          <Button variant="outline" onClick={handleClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleSave} isLoading={isLoading}>
            Save Search
          </Button>
        </Box>
      </Box>
    </Modal>
  );
};
