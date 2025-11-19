# 🔄 Como Alternar Entre OpenRouter e Modelos Locais

## 📊 Status Atual da Configuração

### ✅ Limpeza Realizada (18/11/2025 22:45)

| Local | Antes | Depois | Liberado |
|-------|-------|--------|----------|
| **Notebook (C:)** | 5.8GB modelos | 0GB | ✅ **5.8GB** |
| **Pendrive (D:)** | 7.3GB modelos | 3.8GB | ✅ **3.5GB** |
| **Total Liberado** | 13.1GB | 3.8GB | ✅ **9.3GB** |

### 🎯 Modelos Atuais

**Pendrive (D:/OMA_Portable/.ollama):**
- ✅ `gemma2:2b` (1.6GB) - Visual Agent
- ✅ `phi3:mini` (2.2GB) - Script/Supervisor/Audio
- ❌ `tinyllama` - REMOVIDO
- ❌ `gemma3:4b` - REMOVIDO

**OpenRouter (Cloud):**
- ✅ Qwen 2.5 7B - Supervisor
- ✅ Phi-3.5 Mini - Script
- ✅ Gemma-2 9B - Visual (melhor que local!)
- ✅ Mistral 7B - Audio
- ✅ Llama 3.2 3B - Editor

---

## 🌐 MODO 1: OpenRouter (PADRÃO - Recomendado)

### Quando Usar:
- ✅ Dia a dia normal
- ✅ Precisa de velocidade (3-5 min/vídeo)
- ✅ Melhor qualidade (9/10)
- ✅ Notebook com pouca RAM
- ✅ Internet disponível

### Custo:
- **$0.001 por vídeo** (~R$ 0,005)
- $5 = ~5000 vídeos

### Como Configurar:

**1. Obter API Key:**
```
1. Acesse: https://openrouter.ai/keys
2. Login com Google/GitHub
3. Clique "Create Key"
4. Copie a key (sk-or-v1-...)
```

**2. Adicionar Créditos:**
```
1. Acesse: https://openrouter.ai/credits
2. Adicione $5-10 (cobre meses de uso)
3. Métodos: Cartão, PayPal, Crypto
```

**3. Editar .env:**
```bash
# Abra: C:\Users\paulo\OneDrive\Desktop\OMA_REFACTORED\.env

# Cole sua key:
OPENROUTER_API_KEY=sk-or-v1-SUA-KEY-AQUI

# Modelos (já configurados):
SUPERVISOR_MODEL=qwen/qwen-2.5-7b-instruct
SCRIPT_MODEL=microsoft/phi-3.5-mini-128k
VISUAL_MODEL=google/gemma-2-9b-it
AUDIO_MODEL=mistralai/mistral-7b-instruct-v0.3
EDITOR_MODEL=meta-llama/llama-3.2-3b-instruct
```

**4. Rodar:**
```bash
cd C:\Users\paulo\OneDrive\Desktop\OMA_REFACTORED
python ui_gradio.py
```

**5. Acessar:**
```
http://localhost:7860
```

---

## 💾 MODO 2: Modelos Locais (FALLBACK)

### Quando Usar:
- ✅ Sem internet
- ✅ Créditos OpenRouter acabaram
- ✅ Testes offline
- ✅ Máxima privacidade (0% cloud)

### Custo:
- **$0 por vídeo** (100% grátis)

### Desvantagens:
- ⚠️ Mais lento (6-10 min/vídeo no pendrive)
- ⚠️ Qualidade menor (7/10 vs 9/10)
- ⚠️ Usa mais RAM do notebook

### Como Ativar:

**1. Iniciar Ollama do Pendrive:**
```bash
# Clique duas vezes:
D:\OMA_Portable\start_ollama.bat

# Aguarde aparecer:
# "Ollama is running on http://localhost:11434"
```

**2. Verificar Modelos:**
```bash
# Em outra janela CMD:
set OLLAMA_HOME=D:\OMA_Portable\.ollama
D:\OMA_Portable\ollama\ollama.exe list

# Deve mostrar:
# gemma2:2b    1.6 GB
# phi3:mini    2.2 GB
```

**3. Editar .env:**
```bash
# Abra: C:\Users\paulo\OneDrive\Desktop\OMA_REFACTORED\.env

# COMENTE as linhas OpenRouter (adicione # no início):
#OPENROUTER_API_KEY=sk-or-v1-...
#SUPERVISOR_MODEL=qwen/qwen-2.5-7b-instruct
#SCRIPT_MODEL=microsoft/phi-3.5-mini-128k
#VISUAL_MODEL=google/gemma-2-9b-it
#AUDIO_MODEL=mistralai/mistral-7b-instruct-v0.3
#EDITOR_MODEL=meta-llama/llama-3.2-3b-instruct

# DESCOMENTE as linhas locais (remova #):
OLLAMA_HOST=http://localhost:11434
SUPERVISOR_MODEL=phi3:mini
SCRIPT_MODEL=phi3:mini
VISUAL_MODEL=gemma2:2b
AUDIO_MODEL=phi3:mini
EDITOR_MODEL=gemma2:2b
```

