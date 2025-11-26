# 🚀 OMA.AI - INÍCIO RÁPIDO (5 MINUTOS)

## ⚠️ ANTES DE COMEÇAR

### **Passo 1: Iniciar Docker Desktop**

1. **Abra o Docker Desktop** do menu Iniciar do Windows
2. **Aguarde** até ver o ícone do Docker na bandeja do sistema (área de notificação)
3. **Confirme** que está escrito "Docker Desktop is running"

**IMPORTANTE**: Não prossiga até o Docker estar completamente iniciado!

---

## 🎯 OPÇÃO A: SCRIPT AUTOMATIZADO (RECOMENDADO)

### **Executar em 1 clique:**

```cmd
# Duplo clique no arquivo:
START_HERE.bat
```

**O script vai:**
- ✅ Verificar se Docker está rodando
- ✅ Criar .env se não existir
- ✅ Build das imagens otimizadas (8-10 min)
- ✅ Iniciar todos os serviços
- ✅ Abrir Dashboard no navegador

---

## 🛠️ OPÇÃO B: PASSO A PASSO MANUAL

### **1. Configurar API Keys**

```cmd
# Se .env não existe, copiar do exemplo
copy .env.example .env

# Editar .env e adicionar suas keys:
notepad .env
```

**Mínimo necessário:**
```env
OPENROUTER_API_KEY=sk-or-v1-YOUR-KEY-HERE
PEXELS_API_KEY=YOUR-PEXELS-KEY-HERE
```

### **2. Build das Imagens**

```cmd
cd C:\Users\paulo\OneDrive\Desktop\OMA_REFACTORED

# Dashboard (~3-5 min)
docker build -f Dockerfile.dashboard.optimized -t oma-dashboard:latest .

# Media Agent (~5-8 min)
docker build -f Dockerfile.media.optimized -t oma-media-agent:latest .
```

### **3. Iniciar Serviços**

```cmd
# Stack de desenvolvimento
docker-compose -f docker-compose.dev.yml up -d

# Aguardar 30 segundos para inicialização
timeout /t 30
```

### **4. Verificar Status**

```cmd
# Ver serviços rodando
docker-compose -f docker-compose.dev.yml ps

# Deve mostrar:
# - oma-dashboard (running)
# - oma-media-agent (running)
# - oma-redis (running)
```

### **5. Acessar Dashboard**

Abra no navegador: **http://localhost:7860**

---

## 📊 VERIFICAR SE ESTÁ FUNCIONANDO

### **Health Check:**

```cmd
# Testar endpoint de saúde
curl http://localhost:7860/health

# Deve retornar: 200 OK
```

### **Ver Logs:**

```cmd
# Dashboard
docker-compose -f docker-compose.dev.yml logs -f dashboard

# Media Agent
docker-compose -f docker-compose.dev.yml logs -f media-agent

# Redis
docker-compose -f docker-compose.dev.yml logs -f redis
```

---

## 🎬 TESTAR GERAÇÃO DE VÍDEO

### **No Dashboard (http://localhost:7860):**

1. Preencha os campos:
   - **Título**: "Introdução à IA"
   - **Descrição**: "Vídeo educativo sobre inteligência artificial"
   - **Duração**: 30 segundos
   - **Estilo**: Modern

2. Clique em **"Generate Video"**

3. Aguarde 2-5 minutos (acompanhe os logs)

4. Vídeo será salvo em `outputs/videos/`

---

## 🛑 PARAR SERVIÇOS

```cmd
# Parar todos os serviços
docker-compose -f docker-compose.dev.yml down

# Parar e remover volumes (CUIDADO: apaga dados!)
docker-compose -f docker-compose.dev.yml down -v
```

---

## 🔧 TROUBLESHOOTING

### **Problema: Docker não inicia**

**Solução:**
```cmd
# Verificar se WSL 2 está instalado (Windows)
wsl --install
wsl --set-default-version 2

# Reiniciar Docker Desktop
```

### **Problema: Build falha com "out of space"**

**Solução:**
```cmd
# Limpar cache do Docker
docker system prune -a

# Verificar espaço
docker system df
```

### **Problema: Porta 7860 já em uso**

**Solução:**
```cmd
# Ver o que está usando a porta
netstat -ano | findstr :7860

# Matar processo (substituir PID)
taskkill /F /PID <PID>
```

### **Problema: Container reinicia constantemente**

**Solução:**
```cmd
# Ver logs de erro
docker-compose -f docker-compose.dev.yml logs dashboard

# Verificar .env tem API keys válidas
type .env
```

---

## 📈 PRÓXIMOS PASSOS

Depois de testar localmente:

1. **Ler documentação completa**: [COMPLETE_IMPLEMENTATION_GUIDE.md](COMPLETE_IMPLEMENTATION_GUIDE.md)
2. **Deploy para cloud**: [DOCKER_NEXT_STEPS.md](DOCKER_NEXT_STEPS.md)
3. **Configurar CI/CD**: Ver `.github/workflows/ci-cd.yml`
4. **Monitoramento**: Ativar Prometheus + Grafana

---

## 🆘 PRECISA DE AJUDA?

### **Comandos de Debug:**

```cmd
# Status dos containers
docker ps -a

# Logs em tempo real
docker-compose -f docker-compose.dev.yml logs -f

# Entrar no container
docker exec -it oma-dashboard /bin/bash

# Verificar rede
docker network ls

# Inspecionar container
docker inspect oma-dashboard
```

### **Recursos:**
- **DOCKER_LLMOPS_GUIDE.md** - Guia completo Docker
- **IMPLEMENTATION_SUMMARY.md** - Resumo da implementação
- **SECURITY_DEPLOY_CHECKLIST.md** - Checklist de segurança

---

## ✅ CHECKLIST RÁPIDO

Antes de gerar seu primeiro vídeo:

- [ ] Docker Desktop rodando
- [ ] .env configurado com API keys
- [ ] Imagens buildadas (dashboard + media-agent)
- [ ] Serviços iniciados (docker-compose up)
- [ ] Dashboard acessível (http://localhost:7860)
- [ ] Health check OK (curl http://localhost:7860/health)

**Tudo OK?** Você está pronto para gerar vídeos! 🎉

---

**Versão**: 1.0
**Atualizado**: 2025-11-25
**Tempo estimado**: 5-10 minutos (após Docker iniciar)
