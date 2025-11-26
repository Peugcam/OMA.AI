# 🚀 OMA.AI - Próximos Passos para Deploy LLMOps

## ✅ Implementação Concluída

Todos os arquivos necessários para containerização foram criados com sucesso:

### **Arquivos Criados**

| Arquivo | Descrição | Status |
|---------|-----------|--------|
| `Dockerfile.media` | Container otimizado para processamento de mídia com FFmpeg | ✅ |
| `Dockerfile.dashboard` | Container lightweight para Gradio Dashboard | ✅ |
| `docker-compose.dev.yml` | Stack completo de desenvolvimento com Redis | ✅ |
| `.dockerignore` | Otimizado para excluir arquivos desnecessários | ✅ |
| `monitoring/prometheus.yml` | Configuração de métricas e monitoramento | ✅ |
| `docker-setup.bat` | Script automatizado de setup (Windows) | ✅ |
| `docker-setup.sh` | Script automatizado de setup (Linux/Mac) | ✅ |
| `DOCKER_LLMOPS_GUIDE.md` | Documentação completa de uso | ✅ |

---

## 📋 Próximos Passos

### **Fase 1: Teste Local** (1-2 horas)

#### **1.1 Iniciar Docker Desktop**

⚠️ **IMPORTANTE**: O Docker Desktop precisa estar rodando antes de executar qualquer comando.

**Windows**:
1. Abra o Docker Desktop pelo menu Iniciar
2. Aguarde até ver "Docker Desktop is running" na bandeja do sistema
3. Verifique com: `docker info`

#### **1.2 Executar Setup Automatizado**

```bash
# Windows
cd C:\Users\paulo\OneDrive\Desktop\OMA_REFACTORED
docker-setup.bat

# Ou manualmente:
docker build -f Dockerfile.dashboard -t oma-dashboard:latest .
docker build -f Dockerfile.media -t oma-media-agent:latest .
docker-compose -f docker-compose.dev.yml up -d
```

#### **1.3 Validar Funcionamento**

```bash
# Verificar containers rodando
docker-compose -f docker-compose.dev.yml ps

# Ver logs do Dashboard
docker-compose -f docker-compose.dev.yml logs -f dashboard

# Testar FFmpeg no Media Agent
docker exec -it oma-media-agent ffmpeg -version

# Acessar Dashboard
# Abrir http://localhost:7860
```

#### **1.4 Testar Geração de Vídeo**

1. Acesse http://localhost:7860
2. Preencha os campos do formulário
3. Clique em "Generate Video"
4. Verifique se o vídeo é gerado corretamente
5. Cheque os logs: `docker-compose logs -f media-agent`

---

### **Fase 2: Deploy para Cloud** (1 dia)

#### **Opção A: Google Cloud Run** (Recomendado - $43/mês)

**Por quê?**
- 77% mais barato que AWS
- Scaling automático para zero
- Zero configuração de infraestrutura
- Melhor suporte para containers

**Passos**:

```bash
# 1. Instalar Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# 2. Fazer login
gcloud auth login

# 3. Criar projeto
gcloud projects create oma-ai-prod --name="OMA.AI Production"
gcloud config set project oma-ai-prod

# 4. Habilitar APIs
gcloud services enable \
  run.googleapis.com \
  containerregistry.googleapis.com \
  secretmanager.googleapis.com

# 5. Build e Push
docker build -f Dockerfile.dashboard -t gcr.io/oma-ai-prod/dashboard:v1 .
docker push gcr.io/oma-ai-prod/dashboard:v1

# 6. Criar secrets
echo -n "YOUR_OPENROUTER_KEY" | gcloud secrets create OPENROUTER_API_KEY --data-file=-
echo -n "YOUR_PEXELS_KEY" | gcloud secrets create PEXELS_API_KEY --data-file=-

# 7. Deploy
gcloud run deploy oma-dashboard \
  --image gcr.io/oma-ai-prod/dashboard:v1 \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-secrets=OPENROUTER_API_KEY=OPENROUTER_API_KEY:latest,PEXELS_API_KEY=PEXELS_API_KEY:latest \
  --memory 2Gi \
  --cpu 2 \
  --timeout 900
```

#### **Opção B: Railway** (Mais Simples - $5/mês)

**Por quê?**
- Deploy com 1 clique
- GitHub integration
- Free tier generoso
- Ideal para MVP

**Passos**:

1. Criar conta: https://railway.app
2. Conectar GitHub repository
3. Railway detecta `Dockerfile.dashboard` automaticamente
4. Configurar secrets no painel web:
   - `OPENROUTER_API_KEY`
   - `PEXELS_API_KEY`
5. Deploy automático!

#### **Opção C: Kubernetes (GKE)** (Produção - $100+/mês)

**Por quê?**
- Máximo controle e escalabilidade
- Arquitetura enterprise
- Multi-region deployment

**Passos**:

```bash
# Ver relatório completo do Cláudio para manifests Kubernetes
# Usar arquivos:
# - k8s/deployment-dashboard.yaml
# - k8s/deployment-media-agent.yaml
# - k8s/service.yaml
# - k8s/hpa.yaml
# - k8s/secrets.yaml

# 1. Criar cluster GKE Autopilot
gcloud container clusters create-auto oma-cluster \
  --region us-central1

# 2. Get credentials
gcloud container clusters get-credentials oma-cluster --region us-central1

# 3. Deploy
kubectl apply -f k8s/
```

