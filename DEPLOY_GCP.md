# 🚀 Deploy OMA Video Generator no Google Cloud

Guia completo para deploy no Google Cloud Run com CI/CD automático.

---

## 📋 Pré-requisitos

### 1. Conta Google Cloud
- Criar conta em: https://console.cloud.google.com
- Ativar billing (necessário para Cloud Run)
- Criar novo projeto GCP

### 2. Instalar Google Cloud SDK
```bash
# Linux/Mac
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Windows
# Baixar de: https://cloud.google.com/sdk/docs/install
```

### 3. Autenticar
```bash
gcloud auth login
gcloud config set project SEU-PROJECT-ID
```

### 4. Variáveis de Ambiente
Você precisa da sua chave OpenAI:
```bash
export OPENAI_API_KEY='sk-...'
```

---

## 🎯 Método 1: Deploy Manual (Recomendado para teste)

### Passo 1: Configurar Script
Edite o arquivo `deploy-gcp.sh`:
```bash
PROJECT_ID="seu-projeto-gcp"        # Seu Project ID
REGION="southamerica-east1"         # Região mais próxima do Brasil
SERVICE_NAME="oma-video-generator"  # Nome do serviço
```

### Passo 2: Executar Deploy
```bash
chmod +x deploy-gcp.sh
./deploy-gcp.sh
```

O script irá:
1. ✅ Validar ambiente e credenciais
2. ✅ Habilitar APIs necessárias
3. ✅ Criar Artifact Registry
4. ✅ Buildar imagem Docker
5. ✅ Deploy no Cloud Run
6. ✅ Retornar URL do serviço

### Passo 3: Acessar Aplicação
Após o deploy, você receberá uma URL como:
```
https://oma-video-generator-xxxxx-uc.a.run.app
```

---

## 🔄 Método 2: CI/CD Automático (Deploy a cada commit)

### Passo 1: Habilitar APIs
```bash
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com
```

### Passo 2: Criar Artifact Registry
```bash
gcloud artifacts repositories create docker-repo \
    --repository-format=docker \
    --location=southamerica-east1 \
    --description="OMA Docker Images"
```

### Passo 3: Configurar Cloud Build Trigger

#### Opção A: Via Console (Mais fácil)
1. Acesse: https://console.cloud.google.com/cloud-build/triggers
2. Clique em **"Criar Trigger"**
3. Conecte seu repositório (GitHub/GitLab/Bitbucket)
4. Configure:
   - **Nome**: `oma-auto-deploy`
   - **Evento**: Push para branch `main` ou `master`
   - **Arquivo de build**: `cloudbuild.yaml`
5. Adicionar variáveis:
   - `OPENAI_API_KEY`: sua chave OpenAI

#### Opção B: Via CLI
```bash
# Conectar repositório primeiro no console, depois:
gcloud builds triggers create github \
    --name="oma-auto-deploy" \
    --repo-name="seu-repo" \
    --repo-owner="seu-usuario" \
    --branch-pattern="^main$" \
    --build-config="cloudbuild.yaml"
```

### Passo 4: Configurar Secrets
```bash
# Adicionar OPENAI_API_KEY como secret
echo -n "sk-..." | gcloud secrets create openai-api-key --data-file=-

# Dar permissão ao Cloud Build
gcloud secrets add-iam-policy-binding openai-api-key \
    --member="serviceAccount:PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### Passo 5: Atualizar cloudbuild.yaml
Adicione no step de deploy:
```yaml
- '--set-secrets'
- 'OPENAI_API_KEY=openai-api-key:latest'
```

### Passo 6: Testar
```bash
git add .
git commit -m "🚀 Trigger Cloud Build deploy"
git push origin main
```

Acompanhe o build em:
https://console.cloud.google.com/cloud-build/builds

---

## 📊 Monitoramento e Logs

### Ver Logs em Tempo Real
```bash
gcloud run services logs tail oma-video-generator \
    --region=southamerica-east1
```

### Ver Últimas 50 Linhas
```bash
gcloud run services logs read oma-video-generator \
    --region=southamerica-east1 \
    --limit=50
```

### Ver Métricas
```bash
# CPU e Memória
gcloud run services describe oma-video-generator \
    --region=southamerica-east1 \
    --format="value(status.url)"
