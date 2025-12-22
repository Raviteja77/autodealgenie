'use client';

import React, { useState, useMemo } from 'react';
import {
  Box,
  Typography,
  Grid,
  Divider,
  Stack,
  Alert,
  Chip,
  TextField,
  Slider,
  Paper,
  Table,
  TableBody,
  TableRow,
  TableCell,
  TableHead,
  Tabs,
  Tab,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Calculate,
  CompareArrows,
  LocalAtm,
  AccountBalance,
  Info,
} from '@mui/icons-material';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import type { FinancingOption } from '@/lib/api';

interface FinancingComparisonModalProps {
  isOpen: boolean;
  onClose: () => void;
  financingOptions: FinancingOption[];
  purchasePrice: number;
  onPriceChange?: (newPrice: number) => void;
}

/**
 * FinancingComparisonModal component for detailed side-by-side financing comparison
 * Includes savings calculator, charts, and dynamic price updates
 */
export const FinancingComparisonModal: React.FC<FinancingComparisonModalProps> = ({
  isOpen,
  onClose,
  financingOptions,
  purchasePrice,
  onPriceChange,
}) => {
  const [activeTab, setActiveTab] = useState(0);
  const [customPrice, setCustomPrice] = useState(purchasePrice.toString());
  const [downPaymentPercent, setDownPaymentPercent] = useState(20);

  // Calculate financing options with custom price and down payment
  const calculatedOptions = useMemo(() => {
    const price = parseFloat(customPrice) || purchasePrice;
    const downPayment = (price * downPaymentPercent) / 100;
    const loanAmount = price - downPayment;

    return financingOptions.map((option) => {
      // Recalculate monthly payment based on new loan amount
      const monthlyRate = option.estimated_apr / 12;
      const numPayments = option.loan_term_months;
      const monthlyPayment =
        (loanAmount * monthlyRate * Math.pow(1 + monthlyRate, numPayments)) /
        (Math.pow(1 + monthlyRate, numPayments) - 1);

      const totalCost = monthlyPayment * numPayments + downPayment;
      const totalInterest = totalCost - price;

      return {
        ...option,
        loan_amount: loanAmount,
        down_payment: downPayment,
        monthly_payment_estimate: monthlyPayment,
        total_cost: totalCost,
        total_interest: totalInterest,
      };
    });
  }, [customPrice, downPaymentPercent, purchasePrice, financingOptions]);

  // Calculate cash vs financing savings
  const calculatedCashSavings = useMemo(() => {
    if (calculatedOptions.length === 0) return 0;
    const price = parseFloat(customPrice) || purchasePrice;
    
    // Use 60-month option as default comparison
    const sixtyMonthOption = calculatedOptions.find((opt) => opt.loan_term_months === 60);
    const comparisonOption = sixtyMonthOption || calculatedOptions[0];
    
    return comparisonOption.total_cost - price;
  }, [calculatedOptions, customPrice, purchasePrice]);

  const handlePriceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setCustomPrice(value);
    
    if (onPriceChange) {
      const numValue = parseFloat(value);
      if (!isNaN(numValue) && numValue > 0) {
        onPriceChange(numValue);
      }
    }
  };

  const handleDownPaymentChange = (_event: Event, value: number | number[]) => {
    setDownPaymentPercent(value as number);
  };

  // Find best option (lowest total cost)
  const bestOption = useMemo(() => {
    if (calculatedOptions.length === 0) return null;
    return calculatedOptions.reduce((prev, current) =>
      current.total_cost < prev.total_cost ? current : prev
    );
  }, [calculatedOptions]);

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Financing Comparison & Calculator"
      size="lg"
    >
      <Box sx={{ p: 2 }}>
        {/* Cash Savings Highlight */}
        {calculatedCashSavings > 0 && (
          <Alert severity="success" icon={<LocalAtm />} sx={{ mb: 3 }}>
            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
              💰 Cash Savings: ${calculatedCashSavings.toLocaleString()}
            </Typography>
            <Typography variant="body2">
              Save ${calculatedCashSavings.toLocaleString()} by paying cash instead of financing!
              This includes all interest charges over the loan term.
            </Typography>
            <Box sx={{ mt: 1 }}>
              <Chip
                label="Best Option: Pay Cash"
                color="success"
                size="small"
                icon={<TrendingDown />}
              />
            </Box>
          </Alert>
        )}

        {/* Calculator Section */}
        <Card sx={{ mb: 3 }}>
          <Card.Body>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <Calculate color="primary" />
              <Typography variant="h6">Payment Calculator</Typography>
            </Box>
            <Divider sx={{ mb: 2 }} />

            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Purchase Price"
                  type="number"
                  value={customPrice}
                  onChange={handlePriceChange}
                  InputProps={{
                    startAdornment: <Typography sx={{ mr: 1 }}>$</Typography>,
                  }}
                  helperText="Adjust to see how different prices affect payments"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="body2" gutterBottom>
                  Down Payment: {downPaymentPercent}% ($
                  {(
                    ((parseFloat(customPrice) || purchasePrice) *
                      downPaymentPercent) /
                    100
                  ).toLocaleString()}
                  )
                </Typography>
                <Slider
                  value={downPaymentPercent}
                  onChange={handleDownPaymentChange}
                  min={0}
                  max={50}
                  step={5}
                  marks={[
                    { value: 0, label: '0%' },
                    { value: 20, label: '20%' },
                    { value: 50, label: '50%' },
                  ]}
                  valueLabelDisplay="auto"
                  valueLabelFormat={(value) => `${value}%`}
                />
              </Grid>
            </Grid>

            <Alert severity="info" icon={<Info />} sx={{ mt: 2 }}>
              <Typography variant="caption">
                <strong>Tip:</strong> A higher down payment reduces your loan amount,
                monthly payments, and total interest paid.
              </Typography>
            </Alert>
          </Card.Body>
        </Card>

        {/* Tabs for different views */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)}>
            <Tab label="Side-by-Side" icon={<CompareArrows />} iconPosition="start" />
            <Tab label="Payment Chart" icon={<TrendingUp />} iconPosition="start" />
            <Tab label="Cost Breakdown" icon={<AccountBalance />} iconPosition="start" />
          </Tabs>
        </Box>

        {/* Side-by-Side Comparison */}
        {activeTab === 0 && (
          <Grid container spacing={2}>
            {calculatedOptions.map((option) => (
              <Grid item xs={12} md={4} key={option.loan_term_months}>
                <Paper
                  elevation={bestOption?.loan_term_months === option.loan_term_months ? 4 : 1}
                  sx={{
                    p: 2,
                    height: '100%',
                    border: bestOption?.loan_term_months === option.loan_term_months ? 2 : 0,
                    borderColor: 'primary.main',
                    position: 'relative',
                  }}
                >
                  {bestOption?.loan_term_months === option.loan_term_months && (
                    <Chip
                      label="Best Value"
                      color="primary"
                      size="small"
                      sx={{ position: 'absolute', top: 8, right: 8 }}
                    />
                  )}
                  <Typography variant="h6" gutterBottom>
                    {option.loan_term_months} Months
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {(option.loan_term_months / 12).toFixed(1)} years
                  </Typography>
                  <Divider sx={{ my: 2 }} />

                  <Stack spacing={2}>
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Monthly Payment
                      </Typography>
                      <Typography variant="h5" color="primary.main" fontWeight="bold">
                        ${option.monthly_payment_estimate.toLocaleString(undefined, {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}
                      </Typography>
                    </Box>

                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Interest Rate
                      </Typography>
                      <Typography variant="body1" fontWeight="medium">
                        {(option.estimated_apr * 100).toFixed(2)}% APR
                      </Typography>
                    </Box>

                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Total Interest
                      </Typography>
                      <Typography variant="body1" color="warning.main">
                        ${option.total_interest.toLocaleString(undefined, {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}
                      </Typography>
                    </Box>

                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Total Cost
                      </Typography>
                      <Typography variant="body1" fontWeight="bold">
                        ${option.total_cost.toLocaleString(undefined, {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}
                      </Typography>
                    </Box>
                  </Stack>
                </Paper>
              </Grid>
            ))}
          </Grid>
        )}

        {/* Payment Chart */}
        {activeTab === 1 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Monthly Payment Comparison
            </Typography>
            <Stack spacing={2} sx={{ mt: 2 }}>
              {calculatedOptions.map((option) => {
                const maxPayment = Math.max(
                  ...calculatedOptions.map((opt) => opt.monthly_payment_estimate)
                );
                const percentage = (option.monthly_payment_estimate / maxPayment) * 100;

                return (
                  <Box key={option.loan_term_months}>
                    <Box
                      sx={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        mb: 0.5,
                      }}
                    >
                      <Typography variant="body2">
                        {option.loan_term_months} months
                      </Typography>
                      <Typography variant="body2" fontWeight="bold">
                        ${option.monthly_payment_estimate.toLocaleString(undefined, {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}
                        /mo
                      </Typography>
                    </Box>
                    <Box
                      sx={{
                        width: `${percentage}%`,
                        height: 40,
                        bgcolor:
                          bestOption?.loan_term_months === option.loan_term_months
                            ? 'primary.main'
                            : 'grey.300',
                        borderRadius: 1,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'flex-end',
                        px: 1,
                      }}
                    >
                      <Typography
                        variant="caption"
                        sx={{ color: 'white', fontWeight: 'bold' }}
                      >
                        {(option.estimated_apr * 100).toFixed(2)}% APR
                      </Typography>
                    </Box>
                  </Box>
                );
              })}
            </Stack>
          </Box>
        )}

        {/* Cost Breakdown Table */}
        {activeTab === 2 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Detailed Cost Breakdown
            </Typography>
            <Table size="small" sx={{ mt: 2 }}>
              <TableHead>
                <TableRow>
                  <TableCell>Term</TableCell>
                  <TableCell align="right">Loan Amount</TableCell>
                  <TableCell align="right">Down Payment</TableCell>
                  <TableCell align="right">Monthly</TableCell>
                  <TableCell align="right">Total Interest</TableCell>
                  <TableCell align="right">Total Cost</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {calculatedOptions.map((option) => (
                  <TableRow
                    key={option.loan_term_months}
                    sx={{
                      bgcolor:
                        bestOption?.loan_term_months === option.loan_term_months
                          ? 'action.selected'
                          : 'inherit',
                    }}
                  >
                    <TableCell>
                      {option.loan_term_months} mo
                      {bestOption?.loan_term_months === option.loan_term_months && (
                        <Chip
                          label="Best"
                          color="primary"
                          size="small"
                          sx={{ ml: 1 }}
                        />
                      )}
                    </TableCell>
                    <TableCell align="right">
                      ${option.loan_amount.toLocaleString(undefined, {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </TableCell>
                    <TableCell align="right">
                      ${option.down_payment.toLocaleString(undefined, {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </TableCell>
                    <TableCell align="right">
                      ${option.monthly_payment_estimate.toLocaleString(undefined, {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </TableCell>
                    <TableCell align="right" sx={{ color: 'warning.main' }}>
                      ${option.total_interest.toLocaleString(undefined, {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </TableCell>
                    <TableCell align="right" sx={{ fontWeight: 'bold' }}>
                      ${option.total_cost.toLocaleString(undefined, {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </TableCell>
                  </TableRow>
                ))}
                {/* Cash option row */}
                <TableRow sx={{ bgcolor: 'success.light' }}>
                  <TableCell>
                    <Typography fontWeight="bold">Cash</Typography>
                  </TableCell>
                  <TableCell align="right">$0</TableCell>
                  <TableCell align="right">
                    ${(parseFloat(customPrice) || purchasePrice).toLocaleString(undefined, {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
                  </TableCell>
                  <TableCell align="right">$0</TableCell>
                  <TableCell align="right" sx={{ color: 'success.main' }}>
                    $0
                  </TableCell>
                  <TableCell align="right" sx={{ fontWeight: 'bold' }}>
                    ${(parseFloat(customPrice) || purchasePrice).toLocaleString(undefined, {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>

            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="body2">
                <strong>💡 Financial Tip:</strong> Consider your monthly budget and total
                cost. Shorter terms have higher monthly payments but lower total cost.
                Longer terms have lower monthly payments but cost more overall due to
                interest.
              </Typography>
            </Alert>
          </Box>
        )}

        {/* Action Buttons */}
        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
          <Button
            variant="primary"
            onClick={() => {
              // You could add functionality to apply the selected option
              onClose();
            }}
          >
            Continue with Selected Option
          </Button>
        </Box>
      </Box>
    </Modal>
  );
};
