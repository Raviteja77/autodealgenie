import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Divider,
  Table,
  TableBody,
  TableRow,
  TableCell,
  Alert,
  Chip,
  Stack,
} from '@mui/material';
import { AccountBalance, TrendingUp, TrendingDown, CheckCircle } from '@mui/icons-material';

interface FinancingStepProps {
  assessment: {
    financing_type?: string;
    loan_amount?: number;
    monthly_payment?: number;
    total_cost?: number;
    total_interest?: number;
    affordability_score?: number;
    affordability_notes?: string[];
    recommendation?: string;
    recommendation_reason?: string;
    cash_vs_financing_savings?: number;
    // Legacy fields for backwards compatibility
    estimated_monthly_payment?: number;
    estimated_total_cost?: number;
    financing_recommendation?: string;
  };
  purchasePrice: number;
}

export const FinancingStep: React.FC<FinancingStepProps> = ({
  assessment,
  purchasePrice,
}) => {
  const {
    financing_type,
    loan_amount,
    monthly_payment,
    total_cost,
    total_interest,
    affordability_score,
    affordability_notes,
    recommendation,
    recommendation_reason,
    cash_vs_financing_savings,
    // Legacy fields
    estimated_monthly_payment,
    estimated_total_cost,
    financing_recommendation,
  } = assessment;

  // Handle legacy data structure
  const displayMonthlyPayment = monthly_payment || estimated_monthly_payment;
  const displayTotalCost = total_cost || estimated_total_cost;
  const displayRecommendation = recommendation_reason || financing_recommendation;

  // Determine recommendation color and icon
  const getRecommendationDisplay = () => {
    if (!recommendation) return null;
    
    const recommendationMap: Record<string, { color: 'success' | 'info' | 'warning' | 'error', label: string }> = {
      cash: { color: 'success', label: 'Cash Recommended' },
      financing: { color: 'info', label: 'Financing Recommended' },
      either: { color: 'warning', label: 'Either Option Works' },
    };

    return recommendationMap[recommendation] || { color: 'info', label: 'See Details' };
  };

  const recommendationDisplay = getRecommendationDisplay();

  // Determine affordability status
  const getAffordabilityStatus = (): { color: 'success' | 'info' | 'warning' | 'error', label: string, icon: JSX.Element } | null => {
    if (!affordability_score) return null;
    
    if (affordability_score >= 8) {
      return { color: 'success', label: 'Excellent Affordability', icon: <CheckCircle /> };
    } else if (affordability_score >= 6) {
      return { color: 'info', label: 'Good Affordability', icon: <TrendingUp /> };
    } else if (affordability_score >= 4) {
      return { color: 'warning', label: 'Moderate Affordability', icon: <TrendingDown /> };
    } else {
      return { color: 'error', label: 'Affordability Concern', icon: <TrendingDown /> };
    }
  };

  const affordabilityStatus = getAffordabilityStatus();

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <AccountBalance color="primary" />
          <Typography variant="h6">Financing Assessment</Typography>
        </Box>
        <Divider sx={{ mb: 2 }} />

        {/* Financing Recommendation Alert */}
        {recommendationDisplay && (
          <Alert severity={recommendationDisplay.color} sx={{ mb: 2 }}>
            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
              {recommendationDisplay.label}
            </Typography>
            <Typography variant="body2">
              {displayRecommendation}
            </Typography>
          </Alert>
        )}

        {financing_type === 'cash' ? (
          <Box>
            <Typography variant="body1" gutterBottom>
              {displayRecommendation || 'Cash purchase - no financing costs'}
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Total Cost
              </Typography>
              <Typography variant="h4" fontWeight="bold" color="success.main">
                ${displayTotalCost?.toLocaleString() || purchasePrice.toLocaleString()}
              </Typography>
            </Box>
          </Box>
        ) : (
          <Box>
            {/* Affordability Score */}
            {affordabilityStatus && (
              <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="subtitle2">Affordability:</Typography>
                <Chip
                  label={affordabilityStatus.label}
                  color={affordabilityStatus.color}
                  size="small"
                  icon={affordabilityStatus.icon}
                />
                <Typography variant="body2" color="text.secondary">
                  ({affordability_score?.toFixed(1)}/10)
                </Typography>
              </Box>
            )}

            {/* Payment Summary */}
            <Typography variant="subtitle2" gutterBottom sx={{ mb: 2 }}>
              Payment Calculator (60 months)
            </Typography>
            <Table size="small">
              <TableBody>
                <TableRow>
                  <TableCell>Purchase Price</TableCell>
                  <TableCell align="right">
                    <Typography fontWeight="bold">
                      ${purchasePrice.toLocaleString()}
                    </Typography>
                  </TableCell>
                </TableRow>
                {loan_amount !== undefined && (
                  <TableRow>
                    <TableCell>Loan Amount</TableCell>
                    <TableCell align="right">
                      ${loan_amount.toLocaleString()}
                    </TableCell>
                  </TableRow>
                )}
                {displayMonthlyPayment !== undefined && (
                  <TableRow>
                    <TableCell>
                      <Typography fontWeight="bold">Monthly Payment</Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography fontWeight="bold" color="primary.main">
                        ${displayMonthlyPayment.toLocaleString()}
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
                {total_interest !== undefined && total_interest !== null && (
                  <TableRow>
                    <TableCell>Total Interest</TableCell>
                    <TableCell align="right">
                      ${total_interest.toLocaleString()}
                    </TableCell>
                  </TableRow>
                )}
                {displayTotalCost !== undefined && (
                  <TableRow>
                    <TableCell>
                      <Typography fontWeight="bold">Total Cost</Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography fontWeight="bold">
                        ${displayTotalCost.toLocaleString()}
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
                {cash_vs_financing_savings !== undefined && cash_vs_financing_savings > 0 && (
                  <TableRow>
                    <TableCell>
                      <Typography color="success.main">Savings if Paying Cash</Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography color="success.main" fontWeight="bold">
                        ${cash_vs_financing_savings.toLocaleString()}
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>

            {/* Affordability Notes */}
            {affordability_notes && affordability_notes.length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Affordability Analysis
                </Typography>
                <Stack spacing={1}>
                  {affordability_notes.map((note, index) => (
                    <Typography key={index} variant="body2" color="text.secondary">
                      • {note}
                    </Typography>
                  ))}
                </Stack>
              </Box>
            )}
          </Box>
        )}
      </CardContent>
    </Card>
  );
};
