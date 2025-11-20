"""
Health Check Endpoints
=====================

Endpoints for monitoring API health and readiness.
"""

import time
from datetime import datetime
from fastapi import APIRouter, status
from loguru import logger

from api.models import HealthCheckResponse
from api.config import settings


router = APIRouter()

# Track app start time
START_TIME = time.time()


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check if the API is running and healthy"
)
async def health_check():
    """
    Basic health check endpoint.

    Returns:
        HealthCheckResponse: Current health status
    """
    uptime_seconds = time.time() - START_TIME

    # Check critical components
    checks = {
        "api": True,
        "openai_config": settings.validate_openai_config(),
        "output_directory": settings.OUTPUT_DIR.exists(),
        "temp_directory": settings.TEMP_DIR.exists(),
    }

    # Overall health
    is_healthy = all(checks.values())
    health_status = "healthy" if is_healthy else "unhealthy"

    logger.debug(f"Health check: {health_status}, uptime={uptime_seconds:.2f}s")

    return HealthCheckResponse(
        status=health_status,
        version=settings.APP_VERSION,
        uptime_seconds=uptime_seconds,
        timestamp=datetime.now(),
        checks=checks
    )


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness Check",
    description="Check if the API is ready to accept requests"
)
async def readiness_check():
    """
    Readiness check for K8s/orchestration.

    Returns:
        dict: Ready status
    """
    # Check if OpenAI is configured
    if not settings.validate_openai_config():
        logger.warning("Readiness check failed: OpenAI not configured")
        return {
            "ready": False,
            "reason": "OpenAI API key not configured"
        }

    # Check if output directory is writable
    if not settings.OUTPUT_DIR.exists():
        logger.warning("Readiness check failed: Output directory missing")
        return {
            "ready": False,
            "reason": "Output directory not available"
        }

    return {
        "ready": True,
        "timestamp": datetime.now().isoformat()
    }


@router.get(
    "/ping",
    status_code=status.HTTP_200_OK,
    summary="Ping",
    description="Simple ping endpoint"
)
async def ping():
    """Minimal health check - just returns pong"""
    return {"ping": "pong"}
