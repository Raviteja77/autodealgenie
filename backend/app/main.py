"""
AutoDealGenie FastAPI Application
Main entry point for the backend service
"""
import uuid
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.middleware.error_middleware import ErrorHandlerMiddleware
from app.core.logging import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    configure_logging()
    print("Starting up AutoDealGenie backend...")
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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Request ID Middleware
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
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

# Global Error Handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Internal Server Error", "request_id": getattr(request.state, "request_id", None)},
    )


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
