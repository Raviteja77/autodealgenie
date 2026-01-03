/**
 * NegotiationTips Component
 * 
 * Displays AI-generated negotiation talking points
 */

import { Typography, Stack, Box, Divider } from "@mui/material";
import { Lightbulb } from "@mui/icons-material";
import { Card } from "@/components";

interface NegotiationTipsProps {
  talkingPoints: string[];
}

export function NegotiationTips({ talkingPoints }: NegotiationTipsProps) {
  if (talkingPoints.length === 0) return null;

  return (
    <Card
      sx={{
        bgcolor: "warning.50",
        border: "1px solid",
        borderColor: "warning.200",
      }}
    >
      <Card.Body>
        <Typography variant="h6" gutterBottom sx={{ color: "warning.dark" }}>
          💡 Negotiation Strategy
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Use these points during your negotiation
        </Typography>
        <Divider sx={{ mb: 2 }} />
        <Stack spacing={2}>
          {talkingPoints.map((point, index) => (
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
              <Lightbulb
                color="warning"
                sx={{ mr: 2, mt: 0.2, fontSize: 24, flexShrink: 0 }}
              />
              <Typography variant="body1" sx={{ fontWeight: 500 }}>
                {point}
              </Typography>
            </Box>
          ))}
        </Stack>
      </Card.Body>
    </Card>
  );
}
