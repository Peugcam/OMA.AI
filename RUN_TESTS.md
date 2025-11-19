# 🧪 Como Executar os Testes do Fluxo Híbrido

## 📋 Pré-requisitos

Antes de rodar os testes, certifique-se de ter:

### 1. ✅ API Keys Configuradas

Abra seu arquivo `.env` e verifique:

```bash
# OpenRouter (obrigatório)
OPENROUTER_API_KEY=sk-or-v1-xxxxx

# Pexels (obrigatório para teste híbrido)
PEXELS_API_KEY=xxxxx

# Stability AI (obrigatório para teste híbrido)
STABILITY_API_KEY=sk-xxxxx
```

**Onde conseguir as keys:**
- OpenRouter: https://openrouter.ai/keys
- Pexels: https://www.pexels.com/api/ (GRÁTIS)
- Stability AI: https://platform.stability.ai/

---

## 🚀 Como Executar

### Opção 1: Via Terminal/CMD

```bash
# Navegar para a pasta do projeto
cd C:\Users\paulo\OneDrive\Desktop\OMA_REFACTORED

# Executar testes
python test_hybrid_videos.py
```

### Opção 2: Via VS Code

1. Abrir `test_hybrid_videos.py` no VS Code
2. Clicar com botão direito no arquivo
3. Selecionar "Run Python File in Terminal"

### Opção 3: Via Python Diretamente

```bash
# No diretório do projeto
python -m test_hybrid_videos
```

---

## 🎬 O Que os Testes Fazem

### Teste 1: Vídeo Corporativo

**Brief:** "OMA.AI - Plataforma de Criação de Vídeos"

**Cenas esperadas:**
```
Cena 1: "Pessoa frustrada tentando criar vídeo"
→ Classificação esperada: pexels (tem pessoa)
→ Busca Pexels: pessoa frustrada, escritório
→ Custo: $0.00

Cena 2: "Logo OMA.AI holográfico impactante"
→ Classificação esperada: stability (logo específico)
→ Gera com Stability AI
→ Custo: $0.04

Cena 3: "Equipe feliz usando a plataforma"
→ Classificação esperada: pexels (pessoas, expressões)
→ Busca Pexels: equipe feliz, escritório
→ Custo: $0.00

CUSTO TOTAL ESPERADO: ~$0.04
TAXA PEXELS ESPERADA: ~67% (2/3 cenas)
```

### Teste 2: Vídeo Tech/Abstrato

**Brief:** "Futuro da IA - Inovação Tecnológica"

**Cenas esperadas:**
```
Cena 1: "Cientista de dados analisando código"
→ Classificação esperada: pexels (pessoa trabalhando)
→ Busca Pexels: data scientist, coding
→ Custo: $0.00

Cena 2: "Cérebro digital com redes neurais holográficas"
→ Classificação esperada: stability (conceito abstrato)
→ Gera com Stability AI
→ Custo: $0.04

Cena 3: "Desenvolvedores colaborando"
→ Classificação esperada: pexels (grupo de pessoas)
→ Busca Pexels: developers team collaboration
→ Custo: $0.00

Cena 4: "Visualização abstrata de algoritmos"
→ Classificação esperada: stability (visualização abstrata)
→ Gera com Stability AI
→ Custo: $0.04

CUSTO TOTAL ESPERADO: ~$0.08
TAXA PEXELS ESPERADA: ~50% (2/4 cenas)
```

---

## 📊 O Que Observar nos Resultados

### 1. Classificação Automática

Verifique se o LLM classificou corretamente:

```
✅ BOM:
- "Pessoa sorrindo" → pexels
- "Logo 3D holográfico" → stability
- "Reunião de equipe" → pexels
- "Visualização abstrata" → stability

❌ RUIM:
- "Pessoa sorrindo" → stability (ERRADO! Stability é horrível com rostos)
- "Logo específico" → pexels (não vai achar no Pexels)
```

### 2. Busca no Pexels

Para cenas classificadas como "pexels":

```
✅ BOM:
- Keywords geradas em inglês
- Vídeo encontrado (HD 1280x720+)
- URL válida do vídeo

⚠️ ATENÇÃO:
- Pexels não encontrou nada
- Fallback automático para Stability
- Custo aumentou de $0 para $0.04
```

### 3. Geração com Stability

Para cenas classificadas como "stability":

```
✅ BOM:
- Prompt em inglês otimizado
- Imagem 1024x1024 gerada
- Arquivo salvo: scene_XX.png
- Custo: $0.04

❌ RUIM:
- Erro 401 (API key inválida)
- Erro 402 (sem créditos)
- Timeout (API lenta)
```

### 4. Custos Totais

```
✅ ÓTIMO:
- Vídeo 1: $0.04 (75% Pexels)
- Vídeo 2: $0.08 (50% Pexels)
- Média: $0.06/vídeo

⚠️ REVISAR:
- Vídeo 1: $0.12 (0% Pexels)
  → Problema: Classificador não está detectando pessoas
  → Solução: Ajustar prompt do classificador

- Vídeo 2: $0.00 (100% Pexels)
  → Problema: Todas as cenas foram para Pexels
  → Solução: Conceitos abstratos não estão sendo detectados
```

