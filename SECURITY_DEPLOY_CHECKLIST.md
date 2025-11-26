# 🔒 Checklist de Segurança para Deploy - OMA Video Generator

## ⚠️ PONTOS CRÍTICOS ANTES DO DEPLOY

### 1. **SEGREDOS E CREDENCIAIS** 🔑

#### ❌ NUNCA FAÇA:
- [ ] ❌ Commitar arquivo `.env` no Git
- [ ] ❌ Hardcoded API keys no código
- [ ] ❌ Compartilhar keys em screenshots/vídeos
- [ ] ❌ Deixar keys em logs públicos
- [ ] ❌ Usar mesma key em dev e prod

#### ✅ SEMPRE FAÇA:
- [ ] ✅ Use variáveis de ambiente no servidor
- [ ] ✅ Diferentes keys para dev/staging/prod
- [ ] ✅ Rotacione keys regularmente (30-90 dias)
- [ ] ✅ Use Secret Manager (GCP/AWS/Azure)
- [ ] ✅ Monitore uso de APIs para detectar abusos

---

## 🔐 APIS E KEYS QUE VOCÊ USA

### **OpenRouter API** (CRÍTICO)
- **Arquivo**: `.env` → `OPENROUTER_API_KEY`
- **Custo**: Pay-as-you-go (pode ser cobrado!)
- **Risco**: Se vazado, terceiros podem usar e VOCÊ paga
- **Ação**:
  ```bash
  # NO SERVIDOR (Google Cloud, Railway, etc):
  # Configurar como variável de ambiente
  gcloud secrets create OPENROUTER_API_KEY --data-file=-
  # Ou no painel web da plataforma
  ```

### **Pexels API**
- **Arquivo**: `.env` → `PEXELS_API_KEY`
- **Custo**: Grátis (200 requests/hora)
- **Risco**: Baixo, mas limite pode ser atingido
- **Ação**: Mesma abordagem de Secret Manager

### **Stability AI** (OPCIONAL)
- **Arquivo**: `.env` → `STABILITY_API_KEY`
- **Custo**: $0.04 por imagem gerada
- **Risco**: ALTO - pode gerar custos altos se abusado
- **Ação**:
  - Configurar billing alerts
  - Limitar rate (max X gerações/minuto)

### **ElevenLabs** (OPCIONAL)
- **Arquivo**: `.env` → `ELEVENLABS_API_KEY`
- **Custo**: Pay-as-you-go
- **Risco**: Médio
- **Ação**: Rate limiting no código

---

## 📦 CHECKLIST DE SEGURANÇA POR PLATAFORMA

### **Google Cloud Run**

#### Antes do Deploy:
- [ ] Criar projeto separado para produção
- [ ] Habilitar Cloud Secret Manager
- [ ] Configurar Service Account com mínimos privilégios
- [ ] Configurar billing alerts ($10, $50, $100)
- [ ] Habilitar Cloud Armor (firewall)

#### Configurar Secrets:
```bash
# 1. Criar secrets
echo -n "sk-or-v1-YOUR_KEY" | gcloud secrets create OPENROUTER_API_KEY --data-file=-
echo -n "YOUR_PEXELS_KEY" | gcloud secrets create PEXELS_API_KEY --data-file=-

# 2. Dar permissão ao Cloud Run
gcloud secrets add-iam-policy-binding OPENROUTER_API_KEY \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT" \
  --role="roles/secretmanager.secretAccessor"

# 3. Referenciar no deploy
gcloud run deploy oma-video-generator \
  --set-secrets=OPENROUTER_API_KEY=OPENROUTER_API_KEY:latest,PEXELS_API_KEY=PEXELS_API_KEY:latest
```

#### Segurança Adicional:
- [ ] Configurar Cloud IAP (Identity-Aware Proxy) para autenticação
- [ ] Rate limiting via Cloud Armor
- [ ] Logs estruturados (não incluir keys!)
- [ ] Alertas de erro/spike de custos

---

### **Railway**

#### Configuração:
```bash
# No painel Railway:
# Settings → Environment Variables → Add Variable

OPENROUTER_API_KEY=sk-or-v1-...
PEXELS_API_KEY=...
STABILITY_API_KEY=...
```

