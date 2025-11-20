# Comparativo: OMA vs Dharma.AI vs CrewAI

**Análise técnica detalhada de arquiteturas multi-agente**

**Data**: 2025-11-20

---

## 📊 Executive Summary

| Sistema | Arquitetura | Modelos | Custo | Melhor Para |
|---------|-------------|---------|-------|-------------|
| **OMA** | Custom Multi-Agent | GPT-4 + DALL-E 3 | $0.18/vídeo | Video generation específico |
| **Dharma.AI** | SLM Especializado | Custom SLM | ~$0.004/call | Tarefas específicas (jurisprudência) |
| **CrewAI** | Framework Multi-Agent | GPT-4/qualquer LLM | Variável | Orquestração geral de agentes |

---

## 🏗️ Arquitetura OMA (Atual)

### Stack Tecnológico

```python
┌─────────────────────────────────────────────┐
│              OMA Architecture               │
├─────────────────────────────────────────────┤
│                                             │
│  FastAPI (REST API)                         │
│  ↓                                          │
│  ┌─────────────────────────────────────┐   │
│  │  Supervisor Agent                   │   │
│  │  - OpenAI GPT-4 Turbo              │   │
│  │  - Analisa briefing                │   │
│  │  - Define estratégia               │   │
│  └──────────────┬──────────────────────┘   │
│                 ↓                           │
│  ┌─────────────────────────────────────┐   │
│  │  Script Agent                       │   │
│  │  - OpenAI GPT-4 Turbo              │   │
│  │  - Gera roteiro                    │   │
│  │  - Define cenas e narração         │   │
│  └──────────────┬──────────────────────┘   │
│                 ↓                           │
│  ┌─────────────────────────────────────┐   │
│  │  Visual Agent                       │   │
│  │  - OpenAI DALL-E 3                 │   │
│  │  - Gera imagens (3-5 cenas)       │   │
│  │  - Otimiza prompts                 │   │
│  └──────────────┬──────────────────────┘   │
│                 ↓                           │
│  ┌─────────────────────────────────────┐   │
│  │  Audio Agent                        │   │
│  │  - OpenAI TTS-1 HD                 │   │
│  │  - Síntese de voz                  │   │
│  │  - Narração profissional           │   │
│  └──────────────┬──────────────────────┘   │
│                 ↓                           │
│  ┌─────────────────────────────────────┐   │
│  │  Editor Agent                       │   │
│  │  - FFmpeg (local)                  │   │
│  │  - Composição final                │   │
│  │  - Export MP4                      │   │
│  └──────────────┬──────────────────────┘   │
│                 ↓                           │
│  Video Output (MP4)                         │
│                                             │
└─────────────────────────────────────────────┘
```

### Características OMA

**Vantagens:**
- ✅ Especializado para geração de vídeo
- ✅ Pipeline completo end-to-end
- ✅ Controle fino de cada etapa
- ✅ Qualidade GPT-4 + DALL-E 3
- ✅ Código 100% customizável
- ✅ Sem dependências de frameworks

**Desvantagens:**
- ❌ Código acoplado
- ❌ Manutenção manual
- ❌ Escalabilidade limitada
- ❌ Sem reutilização de agentes

**Custos:**
```
Supervisor:  $0.01
Script:      $0.02
Visual (3×): $0.12
Audio:       $0.03
Editing:     $0.00 (local)
────────────────────
Total:       $0.18/vídeo
```

---

## 🧘 Dharma.AI Architecture

### Conceito: Small Language Models (SLM)

