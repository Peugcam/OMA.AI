# 🔍 Guia de Debug - Dashboard de Geração de Vídeos

## Problema Reportado

**Sintoma:** Dashboard continua gerando vídeos de "auto-ajuda" mesmo quando outros templates são selecionados.

## 🔧 Correções Aplicadas

### 1. Debug Logging Adicionado

**Arquivos Modificados:**
- `video_dashboard_complete.py` - linha 225
- `quick_generate.py` - linha 34

**O que foi adicionado:**
```python
# Printar briefing completo antes de enviar
print("🎬 BRIEFING RECEBIDO:")
print(json.dumps(briefing, indent=2, ensure_ascii=False))
```

### 2. Verificação de Paths para Vídeos

**Arquivo:** `video_dashboard_complete.py` - linha 646

**Correção:**
```python
allowed_paths=[
    "C:\\Users\\paulo\\OneDrive\\Desktop\\OMA_Videos",
    "outputs/videos",
    "."
]
```

## 🧪 Como Testar e Debugar

### Passo 1: Reiniciar Dashboard

```bash
# Parar dashboard atual (Ctrl+C no terminal)

# Iniciar novamente
cd OMA_REFACTORED
py -3 video_dashboard_complete.py
```

### Passo 2: Gerar Vídeo com Template

1. Abra http://localhost:7861
2. **Selecione template** no dropdown (ex: "Produto Tech")
3. **IMPORTANTE:** Aguarde os campos preencherem automaticamente
4. Clique em "Gerar Vídeo"

### Passo 3: Observar Logs no Terminal

Você deverá ver algo assim:

```
============================================================
🎬 BRIEFING RECEBIDO:
============================================================
{
  "title": "Lançamento de Produto Inovador",
  "description": "Vídeo de apresentação de produto tecnológico...",
  "duration": 30,
  "target_audience": "Profissionais de tecnologia",
  "style": "modern",
  "tone": "enthusiastic",
  "cta": "Experimente grátis agora!"
}
============================================================

======================================================================
📥 QUICK_GENERATE - Briefing Recebido:
======================================================================
{
  "title": "Lançamento de Produto Inovador",
  "description": "Vídeo de apresentação de produto tecnológico...",
  ...
}
======================================================================
```

### Passo 4: Verificar Se o Briefing Está Correto

**✅ Correto:** O título e descrição correspondem ao template selecionado

**❌ Incorreto:** Se aparecer "OMA - Produtividade com IA" ou "auto-ajuda"

## 🐛 Possíveis Causas do Problema

### 1. Template Não Está Sendo Aplicado

**Causa:** O JavaScript do Gradio pode não estar atualizando os campos

**Solução:**
- Aguarde 2-3 segundos após selecionar o template
- Verifique visualmente se os campos mudaram
- Se não mudaram, preencha manualmente

### 2. Briefing Hardcoded em Algum Agente

**Verificação:**
```bash
cd OMA_REFACTORED
grep -r "Produtividade com IA" --include="*.py"
grep -r "auto.ajuda" --include="*.py"
```

**Se encontrar em:**
- `generate_full_video.py` - **NORMAL** (é o padrão deste arquivo)
- Qualquer arquivo em `agents/` - **PROBLEMA**

### 3. Agente Ignorando o Briefing

**Arquivos a verificar:**
- `agents/supervisor_agent.py`
- `agents/script_agent.py`

**O que procurar:**
```python
# ❌ ERRADO - briefing hardcoded
brief = {
    "title": "OMA - Produtividade",
    ...
}

# ✅ CORRETO - usa briefing do state
brief = state.get("brief", {})
description = brief.get("description", "")
```

## 🔍 Análise do Fluxo Completo

### Fluxo Esperado:

```
1. Dashboard (video_dashboard_complete.py)
   ↓
   Cria briefing customizado do template
   ↓
2. quick_generate.py
   ↓
   Recebe briefing via parâmetro
   ↓
   Coloca briefing no state
   ↓
3. SupervisorAgent
   ↓
   Lê briefing do state
   ↓
   Analisa e extrai informações
   ↓
4. ScriptAgent
   ↓
   Lê análise E briefing original do state
   ↓
   Gera roteiro baseado nas informações
   ↓
5. VisualAgent → AudioAgent → EditorAgent
   ↓
   Cada um usa informações do state
   ↓
6. Vídeo Final
```

