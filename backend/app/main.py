"""
AutoDealGenie FastAPI Application
Main entry point for the backend service
"""
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.middleware.error_middleware import ErrorHandlerMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    configure_logging()
    print("Starting up AutoDealGenie backend...")
    if settings.USE_MOCK_SERVICES:
        print("Mock services are ENABLED - using mock endpoints for development")
    yield
    # Shutdown
    print("Shutting down AutoDealGenie backend...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Error handling middleware (should be added first to catch all errors)
app.add_middleware(ErrorHandlerMiddleware)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware - restrict in production
allowed_methods = (
    ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    if settings.ENVIRONMENT == "production"
    else ["*"]
)
allowed_headers = (
    ["Content-Type", "Authorization", "X-Request-ID"]
    if settings.ENVIRONMENT == "production"
    else ["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=allowed_methods,
    expose_headers=["X-Request-ID", "X-Process-Time"],
    allow_headers=allowed_headers,
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Conditionally include mock router if USE_MOCK_SERVICES is enabled
if settings.USE_MOCK_SERVICES:
    from app.api.mock import mock_router

    app.include_router(mock_router, prefix="/mock")
    print("Mock router registered at /mock")


# Request ID Middleware
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """
    Middleware that generates a unique request ID for each HTTP request, tracks processing time,
    and adds both as headers to the response.
    Parameters:
        request (Request): The incoming HTTP request.
        call_next (Callable): The next middleware or route handler to call.
    Returns:
        Response: The HTTP response with 'X-Request-ID' and 'X-Process-Time' headers added.
    """
    request_id = str(uuid.uuid4())
    # Bind request_id to the request state for access in endpoints/logs
    request.state.request_id = request_id

    # Start timer
    start_time = time.time()

    response = await call_next(request)

    # Add processing time and request ID to headers
    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)

    return response


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to AutoDealGenie API",
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
