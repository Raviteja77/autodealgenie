/**
 * TalkingPointsList Component
 * 
 * Displays negotiation talking points to help users during negotiation.
 */

import { Box, Typography, Divider, Stack } from "@mui/material";
import { TrendingUp } from "@mui/icons-material";
import { Card } from "@/components";
import { EVALUATION_TEXT } from "@/lib/constants";

interface TalkingPointsListProps {
  talkingPoints: string[];
}

export function TalkingPointsList({
  talkingPoints,
}: TalkingPointsListProps) {
  if (!talkingPoints || talkingPoints.length === 0) {
    return null;
  }

  return (
    <Card
      sx={{
        mb: 3,
        border: "2px solid",
        borderColor: "primary.main",
      }}
    >
      <Card.Body>
        <Typography
          variant="h6"
          gutterBottom
          sx={{ display: "flex", alignItems: "center", gap: 1 }}
        >
          <TrendingUp color="primary" />
          {EVALUATION_TEXT.TITLES.TALKING_POINTS}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Use these points to strengthen your negotiation position
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
                bgcolor: "grey.50",
                borderRadius: 2,
                border: "1px solid",
                borderColor: "grey.200",
              }}
            >
              <Typography
                variant="body2"
                sx={{
                  minWidth: 32,
                  height: 32,
                  borderRadius: "50%",
                  bgcolor: "primary.main",
                  color: "white",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  mr: 2,
                  flexShrink: 0,
                  fontWeight: "bold",
                  fontSize: "1rem",
                }}
              >
                {index + 1}
              </Typography>
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
