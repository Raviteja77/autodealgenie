# API Response Examples

This document provides comprehensive examples of API responses for all AutoDealGenie endpoints.

## Table of Contents

1. [Authentication Endpoints](#authentication-endpoints)
2. [Deal Endpoints](#deal-endpoints)
3. [User Endpoints](#user-endpoints)
4. [Error Responses](#error-responses)

---

## Authentication Endpoints

### POST /api/v1/auth/signup

**Request:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePassword123!",
  "full_name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-12-25T16:30:00.000Z",
  "updated_at": null
}
```

**Error Response (400 Bad Request) - Duplicate Email:**
```json
{
  "detail": "Email already registered"
}
```

**Error Response (422 Unprocessable Entity) - Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    },
    {
      "loc": ["body", "password"],
      "msg": "ensure this value has at least 8 characters",
      "type": "value_error.any_str.min_length",
      "ctx": {"limit_value": 8}
    }
  ]
}
```

---

### POST /api/v1/auth/login

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "is_active": true,
    "is_superuser": false
  }
}
```

**Set-Cookie Header:**
```
access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...; Path=/; HttpOnly; SameSite=Lax; Max-Age=1800
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Incorrect email or password"
}
```

---

### GET /api/v1/auth/me

**Headers:**
```
Cookie: access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-12-25T16:30:00.000Z",
  "updated_at": null
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Not authenticated"
}
```

---

## Deal Endpoints

### GET /api/v1/deals/

**Query Parameters:**
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)
- `status`: string (optional: pending, in_progress, completed, cancelled)

**Headers:**
```
Cookie: access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "customer_name": "Jane Smith",
    "customer_email": "jane@example.com",
    "vehicle_make": "Toyota",
    "vehicle_model": "Camry",
    "vehicle_year": 2022,
    "vehicle_mileage": 15000,
    "vehicle_vin": "1HGBH41JXMN109186",
    "asking_price": 28000.00,
    "offer_price": 26500.00,
    "status": "in_progress",
    "notes": "Clean vehicle history, single owner",
    "created_at": "2025-12-20T10:00:00.000Z",
    "updated_at": "2025-12-24T15:30:00.000Z"
  },
  {
    "id": 2,
    "customer_name": "Bob Johnson",
    "customer_email": "bob@example.com",
    "vehicle_make": "Honda",
    "vehicle_model": "Accord",
    "vehicle_year": 2023,
    "vehicle_mileage": 8000,
    "vehicle_vin": "1HGCY1F30LA000001",
    "asking_price": 32000.00,
    "offer_price": null,
    "status": "pending",
    "notes": "Interested in hybrid model",
    "created_at": "2025-12-24T21:00:00.000Z",
    "updated_at": null
  }
]
```

---

### POST /api/v1/deals/

**Headers:**
```
Cookie: access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

**Request:**
```json
{
  "customer_name": "Alice Brown",
  "customer_email": "alice@example.com",
  "vehicle_make": "Ford",
  "vehicle_model": "F-150",
  "vehicle_year": 2023,
  "vehicle_mileage": 5000,
  "vehicle_vin": "1FTFW1E59MKE00001",
  "asking_price": 45000.00,
  "notes": "Looking for XLT trim with towing package"
}
```

**Response (201 Created):**
```json
{
  "id": 3,
  "customer_name": "Alice Brown",
  "customer_email": "alice@example.com",
  "vehicle_make": "Ford",
  "vehicle_model": "F-150",
  "vehicle_year": 2023,
  "vehicle_mileage": 5000,
  "vehicle_vin": "1FTFW1E59MKE00001",
  "asking_price": 45000.00,
  "offer_price": null,
  "status": "pending",
  "notes": "Looking for XLT trim with towing package",
  "created_at": "2025-12-25T16:35:00.000Z",
  "updated_at": null
}
```

