/**
 * EvaluationScoreCard Component
 * 
 * Displays the overall deal quality score with visual indicators
 * and score breakdown.
 */

import { Box, Typography, Chip, Grid } from "@mui/material";
import { CheckCircle, Warning, Cancel, TrendingUp } from "@mui/icons-material";
import { Card } from "@/components";
import { EVALUATION_TEXT } from "@/lib/constants";

interface EvaluationScoreCardProps {
  score: number;
  priceDifference: number;
}

export function EvaluationScoreCard({
  score,
  priceDifference,
}: EvaluationScoreCardProps) {
  const getScoreColor = (score: number) => {
    if (score >= 8) return "success";
    if (score >= 6.5) return "info";
    if (score >= 5) return "warning";
    return "error";
  };

  const getScoreIcon = (score: number) => {
    if (score >= 8) return <CheckCircle color="success" />;
    if (score >= 6.5) return <TrendingUp color="info" />;
    if (score >= 5) return <Warning color="warning" />;
    return <Cancel color="error" />;
  };

  const getRecommendation = (score: number) => {
    if (score >= 8) return EVALUATION_TEXT.MESSAGES.EXCELLENT_DEAL;
    if (score >= 6.5) return EVALUATION_TEXT.MESSAGES.GOOD_DEAL;
    if (score >= 5) return EVALUATION_TEXT.MESSAGES.FAIR_DEAL;
    return EVALUATION_TEXT.MESSAGES.POOR_DEAL;
  };

  const getScoreLabel = (score: number) => {
    if (score >= 8) return "Excellent";
    if (score >= 6.5) return "Good";
    if (score >= 5) return "Fair";
    return "Poor";
  };

  return (
    <Card
      shadow="lg"
      sx={{
        mb: 3,
        border: "2px solid",
        borderColor:
          getScoreColor(score) === "success"
            ? "success.main"
            : getScoreColor(score) === "error"
            ? "error.main"
            : "warning.main",
      }}
    >
      <Card.Body>
        <Box sx={{ textAlign: "center", py: 3 }}>
          <Typography
            variant="overline"
            color="text.secondary"
            sx={{ letterSpacing: 2 }}
          >
            {EVALUATION_TEXT.TITLES.DEAL_QUALITY_SCORE}
          </Typography>
          <Box
            sx={{
              display: "flex",
              justifyContent: "center",
              mb: 3,
              mt: 2,
            }}
          >
            {getScoreIcon(score)}
          </Box>
          <Typography
            variant="h1"
            component="div"
            gutterBottom
            sx={{ fontWeight: "bold" }}
          >
            {score.toFixed(1)}
            <Typography
              variant="h4"
              component="span"
              color="text.secondary"
              sx={{ ml: 1 }}
            >
              {EVALUATION_TEXT.LABELS.SCORE_OUT_OF_TEN}
            </Typography>
          </Typography>
          <Chip
            label={getRecommendation(score)}
            color={getScoreColor(score)}
            sx={{
              mt: 2,
              fontSize: "1.1rem",
              py: 3,
              px: 2,
              fontWeight: "bold",
            }}
          />

          {/* Score Breakdown */}
          <Box
            sx={{
              mt: 4,
              textAlign: "left",
              bgcolor: "grey.50",
              p: 3,
              borderRadius: 2,
            }}
          >
            <Typography variant="subtitle2" gutterBottom sx={{ mb: 2 }}>
              Score Breakdown
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Box
                  sx={{
                    textAlign: "center",
                    p: 2,
                    bgcolor: "white",
                    borderRadius: 1,
                  }}
                >
                  <Typography variant="caption" color="text.secondary">
                    Price Competitiveness
                  </Typography>
                  <Typography
                    variant="h6"
                    color="success.main"
                    sx={{ fontWeight: "bold" }}
                  >
                    {getScoreLabel(score)}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box
                  sx={{
                    textAlign: "center",
                    p: 2,
                    bgcolor: "white",
                    borderRadius: 1,
                  }}
                >
                  <Typography variant="caption" color="text.secondary">
                    {EVALUATION_TEXT.LABELS.MARKET_POSITION}
                  </Typography>
                  <Typography
                    variant="h6"
                    color="primary.main"
                    sx={{ fontWeight: "bold" }}
                  >
                    {priceDifference > 0
                      ? EVALUATION_TEXT.LABELS.ABOVE_MARKET
                      : EVALUATION_TEXT.LABELS.BELOW_MARKET}
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Box>
        </Box>
      </Card.Body>
    </Card>
  );
}
