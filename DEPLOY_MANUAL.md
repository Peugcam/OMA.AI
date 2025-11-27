# 🚀 Deploy Manual - Passo a Passo

Execute estes comandos na ordem para fazer o deploy no Google Cloud Run.

---

## 📋 PASSO 1: Verificar Instalação do gcloud

Abra um **novo terminal** e execute:

```bash
gcloud --version
```

**Resultado esperado:**
```
Google Cloud SDK 4XX.X.X
```

Se der erro de Python:
1. Reinstale o gcloud SDK: https://cloud.google.com/sdk/docs/install
2. Ou use o Google Cloud Shell (navegador): https://shell.cloud.google.com

---

## 🔐 PASSO 2: Autenticar no Google Cloud

```bash
gcloud auth login
```

Isso abrirá seu navegador para fazer login na sua conta Google.

---

## 📁 PASSO 3: Definir Configurações

### 3.1. Listar seus projetos
```bash
gcloud projects list
```

### 3.2. Definir seu PROJECT_ID
**⚠️ IMPORTANTE: Substitua SEU-PROJECT-ID pelo ID real do seu projeto!**

```bash
# Exemplo: se seu projeto é "oma-video-prod-2024"
export PROJECT_ID="SEU-PROJECT-ID"
gcloud config set project $PROJECT_ID
```

### 3.3. Definir região
```bash
export REGION="southamerica-east1"  # São Paulo
```

### 3.4. Definir nome do serviço
```bash
export SERVICE_NAME="oma-video-generator"
```

---

## 🔑 PASSO 4: Configurar OpenAI API Key

**⚠️ IMPORTANTE: Substitua pela sua chave real da OpenAI!**

```bash
export OPENAI_API_KEY="sk-..."
```

Verifique se está definida:
```bash
echo $OPENAI_API_KEY
```

---

## 🔌 PASSO 5: Habilitar APIs Necessárias

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

**Aguarde**: Pode levar 1-2 minutos.

---

## 📦 PASSO 6: Criar Artifact Registry

```bash
gcloud artifacts repositories create docker-repo \
    --repository-format=docker \
    --location=$REGION \
    --description="OMA Docker Images"
```

Se já existir, você verá uma mensagem dizendo isso. Tudo bem!

---

## 🏗️ PASSO 7: Navegar até o diretório do projeto

```bash
cd C:\Users\paulo\OneDrive\Desktop\OMA_REFACTORED
```

Ou no Git Bash/Linux:
```bash
cd /mnt/c/Users/paulo/OneDrive/Desktop/OMA_REFACTORED
```

---

## 🔨 PASSO 8: Build & Push da Imagem Docker

Este passo pode demorar **10-15 minutos** na primeira vez.

```bash
gcloud builds submit \
    --tag="$REGION-docker.pkg.dev/$PROJECT_ID/docker-repo/oma-api:latest" \
    --timeout=30m \
    --machine-type=e2-highcpu-8 \
    --dockerfile=Dockerfile.cloudrun \
    .
```

**Acompanhe o progresso**: Você verá logs em tempo real do build.

**Possíveis erros:**
- `Permission denied`: Execute `gcloud auth application-default login`
- `Timeout`: Aumente para `--timeout=60m`

---

## 🚀 PASSO 9: Deploy no Cloud Run

```bash
gcloud run deploy $SERVICE_NAME \
    --image="$REGION-docker.pkg.dev/$PROJECT_ID/docker-repo/oma-api:latest" \
    --platform=managed \
    --region=$REGION \
    --cpu=2 \
    --memory=4Gi \
    --min-instances=0 \
    --max-instances=10 \
    --timeout=900 \
    --concurrency=10 \
    --allow-unauthenticated \
    --port=8080 \
    --set-env-vars="ENVIRONMENT=production,GRADIO_SERVER_NAME=0.0.0.0,OPENAI_API_KEY=$OPENAI_API_KEY"
```

**⏱️ Tempo estimado**: 2-3 minutos

---

## ✅ PASSO 10: Obter URL do Serviço

```bash
gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format='value(status.url)'
```

**Exemplo de saída:**
```
https://oma-video-generator-xxxxx-rj.a.run.app
```

**🎉 Copie essa URL e acesse no navegador!**

---

## 📊 PASSO 11: Verificar Logs