#### Segurança:
- [ ] Não commitar `.env`
- [ ] Usar environment variables do Railway
- [ ] Configurar health checks
- [ ] Habilitar auto-restart on failure

---

### **Render**

#### Configuração via `render.yaml`:
```yaml
services:
  - type: web
    name: oma-video-generator
    env: docker
    envVars:
      - key: OPENROUTER_API_KEY
        sync: false  # Não sincroniza do repo
      - key: PEXELS_API_KEY
        sync: false
```

#### No painel Render:
- Settings → Environment → Add Secret File
- Adicionar cada secret manualmente

---

## 🚨 VULNERABILIDADES COMUNS

### 1. **Command Injection** ⚠️ ALTO RISCO

**Onde está no código:**
- `editor_agent.py` - usa FFmpeg via subprocess
- Inputs do usuário podem injetar comandos

**Proteção atual:**
```python
# agents/editor_agent.py usa shlex.quote()
cmd = f"ffmpeg -i {shlex.quote(video_path)} ..."
```

**✅ VERIFICAR:**
- [ ] Todos os inputs estão sanitizados
- [ ] Usar `shlex.quote()` em todos subprocess
- [ ] Validar extensões de arquivo

---

### 2. **Path Traversal** ⚠️ MÉDIO RISCO

**Onde está:**
- Upload de arquivos
- Leitura de vídeos gerados

**Proteção:**
```python
# Validar paths antes de usar
from pathlib import Path

def safe_path(user_input, base_dir):
    path = Path(base_dir) / user_input
    path = path.resolve()
    if not str(path).startswith(str(base_dir)):
        raise ValueError("Invalid path")
    return path
```

---

### 3. **Rate Limiting** ⚠️ ALTO RISCO (CUSTO)

**Problema:**
- Sem rate limit, usuário pode gerar 1000 vídeos e gerar custos altíssimos

**Solução:**
```python
# Adicionar em api/main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/generate")
@limiter.limit("5/hour")  # Max 5 vídeos por hora por IP
async def generate_video(briefing: dict):
    ...
```

---

### 4. **Input Validation** ⚠️ MÉDIO RISCO

**Validar:**
- [ ] Duração: 10-120 segundos (não aceitar 9999)
- [ ] Título: max 200 caracteres
- [ ] Descrição: max 5000 caracteres
- [ ] Estilo/tom: valores válidos apenas

**Código:**
```python
# api/models.py
from pydantic import BaseModel, Field, validator

class VideoBriefing(BaseModel):
    title: str = Field(..., max_length=200)
    description: str = Field(..., max_length=5000)
    duration: int = Field(..., ge=10, le=120)

    @validator('style')
    def validate_style(cls, v):
        valid = ['modern', 'corporate', 'educational', 'promotional', 'social']
        if v not in valid:
            raise ValueError(f'Style must be one of {valid}')
        return v
```

---

### 5. **Logs com Dados Sensíveis** ⚠️ BAIXO RISCO

**Problema:**
```python
# ❌ MAU
logger.info(f"Using API key: {api_key}")

# ✅ BOM
logger.info("API key configured")
```

**Verificar:**
- [ ] Nenhum log inclui API keys
- [ ] Logs não incluem IPs/emails de usuários
- [ ] Usar níveis de log apropriados

---

## 💰 CONTROLE DE CUSTOS

### **Configurar Billing Alerts**

