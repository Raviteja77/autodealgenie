/**
 * Vehicle Constants
 * 
 * Centralizes vehicle-related constants including year ranges,
 * mileage limits, fuel types, and other vehicle specifications.
 */

/**
 * Vehicle Year Range
 */
export const VEHICLE_YEAR = {
  MIN: 2015,
  MAX: 2025,
  DEFAULT_MIN: 2015,
  DEFAULT_MAX: 2025,
} as const;

/**
 * Mileage Limits
 */
export const MILEAGE = {
  MIN: 0,
  MAX: 200000,
  DEFAULT_MAX: 100000,
  LOW: 30000,
  MEDIUM: 60000,
  HIGH: 100000,
} as const;

/**
 * Search Results
 */
export const SEARCH_RESULTS = {
  DEFAULT_MAX: 50,
  MIN: 10,
  MAX: 100,
} as const;

/**
 * Search Radius (in miles)
 */
export const SEARCH_RADIUS = {
  DEFAULT: 50,
  MIN: 10,
  MAX: 500,
  OPTIONS: [10, 25, 50, 100, 200, 500] as const,
} as const;

/**
 * Fuel Types
 */
export const FUEL_TYPE = {
  GASOLINE: "Gasoline",
  DIESEL: "Diesel",
  ELECTRIC: "Electric",
  HYBRID: "Hybrid",
  PLUG_IN_HYBRID: "Plug-in Hybrid",
  UNKNOWN: "Unknown",
  DEFAULT: "Unknown",
} as const;

export type FuelType = typeof FUEL_TYPE[keyof typeof FUEL_TYPE];

/**
 * Vehicle Condition
 */
export const VEHICLE_CONDITION = {
  NEW: "new",
  EXCELLENT: "excellent",
  GOOD: "good",
  FAIR: "fair",
  POOR: "poor",
  DEFAULT: "good",
} as const;

export type VehicleCondition = typeof VEHICLE_CONDITION[keyof typeof VEHICLE_CONDITION];

/**
 * Transmission Types
 */
export const TRANSMISSION = {
  AUTOMATIC: "Automatic",
  MANUAL: "Manual",
  CVT: "CVT",
  UNKNOWN: "Unknown",
} as const;

/**
 * Drivetrain Types
 */
export const DRIVETRAIN = {
  FWD: "FWD",
  RWD: "RWD",
  AWD: "AWD",
  FOUR_WD: "4WD",
  UNKNOWN: "Unknown",
} as const;

/**
 * Body Types
 */
export const BODY_TYPE = {
  SEDAN: "Sedan",
  SUV: "SUV",
  TRUCK: "Truck",
  COUPE: "Coupe",
  CONVERTIBLE: "Convertible",
  HATCHBACK: "Hatchback",
  WAGON: "Wagon",
  VAN: "Van",
  MINIVAN: "Minivan",
} as const;

/**
 * Default VIN for unknown vehicles
 */
export const DEFAULT_VIN = "UNKNOWN00000000000";

/**
 * Helper function to determine mileage category
 */
export function getMileageCategory(mileage: number): "low" | "medium" | "high" | "very high" {
  if (mileage <= MILEAGE.LOW) return "low";
  if (mileage <= MILEAGE.MEDIUM) return "medium";
  if (mileage <= MILEAGE.HIGH) return "high";
  return "very high";
}

/**
 * Helper function to validate year
 */
export function isValidYear(year: number): boolean {
  return year >= VEHICLE_YEAR.MIN && year <= VEHICLE_YEAR.MAX;
}

/**
 * Helper function to validate mileage
 */
export function isValidMileage(mileage: number): boolean {
  return mileage >= MILEAGE.MIN && mileage <= MILEAGE.MAX;
}
