import React from 'react';
import { render, renderHook, act, waitFor } from '@testing-library/react';
import { StepperProvider, useStepper, STEPS } from '../StepperProvider';
import { useRouter, usePathname } from 'next/navigation';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  usePathname: jest.fn(),
}));

describe('StepperProvider', () => {
  let mockRouter: any;
  let mockPush: jest.Mock;

  beforeEach(() => {
    // Clear sessionStorage
    sessionStorage.clear();
    
    // Setup router mock
    mockPush = jest.fn();
    mockRouter = {
      push: mockPush,
      back: jest.fn(),
    };
    (useRouter as jest.Mock).mockReturnValue(mockRouter);
    (usePathname as jest.Mock).mockReturnValue('/dashboard/search');
    
    jest.clearAllMocks();
  });

  afterEach(() => {
    sessionStorage.clear();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <StepperProvider>{children}</StepperProvider>
  );

  describe('Query Parameter Preservation', () => {
    it('should preserve query parameters when completing a step', () => {
      const { result } = renderHook(() => useStepper(), { wrapper });

      act(() => {
        result.current.completeStep(0, {
          searchParams: { make: 'Toyota', model: 'Camry' },
          queryString: 'make=Toyota&model=Camry&budgetMax=30000',
        });
      });

      const stepData = result.current.getStepData(0);
      expect(stepData).toHaveProperty('queryString');
      expect((stepData as any).queryString).toBe('make=Toyota&model=Camry&budgetMax=30000');
    });

    it('should restore query parameters when navigating back to a completed step', async () => {
      const { result } = renderHook(() => useStepper(), { wrapper });

      // Complete step 0 with query params
      act(() => {
        result.current.completeStep(0, {
          searchParams: { make: 'Toyota', model: 'Camry' },
          queryString: 'make=Toyota&model=Camry&budgetMax=30000',
        });
      });

      // Complete step 1 with different query params (vehicle-specific)
      act(() => {
        result.current.completeStep(1, {
          queryString: 'vin=ABC123&make=Toyota&model=Camry&year=2020&price=25000',
          vehicles: [],
        });
      });

      // Navigate back to step 0
      act(() => {
        result.current.navigateToStep(0);
      });

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalled();
      });

      // Check that the router was called with the correct URL including query params
      expect(mockPush).toHaveBeenCalledWith(
        '/dashboard/search?make=Toyota&model=Camry&budgetMax=30000'
      );
    });

    it('should restore query parameters when navigating back from step 3 to step 2', async () => {
      const { result } = renderHook(() => useStepper(), { wrapper });

      // Complete steps in sequence
      act(() => {
        result.current.completeStep(0, {
          queryString: 'make=Toyota&model=Camry&budgetMax=30000',
        });
      });

      act(() => {
        result.current.completeStep(1, {
          queryString: 'vin=ABC123&make=Toyota&model=Camry&year=2020&price=25000&mileage=30000',
        });
      });

      act(() => {
        result.current.completeStep(2, {
          queryString: 'vin=ABC123&make=Toyota&model=Camry&year=2020&price=25000&mileage=30000&fuelType=Gasoline',
          evaluation: { score: 8.5 },
        });
      });

      act(() => {
        result.current.completeStep(3, {
          queryString: 'vin=ABC123&make=Toyota&model=Camry&year=2020&price=24000&mileage=30000&dealId=123',
        });
      });

      // Navigate back to step 2 (evaluation)
      act(() => {
        result.current.navigateToStep(2);
      });

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalled();
      });

      // Check that the router was called with the correct URL including query params
      expect(mockPush).toHaveBeenCalledWith(
        '/dashboard/evaluation?vin=ABC123&make=Toyota&model=Camry&year=2020&price=25000&mileage=30000&fuelType=Gasoline'
      );
    });

    it('should handle navigation when query parameters are missing', async () => {
      const { result } = renderHook(() => useStepper(), { wrapper });

      // Complete step without query string
      act(() => {
        result.current.completeStep(0, {
          searchParams: { make: 'Toyota' },
        });
      });

      // Navigate to step 0
      act(() => {
        result.current.navigateToStep(0);
      });

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalled();
      });

      // Should navigate to the base path without query params
      expect(mockPush).toHaveBeenCalledWith('/dashboard/search');
    });

    it('should persist step data across sessions', () => {
      const { result: result1 } = renderHook(() => useStepper(), { wrapper });

      // Complete step with query params
      act(() => {
        result1.current.completeStep(1, {
          queryString: 'vin=ABC123&make=Toyota&model=Camry&year=2020&price=25000',
          vehicles: [{ make: 'Toyota', model: 'Camry' }],
        });
      });

      // Create a new instance (simulating page refresh or remount)
      const { result: result2 } = renderHook(() => useStepper(), { wrapper });

      // Check that the data persisted
      const stepData = result2.current.getStepData(1);
      expect(stepData).toHaveProperty('queryString');
      expect((stepData as any).queryString).toBe('vin=ABC123&make=Toyota&model=Camry&year=2020&price=25000');
    });
  });

  describe('Step Navigation', () => {
    it('should allow navigation to completed steps', () => {
      const { result } = renderHook(() => useStepper(), { wrapper });

      act(() => {
        result.current.completeStep(0, { queryString: 'make=Toyota' });
        result.current.completeStep(1, { queryString: 'vin=ABC123' });
      });

      expect(result.current.canNavigateToStep(0)).toBe(true);
      expect(result.current.canNavigateToStep(1)).toBe(true);
      expect(result.current.canNavigateToStep(2)).toBe(true); // Can navigate to next step after completing previous
    });

    it('should not allow navigation to steps that require previous steps', () => {
      const { result } = renderHook(() => useStepper(), { wrapper });

      // Only complete step 0
      act(() => {
        result.current.completeStep(0, { queryString: 'make=Toyota' });
      });

      expect(result.current.canNavigateToStep(2)).toBe(false);
      expect(result.current.canNavigateToStep(3)).toBe(false);
    });
  });

  describe('Edge Cases', () => {
    it('should handle invalid step data gracefully', async () => {
      const { result } = renderHook(() => useStepper(), { wrapper });

      // Complete prerequisite steps first
      act(() => {
        result.current.completeStep(0, { queryString: 'make=Toyota' });
      });

      // Set invalid step data
      act(() => {
        result.current.setStepData(1, null);
      });

      // Try to navigate to that step
      act(() => {
        result.current.completeStep(1, {});
        result.current.navigateToStep(1);
      });

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalled();
      });

      // Should still navigate but without query params
      expect(mockPush).toHaveBeenCalledWith('/dashboard/results');
    });

    it('should handle empty query strings', async () => {
      const { result } = renderHook(() => useStepper(), { wrapper });

      // Complete prerequisite steps first
      act(() => {
        result.current.completeStep(0, { queryString: 'make=Toyota' });
      });

      act(() => {
        result.current.completeStep(1, { queryString: '' });
        result.current.navigateToStep(1);
      });

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalled();
      });

      // Should navigate without query params when query string is empty
      expect(mockPush).toHaveBeenCalledWith('/dashboard/results');
    });
  });
});
