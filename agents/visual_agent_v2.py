"""
Visual Agent V2 - Integracao Eficiente Pexels + Stability AI

MELHORIAS vs V1:
1. SceneClassifier de 3 niveis (80% sem LLM)
2. Categoria "both" para cenas hibridas
3. MCP tool calling nativo (1 chamada vs 2)
4. Fallbacks contextuais (nao hardcoded)
5. Metricas de telemetria integradas

Performance esperada:
- 50% menos chamadas LLM
- 80% decisoes no Nivel 1 (instantaneo)
- Melhor qualidade com categoria hibrida
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field

from core import AIClientFactory
from core.scene_classifier import SceneClassifier, ClassificationResult
from mcp import MCPVisualServer
from mcp.tools import search_pexels_video, generate_stability_image, generate_hybrid_visual
from mcp.schemas import VisualResult, PexelsSearchResult, StabilityImageResult, HybridVisualResult


@dataclass
class VisualMetrics:
    """Metricas de geracao visual para telemetria"""
    total_scenes: int = 0
    pexels_count: int = 0
    stability_count: int = 0
    hybrid_count: int = 0
    placeholder_count: int = 0

    level_1_decisions: int = 0  # Keywords (sem LLM)
    level_2_decisions: int = 0  # Hybrid detection (sem LLM)
    level_3_decisions: int = 0  # MCP tool calling (com LLM)

    total_cost: float = 0.0
    total_duration_ms: float = 0.0

    errors: int = 0
    fallbacks_used: int = 0

    def add_scene(
        self,
        source: str,
        cost: float,
        level: int,
        duration_ms: float = 0,
        is_fallback: bool = False
    ):
        """Registra metricas de uma cena processada"""
        self.total_scenes += 1
        self.total_cost += cost
        self.total_duration_ms += duration_ms

        if source == "pexels":
            self.pexels_count += 1
        elif source == "stability_ai":
            self.stability_count += 1
        elif source == "both":
            self.hybrid_count += 1
        else:
            self.placeholder_count += 1

        if level == 1:
            self.level_1_decisions += 1
        elif level == 2:
            self.level_2_decisions += 1
        else:
            self.level_3_decisions += 1

        if is_fallback:
            self.fallbacks_used += 1

    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo das metricas"""
        if self.total_scenes == 0:
            return {"status": "no_scenes_processed"}

        no_llm = self.level_1_decisions + self.level_2_decisions
        efficiency = no_llm / self.total_scenes if self.total_scenes > 0 else 0

        return {
            "total_scenes": self.total_scenes,
            "sources": {
                "pexels": self.pexels_count,
                "stability": self.stability_count,
                "hybrid": self.hybrid_count,
                "placeholder": self.placeholder_count
            },
            "decision_levels": {
                "level_1_keywords": self.level_1_decisions,
                "level_2_hybrid": self.level_2_decisions,
                "level_3_mcp": self.level_3_decisions
            },
            "efficiency": f"{efficiency:.1%}",
            "efficiency_description": f"{no_llm}/{self.total_scenes} decisoes sem LLM",
            "total_cost": f"${self.total_cost:.4f}",
            "avg_cost_per_scene": f"${self.total_cost/self.total_scenes:.4f}",
            "errors": self.errors,
            "fallbacks_used": self.fallbacks_used
        }


