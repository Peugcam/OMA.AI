# 🚀 Guia de Setup - OMA v3.0 (Zero Problemas)

## 📋 Checklist Antes de Começar

Verifique se você tem:
- [ ] Windows 10/11 (64-bit)
- [ ] 16GB RAM (mínimo 8GB)
- [ ] 20GB espaço em disco livre
- [ ] Python 3.11+ instalado
- [ ] Conexão com internet (para download inicial)

---

## 🎯 Setup em 5 Passos (30 minutos)

### ✅ PASSO 1: Verificar Python (2 min)

```bash
# Abrir PowerShell ou CMD
python --version
```

**Deve mostrar:** `Python 3.11.x` ou superior

**Se não tiver Python ou versão antiga:**
```bash
# Baixar Python 3.11+
# https://www.python.org/downloads/
# ⚠️ IMPORTANTE: Marcar "Add Python to PATH" durante instalação
```

---

### ✅ PASSO 2: Instalar Ollama (5 min)

```bash
# Opção 1: Usando winget (Windows 11)
winget install Ollama.Ollama

# Opção 2: Download manual
# https://ollama.com/download/windows
# Baixar e instalar o .exe
```

**Verificar instalação:**
```bash
ollama --version
```

**Iniciar serviço Ollama:**
```bash
# Ollama inicia automaticamente, mas se não estiver rodando:
ollama serve
```

**Deve aparecer:** `Ollama is running on http://localhost:11434`

---

### ✅ PASSO 3: Baixar Modelos SLM (15 min - DOWNLOAD)

```bash
# ⚠️ ATENÇÃO: Vai baixar ~11GB total
# Certifique-se que tem espaço em disco

# 1. Supervisor (2.4GB)
ollama pull qwen2.5:3b-instruct

# 2. Script Writer (2.4GB)
ollama pull phi3.5:3.8b-mini

# 3. Visual Planner (1.6GB)
ollama pull gemma2:2b

# 4. Audio Producer (4.1GB)
ollama pull mistral:7b-instruct

# 5. Editor (934MB)
ollama pull qwen2:1.5b
```

**Verificar modelos instalados:**
```bash
ollama list
```

**Deve mostrar:**
```
NAME                      SIZE
qwen2.5:3b-instruct      2.4 GB
phi3.5:3.8b-mini         2.4 GB
gemma2:2b                1.6 GB
mistral:7b-instruct      4.1 GB
qwen2:1.5b               934 MB
```

---

### ✅ PASSO 4: Instalar FFmpeg (3 min)

**Opção 1: Usando Chocolatey (Recomendado)**
```bash
# Instalar Chocolatey (se não tiver)
# https://chocolatey.org/install

# Depois:
choco install ffmpeg
```

**Opção 2: Download Manual**
```bash
# 1. Baixar: https://www.gyan.dev/ffmpeg/builds/
# 2. Escolher: ffmpeg-release-essentials.zip
# 3. Extrair para: C:\ffmpeg
# 4. Adicionar ao PATH:
#    - Abrir: Variáveis de Ambiente
#    - Editar PATH
#    - Adicionar: C:\ffmpeg\bin
```

**Verificar instalação:**
```bash
ffmpeg -version
```

---

### ✅ PASSO 5: Instalar Dependências Python (5 min)

```bash
# Navegar para pasta do projeto
cd C:\Users\paulo\OneDrive\Desktop\OMA_REFACTORED

# Criar ambiente virtual (RECOMENDADO)
python -m venv venv

# Ativar ambiente virtual
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Windows CMD:
venv\Scripts\activate.bat

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🧪 TESTE RÁPIDO (Verificar se tudo funciona)

### Teste 1: Ollama funcionando

```bash
# Testar modelo supervisor
ollama run qwen2.5:3b-instruct "Olá, você está funcionando?"
```

**Deve responder em português.**

### Teste 2: FFmpeg funcionando

```bash
ffmpeg -version
```

**Deve mostrar versão e configuração.**

### Teste 3: Python imports

```bash
python -c "import ollama; print('Ollama: OK')"
python -c "import ffmpeg; print('FFmpeg: OK')"
python -c "import gradio; print('Gradio: OK')"
```

**Todos devem imprimir "OK"**

---

## 🎬 RODAR INTERFACE

### Opção 1: Gradio (Simples)

```bash
python ui_gradio.py
```

**Acesse:** http://localhost:7860

### Opção 2: Streamlit (Dashboard)

```bash
streamlit run ui_streamlit.py
```

**Acesse:** http://localhost:8501

---

## 🐛 Troubleshooting - Problemas Comuns

### ❌ Erro: "ollama: command not found"

**Solução:**
```bash
# Verificar se Ollama está no PATH
where ollama

# Se não encontrar, adicionar manualmente:
# C:\Users\<seu_usuario>\AppData\Local\Programs\Ollama
```

---

### ❌ Erro: "Failed to connect to Ollama"

**Solução:**
```bash
# 1. Verificar se serviço está rodando
# Windows: Abrir Task Manager → Procurar "ollama"

