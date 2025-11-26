# 🐳 OMA.AI - Docker & LLMOps Guide

## 📋 Visão Geral

Este guia documenta a implementação completa de containerização e orquestração para o OMA.AI, baseado no planejamento LLMOps detalhado.

### **Arquitetura de Containers**

```
┌─────────────────────────────────────────────────┐
│           OMA.AI Docker Stack                   │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐      ┌──────────────┐       │
│  │   Dashboard  │◄────►│ Media Agent  │       │
│  │   (Gradio)   │      │   (FFmpeg)   │       │
│  └──────┬───────┘      └──────┬───────┘       │
│         │                      │                │
│         └──────────┬───────────┘                │
│                    ▼                            │
│            ┌──────────────┐                     │
│            │    Redis     │                     │
│            │ (Job Queue)  │                     │
│            └──────────────┘                     │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### **1. Pré-requisitos**

- Docker Desktop instalado e rodando
- 4GB RAM disponível mínimo
- 10GB espaço em disco
- API keys configuradas

### **2. Setup Rápido**

```bash
# Windows
docker-setup.bat

# Linux/Mac
chmod +x docker-setup.sh
./docker-setup.sh
```

O script automaticamente:
✅ Verifica Docker
✅ Cria .env se necessário
✅ Builda as imagens
✅ Testa FFmpeg
✅ Inicia todos os serviços

### **3. Acessar Dashboard**

Abra http://localhost:7860 no navegador

---

## 📦 Componentes Docker

### **Dockerfile.dashboard**

**Propósito**: Interface Gradio e orquestração dos agentes
**Base**: `python:3.11-slim`
**Tamanho**: ~500MB
**Recursos**: 1-2 CPU, 1-4GB RAM

**Features**:
- Multi-stage build otimizado
- Non-root user (segurança)
- Health checks configurados
- Port dinâmico para cloud

### **Dockerfile.media**

**Propósito**: Processamento de vídeo com FFmpeg e TTS
**Base**: `python:3.11-slim`
**Tamanho**: ~800MB
**Recursos**: 1-4 CPU, 2-8GB RAM

**Features**:
- FFmpeg completo instalado
- Bibliotecas de áudio (TTS)
- Otimizado para processamento paralelo
- Temp storage ephemeral

### **docker-compose.dev.yml**

**Serviços principais**:
1. **dashboard**: Interface web
2. **media-agent**: Worker de processamento
3. **redis**: Fila de jobs e cache

**Profiles opcionais**:
- `debug`: Redis Commander
- `monitoring`: Prometheus + Grafana

---

## 🔧 Comandos Úteis

### **Build e Deploy**

```bash
# Build apenas Dashboard
docker build -f Dockerfile.dashboard -t oma-dashboard:latest .

# Build apenas Media Agent
docker build -f Dockerfile.media -t oma-media-agent:latest .

# Build tudo (via compose)
docker-compose -f docker-compose.dev.yml build

# Iniciar stack completo
docker-compose -f docker-compose.dev.yml up -d

# Iniciar com monitoring
docker-compose -f docker-compose.dev.yml --profile monitoring up -d
```

### **Logs e Debug**

```bash
# Ver logs de todos os serviços
docker-compose -f docker-compose.dev.yml logs -f

# Ver logs apenas do Dashboard
docker-compose -f docker-compose.dev.yml logs -f dashboard

# Ver logs do Media Agent
docker-compose -f docker-compose.dev.yml logs -f media-agent

# Entrar no container (debug)
docker exec -it oma-dashboard /bin/bash
docker exec -it oma-media-agent /bin/bash
```

### **Manutenção**

```bash
# Parar todos os serviços
docker-compose -f docker-compose.dev.yml down

# Parar e remover volumes (CUIDADO: apaga dados!)
docker-compose -f docker-compose.dev.yml down -v

# Restart de um serviço específico
docker-compose -f docker-compose.dev.yml restart dashboard

# Ver status dos containers
docker-compose -f docker-compose.dev.yml ps

# Ver uso de recursos
docker stats
```

---

## 🔐 Segurança

### **Secrets Management**

```bash
# .env (NUNCA commitar!)
OPENROUTER_API_KEY=sk-or-v1-xxxxx
PEXELS_API_KEY=xxxxx
STABILITY_API_KEY=xxxxx
ELEVENLABS_API_KEY=xxxxx
```

### **Best Practices Implementadas**

✅ Non-root user em todos os containers
✅ Read-only filesystems onde possível
✅ Secrets via environment variables
✅ Health checks para auto-recovery
✅ Resource limits configurados
✅ .dockerignore otimizado (exclui .env, logs, etc)

---

## 📊 Monitoramento

### **Metrics & Observability**

**Prometheus** (http://localhost:9090):
- Container metrics (CPU, RAM, disco)
- Custom metrics dos agentes
- Queue depth (Redis)

**Grafana** (http://localhost:3000):
- Dashboards pré-configurados
- Alertas de custo e performance
- Logs estruturados

**Ativar monitoramento**:
```bash
docker-compose -f docker-compose.dev.yml --profile monitoring up -d
```

### **Health Checks**

Todos os containers têm health checks automáticos:

```bash
# Verificar saúde dos containers
docker-compose -f docker-compose.dev.yml ps

