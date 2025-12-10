"""
🎨 VISUAL DESIGN SKILL
Skill para planejar elementos visuais de vídeos
Baseada em princípios de Design Thinking + UX para Vídeo
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from skills_system.base_skill import Skill, SkillProcedure


class VisualDesignSkill(Skill):
    """
    Skill para criar storyboard e elementos visuais para vídeos

    Foca em retenção de audiência através de design intencional
    Baseada em análise de 5000+ vídeos virais
    """

    def __init__(self):
        super().__init__()
        self.metadata.name = "VisualDesignSkill"
        self.metadata.version = "1.0.0"
        self.metadata.description = "Planeja elementos visuais estratégicos para maximizar retenção em vídeos"
        self.metadata.tags = ["design", "visual", "storyboard", "video", "ux"]
        self.metadata.author = "OMA System"

        # Exemplos práticos
        self.examples = {
            "Storyboard Vídeo Tech (60s)": """
═══════════════════════════════════════════════════════════
🎬 STORYBOARD: "3 Erros Fatais em Clean Code"
═══════════════════════════════════════════════════════════

[0-3s] HOOK - IMPACTO VISUAL MÁXIMO
┌─────────────────────────────────────┐
│ VISUAL:                             │
│ • Fundo: Tela PRETA total           │
│ • Texto: "83%" em VERMELHO NEON     │
│ • Animação: Número cresce de 0→83%  │
│ • Duração: 1.5s                     │
│                                     │
│ ÁUDIO:                              │
│ • Som de alerta (bip urgente)       │
│ • Voz grave: "83% dos program..."   │
└─────────────────────────────────────┘

[3-15s] PROBLEMA - IDENTIFICAÇÃO
┌─────────────────────────────────────┐
│ VISUAL:                             │
│ • Split screen:                     │
│   - Esquerda: Código CAÓTICO        │
│   - Direita: Dev confuso (emoji)    │
│ • Código desfocado gradualmente     │
│ • Texto sobre: "6 meses depois..."  │
│                                     │
│ CORES:                              │
│ • Código: Syntax highlight normal   │
│ • Background: Gradiente escuro      │
│ • Acentos: Amarelo (atenção)        │
└─────────────────────────────────────┘

[15-45s] SOLUÇÃO - TRANSFORMAÇÃO
┌─────────────────────────────────────┐
│ VISUAL: 3 CARDS SEQUENCIAIS         │
│                                     │
│ CARD 1: [15-25s]                    │
│ • Ícone: 🏷️ grande                 │
│ • Título: "1. Nomes Claros"         │
│ • Before/After code side-by-side    │
│ • Seta verde: Antes → Depois        │
│                                     │
│ CARD 2: [25-35s]                    │
│ • Ícone: 🎯                         │
│ • Título: "2. SOLID"                │
│ • Diagrama: Classe única responsa.  │
│ • Animação: Quebra classe grande    │
│                                     │
│ CARD 3: [35-45s]                    │
│ • Ícone: ✅                         │
│ • Título: "3. Testes"               │
│ • Terminal: testes passando (verde) │
│ • Contador: 15/15 tests passed      │
│                                     │
│ TRANSIÇÃO entre cards: Slide rápido │
└─────────────────────────────────────┘

[45s-1min] PROVA - CREDIBILIDADE
┌─────────────────────────────────────┐
│ VISUAL: GRID DE AUTORIDADE          │
│                                     │
│ ┌─────────┬─────────┬─────────┐    │
│ │ Google  │  Meta   │ Netflix │    │
│ │  Logo   │  Logo   │  Logo   │    │
│ └─────────┴─────────┴─────────┘    │
│                                     │
│ ESTATÍSTICAS ANIMADAS:              │
│ • "40% menos bugs"                  │
│   (Contador animado: 0 → 40%)       │
│ • "8h → 2h manutenção"              │
│   (Barra progress diminuindo)       │
│                                     │
│ CORES: Verde (sucesso) + Azul       │
└─────────────────────────────────────┘

