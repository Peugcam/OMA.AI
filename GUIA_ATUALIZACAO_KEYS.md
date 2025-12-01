# 🔐 Guia de Atualização de API Keys - OMA.AI
**Data:** 30 de Novembro de 2025
**Status:** URGENTE - Keys expostas no GitHub público

---

## 📋 CHECKLIST DE SEGURANÇA

### ✅ JÁ FEITO:
- [x] Arquivos com keys removidos do GitHub
- [x] `.gitignore` atualizado
- [x] Código Python verificado (sem keys hardcoded)
- [x] Repositório limpo para compartilhar

### ⚠️ PENDENTE (FAZER AGORA):
- [ ] Revogar todas as API keys antigas
- [ ] Gerar novas API keys
- [ ] Atualizar Google Cloud Run
- [ ] Testar se o site funciona
- [ ] Atualizar arquivo .env local

---

## 🔴 PASSO 1: REVOGAR KEYS ANTIGAS (15 minutos)

### 1.1 OpenRouter
**URL:** https://openrouter.ai/keys

1. Faça login
2. Vá em "API Keys"
3. Encontre a key que termina com `...d629e7d`
4. Clique em "Delete" ou "Revoke"
5. Confirme a remoção

### 1.2 Pexels
**URL:** https://www.pexels.com/api/

1. Faça login
2. Vá em "Your API Key" ou "Settings"
3. Encontre a key: `Mk1ywYiG2x71eJsUv8g1yDzM4V4UPZ3Vkeo6A4DICnDUEEiLP78NoUTv`
4. Clique em "Delete API Key" ou "Regenerate"

### 1.3 ElevenLabs
**URL:** https://elevenlabs.io/app/settings/api-keys

1. Faça login
2. Vá em "Profile" → "API Keys"
3. Encontre a key que termina com `...8a9f`
4. Clique em "Delete" ou "Revoke"

### 1.4 Stability AI
**URL:** https://platform.stability.ai/account/keys

1. Faça login
2. Vá em "API Keys"
3. Encontre a key que termina com `...X2rO`
4. Clique em "Delete" ou "Revoke"

### 1.5 AWS (Se ainda usa)
**URL:** https://console.aws.amazon.com/iam/home#/security_credentials

1. Faça login no AWS Console
2. Vá em "IAM" → "Users" → Seu usuário
3. Aba "Security credentials"
4. Encontre Access Key que começa com `AKIA...`
5. Clique em "Deactivate" e depois "Delete"

### 1.6 EC2 SSH Key
**Local:** Seu computador

```bash
# Delete a chave privada antiga
del C:\Users\paulo\OneDrive\Desktop\OMA_REFACTORED\oma-ec2-key.pem

# No AWS Console:
# EC2 → Key Pairs → oma-ec2-key → Delete
```

---

## 🟢 PASSO 2: GERAR NOVAS KEYS (10 minutos)

### 2.1 OpenRouter (OBRIGATÓRIO)
1. Acesse: https://openrouter.ai/keys
2. Clique em "Create API Key"
3. Nome: `OMA-Video-Prod-2025`
4. **COPIE A KEY** (começa com `sk-or-v1-...`)
5. **Cole aqui temporariamente:**
   ```
   NOVA_OPENROUTER_KEY=sk-or-v1-COLE_AQUI
   ```

### 2.2 Pexels (RECOMENDADO)
1. Acesse: https://www.pexels.com/api/new/
2. Clique em "Generate New API Key"
3. **COPIE A KEY**
4. **Cole aqui:**
   ```
   NOVA_PEXELS_KEY=COLE_AQUI
   ```

### 2.3 ElevenLabs (OPCIONAL)
1. Acesse: https://elevenlabs.io/app/settings/api-keys
2. Clique em "Create new key"
3. Nome: `OMA-Video-2025`
4. **COPIE A KEY**
5. **Cole aqui:**
   ```
   NOVA_ELEVENLABS_KEY=COLE_AQUI
   ```

### 2.4 Stability AI (OPCIONAL)
1. Acesse: https://platform.stability.ai/account/keys
2. Clique em "Create API Key"
3. Nome: `OMA-Video-2025`
4. **COPIE A KEY**
5. **Cole aqui:**
   ```
   NOVA_STABILITY_KEY=COLE_AQUI
   ```

---

## 🔧 PASSO 3: ATUALIZAR GOOGLE CLOUD RUN (5 minutos)

### 3.1 Via Console Web (MAIS FÁCIL)

