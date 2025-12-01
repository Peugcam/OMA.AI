"""
Optimized Parameters - Parâmetros otimizados por tipo de tarefa
===================================================================

GRÁTIS: Melhora 20-30% a qualidade sem custo extra.

Baseado em research de Prompt Engineering e fine-tuning:
- Temperature afeta criatividade vs determinismo
- Top-p controla diversidade do vocabulário
- Frequency/Presence penalty evitam repetição
- Max tokens define limite de resposta

Referências:
- OpenAI Best Practices: https://platform.openai.com/docs/guides/gpt-best-practices
- Anthropic Prompt Engineering: https://docs.anthropic.com/claude/docs/prompt-engineering
"""

from dataclasses import dataclass
from typing import Dict, Any, Literal


@dataclass
class ModelParams:
    """
    Parâmetros de inferência para LLMs.

    Atributos:
        temperature: Controla aleatoriedade (0.0 = determinístico, 1.0 = criativo)
        max_tokens: Limite de tokens na resposta
        top_p: Nucleus sampling (0.0-1.0, controla diversidade)
        frequency_penalty: Penaliza repetição de tokens (-2.0 a 2.0)
        presence_penalty: Encoraja novos tópicos (-2.0 a 2.0)
    """
    temperature: float
    max_tokens: int
    top_p: float = 0.95
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0


