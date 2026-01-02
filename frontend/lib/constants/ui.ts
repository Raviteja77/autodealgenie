/**
 * UI Constants
 * 
 * Centralizes UI-related constants including default values,
 * limits, timeouts, debounce delays, and other UI configurations.
 */

/**
 * Debounce Delays (in milliseconds)
 */
export const DEBOUNCE_DELAY = {
  SHORT: 150,
  MEDIUM: 300,
  LONG: 500,
  SEARCH: 300,
  SLIDER: 300,
} as const;

/**
 * API Request Timeouts (in milliseconds)
 */
export const TIMEOUT = {
  SHORT: 5000,
  MEDIUM: 10000,
  LONG: 30000,
  API_REQUEST: 10000,
} as const;

/**
 * Notification Display Duration (in milliseconds)
 */
export const NOTIFICATION_DURATION = {
  SHORT: 3000,
  MEDIUM: 5000,
  LONG: 7000,
  ERROR: 5000,
  SUCCESS: 3000,
} as const;

/**
 * Pagination
 */
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  PAGE_SIZE_OPTIONS: [10, 20, 50, 100] as const,
  INITIAL_PAGE: 1,
} as const;

/**
 * Animation Durations (in milliseconds)
 */
export const ANIMATION = {
  FAST: 150,
  NORMAL: 300,
  SLOW: 500,
  COLLAPSE: 300,
  FADE: 200,
} as const;

/**
 * Loading States
 */
export const LOADING = {
  SPINNER_SIZE: {
    SMALL: "sm" as const,
    MEDIUM: "md" as const,
    LARGE: "lg" as const,
  },
  DEFAULT_TEXT: "Loading...",
} as const;

/**
 * File Size Limits
 */
export const FILE_SIZE = {
  MAX_IMAGE_SIZE: 5 * 1024 * 1024, // 5MB
  MAX_DOCUMENT_SIZE: 10 * 1024 * 1024, // 10MB
} as const;

/**
 * Input Field Limits
 */
export const INPUT_LIMIT = {
  MAX_TEXT_LENGTH: 500,
  MAX_NAME_LENGTH: 100,
  MAX_EMAIL_LENGTH: 255,
  MAX_COMMENT_LENGTH: 1000,
  MAX_SEARCH_QUERY_LENGTH: 200,
} as const;

/**
 * View Modes
 */
export const VIEW_MODE = {
  GRID: "grid" as const,
  LIST: "list" as const,
  DEFAULT: "grid" as const,
} as const;

export type ViewMode = typeof VIEW_MODE[keyof typeof VIEW_MODE];

/**
 * Comparison Limits
 */
export const COMPARISON = {
  MAX_VEHICLES: 4,
  MIN_VEHICLES: 2,
} as const;

/**
 * Chat/Message Limits
 */
export const CHAT = {
  MAX_MESSAGE_LENGTH: 500,
  MAX_MESSAGES_DISPLAYED: 100,
  TYPING_INDICATOR_DELAY: 1000,
} as const;

/**
 * Display Mode for Vehicle Prices
 */
export const DISPLAY_MODE = {
  CASH: "cash" as const,
  MONTHLY: "monthly" as const,
  BOTH: "both" as const,
  DEFAULT: "both" as const,
} as const;

export type DisplayMode = typeof DISPLAY_MODE[keyof typeof DISPLAY_MODE];

/**
 * Z-Index Layers
 */
export const Z_INDEX = {
  MODAL: 1300,
  DRAWER: 1200,
  APPBAR: 1100,
  DROPDOWN: 1000,
  STICKY: 100,
  DEFAULT: 1,
} as const;

/**
 * Breakpoints (matches MUI default breakpoints)
 */
export const BREAKPOINT = {
  XS: 0,
  SM: 600,
  MD: 900,
  LG: 1200,
  XL: 1536,
} as const;

/**
 * Error Retry Configuration
 */
export const RETRY = {
  MAX_ATTEMPTS: 3,
  INITIAL_DELAY: 1000,
  BACKOFF_MULTIPLIER: 2,
} as const;
