# OMA Video Generator - Guia Completo de Deployment Multi-Agente

## Sumário Executivo

Sistema multi-agente para geração automática de vídeos com IA, usando 5 agentes especializados orquestrados por um supervisor. Deploy em Google Cloud Run (serverless, auto-scaling).

**Custo**: ~$20/mês para 1000 vídeos (com free tier: primeiros 1500 vídeos grátis)
**Latência**: 5-6 minutos por vídeo
**Stack**: Python 3.11, FastAPI/Gradio, FFmpeg, Multi-LLM (OpenRouter)

---

## Arquitetura Multi-Agente

### 5 Agentes Especializados

1. **Supervisor Agent** (Orquestrador)
   - Model: Qwen 2.5 7B Instruct
   - Role: Coordenação, planejamento, validação
   - Pattern: Multi-Agent Orchestration

2. **Script Writer Agent**
   - Model: GPT-4o-mini
   - Role: Roteiros, copywriting, storytelling
   - Pattern: Reflection (self-critique)
   - Tempo: ~45s

3. **Visual Planner Agent**
   - Model: Qwen 2.5 7B Instruct
   - Role: Storyboard, prompts visuais, busca de mídia
   - APIs: Pexels (vídeos) + Stability AI (imagens)
   - Tempo: ~60s

4. **Audio Producer Agent**
   - Model: Mistral 7B Instruct
   - Role: Narração TTS, seleção musical
   - APIs: ElevenLabs TTS (primário) + Edge TTS (fallback)
   - Tempo: ~90s

5. **Video Editor Agent**
   - Model: Llama 3.2 3B Instruct
   - Role: Renderização FFmpeg, transições, export
   - Tempo: ~120s

### Diagrama de Fluxo

```
User Input (tema)
    ↓
Supervisor Agent (planejamento)
    ↓
Script Writer (gera roteiro) → Reflection Loop
    ↓
Visual Planner (busca mídia: Pexels + Stability AI)
    ↓
Audio Producer (gera narração: ElevenLabs/Edge TTS)
    ↓
Video Editor (render FFmpeg)
    ↓
Final Video Output
```

---

## Pré-requisitos

### 1. Contas e API Keys Necessárias

| Serviço | Tipo | Custo | Uso |
|---------|------|-------|-----|
| **OpenRouter** | Obrigatório | Pay-per-token | Acesso a GPT-4o-mini, Qwen, Mistral, Llama |
| **ElevenLabs** | Obrigatório | $5-22/mês | TTS de alta qualidade (10k chars grátis) |
| **Pexels** | Obrigatório | Grátis | Vídeos stock (sem limite) |
| **Stability AI** | Opcional | $0.02/imagem | Geração de imagens (fallback: placeholders) |
| **Google Cloud** | Obrigatório | Free tier generoso | Hosting (Cloud Run + Artifact Registry) |

### 2. Ferramentas Locais

```bash
# Git
git --version

# Docker (para testar localmente)
docker --version

# gcloud CLI
gcloud --version

# Python 3.11+ (desenvolvimento local)
python --version
```

---

## Instalação Passo a Passo

### PARTE 1: Setup do Google Cloud

#### 1.1. Criar Projeto GCP

```bash
# Criar projeto
gcloud projects create oma-video-prod --name="OMA Video Generator"

# Definir como padrão
gcloud config set project oma-video-prod

# Habilitar billing (necessário)
# https://console.cloud.google.com/billing/linkedaccount?project=oma-video-prod
```

#### 1.2. Habilitar APIs Necessárias

```bash
# Cloud Run (hosting serverless)
gcloud services enable run.googleapis.com

# Cloud Build (CI/CD)
gcloud services enable cloudbuild.googleapis.com

# Artifact Registry (Docker images)
gcloud services enable artifactregistry.googleapis.com

# Secret Manager (API keys - opcional, mas recomendado)
gcloud services enable secretmanager.googleapis.com
```

#### 1.3. Criar Artifact Registry

```bash
# Criar repositório Docker na região São Paulo
gcloud artifacts repositories create docker-repo \
    --repository-format=docker \
    --location=southamerica-east1 \
    --description="OMA Video Generator Docker Images"

# Configurar autenticação Docker
gcloud auth configure-docker southamerica-east1-docker.pkg.dev
```

#### 1.4. Configurar Service Account Permissions

