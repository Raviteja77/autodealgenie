// frontend/lib/error-handler.ts

/**
 * Structured API Error class.
 * Represents HTTP errors and encapsulates information like status code, message, and optional details.
 */
export class ApiError extends Error {
  constructor(
    public statusCode: number,
    message: string,
    public details?: Record<string, unknown>
  ) {
    super(message);
    Object.setPrototypeOf(this, ApiError.prototype);
  }
}