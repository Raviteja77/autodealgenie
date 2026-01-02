/**
 * useFetchOnce Hook
 * 
 * Prevents duplicate API calls by using a ref to track fetch status.
 * This is a common pattern across dashboard pages to prevent race conditions
 * and duplicate API calls during React's strict mode or rapid re-renders.
 */

import { useRef, useCallback, useEffect } from "react";

export interface UseFetchOnceOptions {
  /**
   * Whether to reset the fetch status when dependencies change
   * @default false
   */
  resetOnDepsChange?: boolean;

  /**
   * Dependencies to watch for changes (if resetOnDepsChange is true)
   */
  deps?: unknown[];
}

export interface UseFetchOnceReturn {
  /**
   * Whether a fetch has been completed
   */
  hasFetched: boolean;

  /**
   * Whether a fetch is currently in progress
   */
  isFetching: boolean;

  /**
   * Wraps an async fetch function with duplicate prevention logic
   */
  executeFetch: <T>(fn: () => Promise<T>) => Promise<T | null>;

  /**
   * Manually reset the fetch status
   */
  reset: () => void;

  /**
   * Check if fetch should be executed (convenience method)
   */
  shouldFetch: () => boolean;
}

/**
 * Custom hook to prevent duplicate API calls
 * 
 * @example
 * const { executeFetch, shouldFetch } = useFetchOnce();
 * 
 * useEffect(() => {
 *   if (!shouldFetch()) return;
 *   
 *   executeFetch(async () => {
 *     const data = await apiClient.getVehicles();
 *     setVehicles(data);
 *   });
 * }, []);
 */
export function useFetchOnce(options: UseFetchOnceOptions = {}): UseFetchOnceReturn {
  const { resetOnDepsChange = false, deps = [] } = options;

  const hasFetchedRef = useRef(false);
  const isFetchingRef = useRef(false);

  // Reset on deps change if requested
  useEffect(() => {
    if (resetOnDepsChange) {
      hasFetchedRef.current = false;
      isFetchingRef.current = false;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  const reset = useCallback(() => {
    hasFetchedRef.current = false;
    isFetchingRef.current = false;
  }, []);

  const shouldFetch = useCallback(() => {
    return !hasFetchedRef.current && !isFetchingRef.current;
  }, []);

  const executeFetch = useCallback(async <T,>(fn: () => Promise<T>): Promise<T | null> => {
    // Guard: already fetched or currently fetching
    if (hasFetchedRef.current || isFetchingRef.current) {
      return null;
    }

    try {
      isFetchingRef.current = true;
      const result = await fn();
      hasFetchedRef.current = true;
      return result;
    } catch (error) {
      // On error, don't mark as fetched to allow retry
      console.error("Fetch error:", error);
      throw error;
    } finally {
      isFetchingRef.current = false;
    }
  }, []);

  return {
    hasFetched: hasFetchedRef.current,
    isFetching: isFetchingRef.current,
    executeFetch,
    reset,
    shouldFetch,
  };
}

/**
 * Alternative hook using useState for reactive fetch status
 * Use this if you need the fetch status to trigger re-renders
 */
export function useFetchOnceReactive(options: UseFetchOnceOptions = {}) {
  const { resetOnDepsChange = false, deps = [] } = options;
  
  const [hasFetched, setHasFetched] = React.useState(false);
  const [isFetching, setIsFetching] = React.useState(false);
  const fetchingRef = useRef(false);

  useEffect(() => {
    if (resetOnDepsChange) {
      setHasFetched(false);
      setIsFetching(false);
      fetchingRef.current = false;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  const reset = useCallback(() => {
    setHasFetched(false);
    setIsFetching(false);
    fetchingRef.current = false;
  }, []);

  const shouldFetch = useCallback(() => {
    return !hasFetched && !fetchingRef.current;
  }, [hasFetched]);

  const executeFetch = useCallback(
    async <T,>(fn: () => Promise<T>): Promise<T | null> => {
      if (hasFetched || fetchingRef.current) {
        return null;
      }

      try {
        fetchingRef.current = true;
        setIsFetching(true);
        const result = await fn();
        setHasFetched(true);
        return result;
      } catch (error) {
        console.error("Fetch error:", error);
        throw error;
      } finally {
        fetchingRef.current = false;
        setIsFetching(false);
      }
    },
    [hasFetched]
  );

  return {
    hasFetched,
    isFetching,
    executeFetch,
    reset,
    shouldFetch,
  };
}

// Fix React import for reactive hook
import * as React from "react";