```bash
# Cloud Build precisa de permissões para Cloud Run
PROJECT_NUMBER=$(gcloud projects describe oma-video-prod --format="value(projectNumber)")

gcloud projects add-iam-policy-binding oma-video-prod \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding oma-video-prod \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"
```

---

### PARTE 2: Configurar API Keys

#### 2.1. OpenRouter (Multi-LLM Gateway)

1. Criar conta: https://openrouter.ai
2. Add credits ($5 mínimo recomendado)
3. Gerar API key: https://openrouter.ai/keys
4. Salvar: `OPENROUTER_API_KEY=sk-or-v1-...`

**Models usados:**
- `openai/gpt-4o-mini-2024-07-18` (Script Writer) - $0.15/1M tokens
- `qwen/qwen-2.5-7b-instruct` (Supervisor, Visual) - $0.06/1M tokens
- `mistralai/mistral-7b-instruct-v0.3` (Audio) - $0.06/1M tokens
- `meta-llama/llama-3.2-3b-instruct` (Editor) - $0.04/1M tokens

#### 2.2. ElevenLabs TTS

1. Criar conta: https://elevenlabs.io
2. Free tier: 10,000 caracteres/mês
3. Gerar API key: Settings > API Keys
4. Salvar: `ELEVENLABS_API_KEY=sk_...`

**Voices disponíveis (português BR):**
- `XrExE9yKIg1WjnnlVkGX` - Matilda (feminina, padrão)
- `pqHfZKP75CvOlQylNhV4` - Bill (masculino)

#### 2.3. Pexels (Vídeos Stock)

1. Criar conta: https://pexels.com
2. Gerar API key: https://pexels.com/api/new
3. **100% GRÁTIS** - sem limites
4. Salvar: `PEXELS_API_KEY=...`

#### 2.4. Stability AI (Imagens - Opcional)

1. Criar conta: https://platform.stability.ai
2. Add credits ($10 mínimo)
3. Gerar API key: Account > API Keys
4. Salvar: `STABILITY_API_KEY=sk-...`

**Custo**: $0.02 por imagem 1024x1024 (SDXL)

---

### PARTE 3: Clonar e Configurar Projeto

#### 3.1. Clonar Repositório

```bash
git clone <seu-repo-url> OMA_REFACTORED
cd OMA_REFACTORED
```

#### 3.2. Estrutura do Projeto

```
OMA_REFACTORED/
├── agents/                    # 5 agentes especializados
│   ├── supervisor_agent.py   # Orquestrador principal
│   ├── script_agent.py       # Geração de roteiros
│   ├── visual_agent.py       # Planejamento visual + APIs
│   ├── audio_agent.py        # Produção de áudio TTS
│   └── editor_agent.py       # Renderização FFmpeg
├── core/                      # Infraestrutura compartilhada
│   ├── ai_client.py          # Client OpenRouter unificado
│   └── factory.py            # AIClientFactory (padrão Factory)
├── utils/                     # Utilitários
│   ├── prompts.py            # Prompt templates
│   └── paths.py              # Cross-platform path handling
├── quick_generate.py         # Orquestrador do workflow
├── app.py                    # Gradio UI
├── Dockerfile.cloudrun       # Container otimizado
├── cloudbuild.yaml           # CI/CD automático
├── requirements.txt          # Dependências Python
└── .env.example              # Template de variáveis
```

#### 3.3. Configurar Environment Variables

```bash
# Copiar template
cp .env.example .env

# Editar com suas API keys
nano .env
```

**Arquivo `.env` completo:**

```bash
# ============================================================================
# ENVIRONMENT
# ============================================================================
ENVIRONMENT=production
GRADIO_SERVER_NAME=0.0.0.0

# ============================================================================
# AI AGENTS - MODEL CONFIGURATION
# ============================================================================
# Supervisor Agent (orquestrador)
SUPERVISOR_MODEL=qwen/qwen-2.5-7b-instruct
SUPERVISOR_USE_LOCAL=false

# Script Writer Agent (roteiros)
SCRIPT_MODEL=openai/gpt-4o-mini-2024-07-18
SCRIPT_USE_LOCAL=false

# Visual Planner Agent (storyboard)
VISUAL_MODEL=qwen/qwen-2.5-7b-instruct
VISUAL_USE_LOCAL=false

# Audio Producer Agent (TTS)
AUDIO_MODEL=mistralai/mistral-7b-instruct-v0.3
AUDIO_USE_LOCAL=false

# Video Editor Agent (rendering)
EDITOR_MODEL=meta-llama/llama-3.2-3b-instruct
EDITOR_USE_LOCAL=false

# ============================================================================
# API KEYS
# ============================================================================
# OpenRouter (multi-LLM gateway)
OPENROUTER_API_KEY=sk-or-v1-...

# ElevenLabs TTS (narração primária)
ELEVENLABS_API_KEY=sk_...

# Pexels (vídeos stock - GRÁTIS)
PEXELS_API_KEY=...

# Stability AI (imagens - opcional)
STABILITY_API_KEY=sk-...
```

