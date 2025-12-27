/**
 * Custom hook for vehicle financing calculations
 */

import { useMemo } from 'react';

export interface FinancingParams {
  downPayment: number;
  loanTerm: number; // in months
  creditScore: 'excellent' | 'good' | 'fair' | 'poor';
  interestRate?: number;
}

export interface PaymentCalculation {
  monthlyPayment: number;
  totalCost: number;
  totalInterest: number;
  effectiveInterestRate: number;
}

// Default interest rates based on credit score
const INTEREST_RATES = {
  excellent: 0.039, // 3.9%
  good: 0.059, // 5.9%
  fair: 0.089, // 8.9%
  poor: 0.129, // 12.9%
};

/**
 * Calculate monthly payment for a vehicle loan
 * Uses the standard loan amortization formula
 */
function calculateMonthlyPayment(
  principal: number,
  monthlyRate: number,
  term: number
): number {
  if (term <= 0 || principal <= 0) {
    return 0;
  }

  // Handle zero interest rate
  if (monthlyRate === 0) {
    return Math.round(principal / term);
  }

  const denominator = Math.pow(1 + monthlyRate, term) - 1;
  
  // Additional safety check
  if (denominator === 0) {
    return Math.round(principal / term);
  }

  const payment =
    (principal * monthlyRate * Math.pow(1 + monthlyRate, term)) / denominator;

  return Math.round(payment);
}

/**
 * Hook for calculating vehicle financing payments
 * @param vehiclePrice - The price of the vehicle
 * @param financingParams - Financing parameters (down payment, loan term, credit score)
 * @returns Payment calculation details
 */
export function useFinancingCalculation(
  vehiclePrice: number,
  financingParams?: FinancingParams
): PaymentCalculation | null {
  return useMemo(() => {
    if (!financingParams) {
      return null;
    }

    const { downPayment, loanTerm, creditScore, interestRate } = financingParams;
    
    // Use provided interest rate or default based on credit score
    const rate = interestRate ?? INTEREST_RATES[creditScore];
    const principal = vehiclePrice - downPayment;
    const monthlyRate = rate / 12;

    const monthlyPayment = calculateMonthlyPayment(principal, monthlyRate, loanTerm);
    const totalCost = monthlyPayment * loanTerm + downPayment;
    const totalInterest = totalCost - vehiclePrice;

    return {
      monthlyPayment,
      totalCost,
      totalInterest,
      effectiveInterestRate: rate,
    };
  }, [vehiclePrice, financingParams]);
}

/**
 * Hook for determining vehicle affordability
 * @param vehiclePrice - The price of the vehicle
 * @param budgetMax - Maximum budget
 * @param monthlyPayment - Optional monthly payment to check
 * @param monthlyBudget - Optional monthly budget limit
 * @returns Affordability information
 */
export function useAffordability(
  vehiclePrice: number,
  budgetMax?: number,
  monthlyPayment?: number,
  monthlyBudget?: number
) {
  return useMemo(() => {
    const isAffordable = budgetMax ? vehiclePrice <= budgetMax : true;
    const monthlyAffordable =
      monthlyBudget && monthlyPayment 
        ? monthlyPayment <= monthlyBudget 
        : monthlyBudget === undefined || monthlyPayment === undefined;
    
    const overBudgetAmount = budgetMax && !isAffordable 
      ? vehiclePrice - budgetMax 
      : 0;

    const overMonthlyBudget = monthlyBudget && monthlyPayment && !monthlyAffordable
      ? monthlyPayment - monthlyBudget
      : 0;

    return {
      isAffordable,
      monthlyAffordable,
      overBudgetAmount,
      overMonthlyBudget,
      withinBudget: isAffordable && monthlyAffordable,
    };
  }, [vehiclePrice, budgetMax, monthlyPayment, monthlyBudget]);
}