# 2. Se não estiver, iniciar:
ollama serve

# 3. Testar conexão:
curl http://localhost:11434/api/version
```

---

### ❌ Erro: "ffmpeg: command not found"

**Solução:**
```bash
# 1. Reinstalar FFmpeg
choco install ffmpeg -y

# 2. Ou adicionar ao PATH manualmente
# Painel de Controle → Sistema → Variáveis de Ambiente
# Adicionar: C:\ffmpeg\bin ao PATH
```

---

### ❌ Erro: "Model not found"

**Solução:**
```bash
# Baixar modelo novamente
ollama pull qwen2.5:3b-instruct

# Verificar se baixou
ollama list
```

---

### ❌ Erro: "Out of memory"

**Causa:** Pouca RAM para rodar todos os modelos

**Solução 1 (Temporária):**
```python
# Editar config/models.yaml
# Comentar modelos maiores:
# - mistral:7b-instruct  # 4.1GB
# Usar apenas os menores (total ~7GB)
```

**Solução 2 (Permanente):**
```bash
# Adicionar mais RAM ou
# Usar apenas 1 modelo por vez (descarregar após uso)
ollama stop mistral:7b-instruct
```

---

### ❌ Erro: "ModuleNotFoundError: No module named 'X'"

**Solução:**
```bash
# Reinstalar dependências
pip install -r requirements.txt --force-reinstall

# Ou instalar módulo específico
pip install nome-do-modulo
```

---

### ❌ Gradio não abre no navegador

**Solução:**
```bash
# Abrir manualmente:
# http://localhost:7860

# Ou verificar porta em uso:
netstat -ano | findstr :7860

# Mudar porta se necessário:
demo.launch(server_port=7861)
```

---

## 📊 Requirements Completo

Crie arquivo `requirements.txt`:

```txt
# Core
ollama==0.3.3
python-dotenv==1.0.0

# Multi-Agent Framework
langgraph==0.2.28
langchain==0.3.0
langchain-community==0.3.0

# LLM Utils
tiktoken==0.7.0
pydantic==2.9.0

# Media Processing
ffmpeg-python==0.2.0
pillow==10.4.0
opencv-python==4.10.0

# TTS (Local)
TTS==0.22.0
pydub==0.25.1

# Vector Store
chromadb==0.5.5
sentence-transformers==3.1.0

# Web Interfaces
gradio==4.44.0
streamlit==1.38.0
plotly==5.24.0

# API
fastapi==0.115.0
uvicorn[standard]==0.30.6
httpx==0.27.2

# Utils
tqdm==4.66.5
python-multipart==0.0.9
```

**Instalar tudo:**
```bash
pip install -r requirements.txt
```

---

## 🎯 Verificação Final

Execute este script de teste:

```python
# test_setup.py
import sys

def test_imports():
    tests = {
        "ollama": False,
        "gradio": False,
        "langchain": False,
        "ffmpeg": False,
        "chromadb": False,
        "TTS": False
    }

    for module in tests.keys():
        try:
            __import__(module)
            tests[module] = True
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - FALTANDO")

    # Verificar Ollama
    try:
        import ollama
        client = ollama.Client()
        models = client.list()
        print(f"\n✅ Ollama conectado: {len(models['models'])} modelos")
    except:
        print(f"\n❌ Ollama não conectado")

    # Verificar FFmpeg
    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg instalado")
        else:
            print("❌ FFmpeg com erro")
    except FileNotFoundError:
        print("❌ FFmpeg não encontrado")

    all_ok = all(tests.values())
    if all_ok:
        print("\n🎉 TUDO PRONTO! Você pode começar a usar o OMA v3.0")
    else:
        print("\n⚠️ Alguns módulos faltando. Instale com:")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    test_imports()
```

**Rodar:**
```bash
python test_setup.py
```

---

## 🆘 Ajuda Extra

Se ainda tiver problemas:

1. **Discord:** discord.gg/oma-community
2. **GitHub Issues:** github.com/Peugcam/OMA_v3/issues
3. **Email:** support@oma.ai

---

## 📝 Checklist Final

Antes de usar o sistema, confirme:

- [ ] Python 3.11+ instalado e funcionando
- [ ] Ollama instalado e rodando (`ollama serve`)
- [ ] 5 modelos SLM baixados (`ollama list`)
- [ ] FFmpeg instalado (`ffmpeg -version`)
- [ ] Dependências Python instaladas (`pip list`)
- [ ] Teste de imports passou (`python test_setup.py`)
- [ ] Interface abre no navegador

**Se todos marcados: VOCÊ ESTÁ PRONTO! 🚀**

---

## 🎬 Primeiro Vídeo

```bash
# Iniciar interface
python ui_gradio.py

# Ou
streamlit run ui_streamlit.py

# Criar seu primeiro vídeo teste:
# Descrição: "Propaganda para cafeteria"
# Duração: 30s
# Clicar em "Criar Vídeo"
```

**Tempo esperado:** 4-6 minutos

---

**Boa sorte! 🍀**
