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
  Chip,
} from '@mui/material';
import { TrendingUp, TrendingDown, Info } from '@mui/icons-material';

interface PriceStepProps {
  assessment: {
    fair_value: number;
    score: number;
    insights: string[];
    talking_points: string[];
  };
  askingPrice: number;
}

export const PriceStep: React.FC<PriceStepProps> = ({ assessment, askingPrice }) => {
  const { fair_value, score, insights, talking_points } = assessment;
  const priceDiff = askingPrice - fair_value;
  const isGoodDeal = priceDiff <= 0;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Price Analysis
        </Typography>
        <Divider sx={{ mb: 2 }} />

        <Box sx={{ display: 'flex', gap: 3, mb: 3, flexWrap: 'wrap' }}>
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Asking Price
            </Typography>
            <Typography variant="h5" fontWeight="bold">
              ${askingPrice.toLocaleString()}
            </Typography>
          </Box>
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Fair Market Value
            </Typography>
            <Typography variant="h5" fontWeight="bold" color="primary.main">
              ${fair_value.toLocaleString()}
            </Typography>
          </Box>
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Price Score
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="h5" fontWeight="bold">
                {score.toFixed(1)}
              </Typography>
              <Typography variant="body1" color="text.secondary">
                / 10
              </Typography>
            </Box>
          </Box>
        </Box>

        <Box sx={{ mb: 3 }}>
          <Chip
            icon={isGoodDeal ? <TrendingDown /> : <TrendingUp />}
            label={
              isGoodDeal
                ? `${Math.abs(priceDiff).toLocaleString()} below market`
                : `${Math.abs(priceDiff).toLocaleString()} above market`
            }
            color={isGoodDeal ? 'success' : 'warning'}
            sx={{ fontWeight: 'bold' }}
          />
        </Box>

        {insights && insights.length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" gutterBottom>
              Key Insights
            </Typography>
            <List dense>
              {insights.map((insight, index) => (
                <ListItem key={index} sx={{ px: 0 }}>
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    <Info color="primary" fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary={insight}
                    primaryTypographyProps={{ variant: 'body2' }}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        )}

        {talking_points && talking_points.length > 0 && (
          <Box
            sx={{
              bgcolor: 'info.light',
              p: 2,
              borderRadius: 1,
            }}
          >
            <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
              Negotiation Talking Points
            </Typography>
            <List dense>
              {talking_points.map((point, index) => (
                <ListItem key={index} sx={{ px: 0 }}>
                  <ListItemText
                    primary={`• ${point}`}
                    primaryTypographyProps={{ variant: 'body2' }}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};
