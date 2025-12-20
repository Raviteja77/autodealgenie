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
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Checkbox,
  FormControlLabel,
} from '@mui/material';
import {
  CheckCircle,
  ExpandMore,
  AssignmentTurnedIn,
  Download,
  Email,
  Share,
} from '@mui/icons-material';
import { Button } from '@/components';

interface FinalStepProps {
  assessment: {
    overall_score: number;
    recommendation: string;
    summary: {
      condition_score: number;
      price_score: number;
      risk_score: number;
    };
    next_steps: string[];
  };
  vehicleInfo: {
    make: string;
    model: string;
    year: number;
  };
}

export const FinalStep: React.FC<FinalStepProps> = ({ assessment, vehicleInfo }) => {
  const { overall_score, recommendation, summary, next_steps } = assessment;
  const [completedActions, setCompletedActions] = React.useState<Set<number>>(
    new Set()
  );

  const toggleAction = (index: number) => {
    setCompletedActions((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  const getRecommendationType = (score: number) => {
    if (score >= 8) return { text: 'Highly Recommended', color: 'success' };
    if (score >= 6.5) return { text: 'Recommended', color: 'info' };
    if (score >= 5) return { text: 'Fair Deal', color: 'warning' };
    return { text: 'Not Recommended', color: 'error' };
  };

  const recType = getRecommendationType(overall_score);

  return (
    <Box>
      {/* Executive Summary */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Final Evaluation Report
          </Typography>
          <Typography variant="subtitle1" color="text.secondary" gutterBottom>
            {vehicleInfo.year} {vehicleInfo.make} {vehicleInfo.model}
          </Typography>
          <Divider sx={{ my: 2 }} />

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Overall Score
              </Typography>
              <Typography variant="h3" fontWeight="bold" color="primary.main">
                {overall_score.toFixed(1)}
                <Typography
                  component="span"
                  variant="h6"
                  color="text.secondary"
                  sx={{ ml: 1 }}
                >
                  / 10
                </Typography>
              </Typography>
            </Box>
            <Chip
              icon={<CheckCircle />}
              label={recType.text}
              color={recType.color as any}
              sx={{ fontWeight: 'bold', fontSize: '0.9rem', px: 1 }}
            />
          </Box>

          <Box
            sx={{
              bgcolor: `${recType.color}.light`,
              p: 2,
              borderRadius: 1,
            }}
          >
            <Typography variant="body1" fontWeight="medium">
              {recommendation}
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* Detailed Analysis */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Detailed Analysis
          </Typography>
          <Divider sx={{ mb: 2 }} />

          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography fontWeight="medium">Score Breakdown</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Vehicle Condition</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {summary.condition_score.toFixed(1)} / 10
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Price Analysis</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {summary.price_score.toFixed(1)} / 10
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Risk Assessment</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {summary.risk_score.toFixed(1)} / 10
                  </Typography>
                </Box>
              </Box>
            </AccordionDetails>
          </Accordion>
        </CardContent>
      </Card>

      {/* Action Items */}
      {next_steps && next_steps.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <AssignmentTurnedIn color="primary" />
              <Typography variant="h6">Recommended Next Steps</Typography>
            </Box>
            <Divider sx={{ mb: 2 }} />
            <List>
              {next_steps.map((step, index) => (
                <ListItem key={index} sx={{ px: 0 }}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={completedActions.has(index)}
                        onChange={() => toggleAction(index)}
                      />
                    }
                    label={
                      <Typography
                        variant="body2"
                        sx={{
                          textDecoration: completedActions.has(index)
                            ? 'line-through'
                            : 'none',
                        }}
                      >
                        {step}
                      </Typography>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {/* Export Options */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Export & Share
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Button
              variant="outline"
              size="md"
              leftIcon={<Download />}
              onClick={() => alert('PDF export coming soon!')}
            >
              Download PDF
            </Button>
            <Button
              variant="outline"
              size="md"
              leftIcon={<Email />}
              onClick={() => alert('Email feature coming soon!')}
            >
              Email Report
            </Button>
            <Button
              variant="outline"
              size="md"
              leftIcon={<Share />}
              onClick={() => alert('Share feature coming soon!')}
            >
              Share
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};
