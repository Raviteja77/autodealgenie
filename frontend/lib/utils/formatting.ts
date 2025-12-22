/**
 * Consolidated formatting utilities for the application
 * 
 * This module provides reusable formatting functions for:
 * - Currency/price formatting
 * - Timestamp/date formatting
 * - Message formatting
 * 
 * All functions are pure and can be used across components without
 * causing unnecessary re-renders when passed as dependencies.
 */

/**
 * Format a number as USD currency
 * 
 * @param value - The numeric value to format
 * @param options - Optional Intl.NumberFormat options
 * @returns Formatted currency string (e.g., "$25,000")
 * 
 * @example
 * formatPrice(25000) // "$25,000"
 * formatPrice(1234.56) // "$1,234.56"
 */
export function formatPrice(
  value: number,
  options?: Intl.NumberFormatOptions
): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
    ...options,
  }).format(value);
}

/**
 * Format a number as a compact currency (e.g., $25K instead of $25,000)
 * 
 * @param value - The numeric value to format
 * @returns Compact currency string
 * 
 * @example
 * formatCompactPrice(25000) // "$25K"
 * formatCompactPrice(1500000) // "$1.5M"
 */
export function formatCompactPrice(value: number): string {
  // For compact formatting, manually handle K/M/B suffixes
  const absValue = Math.abs(value);
  let displayValue: number;
  let suffix: string;
  
  if (absValue >= 1_000_000_000) {
    displayValue = value / 1_000_000_000;
    suffix = "B";
  } else if (absValue >= 1_000_000) {
    displayValue = value / 1_000_000;
    suffix = "M";
  } else if (absValue >= 1_000) {
    displayValue = value / 1_000;
    suffix = "K";
  } else {
    return formatPrice(value);
  }
  
  return `$${displayValue.toFixed(1)}${suffix}`;
}

/**
 * Format a timestamp as a localized time string
 * 
 * @param timestamp - ISO timestamp string or Date object
 * @param options - Optional Intl.DateTimeFormat options
 * @returns Formatted time string (e.g., "2:30 PM")
 * 
 * @example
 * formatTimestamp("2024-01-15T14:30:00Z") // "2:30 PM"
 * formatTimestamp(new Date()) // Current time formatted
 */
export function formatTimestamp(
  timestamp: string | Date,
  options?: Intl.DateTimeFormatOptions
): string {
  const date = typeof timestamp === "string" ? new Date(timestamp) : timestamp;
  
  return new Intl.DateTimeFormat("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    ...options,
  }).format(date);
}

/**
 * Format a timestamp as a full date and time
 * 
 * @param timestamp - ISO timestamp string or Date object
 * @returns Formatted date and time string (e.g., "Jan 15, 2024 at 2:30 PM")
 * 
 * @example
 * formatFullTimestamp("2024-01-15T14:30:00Z") // "Jan 15, 2024 at 2:30 PM"
 */
export function formatFullTimestamp(timestamp: string | Date): string {
  const date = typeof timestamp === "string" ? new Date(timestamp) : timestamp;
  
  const dateStr = new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(date);
  
  const timeStr = formatTimestamp(date);
  
  return `${dateStr} at ${timeStr}`;
}

/**
 * Calculate and format percentage
 * 
 * @param value - The numeric value to convert to percentage
 * @param total - The total value for percentage calculation
 * @param decimals - Number of decimal places (default: 0)
 * @returns Formatted percentage string (e.g., "45%")
 * 
 * @example
 * formatPercentage(45, 100) // "45%"
 * formatPercentage(33.333, 100, 1) // "33.3%"
 */
export function formatPercentage(
  value: number,
  total: number,
  decimals: number = 0
): string {
  if (total === 0) return "0%";
  const percentage = (value / total) * 100;
  return `${percentage.toFixed(decimals)}%`;
}

/**
 * Calculate discount percentage between two prices
 * 
 * @param originalPrice - Original/asking price
 * @param discountedPrice - Discounted/negotiated price
 * @returns Discount percentage as a number (e.g., 10 for 10% off)
 * 
 * @example
 * calculateDiscountPercent(25000, 22500) // 10
 * calculateDiscountPercent(30000, 27000) // 10
 */
export function calculateDiscountPercent(
  originalPrice: number,
  discountedPrice: number
): number {
  if (originalPrice === 0) return 0;
  return ((originalPrice - discountedPrice) / originalPrice) * 100;
}

/**
 * Format a large number with commas (for mileage, etc.)
 * 
 * @param value - The numeric value to format
 * @returns Formatted number string with commas (e.g., "45,000")
 * 
 * @example
 * formatNumber(45000) // "45,000"
 * formatNumber(1234567) // "1,234,567"
 */
export function formatNumber(value: number): string {
  return new Intl.NumberFormat("en-US").format(value);
}

/**
 * Truncate text to a maximum length with ellipsis
 * 
 * @param text - Text to truncate
 * @param maxLength - Maximum length before truncation
 * @returns Truncated text with ellipsis if needed
 * 
 * @example
 * truncateText("This is a long message", 10) // "This is a..."
 * truncateText("Short", 10) // "Short"
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + "...";
}

/**
 * Format savings amount with appropriate sign and color context
 * 
 * @param originalPrice - Original price
 * @param currentPrice - Current/negotiated price
 * @returns Object with formatted savings string and color indicator
 * 
 * @example
 * formatSavings(25000, 22500) 
 * // { text: "$2,500 saved", color: "success", amount: 2500 }
 */
export function formatSavings(
  originalPrice: number,
  currentPrice: number
): {
  text: string;
  color: "success" | "warning" | "error";
  amount: number;
} {
  const savings = originalPrice - currentPrice;
  const absValue = Math.abs(savings);
  
  if (savings > 0) {
    return {
      text: `$${formatNumber(absValue)} saved`,
      color: "success",
      amount: savings,
    };
  } else if (savings < 0) {
    return {
      text: `$${formatNumber(absValue)} over asking`,
      color: "error",
      amount: savings,
    };
  } else {
    return {
      text: "At asking price",
      color: "warning",
      amount: 0,
    };
  }
}
