/**
 * Negotiation Utilities
 * 
 * Helper functions for negotiation-related calculations and validations.
 */

import type { NegotiationMessage } from "@/lib/api";

/**
 * Extract latest negotiated price from messages
 * 
 * @param messages - Array of negotiation messages
 * @returns Latest negotiated price object or null
 */
export interface LatestPriceInfo {
  price: number;
  source: "user" | "dealer" | "ai";
  round: number;
  timestamp: string;
}

export function getLatestNegotiatedPrice(
  messages: NegotiationMessage[]
): LatestPriceInfo | null {
  if (messages.length === 0) return null;

  // Search from most recent to oldest
  for (let i = messages.length - 1; i >= 0; i--) {
    const message = messages[i];
    if (!message.metadata) continue;

    const price =
      message.metadata.suggested_price ||
      message.metadata.counter_offer ||
      message.metadata.price;

    if (typeof price === "number") {
      let source: LatestPriceInfo["source"];
      if (message.role === "user") {
        source = "user";
      } else if (message.role === "dealer_sim") {
        source = "dealer";
      } else {
        source = "ai";
      }

      return {
        price,
        source,
        round: message.round_number,
        timestamp: message.created_at,
      };
    }
  }

  return null;
}

/**
 * Validate negotiated price against bounds
 * 
 * @param negotiatedPrice - The proposed negotiated price
 * @param askingPrice - Original asking price
 * @param targetPrice - User's target price (optional)
 * @returns Validation result with isValid flag and optional error message
 */
export function validateNegotiatedPrice(
  negotiatedPrice: number | null | undefined,
  askingPrice: number,
  targetPrice?: number | null
): { isValid: boolean; error?: string } {
  if (negotiatedPrice === null || negotiatedPrice === undefined) {
    return { isValid: false, error: "No price available" };
  }

  if (negotiatedPrice <= 0) {
    return { isValid: false, error: "Price must be greater than zero" };
  }

  // Price should not be more than asking price (in most cases)
  if (negotiatedPrice > askingPrice * 1.1) {
    return {
      isValid: false,
      error: "Price is significantly higher than asking price",
    };
  }

  // Warning if above target but still valid
  if (targetPrice && negotiatedPrice > targetPrice) {
    return {
      isValid: true,
      error: `Price is $${(negotiatedPrice - targetPrice).toLocaleString()} above your target`,
    };
  }

  return { isValid: true };
}
