#!/bin/bash
# ============================================================================
# OMA Video Generation - Deploy para Google Cloud Run
# ============================================================================
# Este script automatiza o deploy completo no Cloud Run
# Execute: chmod +x deploy-cloudrun.sh && ./deploy-cloudrun.sh
# ============================================================================

set -e  # Parar em caso de erro

# ============================================
# CONFIGURAÇÕES (EDITE AQUI)
# ============================================
PROJECT_ID="${GCP_PROJECT_ID:-seu-projeto-gcp}"
REGION="${GCP_REGION:-southamerica-east1}"  # São Paulo
SERVICE_NAME="oma-video-generator"
IMAGE_NAME="oma-api"

# Recursos do container (ajuste conforme necessidade)
CPU="2"           # 2 vCPUs para FFmpeg
MEMORY="4Gi"      # 4GB RAM
MIN_INSTANCES="0" # Scale to zero (economia)
MAX_INSTANCES="10"
TIMEOUT="900"     # 15 minutos para vídeos longos
CONCURRENCY="10"  # Requests simultâneos por instância

# ============================================
# CORES PARA OUTPUT
# ============================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}   OMA Video Generator - Cloud Run Deploy   ${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# ============================================
# VERIFICAR PRÉ-REQUISITOS
# ============================================
echo -e "${YELLOW}[1/7] Verificando pré-requisitos...${NC}"

# Verificar gcloud instalado
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Erro: gcloud CLI não encontrado!${NC}"
    echo "Instale em: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Verificar docker instalado
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Erro: Docker não encontrado!${NC}"
    echo "Instale em: https://docs.docker.com/get-docker/"
    exit 1
fi

echo -e "${GREEN}✓ gcloud CLI instalado${NC}"
echo -e "${GREEN}✓ Docker instalado${NC}"

# ============================================
# CONFIGURAR PROJETO GCP
# ============================================
echo ""
echo -e "${YELLOW}[2/7] Configurando projeto GCP...${NC}"

# Verificar se projeto foi definido
if [ "$PROJECT_ID" == "seu-projeto-gcp" ]; then
    echo -e "${RED}Erro: Configure GCP_PROJECT_ID!${NC}"
    echo "Execute: export GCP_PROJECT_ID=seu-projeto-id"
    exit 1
fi

gcloud config set project $PROJECT_ID
echo -e "${GREEN}✓ Projeto configurado: $PROJECT_ID${NC}"

# Habilitar APIs necessárias
echo "Habilitando APIs necessárias..."
gcloud services enable cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com \
    artifactregistry.googleapis.com \
    --quiet

echo -e "${GREEN}✓ APIs habilitadas${NC}"

# ============================================
# CONFIGURAR ARTIFACT REGISTRY
# ============================================
echo ""
echo -e "${YELLOW}[3/7] Configurando Artifact Registry...${NC}"

# Criar repositório se não existir
gcloud artifacts repositories create docker-repo \
    --repository-format=docker \
    --location=$REGION \
    --description="OMA Docker images" \
    --quiet 2>/dev/null || echo "Repositório já existe"

# Configurar autenticação Docker
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

echo -e "${GREEN}✓ Artifact Registry configurado${NC}"

# ============================================
# BUILD DA IMAGEM DOCKER
# ============================================
echo ""
echo -e "${YELLOW}[4/7] Construindo imagem Docker...${NC}"

IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/docker-repo/${IMAGE_NAME}:latest"

# Build usando Dockerfile.cloudrun
docker build \
    -f Dockerfile.cloudrun \
    -t $IMAGE_URI \
    --platform linux/amd64 \
    .

echo -e "${GREEN}✓ Imagem construída: $IMAGE_URI${NC}"

# ============================================
# PUSH PARA ARTIFACT REGISTRY
# ============================================
echo ""
echo -e "${YELLOW}[5/7] Enviando imagem para Artifact Registry...${NC}"

docker push $IMAGE_URI

echo -e "${GREEN}✓ Imagem enviada${NC}"

# ============================================
# VERIFICAR VARIÁVEIS DE AMBIENTE
# ============================================
echo ""
echo -e "${YELLOW}[6/7] Verificando variáveis de ambiente...${NC}"

# Verificar se as chaves foram definidas
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo -e "${RED}Aviso: OPENROUTER_API_KEY não definida!${NC}"
    echo "Execute: export OPENROUTER_API_KEY=sua-chave"
    echo "Ou configure depois no Console do Cloud Run"
fi

if [ -z "$PEXELS_API_KEY" ]; then
    echo -e "${RED}Aviso: PEXELS_API_KEY não definida!${NC}"
fi

# ============================================
# DEPLOY NO CLOUD RUN
# ============================================
echo ""
echo -e "${YELLOW}[7/7] Fazendo deploy no Cloud Run...${NC}"

# Construir string de variáveis de ambiente
ENV_VARS="ENVIRONMENT=production"
ENV_VARS="${ENV_VARS},GRADIO_SERVER_NAME=0.0.0.0"

if [ -n "$OPENROUTER_API_KEY" ]; then
    ENV_VARS="${ENV_VARS},OPENROUTER_API_KEY=${OPENROUTER_API_KEY}"
fi

if [ -n "$PEXELS_API_KEY" ]; then
    ENV_VARS="${ENV_VARS},PEXELS_API_KEY=${PEXELS_API_KEY}"
fi

if [ -n "$STABILITY_API_KEY" ]; then
    ENV_VARS="${ENV_VARS},STABILITY_API_KEY=${STABILITY_API_KEY}"
fi

if [ -n "$ELEVENLABS_API_KEY" ]; then
    ENV_VARS="${ENV_VARS},ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY}"
fi

# Deploy
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_URI \
    --platform managed \
    --region $REGION \
    --cpu $CPU \
    --memory $MEMORY \
    --min-instances $MIN_INSTANCES \
    --max-instances $MAX_INSTANCES \
    --timeout $TIMEOUT \
    --concurrency $CONCURRENCY \
    --set-env-vars "$ENV_VARS" \
    --allow-unauthenticated \
    --port 8080

# ============================================
# RESULTADO
# ============================================
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}   DEPLOY CONCLUÍDO COM SUCESSO!           ${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

# Obter URL do serviço
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')

echo -e "${BLUE}URL do serviço:${NC} $SERVICE_URL"
echo ""
echo -e "${YELLOW}Próximos passos:${NC}"
echo "1. Acesse a URL acima para testar o dashboard"
echo "2. Configure variáveis de ambiente no Console se necessário:"
echo "   https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME"
echo ""
echo -e "${YELLOW}Comandos úteis:${NC}"
echo "  Ver logs:     gcloud run logs read --service $SERVICE_NAME --region $REGION"
echo "  Ver status:   gcloud run services describe $SERVICE_NAME --region $REGION"
echo "  Deletar:      gcloud run services delete $SERVICE_NAME --region $REGION"
echo ""
