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
    START_NEGOTIATION: "🤝 Start Negotiation",
  },
  ERRORS: {
    PARSING_VEHICLE_DATA: "Error parsing vehicle data:",
    EVALUATING_DEAL: "Error evaluating deal:",
    INVALID_VEHICLE_DATA: "Invalid vehicle data for evaluation",
    FAILED_TO_EVALUATE: "Failed to evaluate deal",
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
    MAKE_COUNTER_OFFER: "Make Counter Offer",
    ACCEPT_OFFER: "Accept Offer?",
    CANCEL_NEGOTIATION: "Cancel Negotiation?",
    NEGOTIATION_TIPS: "Negotiation Tips",
    AI_INSIGHTS: "AI Insights",
    PRICE_TRACKING: "Price Tracking",
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
    COUNTER_OFFER_PRICE: "Counter Offer Price",
    AI_SUGGESTED: "AI Suggested",
    DEALER_PRICE: "Dealer Price",
    YOUR_COUNTER: "Your Counter",
    DEALER: "Dealer",
    YOU: "You",
    AI: "AI",
    BEST_MATCH: "Best Match",
    CHAT: "Chat",
    ACTIONS: "Actions",
    AVAILABLE: "Available",
    DEALER_INFO: "Dealer Info",
    DEALER_FLEXIBILITY: "Dealer Flexibility",
    DEALER_VERY_FLEXIBLE: "Dealer is very flexible",
    DEALER_SOMEWHAT_FLEXIBLE: "Dealer is somewhat flexible",
    DEALER_HOLDING_FIRM: "Dealer holding firm",
    ORIGINAL_PRICE: "Original Price",
    YOU_SAVE: "You Save",
    FROM_ROUND: "From Round",
  },
  MESSAGES: {
    LOADING_NEGOTIATION: "Loading negotiation data...",
    COUNTER_OFFER_SUBMITTED: "Counter offer submitted!",
    OFFER_ACCEPTED: "Offer accepted! Proceeding to finalize...",
    NEGOTIATION_CANCELLED: "Negotiation cancelled",
    CONNECTING: "Connecting to negotiation service...",
    INITIALIZING: "Initializing negotiation...",
    SESSION_STARTED: "Negotiation session started! Let's get you the best deal.",
    CANCELLED_CAN_RESTART: "Negotiation cancelled. You can start a new one anytime.",
    NO_VALID_PRICE: "No valid price available to accept",
    CANNOT_ACCEPT_INVALID: "Cannot accept offer with invalid price",
    ENTER_VALID_PRICE: "Please enter a valid price",
    FAILED_TO_ACCEPT: "Failed to accept offer",
    FAILED_TO_REJECT: "Failed to reject offer",
    FAILED_TO_COUNTER: "Failed to submit counter offer",
  },
  DESCRIPTIONS: {
    ACCEPT_CONFIRM: "Are you sure you want to accept this offer?",
    CANCEL_CONFIRM: "Are you sure you want to cancel this negotiation? You can resume it later from your deals page.",
    ENTER_COUNTER_AMOUNT: "Enter your counter offer price. Be realistic and strategic to keep the negotiation moving forward.",
    ACCEPT_DEAL_CONFIRMATION: "This will complete the negotiation and move forward with the deal.",
  },
  ACTIONS: {
    CONTINUE_TO_FINALIZE: "Continue to Finalize",
    ACCEPT_OFFER: "Accept Offer",
    COUNTER_OFFER: "Counter Offer",
    CANCEL: "Cancel",
    CONFIRM: "Confirm",
    SEND_COUNTER: "Send Counter",
    MAKE_OFFER: "Make Offer",
    START_NEGOTIATION: "Start Negotiation",
    VIEW_OFFER: "View Offer",
  },
  TIPS: {
    BE_REALISTIC: "• Counter with realistic offers",
    KNOW_MARKET: "• Know the market value",
    BE_PATIENT: "• Be patient and willing to walk away",
    BUILD_RAPPORT: "• Build rapport with the dealer",
  },
  EMPTY_STATES: {
    NO_MESSAGES: "No messages yet. Start the conversation!",
    NO_OFFERS: "No offers have been made yet.",
  },
  ERRORS: {
    INVALID_DATA: "Invalid vehicle data for negotiation",
    FAILED_TO_LOAD: "Failed to load negotiation data",
    FAILED_TO_SEND: "Failed to send message",
    CONNECTION_LOST: "Connection to negotiation service lost",
  },
} as const;

