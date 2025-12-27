/**
 * Type definitions for Price Display molecules
 */

export interface PriceDisplayProps {
  price: number;
  label?: string;
  size?: 'sm' | 'md' | 'lg';
  showCurrency?: boolean;
  color?: 'primary' | 'secondary' | 'success' | 'error' | 'text';
}

export interface MonthlyPaymentDisplayProps {
  monthlyPayment: number;
  cashPrice: number;
  loanTerm?: number;
  totalCost?: number;
  size?: 'sm' | 'md' | 'lg';
}

export interface PriceSwitcherProps {
  cashPrice: number;
  monthlyPayment: number | null;
  displayMode: 'cash' | 'monthly';
  onToggleMode: () => void;
  loanTerm?: number;
  totalCost?: number | null;
}
