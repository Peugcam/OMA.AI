# 🔧 OMA.AI - Troubleshooting Guide

## ❌ Erro: ERR_CONNECTION_REFUSED (localhost:7860)

### **Diagnóstico do Problema**

Você está vendo este erro porque:
```
localhost se recusou a se conectar
ERR_CONNECTION_REFUSED
```

**Causa**: O Docker Desktop não está rodando OU os containers não foram iniciados.

---

## ✅ SOLUÇÃO PASSO A PASSO

### **Passo 1: Verificar se Docker Desktop está Rodando**

#### **Windows:**

1. **Procurar ícone do Docker na bandeja** (canto inferior direito, perto do relógio)

2. **Se NÃO aparecer o ícone:**
   - Abra o Menu Iniciar
   - Digite "Docker Desktop"
   - Clique em "Docker Desktop"
   - Aguarde 1-2 minutos

3. **Quando o Docker iniciar você verá:**
   - Ícone do Docker na bandeja
   - Tooltip: "Docker Desktop is running"
   - Luz verde no ícone

#### **Testar se Docker está funcionando:**

Abra o CMD (Prompt de Comando) e execute:
```cmd
docker --version
```

**Deve retornar algo como:**
```
Docker version 28.3.2, build 578ccf6
```

**Se retornar erro:**
```
error during connect: ...
```
→ Docker Desktop ainda não iniciou. Aguarde mais 1-2 minutos.

---

### **Passo 2: Verificar se Containers estão Rodando**

No CMD, execute:
```cmd
docker ps
```

**Cenário A: Retorna lista vazia**
```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```
→ Containers não foram criados. Vá para **Passo 3**.

**Cenário B: Mostra containers parados (Exited)**
```
CONTAINER ID   IMAGE              STATUS
abc123         oma-dashboard      Exited (1) 2 minutes ago
```
→ Containers existem mas estão parados. Vá para **Passo 4**.

**Cenário C: Mostra containers rodando (Up)**
```
CONTAINER ID   IMAGE              STATUS              PORTS
abc123         oma-dashboard      Up 2 minutes        0.0.0.0:7860->7860/tcp
```
→ Tudo OK! Vá para **Passo 5**.

---

### **Passo 3: Criar e Iniciar Containers (Primeira Vez)**

Se containers não existem, você precisa buildá-los primeiro:

```cmd
cd C:\Users\paulo\OneDrive\Desktop\OMA_REFACTORED

REM Verificar se .env existe
dir .env
```

**Se .env NÃO existe:**
```cmd
copy .env.example .env
notepad .env
```

**Edite o .env e adicione suas API keys:**
```env
OPENROUTER_API_KEY=sk-or-v1-YOUR-KEY-HERE
PEXELS_API_KEY=YOUR-PEXELS-KEY-HERE
```
Salve e feche.

**Agora execute o script automático:**
```cmd
START_HERE.bat
```

**OU manualmente:**
```cmd
REM Build Dashboard (5-8 minutos)
docker build -f Dockerfile.dashboard.optimized -t oma-dashboard:latest .

REM Build Media Agent (5-8 minutos)
docker build -f Dockerfile.media.optimized -t oma-media-agent:latest .

REM Iniciar stack
docker-compose -f docker-compose.dev.yml up -d

REM Aguardar 30 segundos
timeout /t 30
```

---

### **Passo 4: Reiniciar Containers (Se estão parados)**

Se containers existem mas estão parados:

```cmd
cd C:\Users\paulo\OneDrive\Desktop\OMA_REFACTORED

REM Iniciar containers
docker-compose -f docker-compose.dev.yml up -d

REM Verificar status
docker-compose -f docker-compose.dev.yml ps
```

**Se containers continuam parando, ver logs:**
```cmd
docker-compose -f docker-compose.dev.yml logs dashboard
```

**Erros comuns nos logs:**

1. **"OPENROUTER_API_KEY not found"**
   → Edite .env e adicione a key

2. **"port 7860 already in use"**
   → Execute: `netstat -ano | findstr :7860`
   → Mate o processo: `taskkill /F /PID <PID>`

3. **"Out of memory"**
   → Feche programas pesados
   → Aumente RAM no Docker Desktop (Settings > Resources)

---

### **Passo 5: Verificar se Dashboard está Acessível**

```cmd
REM Testar endpoint
curl http://localhost:7860/health

REM OU
powershell -Command "Invoke-WebRequest -Uri http://localhost:7860/health"
```

**Resposta esperada:**
```
StatusCode: 200
```

**Se retornar erro:**
```cmd
REM Ver logs em tempo real
docker-compose -f docker-compose.dev.yml logs -f dashboard
```

---

### **Passo 6: Acessar Dashboard**

Abra o navegador em:
```
http://localhost:7860
```

**Deve mostrar a interface do Gradio!**

---

## 🔍 DIAGNÓSTICO AVANÇADO

### **Verificar Portas em Uso:**
```cmd
netstat -ano | findstr :7860
```

**Se porta está em uso por outro programa:**
```cmd
REM Encontre o PID (última coluna)
REM Mate o processo:
taskkill /F /PID <PID>
```

### **Verificar Rede Docker:**
```cmd
docker network ls
docker network inspect oma-network
```

### **Entrar no Container (Debug):**
```cmd
docker exec -it oma-dashboard /bin/bash

REM Dentro do container:
curl localhost:7860/health
printenv | grep API_KEY
```

### **Rebuild Completo (Solução Drástica):**
```cmd
cd C:\Users\paulo\OneDrive\Desktop\OMA_REFACTORED

REM Parar e remover TUDO
docker-compose -f docker-compose.dev.yml down -v

REM Limpar imagens
docker image rm oma-dashboard oma-media-agent

REM Limpar cache Docker
docker system prune -a

REM Rebuild do zero
START_HERE.bat
```

---

## 🆘 CHECKLIST DE TROUBLESHOOTING

Execute na ordem:

- [ ] Docker Desktop está rodando? (ícone na bandeja)
- [ ] `docker --version` funciona?
- [ ] `docker ps` mostra containers?
- [ ] Arquivo .env existe e tem API keys?
- [ ] Porta 7860 está livre? (`netstat -ano | findstr :7860`)
- [ ] Imagens foram buildadas? (`docker images | findstr oma`)
- [ ] Containers estão UP? (`docker ps`)
- [ ] Logs sem erros? (`docker-compose logs dashboard`)
- [ ] Health check OK? (`curl localhost:7860/health`)

---

## 📞 ÚLTIMOS RECURSOS

### **Se NADA funcionar:**

1. **Reinstalar Docker Desktop:**
   - Desinstalar completamente
   - Baixar versão mais recente
   - Instalar com WSL 2 backend

2. **Usar versão não-otimizada:**
   ```cmd
   REM Use os Dockerfiles originais
   docker build -f Dockerfile -t oma-dashboard:latest .
   docker-compose -f docker-compose.yml up -d
   ```

3. **Rodar sem Docker (Python local):**
   ```cmd
   pip install -r requirements.txt
   python app.py
   ```

---

## ✅ STATUS DE SUCESSO

Você saberá que está tudo OK quando:

1. ✅ `docker ps` mostra 3 containers (dashboard, media-agent, redis)
2. ✅ `curl localhost:7860/health` retorna 200
3. ✅ Navegador abre Dashboard em http://localhost:7860
4. ✅ Pode gerar um vídeo de teste

---

**Última atualização**: 2025-11-25
**Versão**: 1.0
