import React from 'react';
import { Box, Card, CardContent, Typography, LinearProgress } from '@mui/material';
import { CheckCircle, ThumbUp, Warning, ThumbDown } from '@mui/icons-material';

interface ScoreCardProps {
  overallScore: number;
  conditionScore?: number;
  priceScore?: number;
  financingScore?: number;
  riskScore?: number;
}

const getOverallRating = (score: number) => {
  if (score >= 8.5)
    return { text: 'Excellent Deal', icon: <CheckCircle />, color: 'success.main' };
  if (score >= 7)
    return { text: 'Good Deal', icon: <ThumbUp />, color: 'success.main' };
  if (score >= 5.5)
    return { text: 'Fair Deal', icon: <Warning />, color: 'warning.main' };
  return { text: 'Reconsider', icon: <ThumbDown />, color: 'error.main' };
};

export const ScoreCard: React.FC<ScoreCardProps> = ({
  overallScore,
  conditionScore,
  priceScore,
  financingScore,
  riskScore,
}) => {
  const rating = getOverallRating(overallScore);

  return (
    <Card sx={{ bgcolor: rating.color, color: 'white' }}>
      <CardContent>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            mb: 3,
          }}
        >
          <Box>
            <Typography variant="h5" gutterBottom>
              Overall Deal Score
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {rating.icon}
              <Typography variant="h6">{rating.text}</Typography>
            </Box>
          </Box>
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h2" fontWeight="bold">
              {overallScore.toFixed(1)}
            </Typography>
            <Typography variant="body2">out of 10</Typography>
          </Box>
        </Box>

        {/* Breakdown */}
        {(conditionScore !== undefined ||
          priceScore !== undefined ||
          financingScore !== undefined ||
          riskScore !== undefined) && (
          <Box sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)', p: 2, borderRadius: 1 }}>
            <Typography variant="subtitle2" gutterBottom sx={{ mb: 2 }}>
              Score Breakdown
            </Typography>
            {conditionScore !== undefined && (
              <Box sx={{ mb: 2 }}>
                <Box
                  sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}
                >
                  <Typography variant="body2">Condition</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {conditionScore.toFixed(1)}
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={(conditionScore / 10) * 100}
                  sx={{
                    height: 6,
                    borderRadius: 1,
                    bgcolor: 'rgba(255, 255, 255, 0.3)',
                    '& .MuiLinearProgress-bar': {
                      bgcolor: 'white',
                    },
                  }}
                />
              </Box>
            )}
            {priceScore !== undefined && (
              <Box sx={{ mb: 2 }}>
                <Box
                  sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}
                >
                  <Typography variant="body2">Price</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {priceScore.toFixed(1)}
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={(priceScore / 10) * 100}
                  sx={{
                    height: 6,
                    borderRadius: 1,
                    bgcolor: 'rgba(255, 255, 255, 0.3)',
                    '& .MuiLinearProgress-bar': {
                      bgcolor: 'white',
                    },
                  }}
                />
              </Box>
            )}
            {financingScore !== undefined && (
              <Box sx={{ mb: 2 }}>
                <Box
                  sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}
                >
                  <Typography variant="body2">Financing</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {financingScore.toFixed(1)}
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={(financingScore / 10) * 100}
                  sx={{
                    height: 6,
                    borderRadius: 1,
                    bgcolor: 'rgba(255, 255, 255, 0.3)',
                    '& .MuiLinearProgress-bar': {
                      bgcolor: 'white',
                    },
                  }}
                />
              </Box>
            )}
            {riskScore !== undefined && (
              <Box>
                <Box
                  sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}
                >
                  <Typography variant="body2">Risk (lower is better)</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {riskScore.toFixed(1)}
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={((10 - riskScore) / 10) * 100}
                  sx={{
                    height: 6,
                    borderRadius: 1,
                    bgcolor: 'rgba(255, 255, 255, 0.3)',
                    '& .MuiLinearProgress-bar': {
                      bgcolor: 'white',
                    },
                  }}
                />
              </Box>
            )}
          </Box>
        )}
      </CardContent>
    </Card>
  );
};
