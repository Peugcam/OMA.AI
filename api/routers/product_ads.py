"""
📢 PRODUCT ADS API ROUTER
========================

Endpoints para geração de anúncios de produtos via WhatsApp.
Otimizado para afiliados: Beleza, Higiene Feminina, Perfumaria, Eletrônicos.
"""

import os
import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime
import asyncio

from agents.product_ad_agent import ProductAdAgent, ProductCategory, MediaConfig, MediaQuality

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/product-ads",
    tags=["Product Ads"]
)


# Pydantic models
class ProductAdRequest(BaseModel):
    """Request para criar anúncio de produto"""
    name: str
    description: Optional[str] = None
    price: Optional[str] = None
    category: Optional[str] = None
    target_audience: Optional[str] = None
    unique_selling_points: Optional[list[str]] = None
    affiliate_link: Optional[str] = None
    aspect_ratio: str = "16:9"  # "16:9", "9:16", "1:1"
    quality: str = "economy"  # "economy", "standard", "premium"
    webhook_url: Optional[str] = None


class ProductAdResponse(BaseModel):
    """Response com anúncio gerado"""
    task_id: str
    status: str
    message: str
    ad_video_url: Optional[str] = None
    script: Optional[str] = None
    cost: Optional[float] = None
    generation_time: Optional[float] = None


# Storage para tarefas assíncronas
ad_tasks: Dict[str, Dict[str, Any]] = {}


@router.post("/create", response_model=ProductAdResponse)
async def create_product_ad(
    background_tasks: BackgroundTasks,
    product_image: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    price: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    target_audience: Optional[str] = Form(None),
    unique_selling_points: Optional[str] = Form(None),  # JSON string ou comma-separated
    affiliate_link: Optional[str] = Form(None),
    aspect_ratio: str = Form("16:9"),
    quality: str = Form("economy"),
    webhook_url: Optional[str] = Form(None)
):
    """
    Cria anúncio profissional de produto.

    Upload de imagem + informações do produto →
    Análise AI + Pesquisa de mercado + Geração de vídeo →
    Anúncio pronto para publicar

    **Categorias:**
    - beauty, skincare, haircare, makeup
    - feminine_hygiene
    - perfumes
    - electronics, gadgets, home_electronics

    **Aspect Ratios:**
    - 16:9 (YouTube, Facebook)
    - 9:16 (Stories, Reels, TikTok)
    - 1:1 (Instagram Feed)

    **Quality:**
    - economy ($0.12-0.15) - Leonardo + Flux
    - standard ($0.20-0.25) - Luma + DALL-E
    - premium ($0.30-0.40) - Runway + DALL-E HD
    """

    try:
        # Gerar task_id
        task_id = f"ad_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Salvar imagem do produto
        upload_dir = Path("uploads/products")
        upload_dir.mkdir(parents=True, exist_ok=True)

        image_path = upload_dir / f"{task_id}_{product_image.filename}"
        with open(image_path, "wb") as f:
            content = await product_image.read()
            f.write(content)

        # Parse unique_selling_points
        usps = []
        if unique_selling_points:
            if unique_selling_points.startswith('['):
                # JSON
                import json
                usps = json.loads(unique_selling_points)
            else:
                # Comma-separated
                usps = [usp.strip() for usp in unique_selling_points.split(',')]

        # Preparar informações do produto
        product_info = {
            "name": name,
            "description": description,
            "price": price,
            "category": category,
            "target_audience": target_audience,
            "unique_selling_points": usps,
            "affiliate_link": affiliate_link
        }

        # Criar task
        ad_tasks[task_id] = {
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "product_info": product_info,
            "image_path": str(image_path),
            "aspect_ratio": aspect_ratio,
            "quality": quality,
            "webhook_url": webhook_url
        }

        # Processar em background
        background_tasks.add_task(
            _generate_ad_async,
            task_id,
            str(image_path),
            product_info,
            aspect_ratio,
            quality,
            webhook_url
        )

        return ProductAdResponse(
            task_id=task_id,
            status="processing",
            message=f"Anúncio sendo gerado. Use /status/{task_id} para acompanhar."
        )

    except Exception as e:
        logger.error(f"Error creating product ad: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{task_id}", response_model=ProductAdResponse)
