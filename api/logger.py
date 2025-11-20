"""
Structured Logging with Loguru
==============================

Centralized logging configuration for the entire application.
"""

import sys
import json
from pathlib import Path
from typing import Any, Dict
from loguru import logger
from datetime import datetime


class LogConfig:
    """Logging configuration"""

    def __init__(
        self,
        log_level: str = "INFO",
        log_file: Path = Path("./logs/api.log"),
        log_format: str = "json",
        rotation: str = "100 MB"
    ):
        self.log_level = log_level
        self.log_file = log_file
        self.log_format = log_format
        self.rotation = rotation

    def setup(self):
        """Configure loguru logger"""

        # Remove default logger
        logger.remove()

        # Console logging (human-readable for development)
        if self.log_format == "text":
            console_format = (
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            )
        else:
            console_format = "{message}"

        logger.add(
            sys.stderr,
            format=console_format,
            level=self.log_level,
            colorize=True,
            serialize=(self.log_format == "json")
        )

        # File logging (JSON for structured logs)
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)

            logger.add(
                str(self.log_file),
                format="{message}",
                level=self.log_level,
                rotation=self.rotation,
                compression="zip",
                serialize=True,  # Always JSON for files
                enqueue=True,    # Thread-safe
                backtrace=True,  # Full stack trace on errors
                diagnose=True    # Better error context
            )

        logger.info(f"Logging configured: level={self.log_level}, format={self.log_format}")


def log_api_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    user_id: str = None
):
    """
    Log API request in structured format.

    Args:
        method: HTTP method (GET, POST, etc.)
        path: Request path
        status_code: HTTP status code
        duration_ms: Request duration in milliseconds
        user_id: Optional user identifier
    """
    log_data = {
        "event": "api_request",
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
        "timestamp": datetime.now().isoformat()
    }

    if user_id:
        log_data["user_id"] = user_id

    # Log level based on status code
    if status_code >= 500:
        logger.error(json.dumps(log_data))
    elif status_code >= 400:
        logger.warning(json.dumps(log_data))
    else:
        logger.info(json.dumps(log_data))


def log_video_generation(
    task_id: str,
    phase: str,
    status: str,
    duration_seconds: float = None,
    cost: float = None,
    error: str = None
):
    """
    Log video generation event.

    Args:
        task_id: Unique task identifier
        phase: Generation phase (analysis, script, visual, audio, editing)
        status: Status (started, completed, failed)
        duration_seconds: Phase duration
        cost: Cost in USD
        error: Error message if failed
    """
    log_data = {
        "event": "video_generation",
        "task_id": task_id,
        "phase": phase,
        "status": status,
        "timestamp": datetime.now().isoformat()
    }

    if duration_seconds is not None:
        log_data["duration_seconds"] = round(duration_seconds, 2)

    if cost is not None:
        log_data["cost_usd"] = round(cost, 4)

    if error:
        log_data["error"] = error

    if status == "failed":
        logger.error(json.dumps(log_data))
    elif status == "completed":
        logger.success(json.dumps(log_data))
    else:
        logger.info(json.dumps(log_data))


def log_agent_execution(
    agent_name: str,
    task_id: str,
    action: str,
    status: str,
    metadata: Dict[str, Any] = None
):
    """
    Log agent execution.

    Args:
        agent_name: Name of the agent
        task_id: Task identifier
        action: Action being performed
        status: Execution status
        metadata: Additional metadata
    """
    log_data = {
        "event": "agent_execution",
        "agent": agent_name,
        "task_id": task_id,
        "action": action,
        "status": status,
        "timestamp": datetime.now().isoformat()
    }

    if metadata:
        log_data["metadata"] = metadata

    if status == "failed":
        logger.error(json.dumps(log_data))
    else:
        logger.info(json.dumps(log_data))


def log_error(
    error_type: str,
    message: str,
    context: Dict[str, Any] = None,
    exc_info: Exception = None
):
    """
    Log error with full context.

    Args:
        error_type: Type of error
        message: Error message
        context: Additional context
        exc_info: Exception object for stack trace
    """
    log_data = {
        "event": "error",
        "error_type": error_type,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }

    if context:
        log_data["context"] = context

    if exc_info:
        logger.exception(json.dumps(log_data))
    else:
        logger.error(json.dumps(log_data))


# Initialize with default config
log_config = LogConfig()
log_config.setup()
