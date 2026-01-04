/**
 * DealScoreDisplay Component
 * 
 * Displays the AI-generated deal score with visual indicators
 */

import { Box, Typography, LinearProgress, Stack } from "@mui/material";
import { CheckCircle, Warning, Cancel } from "@mui/icons-material";
import { Card } from "@/components";

interface DealScoreDisplayProps {
  score: number;
}

export function DealScoreDisplay({ score }: DealScoreDisplayProps) {
  const getScoreIcon = (score: number) => {
    if (score >= 80) return <CheckCircle />;
    if (score >= 60) return <Warning />;
    return <Cancel />;
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return "Excellent Deal";
    if (score >= 60) return "Good Deal";
    return "Proceed with Caution";
  };

  return (
    <Card
      shadow="lg"
      sx={{
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        color: "white",
      }}
    >
      <Card.Body>
        <Stack spacing={2}>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            {getScoreIcon(score)}
            <Typography variant="h6">{getScoreLabel(score)}</Typography>
          </Box>
          <Typography variant="h2" fontWeight="bold">
            {score}/100
          </Typography>
          <LinearProgress
            variant="determinate"
            value={score}
            sx={{
              height: 8,
              borderRadius: 4,
              bgcolor: "rgba(255,255,255,0.3)",
              "& .MuiLinearProgress-bar": {
                bgcolor: "white",
              },
            }}
          />
          <Typography variant="body2" sx={{ opacity: 0.9 }}>
            Based on market data, vehicle condition, and pricing analysis
          </Typography>
        </Stack>
      </Card.Body>
    </Card>
  );
}