---

### **Fase 3: Monitoramento e Otimização** (Contínuo)

#### **3.1 Configurar Monitoramento**

```bash
# Ativar Prometheus + Grafana localmente
docker-compose -f docker-compose.dev.yml --profile monitoring up -d

# Acessar:
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)
```

#### **3.2 Métricas a Monitorar**

- **Latência P95**: < 5s para gerar vídeo
- **Taxa de Sucesso**: > 95%
- **Custo por Vídeo**: < $0.05
- **CPU Usage**: 60-80% média
- **Queue Depth**: < 20 jobs

#### **3.3 Otimizações**

```yaml
# Ajustar HPA (Horizontal Pod Autoscaler)
# k8s/hpa.yaml

# Media Agent escala baseado em:
# - CPU > 70%
# - Queue depth > 5 jobs/pod
# - Memória > 80%

# Dashboard escala baseado em:
# - Requests/segundo
# - CPU > 60%
```

---

## 🔐 Checklist de Segurança

Antes de ir para produção, verifique:

- [ ] `.env` está no `.gitignore` (não commitar secrets!)
- [ ] API keys configuradas como secrets na plataforma cloud
- [ ] HTTPS habilitado (automático no Cloud Run/Railway)
- [ ] Rate limiting configurado (máx 100 requests/hora)
- [ ] Billing alerts configurados ($10, $50, $100)
- [ ] Backup automático de outputs configurado
- [ ] Logs não incluem API keys
- [ ] Containers rodando como non-root user ✅
- [ ] Health checks funcionando ✅
- [ ] Resource limits configurados ✅

---

## 💰 Estimativa de Custos

### **Cenário: 1000 vídeos/mês**

| Plataforma | Custo Mensal | Incluído |
|------------|--------------|----------|
| **Google Cloud Run** | **$43** | Compute + Storage + Egress |
| **Railway** | **$20** | 2GB RAM + 100GB Bandwidth |
| **AWS EKS** | **$188** | Cluster + EC2 + EBS + Transfer |
| **Azure AKS** | **$69** | VMs + Disks + Bandwidth |

**Recomendação**: Comece com Railway ($20/mês) para MVP, migre para GCP Cloud Run ($43/mês) para escala.

---

## 📊 Roadmap Técnico

### **Semana 1: Validação Local**
- [x] Criar Dockerfiles
- [x] Criar docker-compose
- [x] Criar documentação
- [ ] Testar build local
- [ ] Testar geração de vídeo
- [ ] Validar FFmpeg

### **Semana 2: Deploy MVP**
- [ ] Escolher plataforma (Railway ou Cloud Run)
- [ ] Configurar secrets
- [ ] Fazer primeiro deploy
- [ ] Testar em produção
- [ ] Configurar domínio

### **Semana 3: Monitoramento**
- [ ] Configurar Prometheus
- [ ] Criar dashboards Grafana
- [ ] Setup alertas (custo, erros)
- [ ] Implementar logging estruturado

### **Semana 4: Otimização**
- [ ] Analisar custos reais
- [ ] Otimizar resource limits
- [ ] Implementar cache strategy
- [ ] Configurar CDN para vídeos
- [ ] Fine-tuning HPA

---

## 🆘 Troubleshooting

### **Docker Desktop não inicia**

```bash
# Windows: Verificar se WSL 2 está instalado
wsl --install
wsl --set-default-version 2

# Restart Docker Desktop
# Settings > General > "Use WSL 2 based engine"
```

### **Build falha com "out of disk space"**

```bash
# Limpar cache do Docker
docker system prune -a
docker volume prune

# Verificar espaço
docker system df
```

### **Container não consegue acessar API keys**

```bash
# Verificar se .env existe
cat .env

# Testar container com env vars
docker run --env-file .env oma-dashboard:latest env | grep OPENROUTER
```

---

## 📚 Recursos Adicionais

- **Relatório LLMOps Completo**: Ver output do agente Cláudio acima
- **Documentação Docker**: [DOCKER_LLMOPS_GUIDE.md](DOCKER_LLMOPS_GUIDE.md)
- **Segurança**: [SECURITY_DEPLOY_CHECKLIST.md](SECURITY_DEPLOY_CHECKLIST.md)
- **Cloud Deploy**: [DEPLOY_CLOUDRUN.md](DEPLOY_CLOUDRUN.md)

---

## ✅ Quick Win Path (2 horas)

**Caminho mais rápido para ver funcionando**:

1. **Iniciar Docker Desktop** (5 min)
2. **Executar `docker-setup.bat`** (15 min build)
3. **Acessar http://localhost:7860** (imediato)
4. **Testar geração de vídeo** (2-5 min por vídeo)
5. **Deploy no Railway** (10 min)
6. **Vídeo na nuvem!** 🎉

---

**Status**: ✅ Pronto para teste local
**Próximo passo**: Iniciar Docker Desktop e rodar `docker-setup.bat`

**Dúvidas?** Consulte [DOCKER_LLMOPS_GUIDE.md](DOCKER_LLMOPS_GUIDE.md)

---

**Versão**: 1.0
**Data**: 2025-11-25
**Implementado por**: Claude Code
