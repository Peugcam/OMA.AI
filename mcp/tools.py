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
    SearchPexelsInput,
    GenerateStabilityInput
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
# TOOL REGISTRY (para MCP server)
# ============================================================================

AVAILABLE_TOOLS = {
    "search_pexels_video": {
        "function": search_pexels_video,
        "description": "Search Pexels for real stock videos (people, actions, places). Use for any scene with humans or real-world footage.",
        "parameters": SearchPexelsInput.model_json_schema()
    },
    "generate_stability_image": {
        "function": generate_stability_image,
        "description": "Generate conceptual images with Stability AI (logos, abstract, futuristic). NEVER use for people/faces - Stability generates deformed humans.",
        "parameters": GenerateStabilityInput.model_json_schema()
    }
}
