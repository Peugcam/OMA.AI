"""
🎬 MEDIA GENERATION AGENT - Modern Video & Image APIs
====================================================

Integrates with latest AI media generation services:
- Leonardo.ai (Motion) - Best cost-benefit
- Runway Gen-3 - Premium video
- Luma AI - Dream Machine
- HeyGen - AI Avatars
- Flux.1 - Image generation
- DALL-E 3 - OpenAI images
"""

import os
import asyncio
import httpx
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class MediaQuality(Enum):
    """Quality levels for media generation"""
    ECONOMY = "economy"    # Cheapest, fastest
    STANDARD = "standard"  # Good quality
    PREMIUM = "premium"    # Best quality


@dataclass
class MediaConfig:
    """Configuration for media generation"""
    quality: MediaQuality = MediaQuality.STANDARD
    leonardo_api_key: Optional[str] = None
    runway_api_key: Optional[str] = None
    luma_api_key: Optional[str] = None
    heygen_api_key: Optional[str] = None
    fal_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None


class MediaGenerationAgent:
    """
    Agent for generating videos and images using modern AI APIs.

    Cost comparison (30s video):
    - Economy mode: $0.15-0.30 (Leonardo + Flux)
    - Standard mode: $0.50-1.00 (Luma + DALL-E)
    - Premium mode: $2.00-3.50 (Runway + Midjourney)
    """

    def __init__(self, config: MediaConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=120.0)

    async def generate_video_clip(
        self,
        prompt: str,
        duration: int = 5,
        quality: Optional[MediaQuality] = None
    ) -> Dict[str, Any]:
        """
        Generate video clip from text prompt.

        Args:
            prompt: Description of the video
            duration: Duration in seconds (3-10)
            quality: Quality level (overrides config)

        Returns:
            Dict with video_url, cost, generation_time
        """
        quality = quality or self.config.quality

        if quality == MediaQuality.ECONOMY:
            return await self._generate_leonardo_clip(prompt, duration)
        elif quality == MediaQuality.STANDARD:
            return await self._generate_luma_clip(prompt, duration)
        else:  # PREMIUM
            return await self._generate_runway_clip(prompt, duration)

    async def _generate_leonardo_clip(
        self,
        prompt: str,
        duration: int
    ) -> Dict[str, Any]:
        """Generate video using Leonardo.ai Motion"""

        # First, generate an image
        image_response = await self.client.post(
            "https://cloud.leonardo.ai/api/rest/v1/generations",
            headers={
                "Authorization": f"Bearer {self.config.leonardo_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "prompt": prompt,
                "modelId": "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3",  # Leonardo Diffusion XL
                "width": 1024,
                "height": 576,
                "num_images": 1
            }
        )

        image_data = image_response.json()
        generation_id = image_data["sdGenerationJob"]["generationId"]

        # Wait for image to be ready
        await asyncio.sleep(10)

        # Get generated image
        image_result = await self.client.get(
            f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}",
            headers={"Authorization": f"Bearer {self.config.leonardo_api_key}"}
        )

        image_id = image_result.json()["generations_by_pk"]["generated_images"][0]["id"]

        # Generate motion from image
        motion_response = await self.client.post(
            "https://cloud.leonardo.ai/api/rest/v1/generations-motion-svd",
            headers={
                "Authorization": f"Bearer {self.config.leonardo_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "imageId": image_id,
                "motionStrength": 5,
                "isPublic": False
            }
        )

        motion_id = motion_response.json()["motionSvdGenerationJob"]["generationId"]

        # Wait for video to be ready
        await asyncio.sleep(30)

        # Get video URL
        result = await self.client.get(
            f"https://cloud.leonardo.ai/api/rest/v1/generations/{motion_id}",
            headers={"Authorization": f"Bearer {self.config.leonardo_api_key}"}
        )

        video_url = result.json()["generations_by_pk"]["generated_videos"][0]["url"]

        return {
            "video_url": video_url,
            "cost": 0.01,  # $0.01 per 4s clip
            "generation_time": 40,
            "provider": "leonardo",
            "duration": 4
        }

    async def _generate_luma_clip(
        self,
        prompt: str,
        duration: int
    ) -> Dict[str, Any]:
        """Generate video using Luma AI Dream Machine"""

        response = await self.client.post(
            "https://api.lumalabs.ai/dream-machine/v1/generations",
            headers={
                "Authorization": f"Bearer {self.config.luma_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "prompt": prompt,
                "aspect_ratio": "16:9",
                "loop": False
            }
        )

        generation_id = response.json()["id"]

        # Poll for completion (Luma is slower)
        for _ in range(60):  # Max 2 minutes
            await asyncio.sleep(2)

            status_response = await self.client.get(
                f"https://api.lumalabs.ai/dream-machine/v1/generations/{generation_id}",
                headers={"Authorization": f"Bearer {self.config.luma_api_key}"}
            )

            status_data = status_response.json()

            if status_data["state"] == "completed":
                return {
                    "video_url": status_data["video"]["url"],
                    "cost": 0.10,  # $0.10 per 5s clip
                    "generation_time": status_data.get("generation_time", 60),
                    "provider": "luma",
                    "duration": 5
                }
            elif status_data["state"] == "failed":
                raise Exception(f"Luma generation failed: {status_data.get('failure_reason')}")

        raise TimeoutError("Luma generation timed out")

    async def _generate_runway_clip(
        self,
        prompt: str,
        duration: int
    ) -> Dict[str, Any]:
        """Generate video using Runway Gen-3"""

        response = await self.client.post(
            "https://api.runwayml.com/v1/generate",
            headers={
                "Authorization": f"Bearer {self.config.runway_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "prompt": prompt,
                "duration": min(duration, 10),
                "aspect_ratio": "16:9",
                "model": "gen3a_turbo"
            }
        )

        task_id = response.json()["id"]

        # Poll for completion
        for _ in range(120):  # Max 4 minutes
            await asyncio.sleep(2)

            status_response = await self.client.get(
                f"https://api.runwayml.com/v1/tasks/{task_id}",
                headers={"Authorization": f"Bearer {self.config.runway_api_key}"}
            )

            status_data = status_response.json()

            if status_data["status"] == "SUCCEEDED":
                actual_duration = min(duration, 10)
                return {
                    "video_url": status_data["output"][0],
                    "cost": actual_duration * 0.05,  # $0.05 per second
                    "generation_time": status_data.get("progress", {}).get("duration", 90),
                    "provider": "runway",
                    "duration": actual_duration
                }
            elif status_data["status"] == "FAILED":
                raise Exception(f"Runway generation failed: {status_data.get('error')}")

        raise TimeoutError("Runway generation timed out")

    async def generate_image(
        self,
        prompt: str,
        quality: Optional[MediaQuality] = None
    ) -> Dict[str, Any]:
        """
        Generate image from text prompt.

        Args:
            prompt: Description of the image
            quality: Quality level

        Returns:
            Dict with image_url, cost, generation_time
        """
        quality = quality or self.config.quality

        if quality == MediaQuality.ECONOMY:
            return await self._generate_flux_image(prompt)
        elif quality == MediaQuality.STANDARD:
            return await self._generate_dalle_image(prompt)
        else:  # PREMIUM
            return await self._generate_dalle_image(prompt, model="dall-e-3", quality="hd")

    async def _generate_flux_image(self, prompt: str) -> Dict[str, Any]:
        """Generate image using Flux.1 via fal.ai"""

        response = await self.client.post(
            "https://fal.run/fal-ai/flux-pro",
            headers={
                "Authorization": f"Key {self.config.fal_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "prompt": prompt,
                "image_size": "landscape_16_9",
                "num_inference_steps": 28,
                "guidance_scale": 3.5
            }
        )

        result = response.json()

        return {
            "image_url": result["images"][0]["url"],
            "cost": 0.03,  # $0.03 per image
            "generation_time": 5,
            "provider": "flux",
            "width": 1344,
            "height": 768
        }

    async def _generate_dalle_image(
        self,
        prompt: str,
        model: str = "dall-e-3",
        quality: str = "standard"
    ) -> Dict[str, Any]:
        """Generate image using DALL-E 3"""

        response = await self.client.post(
            "https://api.openai.com/v1/images/generations",
            headers={
                "Authorization": f"Bearer {self.config.openai_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "prompt": prompt,
                "size": "1792x1024",
                "quality": quality,
                "n": 1
            }
        )

        result = response.json()

        cost = 0.080 if quality == "hd" else 0.040

        return {
            "image_url": result["data"][0]["url"],
            "cost": cost,
            "generation_time": 10,
            "provider": "dall-e-3",
            "width": 1792,
            "height": 1024
        }

    async def generate_avatar_video(
        self,
        script: str,
        avatar_id: Optional[str] = None,
        voice_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate video with AI avatar speaking.

        Args:
            script: Text for avatar to speak
            avatar_id: HeyGen avatar ID (optional)
            voice_id: HeyGen voice ID (optional)

        Returns:
            Dict with video_url, cost, duration
        """

        response = await self.client.post(
            "https://api.heygen.com/v2/video/generate",
            headers={
                "X-Api-Key": self.config.heygen_api_key,
                "Content-Type": "application/json"
            },
            json={
                "video_inputs": [{
                    "character": {
                        "type": "avatar",
                        "avatar_id": avatar_id or "default",
                        "avatar_style": "normal"
                    },
                    "voice": {
                        "type": "text",
                        "input_text": script,
                        "voice_id": voice_id or "pt-BR-FranciscaNeural"  # Portuguese
                    }
                }],
                "dimension": {
                    "width": 1920,
                    "height": 1080
                },
                "aspect_ratio": "16:9"
            }
        )

        video_id = response.json()["data"]["video_id"]

        # Poll for completion
        for _ in range(180):  # Max 6 minutes
            await asyncio.sleep(2)

            status_response = await self.client.get(
                f"https://api.heygen.com/v1/video_status.get?video_id={video_id}",
                headers={"X-Api-Key": self.config.heygen_api_key}
            )

            status_data = status_response.json()

            if status_data["data"]["status"] == "completed":
                duration = status_data["data"]["duration"]
                return {
                    "video_url": status_data["data"]["video_url"],
                    "cost": (duration / 60) * 0.096,  # $0.096 per minute
                    "generation_time": status_data["data"].get("processing_time", 120),
                    "provider": "heygen",
                    "duration": duration
                }
            elif status_data["data"]["status"] == "failed":
                raise Exception("HeyGen generation failed")

        raise TimeoutError("HeyGen generation timed out")

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Example usage
if __name__ == "__main__":
    async def test():
        config = MediaConfig(
            quality=MediaQuality.ECONOMY,
            leonardo_api_key=os.getenv("LEONARDO_API_KEY"),
            fal_api_key=os.getenv("FAL_API_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            heygen_api_key=os.getenv("HEYGEN_API_KEY")
        )

        agent = MediaGenerationAgent(config)

        try:
            # Generate video clip
            video = await agent.generate_video_clip(
                "A futuristic city with flying cars at sunset",
                duration=5
            )
            print(f"Video: {video['video_url']}, Cost: ${video['cost']}")

            # Generate image
            image = await agent.generate_image(
                "A beautiful landscape with mountains and lakes"
            )
            print(f"Image: {image['image_url']}, Cost: ${image['cost']}")

            # Generate avatar video
            avatar = await agent.generate_avatar_video(
                "Olá! Bem-vindo ao futuro da criação de vídeos com IA."
            )
            print(f"Avatar: {avatar['video_url']}, Cost: ${avatar['cost']}")

        finally:
            await agent.close()

    asyncio.run(test())
