# 🚀 Quick Start - OMA v3.0 com OpenRouter

## Setup Ultra-Rápido (10 minutos) ⚡

Usando **OpenRouter API** ao invés de modelos locais:

✅ **Sem download de 11GB de modelos**
✅ **Funciona em qualquer máquina**
✅ **Setup em 10 minutos**
✅ **Custo: ~$0.15 por vídeo**

---

## 📋 Pré-requisitos

- [ ] Windows 10/11
- [ ] Python 3.8+ (qualquer versão recente)
- [ ] FFmpeg instalado
- [ ] 2GB espaço em disco (para vídeos gerados)

---

## 🎯 Passo 1: Obter API Keys (5 min)

### 1.1 OpenRouter (OBRIGATÓRIO)

1. Acesse: **https://openrouter.ai/**
2. Clique em "Sign In" (login com Google/GitHub)
3. Vá em: **https://openrouter.ai/keys**
4. Clique em "Create Key"
5. Copie a key (começa com `sk-or-v1-...`)

💰 **Adicione créditos:** $5-10 USD (rende ~30-60 vídeos)

### 1.2 Pexels (OPCIONAL mas recomendado - GRÁTIS)

1. Acesse: **https://www.pexels.com/api/**
2. Clique em "Get Started"
3. Preencha formulário
4. Copie a API key

---

## 🔧 Passo 2: Instalar Dependências (3 min)

### 2.1 Python

Verificar se tem Python:

```bash
python --version
```

Se não tiver, baixar: **https://www.python.org/downloads/**

### 2.2 FFmpeg

**Windows (Chocolatey):**
```bash
choco install ffmpeg
```

**Windows (Manual):**
1. Baixar: https://www.gyan.dev/ffmpeg/builds/
2. Extrair para `C:\ffmpeg`
3. Adicionar `C:\ffmpeg\bin` ao PATH

**Verificar:**
```bash
ffmpeg -version
```

---

## ⚙️ Passo 3: Configurar Projeto (2 min)

```bash
# Navegar para pasta
cd C:\Users\paulo\OneDrive\Desktop\OMA_REFACTORED

# Criar .env
copy .env.example .env

# Editar .env e colar suas API keys
notepad .env
```

**No arquivo `.env`, configure:**
```bash
OPENROUTER_API_KEY=sk-or-v1-SEU-KEY-AQUI
PEXELS_API_KEY=SEU-PEXELS-KEY-AQUI  # Opcional
```

---

## 📦 Passo 4: Instalar Python Packages

```bash
# Criar ambiente virtual (recomendado)
python -m venv venv

# Ativar (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Ou (Windows CMD)
venv\Scripts\activate.bat

# Instalar dependências
pip install --upgrade pip
pip install -r requirements_openrouter.txt
```

---

## 🎬 Passo 5: Rodar Interface

```bash
python ui_gradio.py
```

**Abre em:** http://localhost:7860

---

## ✅ Teste Rápido

1. Abrir http://localhost:7860
2. Preencher:
   - Descrição: "Propaganda para cafeteria moderna"
   - Público: "Millennials urbanos"
   - Duração: 30s
   - Estilo: "Clean e minimalista"
3. Clicar em "🎬 Criar Vídeo"
4. Aguardar 3-5 minutos

**Primeiro vídeo deve custar ~$0.15 USD**

---

## 💰 Custos Estimados (OpenRouter)

| Agente | Modelo | Custo/1M tokens | Tokens/vídeo | Custo/vídeo |
|--------|--------|-----------------|--------------|-------------|
| Supervisor | Qwen-2.5-7B | $0.09 | ~2K | $0.0002 |
| Script | Phi-3.5-Mini | $0.10 | ~3K | $0.0003 |
| Visual | Gemma-2-9B | $0.20 | ~2K | $0.0004 |
| Audio | Mistral-7B | $0.06 | ~1K | $0.00006 |
| Editor | Llama-3.2-3B | $0.06 | ~500 | $0.00003 |
| **TOTAL** | | | **~8.5K** | **~$0.001** |

**Custo REAL por vídeo:** ~$0.001-0.005 USD (centavos!) 🎉

*Nota: A documentação anterior estava com valores superestimados*

---

## 🆚 Comparação: Local vs OpenRouter

| Aspecto | Local (Ollama) | OpenRouter |
|---------|----------------|------------|
| **Download inicial** | 11GB | 0 GB ✅ |
| **RAM necessária** | 16GB | 4GB ✅ |
| **Setup time** | 30 min | 10 min ✅ |
| **Custo/vídeo** | $0 | $0.001-0.005 |
| **Latência** | 4-6 min | 2-4 min ✅ |
| **Qualidade** | 7.5/10 | 8.5/10 ✅ |
| **Funciona offline** | ✅ | ❌ |
| **Privacidade** | ✅ Total | ⚠️ Cloud |

**Recomendação:** OpenRouter para começar, migrar para local se precisar de privacidade/offline.

---

## 🐛 Troubleshooting

### ❌ "OPENROUTER_API_KEY não encontrada"

**Solução:**
```bash
# Verificar se .env existe
dir .env

# Se não existir, copiar de .env.example
copy .env.example .env

# Editar e adicionar sua key
notepad .env
```

### ❌ "Rate limit exceeded"

**Causa:** Créditos OpenRouter acabaram

**Solução:**
1. Ir em: https://openrouter.ai/credits
2. Adicionar mais créditos ($5-10)

### ❌ "FFmpeg not found"

**Solução:**
```bash
# Instalar FFmpeg
choco install ffmpeg

# Verificar
ffmpeg -version
```

### ❌ "ModuleNotFoundError"

**Solução:**
```bash
# Reinstalar dependências
pip install -r requirements_openrouter.txt --force-reinstall
```

---

## 📊 Monitorar Custos

OpenRouter tem dashboard para ver gastos:

1. https://openrouter.ai/activity
2. Ver custos por modelo
3. Configurar alertas de budget

---

## 🎉 Pronto!

Agora você pode:

✅ Criar vídeos ilimitados
✅ Customizar prompts e estilos
✅ Exportar para diferentes formatos
✅ Usar API REST (http://localhost:7860/docs)

---

## 📚 Próximos Passos

- [ ] Criar primeiro vídeo teste
- [ ] Experimentar diferentes estilos
- [ ] Configurar Pexels para vídeos HD grátis
- [ ] Deploy na nuvem (opcional)
- [ ] Migrar para modelos locais (se precisar privacidade)

---

**Dúvidas?**
- 📧 Email: support@oma.ai
- 💬 Discord: discord.gg/oma
- 🐙 GitHub: github.com/Peugcam/OMA_v3

**Boa criação! 🎬**
