# Deploy OMA.AI no Google Cloud Run

Guia completo para deploy do OMA Video Generator no Google Cloud Run com FFmpeg + TTS.

## Sumário

1. [Pré-requisitos](#pré-requisitos)
2. [Configuração Inicial do GCP](#configuração-inicial-do-gcp)
3. [Deploy Manual (Primeira vez)](#deploy-manual-primeira-vez)
4. [Deploy Automatizado (CI/CD)](#deploy-automatizado-cicd)
5. [Configurar Variáveis de Ambiente](#configurar-variáveis-de-ambiente)
6. [Monitoramento e Logs](#monitoramento-e-logs)
7. [Custos Estimados](#custos-estimados)
8. [Troubleshooting](#troubleshooting)

---

## Pré-requisitos

### 1. Instalar Google Cloud SDK

**Windows (PowerShell como Admin):**
```powershell
# Baixar instalador
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:TEMP\GoogleCloudSDKInstaller.exe")

# Executar instalador
& "$env:TEMP\GoogleCloudSDKInstaller.exe"
```

**Ou baixe diretamente:** https://cloud.google.com/sdk/docs/install

### 2. Instalar Docker Desktop

Baixe em: https://www.docker.com/products/docker-desktop/

### 3. Conta Google Cloud

1. Acesse: https://console.cloud.google.com
2. Crie um novo projeto ou use existente
3. Ative o faturamento (necessário para Cloud Run)

---

## Configuração Inicial do GCP

### Passo 1: Login no GCP

```bash
# Fazer login
gcloud auth login

# Verificar conta
gcloud auth list
```

### Passo 2: Criar/Selecionar Projeto

```bash
# Criar novo projeto
gcloud projects create oma-video-prod --name="OMA Video Generator"

# OU selecionar projeto existente
gcloud config set project SEU_PROJETO_ID

# Verificar projeto atual
gcloud config get-value project
```

### Passo 3: Habilitar APIs Necessárias

```bash
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com
```

### Passo 4: Criar Repositório de Imagens

```bash
# Criar repositório no Artifact Registry
gcloud artifacts repositories create docker-repo \
    --repository-format=docker \
    --location=southamerica-east1 \
    --description="OMA Docker images"

# Configurar Docker para usar o registry
gcloud auth configure-docker southamerica-east1-docker.pkg.dev
```

---

## Deploy Manual (Primeira vez)

### Opção A: Usando Script Automatizado (Recomendado)

**Windows:**
```cmd
# Definir variáveis de ambiente
set GCP_PROJECT_ID=seu-projeto-id
set OPENROUTER_API_KEY=sk-or-v1-xxx
set PEXELS_API_KEY=xxx

# Executar script
deploy-cloudrun.bat
```

**Linux/Mac:**
```bash
# Definir variáveis
export GCP_PROJECT_ID=seu-projeto-id
export OPENROUTER_API_KEY=sk-or-v1-xxx
export PEXELS_API_KEY=xxx

# Dar permissão e executar
chmod +x deploy-cloudrun.sh
./deploy-cloudrun.sh
```

### Opção B: Comandos Manuais

```bash
# 1. Definir variáveis
PROJECT_ID="seu-projeto-id"
REGION="southamerica-east1"
SERVICE_NAME="oma-video-generator"
IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/docker-repo/oma-api:latest"

# 2. Build da imagem
docker build -f Dockerfile.cloudrun -t $IMAGE_URI --platform linux/amd64 .

# 3. Push para Artifact Registry
docker push $IMAGE_URI

# 4. Deploy no Cloud Run
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_URI \
    --platform managed \
    --region $REGION \
    --cpu 2 \
    --memory 4Gi \
    --min-instances 0 \
    --max-instances 10 \
    --timeout 900 \
    --concurrency 10 \
    --allow-unauthenticated \
    --port 8080 \
    --set-env-vars "ENVIRONMENT=production,GRADIO_SERVER_NAME=0.0.0.0"
```

---

## Deploy Automatizado (CI/CD)

### Opção 1: Cloud Build (GCP Nativo)

O arquivo `cloudbuild.yaml` já está configurado. Para ativar:

1. **Conectar Repositório:**
   ```
   Console GCP > Cloud Build > Triggers > Connect Repository
   ```

2. **Criar Trigger:**
   ```
   Console GCP > Cloud Build > Triggers > Create Trigger

   Nome: deploy-on-push
   Evento: Push to branch
   Branch: ^main$
   Arquivo: cloudbuild.yaml
   ```

3. **Configurar Secrets:**
   ```bash
   # Criar secrets para API keys
   echo -n "sk-or-v1-xxx" | gcloud secrets create openrouter-api-key --data-file=-
   echo -n "xxx" | gcloud secrets create pexels-api-key --data-file=-
   ```

### Opção 2: GitHub Actions

Crie `.github/workflows/deploy-cloudrun.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]

env:
  PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  REGION: southamerica-east1
  SERVICE_NAME: oma-video-generator

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Auth GCP
      uses: google-github-actions/auth@v2
      with:
        credentials_json: ${{ secrets.GCP_SA_KEY }}

    - name: Setup Cloud SDK
      uses: google-github-actions/setup-gcloud@v2

    - name: Configure Docker
      run: gcloud auth configure-docker ${{ env.REGION }}-docker.pkg.dev

    - name: Build and Push
      run: |
        IMAGE="${{ env.REGION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/docker-repo/oma-api:${{ github.sha }}"
        docker build -f Dockerfile.cloudrun -t $IMAGE .
        docker push $IMAGE

    - name: Deploy
      run: |
        gcloud run deploy ${{ env.SERVICE_NAME }} \
          --image ${{ env.REGION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/docker-repo/oma-api:${{ github.sha }} \
          --region ${{ env.REGION }} \
          --platform managed \
          --cpu 2 \
          --memory 4Gi \
          --allow-unauthenticated
```

---

## Configurar Variáveis de Ambiente

### Via Console (Interface Web)

1. Acesse: https://console.cloud.google.com/run
2. Clique no serviço `oma-video-generator`
3. Clique em "Edit & Deploy New Revision"
4. Na seção "Variables & Secrets", adicione:

| Variável | Valor | Obrigatório |
|----------|-------|-------------|
| `OPENROUTER_API_KEY` | sk-or-v1-xxx | Sim |
| `PEXELS_API_KEY` | xxx | Sim |
| `STABILITY_API_KEY` | xxx | Opcional |
| `ELEVENLABS_API_KEY` | xxx | Opcional |
| `ENVIRONMENT` | production | Sim |

### Via CLI

```bash
gcloud run services update oma-video-generator \
    --region southamerica-east1 \
    --set-env-vars "OPENROUTER_API_KEY=xxx,PEXELS_API_KEY=xxx"
```

### Usando Secret Manager (Mais Seguro)

```bash
# Criar secrets
echo -n "sk-or-v1-xxx" | gcloud secrets create openrouter-key --data-file=-
echo -n "xxx" | gcloud secrets create pexels-key --data-file=-

# Vincular ao Cloud Run
gcloud run services update oma-video-generator \
    --region southamerica-east1 \
    --set-secrets "OPENROUTER_API_KEY=openrouter-key:latest,PEXELS_API_KEY=pexels-key:latest"
```

---

## Monitoramento e Logs

### Ver Logs em Tempo Real

```bash
# Logs do serviço
gcloud run logs read --service oma-video-generator --region southamerica-east1

# Logs em tempo real (streaming)
gcloud run logs tail --service oma-video-generator --region southamerica-east1

# Filtrar por severidade
gcloud run logs read --service oma-video-generator --region southamerica-east1 --filter "severity>=ERROR"
```

### Console Web

- **Logs:** https://console.cloud.google.com/logs
- **Métricas:** https://console.cloud.google.com/run (clique no serviço)
- **Erros:** https://console.cloud.google.com/errors

### Métricas Importantes

| Métrica | Descrição | Alerta Sugerido |
|---------|-----------|-----------------|
| Request Latency | Tempo de resposta | > 30s |
| Container CPU | Uso de CPU | > 80% |
| Container Memory | Uso de RAM | > 80% |
| Request Count | Requisições/min | Variável |
| Error Rate | Taxa de erros | > 5% |

---

## Custos Estimados

### Por Vídeo Gerado (30s, 1080p)

| Componente | Tempo | Custo |
|------------|-------|-------|
| Cloud Run (2 vCPU, 4GB) | ~2 min | ~$0.005 |
| Network Egress | ~50MB | ~$0.006 |
| **Subtotal Infra** | | **~$0.01** |
| OpenRouter (LLMs) | 5 agentes | ~$0.26 |
| **Total por Vídeo** | | **~$0.27** |

### Custo Mensal Estimado

| Volume | Custo Cloud Run | Custo LLMs | Total |
|--------|-----------------|------------|-------|
| 100 vídeos | ~$1 | ~$26 | ~$27 |
| 500 vídeos | ~$5 | ~$130 | ~$135 |
| 1000 vídeos | ~$10 | ~$260 | ~$270 |

### Dicas para Economizar

1. **Min instances = 0:** Scale to zero quando ocioso
2. **Região São Paulo:** Menor latência, custo similar
3. **CPU allocation:** "CPU is only allocated during request processing"
4. **Concurrency alta:** Menos instâncias necessárias

---

## Troubleshooting

### Erro: Container failed to start

```bash
# Ver logs de inicialização
gcloud run logs read --service oma-video-generator --region southamerica-east1 --limit 50

# Verificar se PORT está correto (deve ser 8080)
# Aumentar timeout de startup se necessário
gcloud run services update oma-video-generator \
    --region southamerica-east1 \
    --cpu-boost
```

### Erro: Memory limit exceeded

```bash
# Aumentar memória
gcloud run services update oma-video-generator \
    --region southamerica-east1 \
    --memory 8Gi
```

### Erro: Request timeout

```bash
# Aumentar timeout (máximo 3600s = 1 hora)
gcloud run services update oma-video-generator \
    --region southamerica-east1 \
    --timeout 1800
```

### FFmpeg não encontrado

Verifique se o Dockerfile inclui:
```dockerfile
RUN apt-get update && apt-get install -y ffmpeg
```

### TTS não funciona

1. Verifique se `edge-tts` está no requirements.txt
2. Para ElevenLabs, confirme que `ELEVENLABS_API_KEY` está configurada

### Lentidão no processamento

```bash
# Aumentar CPU
gcloud run services update oma-video-generator \
    --region southamerica-east1 \
    --cpu 4

# Habilitar CPU boost (mais CPU durante startup)
gcloud run services update oma-video-generator \
    --region southamerica-east1 \
    --cpu-boost
```

---

## Comandos Úteis

```bash
# Ver URL do serviço
gcloud run services describe oma-video-generator --region southamerica-east1 --format 'value(status.url)'

# Listar revisões
gcloud run revisions list --service oma-video-generator --region southamerica-east1

# Rollback para revisão anterior
gcloud run services update-traffic oma-video-generator \
    --region southamerica-east1 \
    --to-revisions REVISION_NAME=100

# Deletar serviço
gcloud run services delete oma-video-generator --region southamerica-east1

# Ver métricas de uso
gcloud run services describe oma-video-generator --region southamerica-east1 --format yaml
```

---

## Arquivos Criados

| Arquivo | Descrição |
|---------|-----------|
| `Dockerfile.cloudrun` | Dockerfile otimizado para Cloud Run |
| `deploy-cloudrun.sh` | Script de deploy (Linux/Mac) |
| `deploy-cloudrun.bat` | Script de deploy (Windows) |
| `cloudbuild.yaml` | Configuração CI/CD do Cloud Build |
| `DEPLOY_CLOUDRUN.md` | Este guia |

---

## Suporte

- **Documentação Cloud Run:** https://cloud.google.com/run/docs
- **Pricing Calculator:** https://cloud.google.com/products/calculator
- **Status GCP:** https://status.cloud.google.com