1. Acesse: https://console.cloud.google.com/run?project=oma-video-prod
2. Clique em `oma-video-generator`
3. Clique em "EDITAR E IMPLANTAR NOVA REVISÃO"
4. Vá até "Variáveis e Secrets" → Aba "Variáveis"
5. Atualize cada variável:
   - `OPENROUTER_API_KEY` = Sua nova key do passo 2.1
   - `PEXELS_API_KEY` = Sua nova key do passo 2.2
   - `ELEVENLABS_API_KEY` = Sua nova key do passo 2.3
   - `STABILITY_API_KEY` = Sua nova key do passo 2.4
6. Clique em "IMPLANTAR"
7. Aguarde 2-5 minutos (deploy automático)

### 3.2 Via Linha de Comando (ALTERNATIVA)

**Copie este comando e SUBSTITUA as keys:**

```bash
export CLOUDSDK_PYTHON="C:/Users/paulo/AppData/Local/Programs/Python/Python313/python.exe"

gcloud run services update oma-video-generator \
  --region=southamerica-east1 \
  --update-env-vars=OPENROUTER_API_KEY=sk-or-v1-COLE_SUA_KEY_AQUI \
  --update-env-vars=PEXELS_API_KEY=COLE_SUA_KEY_AQUI \
  --update-env-vars=ELEVENLABS_API_KEY=COLE_SUA_KEY_AQUI \
  --update-env-vars=STABILITY_API_KEY=COLE_SUA_KEY_AQUI \
  --project=oma-video-prod
```

**Execute no terminal:**
```bash
cd C:\Users\paulo\OneDrive\Desktop\OMA_REFACTORED
# Cole o comando acima (já com suas keys)
```

---

## 🧪 PASSO 4: TESTAR SE FUNCIONA (3 minutos)

### 4.1 Verificar Deploy
```bash
# Verificar status do serviço
gcloud run services describe oma-video-generator \
  --region=southamerica-east1 \
  --project=oma-video-prod \
  --format="get(status.url)"
```

**Você deve ver:** `https://oma-video-generator-...run.app`

### 4.2 Testar no Navegador

1. Abra: [Seu URL do Cloud Run]
2. Tente criar um vídeo de teste
3. Verifique se:
   - ✅ Interface carrega
   - ✅ Consegue enviar prompt
   - ✅ Vídeo é gerado com sucesso

### 4.3 Verificar Logs (Se der erro)

```bash
gcloud run services logs read oma-video-generator \
  --region=southamerica-east1 \
  --project=oma-video-prod \
  --limit=50
```

Procure por erros tipo:
- `❌ Invalid API key` → Key errada, verifique no passo 2
- `❌ Authentication failed` → Formato da key incorreto
- `✅ Video generated successfully` → TUDO OK!

---

## 💾 PASSO 5: ATUALIZAR .ENV LOCAL (2 minutos)

**Seu arquivo local (NÃO vai para Git):**

```bash
cd C:\Users\paulo\OneDrive\Desktop\OMA_REFACTORED
notepad .env
```

**Atualize com as NOVAS keys:**
```env
OPENROUTER_API_KEY=sk-or-v1-NOVA_KEY_AQUI
PEXELS_API_KEY=NOVA_KEY_AQUI
ELEVENLABS_API_KEY=NOVA_KEY_AQUI
STABILITY_API_KEY=NOVA_KEY_AQUI
```

**Salve e feche.**

---

## ✅ PASSO 6: VERIFICAÇÃO FINAL

### Checklist Final:
- [ ] Todas as 4 keys antigas revogadas
- [ ] Novas keys geradas
- [ ] Cloud Run atualizado
- [ ] Site testado e funcionando
- [ ] .env local atualizado
- [ ] **DELETAR ESTE ARQUIVO** após concluir

### Comando para deletar este guia:
```bash
cd C:\Users\paulo\OneDrive\Desktop\OMA_REFACTORED
del GUIA_ATUALIZACAO_KEYS.md
```

---

## 🚨 SE ALGO DER ERRADO:

### Erro: "Invalid API key"
**Solução:** Verifique se copiou a key completa (sem espaços extras)

### Erro: "Service unavailable"
**Solução:** Aguarde 5 minutos, o deploy pode demorar

### Erro: "Permission denied"
**Solução:** Execute:
```bash
gcloud auth login
gcloud config set project oma-video-prod
```

### Site não carrega
**Solução:** Verifique se digitou as keys corretamente no Cloud Run Console

---

## 📞 SUPORTE

Se precisar de ajuda, tenho acesso ao seu projeto e posso:
- Verificar logs do Cloud Run
- Validar se as keys estão configuradas
- Debugar erros de deploy

---

## ⚡ TEMPO ESTIMADO TOTAL: 35 minutos

- Revogar keys: 15 min
- Gerar novas: 10 min
- Atualizar Cloud Run: 5 min
- Testar: 3 min
- Atualizar local: 2 min

---

**BOA SORTE! 🚀**

Depois de concluir, seu projeto estará 100% seguro para compartilhar no LinkedIn/X!
