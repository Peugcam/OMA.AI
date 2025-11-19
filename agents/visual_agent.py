"""
Visual Agent - Planejador de Conteudo Visual

Analisa roteiro e cria plano visual com placeholders.
Usa apenas OpenRouter (uma API).
Integrado com módulos otimizados.
"""

import logging
import os
import requests
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

from core import AIClient, AIClientFactory, PromptTemplates, ResponseValidator


class VisualAgent:
    """
    Agente especializado em gerar/buscar conteúdo visual.

    Uses:
    - Stability AI para geração de imagens
    - Gemma-2-9B (via OpenRouter) para análise e keywords
    """

    def __init__(self, model_name: str = None):
        """
        Inicializa Visual Agent.

        Args:
            model_name: Modelo para análise (None = auto-detecta do .env)
        """
        self.logger = logging.getLogger(self.__class__.__name__)

        # AI client para análise de cenas
        if model_name:
            self.llm = AIClient(model=model_name, temperature=0.5)
        else:
            self.llm = AIClientFactory.create_for_agent("visual")

        # Stability AI API key
        self.stability_api_key = os.getenv("STABILITY_API_KEY")
        if not self.stability_api_key:
            self.logger.warning("STABILITY_API_KEY não configurada, usando placeholders")

        # Diretórios de saída (múltiplos locais)
        self.output_dirs = [
            Path("C:/Users/paulo/OneDrive/Desktop/OMA_Videos/images"),
            Path("D:/OMA_Videos/images"),
            Path("./outputs/images")
        ]

        # Criar diretórios
        for dir_path in self.output_dirs:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                self.logger.warning(f"Não foi possível criar {dir_path}: {e}")

        # Usar primeiro como principal
        self.output_dir = self.output_dirs[0]

        # System prompt
        self.system_prompt = PromptTemplates.visual_system_prompt()


    async def plan_visuals(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera plano visual completo baseado no roteiro.

        Args:
            state: Estado com roteiro gerado

        Returns:
            Estado atualizado com plano visual
        """
        self.logger.info("Planejando conteúdo visual...")

        script = state.get("script")
        if not script:
            raise ValueError("Script não encontrado no estado")

        scenes = script.get("scenes", [])
        if not scenes:
            raise ValueError("Script sem cenas")

        # Processar cada cena
        visual_plan = {
            "visual_plan_id": f"visual_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "scenes": [],
            "generated_at": datetime.now().isoformat()
        }

        for scene in scenes:
            self.logger.info(f"Processando cena {scene['scene_number']}...")

            # Gerar imagem para a cena
            visual_scene = await self._generate_scene_visual(scene, state)

            visual_plan["scenes"].append(visual_scene)

        # Atualizar estado
        state["visual_plan"] = visual_plan
        state["current_phase"] = 2

        self.logger.info(f"OK - Plano visual criado: {len(visual_plan['scenes'])} cenas")

        return state


    async def _generate_scene_visual(
        self,
        scene: Dict[str, Any],
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Gera imagem para uma cena específica.

        Args:
            scene: Dados da cena do roteiro
            state: Estado completo

        Returns:
            Dados visuais da cena
        """
        scene_num = scene.get("scene_number", 1)
        description = scene.get("visual_description", "")
        mood = scene.get("mood", "neutral")

        # Criar prompt para Stability AI
        prompt = self._create_image_prompt(description, mood, state)

        # Gerar imagem
        if self.stability_api_key:
            try:
                image_path = self._generate_with_stability(prompt, scene_num)
                source = "stability_ai"
            except Exception as e:
                self.logger.error(f"Erro ao gerar com Stability AI: {e}")
                image_path = self._create_placeholder_image(scene_num)
                source = "placeholder"
        else:
            self.logger.warning("Usando placeholder (Stability AI não configurada)")
            image_path = self._create_placeholder_image(scene_num)
            source = "placeholder"

        return {
            "scene_number": scene_num,
            "image_path": str(image_path),
            "prompt_used": prompt,
            "duration": scene.get("duration", 5),
            "source": source,
            "mood": mood
        }


    def _create_image_prompt(
        self,
        description: str,
        mood: str,
        state: Dict[str, Any]
    ) -> str:
        """
        Cria prompt otimizado para Stability AI.

        Args:
            description: Descrição visual da cena
            mood: Mood/atmosfera
            state: Estado completo

        Returns:
            Prompt formatado para geração (em inglês)
        """
        style = state.get("brief", {}).get("style", "professional")

        # Criar prompt em português primeiro
        prompt_pt = f"{description}, {mood} mood, {style} style, high quality, detailed, professional photography, 4k"

        # Traduzir para inglês usando o LLM
        prompt_en = self._translate_to_english(prompt_pt)

        self.logger.info(f"Prompt PT: {prompt_pt[:60]}...")
        self.logger.info(f"Prompt EN: {prompt_en[:60]}...")

        return prompt_en


    def _translate_to_english(self, text: str) -> str:
        """
        Traduz texto de português para inglês usando o LLM.

        Args:
            text: Texto em português

        Returns:
            Texto traduzido para inglês
        """
        try:
            translation = self.llm.chat(
                messages=[{
                    "role": "user",
                    "content": f"Translate this to English (just the translation, no extra text):\n\n{text}"
                }],
                temperature=0.3,
                max_tokens=200
            )

            # Limpar resposta (remover aspas, etc)
            translation = translation.strip().strip('"').strip("'")

            return translation

        except Exception as e:
            self.logger.error(f"Erro ao traduzir: {e}")
            # Fallback: retornar original (melhor que falhar)
            return text


    def _generate_with_stability(self, prompt: str, scene_num: int) -> Path:
        """
        Gera imagem usando Stability AI API.

        Args:
            prompt: Prompt para geração
            scene_num: Número da cena

        Returns:
            Path para imagem salva

        Raises:
            Exception: Se geração falhar
        """
        self.logger.info(f"Gerando imagem com Stability AI (cena {scene_num})...")

        # API endpoint
        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

        # Headers
        headers = {
            "Authorization": f"Bearer {self.stability_api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Payload
        payload = {
            "text_prompts": [
                {
                    "text": prompt,
                    "weight": 1
                }
            ],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30
        }

        # Fazer requisição
        response = requests.post(url, json=payload, headers=headers, timeout=60)

        if response.status_code != 200:
            raise Exception(f"Stability AI error: {response.status_code} - {response.text}")

        # Processar resposta
        data = response.json()

        # Salvar imagem
        image_data = data["artifacts"][0]
        image_base64 = image_data["base64"]

        import base64
        image_bytes = base64.b64decode(image_base64)

        # Salvar arquivo
        image_path = self.output_dir / f"scene_{scene_num:02d}.png"
        image_path.write_bytes(image_bytes)

        self.logger.info(f"OK - Imagem salva: {image_path}")

        return image_path


    def _create_placeholder_image(self, scene_num: int) -> Path:
        """
        Cria imagem placeholder quando Stability AI não está disponível.

        Args:
            scene_num: Número da cena

        Returns:
            Path para imagem placeholder
        """
        self.logger.info(f"Criando placeholder para cena {scene_num}...")

        try:
            from PIL import Image, ImageDraw, ImageFont

            # Criar imagem 1024x1024
            img = Image.new('RGB', (1024, 1024), color=(73, 109, 137))
            draw = ImageDraw.Draw(img)

            # Adicionar texto
            text = f"Cena {scene_num}\n(Placeholder)"

            # Tentar usar fonte, senão usar padrão
            try:
                font = ImageFont.truetype("arial.ttf", 60)
            except:
                font = ImageFont.load_default()

            # Posição central
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            position = ((1024 - text_width) // 2, (1024 - text_height) // 2)

            draw.text(position, text, fill=(255, 255, 255), font=font)

            # Salvar
            image_path = self.output_dir / f"scene_{scene_num:02d}_placeholder.png"
            img.save(image_path)

            self.logger.info(f"OK - Placeholder salvo: {image_path}")

            return image_path

        except Exception as e:
            self.logger.error(f"Erro ao criar placeholder: {e}")

            # Criar arquivo texto como último recurso
            image_path = self.output_dir / f"scene_{scene_num:02d}_placeholder.txt"
            image_path.write_text(f"Placeholder para cena {scene_num}")

            return image_path


# ============================================================================
# Para compatibilidade com supervisor antigo
# ============================================================================

# Alias para manter compatibilidade
generate_visuals = VisualAgent().plan_visuals
