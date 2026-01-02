/**
 * useVehicleFromParams Hook
 * 
 * Parses vehicle information from URL search parameters.
 * Centralizes the common pattern of extracting vehicle data from URLs
 * used across evaluation, negotiation, and finalize pages.
 */

import { useMemo } from "react";
import { useSearchParams } from "next/navigation";
import { parseVehicleFromParams, type VehicleFromParams } from "@/lib/utils/urlParams";

export interface UseVehicleFromParamsOptions {
  /**
   * Use a default VIN if not provided in params
   * @default false
   */
  useDefaultVin?: boolean;

  /**
   * Require VIN to be present
   * @default false
   */
  requireVin?: boolean;

  /**
   * Callback when vehicle data changes
   */
  onVehicleChange?: (vehicle: VehicleFromParams | null) => void;
}

export interface UseVehicleFromParamsReturn {
  /**
   * Parsed vehicle data or null if required fields are missing
   */
  vehicle: VehicleFromParams | null;

  /**
   * Whether the vehicle data is valid
   */
  isValid: boolean;

  /**
   * Error message if vehicle data is invalid
   */
  error: string | null;
}

/**
 * Hook to parse vehicle information from URL search parameters
 * 
 * @example
 * const { vehicle, isValid, error } = useVehicleFromParams({
 *   useDefaultVin: true
 * });
 * 
 * if (!isValid) {
 *   return <Error message={error} />;
 * }
 * 
 * return <VehicleDetails vehicle={vehicle} />;
 */
export function useVehicleFromParams(
  options: UseVehicleFromParamsOptions = {}
): UseVehicleFromParamsReturn {
  const searchParams = useSearchParams();
  const { useDefaultVin = false, requireVin = false, onVehicleChange } = options;

  const vehicle = useMemo(() => {
    return parseVehicleFromParams(searchParams, { useDefaultVin, requireVin });
  }, [searchParams, useDefaultVin, requireVin]);

  const isValid = vehicle !== null;

  const error = useMemo(() => {
    if (vehicle) return null;

    // Determine what's missing
    const make = searchParams.get("make");
    const model = searchParams.get("model");
    const year = searchParams.get("year");
    const price = searchParams.get("price");
    const mileage = searchParams.get("mileage");
    const vin = searchParams.get("vin");

    if (!make || !model || !year || !price || !mileage) {
      return "Missing required vehicle information. Please select a vehicle from the results page.";
    }

    if (requireVin && !vin) {
      return "Vehicle VIN is required but not provided.";
    }

    return "Invalid vehicle data in URL parameters.";
  }, [vehicle, searchParams, requireVin]);

  // Call onVehicleChange when vehicle changes
  useMemo(() => {
    if (onVehicleChange) {
      onVehicleChange(vehicle);
    }
  }, [vehicle, onVehicleChange]);

  return {
    vehicle,
    isValid,
    error,
  };
}
