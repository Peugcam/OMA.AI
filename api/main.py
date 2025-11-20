"""
OMA Video Generation API - Main Application
===========================================

FastAPI application with all endpoints and middleware.
"""

import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from loguru import logger

from api.config import settings
from api.models import ErrorResponse
from api.exceptions import OMAException
from api.logger import log_api_request, log_error
from api.routers import videos, health, stats


# Application state
app_state: Dict[str, Any] = {
    "start_time": datetime.now(),
    "total_requests": 0,
    "total_videos": 0,
    "total_errors": 0
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"API endpoint: http://{settings.API_HOST}:{settings.API_PORT}{settings.API_PREFIX}")

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}")


# Initialize FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Professional REST API for automated video generation using multi-agent AI",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    lifespan=lifespan
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ============================================
# Middleware
# ============================================

@app.middleware("http")
async def track_requests(request: Request, call_next):
    """Track request metrics and log"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    # Track request count
    app_state["total_requests"] += 1

    # Time the request
    start_time = time.time()

    response = await call_next(request)

    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000

    # Log request
    log_api_request(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms
    )

    # Add custom headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

    return response


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if not settings.DEBUG else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Exception Handlers
# ============================================

@app.exception_handler(OMAException)
async def oma_exception_handler(request: Request, exc: OMAException):
    """Handle custom OMA exceptions"""
    app_state["total_errors"] += 1

    log_error(
        error_type=exc.__class__.__name__,
        message=exc.message,
        context={
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            message=exc.message,
            details=exc.details,
            request_id=getattr(request.state, "request_id", None)
        ).model_dump()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    app_state["total_errors"] += 1

    errors = exc.errors()
    log_error(
        error_type="ValidationError",
        message="Request validation failed",
        context={"errors": errors, "path": request.url.path}
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="ValidationError",
            message="Invalid request data",
            details={"validation_errors": errors},
            request_id=getattr(request.state, "request_id", None)
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    app_state["total_errors"] += 1

    log_error(
        error_type="InternalServerError",
        message=str(exc),
        context={"path": request.url.path},
        exc_info=exc
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred" if settings.is_production else str(exc),
            request_id=getattr(request.state, "request_id", None)
        ).model_dump()
    )


# ============================================
# Include Routers
# ============================================

app.include_router(health.router, prefix=settings.API_PREFIX, tags=["Health"])
app.include_router(videos.router, prefix=settings.API_PREFIX, tags=["Videos"])
app.include_router(stats.router, prefix=settings.API_PREFIX, tags=["Statistics"])


# ============================================
# Root Endpoint
# ============================================

@app.get("/")
async def root():
    """API root - basic information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": f"{settings.API_PREFIX}/docs",
        "health": f"{settings.API_PREFIX}/health"
    }
