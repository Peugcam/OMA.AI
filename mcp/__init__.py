"""
MCP Module - Model Context Protocol Implementation

V2 Updates:
- HybridVisualResult for combined Pexels + Stability
- generate_hybrid_visual tool
- Contextual fallbacks
"""

from .schemas import (
    PexelsSearchResult,
    StabilityImageResult,
    HybridVisualResult,
    SearchPexelsInput,
    GenerateStabilityInput,
    GenerateHybridInput,
    VisualResult
)

from .tools import (
    search_pexels_video,
    generate_stability_image,
    generate_hybrid_visual,
    AVAILABLE_TOOLS
)

from .server import MCPVisualServer

__all__ = [
    # Schemas
    "PexelsSearchResult",
    "StabilityImageResult",
    "HybridVisualResult",
    "SearchPexelsInput",
    "GenerateStabilityInput",
    "GenerateHybridInput",
    "VisualResult",

    # Tools
    "search_pexels_video",
    "generate_stability_image",
    "generate_hybrid_visual",
    "AVAILABLE_TOOLS",

    # Server
    "MCPVisualServer"
]
