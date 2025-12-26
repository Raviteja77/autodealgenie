"""
AutoDealGenie FastAPI Application
Main entry point for the backend service
"""

import asyncio
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.metrics import initialize_metrics
from app.services.kafka_consumer import deals_consumer, handle_deal_message
from app.services.kafka_producer import kafka_producer
from app.middleware.error_middleware import ErrorHandlerMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    configure_logging()
    initialize_metrics()
    consumer_tasks = []
    print("Starting up AutoDealGenie backend...")

    # Import here to avoid circular dependency issues during module initialization
    from app.db.mongodb import mongodb
    from app.db.redis import redis_client

    # Initialize MongoDB connection
    try:
        await mongodb.connect_db()
        print(f"MongoDB connected to {settings.MONGODB_DB_NAME} database")
    except Exception as e:
        print(f"CRITICAL: Failed to initialize MongoDB: {e}")
        print("Application cannot start without MongoDB. Please check your configuration.")
        raise

    # Initialize Redis connection
    try:
        await redis_client.connect_redis()
        print("Redis connected successfully")
    except Exception as e:
        print(f"CRITICAL: Failed to initialize Redis: {e}")
        print("Application cannot start without Redis. Please check your configuration.")
        raise

    # Initialize Kafka producer and consumers
    try:
        await kafka_producer.start()
        await deals_consumer.start()
        # Start consumer in background task
        deals_task = asyncio.create_task(deals_consumer.consume_messages(handle_deal_message))
        consumer_tasks.append(deals_task)
        print("Kafka services initialized successfully")
    except Exception as e:
        print(f"WARNING: Failed to initialize Kafka: {e}")
        print("Application will continue without Kafka features.")

    if settings.USE_MOCK_SERVICES:
        print("Mock services are ENABLED - using mock endpoints for development")
    yield
    # Shutdown
    print("Shutting down AutoDealGenie backend...")

    # Close connections
    await mongodb.close_db()
    print("MongoDB connection closed")

    await redis_client.close_redis()
    print("Redis connection closed")

    # Stop Kafka consumers and producer
    for task in consumer_tasks:
        task.cancel()
    await asyncio.gather(*consumer_tasks, return_exceptions=True)
    await deals_consumer.stop()
    await kafka_producer.stop()
    print("Kafka services stopped")


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

# Initialize Prometheus instrumentation
# This should be done after all routes are registered
instrumentator = Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
    should_respect_env_var=False,  # Always enable metrics
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/metrics", "/health"],
    inprogress_name="autodealgenie_requests_inprogress",
    inprogress_labels=True,
)
instrumentator.instrument(app).expose(app, endpoint="/metrics", include_in_schema=True)


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
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data: https://cdn.jsdelivr.net;"
    )

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
