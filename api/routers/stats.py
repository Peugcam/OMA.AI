"""
Statistics Endpoints
===================

Endpoints for system statistics and metrics.
"""

import time
from datetime import datetime
from fastapi import APIRouter, status, Request

from api.models import StatsResponse
from api.config import settings


router = APIRouter()

# Track stats at module level to avoid circular import
start_time = datetime.now()
stats_data = {
    "total_videos": 0,
    "total_errors": 0,
    "total_cost": 0.0
}


@router.get(
    "/stats",
    response_model=StatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get System Statistics",
    description="Get overall system statistics and metrics"
)
async def get_statistics(request: Request):
    """
    Get system-wide statistics.

    Returns:
        StatsResponse: System statistics
    """
    # Calculate uptime
    uptime = (datetime.now() - start_time).total_seconds()

    # Calculate success rate
    total_videos = stats_data.get("total_videos", 0)
    total_errors = stats_data.get("total_errors", 0)

    if total_videos > 0:
        success_rate = ((total_videos - total_errors) / total_videos) * 100
    else:
        success_rate = 100.0

    # Average generation time (placeholder - implement tracking)
    avg_generation_time = 45.0  # TODO: Track actual times

    return StatsResponse(
        total_videos_generated=total_videos,
        total_cost=stats_data.get("total_cost", 0.0),
        average_generation_time=avg_generation_time,
        success_rate=success_rate,
        uptime_seconds=uptime,
        timestamp=datetime.now()
    )