---

## 📁 Arquivos Gerados

Após executar, você terá:

```
./test_results/
├── video_corporativo_result.json
└── video_tech_result.json
```

### Estrutura do JSON

```json
{
  "test_name": "Vídeo Corporativo",
  "timestamp": "2025-01-19T...",
  "brief": { ... },
  "script": {
    "scenes": [
      {
        "scene_number": 1,
        "visual_description": "...",
        "narration": "..."
      }
    ]
  },
  "visual_plan": {
    "scenes": [
      {
        "scene_number": 1,
        "source": "pexels",
        "media_type": "video",
        "media_path": "https://...",
        "cost": 0.0,
        "keywords": "person frustrated office"
      },
      {
        "scene_number": 2,
        "source": "stability_ai",
        "media_type": "image",
        "media_path": "/path/to/scene_02.png",
        "cost": 0.04,
        "prompt_used": "OMA AI logo 3D holographic..."
      }
    ]
  },
  "statistics": {
    "total_scenes": 3,
    "pexels_count": 2,
    "stability_count": 1,
    "total_cost": 0.04,
    "pexels_rate": 0.67
  }
}
```

---

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError"

```bash
# Instalar dependências
pip install -r requirements_openrouter.txt
```

### Erro: "OPENROUTER_API_KEY not found"

```bash
# Copiar .env.example para .env
cp .env.example .env

# Editar .env e adicionar sua key
OPENROUTER_API_KEY=sk-or-v1-xxxxx
```

### Erro: "PEXELS_API_KEY not configured"

```bash
# Obter key grátis em https://www.pexels.com/api/
# Adicionar no .env
PEXELS_API_KEY=xxxxx
```

### Erro: "Stability AI 401 Unauthorized"

```bash
# Verificar se key está correta
# Obter em https://platform.stability.ai/
STABILITY_API_KEY=sk-xxxxx

# Verificar se tem créditos (mínimo $10)
```

### Erro: "Pexels não encontrou nada"

**Isso é NORMAL!** O Pexels não tem tudo. Quando não encontra:
- ✅ Sistema faz fallback automático para Stability AI
- ✅ Custo aumenta de $0 para $0.04
- ✅ Qualidade mantida

### Classificação errada?

**Exemplo:** "Pessoa sorrindo" foi classificado como "stability"

**Solução:**
1. Abrir `agents/visual_agent.py`
2. Procurar `_classify_scene_type`
3. Ajustar prompt para ser mais explícito
4. Adicionar mais exemplos

---

## ✅ Critérios de Sucesso

O teste é considerado bem-sucedido se:

1. ✅ **Classificação correta:**
   - Cenas com pessoas → pexels
   - Cenas abstratas → stability

2. ✅ **Busca Pexels funcional:**
   - Keywords em inglês
   - Vídeos HD encontrados
   - URLs válidas

3. ✅ **Geração Stability funcional:**
   - Imagens 1024x1024
   - Prompts em inglês
   - Arquivos salvos

4. ✅ **Custos otimizados:**
   - Vídeo corporativo: $0.02-0.06
   - Vídeo tech: $0.06-0.12
   - Taxa Pexels: 40-70%

5. ✅ **Fallback automático:**
   - Se Pexels falhar, usa Stability
   - Sem erros fatais

---

## 🎯 Próximos Passos Após os Testes

### Se Tudo Passar ✅

1. Testar com seus próprios briefings
2. Ajustar thresholds se necessário
3. Monitorar custos reais
4. Deploy para produção!

### Se Algo Falhar ⚠️

1. Verificar logs detalhados
2. Identificar qual fase falhou
3. Ajustar código/prompts
4. Re-testar

### Otimizações Possíveis

1. **Melhorar classificador:**
   - Adicionar mais exemplos
   - Ajustar temperatura do LLM
   - Cache de classificações

2. **Melhorar busca Pexels:**
   - Keywords mais genéricas
   - Tentar múltiplas buscas
   - Fallback para keywords alternativas

3. **Reduzir custos Stability:**
   - Usar apenas quando realmente necessário
   - Cache de imagens similares
   - Compressão de imagens

---

## 📞 Suporte

Se tiver problemas:

1. Verificar logs do terminal
2. Analisar JSON de resultado
3. Verificar API keys
4. Testar APIs individualmente

---

**Boa sorte nos testes!** 🚀

Se tudo funcionar, você terá um sistema que:
- ✅ Classifica automaticamente cenas
- ✅ Usa Pexels para pessoas (grátis + qualidade)
- ✅ Usa Stability para conceitos (pago + único)
- ✅ Mix perfeito de real + abstrato
- ✅ Custo otimizado ($0.04-0.12/vídeo)