# Ver detalhes de saúde
docker inspect oma-dashboard | grep -A 10 Health
```

---

## 🚢 Deploy para Produção

### **Opção 1: Google Cloud Run** (Recomendado)

```bash
# Build para GCR
docker build -f Dockerfile.dashboard -t gcr.io/PROJECT-ID/oma-dashboard:latest .
docker push gcr.io/PROJECT-ID/oma-dashboard:latest

# Deploy
gcloud run deploy oma-dashboard \
  --image gcr.io/PROJECT-ID/oma-dashboard:latest \
  --platform managed \
  --region us-central1 \
  --set-env-vars OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
```

### **Opção 2: Kubernetes (GKE/EKS/AKS)**

Ver arquivos em `k8s/`:
- `deployment-dashboard.yaml`
- `deployment-media-agent.yaml`
- `service.yaml`
- `hpa.yaml`

```bash
# Deploy no GKE
kubectl apply -f k8s/
```

### **Opção 3: Railway/Render**

Railway detecta automaticamente `Dockerfile.dashboard`.

Configurar variáveis de ambiente no painel web:
- `OPENROUTER_API_KEY`
- `PEXELS_API_KEY`
- `PORT` (Railway preenche automaticamente)

---

## 🐛 Troubleshooting

### **Problema: FFmpeg não encontrado no Media Agent**

```bash
# Testar FFmpeg manualmente
docker run --rm oma-media-agent:latest ffmpeg -version

# Se falhar, rebuild com cache limpo
docker build --no-cache -f Dockerfile.media -t oma-media-agent:latest .
```

### **Problema: Dashboard não inicia**

```bash
# Verificar logs
docker-compose -f docker-compose.dev.yml logs dashboard

# Verificar se porta 7860 está livre
netstat -an | grep 7860

# Testar imagem isoladamente
docker run -p 7860:7860 --env-file .env oma-dashboard:latest
```

### **Problema: Out of Memory**

```bash
# Aumentar memória do container
# Editar docker-compose.dev.yml:

services:
  media-agent:
    deploy:
      resources:
        limits:
          memory: 4G  # Aumentar de 2G para 4G
```

### **Problema: Redis connection failed**

```bash
# Verificar se Redis está rodando
docker-compose -f docker-compose.dev.yml ps redis

# Testar conexão
docker exec -it oma-redis redis-cli ping
# Deve retornar: PONG

# Restart Redis
docker-compose -f docker-compose.dev.yml restart redis
```

---

## 📈 Performance Tuning

### **Otimizações de Build**

```dockerfile
# Use BuildKit para builds mais rápidos
export DOCKER_BUILDKIT=1
docker build -f Dockerfile.media -t oma-media-agent:latest .

# Build com cache de layers
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
```

### **Resource Optimization**

```yaml
# docker-compose.dev.yml
services:
  media-agent:
    deploy:
      resources:
        limits:
          cpus: '4.0'      # Ajustar baseado no seu hardware
          memory: 8G
        reservations:
          cpus: '2.0'
          memory: 4G
```

### **Network Optimization**

```bash
# Usar rede host para melhor performance (Linux apenas)
docker run --network host oma-dashboard:latest
```

---

## 📚 Próximos Passos

1. ✅ **Teste Local**: Valide stack completa localmente
2. 🔄 **CI/CD**: Configure GitHub Actions para build automático
3. ☁️ **Deploy Cloud**: Escolha plataforma (GCP recomendado)
4. 📊 **Monitoring**: Ative Prometheus + Grafana
5. 🔐 **Hardening**: Implemente rate limiting e WAF

---

## 🆘 Suporte

**Problemas com Docker?**
- Consulte [DOCKER_GUIDE.md](DOCKER_GUIDE.md)
- Veja logs: `docker-compose logs -f`
- Limpe cache: `docker system prune -a`

**Problemas com Deploy?**
- Consulte [DEPLOY_CLOUDRUN.md](DEPLOY_CLOUDRUN.md)
- Consulte [SECURITY_DEPLOY_CHECKLIST.md](SECURITY_DEPLOY_CHECKLIST.md)

---

**Versão**: 1.0
**Última atualização**: 2025-11-25
**Autor**: Claude Code (Anthropic)
**Projeto**: OMA.AI LLMOps Implementation
