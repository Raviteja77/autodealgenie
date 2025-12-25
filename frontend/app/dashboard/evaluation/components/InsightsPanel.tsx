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
} from '@mui/material';
import { LightbulbOutlined, CheckCircle, Warning, Info } from '@mui/icons-material';

interface InsightsPanelProps {
  insights: Array<{
    type: 'success' | 'warning' | 'info';
    message: string;
  }>;
  title?: string;
}

const getInsightIcon = (type: string) => {
  switch (type) {
    case 'success':
      return <CheckCircle color="success" />;
    case 'warning':
      return <Warning color="warning" />;
    case 'info':
    default:
      return <Info color="info" />;
  }
};

export const InsightsPanel: React.FC<InsightsPanelProps> = ({
  insights,
  title = 'AI Insights',
}) => {
  if (!insights || insights.length === 0) {
    return null;
  }

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <LightbulbOutlined color="primary" />
          <Typography variant="h6">{title}</Typography>
        </Box>
        <List dense>
          {insights.map((insight, index) => (
            <ListItem key={index} sx={{ px: 0 }}>
              <ListItemIcon sx={{ minWidth: 40 }}>
                {getInsightIcon(insight.type)}
              </ListItemIcon>
              <ListItemText
                primary={insight.message}
                primaryTypographyProps={{
                  variant: 'body2',
                }}
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );
};
