/**
 * useQueryParams Hook
 * 
 * Type-safe hook for working with URL query parameters.
 * Provides helpers for parsing, updating, and managing query parameters.
 */

import { useSearchParams, useRouter, ReadonlyURLSearchParams } from "next/navigation";
import { useCallback } from "react";
import {
  parseStringParam,
  parseNumericParam,
  parseIntParam,
  parseBooleanParam,
  buildSearchParams,
  mergeSearchParams,
} from "@/lib/utils/urlParams";

export interface UseQueryParamsReturn {
  /**
   * Raw search params object
   */
  searchParams: URLSearchParams | ReadonlyURLSearchParams;

  /**
   * Get a string parameter
   */
  getString: (key: string, fallback?: string) => string | undefined;

  /**
   * Get a numeric parameter
   */
  getNumber: (key: string, fallback?: number) => number | undefined;

  /**
   * Get an integer parameter
   */
  getInt: (key: string, fallback?: number) => number | undefined;

  /**
   * Get a boolean parameter
   */
  getBoolean: (key: string, fallback?: boolean) => boolean;

  /**
   * Update query parameters (navigates to new URL)
   */
  updateParams: (params: Record<string, string | number | boolean | undefined | null>) => void;

  /**
   * Set multiple query parameters at once
   */
  setParams: (params: Record<string, string | number | boolean | undefined | null>) => void;

  /**
   * Remove a query parameter
   */
  removeParam: (key: string) => void;

  /**
   * Clear all query parameters
   */
  clearParams: () => void;

  /**
   * Get current query string
   */
  getQueryString: () => string;
}

/**
 * Hook for type-safe query parameter management
 * 
 * @example
 * const { getString, getNumber, updateParams } = useQueryParams();
 * 
 * const make = getString('make', 'Toyota');
 * const price = getNumber('price', 25000);
 * 
 * updateParams({ make: 'Honda', price: 30000 });
 */
export function useQueryParams(): UseQueryParamsReturn {
  const searchParams = useSearchParams();
  const router = useRouter();

  const getString = useCallback(
    (key: string, fallback?: string) => {
      return parseStringParam(searchParams, key, fallback);
    },
    [searchParams]
  );

  const getNumber = useCallback(
    (key: string, fallback?: number) => {
      return parseNumericParam(searchParams, key, fallback);
    },
    [searchParams]
  );

  const getInt = useCallback(
    (key: string, fallback?: number) => {
      return parseIntParam(searchParams, key, fallback);
    },
    [searchParams]
  );

  const getBoolean = useCallback(
    (key: string, fallback: boolean = false) => {
      return parseBooleanParam(searchParams, key, fallback);
    },
    [searchParams]
  );

  const updateParams = useCallback(
    (params: Record<string, string | number | boolean | undefined | null>) => {
      const merged = mergeSearchParams(searchParams, params);
      router.push(`?${merged.toString()}`);
    },
    [searchParams, router]
  );

  const setParams = useCallback(
    (params: Record<string, string | number | boolean | undefined | null>) => {
      const newParams = buildSearchParams(params);
      router.push(`?${newParams.toString()}`);
    },
    [router]
  );

  const removeParam = useCallback(
    (key: string) => {
      const merged = new URLSearchParams(searchParams.toString());
      merged.delete(key);
      router.push(`?${merged.toString()}`);
    },
    [searchParams, router]
  );

  const clearParams = useCallback(() => {
    router.push(window.location.pathname);
  }, [router]);

  const getQueryString = useCallback(() => {
    return searchParams.toString();
  }, [searchParams]);

  return {
    searchParams,
    getString,
    getNumber,
    getInt,
    getBoolean,
    updateParams,
    setParams,
    removeParam,
    clearParams,
    getQueryString,
  };
}
