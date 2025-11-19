# 📚 Guia de Uso - Módulos Otimizados OMA v3.0

## 🎯 Visão Geral

Este guia explica como usar os novos módulos otimizados criados para reduzir custo e latência do sistema OMA.

### Módulos Criados

```
core/
├── __init__.py          # Exports principais
├── ai_client.py         # Cliente unificado LLM/SLM
├── router.py            # SmartRouter com cache
├── prompts.py           # Templates de prompts
└── validators.py        # Validação e parsing
```

---

## 🚀 Quick Start

### 1. Testar Sistema

```bash
# Inicie Ollama (para SLMs locais)
D:\OMA_Portable\start_ollama.bat

# Em outra janela, rode os testes
cd C:\Users\paulo\OneDrive\Desktop\OMA_REFACTORED
python test_optimized_supervisor.py
```

### 2. Importar Módulos

```python
# Imports principais
from core import (
    AIClient,
    AIClientFactory,
    SmartRouter,
    PromptTemplates,
    ResponseValidator
)
```

---

## 📘 Módulo 1: AIClient

### O que é?

Cliente abstrato para LLMs/SLMs (locais ou cloud). Elimina duplicação de código de chamada de API.

### Uso Básico

```python
from core import AIClient

# SLM Local (Phi3:mini via Ollama)
client = AIClient(model="phi3:mini", use_local=True)

response = client.chat(
    messages=[{"role": "user", "content": "Olá!"}],
    temperature=0.3,
    max_tokens=100
)
print(response)
```

### Uso Avançado: JSON

```python
# Automaticamente instrui modelo a retornar JSON
response_dict = client.chat_json(
    messages=[{"role": "user", "content": "Liste 3 cores"}],
    temperature=0.5
)
# {"colors": ["vermelho", "azul", "verde"]}
```

### Factory Pattern

```python
from core import AIClientFactory

# Criar cliente baseado no .env
supervisor = AIClientFactory.create_for_agent("supervisor")
script = AIClientFactory.create_for_agent("script")

# Criar todos de uma vez
clients = AIClientFactory.create_all_agents()
# {"supervisor": <AIClient>, "script": <AIClient>, ...}
```

### Estatísticas

```python
# Após uso
client.print_stats()

# Saída:
# ==========================================
# 📊 ESTATÍSTICAS - Ollama (Local)
# ==========================================
# Modelo: phi3:mini
# Total de chamadas: 10
# Tempo médio: 150ms
# Tokens totais: 5,000
# ==========================================
```

---

## 📘 Módulo 2: SmartRouter

### O que é?

Router inteligente que usa SLM local para decisões de roteamento, com cache para evitar chamadas duplicadas.

### Uso Básico

```python
from core import SmartRouter

router = SmartRouter(enable_cache=True)

# Estado do vídeo
state = {
    "current_phase": 0,
    "script": None,
    "visual_plan": None,
    "audio_files": None,
    "video_path": None
}

# Decisão de roteamento
next_agent = router.route(state)
# "script_agent"
```

### Fluxo Completo

```python
# 1. Início
state1 = {"script": None, "visual_plan": None, ...}
router.route(state1)  # "script_agent"

# 2. Script concluído
state2 = {"script": {...}, "visual_plan": None, ...}
router.route(state2)  # "visual_agent" ou "audio_agent"

# 3. Script + Visual concluídos
state3 = {"script": {...}, "visual_plan": {...}, "audio_files": None, ...}
router.route(state3)  # "audio_agent"

# 4. Tudo pronto
state4 = {"script": {...}, "visual_plan": {...}, "audio_files": {...}, "video_path": None}
router.route(state4)  # "editor_agent"

# 5. Vídeo finalizado
state5 = {..., "video_path": "./output.mp4"}
router.route(state5)  # "FINISH"
```

### Cache

```python
# Mesma decisão 2x = cache hit
router.route(state1)  # Chama SLM (200ms)
router.route(state1)  # Cache (0ms)

router.print_stats()
# Taxa de cache: 50%
# Economia: 1 chamada evitada
```