---

### PARTE 4: Deploy Automático no Cloud Run

#### 4.1. Configurar Cloud Build Trigger (Recomendado)

```bash
# Conectar repositório GitHub ao Cloud Build
# https://console.cloud.google.com/cloud-build/triggers

# Criar trigger automático:
# - Name: oma-video-deploy
# - Event: Push to branch
# - Branch: ^master$
# - Configuration: cloudbuild.yaml
```

**Arquivo `cloudbuild.yaml` (já configurado):**

```yaml
steps:
  # Build Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-f'
      - 'Dockerfile.cloudrun'
      - '-t'
      - 'southamerica-east1-docker.pkg.dev/${PROJECT_ID}/docker-repo/oma-api:$BUILD_ID'
      - '--no-cache'
      - '.'

  # Push to Artifact Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'southamerica-east1-docker.pkg.dev/${PROJECT_ID}/docker-repo/oma-api:$BUILD_ID']

  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'oma-video-generator'
      - '--image'
      - 'southamerica-east1-docker.pkg.dev/${PROJECT_ID}/docker-repo/oma-api:$BUILD_ID'
      - '--platform'
      - 'managed'
      - '--region'
      - 'southamerica-east1'
      - '--cpu'
      - '2'
      - '--memory'
      - '4Gi'
      - '--timeout'
      - '900'
      - '--allow-unauthenticated'
      - '--set-env-vars'
      - 'ENVIRONMENT=production,SUPERVISOR_MODEL=qwen/qwen-2.5-7b-instruct,...'
      # IMPORTANTE: Adicionar TODAS as env vars aqui (ver cloudbuild.yaml completo)

timeout: '2400s'
```

#### 4.2. Deploy Manual (Alternativa)

```bash
# Windows (ajustar Python path)
cd OMA_REFACTORED
export CLOUDSDK_PYTHON="C:/Users/paulo/AppData/Local/Programs/Python/Python313/python.exe"

# Linux/Mac
cd OMA_REFACTORED

# Deploy
gcloud builds submit \
    --config=cloudbuild.yaml \
    --substitutions="_REGION=southamerica-east1,_SERVICE_NAME=oma-video-generator,_CPU=2,_MEMORY=4Gi,_MIN_INSTANCES=0,_MAX_INSTANCES=10,_TIMEOUT=900,_CONCURRENCY=10" \
    .
```

**Tempo esperado:** 5-7 minutos

#### 4.3. Verificar Deploy

```bash
# Listar serviços
gcloud run services list --platform=managed --region=southamerica-east1

# Ver detalhes
gcloud run services describe oma-video-generator \
    --platform=managed \
    --region=southamerica-east1

# Ver logs em tempo real
gcloud run services logs tail oma-video-generator \
    --region=southamerica-east1
```

**URL do serviço:**
```
https://oma-video-generator-<hash>-rj.a.run.app
```

---

## Problemas Comuns e Soluções

### Problema 1: ElevenLabs API Error

**Erro:**
```
'ElevenLabs' object has no attribute 'generate'
```

**Causa:** API v2+ mudou método

**Solução:**
```python
# ERRADO (API v1):
audio = client.generate(text=text, voice=voice_id, model="...")

# CORRETO (API v2+):
audio = client.text_to_speech.convert(
    voice_id=voice_id,
    text=text,
    model_id="eleven_multilingual_v2"
)
```

**Arquivo:** `agents/audio_agent.py:213`

---

### Problema 2: Windows Path no Linux (CRÍTICO)

**Erro:**
```
C:/Users/paulo/.../audio/narration.mp3: Protocol not found
```

**Causa:** FFmpeg no Linux não entende `C:/Users/...`

**Solução:** Detecção de OS com `platform.system()`

