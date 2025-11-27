"""
Gerenciamento de Paths - Suporte Multi-Ambiente
==============================================

Detecta automaticamente o ambiente (produção/desenvolvimento) e
retorna os paths apropriados para cada caso.

AMBIENTES SUPORTADOS:
- Cloud Run (produção)
- Windows local (desenvolvimento)
- Linux local (desenvolvimento)
"""

import os
from pathlib import Path
from typing import Optional


def is_production() -> bool:
    """
    Detecta se está rodando em ambiente de produção (Cloud Run).

    Returns:
        True se está em produção, False caso contrário
    """
    # Cloud Run define ENVIRONMENT=production
    if os.getenv("ENVIRONMENT") == "production":
        return True

    # Também verifica se está em Cloud Run pela variável PORT
    if os.getenv("K_SERVICE"):  # Google Cloud Run específico
        return True

    # Se está em /app (container), provavelmente é produção
    if Path("/app").exists() and Path.cwd() == Path("/app"):
        return True

    return False


def get_base_dir() -> Path:
    """
    Retorna o diretório base conforme o ambiente.

    Returns:
        Path do diretório base
    """
    if is_production():
        # Cloud Run: usar /app
        return Path("/app")
    else:
        # Desenvolvimento Windows: usar OneDrive
        windows_path = Path("C:/Users/paulo/OneDrive/Desktop/OMA_Videos")
        if windows_path.exists():
            return windows_path

        # Fallback para diretório local outputs
        return Path("outputs")


def get_output_dir() -> Path:
    """
    Retorna o diretório de outputs (vídeos finais).

    Returns:
        Path do diretório de outputs
    """
    if is_production():
        output_dir = Path("/app/outputs/videos")
    else:
        output_dir = get_base_dir()

    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def get_temp_dir() -> Path:
    """
    Retorna o diretório temporário para processamento.

    Returns:
        Path do diretório temp
    """
    if is_production():
        temp_dir = Path("/app/outputs/temp")
    else:
        temp_dir = get_base_dir() / "temp"

    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


def get_pexels_videos_dir() -> Path:
    """
    Retorna o diretório para cache de vídeos do Pexels.

    Returns:
        Path do diretório de vídeos Pexels
    """
    if is_production():
        pexels_dir = Path("/app/outputs/temp/pexels_videos")
    else:
        pexels_dir = get_base_dir() / "pexels_videos"

    pexels_dir.mkdir(parents=True, exist_ok=True)
    return pexels_dir


def get_images_dir() -> Path:
    """
    Retorna o diretório para armazenar imagens geradas.

    Returns:
        Path do diretório de imagens
    """
    if is_production():
        images_dir = Path("/app/outputs/images")
    else:
        images_dir = get_base_dir() / "images"

    images_dir.mkdir(parents=True, exist_ok=True)
    return images_dir


def get_audio_dir() -> Path:
    """
    Retorna o diretório para armazenar áudios.

    Returns:
        Path do diretório de áudios
    """
    if is_production():
        audio_dir = Path("/app/outputs/temp/audio")
    else:
        audio_dir = get_base_dir() / "audio"

    audio_dir.mkdir(parents=True, exist_ok=True)
    return audio_dir


def get_logs_dir() -> Path:
    """
    Retorna o diretório para logs.

    Returns:
        Path do diretório de logs
    """
    if is_production():
        logs_dir = Path("/app/logs")
    else:
        logs_dir = Path("logs")

    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


# Para debug/logging
def print_environment_info():
    """Imprime informações sobre o ambiente detectado."""
    print("=" * 60)
    print("🔧 CONFIGURAÇÃO DE PATHS")
    print("=" * 60)
    print(f"Ambiente: {'PRODUÇÃO (Cloud Run)' if is_production() else 'DESENVOLVIMENTO'}")
    print(f"Base Dir: {get_base_dir()}")
    print(f"Output Dir: {get_output_dir()}")
    print(f"Temp Dir: {get_temp_dir()}")
    print(f"Pexels Videos: {get_pexels_videos_dir()}")
    print(f"Images Dir: {get_images_dir()}")
    print(f"Audio Dir: {get_audio_dir()}")
    print(f"Logs Dir: {get_logs_dir()}")
    print("=" * 60)


if __name__ == "__main__":
    # Test
    print_environment_info()