/**
 * Search Feature Text Constants
 */
export const SEARCH_TEXT = {
  TITLES: {
    SEARCH_RESULTS: "Search Results",
    FILTERS: "Filters",
    SEARCH_VEHICLES: "Search Vehicles",
    ADVANCED_FILTERS: "Advanced Filters",
  },
  LABELS: {
    NO_RESULTS: "No Results Found",
    RESULTS_COUNT: "results",
    TOGGLE_ADVANCED: "Toggle advanced filters",
  },
  MESSAGES: {
    LOADING: "Loading search form...",
    SEARCHING: "Searching for vehicles...",
  },
  DESCRIPTIONS: {
    SEARCH_INTRO: "Find your perfect vehicle by customizing your search criteria",
  },
  ACTIONS: {
    SEARCH: "Search",
    CLEAR_FILTERS: "Clear Filters",
    APPLY_FILTERS: "Apply Filters",
    SEARCH_VEHICLES: "Search Vehicles",
    RESET: "Reset",
  },
  ERRORS: {
    SEARCH_FAILED: "Search failed. Please try again.",
    INVALID_CRITERIA: "Invalid search criteria",
  },
} as const;

/**
 * Results Feature Text Constants
 */
export const RESULTS_TEXT = {
  TITLES: {
    SEARCH_RESULTS: "Search Results",
    ERROR_LOADING: "Error Loading Vehicles",
    ACTIVE_FILTERS: "Active Filters:",
  },
  LABELS: {
    VEHICLES_COUNT: "vehicles",
    FILTERS: "Filters",
    SAVE_SEARCH: "Save Search",
    VEHICLES_FOUND: "Found",
    MATCHING_CRITERIA: "vehicles matching your criteria",
  },
  MESSAGES: {
    LOADING: "Finding the best deals for you...",
    LOADING_RESULTS: "Loading results...",
    NO_VEHICLES: "No vehicles found matching your criteria",
    NO_VEHICLES_DESCRIPTION: "Try adjusting your filters or search again",
  },
  ACTIONS: {
    VIEW_FAVORITES: "View Favorites",
    REFINE_SEARCH: "Refine Search",
    BACK_TO_SEARCH: "Back to Search",
    FILTERS: "Filters",
    SAVE_SEARCH: "Save Search",
    COMPARE: "Compare",
    VIEW_DETAILS: "View Details",
    ADD_TO_FAVORITES: "Add to Favorites",
    REMOVE_FROM_FAVORITES: "Remove from Favorites",
  },
  EMPTY_STATES: {
    MESSAGE: "No vehicles found matching your criteria",
    DESCRIPTION: "Try adjusting your filters or search again",
  },
  ERRORS: {
    LOAD_FAILED: "Failed to load vehicles",
    FETCH_FAILED: "Error fetching search results",
  },
} as const;

/**
 * Deals Feature Text Constants
 */
export const DEALS_TEXT = {
  TITLES: {
    MY_DEALS: "My Deals",
    DEAL_DETAILS: "Deal Details",
    ERROR_LOADING: "Error Loading Deals",
  },
  LABELS: {
    STATUS: "Status",
    CREATED: "Created",
    UPDATED: "Updated",
    MILEAGE: "Mileage:",
    ASKING_PRICE: "Asking Price:",
    OFFER_PRICE: "Offer Price:",
    MILES_SUFFIX: "miles",
  },
  MESSAGES: {
    LOADING: "Loading deals...",
    NO_DEALS: "No deals found",
    NO_DEALS_DESCRIPTION: "Start browsing vehicles and create your first deal",
  },
  ACTIONS: {
    VIEW_DEAL: "View Deal",
    CREATE_DEAL: "Create Deal",
    SEARCH_VEHICLES: "Search Vehicles",
  },
  EMPTY_STATES: {
    MESSAGE: "No deals found",
    DESCRIPTION: "Start browsing vehicles and create your first deal",
  },
} as const;

