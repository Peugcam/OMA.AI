"""
Video Generation Endpoints
==========================

Main endpoints for video generation operations.
"""

import asyncio
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from loguru import logger

from api.models import (
    VideoGenerationRequest,
    VideoGenerationResponse,
    TaskStatusResponse,
    VideoBriefing,
    VideoMetadata,
    SceneInfo
)
from api.exceptions import (
    VideoGenerationError,
    ResourceNotFoundError,
    ValidationError
)
from api.config import settings
from api.logger import log_video_generation
from quick_generate import generate_video


router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# In-memory task storage (replace with Redis in production)
tasks: Dict[str, Dict] = {}


async def _generate_video_async(task_id: str, briefing: dict):
    """
    Background task for video generation.

    Args:
        task_id: Unique task identifier
        briefing: Video briefing dictionary
    """
    try:
        # Update task status
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["current_phase"] = "initializing"
        tasks[task_id]["updated_at"] = datetime.now()

        log_video_generation(task_id, "all", "started")

        # Generate video
        result = await generate_video(briefing)

        # Update task with result
        if result["success"]:
            tasks[task_id]["status"] = "completed"
            tasks[task_id]["result"] = VideoGenerationResponse(
                success=True,
                task_id=task_id,
                video_path=result.get("video_path"),
                metadata=VideoMetadata(
                    title=briefing.get("title", ""),
                    duration=result.get("metadata", {}).get("duration", 0),
                    resolution=result.get("metadata", {}).get("resolution", "1920x1080"),
                    fps=result.get("metadata", {}).get("fps", 30),
                    codec=result.get("metadata", {}).get("codec", "h264"),
                ),
                scenes=[],
                total_cost=result.get("cost", 0.0),
                generation_time_seconds=result.get("generation_time", 0),
                timestamp=datetime.fromisoformat(result["timestamp"])
            )
            tasks[task_id]["progress"] = 100

            log_video_generation(
                task_id,
                "all",
                "completed",
                cost=result.get("cost", 0.0)
            )
        else:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["error_message"] = result.get("error", "Unknown error")

            log_video_generation(
                task_id,
                "all",
                "failed",
                error=result.get("error")
            )

    except Exception as e:
        logger.exception(f"Video generation failed for task {task_id}")
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error_message"] = str(e)

        log_video_generation(task_id, "all", "failed", error=str(e))

    finally:
        tasks[task_id]["updated_at"] = datetime.now()


@router.post(
    "/videos/generate",
    response_model=VideoGenerationResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate Video",
    description="Generate a video from a briefing. Returns task_id for async tracking."
)
@limiter.limit("5/minute")
async def generate_video_endpoint(
    request: Request,
    video_request: VideoGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate a video based on the provided briefing.

    **Async Mode:**
    - Returns immediately with task_id
    - Use `/videos/status/{task_id}` to check progress

    **Sync Mode:**
    - Waits for video generation to complete
    - Returns final video path and metadata

    Args:
        request: Video generation request with briefing

    Returns:
        VideoGenerationResponse: Task information
    """
    # Generate task ID
    task_id = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Convert Pydantic model to dict
    briefing_dict = video_request.briefing.model_dump()

    # Create task record
    tasks[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "progress": 0,
        "current_phase": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "briefing": briefing_dict,
        "result": None,
        "error_message": None
    }

    logger.info(f"Video generation task created: {task_id}")

    # Start generation in background
    background_tasks.add_task(_generate_video_async, task_id, briefing_dict)

    # Return task info
    return VideoGenerationResponse(
        success=True,
        task_id=task_id,
        timestamp=datetime.now()
    )


@router.get(
    "/videos/status/{task_id}",
    response_model=TaskStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Video Generation Status",
    description="Check the status of a video generation task"
)
async def get_video_status(task_id: str):
    """
    Get the status of a video generation task.

    Args:
        task_id: Task identifier from generate endpoint

    Returns:
        TaskStatusResponse: Current task status

    Raises:
        ResourceNotFoundError: If task_id not found
    """
    if task_id not in tasks:
        raise ResourceNotFoundError(resource="Task", resource_id=task_id)

    task = tasks[task_id]

    return TaskStatusResponse(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        current_phase=task["current_phase"],
        result=task["result"],
        created_at=task["created_at"],
        updated_at=task["updated_at"],
        error_message=task["error_message"]
    )


@router.get(
    "/videos/tasks",
    status_code=status.HTTP_200_OK,
    summary="List All Tasks",
    description="Get a list of all video generation tasks"
)
async def list_tasks(
    status_filter: Optional[str] = None,
    limit: int = 50
):
    """
    List all video generation tasks.

    Args:
        status_filter: Filter by status (pending, processing, completed, failed)
        limit: Maximum number of tasks to return

    Returns:
        List of task summaries
    """
    task_list = []

    for task_id, task_data in list(tasks.items())[:limit]:
        # Apply status filter
        if status_filter and task_data["status"] != status_filter:
            continue

        task_list.append({
            "task_id": task_id,
            "status": task_data["status"],
            "progress": task_data["progress"],
            "created_at": task_data["created_at"].isoformat(),
            "updated_at": task_data["updated_at"].isoformat(),
            "title": task_data["briefing"].get("title", "")
        })

    return {
        "tasks": task_list,
        "total": len(task_list),
        "filtered": status_filter is not None
    }


@router.delete(
    "/videos/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Task",
    description="Delete a task record (completed or failed only)"
)
async def delete_task(task_id: str):
    """
    Delete a task record.

    Args:
        task_id: Task identifier

    Raises:
        ResourceNotFoundError: If task not found
        ValidationError: If task is still processing
    """
    if task_id not in tasks:
        raise ResourceNotFoundError(resource="Task", resource_id=task_id)

    task = tasks[task_id]

    # Don't allow deleting active tasks
    if task["status"] in ["pending", "processing"]:
        raise ValidationError(
            "Cannot delete active task. Wait for completion or failure.",
            details={"task_id": task_id, "status": task["status"]}
        )

    # Delete task
    del tasks[task_id]
    logger.info(f"Task deleted: {task_id}")

    return None
