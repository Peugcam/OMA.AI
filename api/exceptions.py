"""
Custom Exceptions for API
=========================

Structured exception handling for better error management.
"""

from typing import Optional, Dict, Any


class OMAException(Exception):
    """Base exception for all OMA API errors"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(OMAException):
    """Invalid input data"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, details=details)


class ResourceNotFoundError(OMAException):
    """Requested resource not found"""

    def __init__(self, resource: str, resource_id: str):
        message = f"{resource} with ID '{resource_id}' not found"
        super().__init__(message, status_code=404, details={
            "resource": resource,
            "resource_id": resource_id
        })


class VideoGenerationError(OMAException):
    """Error during video generation process"""

    def __init__(self, message: str, phase: Optional[str] = None):
        details = {"phase": phase} if phase else {}
        super().__init__(message, status_code=500, details=details)


class AgentError(OMAException):
    """Error in agent execution"""

    def __init__(self, agent_name: str, message: str):
        super().__init__(
            f"Agent '{agent_name}' failed: {message}",
            status_code=500,
            details={"agent": agent_name}
        )


class RateLimitError(OMAException):
    """Rate limit exceeded"""

    def __init__(self, retry_after: int):
        super().__init__(
            "Rate limit exceeded. Please try again later.",
            status_code=429,
            details={"retry_after_seconds": retry_after}
        )


class AuthenticationError(OMAException):
    """Authentication failed"""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, status_code=401)


class AuthorizationError(OMAException):
    """Insufficient permissions"""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status_code=403)


class ServiceUnavailableError(OMAException):
    """Service temporarily unavailable"""

    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(message, status_code=503)


class ConfigurationError(OMAException):
    """Configuration error"""

    def __init__(self, message: str, config_key: Optional[str] = None):
        details = {"config_key": config_key} if config_key else {}
        super().__init__(message, status_code=500, details=details)
