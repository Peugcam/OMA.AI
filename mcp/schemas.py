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
# HYBRID VISUAL RESULT (Pexels + Stability combinados)
# ============================================================================

class HybridVisualResult(BaseModel):
    """
    Resultado hibrido: Video Pexels + Imagem Stability para overlay.

    Casos de uso:
    - Pessoa apresentando + grafico de dados (overlay)
    - Equipe reunida + logo da empresa (overlay)
    - Escritorio + holograma futurista (overlay)

    O editor combina:
    1. Video Pexels como fundo
    2. Imagem Stability como overlay (transparente ou canto)
    """
    success: bool = True
    source: Literal["both"] = "both"

    # Pexels (video de fundo)
    video_id: int
    video_url: HttpUrl
    video_local_path: Optional[str] = None
    video_width: int
    video_height: int
    video_duration: int
    video_keywords: str

    # Stability (imagem overlay - gerada em 1024x1024, redimensionada no editor)
    image_path: str
    image_prompt: str
    image_width: int = 1024
    image_height: int = 1024

    # Configuracao do overlay
    overlay_position: Literal["top-right", "bottom-right", "top-left", "bottom-left", "center"] = "bottom-right"
    overlay_opacity: float = Field(default=0.9, ge=0.0, le=1.0)
    overlay_scale: float = Field(default=0.25, ge=0.1, le=0.5)  # 25% do tamanho do video

    # Custo total
    cost: float = 0.04  # Pexels gratis + Stability $0.04

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "source": "both",
                "video_id": 8088078,
                "video_url": "https://videos.pexels.com/...",
                "video_local_path": "C:/Users/paulo/OneDrive/Desktop/OMA_Videos/pexels_videos/pexels_8088078.mp4",
                "video_width": 1920,
                "video_height": 1080,
                "video_duration": 15,
                "video_keywords": "team meeting presentation",
                "image_path": "C:/Users/paulo/OneDrive/Desktop/OMA_Videos/images/overlay_logo.png",
                "image_prompt": "modern tech company logo, minimalist, blue gradient",
                "image_width": 512,
                "image_height": 512,
                "overlay_position": "bottom-right",
                "overlay_opacity": 0.9,
                "overlay_scale": 0.25,
                "cost": 0.04
            }
        }


# ============================================================================
# UNIFIED VISUAL RESULT (Union Type)
# ============================================================================

from typing import Union

VisualResult = Union[PexelsSearchResult, StabilityImageResult, HybridVisualResult]

"""
Este Union type permite que o LLM retorne um dos tres tipos,
garantindo type safety em qualquer caso.

Uso:
    result: VisualResult = await mcp_client.call_tool(...)

    if result.source == "pexels":
        # result é PexelsSearchResult
        video_path = result.local_path

    elif result.source == "stability_ai":
        # result é StabilityImageResult
        image_path = result.image_path

    elif result.source == "both":
        # result é HybridVisualResult
        video_path = result.video_local_path
        overlay_path = result.image_path
        # Editor combina video + overlay
"""


# ============================================================================
# INPUT SCHEMA PARA HYBRID
# ============================================================================

class GenerateHybridInput(BaseModel):
    """Input para geracao hibrida (Pexels + Stability)"""

    # Para Pexels (video de fundo)
    video_keywords: str = Field(
        ...,
        description="Keywords em ingles para buscar video no Pexels",
        min_length=3,
        max_length=100
    )
    video_orientation: Literal["landscape", "portrait", "square"] = Field(
        default="landscape",
        description="Orientacao do video"
    )

    # Para Stability (overlay)
    overlay_prompt: str = Field(
        ...,
        description="Prompt para gerar imagem de overlay",
        min_length=10,
        max_length=300
    )
    overlay_position: Literal["top-right", "bottom-right", "top-left", "bottom-left", "center"] = Field(
        default="bottom-right",
        description="Posicao do overlay no video"
    )
    overlay_scale: float = Field(
        default=0.25,
        ge=0.1,
        le=0.5,
        description="Escala do overlay (0.1-0.5 do tamanho do video)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "video_keywords": "team meeting presentation business",
                "video_orientation": "landscape",
                "overlay_prompt": "modern company logo, minimalist design, blue gradient, professional",
                "overlay_position": "bottom-right",
                "overlay_scale": 0.25
            }
        }