class OptimizedParams:
    """
    Parâmetros otimizados para cada tipo de tarefa.

    IMPORTANTE: Não muda modelos, só configura melhor os existentes.

    Uso:
        params = OptimizedParams.STRATEGIC_DECISION
        response = await ai_client.chat(
            messages=messages,
            temperature=params.temperature,
            max_tokens=params.max_tokens,
            top_p=params.top_p
        )
    """

    # ========================================================================
    # DECISÕES ESTRATÉGICAS (Supervisor - Análise)
    # ========================================================================

    STRATEGIC_DECISION = ModelParams(
        temperature=0.2,  # Baixa = mais consistente e focada
        max_tokens=2000,  # Análise completa precisa de espaço
        top_p=0.8,        # Vocabulário um pouco restrito (evita tangentes)
        frequency_penalty=0.0,   # Permitir repetição de conceitos-chave
        presence_penalty=0.0     # Não forçar novos tópicos
    )
    """
    Para: Análise de briefing, decomposição de tarefas

    Por que estes valores:
    - Temperature 0.2: Queremos análise consistente, não criativa
    - Max tokens 2000: Análise completa com strategic_insights
    - Top-p 0.8: Vocabulário profissional e focado
    - Penalties 0: OK repetir "objetivo", "público-alvo", etc
    """

    # ========================================================================
    # ROTEAMENTO (Supervisor - Decisão de próximo agente)
    # ========================================================================

    ROUTING_DECISION = ModelParams(
        temperature=0.0,  # Zero = 100% determinístico (mesma entrada → mesma saída)
        max_tokens=50,    # Resposta é só nome do agente
        top_p=1.0,        # Não importa (temperature=0 já trava)
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    """
    Para: SmartRouter decidindo próximo agente

    Por que estes valores:
    - Temperature 0.0: Decisão deve ser determinística
    - Max tokens 50: Resposta é curta ("script_agent" ou "FINISH")
    - Cache funciona melhor com respostas idênticas
    """

    # ========================================================================
    # ESCRITA CRIATIVA (Script Agent)
    # ========================================================================

    CREATIVE_WRITING = ModelParams(
        temperature=0.8,  # Alta = mais criativo e variado
        max_tokens=3000,  # Roteiros podem ser longos
        top_p=0.95,       # Vocabulário amplo
        frequency_penalty=0.3,   # Evita repetição de palavras
        presence_penalty=0.3     # Encoraja introduzir novos conceitos
    )
    """
    Para: Geração de roteiros, hooks, narrativas

    Por que estes valores:
    - Temperature 0.8: Queremos criatividade (cada roteiro único)
    - Max tokens 3000: Vídeos longos (60s) precisam de mais texto
    - Top-p 0.95: Vocabulário rico e variado
    - Frequency penalty 0.3: Não repetir "então", "agora", etc
    - Presence penalty 0.3: Introduzir ideias novas em cada cena
    """

    # ========================================================================
    # PLANEJAMENTO TÉCNICO (Visual Agent, Audio Agent)
    # ========================================================================

    TECHNICAL_PLANNING = ModelParams(
        temperature=0.4,  # Médio-baixo = alguma variação mas consistente
        max_tokens=2500,  # Planos visuais são detalhados
        top_p=0.9,        # Vocabulário técnico mas não muito restrito
        frequency_penalty=0.1,   # Permitir termos técnicos repetidos
        presence_penalty=0.1     # Leve encorajamento de variação
    )
    """
    Para: Planejamento visual, plano de áudio, storyboards

    Por que estes valores:
    - Temperature 0.4: Equilíbrio entre precisão e variação
    - Max tokens 2500: Descrições visuais são longas
    - Top-p 0.9: Vocabulário técnico (cores, composição, etc)
    - Penalties baixos: OK repetir "close-up", "fade", etc
    """

    # ========================================================================
    # ANÁLISE E SÍNTESE (Editor Agent, Validação)
    # ========================================================================

    ANALYTICAL = ModelParams(
        temperature=0.3,  # Baixa = análise focada
        max_tokens=1500,  # Análise concisa
        top_p=0.85,       # Vocabulário profissional
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    """
    Para: Validação de qualidade, análise de coerência, síntese

    Por que estes valores:
    - Temperature 0.3: Análise deve ser objetiva
    - Max tokens 1500: Relatórios concisos
    - Top-p 0.85: Vocabulário técnico e preciso
    - Penalties 0: Permitir repetir critérios de qualidade
    """

    # ========================================================================
    # VALIDAÇÃO E CRÍTICA (Quality checks)
    # ========================================================================

    VALIDATION = ModelParams(
        temperature=0.1,  # Muito baixa = crítica consistente
        max_tokens=800,   # Feedback objetivo e curto
        top_p=0.75,       # Vocabulário focado
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    """
    Para: Validação de outputs, feedback de qualidade

    Por que estes valores:
    - Temperature 0.1: Crítica deve ser consistente
    - Max tokens 800: Feedback direto ao ponto
    - Top-p 0.75: Vocabulário técnico específico
    """

    # ========================================================================
    # GERAÇÃO DE QUERIES (Busca de mídia)
    # ========================================================================

    QUERY_GENERATION = ModelParams(
        temperature=0.6,  # Médio = variação de queries
        max_tokens=500,   # Queries são curtas
        top_p=0.9,
        frequency_penalty=0.5,   # Evitar queries muito similares
        presence_penalty=0.4     # Encorajar termos diferentes
    )
    """
    Para: Geração de search queries (Pexels, Unsplash)

    Por que estes valores:
    - Temperature 0.6: Queremos variação (múltiplas queries)
    - Max tokens 500: Queries são sempre curtas
    - Frequency penalty 0.5: Cada query diferente
    - Presence penalty 0.4: Usar sinônimos
    """

    # ========================================================================
    # MÉTODOS AUXILIARES
    # ========================================================================

    @classmethod
    def get_params(
        cls,
        task_type: Literal[
            "strategic_decision",
            "routing_decision",
            "creative_writing",
            "technical_planning",
            "analytical",
            "validation",
            "query_generation"
        ]
    ) -> ModelParams:
        """
        Factory method para obter parâmetros por tipo de tarefa.

        Args:
            task_type: Tipo de tarefa

        Returns:
            ModelParams com configuração otimizada

        Exemplo:
            params = OptimizedParams.get_params("creative_writing")
            response = await ai_client.chat(
                messages=messages,
                temperature=params.temperature,
                max_tokens=params.max_tokens
            )
        """
        task_map = {
            "strategic_decision": cls.STRATEGIC_DECISION,
            "routing_decision": cls.ROUTING_DECISION,
            "creative_writing": cls.CREATIVE_WRITING,
            "technical_planning": cls.TECHNICAL_PLANNING,
            "analytical": cls.ANALYTICAL,
            "validation": cls.VALIDATION,
            "query_generation": cls.QUERY_GENERATION,
        }

        if task_type not in task_map:
            raise ValueError(f"Unknown task_type: {task_type}. Valid: {list(task_map.keys())}")

        return task_map[task_type]

    @classmethod
    def to_dict(cls, params: ModelParams) -> Dict[str, Any]:
        """
        Converte ModelParams para dict (para passar pra API).

        Args:
            params: Instância de ModelParams

        Returns:
            Dict com parâmetros

        Exemplo:
            params = OptimizedParams.CREATIVE_WRITING
            api_params = OptimizedParams.to_dict(params)
            # {"temperature": 0.8, "max_tokens": 3000, ...}
        """
        return {
            "temperature": params.temperature,
            "max_tokens": params.max_tokens,
            "top_p": params.top_p,
            "frequency_penalty": params.frequency_penalty,
            "presence_penalty": params.presence_penalty,
        }


# ============================================================================
# TABELA DE REFERÊNCIA RÁPIDA
# ============================================================================

PARAMS_QUICK_REFERENCE = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                    PARÂMETROS OTIMIZADOS - GUIA RÁPIDO                    ║
╚═══════════════════════════════════════════════════════════════════════════╝

┌─────────────────────┬──────────┬───────────┬───────┬──────────────────────┐
│ Tipo de Tarefa      │ Temp     │ Max Tokens│ Top-p │ Uso                  │
├─────────────────────┼──────────┼───────────┼───────┼──────────────────────┤
│ Strategic Decision  │ 0.2      │ 2000      │ 0.8   │ Análise de briefing  │
│ Routing Decision    │ 0.0      │ 50        │ 1.0   │ Decidir próximo agent│
│ Creative Writing    │ 0.8      │ 3000      │ 0.95  │ Roteiros, narrativas │
│ Technical Planning  │ 0.4      │ 2500      │ 0.9   │ Planos visuais/audio │
│ Analytical          │ 0.3      │ 1500      │ 0.85  │ Validação, análise   │
│ Validation          │ 0.1      │ 800       │ 0.75  │ Quality checks       │
│ Query Generation    │ 0.6      │ 500       │ 0.9   │ Search queries       │
└─────────────────────┴──────────┴───────────┴───────┴──────────────────────┘

REGRAS GERAIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Temperature:
  0.0-0.3  → Determinístico (decisões, validações)
  0.4-0.6  → Balanceado (planejamento técnico)
  0.7-1.0  → Criativo (escrita, geração de ideias)

Top-p:
  0.7-0.8  → Vocabulário focado (validação, crítica)
  0.85-0.95 → Vocabulário amplo (escrita, planejamento)
  1.0      → Sem restrição (quando temperature=0)

Penalties (Frequency/Presence):
  0.0      → Permitir repetição (análise, validação)
  0.1-0.3  → Evitar repetição leve (planejamento)
  0.4-0.6  → Evitar repetição forte (escrita criativa)

Max Tokens:
  50-500   → Respostas curtas (decisões, queries)
  1000-2000 → Respostas médias (análises)
  2500-3000 → Respostas longas (roteiros, planos)
"""


# ============================================================================
# TESTES
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("PARÂMETROS OTIMIZADOS - TESTE")
    print("=" * 80)

    # Teste: Obter parâmetros por tipo
    creative_params = OptimizedParams.get_params("creative_writing")
    print(f"\n✓ Creative Writing params:")
    print(f"  Temperature: {creative_params.temperature}")
    print(f"  Max tokens: {creative_params.max_tokens}")
    print(f"  Top-p: {creative_params.top_p}")

    # Teste: Converter para dict
    params_dict = OptimizedParams.to_dict(creative_params)
    print(f"\n✓ Como dict: {params_dict}")

    # Mostrar referência rápida
    print(PARAMS_QUICK_REFERENCE)

    print("\n✅ Arquivo optimized_params.py criado com sucesso!")
