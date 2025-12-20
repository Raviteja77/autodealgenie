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
import { Warning, Error, CheckCircle } from '@mui/icons-material';

interface RiskStepProps {
  assessment: {
    risk_score: number;
    risk_factors: string[];
    recommendation: string;
  };
}

const getRiskLevel = (score: number) => {
  if (score < 4) return { level: 'Low Risk', color: 'success', icon: <CheckCircle /> };
  if (score < 7) return { level: 'Medium Risk', color: 'warning', icon: <Warning /> };
  return { level: 'High Risk', color: 'error', icon: <Error /> };
};

const getRiskIcon = (riskText: string) => {
  const lowerText = riskText.toLowerCase();
  if (lowerText.includes('low') || lowerText.includes('clean') || lowerText.includes('available')) {
    return <CheckCircle color="success" fontSize="small" />;
  }
  if (lowerText.includes('high') || lowerText.includes('over')) {
    return <Error color="error" fontSize="small" />;
  }
  return <Warning color="warning" fontSize="small" />;
};

export const RiskStep: React.FC<RiskStepProps> = ({ assessment }) => {
  const { risk_score, risk_factors, recommendation } = assessment;
  const riskLevel = getRiskLevel(risk_score);

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Risk Assessment
        </Typography>
        <Divider sx={{ mb: 2 }} />

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Risk Score
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="h4" fontWeight="bold" color={`${riskLevel.color}.main`}>
                {risk_score.toFixed(1)}
              </Typography>
              <Typography variant="body1" color="text.secondary">
                / 10
              </Typography>
            </Box>
          </Box>
          <Chip
            icon={riskLevel.icon}
            label={riskLevel.level}
            color={riskLevel.color as 'success' | 'warning' | 'error'}
            sx={{ fontWeight: 'bold' }}
          />
        </Box>

        <Box
          sx={{
            bgcolor: `${riskLevel.color}.light`,
            p: 2,
            borderRadius: 1,
            mb: 3,
          }}
        >
          <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
            Recommendation
          </Typography>
          <Typography variant="body2">{recommendation}</Typography>
        </Box>

        {risk_factors && risk_factors.length > 0 && (
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Identified Risk Factors
            </Typography>
            <List dense>
              {risk_factors.map((factor, index) => (
                <ListItem key={index} sx={{ px: 0 }}>
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    {getRiskIcon(factor)}
                  </ListItemIcon>
                  <ListItemText
                    primary={factor}
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