```

Ou acesse o console:
https://console.cloud.google.com/run

---

## ⚙️ Configurações Importantes

### Recursos do Cloud Run
No arquivo `cloudbuild.yaml` ou `deploy-gcp.sh`:

```yaml
_CPU: '2'              # vCPUs (1, 2, 4, 8)
_MEMORY: '4Gi'         # RAM (512Mi, 1Gi, 2Gi, 4Gi, 8Gi)
_MIN_INSTANCES: '0'    # Escala para zero quando não usado
_MAX_INSTANCES: '10'   # Máximo de instâncias simultâneas
_TIMEOUT: '900'        # 15 minutos (máx para Cloud Run)
_CONCURRENCY: '10'     # Requisições simultâneas por instância
```

### Custos Estimados
Com as configurações padrão (2 CPU + 4GB RAM):
- **Grátis**: 2 milhões de requisições/mês
- **Depois do free tier**: ~$0.024/hora quando ativo
- **Escala para zero**: Sem custo quando não usado

### Otimizar Custos
```bash
# Configuração econômica (1 CPU + 2GB)
--cpu=1 --memory=2Gi --min-instances=0

# Configuração performance (4 CPU + 8GB)
--cpu=4 --memory=8Gi --min-instances=1
```

---

## 🔐 Variáveis de Ambiente

### Definir no Deploy
```bash
gcloud run services update oma-video-generator \
    --region=southamerica-east1 \
    --set-env-vars="ENVIRONMENT=production,OPENAI_API_KEY=sk-..."
```

### Usando Secrets (Recomendado)
```bash
# Criar secret
echo -n "sk-..." | gcloud secrets create openai-key --data-file=-

# Usar no Cloud Run
gcloud run services update oma-video-generator \
    --region=southamerica-east1 \
    --set-secrets="OPENAI_API_KEY=openai-key:latest"
```

---

## 🛠️ Comandos Úteis

### Ver Informações do Serviço
```bash
gcloud run services describe oma-video-generator \
    --region=southamerica-east1
```

### Atualizar Recursos
```bash
gcloud run services update oma-video-generator \
    --region=southamerica-east1 \
    --cpu=4 \
    --memory=8Gi \
    --max-instances=20
```

### Deletar Serviço
```bash
gcloud run services delete oma-video-generator \
    --region=southamerica-east1
```

### Listar Todos os Serviços
```bash
gcloud run services list
```

### Ver Builds Anteriores
```bash
gcloud builds list --limit=10
```

---

## 🔍 Troubleshooting

### Erro: "Permission Denied"
```bash
# Adicionar papel de admin ao Cloud Build
gcloud projects add-iam-policy-binding SEU-PROJECT-ID \
    --member="serviceAccount:PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
    --role="roles/run.admin"
```

### Erro: "Timeout during build"
Aumente o timeout no `cloudbuild.yaml`:
```yaml
timeout: '3600s'  # 1 hora
```

### Erro: "Out of Memory"
Aumente a memória:
```bash
gcloud run services update oma-video-generator \
    --memory=8Gi
```

### Container não inicia
Verifique logs:
```bash
gcloud run services logs read oma-video-generator --limit=100
```

### FFmpeg não encontrado
Verifique se está instalado no Dockerfile.cloudrun:
```dockerfile
RUN apt-get install -y ffmpeg
RUN ffmpeg -version  # Validar
```

---

## 📚 Recursos Adicionais

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Artifact Registry](https://cloud.google.com/artifact-registry/docs)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
- [Best Practices](https://cloud.google.com/run/docs/tips/general)

---

## ✅ Checklist de Deploy

- [ ] Conta GCP criada e billing ativado
- [ ] Google Cloud SDK instalado
- [ ] Autenticado com `gcloud auth login`
- [ ] Project ID definido
- [ ] OPENAI_API_KEY configurada
- [ ] Artifact Registry criado
- [ ] Deploy realizado com sucesso
- [ ] URL do serviço funcionando
- [ ] Logs monitorados
- [ ] Custos revisados

---

## 🎉 Próximos Passos

Após o deploy bem-sucedido:

1. **Domínio Customizado**: Configure um domínio próprio
2. **Cloud CDN**: Adicione CDN para servir vídeos mais rápido
3. **Cloud Storage**: Use para armazenar vídeos permanentemente
4. **Cloud Monitoring**: Configure alertas de erro/latência
5. **Load Testing**: Teste com ferramentas como `wrk` ou `locust`

---

**Precisa de ajuda?** Abra uma issue no repositório!