```python
┌─────────────────────────────────────────────┐
│           Dharma.AI Architecture            │
├─────────────────────────────────────────────┤
│                                             │
│  Task Input (e.g., Legal Document)          │
│  ↓                                          │
│  ┌─────────────────────────────────────┐   │
│  │  Small Specialized LM                │   │
│  │  - Modelo proprietário              │   │
│  │  - Treinado para domínio específico │   │
│  │  - 100-500M parâmetros (vs 175B)   │   │
│  │  - Fine-tuned para tarefa          │   │
│  └──────────────┬──────────────────────┘   │
│                 ↓                           │
│  ┌─────────────────────────────────────┐   │
│  │  Domain-Specific Processor           │   │
│  │  - Lógica customizada               │   │
│  │  - Regras de negócio                │   │
│  │  - Validação de saída               │   │
│  └──────────────┬──────────────────────┘   │
│                 ↓                           │
│  ┌─────────────────────────────────────┐   │
│  │  GPT-4 (Optional Fallback)           │   │
│  │  - Apenas para casos complexos      │   │
│  │  - ~5-10% dos casos                 │   │
│  └──────────────┬──────────────────────┘   │
│                 ↓                           │
│  Structured Output                          │
│                                             │
└─────────────────────────────────────────────┘
```

### Estratégia Dharma.AI

**Abordagem Híbrida:**

1. **SLM para 90% dos casos:**
   - Tarefas específicas e repetitivas
   - Classificação de documentos
   - Extração de informações estruturadas
   - Análise de padrões conhecidos

2. **GPT-4 para 10% dos casos:**
   - Casos complexos ou ambíguos
   - Novas situações não vistas
   - Raciocínio profundo necessário

**Exemplo Real (Jurisprudência BR):**

| Modelo | Acurácia | Custo (100 calls) | Latência |
|--------|----------|-------------------|----------|
| **Dharma SLM** | 86% | $0.40 | 200ms |
| **GPT-4o** | 68% | $20.00 | 2-3s |

**Economia:** 50x mais barato + melhor acurácia!

### Características Dharma.AI

**Vantagens:**
- ✅ Custo 30-50x menor que LLMs
- ✅ Latência 10x menor
- ✅ Consumo energia 30-50x menor
- ✅ Melhor acurácia em domínio específico
- ✅ 100% privado (modelo próprio)
- ✅ Sem vazamento de dados

**Desvantagens:**
- ❌ Requer treinamento customizado
- ❌ Não generaliza para outras tarefas
- ❌ Investment inicial alto (treinar modelo)
- ❌ Precisa dados suficientes (~10K+ exemplos)

**Custos:**
```
SLM Call:         $0.004
GPT-4 Fallback:   $0.02 (10% dos casos)
────────────────────────────────
Média ponderada:  $0.006/call
```

---

## 🤖 CrewAI Framework

### Arquitetura CrewAI

```python
┌─────────────────────────────────────────────┐
│            CrewAI Architecture              │
├─────────────────────────────────────────────┤
│                                             │
│  User Input / Task                          │
│  ↓                                          │
│  ┌─────────────────────────────────────┐   │
│  │  Crew (Orquestrador)                │   │
│  │  - Define workflow                  │   │
│  │  - Gerencia estado compartilhado    │   │
│  │  - Coordena agentes                 │   │
│  └──────────────┬──────────────────────┘   │
│                 ↓                           │
│  ┌──────────────────────────────────────┐  │
│  │  Agent 1: Researcher                 │  │
│  │  - Role: "Senior Researcher"         │  │
│  │  - Goal: "Find information"          │  │
│  │  - LLM: GPT-4 / Claude / Local      │  │
│  │  - Tools: [search, scrape]          │  │
│  └────────┬─────────────────────────────┘  │
│           ↓                                 │
│  ┌──────────────────────────────────────┐  │
│  │  Agent 2: Writer                     │  │
│  │  - Role: "Content Writer"            │  │
│  │  - Goal: "Create content"            │  │
│  │  - LLM: GPT-4 / Claude / Gemini     │  │
│  │  - Tools: [format, validate]        │  │
│  └────────┬─────────────────────────────┘  │
│           ↓                                 │
│  ┌──────────────────────────────────────┐  │
│  │  Agent 3: Editor                     │  │
│  │  - Role: "Senior Editor"             │  │
│  │  - Goal: "Review and improve"        │  │
│  │  - LLM: GPT-4 / Claude               │  │
│  │  - Tools: [grammar_check, style]    │  │
│  └────────┬─────────────────────────────┘  │
│           ↓                                 │
│  Task Result (Collaborative Output)         │
│                                             │
└─────────────────────────────────────────────┘
```