Após acessar a URL, verifique se tudo está funcionando:

```bash
gcloud run services logs read $SERVICE_NAME \
    --region=$REGION \
    --limit=50
```

Você deve ver:
```
🚀 Starting OMA Video Generator on port 8080
Running on local URL: http://0.0.0.0:8080
```

---

## 🔍 Comandos Úteis

### Ver status do serviço
```bash
gcloud run services describe $SERVICE_NAME --region=$REGION
```

### Ver logs em tempo real
```bash
gcloud run services logs tail $SERVICE_NAME --region=$REGION
```

### Atualizar variável de ambiente
```bash
gcloud run services update $SERVICE_NAME \
    --region=$REGION \
    --set-env-vars="OPENAI_API_KEY=nova-chave"
```

### Deletar o serviço
```bash
gcloud run services delete $SERVICE_NAME --region=$REGION
```

---

## 💡 Dicas

### Se o build falhar:
1. Verifique se está no diretório correto
2. Verifique se `Dockerfile.cloudrun` existe
3. Tente com máquina maior: `--machine-type=e2-highcpu-32`

### Se o deploy falhar:
1. Verifique se a imagem foi criada:
   ```bash
   gcloud artifacts docker images list $REGION-docker.pkg.dev/$PROJECT_ID/docker-repo/oma-api
   ```
2. Verifique permissões:
   ```bash
   gcloud projects get-iam-policy $PROJECT_ID
   ```

### Para economizar:
Use configuração mais leve:
```bash
--cpu=1 --memory=2Gi --max-instances=5
```

---

## 🎯 Script Completo (Copiar e Colar)

Para sua conveniência, aqui está tudo em um único bloco:

```bash
# ===== CONFIGURAÇÃO (EDITE AQUI!) =====
export PROJECT_ID="SEU-PROJECT-ID"
export REGION="southamerica-east1"
export SERVICE_NAME="oma-video-generator"
export OPENAI_API_KEY="sk-..."

# ===== VALIDAÇÃO =====
gcloud --version
gcloud auth login
gcloud config set project $PROJECT_ID

# ===== SETUP =====
gcloud services enable cloudbuild.googleapis.com run.googleapis.com artifactregistry.googleapis.com

gcloud artifacts repositories create docker-repo \
    --repository-format=docker \
    --location=$REGION \
    --description="OMA Docker Images" \
    || echo "Repository already exists"

# ===== BUILD =====
cd C:\Users\paulo\OneDrive\Desktop\OMA_REFACTORED

gcloud builds submit \
    --tag="$REGION-docker.pkg.dev/$PROJECT_ID/docker-repo/oma-api:latest" \
    --timeout=30m \
    --machine-type=e2-highcpu-8 \
    --dockerfile=Dockerfile.cloudrun \
    .

# ===== DEPLOY =====
gcloud run deploy $SERVICE_NAME \
    --image="$REGION-docker.pkg.dev/$PROJECT_ID/docker-repo/oma-api:latest" \
    --platform=managed \
    --region=$REGION \
    --cpu=2 \
    --memory=4Gi \
    --min-instances=0 \
    --max-instances=10 \
    --timeout=900 \
    --concurrency=10 \
    --allow-unauthenticated \
    --port=8080 \
    --set-env-vars="ENVIRONMENT=production,GRADIO_SERVER_NAME=0.0.0.0,OPENAI_API_KEY=$OPENAI_API_KEY"

# ===== RESULTADO =====
echo "=========================================="
echo "✅ Deploy completo!"
echo "=========================================="
gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)'
echo "=========================================="
```

---

## ❓ Problemas Comuns

### "gcloud: command not found"
- Windows: Adicione ao PATH: `C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin`
- Mac/Linux: Execute: `exec -l $SHELL` após instalação

### "You do not currently have an active account"
```bash
gcloud auth login
gcloud auth application-default login
```

### "Permission denied on project"
Verifique se você é owner/editor do projeto no console:
https://console.cloud.google.com/iam-admin/iam

### "Container failed to start"
Verifique logs:
```bash
gcloud run services logs read $SERVICE_NAME --region=$REGION --limit=100
```

### "OPENAI_API_KEY not working"
Teste se a key está válida:
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

---

**✅ Pronto! Seu deploy manual está configurado.**

Execute os comandos acima e me avise se encontrar algum erro!
