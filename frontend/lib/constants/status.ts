/**
 * Status Constants
 * 
 * Centralizes status-related constants including deal statuses,
 * colors, messages, and status transitions.
 */

/**
 * Deal Status Values
 */
export const DEAL_STATUS = {
  PENDING: "pending",
  IN_PROGRESS: "in_progress",
  NEGOTIATING: "negotiating",
  ACCEPTED: "accepted",
  REJECTED: "rejected",
  COMPLETED: "completed",
  CANCELLED: "cancelled",
  EXPIRED: "expired",
} as const;

export type DealStatus = typeof DEAL_STATUS[keyof typeof DEAL_STATUS];

/**
 * Status Colors for MUI Components
 */
export const STATUS_COLOR = {
  [DEAL_STATUS.PENDING]: "warning" as const,
  [DEAL_STATUS.IN_PROGRESS]: "info" as const,
  [DEAL_STATUS.NEGOTIATING]: "info" as const,
  [DEAL_STATUS.ACCEPTED]: "success" as const,
  [DEAL_STATUS.REJECTED]: "error" as const,
  [DEAL_STATUS.COMPLETED]: "success" as const,
  [DEAL_STATUS.CANCELLED]: "default" as const,
  [DEAL_STATUS.EXPIRED]: "error" as const,
} as const;

/**
 * Status Display Labels
 */
export const STATUS_LABEL = {
  [DEAL_STATUS.PENDING]: "Pending",
  [DEAL_STATUS.IN_PROGRESS]: "In Progress",
  [DEAL_STATUS.NEGOTIATING]: "Negotiating",
  [DEAL_STATUS.ACCEPTED]: "Accepted",
  [DEAL_STATUS.REJECTED]: "Rejected",
  [DEAL_STATUS.COMPLETED]: "Completed",
  [DEAL_STATUS.CANCELLED]: "Cancelled",
  [DEAL_STATUS.EXPIRED]: "Expired",
} as const;

/**
 * Navigation Hints by Deal Status
 */
export const STATUS_NAVIGATION_HINT = {
  [DEAL_STATUS.PENDING]: "Click to continue evaluation",
  [DEAL_STATUS.IN_PROGRESS]: "Click to continue negotiation",
  [DEAL_STATUS.NEGOTIATING]: "Click to continue negotiation",
  [DEAL_STATUS.ACCEPTED]: "Click to finalize deal",
  [DEAL_STATUS.REJECTED]: null,
  [DEAL_STATUS.COMPLETED]: "View completed deal",
  [DEAL_STATUS.CANCELLED]: null,
  [DEAL_STATUS.EXPIRED]: null,
} as const;

/**
 * Negotiation Status
 */
export const NEGOTIATION_STATUS = {
  IDLE: "idle",
  ACTIVE: "active",
  WAITING_DEALER: "waiting_dealer",
  WAITING_USER: "waiting_user",
  COMPLETED: "completed",
  FAILED: "failed",
} as const;

export type NegotiationStatus = typeof NEGOTIATION_STATUS[keyof typeof NEGOTIATION_STATUS];

/**
 * Message Roles
 */
export const MESSAGE_ROLE = {
  USER: "user",
  DEALER: "dealer_sim",
  AI: "ai_assistant",
  SYSTEM: "system",
} as const;

export type MessageRole = typeof MESSAGE_ROLE[keyof typeof MESSAGE_ROLE];

/**
 * Alert/Notification Types
 */
export const ALERT_TYPE = {
  SUCCESS: "success" as const,
  ERROR: "error" as const,
  WARNING: "warning" as const,
  INFO: "info" as const,
} as const;

export type AlertType = typeof ALERT_TYPE[keyof typeof ALERT_TYPE];

/**
 * Connection Status
 */
export const CONNECTION_STATUS = {
  CONNECTED: "connected",
  DISCONNECTED: "disconnected",
  CONNECTING: "connecting",
  ERROR: "error",
} as const;

export type ConnectionStatus = typeof CONNECTION_STATUS[keyof typeof CONNECTION_STATUS];

/**
 * Helper function to get status color
 */
export function getStatusColor(
  status: string
): "warning" | "info" | "success" | "error" | "default" {
  return STATUS_COLOR[status as DealStatus] ?? "default";
}

/**
 * Helper function to get status label
 */
export function getStatusLabel(status: string): string {
  return STATUS_LABEL[status as DealStatus] ?? status;
}

/**
 * Helper function to get navigation hint
 */
export function getNavigationHint(status: string): string | null {
  return STATUS_NAVIGATION_HINT[status as DealStatus] ?? null;
}