### Exemplo CrewAI (Video Generation)

```python
from crewai import Agent, Task, Crew

# Define Agents
supervisor = Agent(
    role='Video Strategy Director',
    goal='Analyze briefing and create video strategy',
    backstory='Expert in video marketing with 10 years experience',
    llm='gpt-4',
    verbose=True
)

scriptwriter = Agent(
    role='Senior Scriptwriter',
    goal='Write compelling video scripts',
    backstory='Award-winning scriptwriter specialized in short-form content',
    llm='gpt-4',
    verbose=True
)

visual_director = Agent(
    role='Visual Creative Director',
    goal='Design visual concepts for scenes',
    backstory='Creative director with expertise in visual storytelling',
    llm='gpt-4',
    tools=[image_generator_tool],
    verbose=True
)

# Define Tasks
analyze_task = Task(
    description='Analyze the briefing: {briefing}',
    agent=supervisor,
    expected_output='Detailed strategy document'
)

script_task = Task(
    description='Create script based on strategy',
    agent=scriptwriter,
    expected_output='Complete video script with scenes'
)

visual_task = Task(
    description='Generate visual concepts for each scene',
    agent=visual_director,
    expected_output='Visual descriptions and image prompts'
)

# Create Crew
video_crew = Crew(
    agents=[supervisor, scriptwriter, visual_director],
    tasks=[analyze_task, script_task, visual_task],
    process='sequential',  # or 'hierarchical'
    verbose=True
)

# Execute
result = video_crew.kickoff(inputs={'briefing': user_briefing})
```

### Características CrewAI

**Vantagens:**
- ✅ Framework maduro (30K+ stars GitHub)
- ✅ 1M+ downloads/mês
- ✅ Abstração de alto nível
- ✅ Suporta qualquer LLM (GPT-4, Claude, Gemini, local)
- ✅ Reutilização de agentes
- ✅ Comunidade ativa
- ✅ Documentação excelente
- ✅ Ferramentas built-in
- ✅ Workflows flexíveis (sequential, hierarchical)

**Desvantagens:**
- ❌ Overhead do framework
- ❌ Menos controle fino
- ❌ Abstração pode esconder problemas
- ❌ Dependência externa

**Custos (mesmo exemplo vídeo):**
```
Supervisor Agent (GPT-4):  $0.01
Script Agent (GPT-4):      $0.02
Visual Agent (GPT-4):      $0.01
DALL-E 3 calls (via tool): $0.12
Framework overhead:        $0.00
────────────────────────────────
Total:                     $0.16/vídeo
```

---

## 📊 Comparativo Detalhado

### 1. Arquitetura

| Aspecto | OMA | Dharma.AI | CrewAI |
|---------|-----|-----------|--------|
| **Tipo** | Custom pipeline | SLM + LLM hybrid | Framework orquestrador |
| **Flexibilidade** | ⭐⭐⭐⭐⭐ Total | ⭐⭐ Limitada | ⭐⭐⭐⭐ Alta |
| **Complexidade** | ⭐⭐⭐ Média | ⭐⭐⭐⭐⭐ Alta | ⭐⭐ Baixa |
| **Reutilização** | ⭐⭐ Baixa | ⭐ Muito baixa | ⭐⭐⭐⭐⭐ Muito alta |
| **Manutenção** | ⭐⭐⭐ Manual | ⭐⭐⭐⭐ Complexa | ⭐⭐⭐⭐⭐ Fácil |

### 2. Custos

| Volume | OMA | Dharma.AI* | CrewAI |
|--------|-----|------------|--------|
| **100 calls** | $18 | $0.60 | $16 |
| **1,000 calls** | $180 | $6 | $160 |
| **10,000 calls** | $1,800 | $60 | $1,600 |
| **100,000 calls** | $18,000 | $600 | $16,000 |

*Para tarefas específicas semelhantes a jurisprudência

### 3. Performance