### Fallback

```python
# Se SLM falhar, usa regras determinísticas
router = SmartRouter(enable_fallback=True)

# SLM offline/erro → fallback automático
next_agent = router.route(state)  # Ainda funciona!
```

---

## 📘 Módulo 3: PromptTemplates

### O que é?

Templates parametrizados para todos os agentes. Evita duplicação de prompts e garante consistência.

### Routing

```python
from core import PromptTemplates

state = {"current_phase": 1, "script": {...}, ...}

# Prompt para decisão de roteamento
prompt = PromptTemplates.routing_decision(state)

# Saída:
# Fase: 1
# Script: ✓
# Visual: ✗
# Audio: ✗
# Video: ✗
#
# Próximo agente:
```

### Script Generation

```python
prompt = PromptTemplates.script_generation(
    description="Propaganda cafeteria moderna",
    target_audience="Millennials urbanos",
    duration=30,
    style="Clean e minimalista",
    cta="Visite nossa loja"
)

# Prompt completo com estrutura JSON esperada
```

### Visual Keywords

```python
prompt = PromptTemplates.visual_keywords(
    scene_description="Barista preparando café",
    mood="profissional",
    duration=5
)

# Retorna prompt para gerar keywords de busca
```

### Audio Plan

```python
prompt = PromptTemplates.audio_plan(
    narration_text="Cada xícara é feita com paixão...",
    duration=30,
    music_style="indie lo-fi",
    scenes=[...]
)
```

### System Prompts

```python
# Cada agente tem system prompt otimizado
system = PromptTemplates.script_system_prompt()
system = PromptTemplates.visual_system_prompt()
system = PromptTemplates.audio_system_prompt()
```

---

## 📘 Módulo 4: ResponseValidator

### O que é?

Validadores para parsing e validação de respostas de IA.

### Parse JSON

```python
from core import ResponseValidator

# JSON válido
result = ResponseValidator.parse_json('{"a": 1}')
# {"a": 1}

# JSON inválido (com default)
result = ResponseValidator.parse_json('invalid', default={})
# {}
```

### Extrair JSON de Texto

```python
# Modelo adiciona texto extra
text = 'Aqui está o resultado: {"status": "ok"} e mais texto'

result = ResponseValidator.extract_first_json(text)
# {"status": "ok"}
```

### Validar Agente

```python
# Verificar se nome de agente é válido
ResponseValidator.validate_agent_name("script_agent")  # True
ResponseValidator.validate_agent_name("invalid")       # False
```

### Limpar Nome

```python
# Limpar resposta de roteamento
clean = ResponseValidator.clean_agent_name("  visual_agent\n")
# "visual_agent"

clean = ResponseValidator.clean_agent_name("O próximo é: audio_agent")
# "audio_agent"
```

### Validar Schema

```python
data = {"a": 1, "b": 2}

valid, missing = ResponseValidator.validate_json_schema(
    data,
    required_keys=["a", "b", "c"]
)
# (False, ["c"])
```

### Validação de VideoState

```python
from core import VideoStateValidator

# Validar script
script = {"script_id": "...", "scenes": [...], "duration_seconds": 30}

valid, error = VideoStateValidator.validate_script(script)
if not valid:
    print(f"Erro: {error}")
```

---

## 🎯 Exemplo Completo: Uso Integrado

