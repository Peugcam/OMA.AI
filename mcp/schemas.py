"""
MCP Schemas - Pydantic Models para Tools
Garante type safety e validação automática
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field, HttpUrl


# ============================================================================
# PEXELS SCHEMAS
# ============================================================================

class PexelsVideoFile(BaseModel):
    """Arquivo de vídeo individual do Pexels"""
    id: int
    quality: str
    file_type: str
    width: int
    height: int
    fps: Optional[float] = None
    link: HttpUrl


class PexelsVideo(BaseModel):
    """Vídeo do Pexels"""
    id: int
    width: int
    height: int
    duration: int
    url: HttpUrl
    image: HttpUrl
    video_files: List[PexelsVideoFile]
    user: dict


class PexelsSearchResult(BaseModel):
    """Resultado de busca no Pexels"""
    success: bool = True
    source: Literal["pexels"] = "pexels"
    video_id: int
    video_url: HttpUrl
    local_path: Optional[str] = None
    width: int
    height: int
    duration: int
    keywords: str
    cost: float = 0.0  # Pexels é grátis

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "source": "pexels",
                "video_id": 8088078,
                "video_url": "https://videos.pexels.com/...",
                "local_path": "C:/Users/paulo/OneDrive/Desktop/OMA_Videos/pexels_videos/pexels_8088078.mp4",
                "width": 1920,
                "height": 1080,
                "duration": 15,
                "keywords": "business meeting team",
                "cost": 0.0
            }
        }


# ============================================================================
# STABILITY AI SCHEMAS
# ============================================================================

class StabilityImageResult(BaseModel):
    """Resultado de geração do Stability AI"""
    success: bool = True
    source: Literal["stability_ai"] = "stability_ai"
    image_path: str
    prompt_used: str
    width: int = 1024
    height: int = 1024
    cost: float = 0.04  # SDXL 1024x1024
    seed: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "source": "stability_ai",
                "image_path": "C:/Users/paulo/OneDrive/Desktop/OMA_Videos/images/scene_06.png",
                "prompt_used": "modern holographic logo floating in space, futuristic, high quality",
                "width": 1024,
                "height": 1024,
                "cost": 0.04
            }
        }


# ============================================================================
# TOOL INPUT SCHEMAS
# ============================================================================

class SearchPexelsInput(BaseModel):
    """Input para search_pexels_video tool"""
    keywords: str = Field(
        ...,
        description="Search keywords in English (e.g., 'business meeting team')",
        min_length=3,
        max_length=100
    )
    orientation: Literal["landscape", "portrait", "square"] = Field(
        default="landscape",
        description="Video orientation"
    )
    per_page: int = Field(
        default=3,
        ge=1,
        le=15,
        description="Number of results (max 15)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "keywords": "person working laptop office",
                "orientation": "landscape",
                "per_page": 3
            }
        }


class GenerateStabilityInput(BaseModel):
    """Input para generate_stability_image tool"""
    prompt: str = Field(
        ...,
        description="Image generation prompt in English",
        min_length=10,
        max_length=500
    )
    width: int = Field(
        default=1024,
        ge=512,
        le=1024,
        description="Image width (512-1024)"
    )
    height: int = Field(
        default=1024,
        ge=512,
        le=1024,
        description="Image height (512-1024)"
    )
    cfg_scale: float = Field(
        default=7.0,
        ge=0.0,
        le=15.0,
        description="Prompt adherence (0-15, default 7)"
    )
    negative_prompt: Optional[str] = Field(
        default="ugly, blurry, low quality, distorted, deformed",
        description="What to avoid in the image"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "modern holographic logo floating in space, futuristic, professional, high quality, 4k",
                "width": 1024,
                "height": 1024,
                "cfg_scale": 7.0,
                "negative_prompt": "ugly, blurry, low quality, people, faces"
            }
        }


# ============================================================================
# UNIFIED VISUAL RESULT (Union Type)
# ============================================================================

from typing import Union

VisualResult = Union[PexelsSearchResult, StabilityImageResult]

"""
Este Union type permite que o LLM retorne um dos dois tipos,
garantindo type safety em qualquer caso.

Uso:
    result: VisualResult = await mcp_client.call_tool(...)

    if result.source == "pexels":
        # result é PexelsSearchResult
        video_path = result.local_path
    else:
        # result é StabilityImageResult
        image_path = result.image_path
"""
