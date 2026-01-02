/**
 * Financial Constants
 * 
 * Centralizes all financial-related constants including budget ranges,
 * loan terms, credit scores, interest rates, and payment calculations.
 */

/**
 * Budget and Price Ranges
 */
export const BUDGET = {
  MIN: 10000,
  MAX: 50000,
  DEFAULT_MIN: 10000,
  DEFAULT_MAX: 50000,
} as const;

/**
 * Loan Terms (in months)
 */
export const LOAN_TERM = {
  MIN: 12,
  MAX: 84,
  DEFAULT: 60,
  OPTIONS: [12, 24, 36, 48, 60, 72, 84] as const,
} as const;

/**
 * Credit Score Categories and Associated Interest Rates
 */
export const CREDIT_SCORE = {
  EXCELLENT: {
    label: "Excellent (750+)",
    value: "excellent" as const,
    interestRate: 3.5,
  },
  GOOD: {
    label: "Good (700-749)",
    value: "good" as const,
    interestRate: 5.5,
  },
  FAIR: {
    label: "Fair (650-699)",
    value: "fair" as const,
    interestRate: 8.5,
  },
  POOR: {
    label: "Poor (below 650)",
    value: "poor" as const,
    interestRate: 12.5,
  },
} as const;

export type CreditScoreValue = typeof CREDIT_SCORE[keyof typeof CREDIT_SCORE]["value"];

/**
 * Interest Rates by Credit Score
 */
export const INTEREST_RATE = {
  excellent: 3.5,
  good: 5.5,
  fair: 8.5,
  poor: 12.5,
  DEFAULT: 5.5,
} as const;

/**
 * Down Payment Constants
 */
export const DOWN_PAYMENT = {
  MIN_PERCENTAGE: 0,
  MAX_PERCENTAGE: 50,
  RECOMMENDED_PERCENTAGE: 20,
  MIN_AMOUNT: 0,
} as const;

/**
 * Negotiation Constants
 */
export const NEGOTIATION = {
  DEFAULT_TARGET_DISCOUNT_PERCENTAGE: 10, // 10% off asking price
  MIN_DISCOUNT_PERCENTAGE: 5,
  MAX_DISCOUNT_PERCENTAGE: 25,
  MAX_ROUNDS: 10,
  PRICE_TOLERANCE_PERCENTAGE: 10, // Price should not exceed asking by more than 10%
} as const;

/**
 * Deal Evaluation Score Ranges
 */
export const EVALUATION_SCORE = {
  EXCELLENT: { min: 90, label: "Excellent Deal" },
  GOOD: { min: 75, label: "Good Deal" },
  FAIR: { min: 60, label: "Fair Deal" },
  POOR: { min: 0, label: "Poor Deal" },
} as const;

/**
 * Helper function to get interest rate by credit score
 */
export function getInterestRate(creditScore: string): number {
  return INTEREST_RATE[creditScore as keyof typeof INTEREST_RATE] ?? INTEREST_RATE.DEFAULT;
}

/**
 * Helper function to calculate monthly payment
 */
export function calculateMonthlyPayment(
  principal: number,
  interestRate: number,
  loanTermMonths: number
): number {
  if (principal <= 0 || loanTermMonths <= 0) return 0;
  if (interestRate === 0) return principal / loanTermMonths;

  const monthlyRate = interestRate / 100 / 12;
  const payment =
    (principal * monthlyRate * Math.pow(1 + monthlyRate, loanTermMonths)) /
    (Math.pow(1 + monthlyRate, loanTermMonths) - 1);

  return Math.round(payment * 100) / 100;
}

/**
 * Helper function to calculate target negotiation price
 */
export function calculateTargetPrice(
  askingPrice: number,
  discountPercentage: number = NEGOTIATION.DEFAULT_TARGET_DISCOUNT_PERCENTAGE
): number {
  return askingPrice * (1 - discountPercentage / 100);
}
