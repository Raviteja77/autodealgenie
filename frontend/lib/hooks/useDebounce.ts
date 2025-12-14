'use client';

import { useState, useEffect } from 'react';

interface UseDebounceOptions {
  delay?: number;
}

/**
 * Custom hook to debounce a value
 * 
 * @example
 * ```tsx
 * const [searchTerm, setSearchTerm] = useState('');
 * const debouncedSearchTerm = useDebounce(searchTerm, { delay: 500 });
 * 
 * useEffect(() => {
 *   if (debouncedSearchTerm) {
 *     // Perform search
 *     searchApi(debouncedSearchTerm);
 *   }
 * }, [debouncedSearchTerm]);
 * ```
 */
export function useDebounce<T>(value: T, options?: UseDebounceOptions): T {
  const delay = options?.delay ?? 500;
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}
