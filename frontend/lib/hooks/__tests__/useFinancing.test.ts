import { renderHook, act } from '@testing-library/react';
import { useFinancingCalculation, useAffordability } from '../useFinancing';

describe('useFinancingCalculation', () => {
  it('returns null when no financing params provided', () => {
    const { result } = renderHook(() => useFinancingCalculation(25000));
    expect(result.current).toBeNull();
  });

  it('calculates monthly payment correctly', () => {
    const { result } = renderHook(() =>
      useFinancingCalculation(25000, {
        downPayment: 5000,
        loanTerm: 60,
        creditScore: 'good',
      })
    );

    expect(result.current).not.toBeNull();
    expect(result.current?.monthlyPayment).toBeGreaterThan(0);
    expect(result.current?.totalCost).toBeGreaterThan(25000);
  });

  it('handles zero down payment', () => {
    const { result } = renderHook(() =>
      useFinancingCalculation(25000, {
        downPayment: 0,
        loanTerm: 60,
        creditScore: 'good',
      })
    );

    expect(result.current?.monthlyPayment).toBeGreaterThan(0);
  });

  it('handles different credit scores', () => {
    const excellent = renderHook(() =>
      useFinancingCalculation(25000, {
        downPayment: 5000,
        loanTerm: 60,
        creditScore: 'excellent',
      })
    );

    const poor = renderHook(() =>
      useFinancingCalculation(25000, {
        downPayment: 5000,
        loanTerm: 60,
        creditScore: 'poor',
      })
    );

    expect(excellent.result.current?.monthlyPayment).toBeLessThan(
      poor.result.current?.monthlyPayment ?? 0
    );
  });

  it('calculates total interest correctly', () => {
    const { result } = renderHook(() =>
      useFinancingCalculation(25000, {
        downPayment: 5000,
        loanTerm: 60,
        creditScore: 'good',
      })
    );

    expect(result.current?.totalInterest).toBeGreaterThan(0);
    expect(result.current?.totalCost).toBe(
      (result.current?.monthlyPayment ?? 0) * 60 + 5000
    );
  });
});

describe('useAffordability', () => {
  it('returns affordable when no budget provided', () => {
    const { result } = renderHook(() => useAffordability(25000));
    
    expect(result.current.isAffordable).toBe(true);
    expect(result.current.withinBudget).toBe(true);
  });

  it('correctly determines affordability', () => {
    const { result } = renderHook(() => useAffordability(25000, 30000));
    
    expect(result.current.isAffordable).toBe(true);
    expect(result.current.overBudgetAmount).toBe(0);
  });

  it('correctly determines non-affordability', () => {
    const { result } = renderHook(() => useAffordability(25000, 20000));
    
    expect(result.current.isAffordable).toBe(false);
    expect(result.current.overBudgetAmount).toBe(5000);
  });

  it('checks monthly affordability', () => {
    const { result } = renderHook(() => 
      useAffordability(25000, undefined, 500, 600)
    );
    
    expect(result.current.monthlyAffordable).toBe(true);
  });

  it('detects over monthly budget', () => {
    const { result } = renderHook(() => 
      useAffordability(25000, undefined, 700, 600)
    );
    
    expect(result.current.monthlyAffordable).toBe(false);
    expect(result.current.overMonthlyBudget).toBe(100);
  });
});