class VisualAgentV2:
    """
    Visual Agent V2 - Integracao Eficiente Pexels + Stability.

    Usa SceneClassifier de 3 niveis para decisoes rapidas:
    - Nivel 1: Keywords (80% das cenas, sem LLM)
    - Nivel 2: Deteccao hibrida (15%, sem LLM)
    - Nivel 3: MCP tool calling (5%, com LLM)

    Suporta 3 tipos de resultado:
    - Pexels: Video real (pessoas, acoes)
    - Stability: Imagem gerada (logos, abstratos)
    - Both: Video + overlay (pessoas + elementos digitais)
    """

    def __init__(self, model_name: str = None):
        """
        Inicializa Visual Agent V2.

        Args:
            model_name: Modelo para MCP tool calling (None = auto-detecta)
        """
        self.logger = logging.getLogger(self.__class__.__name__)

        # Classificador inteligente de 3 niveis
        self.classifier = SceneClassifier()

        # MCP Server para tool calling (Nivel 3)
        if model_name:
            self.mcp_server = MCPVisualServer(model_name=model_name)
        else:
            visual_client = AIClientFactory.create_for_agent("visual")
            self.mcp_server = MCPVisualServer(model_name=visual_client.model)

        # Metricas
        self.metrics = VisualMetrics()

        self.logger.info("Visual Agent V2 inicializado (3-level classifier + MCP)")


    async def plan_visuals(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera plano visual completo usando integracao eficiente.

        Args:
            state: Estado com roteiro gerado

        Returns:
            Estado atualizado com plano visual
        """
        self.logger.info("=== VISUAL AGENT V2 ===")
        self.logger.info("Planejando conteudo visual (integracao eficiente)...")

        script = state.get("script")
        if not script:
            raise ValueError("Script nao encontrado no estado")

        scenes = script.get("scenes", [])
        if not scenes:
            raise ValueError("Script sem cenas")

        # Resetar metricas para este video
        self.metrics = VisualMetrics()

        # Processar cada cena
        visual_plan = {
            "visual_plan_id": f"visual_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "scenes": [],
            "generated_at": datetime.now().isoformat(),
            "version": "v2",
            "classifier": "3-level"
        }

        for scene in scenes:
            scene_num = scene.get("scene_number", 1)
            self.logger.info(f"\n--- Cena {scene_num} ---")

            try:
                start_time = datetime.now()

                # Gerar visual usando integracao eficiente
                visual_scene = await self._generate_scene_visual(scene, state)

                duration_ms = (datetime.now() - start_time).total_seconds() * 1000

                # Registrar metricas
                self.metrics.add_scene(
                    source=visual_scene.get("source", "unknown"),
                    cost=visual_scene.get("cost", 0),
                    level=visual_scene.get("classification_level", 3),
                    duration_ms=duration_ms,
                    is_fallback=visual_scene.get("is_fallback", False)
                )

                visual_plan["scenes"].append(visual_scene)

            except Exception as e:
                self.logger.error(f"Erro na cena {scene_num}: {e}")
                self.metrics.errors += 1

                # Criar placeholder
                visual_plan["scenes"].append(
                    self._create_placeholder_scene(scene_num, str(e))
                )

        # Adicionar metricas ao plano
        visual_plan["metrics"] = self.metrics.get_summary()

        # Atualizar estado
        state["visual_plan"] = visual_plan
        state["current_phase"] = 2

        # Log final
        self.logger.info("\n=== RESULTADO VISUAL V2 ===")
        self.logger.info(f"Cenas processadas: {len(visual_plan['scenes'])}")
        self.logger.info(f"Eficiencia: {visual_plan['metrics']['efficiency']}")
        self.logger.info(f"Custo total: {visual_plan['metrics']['total_cost']}")
        self.logger.info(f"Fontes: Pexels={self.metrics.pexels_count}, "
                        f"Stability={self.metrics.stability_count}, "
                        f"Hybrid={self.metrics.hybrid_count}")

        return state


    async def _generate_scene_visual(
        self,
        scene: Dict[str, Any],
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Gera visual para cena usando integracao eficiente de 3 niveis.

        FLUXO:
        1. Classificador decide tipo (80% sem LLM)
        2. Se pexels/stability: executa diretamente
        3. Se both: executa hibrido
        4. Se unknown: MCP tool calling

        Args:
            scene: Dados da cena
            state: Estado completo

        Returns:
            Dados visuais da cena
        """
        scene_num = scene.get("scene_number", 1)
        description = scene.get("visual_description", "")
        mood = scene.get("mood", "neutral")
        style = state.get("brief", {}).get("style", "professional")

        self.logger.info(f"Descricao: {description[:60]}...")

        # PASSO 1: Classificar cena (3 niveis)
        classification = self.classifier.classify(description, mood, style)

        self.logger.info(
            f"Classificacao: {classification.tool.upper()} "
            f"(L{classification.level}, conf={classification.confidence:.0%})"
        )

        # PASSO 2: Executar baseado na classificacao
        try:
            if classification.tool == "pexels":
                return await self._execute_pexels(scene_num, description, mood, classification)

            elif classification.tool == "stability":
                return await self._execute_stability(scene_num, description, mood, style, classification)

            elif classification.tool == "both":
                return await self._execute_hybrid(scene_num, description, mood, style, classification)

            else:  # unknown -> MCP tool calling
                return await self._execute_mcp(scene_num, description, mood, style, classification)

        except Exception as e:
            self.logger.error(f"Erro na execucao: {e}")
            # Tentar fallback
            return await self._execute_fallback(scene_num, description, mood, classification, str(e))


    async def _execute_pexels(
        self,
        scene_num: int,
        description: str,
        mood: str,
        classification: ClassificationResult
    ) -> Dict[str, Any]:
        """Executa busca Pexels diretamente (sem MCP)"""
        self.logger.info("Executando Pexels direto...")

        # Gerar keywords simples (sem LLM adicional)
        keywords = self._generate_keywords_simple(description)

        result = search_pexels_video(keywords=keywords)

        return {
            "scene_number": scene_num,
            "media_path": result.local_path,
            "media_type": "video",
            "source": "pexels",
            "duration": 5,
            "mood": mood,
            "cost": result.cost,
            "keywords": result.keywords,
            "pexels_video_id": result.video_id,
            "classification_level": classification.level,
            "classification_reason": classification.reason
        }


    async def _execute_stability(
        self,
        scene_num: int,
        description: str,
        mood: str,
        style: str,
        classification: ClassificationResult
    ) -> Dict[str, Any]:
        """Executa geracao Stability diretamente (sem MCP)"""
        self.logger.info("Executando Stability direto...")

        # Gerar prompt simples (sem LLM adicional)
        prompt = self._generate_prompt_simple(description, mood, style)

        result = generate_stability_image(prompt=prompt)

        return {
            "scene_number": scene_num,
            "media_path": result.image_path,
            "media_type": "image",
            "source": "stability_ai",
            "prompt_used": result.prompt_used,
            "duration": 5,
            "mood": mood,
            "cost": result.cost,
            "classification_level": classification.level,
            "classification_reason": classification.reason
        }


    async def _execute_hybrid(
        self,
        scene_num: int,
        description: str,
        mood: str,
        style: str,
        classification: ClassificationResult
    ) -> Dict[str, Any]:
        """Executa geracao hibrida (Pexels + Stability overlay)"""
        self.logger.info("Executando Hybrid (Pexels + Stability overlay)...")

        # Separar keywords para video e prompt para overlay
        video_keywords = self._generate_keywords_simple(description)
        overlay_prompt = self._generate_overlay_prompt(description, mood, style)

        result = generate_hybrid_visual(
            video_keywords=video_keywords,
            overlay_prompt=overlay_prompt,
            overlay_position="bottom-right",
            overlay_scale=0.25
        )

        return {
            "scene_number": scene_num,
            "media_type": "hybrid",
            "source": "both",

            # Video
            "video_path": result.video_local_path,
            "video_id": result.video_id,
            "video_keywords": result.video_keywords,

            # Overlay
            "overlay_path": result.image_path,
            "overlay_prompt": result.image_prompt,
            "overlay_position": result.overlay_position,
            "overlay_scale": result.overlay_scale,

            "duration": result.video_duration,
            "mood": mood,
            "cost": result.cost,
            "classification_level": classification.level,
            "classification_reason": classification.reason
        }


    async def _execute_mcp(
        self,
        scene_num: int,
        description: str,
        mood: str,
        style: str,
        classification: ClassificationResult
    ) -> Dict[str, Any]:
        """Executa via MCP tool calling (LLM decide)"""
        self.logger.info("Executando via MCP (LLM tool calling)...")

        result = await self.mcp_server.get_visual_for_scene(
            description=description,
            mood=mood,
            style=style
        )

        # Processar resultado baseado no tipo
        if result.source == "pexels":
            return {
                "scene_number": scene_num,
                "media_path": result.local_path,
                "media_type": "video",
                "source": "pexels",
                "duration": 5,
                "mood": mood,
                "cost": result.cost,
                "keywords": result.keywords,
                "pexels_video_id": result.video_id,
                "classification_level": 3,
                "classification_reason": "MCP tool calling"
            }

        elif result.source == "stability_ai":
            return {
                "scene_number": scene_num,
                "media_path": result.image_path,
                "media_type": "image",
                "source": "stability_ai",
                "prompt_used": result.prompt_used,
                "duration": 5,
                "mood": mood,
                "cost": result.cost,
                "classification_level": 3,
                "classification_reason": "MCP tool calling"
            }

        else:  # both (hybrid)
            return {
                "scene_number": scene_num,
                "media_type": "hybrid",
                "source": "both",
                "video_path": result.video_local_path,
                "overlay_path": result.image_path,
                "duration": result.video_duration,
                "mood": mood,
                "cost": result.cost,
                "classification_level": 3,
                "classification_reason": "MCP tool calling"
            }


    async def _execute_fallback(
        self,
        scene_num: int,
        description: str,
        mood: str,
        classification: ClassificationResult,
        error: str
    ) -> Dict[str, Any]:
        """Executa fallback quando execucao principal falha"""
        self.logger.warning(f"Executando fallback (erro: {error[:50]}...)")

        # Se era para ser Stability e falhou, tentar Pexels
        if classification.tool == "stability":
            try:
                keywords = self._generate_keywords_simple(description)
                result = search_pexels_video(keywords=keywords)

                return {
                    "scene_number": scene_num,
                    "media_path": result.local_path,
                    "media_type": "video",
                    "source": "pexels",
                    "duration": 5,
                    "mood": mood,
                    "cost": result.cost,
                    "is_fallback": True,
                    "original_error": error,
                    "classification_level": classification.level
                }
            except:
                pass

        # Se era para ser Pexels e falhou, tentar Stability
        if classification.tool == "pexels":
            try:
                prompt = self._generate_prompt_simple(description, mood, "professional")
                result = generate_stability_image(prompt=prompt)

                return {
                    "scene_number": scene_num,
                    "media_path": result.image_path,
                    "media_type": "image",
                    "source": "stability_ai",
                    "duration": 5,
                    "mood": mood,
                    "cost": result.cost,
                    "is_fallback": True,
                    "original_error": error,
                    "classification_level": classification.level
                }
            except:
                pass

        # Ultimo recurso: placeholder
        return self._create_placeholder_scene(scene_num, error)


    def _generate_keywords_simple(self, description: str) -> str:
        """
        Gera keywords para Pexels SEM chamar LLM.

        Usa mapeamento PT->EN e extrai palavras relevantes.
        """
        pt_to_en = {
            'pessoa': 'person', 'pessoas': 'people', 'trabalhando': 'working',
            'escritorio': 'office', 'reuniao': 'meeting', 'equipe': 'team',
            'laptop': 'laptop', 'computador': 'computer', 'apresentando': 'presenting',
            'professor': 'teacher', 'estudante': 'student', 'aula': 'classroom',
            'tecnologia': 'technology', 'negocio': 'business', 'moderno': 'modern'
        }

        words = description.lower().split()
        keywords = []

        for word in words:
            clean = ''.join(c for c in word if c.isalnum())
            if clean in pt_to_en:
                keywords.append(pt_to_en[clean])

        if keywords:
            return ' '.join(keywords[:5])

        return "business professional modern"


    def _generate_prompt_simple(self, description: str, mood: str, style: str) -> str:
        """
        Gera prompt para Stability SEM chamar LLM.

        Monta prompt baseado em padroes comuns.
        """
        # Detectar tipo
        desc_lower = description.lower()

        if any(p in desc_lower for p in ['logo', 'marca', 'brand']):
            base = "modern minimalist logo, professional design"
        elif any(p in desc_lower for p in ['holograma', 'hologram']):
            base = "holographic display, futuristic technology, glowing"
        elif any(p in desc_lower for p in ['dados', 'data', 'grafico']):
            base = "abstract data visualization, flowing particles"
        else:
            base = "modern abstract concept, professional design"

        return f"{base}, {mood} mood, {style} style, high quality, 4k"


    def _generate_overlay_prompt(self, description: str, mood: str, style: str) -> str:
        """
        Gera prompt para overlay (imagem menor, fundo transparente).
        """
        desc_lower = description.lower()

        if any(p in desc_lower for p in ['logo', 'marca']):
            return "minimalist logo icon, clean design, suitable for overlay, no background"
        elif any(p in desc_lower for p in ['grafico', 'chart', 'dados']):
            return "simple data chart icon, clean lines, blue colors, no background"
        elif any(p in desc_lower for p in ['holograma', 'digital']):
            return "holographic icon, glowing blue, futuristic, transparent style"
        else:
            return f"abstract {style} icon, clean design, {mood} mood, no background"


    def _create_placeholder_scene(self, scene_num: int, error: str) -> Dict[str, Any]:
        """Cria placeholder em caso de erro total"""
        self.logger.warning(f"Criando placeholder para cena {scene_num}")

        return {
            "scene_number": scene_num,
            "media_path": "placeholder",
            "media_type": "placeholder",
            "source": "error",
            "duration": 5,
            "cost": 0.0,
            "error": error,
            "classification_level": 0
        }


    def get_metrics(self) -> Dict[str, Any]:
        """Retorna metricas de processamento"""
        return self.metrics.get_summary()


    def get_classifier_stats(self) -> Dict[str, Any]:
        """Retorna estatisticas do classificador"""
        return self.classifier.get_stats()