### Onde Pode Dar Errado:

**❌ Ponto de Falha 1:** Dashboard não cria briefing correto
- **Debug:** Ver logs "🎬 BRIEFING RECEBIDO"

**❌ Ponto de Falha 2:** quick_generate não recebe o briefing
- **Debug:** Ver logs "📥 QUICK_GENERATE"

**❌ Ponto de Falha 3:** Agente usa briefing hardcoded
- **Debug:** Adicionar prints nos agentes

## 🛠️ Como Adicionar Mais Debug

### No Supervisor Agent

```python
# No arquivo agents/supervisor_agent.py
async def analyze_request(self, state: Dict[str, Any]) -> Dict[str, Any]:
    # Adicionar no início:
    brief = state.get("brief", {})
    print(f"\n🧠 SUPERVISOR - Analisando briefing:")
    print(f"   Título: {brief.get('title', 'N/A')}")
    print(f"   Descrição: {brief.get('description', 'N/A')[:100]}...")
```

### No Script Agent

```python
# No arquivo agents/script_agent.py
async def generate_script(self, state: Dict[str, Any]) -> Dict[str, Any]:
    # Adicionar no início:
    brief = state.get("brief", {})
    print(f"\n📝 SCRIPT AGENT - Gerando roteiro para:")
    print(f"   Título: {brief.get('title', 'N/A')}")
    print(f"   Estilo: {brief.get('style', 'N/A')}")
```

## ✅ Checklist de Verificação

Antes de gerar um novo vídeo:

- [ ] Dashboard está rodando (porta 7861)
- [ ] Selecionou template no dropdown
- [ ] **Aguardou campos preencherem**
- [ ] Verificou que o título mudou
- [ ] Verificou que a descrição mudou
- [ ] Terminal está visível para ver logs
- [ ] Clicou em "Gerar Vídeo"
- [ ] Viu logs "🎬 BRIEFING RECEBIDO" no terminal
- [ ] Briefing nos logs está correto

## 📊 Exemplo de Log Esperado

### Se Tudo Estiver Funcionando:

```
============================================================
🎬 BRIEFING RECEBIDO:
============================================================
{
  "title": "Lançamento de Produto Inovador",
  "description": "Vídeo de apresentação de produto tecnológico inovador.\n\n**ESTRUTURA:**\n- Abertura impactante...",
  "duration": 30,
  "target_audience": "Profissionais de tecnologia, early adopters",
  "style": "modern",
  "tone": "enthusiastic",
  "cta": "Experimente grátis agora!"
}
============================================================

======================================================================
📥 QUICK_GENERATE - Briefing Recebido:
======================================================================
{
  "title": "Lançamento de Produto Inovador",
  ...
}
======================================================================

📊 Estado inicial criado: task_id=video_20251120_095030
📋 Briefing no state: Lançamento de Produto Inovador
```

### Se Houver Problema:

```
============================================================
🎬 BRIEFING RECEBIDO:
============================================================
{
  "title": "OMA - Produtividade com IA",   ← ❌ ERRADO!
  "description": "Anúncio moderno...",
  ...
}
```

## 🎯 Próximos Passos

1. **Reinicie o dashboard** com os logs de debug
2. **Teste com template "Redes Sociais"** (mais rápido)
3. **Observe os logs** no terminal
4. **Se o briefing estiver errado nos logs:**
   - O problema é no dashboard (JavaScript não está atualizando)
   - Solução temporária: Preencher manualmente
5. **Se o briefing estiver correto nos logs mas vídeo errado:**
   - O problema é em algum agente
   - Adicionar mais debug nos agentes

## 📞 Report de Bug

Se o problema persistir, capture e envie:

1. Screenshot do dashboard com template selecionado
2. Logs completos do terminal
3. Vídeo gerado (para análise do conteúdo)

---

**Atualizado:** 2025-11-20
**Status:** Debug ativo
