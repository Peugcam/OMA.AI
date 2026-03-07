# 🔑 Guia de Setup - APIs para OMA.AI (Runway Edition)

**Data:** 2024-03-07
**Stack:** RunwayML Gen-3 + ElevenLabs + OpenRouter
**Objetivo:** Configurar todas as APIs necessárias para geração profissional de vídeos de afiliados

---

## 💰 RESUMO DE CUSTOS MENSAIS

| API | Plano | Custo/Mês | Uso |
|-----|-------|-----------|-----|
| **RunwayML Gen-3** | Standard | $28 | 200 créditos (~40 vídeos de 20s) |
| **ElevenLabs** | Starter | $22 | 100k caracteres/mês (~200 narrações) |
| **OpenRouter** | Pay-as-you-go | $10-20 | Scripts + Análise de produtos |
| **TOTAL** | | **$60-70/mês** | Produção automatizada completa |

**ROI Estimado:** Com 40 vídeos/mês, precisando converter apenas 2-3 vendas para pagar as APIs.

---

## 🚀 SETUP PASSO-A-PASSO

### 1️⃣ RunwayML Gen-3 (PRIORITÁRIO)

**Por quê:** Principal ferramenta de geração de vídeo AI profissional

**Passos:**

1. **Acesse:** https://runwayml.com/
2. **Crie conta:**
   - Clique em "Sign Up"
   - Use seu email (recomendo criar um email profissional se ainda não tiver)
   - Confirme o email

3. **Escolha o plano:**
   - Vá em "Pricing"
   - Selecione **"Standard" - $28/mês**
   - 200 créditos mensais
   - Gen-3 Alpha Turbo disponível

4. **Obtenha a API Key:**
   - Vá em Settings → API Keys
   - Clique em "Create New Key"
   - Copie a chave (formato: `rw_xxxxxxxxxxxxx`)
   - **IMPORTANTE:** Guarde em local seguro, só aparece uma vez!

5. **Teste rápido (opcional):**
   ```bash
   curl -X POST https://api.runwayml.com/v1/generate \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "A beautiful sunset over the ocean",
       "duration": 5
     }'
   ```

**Documentação:** https://docs.runwayml.com/

---

### 2️⃣ ElevenLabs (NARRAÇÃO PROFISSIONAL)

**Por quê:** Narração de qualidade humana para os vídeos

**Passos:**

1. **Acesse:** https://elevenlabs.io/
2. **Crie conta:**
   - Sign Up com Google ou Email
   - Confirme email

3. **Escolha o plano:**
   - **"Starter" - $22/mês**
   - 100,000 caracteres/mês
   - Suficiente para ~200 vídeos de 20s

4. **Obtenha a API Key:**
   - Clique no seu avatar (canto superior direito)
   - "Profile Settings"
   - Aba "API Keys"
   - Clique em "Create API Key"
   - Copie (formato: `sk_xxxxxxxxxxxxxxxxxxxxxxx`)

5. **Escolha uma voz:**
   - Vá em "Voice Lab"
   - Teste vozes disponíveis
   - Recomendações para português BR:
     - **Masculina:** "Paulo" ou "Matheus"
     - **Feminina:** "Isabella" ou "Camila"
   - Anote o `voice_id` da voz escolhida

6. **Teste rápido:**
   ```bash
   curl -X POST https://api.elevenlabs.io/v1/text-to-speech/VOICE_ID \
     -H "xi-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Esse é um teste de narração profissional",
       "model_id": "eleven_multilingual_v2"
     }' \
     --output test.mp3
   ```

**Documentação:** https://docs.elevenlabs.io/

---

### 3️⃣ OpenRouter (LLM MULTI-MODEL)

**Por quê:** Scripts criativos + Análise de produtos com Claude Vision

**Passos:**

1. **Acesse:** https://openrouter.ai/
2. **Crie conta:**
   - "Sign Up" com Google ou GitHub (recomendado)
   - Aceite os termos

