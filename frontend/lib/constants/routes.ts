/**
 * Routes Constants
 * 
 * Centralizes all route paths and query parameter keys used throughout the application.
 */

/**
 * Dashboard Routes
 */
export const ROUTES = {
  HOME: "/",
  DASHBOARD: "/dashboard",
  SEARCH: "/dashboard/search",
  RESULTS: "/dashboard/results",
  EVALUATION: "/dashboard/evaluation",
  NEGOTIATION: "/dashboard/negotiation",
  FINALIZE: "/dashboard/finalize",
  DEALS: "/dashboard/deals",
  FAVORITES: "/dashboard/favorites",
  AUTH: {
    LOGIN: "/auth/login",
    SIGNUP: "/auth/signup",
    LOGOUT: "/auth/logout",
  },
} as const;

/**
 * Query Parameter Keys
 */
export const QUERY_PARAMS = {
  // Vehicle Information
  VIN: "vin",
  MAKE: "make",
  MODEL: "model",
  YEAR: "year",
  PRICE: "price",
  MILEAGE: "mileage",
  FUEL_TYPE: "fuelType",
  CONDITION: "condition",
  COLOR: "color",
  LOCATION: "location",
  ZIP_CODE: "zipCode",
  DEALER_NAME: "dealer_name",
  VDP_URL: "vdp_url",

  // Search Filters
  YEAR_MIN: "yearMin",
  YEAR_MAX: "yearMax",
  MILEAGE_MAX: "mileageMax",
  BUDGET_MIN: "budgetMin",
  BUDGET_MAX: "budgetMax",
  CAR_TYPE: "carType",
  BODY_TYPE: "bodyType",
  TRANSMISSION: "transmission",
  DRIVETRAIN: "drivetrain",
  SEARCH_RADIUS: "searchRadius",
  MAX_RESULTS: "maxResults",

  // Financing
  PAYMENT_METHOD: "paymentMethod",
  DOWN_PAYMENT: "downPayment",
  LOAN_TERM: "loanTerm",
  CREDIT_SCORE: "creditScore",
  MONTHLY_PAYMENT_MAX: "monthlyPaymentMax",
  TRADE_IN_VALUE: "tradeInValue",

  // Deal/Negotiation
  DEAL_ID: "dealId",
  TARGET_PRICE: "targetPrice",
  NEGOTIATED_PRICE: "negotiatedPrice",
  SESSION_ID: "sessionId",

  // Pagination & Sorting
  PAGE: "page",
  PER_PAGE: "perPage",
  SORT_BY: "sortBy",
  ORDER: "order",

  // Features
  MUST_HAVE_FEATURES: "mustHaveFeatures",
  USER_PRIORITIES: "userPriorities",
} as const;

/**
 * Stepper Step Indices
 */
export const STEPPER_STEPS = {
  SEARCH: 0,
  RESULTS: 1,
  EVALUATION: 2,
  NEGOTIATION: 3,
  FINALIZE: 4,
} as const;

/**
 * Helper function to build query string from vehicle data
 */
export function buildVehicleQueryString(vehicle: {
  vin?: string;
  make: string;
  model: string;
  year: number;
  price: number;
  mileage: number;
  fuelType?: string;
  condition?: string;
  zipCode?: string;
  dealId?: string | number;
}): string {
  const params = new URLSearchParams();

  if (vehicle.vin) params.set(QUERY_PARAMS.VIN, vehicle.vin);
  params.set(QUERY_PARAMS.MAKE, vehicle.make);
  params.set(QUERY_PARAMS.MODEL, vehicle.model);
  params.set(QUERY_PARAMS.YEAR, vehicle.year.toString());
  params.set(QUERY_PARAMS.PRICE, vehicle.price.toString());
  params.set(QUERY_PARAMS.MILEAGE, vehicle.mileage.toString());
  if (vehicle.fuelType) params.set(QUERY_PARAMS.FUEL_TYPE, vehicle.fuelType);
  if (vehicle.condition) params.set(QUERY_PARAMS.CONDITION, vehicle.condition);
  if (vehicle.zipCode) params.set(QUERY_PARAMS.ZIP_CODE, vehicle.zipCode);
  if (vehicle.dealId) params.set(QUERY_PARAMS.DEAL_ID, vehicle.dealId.toString());

  return params.toString();
}

/**
 * Helper function to get route with query params
 */
export function getRouteWithParams(route: string, params: Record<string, string | number>): string {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    searchParams.set(key, value.toString());
  });
  return `${route}?${searchParams.toString()}`;
}