```python
from core import (
    AIClientFactory,
    SmartRouter,
    PromptTemplates,
    ResponseValidator
)

# 1. Criar clientes
clients = AIClientFactory.create_all_agents()
supervisor_client = clients["supervisor"]
script_client = clients["script"]

# 2. Criar router
router = SmartRouter(enable_cache=True)

# 3. Estado inicial
state = {
    "task_id": "video_001",
    "current_phase": 0,
    "script": None,
    "visual_plan": None,
    "audio_files": None,
    "video_path": None
}

# 4. Loop de execução
while True:
    # Decidir próximo agente
    next_agent = router.route(state)

    if next_agent == "FINISH":
        break

    print(f"Executando: {next_agent}")

    # Exemplo: Script Agent
    if next_agent == "script_agent":
        # Criar prompt
        prompt = PromptTemplates.script_generation(
            description="Propaganda cafeteria",
            target_audience="Millennials",
            duration=30,
            style="Clean",
            cta="Visite"
        )

        # Chamar modelo
        response = script_client.chat_json(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )

        # Validar
        valid, error = ResponseValidator.validate_json_schema(
            response,
            required_keys=["script_id", "scenes", "duration_seconds"]
        )

        if valid:
            state["script"] = response
            state["current_phase"] = 1
        else:
            print(f"Erro: {error}")
            break

    # ... outros agentes ...

# Estatísticas
router.print_stats()
supervisor_client.print_stats()
script_client.print_stats()
```

---

## 📊 Comparação: Antes vs Depois

### ANTES (código duplicado)

```python
# Em cada agente, repetir:
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

response = client.chat.completions.create(
    model="qwen/qwen-2.5-7b-instruct",
    messages=[{"role": "user", "content": "..."}],
    temperature=0.7
)

result = response.choices[0].message.content

# Parse JSON manualmente
try:
    data = json.loads(result)
except:
    # Tratar erro...
```

**Problemas:**
- ❌ Código duplicado em 5 agentes
- ❌ Sem abstração
- ❌ Difícil trocar modelos
- ❌ Sem estatísticas
- ❌ Sem cache

### DEPOIS (com módulos otimizados)

```python
from core import AIClient, ResponseValidator

client = AIClient(model="phi3:mini", use_local=True)

data = client.chat_json(
    messages=[{"role": "user", "content": "..."}],
    temperature=0.7
)

# JSON já parseado, validado, com stats!
client.print_stats()
```

**Benefícios:**
- ✅ Zero duplicação
- ✅ Abstração limpa
- ✅ Trocar modelo = mudar 1 linha
- ✅ Estatísticas automáticas
- ✅ JSON automático

---

## 🎯 Próximos Passos

1. ✅ **Teste os módulos**
   ```bash
   python test_optimized_supervisor.py
   ```

2. ✅ **Integre no Supervisor**
   - Ver: `agents/supervisor_agent.py`
   - Substituir código antigo por novos módulos

3. ✅ **Adapte outros agentes**
   - Script Agent → usar `AIClient` + `PromptTemplates`
   - Visual Agent → usar `AIClient` + `ResponseValidator`
   - Audio Agent → usar `AIClient` + `PromptTemplates`
   - Editor Agent → usar `AIClient` + `PromptTemplates`

4. ✅ **Monitore resultados**
   - Comparar tempo de execução
   - Comparar custos
   - Ajustar temperaturas/prompts

---

## 🐛 Troubleshooting

### Erro: "Module 'core' not found"

```bash
# Certifique-se de estar na pasta raiz do projeto
cd C:\Users\paulo\OneDrive\Desktop\OMA_REFACTORED

# Ou adicione ao PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/caminho/para/OMA_REFACTORED"
```

### Erro: "Ollama not found"

```bash
# Inicie Ollama
D:\OMA_Portable\start_ollama.bat

# Verifique se está rodando
curl http://localhost:11434/api/version
```

### Erro: "OPENROUTER_API_KEY not set"

```bash
# Verifique .env
cat .env | grep OPENROUTER_API_KEY

# Deve ter:
# OPENROUTER_API_KEY=sk-or-v1-sua-chave-aqui
```

### Router sempre usa fallback

- Verifique se Ollama está rodando
- Verifique se modelo phi3:mini está instalado: `ollama list`
- Teste manualmente: `ollama run phi3:mini "Olá"`

---

## 📚 Documentação Adicional

- **Estratégia Completa**: `ESTRATEGIA_HIBRIDA_OTIMIZADA.md`
- **Alternância de Modelos**: `COMO_ALTERNAR_MODELOS.md`
- **Configuração**: `.env` (comentários inline)

---

**Criado em:** 18/11/2025
**Versão:** 3.0.0
**Status:** ✅ Pronto para uso!
