"""
Core Module - Módulos Fundamentais do OMA v3.0

Este módulo contém as abstrações e utilitários principais:
- AIClient: Cliente unificado para LLM/SLM (local e cloud)
- SmartRouter: Roteamento otimizado com cache
- PromptTemplates: Templates reutilizáveis de prompts
- ResponseValidator: Validação e parsing de respostas
"""

from core.ai_client import AIClient, AIClientFactory
from core.router import SmartRouter
from core.prompts import PromptTemplates, PromptBuilder
from core.validators import ResponseValidator, VideoStateValidator
from core.scene_classifier import SceneClassifier, ClassificationResult
from core.paths import (
    is_production,
    get_base_dir,
    get_output_dir,
    get_temp_dir,
    get_pexels_videos_dir,
    get_images_dir,
    get_audio_dir,
    get_logs_dir
)

__all__ = [
    # AI Client
    "AIClient",
    "AIClientFactory",

    # Router
    "SmartRouter",

    # Prompts
    "PromptTemplates",
    "PromptBuilder",

    # Validators
    "ResponseValidator",
    "VideoStateValidator",

    # Scene Classifier (novo)
    "SceneClassifier",
    "ClassificationResult",

    # Paths (novo)
    "is_production",
    "get_base_dir",
    "get_output_dir",
    "get_temp_dir",
    "get_pexels_videos_dir",
    "get_images_dir",
    "get_audio_dir",
    "get_logs_dir",
]

__version__ = "3.1.0"  # Bump version for V2 visual integration
