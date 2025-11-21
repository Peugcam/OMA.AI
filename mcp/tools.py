"""
MCP Tools - Pexels e Stability AI
Implementacao das ferramentas como funcoes puras
"""

import os
import requests
import logging
import base64
from pathlib import Path
from typing import Optional

from .schemas import (
    PexelsSearchResult,
    StabilityImageResult,
    HybridVisualResult,
    SearchPexelsInput,
    GenerateStabilityInput,
    GenerateHybridInput
)


logger = logging.getLogger(__name__)


# ============================================================================
# PEXELS TOOL
# ============================================================================

def search_pexels_video(
    keywords: str,
    orientation: str = "landscape",
    per_page: int = 3
) -> PexelsSearchResult:
    """
    Search Pexels for stock videos.

    Use this tool for:
    - Real people, faces, emotions
    - Physical actions (working, walking, meeting)
    - Common places (office, cafe, street, nature)
    - Objects being used by people

    Args:
        keywords: Search keywords in English (e.g., "business meeting team")
        orientation: Video orientation (landscape/portrait/square)
        per_page: Number of results to fetch (1-15)

    Returns:
        PexelsSearchResult with video details and local path

    Raises:
        Exception: If API call fails or no results found
    """
    logger.info(f"[MCP TOOL] search_pexels_video: '{keywords}'")

    # Validar input
    input_data = SearchPexelsInput(
        keywords=keywords,
        orientation=orientation,
        per_page=per_page
    )

    # API key
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        raise ValueError("PEXELS_API_KEY nao configurada")

    # Fazer busca
    try:
        response = requests.get(
            "https://api.pexels.com/videos/search",
            headers={"Authorization": api_key},
            params={
                "query": input_data.keywords,
                "per_page": input_data.per_page,
                "orientation": input_data.orientation,
                "size": "medium"
            },
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        if not data.get("videos"):
            raise Exception(f"Nenhum video encontrado para: {keywords}")

        # Pegar primeiro video
        video = data["videos"][0]
        video_files = video.get("video_files", [])

        if not video_files:
            raise Exception("Video sem arquivos disponiveis")

        # Preferir HD (1280x720 ou maior)
        hd_video = None
        for vf in video_files:
            if vf.get("width", 0) >= 1280:
                hd_video = vf
                break

        if not hd_video:
            hd_video = max(video_files, key=lambda x: x.get("width", 0))

        video_url = hd_video["link"]
        video_id = video.get("id")

        # Baixar video localmente
        local_path = _download_pexels_video(video_url, video_id)

        logger.info(f"OK - Video Pexels baixado: {local_path}")

        # Retornar resultado validado
        return PexelsSearchResult(
            video_id=video_id,
            video_url=video_url,
            local_path=str(local_path) if local_path else None,
            width=hd_video.get("width", 1920),
            height=hd_video.get("height", 1080),
            duration=video.get("duration", 10),
            keywords=input_data.keywords
        )

    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na API Pexels: {e}")
        raise Exception(f"Falha ao buscar Pexels: {e}")


def _download_pexels_video(video_url: str, video_id: int) -> Optional[Path]:
    """
    Baixa video do Pexels localmente.

    Args:
        video_url: URL do video
        video_id: ID do video no Pexels

    Returns:
        Path do arquivo baixado ou None se falhar
    """
    try:
        # Diretorio de download
        download_dir = Path("C:/Users/paulo/OneDrive/Desktop/OMA_Videos/pexels_videos")
        download_dir.mkdir(parents=True, exist_ok=True)

        filename = f"pexels_{video_id}.mp4"
        filepath = download_dir / filename

        # Se ja existe, retornar
        if filepath.exists():
            logger.info(f"Video ja existe: {filepath}")
            return filepath

        # Baixar
        logger.info(f"Baixando video Pexels ID {video_id}...")
        response = requests.get(video_url, stream=True, timeout=60)
        response.raise_for_status()

        # Salvar
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        file_size = filepath.stat().st_size / (1024 * 1024)
        logger.info(f"Download completo: {filepath} ({file_size:.1f} MB)")

        return filepath

    except Exception as e:
        logger.error(f"Erro ao baixar video: {e}")
        return None


# ============================================================================
# STABILITY AI TOOL
# ============================================================================

def generate_stability_image(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    cfg_scale: float = 7.0,
    negative_prompt: Optional[str] = None
) -> StabilityImageResult:
    """
    Generate image with Stability AI.

    Use this tool for:
    - Logos and branding (WITHOUT people)
    - Abstract concepts (technology, data visualization)
    - Futuristic environments (empty, no humans)
    - Products alone (no hands holding them)
    - Conceptual landscapes
    - Abstract art

    CRITICAL: DO NOT use for people/faces (Stability AI generates deformed faces).

    Args:
        prompt: Image generation prompt in English
        width: Image width in pixels (512-1024)
        height: Image height in pixels (512-1024)
        cfg_scale: Prompt adherence (0-15, default 7)
        negative_prompt: What to avoid in the image

    Returns:
        StabilityImageResult with image path and details

    Raises:
        Exception: If API call fails or generation fails
    """
    logger.info(f"[MCP TOOL] generate_stability_image: '{prompt[:60]}...'")

    # Validar input
    input_data = GenerateStabilityInput(
        prompt=prompt,
        width=width,
        height=height,
        cfg_scale=cfg_scale,
        negative_prompt=negative_prompt or "ugly, blurry, low quality, distorted, deformed"
    )

    # API key
    api_key = os.getenv("STABILITY_API_KEY")
    if not api_key:
        raise ValueError("STABILITY_API_KEY nao configurada")

    # API endpoint
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

    # Headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Payload
    payload = {
        "text_prompts": [
            {"text": input_data.prompt, "weight": 1},
            {"text": input_data.negative_prompt, "weight": -1}
        ],
        "cfg_scale": input_data.cfg_scale,
        "height": input_data.height,
        "width": input_data.width,
        "samples": 1,
        "steps": 30
    }

    try:
        # Fazer requisicao
        logger.info("Gerando imagem com Stability AI...")
        response = requests.post(url, json=payload, headers=headers, timeout=60)

        if response.status_code != 200:
            raise Exception(f"Stability AI error: {response.status_code} - {response.text}")

        data = response.json()

        # Salvar imagem
        image_data = data["artifacts"][0]
        image_base64 = image_data["base64"]
        seed = image_data.get("seed")

        image_bytes = base64.b64decode(image_base64)

        # Diretorio de saida
        output_dir = Path("C:/Users/paulo/OneDrive/Desktop/OMA_Videos/images")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Nome do arquivo (timestamp)
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_path = output_dir / f"stability_{timestamp}.png"

        image_path.write_bytes(image_bytes)

        logger.info(f"OK - Imagem Stability salva: {image_path}")

        # Retornar resultado validado
        return StabilityImageResult(
            image_path=str(image_path),
            prompt_used=input_data.prompt,
            width=input_data.width,
            height=input_data.height,
            seed=seed
        )

    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na API Stability: {e}")
        raise Exception(f"Falha ao gerar imagem Stability: {e}")


# ============================================================================
# HYBRID TOOL (Pexels + Stability combinados)
# ============================================================================

def generate_hybrid_visual(
    video_keywords: str,
    overlay_prompt: str,
    video_orientation: str = "landscape",
    overlay_position: str = "bottom-right",
    overlay_scale: float = 0.25
) -> HybridVisualResult:
    """
    Generate hybrid visual: Pexels video + Stability overlay.

    Use this tool for scenes that combine:
    - Real people/actions (video from Pexels)
    - Digital/abstract elements (image from Stability for overlay)

    Examples:
    - "Person presenting data charts" → video of person + chart overlay
    - "Team meeting with company logo" → video of team + logo overlay
    - "Office with holographic display" → video of office + hologram overlay

    Args:
        video_keywords: Keywords for Pexels video search (English)
        overlay_prompt: Prompt for Stability AI overlay image
        video_orientation: Video orientation (landscape/portrait/square)
        overlay_position: Where to place overlay (top-right, bottom-right, etc)
        overlay_scale: Overlay size relative to video (0.1-0.5)

    Returns:
        HybridVisualResult with video and overlay paths

    Raises:
        Exception: If either API fails
    """
    logger.info(f"[MCP TOOL] generate_hybrid_visual: video='{video_keywords}', overlay='{overlay_prompt[:40]}...'")

    # Validar input
    input_data = GenerateHybridInput(
        video_keywords=video_keywords,
        video_orientation=video_orientation,
        overlay_prompt=overlay_prompt,
        overlay_position=overlay_position,
        overlay_scale=overlay_scale
    )

    # PASSO 1: Buscar video no Pexels
    logger.info("Hybrid Step 1: Buscando video Pexels...")
    pexels_result = search_pexels_video(
        keywords=input_data.video_keywords,
        orientation=input_data.video_orientation
    )

    # PASSO 2: Gerar imagem overlay com Stability
    logger.info("Hybrid Step 2: Gerando overlay Stability...")

    # SDXL requer dimensoes especificas - usar 1024x1024 (sera redimensionado depois)
    # Dimensoes permitidas: 1024x1024, 1152x896, 1216x832, 1344x768, 1536x640
    stability_result = generate_stability_image(
        prompt=input_data.overlay_prompt + ", transparent background, clean edges, suitable for overlay, centered composition",
        width=1024,
        height=1024,
        cfg_scale=8.0,  # Mais aderencia ao prompt para overlays
        negative_prompt="background, scenery, complex scene, people, faces, blurry edges, cluttered"
    )

    logger.info(f"OK - Hybrid visual completo: video={pexels_result.video_id}, overlay={stability_result.image_path}")

    # Retornar resultado combinado
    return HybridVisualResult(
        # Video (Pexels)
        video_id=pexels_result.video_id,
        video_url=pexels_result.video_url,
        video_local_path=pexels_result.local_path,
        video_width=pexels_result.width,
        video_height=pexels_result.height,
        video_duration=pexels_result.duration,
        video_keywords=pexels_result.keywords,

        # Overlay (Stability)
        image_path=stability_result.image_path,
        image_prompt=stability_result.prompt_used,
        image_width=stability_result.width,
        image_height=stability_result.height,

        # Config
        overlay_position=input_data.overlay_position,
        overlay_scale=input_data.overlay_scale,

        # Custo total
        cost=pexels_result.cost + stability_result.cost  # 0 + 0.04 = 0.04
    )


# ============================================================================
# TOOL REGISTRY (para MCP server)
# ============================================================================

AVAILABLE_TOOLS = {
    "search_pexels_video": {
        "function": search_pexels_video,
        "description": "Search Pexels for real stock videos (people, actions, places). Use for any scene with humans or real-world footage. ALWAYS use this for scenes with people.",
        "parameters": SearchPexelsInput.model_json_schema()
    },
    "generate_stability_image": {
        "function": generate_stability_image,
        "description": "Generate conceptual images with Stability AI (logos, abstract, futuristic). NEVER use for people/faces - Stability generates deformed humans. Only use for scenes WITHOUT humans.",
        "parameters": GenerateStabilityInput.model_json_schema()
    },
    "generate_hybrid_visual": {
        "function": generate_hybrid_visual,
        "description": "Generate hybrid visual: Pexels video (background) + Stability image (overlay). Use when scene has BOTH real people AND digital/abstract elements (e.g., 'person presenting chart', 'team with logo').",
        "parameters": GenerateHybridInput.model_json_schema()
    }
}
