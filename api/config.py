"""
Configuration Management
========================

Environment-based configuration with validation.
"""

import os
from pathlib import Path
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from functools import lru_cache


# Get base directory (project root)
BASE_DIR = Path(__file__).resolve().parent.parent


def get_cors_origins() -> List[str]:
    """Get CORS origins from environment or defaults"""
    cors_env = os.environ.get("CORS_ORIGINS", "")
    if cors_env:
        return [origin.strip() for origin in cors_env.split(",")]
    return ["http://localhost:7861", "http://localhost:3000"]


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Application
    APP_NAME: str = "OMA Video Generation API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:7861", "http://localhost:3000", "*"]

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 10
    RATE_LIMIT_PER_HOUR: int = 100

    # Video Generation
    MAX_VIDEO_DURATION: int = 180  # seconds
    MIN_VIDEO_DURATION: int = 15   # seconds
    DEFAULT_VIDEO_DURATION: int = 30
    OUTPUT_DIR: Path = BASE_DIR / "outputs" / "videos"
    TEMP_DIR: Path = BASE_DIR / "temp"

    # OpenAI / OpenRouter
    OPENAI_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MAX_TOKENS: int = 4000
    OPENAI_TEMPERATURE: float = 0.7

    # Logging
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FILE: Optional[Path] = BASE_DIR / "logs" / "api.log"
    LOG_FORMAT: str = "json"  # json or text
    LOG_ROTATION: str = "100 MB"  # Size-based rotation

    # Security
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "CHANGE_THIS_IN_PRODUCTION")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_HOSTS: List[str] = ["*"]

    # Background Tasks
    MAX_CONCURRENT_GENERATIONS: int = 3
    TASK_TIMEOUT_SECONDS: int = 600  # 10 minutes

    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090

    # File Storage
    MAX_UPLOAD_SIZE_MB: int = 100
    ALLOWED_VIDEO_FORMATS: List[str] = ["mp4", "mov", "avi"]
    ALLOWED_IMAGE_FORMATS: List[str] = ["jpg", "jpeg", "png", "webp"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create required directories
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)
        if self.LOG_FILE:
            self.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT == "development"

    def validate_openai_config(self) -> bool:
        """Validate OpenAI configuration"""
        if not self.OPENAI_API_KEY:
            return False
        return True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Use lru_cache to avoid re-reading .env file on every call.
    """
    return Settings()


# Global settings instance
settings = get_settings()
