"""
Prompt Templates - Templates Reutilizáveis para Todos os Agentes

Templates parametrizados que evitam duplicação de código
e garantem consistência nos prompts do sistema.
"""

from typing import Optional


class PromptTemplates:
    """
    Templates de prompts para todos os agentes do sistema OMA.

    Todos os métodos são estáticos e retornam strings formatadas.
    """

    # ========================================================================
    # SUPERVISOR AGENT
    # ========================================================================

    @staticmethod
    def routing_decision(state: dict) -> str:
        """
        Template para decisão de roteamento (Supervisor).

        Prompt minimalista para decisão rápida com SLM.

        Args:
            state: Estado atual do vídeo

        Returns:
            Prompt formatado
        """
        phase = state.get('current_phase', 0)
        has_script = bool(state.get('script'))
        has_visual = bool(state.get('visual_plan'))
        has_audio = bool(state.get('audio_files'))
        has_video = bool(state.get('video_path'))

        return f"""Fase: {phase}
Script: {'✓' if has_script else '✗'}
Visual: {'✓' if has_visual else '✗'}
Audio: {'✓' if has_audio else '✗'}
Video: {'✓' if has_video else '✗'}

Próximo agente (script_agent|visual_agent|audio_agent|editor_agent|FINISH):"""

    @staticmethod
    def routing_system_prompt() -> str:
        """System prompt para roteamento do Supervisor"""
        return """Você é um roteador de tarefas para criação de vídeos.

REGRAS:
1. Responda APENAS com o nome do próximo agente
2. Opções válidas: script_agent, visual_agent, audio_agent, editor_agent, FINISH
3. Não adicione explicações ou texto extra
4. Script sempre vem primeiro
5. Visual e Audio podem rodar em paralelo (após Script)
6. Editor sempre vem por último (após Visual e Audio)
7. FINISH quando Video estiver pronto

Exemplo de resposta correta: script_agent"""

    @staticmethod
    def supervisor_system_prompt() -> str:
        """System prompt completo para Supervisor Agent"""
        return """Você é o SUPERVISOR AGENT de um sistema multi-agente para criação de vídeos.

Seu papel é COORDENAR outros agentes especializados:
- Script Agent: Escreve roteiros e narrativas
- Visual Agent: Planeja storyboard e mídia visual
- Audio Agent: Produz narração e música
- Editor Agent: Monta e renderiza o vídeo final

SUAS RESPONSABILIDADES:

1. ANÁLISE: Entenda completamente a requisição do usuário
2. DECOMPOSIÇÃO: Quebre em subtarefas atômicas
3. PLANEJAMENTO: Determine ordem de execução e paralelismo
4. ROTEAMENTO: Delegue cada subtask ao agente certo
5. SÍNTESE: Combine resultados parciais de forma coerente
6. VALIDAÇÃO: Garanta qualidade antes de finalizar

REGRAS:
- Script sempre vem PRIMEIRO (outros agentes dependem dele)
- Visual e Audio podem rodar em PARALELO após script
- Editor sempre é o ÚLTIMO (precisa de todos os assets)
- Se um agente falhar, tente recovery ou delegue novamente
- Mantenha comunicação clara e objetiva com cada agente

FORMATO DE RESPOSTA:
Sempre responda em JSON estruturado com:
{
  "analysis": "análise da requisição",
  "subtasks": [lista de subtarefas],
  "execution_plan": "estratégia de execução",
  "estimated_time": segundos totais
}"""

    # ========================================================================
    # SCRIPT AGENT
    # ========================================================================

    @staticmethod
    def script_generation(
        description: str,
        target_audience: str,
        duration: int,
        style: str,
        cta: str
    ) -> str:
        """
        Template para geração de roteiro criativo.

        Args:
            description: Descrição do vídeo
            target_audience: Público-alvo
            duration: Duração em segundos
            style: Estilo visual
            cta: Call-to-action

        Returns:
            Prompt formatado
        """
        return f"""Crie um roteiro de vídeo profissional:

DESCRIÇÃO: {description}
PÚBLICO: {target_audience}
DURAÇÃO: {duration} segundos
ESTILO: {style}
CALL-TO-ACTION: {cta}

Retorne JSON com esta estrutura:
{{
  "script_id": "script_{{timestamp}}",
  "title": "Título do Vídeo",
  "duration_seconds": {duration},
  "scenes": [
    {{
      "scene_number": 1,
      "duration": 5,
      "time_range": "00:00-00:05",
      "visual_description": "Descrição visual detalhada da cena",
      "narration": "Texto da narração (se houver)",
      "on_screen_text": "Texto que aparece na tela",
      "keywords": ["keyword1", "keyword2", "keyword3"],
      "mood": "Mood/atmosfera da cena"
    }}
  ],
  "narration_full": "Narração completa concatenada",
  "music_style": "Estilo de música de fundo",
  "estimated_word_count": 20
}}

DIRETRIZES:
- Crie 4-6 cenas
- Primeira cena deve ter HOOK forte (3-5s)
- Última cena deve ter CTA claro
- Keywords em inglês para busca de vídeos stock
- Narração deve ser natural e engajante
- Mood deve guiar seleção visual"""

    @staticmethod
    def script_system_prompt() -> str:
        """System prompt para Script Agent"""
        return """Você é um roteirista profissional versátil, capaz de criar vídeos para diversos formatos e propósitos.

EXPERTISE:
- Storytelling efetivo para diferentes formatos (educacional, corporativo, promocional, social media, institucional)
- Hooks que prendem atenção adaptados ao público-alvo
- Narrativas concisas e impactantes
- CTAs persuasivos personalizados
- Adaptação de tom e estilo conforme o briefing

ESTILO:
- Adaptável ao público-alvo e objetivo do vídeo
- Linguagem apropriada ao contexto (profissional, casual, técnico, etc.)
- Ritmo ajustado à duração e formato
- Foco em benefícios e mensagem principal

IMPORTANTE: Sempre siga as diretrizes do briefing fornecido (estilo, tom, público-alvo, duração).
Sempre retorne JSON válido conforme template fornecido."""

    # ========================================================================
    # VISUAL AGENT
    # ========================================================================

    @staticmethod
    def visual_keywords(
        scene_description: str,
        mood: str,
        duration: int
    ) -> str:
        """
        Template para geração de keywords visuais.

        Args:
            scene_description: Descrição da cena
            mood: Mood/atmosfera
            duration: Duração mínima necessária

        Returns:
            Prompt formatado
        """
        return f"""Gere keywords para buscar vídeo stock:

CENA: {scene_description}
MOOD: {mood}
DURAÇÃO MÍNIMA: {duration}s

Retorne JSON:
{{
  "primary_keywords": ["keyword1", "keyword2", "keyword3"],
  "alternative_keywords": ["alt1", "alt2"],
  "required_duration": {duration},
  "suggested_effects": ["slow_motion", "fade_in"]
}}

DIRETRIZES:
- Keywords em inglês
- Específicas mas não muito nichadas
- Ordenadas por relevância
- Incluir variações para maior chance de match"""

    @staticmethod
    def visual_system_prompt() -> str:
        """System prompt para Visual Agent"""
        return """Você é um diretor visual especializado em selecionar vídeos stock.

EXPERTISE:
- Composição visual
- Stock video libraries (Pexels)
- Estética de vídeos sociais
- Keywords efetivas para busca

OBJETIVO:
- Encontrar vídeos que transmitam o mood desejado
- Garantir qualidade visual (HD+)
- Matching semântico com descrição

Retorne sempre JSON válido."""

    # ========================================================================
    # AUDIO AGENT
    # ========================================================================

    @staticmethod
    def audio_plan(
        narration_text: str,
        duration: int,
        music_style: str,
        scenes: list[dict]
    ) -> str:
        """
        Template para plano de produção de áudio.

        Args:
            narration_text: Texto completo da narração
            duration: Duração total do vídeo
            music_style: Estilo de música
            scenes: Lista de cenas (para timing)

        Returns:
            Prompt formatado
        """
        scene_count = len(scenes)

        return f"""Crie plano de produção de áudio:

NARRAÇÃO: "{narration_text}"
DURAÇÃO TOTAL: {duration}s
ESTILO MÚSICA: {music_style}
NÚMERO DE CENAS: {scene_count}

Retorne JSON:
{{
  "tts_config": {{
    "voice": "pt-BR-female",
    "speed": 1.0,
    "pitch": 1.0
  }},
  "narration_timing": [
    {{
      "start": 3,
      "end": 6,
      "text": "Texto desta parte"
    }}
  ],
  "music": {{
    "style": "{music_style}",
    "volume_db": -12,
    "fade_in_duration": 2,
    "fade_out_duration": 2
  }},
  "ducking": {{
    "enabled": true,
    "reduction_db": -18,
    "attack_ms": 100,
    "release_ms": 500
  }}
}}

DIRETRIZES:
- Timing de narração alinhado com cenas
- Música não deve competir com narração
- Ducking durante falas
- Fade in/out suaves"""

    @staticmethod
    def audio_system_prompt() -> str:
        """System prompt para Audio Agent"""
        return """Você é um produtor de áudio especializado em mixagem para vídeos.

EXPERTISE:
- Text-to-Speech (TTS)
- Mixagem de narração + música
- Ducking e compressão
- Sincronização com visual

OBJETIVO:
- Áudio claro e profissional
- Música complementar (não competitiva)
- Timing perfeito com vídeo

Retorne sempre JSON válido."""

    # ========================================================================
    # EDITOR AGENT
    # ========================================================================

    @staticmethod
    def ffmpeg_pipeline(
        scenes: list[dict],
        audio_path: str,
        duration: int,
        resolution: str = "1920x1080"
    ) -> str:
        """
        Template para geração de pipeline FFmpeg.

        Args:
            scenes: Lista de cenas com caminhos de arquivo
            audio_path: Caminho do áudio final
            duration: Duração total
            resolution: Resolução do vídeo

        Returns:
            Prompt formatado
        """
        scene_count = len(scenes)

        return f"""Gere pipeline FFmpeg para montagem de vídeo:

CENAS: {scene_count} arquivos
ÁUDIO: {audio_path}
DURAÇÃO: {duration}s
RESOLUÇÃO: {resolution}

Retorne JSON com comandos:
{{
  "step_1_concat": "ffmpeg -f concat -safe 0 -i scenes.txt -c copy temp_video.mp4",
  "step_2_text_overlay": "ffmpeg -i temp_video.mp4 -vf \\"drawtext=...\" temp_text.mp4",
  "step_3_audio_mix": "ffmpeg -i temp_text.mp4 -i {audio_path} -c:v copy -c:a aac final.mp4",
  "step_4_optimize": "ffmpeg -i final.mp4 -vcodec libx264 -preset fast -crf 23 output.mp4"
}}

DIRETRIZES:
- Todos os vídeos devem ter mesma resolução
- Transições suaves entre cenas
- Áudio em AAC 192kbps
- Vídeo em H.264 para compatibilidade
- Otimizar para web (faststart)"""

    @staticmethod
    def editor_system_prompt() -> str:
        """System prompt para Editor Agent"""
        return """Você é um editor de vídeo especializado em automação com FFmpeg.

EXPERTISE:
- Comandos FFmpeg
- Codecs e formatos
- Otimização para web
- Overlay de texto

OBJETIVO:
- Gerar comandos FFmpeg válidos e eficientes
- Garantir compatibilidade
- Otimizar tamanho sem perder qualidade

Retorne sempre JSON com comandos válidos."""

    # ========================================================================
    # VALIDAÇÃO E QUALIDADE
    # ========================================================================

    @staticmethod
    def quality_validation(
        video_path: str,
        expected_duration: int,
        scene_count: int
    ) -> str:
        """
        Template para validação de qualidade final.

        Args:
            video_path: Caminho do vídeo gerado
            expected_duration: Duração esperada
            scene_count: Número de cenas esperadas

        Returns:
            Prompt formatado
        """
        return f"""Valide a qualidade do vídeo gerado:

ARQUIVO: {video_path}
DURAÇÃO ESPERADA: {expected_duration}s
CENAS ESPERADAS: {scene_count}

Retorne JSON:
{{
  "is_valid": true,
  "issues": [],
  "quality_score": 8.5,
  "checks": {{
    "file_exists": true,
    "duration_correct": true,
    "resolution_correct": true,
    "audio_synced": true,
    "all_scenes_present": true
  }},
  "recommendations": ["Sugestão 1", "Sugestão 2"]
}}

Verifique:
- Arquivo existe e é acessível
- Duração está dentro de ±2s do esperado
- Todas as cenas foram renderizadas
- Áudio está sincronizado
- Qualidade visual aceitável"""