```python
import platform
from pathlib import Path

if platform.system() == "Windows":
    # Desenvolvimento local
    output_dirs = [
        Path("C:/Users/paulo/OMA_Videos/audio"),
        Path("D:/OMA_Videos/audio"),
        Path("./outputs/audio")
    ]
else:
    # Production (Cloud Run = Linux)
    output_dirs = [
        Path("./outputs/audio")
    ]

# Usar primeiro que funcionar
for dir_path in output_dirs:
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
        self.output_dir = dir_path
        break
    except Exception as e:
        logger.warning(f"Failed to create {dir_path}: {e}")
```

**Arquivo:** `agents/audio_agent.py:42-75`

**⚠️ CRÍTICO:** Sem isso, áudio é gerado mas FFmpeg não consegue ler!

---

### Problema 3: Environment Variables Não Persistem

**Sintoma:** Agents inicializam sem API keys após deploy

**Causa:** Variáveis não configuradas no `cloudbuild.yaml`

**Solução:** Adicionar TODAS as vars no step de deploy

```yaml
- '--set-env-vars'
- 'ENVIRONMENT=production,
   OPENROUTER_API_KEY=sk-or-v1-...,
   ELEVENLABS_API_KEY=sk_...,
   PEXELS_API_KEY=...,
   STABILITY_API_KEY=sk-...,
   SUPERVISOR_MODEL=qwen/qwen-2.5-7b-instruct,
   SUPERVISOR_USE_LOCAL=false,
   ...'
```

**Arquivo:** `cloudbuild.yaml:69`

**⚠️ IMPORTANTE:** Para produção, migrar para Secret Manager!

---

### Problema 4: Stability AI Gera Pessoas (Conhecido)

**Sintoma:** Imagens com rostos/pessoas apesar de proteções

**Status:** CONHECIDO - Fix agendado

**Workaround temporário:**
```python
# agents/visual_agent.py:196-207
people_keywords = ['person', 'people', 'face', 'hand', 'team', 'human',
                   'man', 'woman', 'teacher', 'student', 'professor',
                   'pessoa', 'pessoas', 'rosto', 'mão', 'equipe']

if any(kw in description.lower() for kw in people_keywords):
    description = f"Abstract concept of {mood} environment, geometric shapes, no people"
```

**Fix planejado:**
- Adicionar negative prompts explícitos
- Melhorar detecção de keywords
- Fallback para Pexels em casos ambíguos

---

### Problema 5: Build Timeout

**Erro:**
```
ERROR: build step 0 timed out
```

**Causa:** Máquina muito lenta ou dependências grandes

**Solução 1:** Aumentar timeout
```yaml
# cloudbuild.yaml
timeout: '2400s'  # 40 minutos
```

**Solução 2:** Máquina mais potente
```yaml
options:
  machineType: 'E2_HIGHCPU_8'
```

**Solução 3:** Build cache (cuidado com bugs)
```yaml
# Não usar --no-cache (mais rápido mas pode ter cache stale)
args: ['build', '-t', '...', '.']
```

---

## Monitoramento e Logs

### Cloud Run Logs

```bash
# Logs em tempo real
gcloud run services logs tail oma-video-generator \
    --region=southamerica-east1 \
    --format=json

# Buscar erros específicos
gcloud logging read "resource.type=cloud_run_revision AND \
    resource.labels.service_name=oma-video-generator AND \
    severity>=ERROR" \
    --limit=50 \
    --format=json

# Filtrar por timestamp
gcloud logging read "resource.type=cloud_run_revision AND \
    timestamp>=\"2025-11-27T22:00:00Z\"" \
    --limit=100
```

### Métricas de Performance

```bash
# Via console web (recomendado):
# https://console.cloud.google.com/run/detail/southamerica-east1/oma-video-generator/metrics

# Ou via CLI:
gcloud monitoring time-series list \
    --filter='metric.type="run.googleapis.com/request_count"' \
    --format=json
```

**Métricas importantes:**
- Request latency (deve ser ~300-360s por vídeo)
- Container CPU utilization (deve ficar <80%)
- Memory utilization (deve ficar <3GB de 4GB)
- Instance count (0-10 conforme demanda)

---

## Otimizações de Custo

### 1. Aproveitar Free Tier

**Google Cloud Run Free Tier (mensal):**
- 2 milhões de requests
- 360,000 vCPU-segundos = ~1,500 vídeos grátis (6min cada)
- 180,000 GiB-segundos

**Como maximizar:**
```yaml
# Reduzir recursos quando possível
_CPU: '1'           # Ao invés de 2 (2x mais barato)
_MEMORY: '2Gi'      # Ao invés de 4Gi (2x mais barato)
_MIN_INSTANCES: '0' # Sem custo idle (aceitar cold start)
```