| Métrica | OMA | Dharma.AI | CrewAI |
|---------|-----|-----------|--------|
| **Latência** | 15-25s | 0.2-3s | 20-30s |
| **Throughput** | 60/min | 1000+/min | 50/min |
| **Acurácia** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ (domínio) | ⭐⭐⭐⭐ |
| **Qualidade** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

### 4. Casos de Uso

**OMA (Custom):**
- ✅ Geração de vídeo completa
- ✅ Controle fino necessário
- ✅ Pipeline específico
- ✅ Integração profunda

**Dharma.AI (SLM):**
- ✅ Classificação de documentos
- ✅ Extração de informações
- ✅ Análise de jurisprudência
- ✅ Tarefas repetitivas de domínio
- ✅ Necessidade de privacidade total

**CrewAI (Framework):**
- ✅ Pesquisa + escrita + revisão
- ✅ Análise multi-perspectiva
- ✅ Workflows colaborativos
- ✅ Prototipagem rápida
- ✅ Orquestração geral

---

## 🔄 Híbrido: OMA + Dharma.AI + CrewAI

### Arquitetura Ideal Combinada

```python
┌─────────────────────────────────────────────┐
│         Hybrid Multi-Agent System           │
├─────────────────────────────────────────────┤
│                                             │
│  CrewAI (Orquestração)                      │
│  ↓                                          │
│  ┌─────────────────────────────────────┐   │
│  │  Supervisor Agent (CrewAI)          │   │
│  │  - GPT-4 para análise complexa      │   │
│  └──────────────┬──────────────────────┘   │
│                 ↓                           │
│  ┌─────────────────────────────────────┐   │
│  │  Script Agent (Dharma SLM)          │   │
│  │  - SLM para roteiros padrão         │   │
│  │  - GPT-4 fallback para criativos   │   │
│  └──────────────┬──────────────────────┘   │
│                 ↓                           │
│  ┌─────────────────────────────────────┐   │
│  │  Visual Agent (Custom)              │   │
│  │  - DALL-E 3 para imagens            │   │
│  │  - Stable Diffusion para volume     │   │
│  └──────────────┬──────────────────────┘   │
│                 ↓                           │
│  ┌─────────────────────────────────────┐   │
│  │  Audio Agent (Custom)               │   │
│  │  - TTS-1 HD OpenAI                  │   │
│  └──────────────┬──────────────────────┘   │
│                 ↓                           │
│  ┌─────────────────────────────────────┐   │
│  │  Editor Agent (Custom FFmpeg)       │   │
│  └──────────────┬──────────────────────┘   │
│                 ↓                           │
│  Video Output                               │
│                                             │
└─────────────────────────────────────────────┘
```

### Código Exemplo Híbrido

```python
from crewai import Agent, Task, Crew
from dharma_slm import DharmaSLM  # Hipotético
import openai

# SLM customizado para roteiros
dharma_script_slm = DharmaSLM(
    model='oma-script-v1',
    domain='video_scriptwriting'
)

# Wrapper para usar SLM com CrewAI
class DharmaSLMWrapper:
    def __init__(self, slm_model, fallback_llm='gpt-4'):
        self.slm = slm_model
        self.fallback = fallback_llm

    def generate(self, prompt, **kwargs):
        try:
            # Tentar SLM primeiro (barato)
            result = self.slm.generate(prompt)
            if self.slm.confidence > 0.85:
                return result
        except:
            pass

        # Fallback para GPT-4 (caro mas confiável)
        return openai.ChatCompletion.create(
            model=self.fallback,
            messages=[{"role": "user", "content": prompt}]
        )

# Criar agente híbrido
script_agent = Agent(
    role='Hybrid Scriptwriter',
    goal='Generate video scripts efficiently',
    llm=DharmaSLMWrapper(dharma_script_slm),
    backstory='Expert scriptwriter with AI assistance'
)

# Agente visual mantém custom (OMA)
visual_agent = Agent(
    role='Visual Director',
    goal='Generate scene visuals',
    llm='gpt-4',
    tools=[custom_dalle_tool],  # OMA custom
    backstory='Creative visual expert'
)

# Crew orchestração
video_crew = Crew(
    agents=[script_agent, visual_agent],
    tasks=[script_task, visual_task],
    process='sequential'
)
```

