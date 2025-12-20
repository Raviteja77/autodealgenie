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
} from '@mui/material';
import { AccountBalance } from '@mui/icons-material';

interface FinancingStepProps {
  assessment: {
    financing_type?: string;
    loan_amount?: number;
    estimated_monthly_payment?: number;
    estimated_total_cost?: number;
    total_interest?: number;
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
    estimated_monthly_payment,
    estimated_total_cost,
    total_interest,
    financing_recommendation,
  } = assessment;

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <AccountBalance color="primary" />
          <Typography variant="h6">Financing Assessment</Typography>
        </Box>
        <Divider sx={{ mb: 2 }} />

        {financing_type === 'cash' ? (
          <Box>
            <Typography variant="body1" gutterBottom>
              {financing_recommendation || 'Cash purchase - no financing costs'}
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Total Cost
              </Typography>
              <Typography variant="h4" fontWeight="bold" color="success.main">
                ${estimated_total_cost?.toLocaleString() || purchasePrice.toLocaleString()}
              </Typography>
            </Box>
          </Box>
        ) : (
          <Box>
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
                {estimated_monthly_payment !== undefined && (
                  <TableRow>
                    <TableCell>
                      <Typography fontWeight="bold">Monthly Payment</Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography fontWeight="bold" color="primary.main">
                        ${estimated_monthly_payment.toLocaleString()}
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
                {total_interest !== undefined && (
                  <TableRow>
                    <TableCell>Total Interest</TableCell>
                    <TableCell align="right">
                      ${total_interest.toLocaleString()}
                    </TableCell>
                  </TableRow>
                )}
                {estimated_total_cost !== undefined && (
                  <TableRow>
                    <TableCell>
                      <Typography fontWeight="bold">Total Cost</Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography fontWeight="bold">
                        ${estimated_total_cost.toLocaleString()}
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};
