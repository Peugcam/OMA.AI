"""
Pydantic Models for Request/Response Validation
===============================================

All API data models with strict validation.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator, field_validator


class VideoStyle(str, Enum):
    """Available video styles"""
    PROFESSIONAL = "professional"
    MODERN = "modern"
    MINIMALIST = "minimalist"
    ENERGETIC = "energetic"
    ELEGANT = "elegant"


class VideoTone(str, Enum):
    """Available video tones"""
    NEUTRAL = "neutral"
    ENTHUSIASTIC = "enthusiastic"
    CALM = "calm"
    INSPIRING = "inspiring"
    URGENT = "urgent"


class TemplateType(str, Enum):
    """Pre-defined templates"""
    CUSTOM = "custom"
    PRODUCT_TECH = "product_tech"
    EDUCATIONAL = "educational"
    SOCIAL_MEDIA = "social_media"
    CORPORATE = "corporate"


class VideoBriefing(BaseModel):
    """Video generation briefing request"""

    title: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Video title",
        examples=["Lançamento de Produto Inovador"]
    )

    description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Detailed video description and structure",
        examples=["Vídeo de apresentação de produto tecnológico..."]
    )

    duration: int = Field(
        default=30,
        ge=15,
        le=180,
        description="Video duration in seconds (15-180s)"
    )

    target_audience: str = Field(
        default="Público geral",
        min_length=3,
        max_length=200,
        description="Target audience description"
    )

    style: VideoStyle = Field(
        default=VideoStyle.PROFESSIONAL,
        description="Visual style of the video"
    )

    tone: VideoTone = Field(
        default=VideoTone.NEUTRAL,
        description="Narrative tone"
    )

    cta: str = Field(
        default="Saiba mais!",
        min_length=3,
        max_length=100,
        description="Call-to-action message"
    )

    template: Optional[TemplateType] = Field(
        default=None,
        description="Use pre-defined template (overrides other fields if set)"
    )

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title format"""
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description format"""
        if not v.strip():
            raise ValueError("Description cannot be empty or whitespace")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Lançamento de Produto Inovador",
                "description": "Vídeo de apresentação de produto tecnológico de ponta",
                "duration": 30,
                "target_audience": "Profissionais de tecnologia",
                "style": "modern",
                "tone": "enthusiastic",
                "cta": "Experimente grátis agora!"
            }
        }


class VideoGenerationRequest(BaseModel):
    """Complete video generation request"""

    briefing: VideoBriefing = Field(
        ...,
        description="Video briefing details"
    )

    async_mode: bool = Field(
        default=False,
        description="If true, returns task_id immediately without waiting"
    )

    webhook_url: Optional[str] = Field(
        default=None,
        description="URL to receive completion notification (async mode only)"
    )


class SceneInfo(BaseModel):
    """Information about a generated scene"""

    scene_number: int = Field(..., ge=1)
    description: str
    duration: float = Field(..., ge=0)
    cost: float = Field(..., ge=0)
    image_path: Optional[str] = None


class VideoMetadata(BaseModel):
    """Metadata about generated video"""

    title: str
    duration: float = Field(..., ge=0)
    resolution: str = Field(default="1920x1080")
    fps: int = Field(default=30, ge=1)
    codec: str = Field(default="h264")
    file_size_mb: Optional[float] = Field(default=None, ge=0)


class VideoGenerationResponse(BaseModel):
    """Video generation response"""

    success: bool
    task_id: str
    video_path: Optional[str] = None
    metadata: Optional[VideoMetadata] = None
    scenes: List[SceneInfo] = Field(default_factory=list)
    total_cost: float = Field(default=0.0, ge=0)
    generation_time_seconds: Optional[float] = Field(default=None, ge=0)
    timestamp: datetime = Field(default_factory=datetime.now)
    error_message: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "task_id": "video_20251120_101530",
                "video_path": "outputs/videos/video_20251120_101530.mp4",
                "metadata": {
                    "title": "Lançamento de Produto Inovador",
                    "duration": 30.5,
                    "resolution": "1920x1080",
                    "fps": 30,
                    "codec": "h264"
                },
                "scenes": [],
                "total_cost": 0.0234,
                "generation_time_seconds": 45.2,
                "timestamp": "2025-11-20T10:15:30"
            }
        }


class TaskStatusResponse(BaseModel):
    """Status of an async task"""

    task_id: str
    status: str = Field(
        ...,
        description="Status: pending, processing, completed, failed"
    )
    progress: int = Field(default=0, ge=0, le=100, description="Progress percentage")
    current_phase: Optional[str] = None
    result: Optional[VideoGenerationResponse] = None
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """Health check response"""

    status: str = Field(..., description="healthy or unhealthy")
    version: str
    uptime_seconds: float = Field(..., ge=0)
    timestamp: datetime = Field(default_factory=datetime.now)
    checks: Dict[str, bool] = Field(
        default_factory=dict,
        description="Individual component health checks"
    )


class ErrorResponse(BaseModel):
    """Standard error response"""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error details"
    )
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid briefing data",
                "details": {
                    "field": "duration",
                    "issue": "must be between 15 and 180 seconds"
                },
                "timestamp": "2025-11-20T10:15:30"
            }
        }


class StatsResponse(BaseModel):
    """System statistics"""

    total_videos_generated: int = Field(default=0, ge=0)
    total_cost: float = Field(default=0.0, ge=0)
    average_generation_time: float = Field(default=0.0, ge=0)
    success_rate: float = Field(default=0.0, ge=0, le=100)
    uptime_seconds: float = Field(..., ge=0)
    timestamp: datetime = Field(default_factory=datetime.now)
