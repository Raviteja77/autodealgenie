/**
 * URL Parameter Utilities
 * 
 * Helper functions for parsing and validating URL search parameters.
 * Centralizes duplicate URL parsing logic from dashboard pages.
 */

import { QUERY_PARAMS, DEFAULT_VIN, FUEL_TYPE } from "@/lib/constants";

/**
 * Vehicle information interface
 */
export interface VehicleFromParams {
  vin?: string;
  make: string;
  model: string;
  year: number;
  price: number;
  mileage: number;
  fuelType?: string;
  condition?: string;
  zipCode?: string;
  dealId?: string;
}

/**
 * Parse vehicle information from URL search parameters
 * 
 * @param searchParams - Next.js useSearchParams hook result
 * @param options - Parsing options
 * @returns Parsed vehicle data or null if required fields are missing
 * 
 * @example
 * const vehicleData = parseVehicleFromParams(searchParams);
 * if (vehicleData) {
 *   // Use vehicle data
 * }
 */
export function parseVehicleFromParams(
  searchParams: URLSearchParams | ReadonlyURLSearchParams,
  options: {
    useDefaultVin?: boolean;
    requireVin?: boolean;
  } = {}
): VehicleFromParams | null {
  const { useDefaultVin = false, requireVin = false } = options;

  try {
    // Extract parameters
    const vin = searchParams.get(QUERY_PARAMS.VIN);
    const make = searchParams.get(QUERY_PARAMS.MAKE);
    const model = searchParams.get(QUERY_PARAMS.MODEL);
    const yearStr = searchParams.get(QUERY_PARAMS.YEAR);
    const priceStr = searchParams.get(QUERY_PARAMS.PRICE);
    const mileageStr = searchParams.get(QUERY_PARAMS.MILEAGE);
    const fuelType = searchParams.get(QUERY_PARAMS.FUEL_TYPE);
    const condition = searchParams.get(QUERY_PARAMS.CONDITION);
    const zipCode = searchParams.get(QUERY_PARAMS.ZIP_CODE);
    const dealId = searchParams.get(QUERY_PARAMS.DEAL_ID);

    // Validate required fields
    if (!make || !model || !yearStr || !priceStr || !mileageStr) {
      return null;
    }

    if (requireVin && !vin) {
      return null;
    }

    // Parse numeric values
    const year = parseInt(yearStr, 10);
    const price = parseFloat(priceStr);
    const mileage = parseInt(mileageStr, 10);

    // Validate parsed values
    if (isNaN(year) || isNaN(price) || isNaN(mileage)) {
      return null;
    }

    // Build result
    const result: VehicleFromParams = {
      make,
      model,
      year,
      price,
      mileage,
    };

    // Optional fields
    if (vin) {
      result.vin = vin;
    } else if (useDefaultVin) {
      result.vin = DEFAULT_VIN;
    }

    if (fuelType) {
      result.fuelType = fuelType;
    } else {
      result.fuelType = FUEL_TYPE.DEFAULT;
    }

    if (condition) result.condition = condition;
    if (zipCode) result.zipCode = zipCode;
    if (dealId) result.dealId = dealId;

    return result;
  } catch (error) {
    console.error("Error parsing vehicle from params:", error);
    return null;
  }
}

/**
 * Parse a string parameter with fallback
 */
export function parseStringParam(
  searchParams: URLSearchParams | ReadonlyURLSearchParams,
  key: string,
  fallback?: string
): string | undefined {
  const value = searchParams.get(key);
  return value || fallback;
}

/**
 * Parse a numeric parameter with validation
 */
export function parseNumericParam(
  searchParams: URLSearchParams | ReadonlyURLSearchParams,
  key: string,
  fallback?: number
): number | undefined {
  const value = searchParams.get(key);
  if (!value) return fallback;

  const parsed = parseFloat(value);
  return isNaN(parsed) ? fallback : parsed;
}

/**
 * Parse an integer parameter with validation
 */
export function parseIntParam(
  searchParams: URLSearchParams | ReadonlyURLSearchParams,
  key: string,
  fallback?: number
): number | undefined {
  const value = searchParams.get(key);
  if (!value) return fallback;

  const parsed = parseInt(value, 10);
  return isNaN(parsed) ? fallback : parsed;
}

/**
 * Parse a boolean parameter
 */
export function parseBooleanParam(
  searchParams: URLSearchParams | ReadonlyURLSearchParams,
  key: string,
  fallback: boolean = false
): boolean {
  const value = searchParams.get(key);
  if (!value) return fallback;

  return value === "true" || value === "1";
}

/**
 * Build URLSearchParams from an object
 */
export function buildSearchParams(params: Record<string, string | number | boolean | undefined | null>): URLSearchParams {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      searchParams.set(key, value.toString());
    }
  });

  return searchParams;
}

/**
 * Merge existing search params with new params
 */
export function mergeSearchParams(
  existing: URLSearchParams | ReadonlyURLSearchParams,
  updates: Record<string, string | number | boolean | undefined | null>
): URLSearchParams {
  const merged = new URLSearchParams(existing.toString());

  Object.entries(updates).forEach(([key, value]) => {
    if (value === undefined || value === null) {
      merged.delete(key);
    } else {
      merged.set(key, value.toString());
    }
  });

  return merged;
}

/**
 * Extract multiple query parameters as an object
 */
export function extractParams<T extends Record<string, string | number>>(
  searchParams: URLSearchParams | ReadonlyURLSearchParams,
  keys: readonly string[]
): Partial<T> {
  const result: Partial<T> = {};

  keys.forEach((key) => {
    const value = searchParams.get(key);
    if (value !== null) {
      result[key as keyof T] = value as T[keyof T];
    }
  });

  return result;
}