#### Google Cloud:
```bash
# Criar budget alert
gcloud billing budgets create \
  --billing-account=YOUR_BILLING_ACCOUNT \
  --display-name="OMA Monthly Budget" \
  --budget-amount=100USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

### **Estimativas de Custo por Vídeo:**

| Componente | Custo | Notas |
|------------|-------|-------|
| OpenRouter (LLM) | $0.0003 | Script generation |
| Pexels | $0 | Grátis (rate limited) |
| Stability AI | $0.04 | Se usar geração de imagem |
| Cloud Run | $0.0002 | Compute time |
| **Total (sem Stability)** | **$0.0005** | **Ultra-baixo** |
| **Total (com Stability)** | **$0.0405** | **Cuidado!** |

### **Rate Limiting Recomendado:**

```python
# config.py
MAX_VIDEOS_PER_HOUR_FREE = 5
MAX_VIDEOS_PER_HOUR_PAID = 50
MAX_CONCURRENT_GENERATIONS = 3
MAX_DURATION_SECONDS = 120
```

---

## 🔍 MONITORAMENTO

### **Métricas Críticas:**
- [ ] Número de gerações/hora
- [ ] Custo acumulado/dia
- [ ] Taxa de erro (>10% = problema)
- [ ] Latência média (>5min = problema)
- [ ] Storage usado (limpar vídeos antigos)

### **Alertas:**
- [ ] Custo diário > $10
- [ ] Mais de 100 gerações/hora
- [ ] Taxa de erro > 20%
- [ ] Storage > 90% capacity

### **Google Cloud Monitoring:**
```bash
# Criar alerta de custo
gcloud alpha monitoring policies create \
  --notification-channels=YOUR_CHANNEL \
  --display-name="High API usage" \
  --condition-display-name="OpenRouter requests > 1000/hour"
```

---

## 🧹 LIMPEZA E MANUTENÇÃO

### **Rotação de Secrets** (A cada 90 dias):
1. Gerar nova API key
2. Adicionar como secret
3. Deploy com nova key
4. Testar
5. Revogar key antiga

### **Limpeza de Arquivos**:
```python
# Adicionar job de limpeza
# Deletar vídeos com mais de 7 dias
import shutil
from datetime import datetime, timedelta

def cleanup_old_videos():
    outputs_dir = Path("outputs/videos")
    cutoff = datetime.now() - timedelta(days=7)

    for video in outputs_dir.glob("*.mp4"):
        if datetime.fromtimestamp(video.stat().st_mtime) < cutoff:
            video.unlink()
            print(f"Deleted old video: {video.name}")
```

---

## ✅ CHECKLIST FINAL ANTES DO DEPLOY

### **Código:**
- [ ] `.env` está no `.gitignore`
- [ ] Nenhum secret hardcoded
- [ ] Input validation implementada
- [ ] Rate limiting configurado
- [ ] Error handling robusto
- [ ] Logs não incluem dados sensíveis

### **Infraestrutura:**
- [ ] Secrets no Secret Manager
- [ ] Billing alerts configurados
- [ ] Firewall/Cloud Armor habilitado
- [ ] Backup configurado
- [ ] Health checks funcionando
- [ ] Auto-scaling configurado

### **Monitoramento:**
- [ ] Logs centralizados
- [ ] Métricas de custo
- [ ] Alertas configurados
- [ ] Dashboard de monitoramento

### **Documentação:**
- [ ] README atualizado
- [ ] Runbook de incidentes
- [ ] Procedimentos de rollback
- [ ] Contatos de suporte

---

## 🆘 PLANO DE RESPOSTA A INCIDENTES

### **Key Comprometida:**
1. **IMEDIATO**: Revogar key na plataforma
2. Gerar nova key
3. Atualizar secrets no servidor
4. Fazer redeploy
5. Analisar logs para uso não autorizado
6. Contestar cobranças indevidas

### **Custo Inesperado:**
1. Pausar serviço imediatamente
2. Analisar logs de uso
3. Identificar fonte (IP/usuário)
4. Bloquear abusador
5. Reativar com rate limiting mais agressivo

### **Serviço Down:**
1. Verificar logs
2. Verificar billing (pode ter sido pausado)
3. Fazer rollback se necessário
4. Comunicar usuários

---

## 📞 CONTATOS ÚTEIS

- **OpenRouter Support**: https://openrouter.ai/support
- **Pexels API**: https://www.pexels.com/api/documentation/
- **Google Cloud Support**: console.cloud.google.com/support
- **Stability AI**: https://stability.ai/support

---

## 📚 RECURSOS ADICIONAIS

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Google Cloud Security Best Practices](https://cloud.google.com/security/best-practices)
- [Twelve-Factor App](https://12factor.net/)

---

**Última atualização**: 2025-11-24
**Versão**: 1.0
**Autor**: Claude Code (Anthropic)
