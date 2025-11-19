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
]

__version__ = "3.0.0"
