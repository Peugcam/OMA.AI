"""
🎬 VIDEO GENERATOR - RunwayML Gen-3 Edition
==========================================

Gerador de vídeos otimizado para anúncios de afiliados (15-20s).

Workflow:
1. Recebe prompts de vídeo do ProductAdAgent
2. Gera 3-4 clips de 5s em paralelo (RunwayML Gen-3)
3. Gera narração (ElevenLabs)
4. Compõe vídeo final com FFmpeg
5. Output: Vídeo pronto para publicar

Otimizações:
- Geração paralela de clips (90s ao invés de 4x90s = 360s)
- Cache de clips genéricos reutilizáveis
- Retry automático com exponential backoff
- Monitoramento de custos em tempo real

Custo por vídeo de 20s:
- 4 clips de 5s (RunwayML): $1.00
- Narração (ElevenLabs): $0.11
- Total: ~$1.11
"""

import os
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import subprocess

from core.runwayml_client import RunwayMLClient
from core.openrouter_client import OpenRouterClient


class VideoGeneratorRunway:
    """
    Gerador de vídeos para anúncios de afiliados usando RunwayML Gen-3.

    Otimizado para vídeos curtos (15-20s) com máxima qualidade.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        # Clients
        self.runway = RunwayMLClient()
        self.llm = OpenRouterClient()

        # API keys
        self.elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
        self.elevenlabs_voice_id = os.getenv("ELEVENLABS_VOICE_ID")

        # Configurações do .env
        self.default_duration = int(os.getenv("DEFAULT_VIDEO_DURATION", "20"))
        self.clips_per_video = int(os.getenv("CLIPS_PER_VIDEO", "4"))
        self.clip_duration = int(os.getenv("RUNWAYML_CLIP_DURATION", "5"))

        # Output directory
        self.output_dir = Path("./outputs/affiliate_videos")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Cache directory
        self.cache_dir = Path("./cache/video_clips")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def create_affiliate_video(
        self,
        product_info: Dict[str, Any],
        script: str,
        video_prompts: List[str],
        duration: int = 20
    ) -> Dict[str, Any]:
        """
        Cria vídeo completo de anúncio de afiliado.

        Args:
            product_info: Informações do produto
            script: Script do anúncio (gerado pelo ProductAdAgent)
            video_prompts: Lista de prompts para cada clip
            duration: Duração total do vídeo

        Returns:
            {
                'video_path': Path do vídeo final,
                'cost': Custo total,
                'generation_time': Tempo total,
                'clips': Informações dos clips gerados
            }
        """
        start_time = datetime.now()
        product_name = product_info.get('name', 'produto')

        self.logger.info(f"🎬 Creating {duration}s affiliate video for: {product_name}")

        try:
            # 1. Gerar narração (concorrente com vídeos)
            self.logger.info("🎤 Generating narration...")
            narration_task = asyncio.create_task(
                self._generate_narration(script)
            )

            # 2. Gerar clips de vídeo em paralelo
            self.logger.info(f"🎥 Generating {len(video_prompts)} video clips in parallel...")
            clips = await self.runway.generate_multiple_videos(
                prompts=video_prompts,
                duration=self.clip_duration,
                aspect_ratio="9:16"  # Vertical para Reels/TikTok
            )

            # 3. Aguardar narração
            narration = await narration_task

            # 4. Compor vídeo final
            self.logger.info("🎬 Composing final video...")
            final_video = await self._compose_video(
                clips=clips,
                narration=narration,
                product_info=product_info
            )

            # 5. Calcular métricas
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()

            total_cost = (
                sum(clip.get('cost', 0) for clip in clips) +
                narration.get('cost', 0)
            )

            result = {
                'video_path': final_video,
                'cost': total_cost,
                'generation_time': generation_time,
                'clips': clips,
                'narration': narration,
                'product_name': product_name
            }

            self.logger.info(
                f"✅ Video created! "
                f"Cost: ${total_cost:.2f}, "
                f"Time: {generation_time:.1f}s"
            )

            return result

        except Exception as e:
            self.logger.error(f"❌ Error creating video: {e}")
            raise

    async def _generate_narration(self, script: str) -> Dict[str, Any]:
        """
        Gera narração profissional com ElevenLabs.
        """
        import httpx

        if not self.elevenlabs_key:
            self.logger.warning("ElevenLabs not configured, skipping narration")
            return {
                'audio_path': None,
                'cost': 0.0,
                'duration': 0
            }

        try:
            # Configurações de voz do .env
            model = os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")
            stability = float(os.getenv("ELEVENLABS_STABILITY", "0.5"))
            similarity_boost = float(os.getenv("ELEVENLABS_SIMILARITY_BOOST", "0.75"))
            style = float(os.getenv("ELEVENLABS_STYLE", "0.2"))

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{self.elevenlabs_voice_id}",
                    headers={
                        "xi-api-key": self.elevenlabs_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "text": script,
                        "model_id": model,
                        "voice_settings": {
                            "stability": stability,
                            "similarity_boost": similarity_boost,
                            "style": style
                        }
                    }
                )

                response.raise_for_status()

                # Salvar áudio
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                audio_path = self.output_dir / f"narration_{timestamp}.mp3"

                with open(audio_path, "wb") as f:
                    f.write(response.content)

                # Calcular duração e custo
                chars = len(script)
                cost = (chars / 1000) * 0.30  # $0.30 per 1k chars

                self.logger.info(f"✅ Narration generated: {audio_path.name}")

                return {
                    'audio_path': str(audio_path),
                    'cost': cost,
                    'characters': chars
                }

        except Exception as e:
            self.logger.error(f"Error generating narration: {e}")
            return {
                'audio_path': None,
                'cost': 0.0,
                'duration': 0
            }

    async def _compose_video(
        self,
        clips: List[Dict[str, Any]],
        narration: Dict[str, Any],
        product_info: Dict[str, Any]
    ) -> str:
        """
        Compõe vídeo final concatenando clips + narração + texto.
        """
        try:
            # Criar arquivo de lista de clips para FFmpeg
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            concat_file = self.output_dir / f"concat_{timestamp}.txt"

            with open(concat_file, 'w') as f:
                for clip in clips:
                    video_path = clip.get('video_path')
                    if video_path and Path(video_path).exists():
                        # Escapar path para FFmpeg
                        escaped_path = str(video_path).replace("\\", "/")
                        f.write(f"file '{escaped_path}'\n")

            # Output path
            product_name_safe = product_info.get('name', 'video').replace(' ', '_')[:30]
            output_path = self.output_dir / f"{product_name_safe}_{timestamp}.mp4"

            # Comando FFmpeg
            # 1. Concatenar clips
            # 2. Adicionar narração
            # 3. Adicionar legendas (opcional)
            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(concat_file),
            ]

            # Adicionar narração se existir
            if narration.get('audio_path') and Path(narration['audio_path']).exists():
                cmd.extend([
                    '-i', narration['audio_path'],
                    '-c:v', 'copy',
                    '-c:a', 'aac',
                    '-b:a', '128k',
                    '-map', '0:v:0',
                    '-map', '1:a:0',
                    '-shortest'
                ])
            else:
                cmd.extend([
                    '-c', 'copy'
                ])

            cmd.append(str(output_path))

            # Executar FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            # Limpar arquivo temporário
            concat_file.unlink(missing_ok=True)

            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            self.logger.info(f"✅ Video composed: {output_path.name} ({file_size_mb:.2f} MB)")

            return str(output_path)

        except subprocess.CalledProcessError as e:
            self.logger.error(f"FFmpeg error: {e.stderr}")
            raise
        except Exception as e:
            self.logger.error(f"Error composing video: {e}")
            raise

    async def close(self):
        """Cleanup"""
        await self.runway.close()


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

async def example_usage():
    """Exemplo de como usar o VideoGeneratorRunway."""

    generator = VideoGeneratorRunway()

    # Informações do produto
    product_info = {
        'name': 'Perfume Chanel N°5',
        'category': 'perfumes',
        'price': 'R$ 899,00'
    }

    # Script (gerado pelo ProductAdAgent)
    script = """
    O que Marilyn Monroe usava para dormir? Apenas Chanel N°5.
    Este não é apenas um perfume. É a fragrância mais icônica da história.
    Criada em 1921, Chanel N°5 é sinônimo de elegância atemporal.
    Fragrância marcante que dura o dia inteiro.
    Garanta o seu com frete grátis - link na bio!
    """

    # Prompts de vídeo (4 clips de 5s cada)
    video_prompts = [
        "Elegant Chanel N°5 perfume bottle on white marble, luxury product photography, cinematic lighting, 4K",
        "Close-up of Chanel N°5 bottle and golden cap, premium details, soft focus, luxury aesthetic",
        "Woman's hand spraying Chanel N°5 perfume, slow motion, elegant movement, warm lighting",
        "Chanel N°5 perfume with gift box, call-to-action setup, professional product shot, bright background"
    ]

    # Gerar vídeo
    result = await generator.create_affiliate_video(
        product_info=product_info,
        script=script,
        video_prompts=video_prompts,
        duration=20
    )

    print(f"\n✅ Vídeo criado com sucesso!")
    print(f"Path: {result['video_path']}")
    print(f"Custo: ${result['cost']:.2f}")
    print(f"Tempo: {result['generation_time']:.1f}s")

    await generator.close()


if __name__ == "__main__":
    # Descomentar para testar
    # asyncio.run(example_usage())
    pass