### Economia Híbrida

**Breakdown por componente:**

| Component | Solução | Custo/vídeo | Razão |
|-----------|---------|-------------|-------|
| Supervisor | GPT-4 | $0.01 | Complexidade necessária |
| Script | Dharma SLM (85%) | $0.003 | Roteiros padrão |
| Script | GPT-4 (15%) | $0.003 | Casos complexos |
| Visual | DALL-E 3 | $0.12 | Qualidade necessária |
| Audio | TTS-1 HD | $0.03 | Melhor custo/qualidade |
| Editing | FFmpeg | $0.00 | Local, gratuito |
| **Total** | **Híbrido** | **$0.166** | **-8% vs OMA** |

**Benefícios adicionais:**
- ✅ Orquestração CrewAI (manutenção)
- ✅ Economia Dharma SLM (script)
- ✅ Qualidade OMA mantida

---

## 💡 Recomendações

### Para OMA Agora

**Opção 1: Manter Custom (Recomendado)**

**Razões:**
- ✅ Controle total
- ✅ Já funciona
- ✅ Custo conhecido
- ✅ Sem dependências

**Quando migrar:** > 5,000 vídeos/mês

---

**Opção 2: Migrar para CrewAI**

**Vantagens:**
- ✅ Manutenção mais fácil
- ✅ Código mais limpo
- ✅ Reutilização de agentes
- ✅ Comunidade ativa

**Custos:**
- ⚠️ 2-3 dias de migração
- ⚠️ Possível overhead de performance
- ⚠️ Nova curva de aprendizado

**Quando migrar:** Quando equipe crescer

---

**Opção 3: Híbrido (Futuro)**

**Implementar gradualmente:**

1. **Fase 1:** Manter OMA atual
2. **Fase 2:** Treinar SLM para scripts (Dharma approach)
3. **Fase 3:** Migrar orquestração para CrewAI
4. **Fase 4:** Otimizar componentes individualmente

**Timeline:** 6-12 meses

**Economia projetada:** 30-40%

---

## 📊 Matriz de Decisão

| Cenário | Recomendação | Razão |
|---------|--------------|-------|
| **Startup MVP (< 1K/mês)** | OMA Custom | Controle + custo OK |
| **Crescimento (1K-10K/mês)** | CrewAI | Manutenção + escala |
| **High Volume (> 10K/mês)** | Híbrido SLM | Economia significativa |
| **Tarefas específicas** | Dharma SLM | 30-50x mais barato |
| **Múltiplos produtos** | CrewAI | Reutilização |

---

## 🎯 Conclusão

### TL;DR

**OMA (atual):**
- ✅ Perfeito para agora
- ✅ Controle total
- ✅ Custo aceitável
- ⚠️ Considerar CrewAI quando escalar

**Dharma.AI approach:**
- ✅ Revolucionário para tarefas específicas
- ✅ 30-50x mais barato
- ❌ Requer investment inicial
- ⚠️ Avaliar para scripts no futuro

**CrewAI:**
- ✅ Melhor para múltiplos use cases
- ✅ Manutenção mais fácil
- ✅ Comunidade ativa
- ⚠️ Considerar quando equipe crescer

### Roadmap Sugerido

```
Agora (0-6 meses):
✅ Manter OMA custom
✅ Coletar dados de scripts
✅ Monitorar padrões

Médio prazo (6-12 meses):
⚠️ Avaliar CrewAI para orquestração
⚠️ Treinar SLM para scripts (se volume justificar)
⚠️ A/B test híbrido

Longo prazo (12-24 meses):
⚠️ Full hybrid architecture
⚠️ SLM para componentes repetitivos
⚠️ GPT-4 para criatividade
```

---

**Documento atualizado:** 2025-11-20
**Próxima revisão:** Quando atingir 5,000 vídeos/mês