# ============================================================================
# HELPER: Criar prompts com contexto
# ============================================================================

class PromptBuilder:
    """
    Builder para criar prompts complexos com contexto adicional.
    """

    def __init__(self):
        self.parts = []

    def add_section(self, title: str, content: str) -> 'PromptBuilder':
        """Adiciona seção ao prompt"""
        self.parts.append(f"{title}:\n{content}\n")
        return self

    def add_instruction(self, instruction: str) -> 'PromptBuilder':
        """Adiciona instrução"""
        self.parts.append(f"• {instruction}\n")
        return self

    def add_example(self, example: str) -> 'PromptBuilder':
        """Adiciona exemplo"""
        self.parts.append(f"Exemplo:\n{example}\n")
        return self

    def build(self) -> str:
        """Constrói prompt final"""
        return "\n".join(self.parts)


# ============================================================================
# TESTES
# ============================================================================

if __name__ == "__main__":
    print("🧪 Testando PromptTemplates...\n")

    # Teste 1: Routing
    print("TESTE 1: Routing Decision")
    print("=" * 60)

    state = {
        "current_phase": 1,
        "script": {"scenes": []},
        "visual_plan": None,
        "audio_files": None,
        "video_path": None
    }

    prompt = PromptTemplates.routing_decision(state)
    print(prompt)
    print()

    # Teste 2: Script Generation
    print("TESTE 2: Script Generation")
    print("=" * 60)

    prompt = PromptTemplates.script_generation(
        description="Propaganda para cafeteria moderna",
        target_audience="Millennials urbanos",
        duration=30,
        style="Clean e minimalista",
        cta="Visite nossa loja"
    )
    print(prompt[:300] + "...\n")

    # Teste 3: Visual Keywords
    print("TESTE 3: Visual Keywords")
    print("=" * 60)

    prompt = PromptTemplates.visual_keywords(
        scene_description="Barista preparando café com latte art",
        mood="profissional",
        duration=5
    )
    print(prompt)
    print()

    # Teste 4: PromptBuilder
    print("TESTE 4: PromptBuilder")
    print("=" * 60)

    prompt = (
        PromptBuilder()
        .add_section("TAREFA", "Criar roteiro de vídeo")
        .add_instruction("Use linguagem simples")
        .add_instruction("Foque em benefícios")
        .add_example('{"title": "Exemplo"}')
        .build()
    )
    print(prompt)

    print("\n✅ Todos os testes concluídos!")
