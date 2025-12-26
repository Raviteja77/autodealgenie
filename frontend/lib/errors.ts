/**
 * Structured Error Classes for API and Application Errors
 */

/**
 * Base API Error class
 */
export class ApiError extends Error {
  public statusCode: number;
  public details?: unknown;

  constructor(message: string, statusCode: number, details?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.details = details;
    Object.setPrototypeOf(this, ApiError.prototype);
  }
}

/**
 * Authentication Error (401)
 */
export class AuthenticationError extends ApiError {
  constructor(message: string = 'Authentication required', details?: unknown) {
    super(message, 401, details);
    this.name = 'AuthenticationError';
    Object.setPrototypeOf(this, AuthenticationError.prototype);
  }
}

/**
 * Authorization Error (403)
 */
export class AuthorizationError extends ApiError {
  constructor(message: string = 'Access forbidden', details?: unknown) {
    super(message, 403, details);
    this.name = 'AuthorizationError';
    Object.setPrototypeOf(this, AuthorizationError.prototype);
  }
}

/**
 * Not Found Error (404)
 */
export class NotFoundError extends ApiError {
  constructor(message: string = 'Resource not found', details?: unknown) {
    super(message, 404, details);
    this.name = 'NotFoundError';
    Object.setPrototypeOf(this, NotFoundError.prototype);
  }
}

/**
 * Validation Error (422)
 */
export class ValidationError extends ApiError {
  public validationErrors?: Record<string, string[]>;

  constructor(
    message: string = 'Validation failed',
    validationErrors?: Record<string, string[]>,
    details?: unknown
  ) {
    super(message, 422, details);
    this.name = 'ValidationError';
    this.validationErrors = validationErrors;
    Object.setPrototypeOf(this, ValidationError.prototype);
  }
}

/**
 * Server Error (500)
 */
export class ServerError extends ApiError {
  constructor(message: string = 'Internal server error', details?: unknown) {
    super(message, 500, details);
    this.name = 'ServerError';
    Object.setPrototypeOf(this, ServerError.prototype);
  }
}

/**
 * Network Error
 */
export class NetworkError extends Error {
  constructor(message: string = 'Network request failed') {
    super(message);
    this.name = 'NetworkError';
    Object.setPrototypeOf(this, NetworkError.prototype);
  }
}

/**
 * Parse error response and create appropriate error instance
 */
export function createErrorFromResponse(
  statusCode: number,
  message: string,
  details?: unknown
): ApiError {
  switch (statusCode) {
    case 401:
      return new AuthenticationError(message, details);
    case 403:
      return new AuthorizationError(message, details);
    case 404:
      return new NotFoundError(message, details);
    case 422:
      if (details && typeof details === 'object' && 'validation_errors' in details) {
        return new ValidationError(
          message,
          details.validation_errors as Record<string, string[]>,
          details
        );
      }
      if(details && typeof details === 'object' && 'detail' in details && Array.isArray(details.detail)) {
        const error = details.detail.map((e: any) => e.msg).join(", ");
        return new ValidationError(
          error,
          undefined,
          details.detail
        );
      }
      return new ValidationError(message, undefined, details);
    case 500:
    case 502:
    case 503:
    case 504:
      return new ServerError(message, details);
    default:
      return new ApiError(message, statusCode, details);
  }
}

/**
 * Type guard to check if error is an ApiError
 */
export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

/**
 * Type guard to check if error is a ValidationError
 */
export function isValidationError(error: unknown): error is ValidationError {
  return error instanceof ValidationError;
}

/**
 * Type guard to check if error is an AuthenticationError
 */
export function isAuthenticationError(error: unknown): error is AuthenticationError {
  return error instanceof AuthenticationError;
}

/**
 * Type guard to check if error is a NetworkError
 */
export function isNetworkError(error: unknown): error is NetworkError {
  return error instanceof NetworkError;
}

/**
 * Get user-friendly error message
 */
export function getUserFriendlyErrorMessage(error: unknown): string {
  if (isApiError(error)) {
    return error.message;
  }
  if (isNetworkError(error)) {
    return 'Unable to connect to the server. Please check your internet connection.';
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unexpected error occurred. Please try again.';
}

/**
 * Extract error message from API response detail field
 * Handles both string and array formats from FastAPI backend
 * 
 * FastAPI returns errors in two formats:
 * 1. HTTPException: { detail: "Error message string" }
 * 2. Pydantic validation: { detail: [{ msg: "Error message", type: "...", loc: [...] }] }
 * 
 * @param detail - The detail field from API error response
 * @param fallback - Fallback message if extraction fails
 * @returns Extracted error message
 */
export function extractErrorMessage(detail: unknown, fallback: string): string {
  // Case 1: detail is a string (HTTPException format)
  if (typeof detail === "string") {
    return detail;
  }

  // Case 2: detail is an array (Pydantic validation format)
  if (Array.isArray(detail) && detail.length > 0) {
    const messages = detail
      .map((item: unknown) => {
        if (typeof item === "string") {
          return item;
        }
        if (item && typeof item === "object" && "msg" in item) {
          const msg = (item as { msg?: unknown }).msg;
          return typeof msg === "string" ? msg : "";
        }
        return "";
      })
      .filter((msg) => msg.length > 0);

    if (messages.length > 0) {
      return messages.join("; ");
    }
  }

  // Case 3: Unable to extract message, use fallback
  return fallback;
}