3. **Adicione créditos:**
   - Vá em "Credits"
   - Adicione $10-20 iniciais
   - Dura 1-2 meses dependendo do uso

4. **Obtenha a API Key:**
   - Vá em "API Keys"
   - Clique em "Create Key"
   - Nomeie: "OMA.AI Production"
   - Copie a chave (formato: `sk-or-v1-xxxxxxxxxxxx`)

5. **Modelos recomendados para OMA.AI:**
   - **Scripts:** `anthropic/claude-3.5-sonnet` ($3/1M tokens)
   - **Análise de imagens:** `anthropic/claude-3.5-sonnet` (suporta vision)
   - **Fallback econômico:** `google/gemini-pro-1.5` ($0.50/1M tokens)

6. **Teste:**
   ```bash
   curl https://openrouter.ai/api/v1/chat/completions \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "anthropic/claude-3.5-sonnet",
       "messages": [{"role": "user", "content": "Teste"}]
     }'
   ```

**Documentação:** https://openrouter.ai/docs

---

## ⚙️ CONFIGURAÇÃO NO OMA.AI

### Passo 1: Criar arquivo .env

```bash
cd C:\Users\paulo\OneDrive\Desktop\OMA.AI
cp .env.example .env
```

### Passo 2: Editar .env com suas chaves

Abra `C:\Users\paulo\OneDrive\Desktop\OMA.AI\.env` e adicione:

```bash
# ============================================================================
# OMA.AI - Production Environment Variables
# ============================================================================

# ===================
# REQUIRED API KEYS
# ===================

# OpenRouter (Scripts + Claude Vision)
OPENROUTER_API_KEY=sk-or-v1-SEU_TOKEN_AQUI

# RunwayML Gen-3 (Video Generation)
RUNWAYML_API_KEY=rw_SEU_TOKEN_AQUI

# ElevenLabs (TTS Narration)
ELEVENLABS_API_KEY=sk_SEU_TOKEN_AQUI
ELEVENLABS_VOICE_ID=seu_voice_id_aqui

# ===================
# DEPRECATED (NÃO USAR)
# ===================
# Pexels - Substituído por RunwayML Gen-3
# PEXELS_API_KEY=

# Stability AI - Desnecessário com Runway
# STABILITY_API_KEY=

# ===================
# APPLICATION CONFIG
# ===================

ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# ===================
# VIDEO GENERATION CONFIG
# ===================

# Duração padrão dos vídeos (segundos)
DEFAULT_VIDEO_DURATION=20

# Duração máxima permitida
MAX_VIDEO_DURATION=30

# Número de clips por vídeo (20s = 4 clips de 5s)
CLIPS_PER_VIDEO=4

# Geração concorrente (Runway suporta múltiplas chamadas)
MAX_CONCURRENT_GENERATIONS=3

# Timeout por vídeo (minutos)
TASK_TIMEOUT_SECONDS=600

# ===================
# RUNWAYML CONFIG
# ===================

# Modelo a usar (gen3a_turbo recomendado para velocidade)
RUNWAYML_MODEL=gen3a_turbo

# Duração de cada clip (segundos)
RUNWAYML_CLIP_DURATION=5

# Qualidade (720p, 1080p)
RUNWAYML_RESOLUTION=1080p

# ===================
# ELEVENLABS CONFIG
# ===================

# Modelo de voz (multilingual v2 para português)
ELEVENLABS_MODEL=eleven_multilingual_v2

# Configurações de voz
ELEVENLABS_STABILITY=0.5
ELEVENLABS_SIMILARITY_BOOST=0.75
ELEVENLABS_STYLE=0.2

# ===================
# OPENROUTER CONFIG
# ===================

# Modelo para scripts criativos
OPENROUTER_SCRIPT_MODEL=anthropic/claude-3.5-sonnet

# Modelo para análise de produtos (com vision)
OPENROUTER_VISION_MODEL=anthropic/claude-3.5-sonnet

# Fallback econômico (opcional)
OPENROUTER_FALLBACK_MODEL=google/gemini-pro-1.5

# ===================
# SECURITY
# ===================

SECRET_KEY=generate-com-comando-abaixo
# python -c "import secrets; print(secrets.token_hex(32))"

# ===================
# SERVER CONFIG
# ===================

API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:7860,http://localhost:3000
```