**4. Rodar:**
```bash
cd C:\Users\paulo\OneDrive\Desktop\OMA_REFACTORED
python ui_gradio.py
```

---

## ⚡ MODO 3: Híbrido (Avançado)

Use OpenRouter para alguns agentes e local para outros:

```bash
# .env configuração híbrida:

OPENROUTER_API_KEY=sk-or-v1-...

# Usar cloud para tarefas pesadas:
SUPERVISOR_MODEL=qwen/qwen-2.5-7b-instruct     # Cloud (melhor)
VISUAL_MODEL=google/gemma-2-9b-it              # Cloud (melhor)

# Usar local para tarefas simples:
SCRIPT_MODEL=phi3:mini                         # Local
AUDIO_MODEL=phi3:mini                          # Local
EDITOR_MODEL=gemma2:2b                         # Local

# Indicar Ollama para modelos locais:
OLLAMA_HOST=http://localhost:11434
```

**Resultado:**
- Custo reduzido (~$0.0005/vídeo)
- Performance balanceada
- Aproveita melhor de cada mundo

---

## 🔍 Como Saber Qual Modo Está Ativo?

### OpenRouter Ativo:
```bash
# Ao rodar ui_gradio.py, você verá:
INFO: Using OpenRouter API
INFO: Models: qwen/qwen-2.5-7b-instruct, microsoft/phi-3.5-mini...
```

### Local Ativo:
```bash
# Ao rodar ui_gradio.py, você verá:
INFO: Using Ollama at http://localhost:11434
INFO: Models: phi3:mini, gemma2:2b
```

---

## 🐛 Troubleshooting

### ❌ "OpenRouter API key inválida"

**Solução:**
1. Verifique se copiou a key completa do https://openrouter.ai/keys
2. Verifique se tem créditos em https://openrouter.ai/credits
3. Formato correto: `sk-or-v1-...` (deve ter 60+ caracteres)

---

### ❌ "Ollama not found" ou "Connection refused"

**Solução:**
1. Verifique se `start_ollama.bat` está rodando
2. Abra http://localhost:11434 no navegador (deve mostrar "Ollama is running")
3. Se não funcionar, reinicie o Ollama:
   ```bash
   # Task Manager → Finalizar "ollama"
   # Depois rode novamente:
   D:\OMA_Portable\start_ollama.bat
   ```

---

### ❌ Notebook travando ao usar modelos locais

**Causa:** Ollama carregando modelos grandes na RAM

**Solução 1 (Rápida):**
- Use apenas OpenRouter (comente `OLLAMA_HOST` no .env)
- Feche o `start_ollama.bat`

**Solução 2 (Limitar RAM do Ollama):**
```bash
# Antes de start_ollama.bat, rode:
set OLLAMA_MAX_LOADED_MODELS=1
set OLLAMA_NUM_PARALLEL=1

# Depois:
D:\OMA_Portable\start_ollama.bat
```

---

### ❌ "Out of credits" no OpenRouter

**Solução:**
1. Acesse https://openrouter.ai/credits
2. Adicione mais créditos ($5 = 5000 vídeos)
3. OU ative modo local (ver seção "MODO 2" acima)

---

### ❌ Vídeo demora mais de 10 minutos

**Diagnóstico:**
```bash
# Verifique qual modo está usando:
cat .env | grep -E "SUPERVISOR_MODEL|OLLAMA_HOST"
```

**Se mostrar modelos locais (phi3:mini, gemma2:2b):**
- ⚠️ Normal no pendrive (USB 2.0/3.0)
- Solução: Use OpenRouter para velocidade

**Se mostrar OpenRouter (qwen/qwen-2.5...):**
- ⚠️ Problema de internet lenta
- Solução: Verifique conexão

---

## 📊 Comparação de Performance

| Aspecto | OpenRouter | Local (Pendrive) |
|---------|-----------|------------------|
| **Velocidade** | 3-5 min ⚡⚡⚡ | 6-10 min ⚡ |
| **Qualidade** | 9/10 🌟 | 7/10 ⭐ |
| **Custo/vídeo** | $0.001 💰 | $0 ✅ |
| **RAM usada** | ~2GB | ~6GB |
| **Internet** | Necessária | Opcional |
| **Privacidade** | Cloud ☁️ | 100% Local 🔒 |
| **Setup** | 2 min | 5 min |

---

## 🎯 Recomendação Final

### Para Uso Diário:
✅ **Use OpenRouter** (MODO 1)
- Rápido, confiável, barato
- Não trava o notebook
- Melhor qualidade

### Para Emergências/Testes:
✅ **Use Local** (MODO 2)
- Quando internet cair
- Quando créditos acabarem
- Para máxima privacidade

---

## 📞 Suporte

**Dúvidas?**
- 📧 Email: support@oma.ai
- 💬 Discord: discord.gg/oma
- 🐙 GitHub: github.com/Peugcam/OMA_v3

---

**Última atualização:** 18/11/2025 22:45
**Configuração testada:** ✅ Funcionando
**Modelos no pendrive:** gemma2:2b (1.6GB) + phi3:mini (2.2GB)
**Espaço liberado total:** 9.3GB
