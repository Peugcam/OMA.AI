#!/bin/bash
# ============================================================================
# OMA Video Generator - Google Cloud Deploy Script
# ============================================================================
# Script para deploy manual no Google Cloud Run
# ============================================================================

set -e  # Exit on error

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "======================================================"
echo "🚀 OMA Video Generator - Google Cloud Deploy"
echo "======================================================"

# ============================================
# CONFIGURAÇÕES (EDITE AQUI!)
# ============================================
PROJECT_ID="oma-video-prod"
REGION="southamerica-east1"
SERVICE_NAME="oma-video-generator"
REPO_NAME="docker-repo"

# Recursos
CPU="2"
MEMORY="4Gi"
MIN_INSTANCES="0"
MAX_INSTANCES="10"
TIMEOUT="900"
CONCURRENCY="10"

# ============================================
# VALIDAÇÕES
# ============================================
echo -e "${YELLOW}📋 Validating environment...${NC}"

# Checar se gcloud está instalado
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI não está instalado!${NC}"
    echo "Instale em: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Checar se está autenticado
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo -e "${RED}❌ Você não está autenticado no gcloud!${NC}"
    echo "Execute: gcloud auth login"
    exit 1
fi

# Verificar se API Key está definida
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}❌ OPENAI_API_KEY não está definida!${NC}"
    echo "Execute: export OPENAI_API_KEY='sua-chave-aqui'"
    exit 1
fi

echo -e "${GREEN}✅ Environment validated${NC}"

# ============================================
# CONFIGURAR PROJETO
# ============================================
echo -e "${YELLOW}🔧 Setting GCP project...${NC}"
gcloud config set project $PROJECT_ID

# ============================================
# HABILITAR APIs
# ============================================
echo -e "${YELLOW}🔌 Enabling required APIs...${NC}"
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    --quiet

# ============================================
# CRIAR ARTIFACT REGISTRY (se não existir)
# ============================================
echo -e "${YELLOW}📦 Checking Artifact Registry...${NC}"
if ! gcloud artifacts repositories describe $REPO_NAME --location=$REGION &> /dev/null; then
    echo "Creating Docker repository..."
    gcloud artifacts repositories create $REPO_NAME \
        --repository-format=docker \
        --location=$REGION \
        --description="OMA Video Generator Docker Images"
else
    echo "Repository already exists."
fi

# ============================================
# BUILD & PUSH DA IMAGEM usando cloudbuild.yaml
# ============================================
IMAGE_NAME="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/oma-api"

echo -e "${YELLOW}🏗️  Building and deploying via Cloud Build...${NC}"
gcloud builds submit \
    --config=cloudbuild.yaml \
    --timeout=30m \
    --machine-type=e2-highcpu-8 \
    --substitutions="_REGION=$REGION,_SERVICE_NAME=$SERVICE_NAME,_CPU=$CPU,_MEMORY=$MEMORY,_MIN_INSTANCES=$MIN_INSTANCES,_MAX_INSTANCES=$MAX_INSTANCES,_TIMEOUT=$TIMEOUT,_CONCURRENCY=$CONCURRENCY" \
    .

# ============================================
# OBTER URL DO SERVIÇO
# ============================================
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')

echo ""
echo "======================================================"
echo -e "${GREEN}✅ Deploy completed successfully!${NC}"
echo "======================================================"
echo -e "🌐 Service URL: ${GREEN}$SERVICE_URL${NC}"
echo ""
echo "📊 To view logs:"
echo "   gcloud run logs read $SERVICE_NAME --region=$REGION --limit=50"
echo ""
echo "🔍 To view service details:"
echo "   gcloud run services describe $SERVICE_NAME --region=$REGION"
echo ""
echo "🔥 To delete the service:"
echo "   gcloud run services delete $SERVICE_NAME --region=$REGION"
echo "======================================================"
