# 🎬 OMA - Integração com Dashboard

## ✅ Sistema Pronto para Uso

O pipeline completo está funcionando e pronto para integrar com o dashboard.

---

## 🚀 Uso Rápido

### Opção 1: Script Completo (com briefing customizado)

```bash
python generate_full_video.py
```

Edite o briefing dentro do arquivo antes de rodar.

### Opção 2: Script Rápido (via CLI)

```bash
python quick_generate.py briefing.json
```

**Exemplo de `briefing.json`:**
```json
{
  "title": "Lançamento Produto X",
  "description": "Vídeo promocional moderno destacando inovação...",
  "duration": 30,
  "target_audience": "Empresários 30-50 anos",
  "style": "professional, modern",
  "tone": "inspirational",
  "cta": "Compre agora com 20% OFF!"
}
```

### Opção 3: Via Python (para Dashboard)

```python
import asyncio
from quick_generate import generate_video

briefing = {
    "title": "Meu Vídeo",
    "description": "...",
    "duration": 30,
    # ...
}

result = asyncio.run(generate_video(briefing))

if result["success"]:
    video_path = result["video_path"]
    cost = result["cost"]
    print(f"Vídeo gerado: {video_path}")
else:
    print(f"Erro: {result['error']}")
```

---

## 📊 Resultado

### Sucesso:

```json
{
  "success": true,
  "video_path": "C:/Users/paulo/OneDrive/Desktop/OMA_Videos/video_20251119_155652.mp4",
  "metadata": {
    "duration_seconds": 30,
    "resolution": "1280x720",
    "file_size_mb": 15.2
  },
  "cost": 0.04,
  "scenes": 5,
  "timestamp": "2025-11-19T15:57:09"
}
```

### Erro:

```json
{
  "success": false,
  "error": "Mensagem de erro detalhada",
  "timestamp": "2025-11-19T15:57:09"
}
```

---

## 💰 Custos Esperados

| Cenas | Pexels | Stability | Custo Total |
|-------|--------|-----------|-------------|
| 5 cenas | 4 | 1 | $0.04 |
| 5 cenas | 5 | 0 | $0.00 |
| 6 cenas | 5 | 1 | $0.04 |
| 10 cenas | 8 | 2 | $0.08 |

**Média: $0.04 por vídeo de 30 segundos**

---

## ⏱️ Tempo de Geração

- **Análise:** ~2-3s
- **Roteiro:** ~15-20s
- **Visual:** ~30-60s (depende de quantos vídeos baixar)
- **Áudio:** ~2-3s
- **Edição FFmpeg:** ~15-20s

**Total: 1-2 minutos por vídeo**

---

## 🔧 Para Dashboard

### Endpoint Sugerido:

```python
from fastapi import FastAPI, BackgroundTasks
from quick_generate import generate_video

app = FastAPI()

@app.post("/api/generate-video")
async def create_video(briefing: dict, background_tasks: BackgroundTasks):
    # Adicionar à fila
    task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Processar em background
    background_tasks.add_task(generate_video, briefing)

    return {
        "task_id": task_id,
        "status": "processing",
        "message": "Vídeo será gerado em 1-2 minutos"
    }

@app.get("/api/video-status/{task_id}")
async def get_status(task_id: str):
    # Verificar status
    result_file = Path(f"./outputs/result_{task_id}.json")

    if result_file.exists():
        with open(result_file) as f:
            return json.load(f)

    return {"status": "processing"}
```

---

## 📁 Estrutura de Arquivos

```
OMA_REFACTORED/
├── agents/                    # Agentes do pipeline
│   ├── supervisor_agent.py
│   ├── script_agent.py
│   ├── visual_agent.py
│   ├── audio_agent.py
│   └── editor_agent.py
├── core/                      # Utilitários
│   ├── ai_client.py          # Cliente unificado LLM
│   └── validators.py
├── .env                       # Configurações/APIs
├── generate_full_video.py    # Script completo
├── quick_generate.py          # Script rápido (para dashboard)
├── SISTEMA_FUNCIONANDO.md    # Documentação técnica
└── README_PARA_DASHBOARD.md  # Este arquivo
```

### Outputs:

```
OMA_Videos/
├── pexels_videos/            # Vídeos baixados (cache)
├── images/                   # Imagens Stability (cache)
├── audio/                    # Narrações TTS (cache)
└── video_YYYYMMDD_HHMMSS.mp4 # Vídeos finais

outputs/
├── videos/                   # Cópia dos vídeos
├── temp/                     # Arquivos temporários FFmpeg
└── result_*.json             # Metadados dos vídeos
```

---

## ⚙️ Configuração

### 1. Variáveis de Ambiente (.env)

Já configuradas e funcionando:

```bash
# APIs
OPENROUTER_API_KEY=sk-or-v1-...
PEXELS_API_KEY=Mk1ywYiG2x71...
STABILITY_API_KEY=sk-i7Mp5vGgNWq1...

# Modelos (via OpenRouter)
SUPERVISOR_MODEL=qwen/qwen-2.5-7b-instruct
SCRIPT_MODEL=openai/gpt-4o-mini-2024-07-18
VISUAL_MODEL=google/gemma-2-9b-it
AUDIO_MODEL=mistralai/mistral-7b-instruct-v0.3
EDITOR_MODEL=meta-llama/llama-3.2-3b-instruct

# Todos com USE_LOCAL=false (usando cloud)
```

### 2. Dependências Python

```bash
pip install openai requests python-dotenv httpx Pillow edge-tts
```

### 3. FFmpeg

Já instalado e funcionando.

---

## 🎯 Próximos Passos

### Para Dashboard:

1. **Criar endpoint REST API** (FastAPI/Flask)
2. **Fila de processamento** (Redis/Celery)
3. **Webhook de conclusão** (notificar quando pronto)
4. **Interface de preview** (mostrar progresso)
5. **Gerenciamento de vídeos** (listar, deletar, baixar)

### Melhorias do Sistema:

- [ ] Transições suaves entre cenas (fade in/out)
- [ ] Música de fundo automática
- [ ] Múltiplas vozes TTS
- [ ] Templates de briefing
- [ ] Preview antes de renderizar
- [ ] Legendas automáticas

---

## 🐛 Debug

### Ver logs detalhados:

Edite `.env`:
```bash
LOG_LEVEL=DEBUG
VERBOSE=true
```

### Testar componentes isolados:

```python
# Testar só o Script Agent
from agents.script_agent import ScriptAgent
state = {"brief": {...}}
result = await ScriptAgent().generate_script(state)

# Testar só o Visual Agent
from agents.visual_agent import VisualAgent
state = {"script": {...}}
result = await VisualAgent().plan_visuals(state)
```

---

## 📞 Suporte

**Arquivos importantes:**
- `SISTEMA_FUNCIONANDO.md` - Documentação técnica completa
- `test_hybrid_videos.py` - Testes automatizados
- `generate_full_video.py` - Pipeline completo
- `quick_generate.py` - API simples

**Quando voltar, podemos:**
1. Integrar com seu dashboard existente
2. Criar interface web
3. Deploy em produção (AWS/Railway/etc)
4. Adicionar features extras

---

✅ **Sistema 100% funcional e pronto para dashboard!**

**Última atualização:** 19/11/2025 16:02