### Passo 3: Gerar SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copie o output e substitua em `SECRET_KEY=`

### Passo 4: Validar configuração

```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✅ RUNWAYML:', 'OK' if os.getenv('RUNWAYML_API_KEY') else '❌ FALTANDO')"
```

---

## ✅ CHECKLIST DE VALIDAÇÃO

Antes de rodar o OMA.AI em produção, confirme:

- [ ] RunwayML Gen-3 API key configurada
- [ ] ElevenLabs API key + Voice ID configurados
- [ ] OpenRouter API key configurada
- [ ] Créditos adicionados no OpenRouter ($10+)
- [ ] Planos pagos ativos (Runway $28 + ElevenLabs $22)
- [ ] Arquivo .env criado e validado
- [ ] SECRET_KEY gerado (não usar o padrão!)
- [ ] Testou pelo menos uma API manualmente

---

## 🧪 TESTE INTEGRADO

Depois de configurar tudo, teste o sistema completo:

```bash
cd C:\Users\paulo\OneDrive\Desktop\OMA.AI

# Testar geração de vídeo completo
python create_video.py --produto "Perfume Chanel N5" --duracao 20 --test

# Ou via API
python -m uvicorn api.main:app --reload
# Acesse: http://localhost:8000/docs
```

---

## 📊 MONITORAMENTO DE CUSTOS

### Runway ML

- 200 créditos/mês = ~40 vídeos de 20s
- Após esgotar: $0.05/segundo adicional
- Dashboard: https://app.runwayml.com/billing

### ElevenLabs

- 100k caracteres/mês
- 1 vídeo de 20s ≈ 500 caracteres
- Dashboard: https://elevenlabs.io/subscription

### OpenRouter

- Pay-as-you-go
- 1 script ≈ $0.03
- 1 análise de imagem ≈ $0.02
- Dashboard: https://openrouter.ai/activity

**Total por vídeo:** ~$0.70 (Runway) + $0.11 (ElevenLabs) + $0.05 (OpenRouter) = **$0.86/vídeo**

---

## ⚠️ TROUBLESHOOTING

### Erro: "Invalid API Key" (RunwayML)

**Solução:**
1. Verifique se copiou a chave completa (começa com `rw_`)
2. Confirme que o plano está ativo
3. Regenere a chave se necessário

### Erro: "Insufficient credits" (RunwayML)

**Solução:**
1. Verifique créditos em: https://app.runwayml.com/billing
2. Upgrade de plano ou aguarde reset mensal
3. Configure alertas de uso

### Erro: "Voice not found" (ElevenLabs)

**Solução:**
1. Verifique o `ELEVENLABS_VOICE_ID` no .env
2. Liste vozes disponíveis:
   ```bash
   curl https://api.elevenlabs.io/v1/voices \
     -H "xi-api-key: YOUR_KEY"
   ```

### Erro: "Rate limit exceeded" (OpenRouter)

**Solução:**
1. Implemente retry com exponential backoff (já tem no código)
2. Adicione mais créditos
3. Use fallback model (Gemini)

---

## 🚀 PRÓXIMOS PASSOS

Após configurar todas as APIs:

1. ✅ Testar geração de 1 vídeo manualmente
2. ✅ Validar qualidade do output
3. ✅ Configurar monitoramento de custos
4. ✅ Implementar sistema de queue (Celery)
5. ✅ Deploy em produção

---

## 📞 SUPORTE

- **RunwayML:** support@runwayml.com
- **ElevenLabs:** support@elevenlabs.io
- **OpenRouter:** Discord - https://discord.gg/openrouter

---

**Criado para:** Setup profissional do OMA.AI com stack Runway
**Tempo estimado:** 30-45 minutos
**Dificuldade:** Fácil
**Custo total:** $60-70/mês
