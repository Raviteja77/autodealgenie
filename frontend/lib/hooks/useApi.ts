'use client';

import { useState, useCallback, useMemo } from 'react';
import { getUserFriendlyErrorMessage } from '../errors';

interface UseApiOptions<T> {
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
}

/**
 * Custom hook for handling API requests with loading and error states
 * 
 * @example
 * ```tsx
 * const { data, isLoading, error, execute } = useApi<Deal[]>({
 *   onSuccess: (data) => console.log('Success!', data),
 *   onError: (error) => console.error('Error:', error),
 * });
 * 
 * const handleClick = async () => {
 *   await execute(() => apiClient.getDeals());
 * };
 * ```
 */
export function useApi<T = unknown>(options?: UseApiOptions<T>) {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Memoize callbacks to prevent unnecessary re-renders
  const onSuccess = useMemo(() => options?.onSuccess, [options?.onSuccess]);
  const onError = useMemo(() => options?.onError, [options?.onError]);

  const execute = useCallback(
    async (apiCall: () => Promise<T>) => {
      setIsLoading(true);
      setError(null);

      try {
        const result = await apiCall();
        setData(result);
        onSuccess?.(result);
        return result;
      } catch (err) {
        const error = err instanceof Error ? err : new Error('An unknown error occurred');
        setError(error);
        onError?.(error);
        throw error;
      } finally {
        setIsLoading(false);
      }
    },
    [onSuccess, onError]
  );

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setIsLoading(false);
  }, []);

  return {
    data,
    isLoading,
    error,
    errorMessage: error ? getUserFriendlyErrorMessage(error) : null,
    execute,
    reset,
  };
}