**Error Response (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "loc": ["body", "vehicle_year"],
      "msg": "ensure this value is greater than or equal to 1900",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

---

### GET /api/v1/deals/{deal_id}

**Headers:**
```
Cookie: access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "id": 1,
  "customer_name": "Jane Smith",
  "customer_email": "jane@example.com",
  "vehicle_make": "Toyota",
  "vehicle_model": "Camry",
  "vehicle_year": 2022,
  "vehicle_mileage": 15000,
  "vehicle_vin": "1HGBH41JXMN109186",
  "asking_price": 28000.00,
  "offer_price": 26500.00,
  "status": "in_progress",
  "notes": "Clean vehicle history, single owner",
  "created_at": "2025-12-20T10:00:00.000Z",
  "updated_at": "2025-12-24T15:30:00.000Z"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Deal not found"
}
```

---

### PUT /api/v1/deals/{deal_id}

**Headers:**
```
Cookie: access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

**Request:**
```json
{
  "offer_price": 27000.00,
  "status": "in_progress",
  "notes": "Negotiating final price, customer interested"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "customer_name": "Jane Smith",
  "customer_email": "jane@example.com",
  "vehicle_make": "Toyota",
  "vehicle_model": "Camry",
  "vehicle_year": 2022,
  "vehicle_mileage": 15000,
  "vehicle_vin": "1HGBH41JXMN109186",
  "asking_price": 28000.00,
  "offer_price": 27000.00,
  "status": "in_progress",
  "notes": "Negotiating final price, customer interested",
  "created_at": "2025-12-20T10:00:00.000Z",
  "updated_at": "2025-12-25T16:40:00.000Z"
}
```

---

### DELETE /api/v1/deals/{deal_id}

**Headers:**
```
Cookie: access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (204 No Content)**

No response body.

**Error Response (404 Not Found):**
```json
{
  "detail": "Deal not found"
}
```

---

## Health Endpoints

### GET /health

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-25T16:45:00.000Z",
  "version": "1.0.0"
}
```

---

## Error Responses

### Common HTTP Status Codes

#### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

#### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

#### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

#### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

#### 422 Unprocessable Entity (Validation Error)
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

#### 503 Service Unavailable
```json
{
  "detail": "Service temporarily unavailable"
}
```

---

## Response Headers

All API responses include the following headers:

- `X-Request-ID`: Unique identifier for the request (UUID format)
- `X-Process-Time`: Time taken to process the request (in seconds)
- `Content-Type`: `application/json`
- `X-Frame-Options`: `DENY`
- `X-Content-Type-Options`: `nosniff`
- `X-XSS-Protection`: `1; mode=block`

**Example:**
```
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-Process-Time: 0.025
Content-Type: application/json
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
```

---

## Pagination

For endpoints that return lists, use the `skip` and `limit` query parameters:

**Request:**
```
GET /api/v1/deals/?skip=20&limit=10
```

This retrieves items 21-30.

---

## Filtering

Some endpoints support filtering via query parameters:

**Request:**
```
GET /api/v1/deals/?status=in_progress&vehicle_make=Toyota
```

---

## Testing Tips

1. **Authentication**: Always include the `access_token` cookie for protected endpoints
2. **Content-Type**: Set `Content-Type: application/json` for POST/PUT requests
3. **Request ID**: Track requests using the `X-Request-ID` response header
4. **Error Handling**: Check both status code and `detail` field for error information
5. **Validation**: FastAPI returns detailed validation errors in the `detail` array

---

## Postman Collection

Import the provided Postman collection for easy API testing:
- File: `postman_collection.json` (to be created)
- Includes all endpoints with example requests
- Pre-configured environment variables
- Automated token management

---

## cURL Examples

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}' \
  -c cookies.txt
```

### Get Deals (with authentication)
```bash
curl -X GET http://localhost:8000/api/v1/deals/ \
  -b cookies.txt
```

### Create Deal
```bash
curl -X POST http://localhost:8000/api/v1/deals/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "vehicle_make": "Tesla",
    "vehicle_model": "Model 3",
    "vehicle_year": 2023,
    "vehicle_mileage": 1000,
    "vehicle_vin": "5YJ3E1EA1KF000001",
    "asking_price": 42000.00
  }'
```
