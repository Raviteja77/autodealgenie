# Structured Error Handling Implementation

This document describes the structured error handling implementation for AutoDealGenie.

## Overview

This implementation introduces consistent error handling across both backend (Python) and frontend (TypeScript) components.

## Backend Implementation

### 1. ApiError Class (`backend/app/utils/error_handler.py`)

A custom exception class for creating structured error objects:

```python
from app.utils.error_handler import ApiError

# Basic usage
raise ApiError(status_code=404, message="Resource not found")

# With additional details
raise ApiError(
    status_code=422,
    message="Validation failed",
    details={"field": "email", "reason": "invalid format"}
)

# Convert to dictionary for JSON responses
error = ApiError(status_code=400, message="Bad request")
error_dict = error.to_dict()  # {'status_code': 400, 'message': 'Bad request'}
```

### 2. Error Middleware (`backend/app/middleware/error_middleware.py`)

Middleware that catches `ApiError` exceptions and returns standardized JSON responses:

**Features:**
- Automatically catches `ApiError` exceptions
- Returns structured JSON error responses
- Logs errors with context (path, method, status code)
- Handles unexpected exceptions gracefully
- Returns 500 error for unexpected exceptions

**Response Format:**
```json
{
  "detail": "Error message",
  "status_code": 404,
  "details": {
    "additional": "context"
  }
}
```

### 3. Integration (`backend/app/main.py`)

The middleware is registered in the FastAPI application:

```python
from app.middleware.error_middleware import ErrorHandlerMiddleware

app = FastAPI(...)
app.add_middleware(ErrorHandlerMiddleware)
```

### Usage Examples

**In API Endpoints:**

```python
from fastapi import APIRouter, Depends
from app.utils.error_handler import ApiError
from app.repositories.user_repository import UserRepository

router = APIRouter()

@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    
    if not user:
        raise ApiError(
            status_code=404,
            message="User not found",
            details={"user_id": user_id}
        )
    
    return user
```

**In Services:**

```python
from app.utils.error_handler import ApiError

class MyService:
    def process_data(self, data):
        if not self.validate(data):
            raise ApiError(
                status_code=422,
                message="Invalid data",
                details={"validation_errors": self.get_errors()}
            )
        
        return self.process(data)
```

## Frontend Implementation

### ApiError Class (`frontend/lib/error-handler.ts`)

A TypeScript class for handling API errors on the frontend:

```typescript
import { ApiError, isApiError, handleApiError } from '@/lib/error-handler';

// Basic usage
const error = new ApiError('Not found', 404);

// With details
const error = new ApiError(
  'Validation failed',
  422,
  { field: 'email', reason: 'invalid' }
);

// Create from fetch Response
try {
  const response = await fetch('/api/endpoint');
  if (!response.ok) {
    const error = await ApiError.fromResponse(response);
    throw error;
  }
} catch (error) {
  if (isApiError(error)) {
    console.error('API Error:', error.statusCode, error.message);
  }
}

// Get user-friendly messages
const error = new ApiError('Auth failed', 401);
const message = error.getUserFriendlyMessage(); // "Authentication required. Please log in."

// Type checking
if (error.isAuthenticationError()) {
  // Redirect to login
}

if (error.isValidationError()) {
  // Show validation errors
}
```

### Usage in API Calls

```typescript
import { ApiError, handleApiError } from '@/lib/error-handler';

async function fetchData() {
  try {
    const response = await fetch('/api/v1/data', {
      method: 'GET',
      credentials: 'include',
    });

    if (!response.ok) {
      const apiError = await ApiError.fromResponse(response);
      throw apiError;
    }

    return await response.json();
  } catch (error) {
    // Convert to ApiError and handle
    const apiError = handleApiError(error, 'fetchData');
    
    // Show user-friendly message
    toast.error(apiError.getUserFriendlyMessage());
    
    // Handle specific error types
    if (apiError.isAuthenticationError()) {
      router.push('/login');
    }
    
    throw apiError;
  }
}
```

## Benefits

1. **Consistency**: Standardized error format across backend and frontend
2. **Type Safety**: TypeScript types for frontend errors
3. **Debugging**: Structured logging with context
4. **User Experience**: User-friendly error messages
5. **Flexibility**: Support for additional error details
6. **Maintainability**: Centralized error handling logic

## Testing

### Backend Tests

- `tests/test_error_handler.py`: Tests for ApiError class (9 tests)
- `tests/test_error_middleware.py`: Tests for error middleware (7 tests)

All tests pass with 100% coverage on error handling code.

### Running Tests

```bash
cd backend
pytest tests/test_error_handler.py tests/test_error_middleware.py -v
```

## HTTP Status Codes

The implementation supports standard HTTP status codes:

- **400**: Bad Request
- **401**: Unauthorized (Authentication required)
- **403**: Forbidden (Authorization failed)
- **404**: Not Found
- **422**: Unprocessable Entity (Validation failed)
- **500**: Internal Server Error
- **502-504**: Server unavailable errors

## Migration Guide

### For Existing Endpoints

Replace `HTTPException` with `ApiError`:

**Before:**
```python
from fastapi import HTTPException

raise HTTPException(status_code=404, detail="Not found")
```

**After:**
```python
from app.utils.error_handler import ApiError

raise ApiError(status_code=404, message="Not found")
```

### For Frontend

The existing `errors.ts` file can work alongside `error-handler.ts`. The new `error-handler.ts` provides additional functionality like:

- `fromResponse()` method for creating errors from fetch responses
- `getUserFriendlyMessage()` for displaying error messages
- Type checking methods (`isAuthenticationError()`, `isValidationError()`, etc.)
- JSON serialization with `toJSON()`

## Future Enhancements

1. **Error Tracking**: Integration with Sentry or similar error tracking services
2. **Error Recovery**: Automatic retry logic for transient errors
3. **Rate Limiting**: Specific error responses for rate limit violations
4. **Localization**: Multi-language error messages
5. **Error Analytics**: Track error patterns for monitoring
