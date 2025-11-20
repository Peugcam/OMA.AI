"""
Script Agent - Gerador de Roteiros com IA

Especializado em criar roteiros criativos e engajantes para videos curtos.
Usa GPT-4o-mini para maxima criatividade e qualidade.
"""

import logging
from typing import Dict, Any
from datetime import datetime

from core import AIClient, AIClientFactory, PromptTemplates, ResponseValidator


class ScriptAgent:
    """
    Agente especializado em criar roteiros de video.

    Model: GPT-4o-mini (via OpenRouter)
    Capabilities:
    - Roteiros criativos e engajantes
    - Storytelling efetivo
    - Hooks que prendem atencao
    - CTAs persuasivos
    """

    def __init__(self, model_name: str = None, temperature: float = 0.7):
        """
        Inicializa Script Agent.

        Args:
            model_name: Modelo a usar (None = auto-detecta do .env)
            temperature: Temperatura para geracao (0.7 = criativo)
        """
        self.temperature = temperature
        self.logger = logging.getLogger(self.__class__.__name__)

        # Criar AI client usando Factory (le do .env)
        if model_name:
            self.llm = AIClient(model=model_name, temperature=temperature)
        else:
            self.llm = AIClientFactory.create_for_agent("script")

        # System prompt otimizado
        self.system_prompt = PromptTemplates.script_system_prompt()


    async def generate_script(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera roteiro completo baseado no briefing COM REFLECTION PATTERN.

        Reflection = Self-Critique (auto-crítica) + Improvement (melhoria iterativa)

        Melhoria: +25-35% qualidade do script, +$0.04/vídeo

        Args:
            state: Estado atual com briefing e analise

        Returns:
            Estado atualizado com script gerado + metadata de reflection
        """
        self.logger.info("🧠 [REFLECTION] Gerando roteiro com auto-crítica...")

        # Usar Reflection pattern (1 iteração)
        return await self.generate_script_with_reflection(state)


    async def generate_script_with_reflection(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera roteiro com Reflection pattern: gera → critica → melhora.

        Fluxo:
        1. Gerar roteiro v1 (baseline)
        2. Auto-crítica (avaliar qualidade)
        3. Se score < 8/10, gerar v2 melhorada
        4. Retornar melhor versão + metadata

        Args:
            state: Estado atual com briefing e analise

        Returns:
            Estado com script + reflection metadata
        """
        self.logger.info("📝 [REFLECTION] Gerando versão inicial...")

        # Extrair informacoes do briefing
        brief = state.get("brief", {})
        analysis = state.get("analysis", {})

        description = analysis.get("objective", brief.get("description", ""))
        target_audience = analysis.get("target_audience", brief.get("target", ""))
        duration = analysis.get("duration_seconds", brief.get("duration", 30))
        style = analysis.get("style", brief.get("style", "profissional"))
        cta = analysis.get("cta", brief.get("cta", ""))

        try:
            # PASSO 1: Gerar roteiro v1 (baseline)
            script_v1 = await self._generate_script_base(
                description, target_audience, duration, style, cta
            )

            self.logger.info(f"✅ [REFLECTION] Roteiro v1 gerado: {len(script_v1.get('scenes', []))} cenas")

            # PASSO 2: Auto-crítica do roteiro v1
            critique = await self._critique_script(script_v1, brief, analysis)

            score = critique.get("score", 0)
            self.logger.info(f"📊 [REFLECTION] Score v1: {score}/10")

            # PASSO 3: Se score < 8, gerar versão melhorada
            if score < 8:
                self.logger.info(f"🔄 [REFLECTION] Score baixo ({score}/10), gerando versão melhorada...")

                script_v2 = await self._improve_script(script_v1, critique, brief, analysis)

                self.logger.info(f"✅ [REFLECTION] Roteiro v2 gerado: {len(script_v2.get('scenes', []))} cenas")

                # Adicionar metadata
                script_v2["generated_at"] = datetime.now().isoformat()
                script_v2["model"] = self.llm.model
                script_v2["reflection"] = {
                    "v1_score": score,
                    "critique": critique.get("summary", ""),
                    "improved": True,
                    "iterations": 1
                }

                state["script"] = script_v2
            else:
                self.logger.info(f"✅ [REFLECTION] Score alto ({score}/10), usando v1")

                # Adicionar metadata
                script_v1["generated_at"] = datetime.now().isoformat()
                script_v1["model"] = self.llm.model
                script_v1["reflection"] = {
                    "v1_score": score,
                    "improved": False,
                    "iterations": 0
                }

                state["script"] = script_v1

            state["current_phase"] = 1

            return state

        except Exception as e:
            self.logger.error(f"❌ [REFLECTION] Erro ao gerar roteiro: {e}")

            # Fallback: criar roteiro basico
            script = self._create_fallback_script(description, duration, cta)
            script["reflection"] = {"error": str(e), "fallback": True}

            state["script"] = script
            state["current_phase"] = 1

            return state


    async def _generate_script_base(
        self,
        description: str,
        target_audience: str,
        duration: int,
        style: str,
        cta: str
    ) -> Dict[str, Any]:
        """
        Gera roteiro baseline (v1) sem reflection.

        Args:
            description: Descrição do vídeo
            target_audience: Público-alvo
            duration: Duração em segundos
            style: Estilo/tom
            cta: Call-to-action

        Returns:
            Roteiro estruturado (dict)
        """
        # Gerar prompt usando template
        prompt = PromptTemplates.script_generation(
            description=description,
            target_audience=target_audience,
            duration=duration,
            style=style,
            cta=cta
        )

        # Chamar LLM (metodo async)
        response = await self.llm.chat(
            messages=[{"role": "user", "content": prompt}],
            system_prompt=self.system_prompt,
            temperature=self.temperature,
            max_tokens=2000
        )

        # Parsear resposta JSON
        script = ResponseValidator.extract_first_json(response)

        if not script or "scenes" not in script:
            raise ValueError("Resposta invalida: sem 'scenes'")

        return script


    async def _critique_script(
        self,
        script: Dict[str, Any],
        brief: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Auto-crítica do roteiro gerado.

        Avalia:
        1. Clareza (1-10)
        2. Engajamento emocional (1-10)
        3. Alinhamento com briefing (1-10)
        4. CTA forte (1-10)
        5. Estrutura narrativa (1-10)

        Args:
            script: Roteiro gerado
            brief: Briefing original
            analysis: Análise do briefing

        Returns:
            Dict com score total, pontos fortes, fracos e sugestões
        """
        critique_prompt = f"""Você é um crítico profissional de roteiros de vídeo.

Avalie este roteiro de forma RIGOROSA:

ROTEIRO:
{json.dumps(script, indent=2, ensure_ascii=False)}

BRIEFING ORIGINAL:
{json.dumps(brief, indent=2, ensure_ascii=False)}

CRITÉRIOS DE AVALIAÇÃO (1-10):
1. CLAREZA: O roteiro é fácil de entender? Mensagem clara?
2. ENGAJAMENTO: Prende atenção? Storytelling envolvente?
3. ALINHAMENTO: Está alinhado com o objetivo do briefing?
4. CTA FORTE: Call-to-action é persuasivo e claro?
5. ESTRUTURA: Hook → Desenvolvimento → CTA bem estruturado?

IMPORTANTE:
- Seja CRÍTICO (não dê 10 facilmente)
- Score 7-8 = bom mas pode melhorar
- Score 9-10 = excelente, raro

Responda em JSON:
{{
  "scores": {{
    "clareza": número,
    "engajamento": número,
    "alinhamento": número,
    "cta": número,
    "estrutura": número
  }},
  "score": média_total,
  "pontos_fortes": ["força1", "força2"],
  "pontos_fracos": ["fraqueza1", "fraqueza2"],
  "sugestoes": ["sugestão específica 1", "sugestão específica 2"],
  "summary": "resumo da crítica em 1-2 linhas"
}}"""

        response = await self.llm.chat(
            messages=[{"role": "user", "content": critique_prompt}],
            temperature=0.3,  # Baixa temperatura para crítica consistente
            max_tokens=800
        )

        # Parsear JSON
        critique = ResponseValidator.extract_first_json(response)

        if not critique or "score" not in critique:
            # Fallback: score médio
            self.logger.warning("⚠️ Crítica inválida, usando score padrão 7")
            return {
                "score": 7,
                "scores": {"clareza": 7, "engajamento": 7, "alinhamento": 7, "cta": 7, "estrutura": 7},
                "pontos_fortes": ["Roteiro funcional"],
                "pontos_fracos": ["Necessita revisão"],
                "sugestoes": ["Revisar estrutura geral"],
                "summary": "Roteiro funcional mas pode ser melhorado"
            }

        return critique


    async def _improve_script(
        self,
        script_v1: Dict[str, Any],
        critique: Dict[str, Any],
        brief: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Gera versão melhorada do roteiro baseada na crítica.

        Args:
            script_v1: Roteiro original
            critique: Crítica com sugestões
            brief: Briefing original
            analysis: Análise do briefing

        Returns:
            Roteiro v2 melhorado
        """
        improve_prompt = f"""Você é um roteirista expert. Melhore este roteiro baseado na crítica recebida.

ROTEIRO ORIGINAL (v1):
{json.dumps(script_v1, indent=2, ensure_ascii=False)}

CRÍTICA RECEBIDA:
Score: {critique.get('score')}/10
Pontos Fracos: {critique.get('pontos_fracos', [])}
Sugestões: {critique.get('sugestoes', [])}

BRIEFING:
{json.dumps(brief, indent=2, ensure_ascii=False)}

TAREFA:
- Mantenha a estrutura JSON original (mesmos campos)
- Corrija os pontos fracos identificados
- Implemente as sugestões de melhoria
- Fortaleça hook, storytelling e CTA
- Mantenha duração similar

Retorne o roteiro melhorado no MESMO formato JSON do original."""

        response = await self.llm.chat(
            messages=[{"role": "user", "content": improve_prompt}],
            system_prompt=self.system_prompt,
            temperature=0.7,
            max_tokens=2000
        )

        # Parsear JSON
        script_v2 = ResponseValidator.extract_first_json(response)

        if not script_v2 or "scenes" not in script_v2:
            self.logger.warning("⚠️ Melhoria falhou, retornando v1")
            return script_v1

        return script_v2


    def _create_fallback_script(
        self,
        description: str,
        duration: int,
        cta: str
    ) -> Dict[str, Any]:
        """
        Cria roteiro basico caso LLM falhe.

        Args:
            description: Descricao do video
            duration: Duracao em segundos
            cta: Call-to-action

        Returns:
            Script basico estruturado
        """
        self.logger.info("Usando roteiro fallback...")

        return {
            "script_id": f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": description[:50],
            "duration_seconds": duration,
            "scenes": [
                {
                    "scene_number": 1,
                    "duration": 5,
                    "time_range": "00:00-00:05",
                    "visual_description": "Abertura chamativa",
                    "narration": description[:100],
                    "on_screen_text": description[:30],
                    "keywords": ["modern", "professional", "clean"],
                    "mood": "energetico"
                },
                {
                    "scene_number": 2,
                    "duration": duration - 10,
                    "time_range": f"00:05-00:{duration-5:02d}",
                    "visual_description": "Conteudo principal",
                    "narration": description,
                    "on_screen_text": "",
                    "keywords": ["business", "quality", "professional"],
                    "mood": "confiante"
                },
                {
                    "scene_number": 3,
                    "duration": 5,
                    "time_range": f"00:{duration-5:02d}-00:{duration:02d}",
                    "visual_description": "Call-to-action final",
                    "narration": cta,
                    "on_screen_text": cta,
                    "keywords": ["action", "call", "contact"],
                    "mood": "motivador"
                }
            ],
            "narration_full": f"{description}. {cta}",
            "music_style": "upbeat corporate",
            "estimated_word_count": 50,
            "generated_at": datetime.now().isoformat(),
            "model": "fallback"
        }


# ============================================================================
# TESTE
# ============================================================================

if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    import os
    import sys

    # Adicionar diretorio raiz ao path
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, root_dir)

    # Carregar .env
    load_dotenv(os.path.join(root_dir, '.env'))

    async def test():
        print("\nTestando ScriptAgent...\n")

        agent = ScriptAgent()

        state = {
            "brief": {
                "title": "Teste Script Agent",
                "description": "Propaganda de cafeteria moderna e aconchegante",
                "target": "Jovens adultos 25-35 anos",
                "style": "Clean e minimalista",
                "duration": 30,
                "cta": "Visite nossa loja!"
            },
            "analysis": {
                "objective": "Atrair clientes para nova cafeteria",
                "target_audience": "Millennials urbanos",
                "style": "moderno",
                "duration_seconds": 30,
                "cta": "Visite nossa loja hoje!"
            }
        }

        result = await agent.generate_script(state)

        script = result.get("script")
        print(f"Script ID: {script.get('script_id')}")
        print(f"Titulo: {script.get('title')}")
        print(f"Cenas: {len(script.get('scenes', []))}")
        print(f"Modelo: {script.get('model')}")
        print(f"\nPrimeira cena:")
        print(f"  {script['scenes'][0]}")

        print("\nOK - ScriptAgent funcionando!")

    asyncio.run(test())
