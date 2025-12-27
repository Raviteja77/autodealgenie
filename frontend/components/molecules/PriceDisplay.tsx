import React from 'react';
import { Box, Typography, ToggleButtonGroup, ToggleButton } from '@mui/material';
import { AttachMoney, AccountBalance } from '@mui/icons-material';
import {
  PriceDisplayProps,
  MonthlyPaymentDisplayProps,
  PriceSwitcherProps,
} from './PriceDisplay.types';

/**
 * Simple price display component
 */
export const PriceDisplay: React.FC<PriceDisplayProps> = ({
  price,
  label,
  size = 'md',
  showCurrency = true,
  color = 'primary',
}) => {
  const variantMap = {
    sm: 'h6',
    md: 'h4',
    lg: 'h2',
  } as const;

  return (
    <Box>
      {label && (
        <Typography variant="body2" color="text.secondary" gutterBottom>
          {label}
        </Typography>
      )}
      <Typography
        variant={variantMap[size]}
        color={color}
        fontWeight={700}
      >
        {showCurrency && '$'}
        {price.toLocaleString()}
      </Typography>
    </Box>
  );
};

/**
 * Monthly payment display with details
 */
export const MonthlyPaymentDisplay: React.FC<MonthlyPaymentDisplayProps> = ({
  monthlyPayment,
  cashPrice,
  loanTerm,
  totalCost,
  size = 'md',
}) => {
  const variantMap = {
    sm: 'h6',
    md: 'h4',
    lg: 'h2',
  } as const;

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1 }}>
        <Typography variant={variantMap[size]} color="primary" fontWeight={700}>
          ${monthlyPayment.toLocaleString()}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          /month
        </Typography>
      </Box>
      <Typography variant="body2" color="text.secondary">
        Cash price: ${cashPrice.toLocaleString()}
      </Typography>
      {totalCost && loanTerm && (
        <Typography variant="caption" color="text.secondary">
          Total cost: ${totalCost.toLocaleString()} over {loanTerm} months
        </Typography>
      )}
    </Box>
  );
};

/**
 * Price switcher with toggle between cash and monthly payment
 */
export const PriceSwitcher: React.FC<PriceSwitcherProps> = ({
  cashPrice,
  monthlyPayment,
  displayMode,
  onToggleMode,
  loanTerm,
  totalCost,
}) => {
  if (monthlyPayment === null) {
    return <PriceDisplay price={cashPrice} />;
  }

  return (
    <Box>
      {/* Toggle Button */}
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'center' }}>
        <ToggleButtonGroup
          value={displayMode}
          exclusive
          onChange={onToggleMode}
          size="small"
        >
          <ToggleButton value="cash">
            <AttachMoney fontSize="small" sx={{ mr: 0.5 }} />
            Cash
          </ToggleButton>
          <ToggleButton value="monthly">
            <AccountBalance fontSize="small" sx={{ mr: 0.5 }} />
            Monthly
          </ToggleButton>
        </ToggleButtonGroup>
      </Box>

      {/* Price Display */}
      {displayMode === 'cash' ? (
        <Box>
          <PriceDisplay price={cashPrice} />
          {monthlyPayment && (
            <Typography variant="body2" color="text.secondary">
              or ${monthlyPayment.toLocaleString()}/month
            </Typography>
          )}
        </Box>
      ) : (
        <MonthlyPaymentDisplay
          monthlyPayment={monthlyPayment}
          cashPrice={cashPrice}
          loanTerm={loanTerm}
          totalCost={totalCost}
        />
      )}
    </Box>
  );
};
