/**
 * Text Constants
 * 
 * Centralizes all UI text, labels, messages, and button text used throughout the application.
 * Organized by feature/page for easy maintenance and localization support.
 */

/**
 * Evaluation Feature Text Constants
 */
export const EVALUATION_TEXT = {
  TITLES: {
    DEAL_QUALITY_SCORE: "Deal Quality Score",
    KEY_INSIGHTS: "Key Insights",
    MARKET_ANALYSIS: "Market Analysis",
    TALKING_POINTS: "Talking Points",
    EVALUATING: "Evaluating Vehicle",
    EVALUATION_ERROR: "Evaluation Error",
    INVALID_VEHICLE_DATA: "Invalid Vehicle Data",
  },
  LABELS: {
    SCORE_OUT_OF_TEN: "/10",
    MARKET_POSITION: "Market Position",
    STRONG_POSITION: "Strong Position",
    ABOVE_MARKET: "Above Market",
    BELOW_MARKET: "Below Market",
    SIMILAR_VEHICLES: "Similar Vehicles",
    DAYS_ON_MARKET: "Days on Market",
  },
  MESSAGES: {
    EXCELLENT_DEAL: "Excellent Deal! This is a great value.",
    GOOD_DEAL: "Good Deal. This is priced competitively.",
    FAIR_DEAL: "Fair Deal. Price is reasonable for the market.",
    POOR_DEAL: "Poor Deal. You may be overpaying for this vehicle.",
    PRICE_DIFFERENCE: "price difference from market average",
    IN_YOUR_AREA: "in your area",
    AVERAGE_PREFIX: "Average:",
    FASTER_THAN_AVERAGE: "faster than average",
  },
  DESCRIPTIONS: {
    MARKET_ANALYSIS: "Based on analysis of similar vehicles in your area",
    ANALYZING: "Analyzing vehicle data and market conditions...",
    INVALID_DATA: "The vehicle data provided is incomplete or invalid. Please return to search and select a valid vehicle.",
  },
  ACTIONS: {
    BACK_TO_SEARCH: "Back to Search",
    RETRY_EVALUATION: "Retry Evaluation",
  },
} as const;

/**
 * Negotiation Feature Text Constants
 */
export const NEGOTIATION_TEXT = {
  TITLES: {
    NEGOTIATION: "Negotiation",
    CONGRATULATIONS: "Congratulations!",
    FINANCING_OPTIONS: "Financing Options",
  },
  LABELS: {
    VIN: "VIN",
    PRICE_TRACKING: "Price Tracking",
    ASKING_PRICE: "Asking Price",
    TARGET_PRICE: "Target Price",
    CURRENT_OFFER: "Current Offer",
    CURRENT_PRICE: "Current Price",
    NEGOTIATION_PROGRESS: "Negotiation Progress",
    SAVINGS: "Savings",
  },
  ACTIONS: {
    CONTINUE_TO_FINALIZE: "Continue to Finalize",
  },
} as const;

/**
 * Search Feature Text Constants
 */
export const SEARCH_TEXT = {
  TITLES: {
    SEARCH_RESULTS: "Search Results",
    FILTERS: "Filters",
  },
  LABELS: {
    NO_RESULTS: "No Results Found",
    RESULTS_COUNT: "results",
  },
  ACTIONS: {
    SEARCH: "Search",
    CLEAR_FILTERS: "Clear Filters",
    APPLY_FILTERS: "Apply Filters",
  },
} as const;

/**
 * Deals Feature Text Constants
 */
export const DEALS_TEXT = {
  TITLES: {
    MY_DEALS: "My Deals",
    DEAL_DETAILS: "Deal Details",
  },
  LABELS: {
    STATUS: "Status",
    CREATED: "Created",
    UPDATED: "Updated",
  },
  ACTIONS: {
    VIEW_DEAL: "View Deal",
    CREATE_DEAL: "Create Deal",
  },
} as const;

/**
 * Common UI Text Constants
 */
export const COMMON_TEXT = {
  LOADING: "Loading...",
  ERROR: "Error",
  SUCCESS: "Success",
  CANCEL: "Cancel",
  SAVE: "Save",
  DELETE: "Delete",
  EDIT: "Edit",
  CLOSE: "Close",
  BACK: "Back",
  NEXT: "Next",
  SUBMIT: "Submit",
  RETRY: "Retry",
  CONFIRM: "Confirm",
} as const;

/**
 * Error Messages
 */
export const ERROR_MESSAGES = {
  GENERIC: "An unexpected error occurred. Please try again.",
  NETWORK: "Network error. Please check your connection.",
  NOT_FOUND: "The requested resource was not found.",
  UNAUTHORIZED: "You are not authorized to perform this action.",
  VALIDATION: "Please check your input and try again.",
} as const;

/**
 * Empty State Messages
 */
export const EMPTY_STATE_MESSAGES = {
  NO_RESULTS: "No results found",
  NO_DATA: "No data available",
  NO_FAVORITES: "You haven't added any favorites yet",
  NO_DEALS: "You don't have any deals yet",
} as const;