/**
 * Favorites Feature Text Constants
 */
export const FAVORITES_TEXT = {
  TITLES: {
    MY_FAVORITES: "My Favorites",
    ERROR_LOADING: "Error Loading Favorites",
  },
  LABELS: {
    CONDITION: "Condition:",
    MILEAGE_SUFFIX: "mi",
    VEHICLE: "vehicle",
    VEHICLES: "vehicles",
  },
  MESSAGES: {
    LOADING: "Loading your favorites...",
    NO_FAVORITES: "You haven't added any favorites yet",
    YOU_HAVE: "You have",
    SAVED: "saved",
  },
  DESCRIPTIONS: {
    NO_FAVORITES: "Start browsing and save your favorite vehicles",
  },
  ACTIONS: {
    BROWSE_CARS: "Browse Cars",
    SEARCH_CARS: "Search Cars",
    NEGOTIATE: "Negotiate",
    VIEW_DETAILS: "View Details",
  },
  EMPTY_STATES: {
    MESSAGE: "No favorites yet",
    DESCRIPTION: "Start browsing and save your favorite vehicles",
  },
  ERRORS: {
    FETCH_FAILED: "Error fetching favorites:",
    REMOVE_FAILED: "Error removing favorite:",
  },
  FALLBACK: {
    NOT_AVAILABLE: "N/A",
  },
} as const;

/**
 * Finalize Feature Text Constants
 */
export const FINALIZE_TEXT = {
  TITLES: {
    FINALIZE_DEAL: "Finalize Your Deal",
    DEAL_SUMMARY: "Deal Summary",
    PRICE_BREAKDOWN: "Price Breakdown",
    VEHICLE_DETAILS: "Vehicle Details",
    RECOMMENDATIONS: "Recommendations",
    ERROR_LOADING: "Error Loading Data",
  },
  LABELS: {
    STEP_LABEL: "Step 4 of 4",
    INSURANCE: "Insurance",
    FINANCING: "Financing",
    BEST_MATCH: "Best Match",
    VEHICLE_PRICE: "Vehicle Price",
    NEGOTIATED_PRICE: "Negotiated Price",
    SAVINGS: "Savings",
    TAX: "Tax",
    FEES: "Fees",
    TOTAL_PRICE: "Total Price",
    DOWN_PAYMENT: "Down Payment",
    LOAN_AMOUNT: "Loan Amount",
    MONTHLY_PAYMENT: "Monthly Payment",
    VIN: "VIN",
    MILEAGE: "Mileage",
    CONDITION: "Condition",
  },
  MESSAGES: {
    LOADING_INSURANCE: "Loading insurance recommendations...",
    LOADING_FINANCING: "Loading financing options...",
    CALCULATING: "Calculating your best options...",
    DEAL_SCORE_PREFIX: "Deal Quality Score:",
    EXCELLENT_DEAL: "Excellent deal! This is well below market value.",
    GOOD_DEAL: "Good deal! Fair price for this vehicle.",
    CONSIDER_NEGOTIATING: "Consider negotiating further or exploring other options.",
    FINAL_DEAL_SUMMARY: "🎉 Final Deal Summary",
    REVIEW_DETAILS: "Review your deal details and explore financing & insurance options before finalizing",
  },
  DESCRIPTIONS: {
    INSURANCE_INTRO: "Compare insurance quotes for your new vehicle",
    FINANCING_INTRO: "Explore financing options tailored to your needs",
    FINAL_STEP: "Review your deal and complete your purchase",
  },
  ACTIONS: {
    BACK_TO_NEGOTIATION: "Back to Negotiation",
    COMPLETE_PURCHASE: "Complete Purchase",
    GET_INSURANCE_QUOTE: "Get Insurance Quote",
    APPLY_FOR_FINANCING: "Apply for Financing",
    VIEW_DETAILS: "View Details",
    COMPARE_OPTIONS: "Compare Options",
  },
  EMPTY_STATES: {
    NO_INSURANCE: "No insurance recommendations available",
    NO_FINANCING: "No financing options available",
  },
  ERRORS: {
    INVALID_DATA: "Invalid vehicle data. Please return to search.",
    FETCH_FAILED: "Failed to load recommendations",
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
