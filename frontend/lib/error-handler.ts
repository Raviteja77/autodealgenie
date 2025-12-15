/**
 * Structured Error Handler for Frontend API Responses
 * 
 * This module provides a TypeScript ApiError class for handling API responses
 * with structured error information including HTTP status codes, messages,
 * and optional details.
 */

/**
 * Custom TypeScript ApiError class for structured error handling
 * 
 * Enables structured error handling for API responses on the frontend,
 * including HTTP statusCode, error message, and optional details.
 */
export class ApiError extends Error {
  /**
   * HTTP status code (e.g., 400, 401, 404, 500)
   */
  public statusCode: number;

  /**
   * Optional additional error details or context
   */
  public details?: unknown;

  /**
   * Create a new ApiError instance
   * 
   * @param message - Human-readable error message
   * @param statusCode - HTTP status code
   * @param details - Optional additional error details
   */
  constructor(message: string, statusCode: number, details?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.details = details;

    // Maintains proper prototype chain for instanceof checks
    Object.setPrototypeOf(this, ApiError.prototype);
  }

  /**
   * Convert error to JSON-serializable object
   * 
   * @returns Object representation of the error
   */
  toJSON(): Record<string, unknown> {
    return {
      name: this.name,
      message: this.message,
      statusCode: this.statusCode,
      ...(this.details && { details: this.details }),
    };
  }

  /**
   * Check if an error is an ApiError instance
   * 
   * @param error - Error to check
   * @returns True if error is an ApiError
   */
  static isApiError(error: unknown): error is ApiError {
    return error instanceof ApiError;
  }

  /**
   * Create an ApiError from a fetch Response object
   * 
   * @param response - Fetch API Response object
   * @param defaultMessage - Default message if response doesn't contain one
   * @returns ApiError instance
   */
  static async fromResponse(
    response: Response,
    defaultMessage: string = 'Request failed'
  ): Promise<ApiError> {
    let errorData: any;
    let errorMessage = defaultMessage;

    try {
      errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || defaultMessage;
    } catch {
      // If JSON parsing fails, use status text or default
      errorMessage = response.statusText || defaultMessage;
    }

    return new ApiError(errorMessage, response.status, errorData);
  }

  /**
   * Get user-friendly error message based on status code
   * 
   * @returns User-friendly error message
   */
  getUserFriendlyMessage(): string {
    switch (this.statusCode) {
      case 400:
        return this.message || 'Invalid request. Please check your input.';
      case 401:
        return 'Authentication required. Please log in.';
      case 403:
        return 'Access forbidden. You do not have permission to perform this action.';
      case 404:
        return this.message || 'The requested resource was not found.';
      case 422:
        return this.message || 'Validation failed. Please check your input.';
      case 500:
        return 'Internal server error. Please try again later.';
      case 502:
      case 503:
      case 504:
        return 'Server is temporarily unavailable. Please try again later.';
      default:
        return this.message || 'An error occurred. Please try again.';
    }
  }

  /**
   * Check if error is a client error (4xx)
   * 
   * @returns True if status code is in 400-499 range
   */
  isClientError(): boolean {
    return this.statusCode >= 400 && this.statusCode < 500;
  }

  /**
   * Check if error is a server error (5xx)
   * 
   * @returns True if status code is in 500-599 range
   */
  isServerError(): boolean {
    return this.statusCode >= 500 && this.statusCode < 600;
  }

  /**
   * Check if error indicates authentication failure
   * 
   * @returns True if status code is 401
   */
  isAuthenticationError(): boolean {
    return this.statusCode === 401;
  }

  /**
   * Check if error indicates authorization failure
   * 
   * @returns True if status code is 403
   */
  isAuthorizationError(): boolean {
    return this.statusCode === 403;
  }

  /**
   * Check if error indicates validation failure
   * 
   * @returns True if status code is 422
   */
  isValidationError(): boolean {
    return this.statusCode === 422;
  }
}

/**
 * Type guard to check if an error is an ApiError
 * 
 * @param error - Error to check
 * @returns True if error is an ApiError
 */
export function isApiError(error: unknown): error is ApiError {
  return ApiError.isApiError(error);
}

/**
 * Handle API errors with consistent logging and error transformation
 * 
 * @param error - Error to handle
 * @param context - Optional context for logging
 * @returns ApiError instance
 */
export function handleApiError(error: unknown, context?: string): ApiError {
  // If already an ApiError, return as-is
  if (isApiError(error)) {
    if (context) {
      console.error(`[${context}] API Error:`, error.toJSON());
    }
    return error;
  }

  // Convert other errors to ApiError
  if (error instanceof Error) {
    const apiError = new ApiError(error.message, 500, { originalError: error.name });
    if (context) {
      console.error(`[${context}] Unexpected Error:`, apiError.toJSON());
    }
    return apiError;
  }

  // Handle unknown error types
  const apiError = new ApiError('An unexpected error occurred', 500, { error });
  if (context) {
    console.error(`[${context}] Unknown Error:`, apiError.toJSON());
  }
  return apiError;
}

export default ApiError;
