/**
 * KeyInsightsList Component
 * 
 * Displays key market insights about the vehicle.
 */

import { Box, Typography, Divider, Stack } from "@mui/material";
import { CheckCircle } from "@mui/icons-material";
import { Card } from "@/components";
import { EVALUATION_TEXT } from "@/lib/constants";

interface KeyInsightsListProps {
  insights: string[];
}

export function KeyInsightsList({ insights }: KeyInsightsListProps) {
  if (!insights || insights.length === 0) {
    return null;
  }

  return (
    <Card
      sx={{
        mb: 3,
        bgcolor: "primary.50",
        border: "1px solid",
        borderColor: "primary.200",
      }}
    >
      <Card.Body>
        <Typography
          variant="h6"
          gutterBottom
          sx={{ color: "primary.dark" }}
        >
          📊 {EVALUATION_TEXT.TITLES.KEY_INSIGHTS}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Important factors influencing this vehicle&apos;s value
        </Typography>
        <Divider sx={{ mb: 2 }} />
        <Stack spacing={2}>
          {insights.map((insight, index) => (
            <Box
              key={index}
              sx={{
                display: "flex",
                alignItems: "start",
                p: 2,
                bgcolor: "white",
                borderRadius: 2,
                boxShadow: 1,
              }}
            >
              <CheckCircle
                color="success"
                sx={{ mr: 2, mt: 0.2, fontSize: 24, flexShrink: 0 }}
              />
              <Typography variant="body1" sx={{ fontWeight: 500 }}>
                {insight}
              </Typography>
            </Box>
          ))}
        </Stack>
      </Card.Body>
    </Card>
  );
}
