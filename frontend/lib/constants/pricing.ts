/**
 * Pricing Constants
 * 
 * Centralizes all numeric constants related to pricing, taxes, fees, and financial calculations.
 * These values should be configurable and easily maintainable.
 */

/**
 * Tax Rates
 */
export const TAX_RATES = {
  /** Default sales tax rate (8%) */
  DEFAULT: 0.08,
  /** State-specific tax rates can be added here */
  STATES: {
    CA: 0.0725, // California
    TX: 0.0625, // Texas
    NY: 0.08, // New York
    FL: 0.06, // Florida
    // Add more states as needed
  },
} as const;

/**
 * Standard Fees
 */
export const FEES = {
  /** Vehicle registration fee */
  REGISTRATION: 300,
  /** Documentation and processing fee */
  DOCUMENTATION: 150,
  /** Title transfer fee */
  TITLE_TRANSFER: 75,
  /** Dealer preparation fee */
  DEALER_PREP: 500,
} as const;

/**
 * Financial Defaults
 */
export const FINANCIAL_DEFAULTS = {
  /** Default down payment percentage (20%) */
  DOWN_PAYMENT_PERCENT: 0.2,
  /** Default loan term in months */
  LOAN_TERM_MONTHS: 60,
  /** Default annual percentage rate (APR) for financing */
  DEFAULT_APR: 0.05,
  /** Default driver age for insurance calculations */
  DRIVER_AGE: 30,
} as const;

/**
 * Price Thresholds
 */
export const PRICE_THRESHOLDS = {
  /** Minimum vehicle price for financing eligibility */
  MIN_FINANCED_AMOUNT: 5000,
  /** Maximum vehicle price in the system */
  MAX_VEHICLE_PRICE: 500000,
  /** Minimum down payment amount */
  MIN_DOWN_PAYMENT: 1000,
} as const;

/**
 * Negotiation Constants
 */
export const NEGOTIATION = {
  /** Maximum number of negotiation rounds */
  MAX_ROUNDS: 10,
  /** Minimum price reduction per counter offer (5%) */
  MIN_PRICE_REDUCTION_PERCENT: 0.05,
  /** Maximum price reduction per counter offer (15%) */
  MAX_PRICE_REDUCTION_PERCENT: 0.15,
} as const;

/**
 * Insurance Premiums (Example values)
 */
export const INSURANCE_PREMIUMS = {
  /** Base monthly premium multiplier by vehicle value */
  BASE_RATE_MULTIPLIER: 0.01,
  /** Liability coverage minimum monthly premium */
  LIABILITY_MIN: 50,
  /** Comprehensive coverage minimum monthly premium */
  COMPREHENSIVE_MIN: 100,
  /** Full coverage minimum monthly premium */
  FULL_COVERAGE_MIN: 150,
} as const;

/**
 * Helper function to calculate sales tax
 */
export function calculateSalesTax(
  price: number,
  stateCode?: string
): number {
  const rate = stateCode && stateCode in TAX_RATES.STATES
    ? TAX_RATES.STATES[stateCode as keyof typeof TAX_RATES.STATES]
    : TAX_RATES.DEFAULT;
  return price * rate;
}

/**
 * Helper function to calculate total fees
 */
export function calculateTotalFees(): number {
  return (
    FEES.REGISTRATION +
    FEES.DOCUMENTATION +
    FEES.TITLE_TRANSFER +
    FEES.DEALER_PREP
  );
}

/**
 * Helper function to calculate monthly payment
 */
export function calculateMonthlyPayment(
  principal: number,
  annualRate: number,
  termMonths: number
): number {
  const monthlyRate = annualRate / 12;
  if (monthlyRate === 0) return principal / termMonths;
  
  return (
    (principal * monthlyRate * Math.pow(1 + monthlyRate, termMonths)) /
    (Math.pow(1 + monthlyRate, termMonths) - 1)
  );
}