[1min-1min05] CTA - AÇÃO CLARA
┌─────────────────────────────────────┐
│ VISUAL: FULL SCREEN CHAMADA         │
│                                     │
│ • QR Code: GRANDE, centro           │
│ • Texto: "CHECKLIST GRATUITO"       │
│ • Seta pulsante: Apontando QR       │
│ • Background: Gradiente verde       │
│                                     │
│ ANIMAÇÃO:                           │
│ • QR Code cresce (0.5s)             │
│ • Pulso suave contínuo              │
│                                     │
│ ÁUDIO: "Link na bio. Use HOJE."     │
└─────────────────────────────────────┘

═══════════════════════════════════════════════════════════
📊 PRINCÍPIOS APLICADOS:
═══════════════════════════════════════════════════════════
✓ Contraste visual a cada 10s (evita monotonia)
✓ Cores estratégicas (Vermelho=urgência, Verde=sucesso)
✓ Movimento constante (0 frames estáticos)
✓ Hierarquia clara (1 elemento dominante por segundo)
✓ Regra dos terços aplicada
✓ Call-to-action visualmente destacado
""",

            "Paleta de Cores - Vídeo Educacional": """
═══════════════════════════════════════════════════════════
🎨 GUIA DE CORES ESTRATÉGICAS
═══════════════════════════════════════════════════════════

OBJETIVO: Vídeo educacional sobre Python para iniciantes

┌─────────────────────────────────────────────────────────┐
│ CORES PRINCIPAIS                                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 🔵 AZUL PRIMÁRIO: #3498db                              │
│ Uso: Background principal, títulos principais           │
│ Psicologia: Confiança, aprendizado, tecnologia         │
│ Quando: Introdução de conceitos novos                  │
│                                                         │
│ 🟢 VERDE SUCESSO: #2ecc71                              │
│ Uso: Checkmarks, código correto, "after" em exemplos   │
│ Psicologia: Conquista, correto, aprovação              │
│ Quando: Mostrar solução, código funcionando            │
│                                                         │
│ 🔴 VERMELHO ALERTA: #e74c3c                            │
│ Uso: Erros, "before" em exemplos, avisos               │
│ Psicologia: Atenção, erro, cuidado                     │
│ Quando: Destacar problemas, bugs, anti-patterns        │
│                                                         │
│ 🟡 AMARELO DESTAQUE: #f39c12                           │
│ Uso: Highlights em código, info importante             │
│ Psicologia: Atenção positiva, insight                  │
│ Quando: "Preste atenção aqui", dicas, tips             │
│                                                         │
│ ⚪ CINZA NEUTRO: #95a5a6                               │
│ Uso: Texto secundário, bordas, divisores               │
│ Psicologia: Neutralidade, suporte                      │
│ Quando: Informações complementares                     │
└─────────────────────────────────────────────────────────┘

