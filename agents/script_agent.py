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
        Gera roteiro completo baseado no briefing.

        Args:
            state: Estado atual com briefing e analise

        Returns:
            Estado atualizado com script gerado
        """
        self.logger.info("Gerando roteiro...")

        # Extrair informacoes do briefing
        brief = state.get("brief", {})
        analysis = state.get("analysis", {})

        description = analysis.get("objective", brief.get("description", ""))
        target_audience = analysis.get("target_audience", brief.get("target", ""))
        duration = analysis.get("duration_seconds", brief.get("duration", 30))
        style = analysis.get("style", brief.get("style", "profissional"))
        cta = analysis.get("cta", brief.get("cta", ""))

        # Gerar prompt usando template
        prompt = PromptTemplates.script_generation(
            description=description,
            target_audience=target_audience,
            duration=duration,
            style=style,
            cta=cta
        )

        try:
            # Chamar LLM (metodo sincrono)
            response = self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                system_prompt=self.system_prompt,
                temperature=self.temperature,
                max_tokens=2000
            )

            # Parsear resposta JSON
            script = ResponseValidator.extract_first_json(response)

            if not script or "scenes" not in script:
                raise ValueError("Resposta invalida: sem 'scenes'")

            # Adicionar metadata
            script["generated_at"] = datetime.now().isoformat()
            script["model"] = self.llm.model

            self.logger.info(f"OK - Roteiro gerado: {len(script.get('scenes', []))} cenas")

            # Atualizar estado
            state["script"] = script
            state["current_phase"] = 1

            return state

        except Exception as e:
            self.logger.error(f"ERRO ao gerar roteiro: {e}")

            # Fallback: criar roteiro basico
            script = self._create_fallback_script(description, duration, cta)
            state["script"] = script
            state["current_phase"] = 1

            return state


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
