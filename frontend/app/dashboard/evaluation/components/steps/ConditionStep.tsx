import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
} from '@mui/material';
import { CheckCircle, Build } from '@mui/icons-material';

interface ConditionStepProps {
  assessment: {
    condition_score: number;
    condition_notes: string[];
    recommended_inspection: boolean;
  };
}

export const ConditionStep: React.FC<ConditionStepProps> = ({ assessment }) => {
  const { condition_score, condition_notes, recommended_inspection } = assessment;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Vehicle Condition Assessment
        </Typography>
        <Divider sx={{ mb: 2 }} />

        <Box sx={{ mb: 3 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Condition Score
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="h4" fontWeight="bold" color="primary.main">
              {condition_score.toFixed(1)}
            </Typography>
            <Typography variant="body1" color="text.secondary">
              / 10
            </Typography>
          </Box>
        </Box>

        {condition_notes && condition_notes.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Key Observations
            </Typography>
            <List dense>
              {condition_notes.map((note, index) => (
                <ListItem key={index} sx={{ px: 0 }}>
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    <CheckCircle color="primary" fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary={note}
                    primaryTypographyProps={{ variant: 'body2' }}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        )}

        {recommended_inspection && (
          <Box
            sx={{
              bgcolor: 'warning.light',
              p: 2,
              borderRadius: 1,
              display: 'flex',
              alignItems: 'center',
              gap: 2,
            }}
          >
            <Build color="warning" />
            <Box>
              <Typography variant="subtitle2" fontWeight="bold">
                Professional Inspection Recommended
              </Typography>
              <Typography variant="body2">
                We recommend getting a professional pre-purchase inspection before
                finalizing this deal.
              </Typography>
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};