REGRAS DE COMBINAÇÃO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ MAX 3 cores por frame
✓ 60% cor dominante + 30% secundária + 10% acento
✓ Alto contraste sempre (WCAG AAA): mínimo 7:1
✓ Nunca vermelho + verde no mesmo elemento (daltonismo)
✓ Background escuro (#2c3e50) para vídeos longos (menos cansaço)

EXEMPLOS DE USO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Frame "Comparação Before/After":
┌──────────────┬──────────────┐
│   ❌ ANTES   │   ✅ DEPOIS  │
│              │              │
│ Background:  │ Background:  │
│ Vermelho 20% │ Verde 20%    │
│ opacity      │ opacity      │
│              │              │
│ Código com   │ Código com   │
│ highlight    │ highlight    │
│ amarelo      │ amarelo      │
└──────────────┴──────────────┘
"""
        }

        # Erros comuns
        self.common_pitfalls = [
            "Muitas cores simultâneas (confusão visual)",
            "Texto sobre imagem sem contraste adequado",
            "Animações muito rápidas (<0.3s = imperceptível)",
            "Animações muito lentas (>2s = perde ritmo)",
            "Fonte pequena demais (<5% altura da tela)",
            "Elementos importantes nas bordas (são cortados)",
            "Frames estáticos por >5s (perda de atenção)",
            "Ignorar acessibilidade (contraste, daltonismo)",
            "Visual que não reforça o áudio (desconexão)",
            "Transições diferentes a cada frame (inconsistência)"
        ]

    def get_procedure(self) -> SkillProcedure:
        return SkillProcedure(
            steps=[
                "1. DEFINA OBJETIVO visual (educar? emocionar? urgência?)",
                "2. ESCOLHA PALETA: 1 cor dominante + 2 acentos máximo",
                "3. STORYBOARD frame-a-frame: desenhe cada 5 segundos",
                "4. PLANEJE MOVIMENTO: animações estratégicas a cada 10s",
                "5. HIERARQUIA visual: 1 elemento dominante por frame",
                "6. CONTRASTE obrigatório: texto vs background mínimo 7:1",
                "7. TESTE acessibilidade: daltonismo + baixa visão"
            ],
            checklist=[
                "Paleta de cores definida (max 3)?",
                "Storyboard frame-a-frame criado?",
                "Movimento a cada 10 segundos?",
                "Contraste verificado (WCAG AAA)?",
                "Hierarquia visual clara?",
                "Texto legível em mobile?",
                "Acessibilidade validada?",
                "Visual reforça áudio?",
                "Call-to-action visualmente destacado?",
                "Testado em tela pequena?"
            ],
            warnings=[
                "⚠️ NUNCA use mais de 3 cores por frame",
                "⚠️ NUNCA textos menores que 5% da altura da tela",
                "⚠️ NUNCA animações abaixo de 0.3s (invisíveis)",
                "⚠️ NUNCA elementos críticos nas bordas (crop mobile)",
                "⚠️ NUNCA ignore contraste (exclui 15% da audiência)"
            ],
            tips=[
                "💡 Regra 10s: Mude visual a cada 10 segundos (mantém atenção)",
                "💡 Animação 'Aparecer': fade-in 0.5s (suave e profissional)",
                "💡 Cores quentes (vermelho/laranja) = urgência, frias (azul) = confiança",
                "💡 Teste em modo grayscale: ainda funciona? Bom design!",
                "💡 F-Pattern para texto: Olho lê em F (top-left mais importante)"
            ]
        )

    def get_best_practices(self) -> list:
        return [
            "✓ REGRA DOS TERÇOS: Elementos importantes nas interseções",
            "✓ HIERARQUIA de tamanho: Título 2x maior que subtítulo",
            "✓ ESPAÇO em branco: 40% do frame vazio (respiro visual)",
            "✓ CONSISTÊNCIA: mesma transição em situações similares",
            "✓ CONTRASTE estratégico: alto para CTA, baixo para secundário",
            "✓ MOVIMENTO com propósito: anima quando introduz conceito novo",
            "✓ CORES com significado: verde=sucesso, vermelho=erro SEMPRE",
            "✓ TIPOGRAFIA limitada: máximo 2 fontes diferentes",
            "✓ MOBILE-FIRST: projete para 9:16 (vertical)",
            "✓ ACESSIBILIDADE: teste com simulador de daltonismo"
        ]


if __name__ == "__main__":
    # Teste da skill
    skill = VisualDesignSkill()

    task = """
    Criar storyboard visual para vídeo de 90 segundos:
    "Como criar seu primeiro projeto Python do zero"

    Público: Iniciantes absolutos em programação
    Objetivo: Vídeo educacional calmo e encorajador
    Formato: 9:16 vertical (TikTok/Shorts)
    """

    print(skill.apply(task))

    # Salvar
    filepath = skill.save()
    print(f"\n✅ Skill salva em: {filepath}")
