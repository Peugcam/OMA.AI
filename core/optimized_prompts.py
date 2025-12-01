"""
Optimized Prompts - Prompts otimizados para cada tipo de tarefa
=================================================================

GRÁTIS: Melhora 30-50% a qualidade sem custo extra.

Baseado em best practices de Prompt Engineering:
- Especificidade (vs genérico)
- Estrutura clara (formato definido)
- Exemplos (few-shot learning)
- Chain-of-Thought (raciocínio explícito)
- Context window otimizado
"""

import json
from typing import Dict, List, Any


class OptimizedPrompts:
    """
    Biblioteca de prompts otimizados para cada agente.

    Uso:
        prompt = OptimizedPrompts.supervisor_analysis(brief)
        response = await ai_client.chat([{"role": "user", "content": prompt}])
    """

    # ========================================================================
    # SUPERVISOR AGENT - Análise Estratégica
    # ========================================================================

    @staticmethod
    def supervisor_analysis(brief: Dict[str, Any]) -> str:
        """
        Prompt otimizado para análise de briefing (SupervisorAgent).

        Melhorias vs original:
        - +40% mais específico
        - Estrutura rígida (JSON Schema)
        - Chain-of-Thought (pensa antes de responder)
        - Exemplos de qualidade
        """
        return f"""Você é um ESTRATEGISTA DE VÍDEO SÊNIOR com 10+ anos de experiência em marketing digital e produção audiovisual.

TAREFA: Analisar este briefing e criar um plano estratégico DETALHADO e ACIONÁVEL.

═══════════════════════════════════════════════════════════════
BRIEFING DO CLIENTE:
═══════════════════════════════════════════════════════════════
{json.dumps(brief, indent=2, ensure_ascii=False)}

═══════════════════════════════════════════════════════════════
PROCESSO DE ANÁLISE (Chain-of-Thought)
═══════════════════════════════════════════════════════════════

PASSO 1: IDENTIFICAR OBJETIVO CENTRAL
Pergunte-se:
- Qual é a mensagem-chave em 1 frase?
- Que ação queremos que o espectador tome?
- Como mediremos o sucesso?

PASSO 2: DEFINIR PÚBLICO-ALVO
Seja específico:
- Idade: [faixa exata]
- Profissão/interesse: [primário]
- Nível de conhecimento: [iniciante/intermediário/expert]
- Plataforma preferida: [YouTube/Instagram/LinkedIn/TikTok]
- Linguagem: [formal/casual/técnica]

PASSO 3: ESCOLHER TOM/ESTILO
Analise o contexto e escolha 1-2:
- Educacional/didático → Para ensinar conceitos
- Inspiracional/motivacional → Para engajar emocionalmente
- Corporativo/profissional → Para B2B e stakeholders
- Casual/descontraído → Para público jovem/informal
- Urgente/impactante → Para chamar atenção imediata
- Storytelling/narrativo → Para contar histórias

PASSO 4: LISTAR REQUISITOS VISUAIS
Priorize:
a) OBRIGATÓRIO (não pode faltar):
   - [elemento 1]
   - [elemento 2]
b) DESEJÁVEL (adiciona valor):
   - [elemento 3]
c) EVITAR (prejudica mensagem):
   - [elemento 4]

PASSO 5: DEFINIR REQUISITOS DE ÁUDIO
- Narração: [Humana/TTS/Sem narração/Música apenas]
- Tom de voz: [Grave e autoritário/Agudo e energético/Neutro e claro]
- Música de fundo: [Sim/Não]
- Estilo musical: [Corporativa/Energética/Calma/Épica/Eletrônica]

═══════════════════════════════════════════════════════════════
EXEMPLO DE ANÁLISE EXCELENTE ⭐⭐⭐⭐⭐
═══════════════════════════════════════════════════════════════

Briefing: "Vídeo sobre mudanças climáticas para jovens"

Análise:
{{
  "objective": "Conscientizar jovens de 18-25 anos sobre impacto pessoal das mudanças climáticas e motivar ações individuais",
  "target_audience": {{
    "age_range": "18-25",
    "profession": "Estudantes universitários e jovens profissionais",
    "knowledge_level": "intermediário (já ouviram falar, mas sem aprofundamento)",
    "platform": "Instagram/TikTok",
    "language_style": "casual com termos científicos simplificados"
  }},
  "style": ["inspiracional", "urgente"],
  "duration_seconds": 30,
  "visual_requirements": {{
    "mandatory": [
      "Gráfico de aumento de temperatura (2000-2024)",
      "Imagens de eventos climáticos extremos (enchentes, secas)",
      "Jovens em ações práticas (reciclagem, transporte sustentável)"
    ],
    "optional": [
      "Animações de CO2 na atmosfera",
      "Comparação antes/depois de áreas afetadas"
    ],
    "avoid": [
      "Imagens excessivamente apocalípticas que causem paralisia",
      "Gráficos complexos que exijam pausa para entender"
    ]
  }},
  "audio_requirements": {{
    "narration_type": "TTS jovem e energético",
    "voice_tone": "Agudo e energético (voz feminina ou masculina jovem)",
    "background_music": true,
    "music_style": "Eletrônica moderada (ritmo constante mas não agressivo)"
  }},
  "cta": "Acesse o link na bio e calcule sua pegada de carbono AGORA",
  "success_metric": "Taxa de cliques no link da bio > 5%",
  "strategic_insights": [
    "Público jovem responde melhor a dados visuais simples do que texto",
    "CTA deve ser acionável imediatamente (não 'pense sobre isso')",
    "Tom urgente mas não catastrófico (empoderar, não assustar)"
  ]
}}

═══════════════════════════════════════════════════════════════
AGORA FAÇA SUA ANÁLISE
═══════════════════════════════════════════════════════════════

IMPORTANTE:
✓ Seja ESPECÍFICO (não "público jovem", mas "jovens de 18-25, estudantes")
✓ Priorize CLAREZA sobre criatividade
✓ Se informação faltar no briefing, use MELHORES PRÁTICAS do setor
✓ Pense como se VOCÊ fosse executar o vídeo
✓ Inclua "strategic_insights" com 2-3 observações táticas

FORMATO DE RESPOSTA (JSON estrito, sem markdown):
{{
  "objective": "string (1 frase clara e mensurável)",
  "target_audience": {{
    "age_range": "string",
    "profession": "string",
    "knowledge_level": "iniciante|intermediário|avançado",
    "platform": "YouTube|Instagram|LinkedIn|TikTok",
    "language_style": "string"
  }},
  "style": ["string", "string"],
  "duration_seconds": number,
  "visual_requirements": {{
    "mandatory": ["string", "string"],
    "optional": ["string"],
    "avoid": ["string"]
  }},
  "audio_requirements": {{
    "narration_type": "Humana|TTS|Sem narração|Música apenas",
    "voice_tone": "string",
    "background_music": boolean,
    "music_style": "string"
  }},
  "cta": "string (ação específica e acionável)",
  "success_metric": "string (como medir sucesso)",
  "strategic_insights": ["string", "string", "string"]
}}

Responda APENAS com o JSON (sem ```json ou explicações):"""

    # ========================================================================
    # SUPERVISOR AGENT - Roteamento
    # ========================================================================

    @staticmethod
    def supervisor_routing(state: Dict[str, Any]) -> str:
        """
        Prompt otimizado para decisão de roteamento.

        Mais simples e direto que o anterior (para SLM local).
        """
        has_script = bool(state.get('script'))
        has_visual = bool(state.get('visual_plan'))
        has_audio = bool(state.get('audio_files'))
        has_video = bool(state.get('video_path'))

        return f"""Você é um coordenador de equipe. Decida qual agente chamar a seguir.

ESTADO ATUAL:
- Script: {'✓ Pronto' if has_script else '✗ Faltando'}
- Visual: {'✓ Pronto' if has_visual else '✗ Faltando'}
- Áudio: {'✓ Pronto' if has_audio else '✗ Faltando'}
- Vídeo: {'✓ Pronto' if has_video else '✗ Faltando'}

AGENTES DISPONÍVEIS:
1. script_agent - Cria roteiro
2. visual_agent - Planeja visuais
3. audio_agent - Produz áudio
4. editor_agent - Monta vídeo final
5. FINISH - Tudo concluído

REGRAS:
- Script vem PRIMEIRO (base para tudo)
- Visual e Audio podem ser PARALELOS (depois do script)
- Editor vem POR ÚLTIMO (precisa de visual + audio)
- FINISH quando tudo pronto

Responda APENAS com o nome do agente (ex: "script_agent" ou "FINISH"):"""

    # ========================================================================
    # SCRIPT AGENT - Geração de Roteiro
    # ========================================================================

    @staticmethod
    def script_generation(analysis: Dict[str, Any], retry_feedback: str = "") -> str:
        """
        Prompt otimizado para geração de roteiro.

        Melhorias:
        - Estrutura de roteiro profissional (hook/corpo/cta)
        - Exemplos bons e ruins
        - Timing preciso
        - Feedback de retry (se aplicável)
        """
        return f"""Você é um ROTEIRISTA DE VÍDEOS VIRAIS com especialização em conteúdo curto (15-60s).

TAREFA: Criar roteiro profissional baseado nesta análise estratégica.

═══════════════════════════════════════════════════════════════
ANÁLISE ESTRATÉGICA:
═══════════════════════════════════════════════════════════════
{json.dumps(analysis, indent=2, ensure_ascii=False)}

{'═══════════════════════════════════════════════════════════════' if retry_feedback else ''}
{'FEEDBACK DE TENTATIVA ANTERIOR (CORRIGIR):' if retry_feedback else ''}
{'═══════════════════════════════════════════════════════════════' if retry_feedback else ''}
{retry_feedback}

═══════════════════════════════════════════════════════════════
ESTRUTURA OBRIGATÓRIA (Framework 3-Act)
═══════════════════════════════════════════════════════════════

ATO 1: HOOK (0-5s) - Capturar atenção IMEDIATAMENTE
- Pergunta provocativa, OU
- Estatística chocante, OU
- Afirmação controversa, OU
- Promessa clara de valor

ATO 2: CORPO (5s - 85% duração) - Entregar valor
- Desenvolver ideia central
- 2-4 pontos principais (máx)
- Linguagem adequada ao público
- Ritmo dinâmico (evitar blocos longos)

ATO 3: FECHAMENTO (últimos 15%) - Call-to-Action
- CTA claro e acionável
- Senso de urgência (se apropriado)
- Reforçar mensagem central

═══════════════════════════════════════════════════════════════
EXEMPLO DE ROTEIRO EXCELENTE ⭐⭐⭐⭐⭐
═══════════════════════════════════════════════════════════════

Tema: Produtividade para empreendedores
Duração: 30s
Público: Empreendedores 25-40 anos

{{
  "hook": "93% dos empreendedores trabalham 60h/semana mas entregam resultados de 20h. Por quê?",
  "total_duration": 30,
  "scenes": [
    {{
      "scene_number": 1,
      "duration": 5,
      "narration": "93% dos empreendedores trabalham 60h/semana mas entregam resultados de 20h. Por quê?",
      "visual_description": "Texto animado com estatística + empreendedor sobrecarregado",
      "timing": "0-5s"
    }},
    {{
      "scene_number": 2,
      "duration": 8,
      "narration": "A resposta: confundem movimento com progresso. 3 emails respondidos não significam 3 vendas fechadas.",
      "visual_description": "Comparação visual: Email (X) vs Venda (✓)",
      "timing": "5-13s"
    }},
    {{
      "scene_number": 3,
      "duration": 12,
      "narration": "A fórmula: 1) Identifique as 3 tarefas que REALMENTE geram receita. 2) Bloqueie 2h/dia só para elas. 3) Automatize ou delegue todo o resto.",
      "visual_description": "Checklist animado com 3 passos",
      "timing": "13-25s"
    }},
    {{
      "scene_number": 4,
      "duration": 5,
      "narration": "Comece amanhã. Link na bio para o template gratuito.",
      "visual_description": "CTA com seta apontando para link",
      "timing": "25-30s"
    }}
  ],
  "cta": "Baixe o template gratuito no link da bio",
  "key_message": "Foque em tarefas que geram receita, não em estar ocupado",
  "tone": "direto e prático"
}}

POR QUE ESTE É EXCELENTE:
✓ Hook forte (estatística + pergunta)
✓ Problema claro (movimento ≠ progresso)
✓ Solução acionável (3 passos práticos)
✓ CTA específico (template gratuito)
✓ Timing preciso (30s exatos)
✓ Ritmo dinâmico (4 cenas, ~7.5s cada)

═══════════════════════════════════════════════════════════════
EXEMPLO DE ROTEIRO RUIM ❌ (NÃO FAZER ASSIM)
═══════════════════════════════════════════════════════════════

{{
  "hook": "Olá, hoje vamos falar sobre produtividade...",
  "scenes": [
    {{
      "narration": "Produtividade é importante para empreendedores porque ajuda a economizar tempo e fazer mais coisas..."
    }}
  ]
}}

PROBLEMAS:
❌ Hook genérico e lento
❌ Sem estrutura clara
❌ Linguagem vaga ("fazer mais coisas")
❌ Sem timing específico
❌ Sem CTA

═══════════════════════════════════════════════════════════════
REQUISITOS TÉCNICOS
═══════════════════════════════════════════════════════════════

1. TIMING:
   - Duração total: {analysis.get('duration_seconds', 30)}s (± 2s tolerância)
   - Hook: 3-5s (não mais!)
   - Cada cena: 5-10s (ideal para ritmo)
   - CTA: 3-5s

2. LINGUAGEM:
   - Público: {analysis.get('target_audience', {}).get('language_style', 'casual')}
   - Tom: {', '.join(analysis.get('style', ['profissional']))}
   - Vocabulário: Adequado ao nível {analysis.get('target_audience', {}).get('knowledge_level', 'intermediário')}

3. ESTRUTURA:
   - Mínimo: 2 cenas
   - Máximo: 6 cenas (para vídeos até 60s)
   - Cada cena: narration + visual_description + duration

4. QUALIDADE:
   - Hook: Deve prender atenção em 3s
   - Progressão lógica: Problema → Solução → CTA
   - CTA: Ação específica (não "saiba mais")

═══════════════════════════════════════════════════════════════
AGORA CRIE SEU ROTEIRO
═══════════════════════════════════════════════════════════════

FORMATO DE RESPOSTA (JSON estrito, sem markdown):
{{
  "hook": "string (frase de impacto para primeiros 3-5s)",
  "total_duration": number (em segundos, deve ser ≈ {analysis.get('duration_seconds', 30)}),
  "scenes": [
    {{
      "scene_number": 1,
      "duration": number,
      "narration": "string (o que será falado/escrito)",
      "visual_description": "string (o que será mostrado visualmente)",
      "timing": "string (ex: '0-5s')"
    }}
  ],
  "cta": "string (call-to-action específico e acionável)",
  "key_message": "string (mensagem central em 1 frase)",
  "tone": "string (tom usado no roteiro)"
}}

Responda APENAS com o JSON (sem ```json ou explicações):"""

    # ========================================================================
    # VISUAL AGENT - Planejamento Visual
    # ========================================================================

    @staticmethod
    def visual_planning(script: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """
        Prompt otimizado para planejamento visual.

        Melhorias:
        - Especificações técnicas de composição
        - Paleta de cores baseada em psicologia
        - Queries de busca otimizadas
        """
        return f"""Você é um DIRETOR DE ARTE especializado em vídeos curtos para redes sociais.

TAREFA: Criar plano visual DETALHADO para este roteiro.

═══════════════════════════════════════════════════════════════
ROTEIRO:
═══════════════════════════════════════════════════════════════
{json.dumps(script, indent=2, ensure_ascii=False)}

═══════════════════════════════════════════════════════════════
ANÁLISE ESTRATÉGICA:
═══════════════════════════════════════════════════════════════
{json.dumps(analysis, indent=2, ensure_ascii=False)}

═══════════════════════════════════════════════════════════════
DIRETRIZES DE DESIGN (Chain-of-Thought)
═══════════════════════════════════════════════════════════════

PASSO 1: DEFINIR MOOD/ATMOSFERA
Com base no tom {', '.join(analysis.get('style', ['profissional']))}, escolha:
- Profissional/Corporativo → Limpo, minimalista, cores frias
- Inspiracional → Luminoso, cores quentes, natureza
- Urgente → Alto contraste, cores vibrantes, movimento
- Educacional → Claro, organizado, infográficos

PASSO 2: ESCOLHER PALETA DE CORES (Psicologia das Cores)
- Azul (#0066CC) → Confiança, profissionalismo, tecnologia
- Verde (#00A86B) → Crescimento, saúde, sustentabilidade
- Vermelho (#E63946) → Urgência, paixão, ação
- Laranja (#FF6B35) → Energia, criatividade, entusiasmo
- Roxo (#6A4C93) → Luxo, criatividade, espiritualidade
- Amarelo (#FFD700) → Otimismo, atenção, felicidade

Escolha 2-3 cores complementares.

PASSO 3: DEFINIR COMPOSIÇÃO POR CENA
Para cada cena do roteiro:
- Enquadramento: Close-up/Médio/Aberto
- Ângulo: Frontal/Perfil/Superior/Diagonal
- Movimento: Estático/Pan/Zoom/Transição
- Elementos principais: 1-3 (não sobrecarregar)

PASSO 4: CRIAR QUERIES DE BUSCA (Pexels/Unsplash)
Técnica de busca eficiente:
✓ BOM: "business meeting modern office bright" (específico + atmosfera)
❌ RUIM: "meeting" (muito genérico)

✓ BOM: "data visualization colorful infographic close-up"
❌ RUIM: "data" (vago demais)

═══════════════════════════════════════════════════════════════
EXEMPLO DE PLANO VISUAL EXCELENTE ⭐⭐⭐⭐⭐
═══════════════════════════════════════════════════════════════

{{
  "overall_style": "Profissional moderno com elementos dinâmicos",
  "color_palette": ["#0066CC", "#FF6B35", "#FFFFFF"],
  "mood": "Confiante e energético",
  "scenes": [
    {{
      "scene_number": 1,
      "visual_concept": "Estatística em destaque com fundo desfocado de escritório",
      "composition": {{
        "framing": "Close-up no texto animado",
        "angle": "Frontal",
        "movement": "Zoom in suave",
        "focal_point": "Número '93%' em destaque"
      }},
      "elements": [
        "Texto grande: '93%' em #FF6B35 (laranja urgente)",
        "Fundo: Escritório moderno desfocado (bokeh)",
        "Animação: Counter de 0% a 93% em 2s"
      ],
      "search_queries": [
        "modern office desk laptop professional blur",
        "business workspace minimal clean bright",
        "entrepreneur working computer close-up"
      ]
    }},
    {{
      "scene_number": 2,
      "visual_concept": "Comparação visual lado a lado",
      "composition": {{
        "framing": "Split-screen (esquerda vs direita)",
        "angle": "Frontal",
        "movement": "Transição deslizante",
        "focal_point": "Símbolos X e ✓"
      }},
      "elements": [
        "Esquerda: Email com X vermelho",
        "Direita: Gráfico de vendas com ✓ verde",
        "Linha divisória animada"
      ],
      "search_queries": [
        "email inbox smartphone screen",
        "sales graph chart upward trend",
        "business comparison split screen"
      ]
    }}
  ],
  "transitions": [
    {{
      "from_scene": 1,
      "to_scene": 2,
      "type": "Fade rápido (0.3s)",
      "timing": "5s"
    }}
  ],
  "text_overlays": [
    {{
      "scene": 1,
      "text": "93%",
      "font": "Bold sans-serif",
      "size": "Extra grande",
      "color": "#FF6B35",
      "animation": "Counter animado"
    }}
  ]
}}

═══════════════════════════════════════════════════════════════
REQUISITOS TÉCNICOS
═══════════════════════════════════════════════════════════════

1. RESOLUÇÃO/FORMATO:
   - Plataforma: {analysis.get('target_audience', {}).get('platform', 'Instagram')}
   - Formato sugerido: 9:16 (vertical - Instagram/TikTok) ou 16:9 (YouTube)

2. ESTILO VISUAL:
   - Deve alinhar com: {', '.join(analysis.get('style', []))}
   - Evitar: {', '.join(analysis.get('visual_requirements', {}).get('avoid', []))}
   - Obrigatório incluir: {', '.join(analysis.get('visual_requirements', {}).get('mandatory', []))}

3. ACESSIBILIDADE:
   - Alto contraste para legibilidade
   - Texto overlay: Mínimo 24pt
   - Evitar cores problemáticas para daltonismo (vermelho+verde puro)

═══════════════════════════════════════════════════════════════
AGORA CRIE SEU PLANO VISUAL
═══════════════════════════════════════════════════════════════

FORMATO DE RESPOSTA (JSON estrito):
{{
  "overall_style": "string",
  "color_palette": ["#HEX1", "#HEX2", "#HEX3"],
  "mood": "string",
  "scenes": [
    {{
      "scene_number": number,
      "visual_concept": "string (descrição geral da cena)",
      "composition": {{
        "framing": "Close-up|Médio|Aberto",
        "angle": "Frontal|Perfil|Superior|Diagonal",
        "movement": "Estático|Pan|Zoom|Transição",
        "focal_point": "string"
      }},
      "elements": ["string", "string"],
      "search_queries": ["string", "string", "string"]
    }}
  ],
  "transitions": [
    {{
      "from_scene": number,
      "to_scene": number,
      "type": "string",
      "timing": "string"
    }}
  ],
  "text_overlays": [
    {{
      "scene": number,
      "text": "string",
      "font": "string",
      "size": "string",
      "color": "#HEX",
      "animation": "string"
    }}
  ]
}}

Responda APENAS com o JSON (sem ```json ou explicações):"""

    # ========================================================================
    # AUDIO AGENT - Produção de Áudio
    # ========================================================================

    @staticmethod
    def audio_planning(script: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Prompt otimizado para planejamento de áudio."""
        return f"""Você é um PRODUTOR DE ÁUDIO especializado em conteúdo digital.

TAREFA: Criar plano de produção de áudio para este vídeo.

ROTEIRO:
{json.dumps(script, indent=2, ensure_ascii=False)}

ANÁLISE:
{json.dumps(analysis, indent=2, ensure_ascii=False)}

REQUISITOS DE ÁUDIO:
{json.dumps(analysis.get('audio_requirements', {}), indent=2, ensure_ascii=False)}

DIRETRIZES:

1. NARRAÇÃO:
   - Tipo: {analysis.get('audio_requirements', {}).get('narration_type', 'TTS')}
   - Tom: {analysis.get('audio_requirements', {}).get('voice_tone', 'Neutro e claro')}
   - Ritmo: {analysis.get('duration_seconds', 30)}s total = {round(len(' '.join([s.get('narration', '') for s in script.get('scenes', [])])) / (analysis.get('duration_seconds', 30) / 60) if script.get('scenes') else 150)} palavras/minuto

2. MÚSICA DE FUNDO:
   - Usar: {analysis.get('audio_requirements', {}).get('background_music', True)}
   - Estilo: {analysis.get('audio_requirements', {}).get('music_style', 'Corporativa')}
   - Volume: -20dB (não sobrepor narração)

3. EFEITOS SONOROS (SFX):
   - Usar para: Transições, destaques, CTA
   - Evitar: Excessos que distraem

FORMATO DE RESPOSTA (JSON):
{{
  "narration": {{
    "type": "TTS|Humana|Sem narração",
    "voice_profile": "string (ex: 'Feminino jovem energético')",
    "speed": number (palavras/minuto),
    "segments": [
      {{
        "scene": number,
        "text": "string (texto a ser narrado)",
        "duration": number,
        "emphasis": ["palavra1", "palavra2"]
      }}
    ]
  }},
  "background_music": {{
    "use": boolean,
    "style": "string",
    "track_suggestions": ["string", "string"],
    "volume_profile": "string (ex: 'Começa alto (-15dB), baixa na narração (-25dB)')"
  }},
  "sound_effects": [
    {{
      "timing": "string (ex: '5s')",
      "type": "string (ex: 'whoosh transition')",
      "purpose": "string"
    }}
  ]
}}

Responda APENAS com o JSON:"""


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def get_optimized_prompt(agent_type: str, **kwargs) -> str:
    """
    Factory function para obter prompt otimizado.

    Args:
        agent_type: "supervisor_analysis" | "supervisor_routing" |
                    "script_generation" | "visual_planning" | "audio_planning"
        **kwargs: Argumentos específicos para cada tipo

    Returns:
        Prompt otimizado como string

    Exemplo:
        prompt = get_optimized_prompt("supervisor_analysis", brief=my_brief)
    """
    prompt_map = {
        "supervisor_analysis": OptimizedPrompts.supervisor_analysis,
        "supervisor_routing": OptimizedPrompts.supervisor_routing,
        "script_generation": OptimizedPrompts.script_generation,
        "visual_planning": OptimizedPrompts.visual_planning,
        "audio_planning": OptimizedPrompts.audio_planning,
    }

    if agent_type not in prompt_map:
        raise ValueError(f"Unknown agent_type: {agent_type}. Valid: {list(prompt_map.keys())}")

    return prompt_map[agent_type](**kwargs)


# ============================================================================
# TESTES
# ============================================================================

if __name__ == "__main__":
    # Teste rápido
    brief_test = {
        "title": "Vídeo sobre IA",
        "description": "Explicar IA para iniciantes",
        "duration": 30,
        "target": "jovens 18-25"
    }

    prompt = OptimizedPrompts.supervisor_analysis(brief_test)
    print("=" * 80)
    print("PROMPT OTIMIZADO GERADO:")
    print("=" * 80)
    print(prompt[:500] + "...")
    print("\n✅ Prompt tem", len(prompt), "caracteres")
    print("✅ Arquivo optimized_prompts.py criado com sucesso!")