**Trade-off:** Geração mais lenta (8-10min ao invés de 5-6min)

### 2. Usar Edge TTS (Grátis) ao invés de ElevenLabs

```python
# Remover/comentar ELEVENLABS_API_KEY
# Sistema automaticamente usa Edge TTS (Microsoft, grátis, ilimitado)

# Qualidade: 80% do ElevenLabs, mas 100% grátis
```

### 3. Pexels-Only (Sem Stability AI)

```python
# Não configurar STABILITY_API_KEY
# Visual agent usa apenas Pexels (100% grátis, sem limite)

# Trade-off: Menos customização visual
```

### 4. Modelos Mais Baratos

```bash
# .env - trocar por modelos cheaper
SCRIPT_MODEL=meta-llama/llama-3.2-3b-instruct      # $0.04/1M (vs GPT-4o-mini $0.15/1M)
SUPERVISOR_MODEL=meta-llama/llama-3.2-3b-instruct  # $0.04/1M
```

**Economia:** ~60% nos custos de LLM
**Trade-off:** Qualidade de roteiros ~10% menor

---

## Escalonamento e Performance

### Configurações por Volume

#### Baixo Volume (<100 vídeos/dia)

```yaml
_CPU: '1'
_MEMORY: '2Gi'
_MIN_INSTANCES: '0'
_MAX_INSTANCES: '3'
_CONCURRENCY: '5'
```

**Custo:** ~$5-10/mês
**Latency:** 8-10min/vídeo
**Cold start:** ~10-15s

#### Médio Volume (100-500 vídeos/dia)

```yaml
_CPU: '2'
_MEMORY: '4Gi'
_MIN_INSTANCES: '1'   # Evitar cold start
_MAX_INSTANCES: '10'
_CONCURRENCY: '10'
```

**Custo:** ~$30-50/mês
**Latency:** 5-6min/vídeo
**Cold start:** Nenhum (always warm)

#### Alto Volume (>500 vídeos/dia)

```yaml
_CPU: '4'
_MEMORY: '8Gi'
_MIN_INSTANCES: '2'
_MAX_INSTANCES: '20'
_CONCURRENCY: '20'
```

**Custo:** ~$150-300/mês
**Latency:** 3-4min/vídeo
**Consider:** Migrar para GKE (Kubernetes) para melhor custo/benefício

---

## Migração para Outros Clouds

### AWS (Lambda + ECS Fargate)

**Vantagens:**
- 11% mais barato que Cloud Run
- Maturidade maior

**Desvantagens:**
- Configuração muito mais complexa (VPC, ALB, etc)
- Sem CI/CD integrado (precisa CodePipeline)

**Arquivos necessários:**
- `Dockerfile` (ajustar para AWS)
- `buildspec.yml` (equivalente ao cloudbuild.yaml)
- Terraform/CDK para infra

### Azure (Container Instances)

**Vantagens:**
- Mais barato (~$10/mês vs $20/mês)
- Integração com Azure DevOps

**Desvantagens:**
- Menos features de auto-scaling
- Região Brasil mais cara (usar US East)

**Arquivos necessários:**
- `azure-pipelines.yml`
- ARM templates ou Bicep

### Railway / Render (Alternativas Simples)

**Railway:**
```bash
# Install CLI
npm i -g @railway/cli

# Login
railway login

# Deploy
railway up
```

**Custo:** $5-10/mês (mais barato)
**Limitação:** Máx 8GB RAM, sem auto-scaling robusto

---

## Segurança e Boas Práticas

### 1. Migrar API Keys para Secret Manager

```bash
# Criar secrets
echo -n "sk-or-v1-..." | gcloud secrets create openrouter-api-key --data-file=-
echo -n "sk_..." | gcloud secrets create elevenlabs-api-key --data-file=-

# Dar acesso ao Cloud Run
gcloud secrets add-iam-policy-binding openrouter-api-key \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

**Atualizar cloudbuild.yaml:**
```yaml
- '--set-secrets'
- 'OPENROUTER_API_KEY=openrouter-api-key:latest,ELEVENLABS_API_KEY=elevenlabs-api-key:latest'
```

### 2. Rate Limiting

```python
# app.py - adicionar rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@limiter.limit("10/minute")
def generate_video(topic: str):
    ...
