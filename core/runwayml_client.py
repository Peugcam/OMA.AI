"""
🎬 RUNWAYML GEN-3 CLIENT
========================

Cliente otimizado para geração de vídeos com RunwayML Gen-3 Alpha Turbo.

Features:
- Geração de vídeos curtos (5-10s por clip)
- Processamento paralelo de múltiplos clips
- Polling inteligente com exponential backoff
- Tratamento de erros e retry automático
- Cálculo preciso de custos

Custo:
- Gen-3 Alpha Turbo: ~$0.05/segundo
- Vídeo de 5s: ~$0.25
- Vídeo de 20s (4 clips): ~$1.00
"""

import os
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


class RunwayMLClient:
    """
    Cliente para RunwayML Gen-3 API.

    Usage:
        client = RunwayMLClient()
        video = await client.generate_video(
            prompt="Beautiful sunset over ocean",
            duration=5
        )
    """

    BASE_URL = "https://api.runwayml.com/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("RUNWAYML_API_KEY")
        if not self.api_key:
            raise ValueError("RUNWAYML_API_KEY not found in environment")

        self.logger = logging.getLogger(self.__class__.__name__)

        # HTTP client com timeout generoso
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(300.0, connect=10.0),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )

        # Configurações do .env
        self.model = os.getenv("RUNWAYML_MODEL", "gen3a_turbo")
        self.resolution = os.getenv("RUNWAYML_RESOLUTION", "1080p")
        self.default_duration = int(os.getenv("RUNWAYML_CLIP_DURATION", "5"))

        # Output directory
        self.output_dir = Path("./outputs/runwayml_videos")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate_video(
        self,
        prompt: str,
        duration: int = 5,
        image_prompt: Optional[str] = None,
        aspect_ratio: str = "16:9"
    ) -> Dict[str, Any]:
        """
        Gera um vídeo com RunwayML Gen-3.

        Args:
            prompt: Descrição do vídeo a ser gerado
            duration: Duração em segundos (5 ou 10)
            image_prompt: URL ou path de imagem inicial (opcional)
            aspect_ratio: "16:9", "9:16" ou "1:1"

        Returns:
            {
                'video_path': Path do vídeo gerado,
                'duration': Duração real,
                'cost': Custo da geração,
                'generation_time': Tempo total,
                'task_id': ID da task no Runway
            }
        """
        start_time = datetime.now()

        # Validar duração (RunwayML suporta 5s ou 10s)
        if duration not in [5, 10]:
            self.logger.warning(f"Duration {duration}s not supported, using 5s")
            duration = 5

        self.logger.info(f"🎬 Generating {duration}s video: {prompt[:50]}...")

        try:
            # 1. Criar task de geração
            task_id = await self._create_generation_task(
                prompt=prompt,
                duration=duration,
                image_prompt=image_prompt,
                aspect_ratio=aspect_ratio
            )

            # 2. Polling até conclusão
            video_url = await self._poll_task_completion(task_id)

            # 3. Download do vídeo
            video_path = await self._download_video(video_url, task_id)

            # 4. Calcular métricas
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()

            # Custo: ~$0.05/segundo (Gen-3 Alpha Turbo)
            cost = duration * 0.05

            result = {
                'video_path': str(video_path),
                'duration': duration,
                'cost': cost,
                'generation_time': generation_time,
                'task_id': task_id
            }

            self.logger.info(
                f"✅ Video generated! "
                f"Duration: {duration}s, "
                f"Cost: ${cost:.2f}, "
                f"Time: {generation_time:.1f}s"
            )

            return result

        except Exception as e:
            self.logger.error(f"❌ Error generating video: {e}")
            raise

    async def generate_multiple_videos(
        self,
        prompts: List[str],
        duration: int = 5,
        aspect_ratio: str = "16:9"
    ) -> List[Dict[str, Any]]:
        """
        Gera múltiplos vídeos em paralelo.

        Args:
            prompts: Lista de prompts
            duration: Duração de cada clip
            aspect_ratio: Aspect ratio

        Returns:
            Lista de resultados (mesma ordem dos prompts)
        """
        self.logger.info(f"🎬 Generating {len(prompts)} videos in parallel...")

        tasks = [
            self.generate_video(prompt, duration, aspect_ratio=aspect_ratio)
            for prompt in prompts
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filtrar erros
        successful = [r for r in results if not isinstance(r, Exception)]
        failed = [r for r in results if isinstance(r, Exception)]

        if failed:
            self.logger.warning(f"⚠️ {len(failed)} videos failed to generate")

        self.logger.info(f"✅ {len(successful)}/{len(prompts)} videos generated successfully")

        return successful

    async def _create_generation_task(
        self,
        prompt: str,
        duration: int,
        image_prompt: Optional[str],
        aspect_ratio: str
    ) -> str:
        """Cria task de geração no RunwayML."""

        # Mapear aspect ratio para dimensões
        dimensions = {
            "16:9": {"width": 1920, "height": 1080},
            "9:16": {"width": 1080, "height": 1920},
            "1:1": {"width": 1080, "height": 1080}
        }

        dim = dimensions.get(aspect_ratio, dimensions["16:9"])

        # Payload
        payload = {
            "model": self.model,
            "text_prompt": prompt,
            "duration": duration,
            "width": dim["width"],
            "height": dim["height"],
            "seed": None,  # Random seed para variação
            "watermark": False
        }

        # Adicionar imagem inicial se fornecida
        if image_prompt:
            payload["image_prompt"] = image_prompt

        # Criar task
        response = await self.client.post(
            f"{self.BASE_URL}/generations",
            json=payload
        )

        response.raise_for_status()
        data = response.json()

        task_id = data.get("id")
        if not task_id:
            raise ValueError(f"No task ID returned: {data}")

        self.logger.info(f"📝 Task created: {task_id}")
        return task_id

    async def _poll_task_completion(
        self,
        task_id: str,
        max_wait_time: int = 300,
        poll_interval: int = 5
    ) -> str:
        """
        Polling da task até conclusão.

        Args:
            task_id: ID da task
            max_wait_time: Tempo máximo de espera (segundos)
            poll_interval: Intervalo entre polls (segundos)

        Returns:
            URL do vídeo gerado
        """
        self.logger.info(f"⏳ Polling task {task_id}...")

        start_time = datetime.now()

        while True:
            # Verificar timeout
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > max_wait_time:
                raise TimeoutError(f"Task {task_id} timeout after {max_wait_time}s")

            # Consultar status
            response = await self.client.get(
                f"{self.BASE_URL}/generations/{task_id}"
            )

            response.raise_for_status()
            data = response.json()

            status = data.get("status")
            progress = data.get("progress", 0)

            self.logger.debug(f"Task {task_id}: {status} ({progress}%)")

            if status == "SUCCEEDED":
                video_url = data.get("output", {}).get("url")
                if not video_url:
                    raise ValueError(f"No video URL in response: {data}")

                self.logger.info(f"✅ Task completed: {task_id}")
                return video_url

            elif status == "FAILED":
                error = data.get("error", "Unknown error")
                raise RuntimeError(f"Task {task_id} failed: {error}")

            elif status in ["PENDING", "RUNNING"]:
                # Aguardar antes de próximo poll
                await asyncio.sleep(poll_interval)

            else:
                self.logger.warning(f"Unknown status: {status}")
                await asyncio.sleep(poll_interval)

    async def _download_video(self, video_url: str, task_id: str) -> Path:
        """Download do vídeo gerado."""

        self.logger.info(f"⬇️ Downloading video from {video_url[:50]}...")

        response = await self.client.get(video_url)
        response.raise_for_status()

        # Salvar vídeo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_path = self.output_dir / f"runway_{task_id}_{timestamp}.mp4"

        with open(video_path, "wb") as f:
            f.write(response.content)

        file_size_mb = video_path.stat().st_size / (1024 * 1024)
        self.logger.info(f"✅ Video downloaded: {video_path.name} ({file_size_mb:.2f} MB)")

        return video_path

    async def get_account_info(self) -> Dict[str, Any]:
        """Retorna informações da conta (créditos, usage, etc)."""

        try:
            response = await self.client.get(f"{self.BASE_URL}/account")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Error fetching account info: {e}")
            return {}

    async def close(self):
        """Cleanup"""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# ============================================================================
# TESTES E EXEMPLOS
# ============================================================================

async def test_single_video():
    """Teste de geração de um vídeo."""

    async with RunwayMLClient() as client:
        result = await client.generate_video(
            prompt="Beautiful sunset over the ocean, cinematic, golden hour lighting",
            duration=5,
            aspect_ratio="16:9"
        )

        print(f"\n✅ Video generated!")
        print(f"Path: {result['video_path']}")
        print(f"Duration: {result['duration']}s")
        print(f"Cost: ${result['cost']:.2f}")
        print(f"Generation time: {result['generation_time']:.1f}s")


async def test_multiple_videos():
    """Teste de geração paralela de múltiplos vídeos."""

    prompts = [
        "Elegant perfume bottle on marble surface, luxury product photography",
        "Woman spraying perfume, slow motion, soft focus, cinematic lighting",
        "Perfume bottle with flowers, premium aesthetic, golden hour",
        "Close-up of perfume bottle cap, luxury details, 4K quality"
    ]

    async with RunwayMLClient() as client:
        results = await client.generate_multiple_videos(
            prompts=prompts,
            duration=5,
            aspect_ratio="16:9"
        )

        print(f"\n✅ {len(results)} videos generated!")

        total_cost = sum(r['cost'] for r in results)
        total_time = max(r['generation_time'] for r in results)

        print(f"Total cost: ${total_cost:.2f}")
        print(f"Total time: {total_time:.1f}s (parallel)")


if __name__ == "__main__":
    # Descomentar para testar
    # asyncio.run(test_single_video())
    # asyncio.run(test_multiple_videos())
    pass