async def get_ad_status(task_id: str):
    """
    Verifica status de geração do anúncio.
    """

    if task_id not in ad_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = ad_tasks[task_id]
    status = task["status"]

    if status == "completed":
        return ProductAdResponse(
            task_id=task_id,
            status="completed",
            message="Anúncio gerado com sucesso!",
            ad_video_url=f"/api/v1/product-ads/download/{task_id}",
            script=task.get("result", {}).get("script"),
            cost=task.get("result", {}).get("cost"),
            generation_time=task.get("result", {}).get("generation_time")
        )
    elif status == "failed":
        return ProductAdResponse(
            task_id=task_id,
            status="failed",
            message=f"Erro: {task.get('error')}"
        )
    else:
        return ProductAdResponse(
            task_id=task_id,
            status="processing",
            message="Anúncio sendo gerado..."
        )


@router.get("/download/{task_id}")
async def download_ad(task_id: str):
    """
    Download do vídeo do anúncio.
    """

    if task_id not in ad_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = ad_tasks[task_id]

    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Ad not ready yet")

    video_path = task.get("result", {}).get("ad_video_path")

    if not video_path or not Path(video_path).exists():
        raise HTTPException(status_code=404, detail="Video file not found")

    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=f"product_ad_{task_id}.mp4"
    )


async def _generate_ad_async(
    task_id: str,
    image_path: str,
    product_info: Dict[str, Any],
    aspect_ratio: str,
    quality: str,
    webhook_url: Optional[str]
):
    """
    Gera anúncio de forma assíncrona.
    """

    try:
        # Atualizar status
        ad_tasks[task_id]["status"] = "processing"

        # Enviar webhook de início (se configurado)
        if webhook_url:
            await _send_webhook(webhook_url, task_id, "ad.started", {})

        # Configurar MediaConfig
        quality_map = {
            "economy": MediaQuality.ECONOMY,
            "standard": MediaQuality.STANDARD,
            "premium": MediaQuality.PREMIUM
        }

        config = MediaConfig(
            quality=quality_map.get(quality, MediaQuality.ECONOMY),
            leonardo_api_key=os.getenv("LEONARDO_API_KEY"),
            fal_api_key=os.getenv("FAL_API_KEY"),
            heygen_api_key=os.getenv("HEYGEN_API_KEY"),
            luma_api_key=os.getenv("LUMA_API_KEY"),
            runway_api_key=os.getenv("RUNWAY_API_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        # Criar agente
        agent = ProductAdAgent(config)

        # Gerar anúncio
        result = await agent.create_product_ad(
            product_info=product_info,
            product_image_path=image_path,
            aspect_ratio=aspect_ratio
        )

        # Atualizar task
        ad_tasks[task_id]["status"] = "completed"
        ad_tasks[task_id]["result"] = result
        ad_tasks[task_id]["completed_at"] = datetime.now().isoformat()

        # Enviar webhook de conclusão
        if webhook_url:
            await _send_webhook(webhook_url, task_id, "ad.completed", {
                "video_url": f"/api/v1/product-ads/download/{task_id}",
                "script": result.get("script"),
                "cost": result.get("cost"),
                "generation_time": result.get("generation_time")
            })

        await agent.close()

    except Exception as e:
        logger.error(f"Error generating ad for task {task_id}: {e}")
        ad_tasks[task_id]["status"] = "failed"
        ad_tasks[task_id]["error"] = str(e)
        ad_tasks[task_id]["failed_at"] = datetime.now().isoformat()

        # Enviar webhook de erro
        if webhook_url:
            await _send_webhook(webhook_url, task_id, "ad.failed", {
                "error": str(e)
            })


async def _send_webhook(webhook_url: str, task_id: str, event: str, data: Dict[str, Any]):
    """Envia webhook de notificação"""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "event": event,
                "task_id": task_id,
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            await client.post(webhook_url, json=payload)
            logger.info(f"Webhook sent: {event} for task {task_id}")
    except Exception as e:
        logger.warning(f"Failed to send webhook: {e}")