```

### 3. Input Validation

```python
# Evitar prompt injection
def sanitize_input(topic: str) -> str:
    # Remover caracteres perigosos
    topic = re.sub(r'[^\w\s\-.,!?]', '', topic)
    # Limitar tamanho
    return topic[:500]
```

### 4. Logging Estruturado

```python
import logging
import json

# Formato JSON para Cloud Logging
logging.basicConfig(
    format='{"severity": "%(levelname)s", "message": "%(message)s", "timestamp": "%(asctime)s"}',
    level=logging.INFO
)
```

---

## Checklist de Deploy

### Pré-Deploy

- [ ] API keys todas configuradas em `.env`
- [ ] Testado localmente com `python app.py`
- [ ] Requirements.txt atualizado
- [ ] Dockerfile.cloudrun otimizado
- [ ] cloudbuild.yaml com TODAS env vars
- [ ] Git commit de todas mudanças

### Deploy

- [ ] `git push origin master` (se trigger automático)
- [ ] OU `gcloud builds submit` (manual)
- [ ] Aguardar 5-7min (build + deploy)
- [ ] Verificar logs para erros

### Pós-Deploy

- [ ] Acessar URL e testar UI
- [ ] Gerar vídeo de teste (tema simples)
- [ ] Verificar logs em tempo real
- [ ] Confirmar áudio funcionando
- [ ] Confirmar vídeos/imagens carregando
- [ ] Monitorar métricas (CPU, memória, latency)

### Rollback (Se necessário)

```bash
# Listar revisions
gcloud run revisions list --service=oma-video-generator --region=southamerica-east1

# Voltar para revision anterior
gcloud run services update-traffic oma-video-generator \
    --to-revisions=oma-video-generator-00063=100 \
    --region=southamerica-east1
```

---

## Referências e Documentação

### APIs

- **OpenRouter:** https://openrouter.ai/docs
- **ElevenLabs:** https://elevenlabs.io/docs/api-reference
- **Pexels:** https://pexels.com/api/documentation
- **Stability AI:** https://platform.stability.ai/docs

### Google Cloud

- **Cloud Run:** https://cloud.google.com/run/docs
- **Cloud Build:** https://cloud.google.com/build/docs
- **Artifact Registry:** https://cloud.google.com/artifact-registry/docs
- **Secret Manager:** https://cloud.google.com/secret-manager/docs

### Patterns

- **Multi-Agent Systems:** https://arxiv.org/abs/2308.08155
- **Reflection Pattern:** https://arxiv.org/abs/2303.11366
- **LLM Orchestration:** https://github.com/langchain-ai/langgraph

---

## Suporte e Troubleshooting

### Logs Úteis

```bash
# Audio agent logs
gcloud logging read "resource.type=cloud_run_revision AND textPayload=~\"Audio\" " --limit=20

# Script agent logs
gcloud logging read "resource.type=cloud_run_revision AND textPayload=~\"Script\" " --limit=20

# Errors apenas
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" --limit=50
```

### Debug Local

```bash
# Rodar localmente (Docker)
docker build -f Dockerfile.cloudrun -t oma-local .
docker run -p 8080:8080 --env-file .env oma-local

# Testar endpoint
curl http://localhost:8080/health
```

### Contato

- **Issues GitHub:** <repo-url>/issues
- **Email:** seu-email@exemplo.com
- **Documentação completa:** Este arquivo

---

## Changelog de Deploys

### Revision 64 (2025-11-27) - STABLE ✅

- ✅ Fix: Windows path detection com `platform.system()`
- ✅ Fix: ElevenLabs v2+ API method correto
- ✅ Feature: Edge TTS fallback funcionando
- ✅ Status: Áudio + vídeo + imagens 100% funcionais

**Issues conhecidos:**
- ⚠️ Stability AI ainda gera pessoas ocasionalmente (fix agendado Monday)

### Revision 63 (2025-11-27) - FAILED

- ❌ Tentativa de fix de path (não funcionou)
- Problema: Linux `mkdir()` não falha em paths Windows

### Revision 62 (2025-11-27) - FAILED

- ✅ ElevenLabs API fix
- ❌ Windows path ainda presente

### Revision 61 (2025-11-27) - FAILED

- ❌ ElevenLabs API error: `'generate' attribute not found`
- ❌ Edge TTS error: "No audio received"

---

**Última atualização:** 2025-11-27
**Versão do guia:** 1.0
**Autor:** Paulo + Claude Code
**Licença:** MIT
