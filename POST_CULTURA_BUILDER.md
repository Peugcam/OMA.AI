# 🎬 Como Construí um Sistema Multi-Agente de IA para Gerar Vídeos Automaticamente

## O Desafio

Queria criar algo ambicioso: um sistema que recebe apenas um tema e gera vídeos completos automaticamente - com roteiro, narração em português, imagens, vídeos stock e edição. Tudo isso rodando na nuvem, escalável e sem gastar uma fortuna.

O problema? Nenhuma IA sozinha consegue fazer tudo isso bem. Cada parte exige expertise diferente.

## A Solução: Arquitetura Multi-Agente

Inspirado em como empresas reais funcionam, criei **5 agentes especializados**, cada um expert em sua área:

### 🎯 1. Supervisor Agent (O Chefe)
- **Modelo**: Qwen 2.5 7B
- **Função**: Coordena todo mundo, valida entregas, garante qualidade
- **Pattern**: Orchestration - delega tarefas e cobra resultados

### ✍️ 2. Script Writer (O Roteirista)
- **Modelo**: GPT-4o-mini
- **Função**: Cria roteiros virais com hooks, storytelling e copywriting
- **Pattern**: Reflection - se auto-critica e melhora o próprio trabalho
- **Tempo**: ~45s por roteiro

### 🎨 3. Visual Planner (O Diretor de Arte)
- **Modelo**: Qwen 2.5 7B
- **Função**: Planeja cenas, busca vídeos (Pexels) e gera imagens (Stability AI)
- **Tempo**: ~60s
- **Proteção**: Detecta e evita gerar imagens com pessoas

### 🎙️ 4. Audio Producer (O Produtor de Som)
- **Modelo**: Mistral 7B
- **Função**: Gera narração em português BR com vozes naturais
- **TTS**: ElevenLabs (primário) + Edge TTS (fallback gratuito)
- **Tempo**: ~90s

### 🎞️ 5. Video Editor (O Editor)
- **Modelo**: Llama 3.2 3B
- **Função**: Monta tudo com FFmpeg, adiciona transições, exporta
- **Tempo**: ~120s

**Resultado**: Vídeo completo em **5-6 minutos** 🚀

## Stack Técnica

### APIs e Serviços
- **OpenRouter**: Gateway único para acessar GPT-4o-mini, Qwen, Mistral, Llama ($0.04-$0.15 por 1M tokens)
- **ElevenLabs**: TTS profissional em português ($5-22/mês, 10k chars grátis)
- **Pexels**: Vídeos stock 100% grátis, ilimitados
- **Stability AI**: Geração de imagens SDXL ($0.02/imagem)

### Infraestrutura
- **Google Cloud Run**: Serverless, auto-scaling de 0 a 10 instâncias
- **Cloud Build**: CI/CD automático (push no git = deploy automático)
- **Artifact Registry**: Armazenamento de containers Docker
- **Config**: 2 vCPUs, 4GB RAM, timeout 15min

### Code
- **Python 3.11** com FastAPI + Gradio
- **FFmpeg** para processamento de vídeo
- **Edge TTS** como fallback gratuito
- **AIClientFactory** pattern para gerenciar múltiplos LLMs

## Os Perrengues (e Como Resolvi)

### 🐛 Problema 1: ElevenLabs API v2+
**Error**: `'ElevenLabs' object has no attribute 'generate'`

A documentação antiga da internet usa `.generate()`, mas a API v2+ mudou para `.text_to_speech.convert()`. Depois de 3 deploys debuggando logs no Cloud Run, descobri e corrigi.

```python
# ERRADO (v1):
audio = client.generate(text=text, voice=voice_id)

# CORRETO (v2+):
audio = client.text_to_speech.convert(
    voice_id=voice_id,
    text=text,
    model_id="eleven_multilingual_v2"
)
```

### 🔥 Problema 2: Windows Path no Linux (O Pior)
**Error**: `C:/Users/paulo/.../audio.mp3: Protocol not found`

Este foi tenso. O áudio estava sendo gerado perfeitamente, mas o FFmpeg não conseguia ler porque o código usava paths do Windows (`C:/Users/...`) mesmo rodando em Linux (Cloud Run).

O pior: em Linux, `mkdir("C:/Users/...")` **não falha** - cria um diretório literal com esse nome! Então minha primeira tentativa de fix (testar vários diretórios) sempre pegava o primeiro path Windows.

**Solução**: Detecção de OS com `platform.system()`:

```python
import platform

if platform.system() == "Windows":
    # Desenvolvimento local
    output_dirs = [
        Path("C:/Users/paulo/OMA_Videos/audio"),
        Path("D:/OMA_Videos/audio"),
        Path("./outputs/audio")
    ]
else:
    # Cloud Run = Linux
    output_dirs = [Path("./outputs/audio")]
```

**Lição aprendida**: Cross-platform code é traição. Sempre testar em ambiente similar ao de produção.

### ⚙️ Problema 3: Environment Variables Sumindo
As variáveis de ambiente (API keys, models) sumiam entre deploys. Solução: colocar TUDO no `cloudbuild.yaml`:

```yaml
--set-env-vars 'OPENROUTER_API_KEY=...,ELEVENLABS_API_KEY=...,PEXELS_API_KEY=...'
```

(Em produção, migrar para Secret Manager por segurança)

## Custos: Comparação Real

Rodei os números de **1000 vídeos/mês** em diferentes clouds:

| Cloud | Custo/mês | Vantagens | Desvantagens |
|-------|-----------|-----------|--------------|
| **Google Cloud Run** | ~$20 | Free tier generoso (1500 vídeos grátis), CI/CD integrado, região BR | - |
| **AWS Fargate** | ~$11 | Mais barato | Setup muito complexo (VPC, ALB, etc) |
| **Azure Containers** | ~$10 | Mais barato ainda | Menos features de auto-scaling |
| **Vertex AI** | ~$19 | Otimizado para ML | Sem free tier, precisa GPU |
| **Railway** | ~$5-10 | Muito simples | Sem auto-scaling robusto, max 8GB RAM |

**Escolhi Cloud Run** porque:
- ✅ Free tier = ~1500 vídeos grátis/mês
- ✅ Zero configuração de infraestrutura
- ✅ Auto-scaling instantâneo (0 → 10 instâncias)
- ✅ Região São Paulo (baixa latência)
- ✅ `git push` = deploy automático

## Otimizações Implementadas

### 1. Dual TTS System
- **ElevenLabs** (voz profissional) como primário
- **Edge TTS** (Microsoft, grátis) como fallback
- Se ElevenLabs falha ou acaba crédito, usa Edge automaticamente

### 2. Hybrid Visual Content
- **Pexels** para cenas genéricas (100% grátis, ilimitado)
- **Stability AI** só quando precisa algo muito específico
- Detector de pessoas (evita gerar rostos, compliance com ToS)

### 3. Model Selection Estratégica
Não uso o modelo mais caro para tudo:
- **Roteiros**: GPT-4o-mini ($0.15/1M tokens) - vale a pena pela qualidade
- **Coordenação**: Qwen 2.5 ($0.06/1M tokens) - barato e eficiente
- **Edição**: Llama 3.2 3B ($0.04/1M tokens) - mais barato, task simples

### 4. Resource Management
```yaml
CPU: 2 cores (suficiente para FFmpeg)
Memory: 4GB (headroom para vídeos grandes)
Min Instances: 0 (zero custo idle, aceito cold start)
Max Instances: 10 (limita custo máximo)
Timeout: 15min (garante que vídeos complexos completem)
```

## Deploy Flow (99% Automático)

```bash
# 1. Desenvolvo localmente
git add .
git commit -m "Nova feature X"
git push origin master

# 2. Cloud Build detecta push
# 3. Builda Docker image automaticamente
# 4. Publica no Artifact Registry
# 5. Deploy no Cloud Run
# 6. 5-7 minutos depois: LIVE! ✅
```

**URL**: https://oma-video-generator-v2ecvhlyza-rj.a.run.app

## Métricas de Performance

- **Latência média**: 5-6 min por vídeo
- **Cold start**: ~10-15s (quando idle, min instances = 0)
- **CPU utilization**: ~70% (otimizado)
- **Memory utilization**: ~3GB de 4GB disponíveis
- **Success rate**: 95%+ (após correções de path)

## Lições Aprendidas

### 1. Multi-Agent > Single-Agent
Tentei primeiro com um único LLM fazendo tudo. Resultado: medíocre em tudo. Separar em agentes especializados melhorou qualidade em 300%.

### 2. Logs São Tudo
90% dos bugs foram resolvidos analisando logs estruturados no Cloud Logging. Sem logs, estaria no escuro.

### 3. Free Tiers São Generosos
Com Pexels (vídeos grátis) + Cloud Run free tier + Edge TTS (fallback grátis), dá pra rodar o MVP praticamente de graça.

### 4. Cross-Platform É Traiçoeiro
Código que funciona no Windows pode falhar silenciosamente em Linux de formas inesperadas (como paths). Sempre testar em ambiente similar ao de produção.

### 5. Patterns Importam
- **Orchestration** (supervisor delega tarefas)
- **Reflection** (script se auto-critica)
- **Factory** (cria clients de forma consistente)

Esses patterns deixaram o código limpo e manutenível.

## Próximos Passos

### Curto Prazo (Esta Semana)
- [ ] Fix Stability AI people detection (melhorar keywords)
- [ ] Migrar API keys para Secret Manager (segurança)
- [ ] Add rate limiting (evitar abuso)

### Médio Prazo (Próximo Mês)
- [ ] Adicionar music background (biblioteca livre de direitos)
- [ ] Suporte a múltiplos idiomas (espanhol, inglês)
- [ ] Dashboard de analytics (quantos vídeos, tempo médio, etc)

### Longo Prazo (Visão)
- [ ] Marketplace de templates (usuários criam seus próprios styles)
- [ ] Fine-tuning de models com vídeos bem-sucedidos
- [ ] API pública para devs integrarem

## Tech Stack Completo

```
Frontend:
- Gradio (UI rápida para prototipação)

Backend:
- FastAPI (endpoints REST)
- Python 3.11
- FFmpeg (video processing)

AI/ML:
- OpenRouter (multi-LLM gateway)
- ElevenLabs TTS + Edge TTS
- Stability AI SDXL
- Pexels API

Infrastructure:
- Google Cloud Run (compute)
- Cloud Build (CI/CD)
- Artifact Registry (containers)
- Cloud Logging (observability)

Dev Tools:
- Docker
- Git
- gcloud CLI
```

## Conclusão

Construir um sistema multi-agente foi um desafio técnico absurdo, mas extremamente gratificante. Ver 5 IAs diferentes colaborando para criar um vídeo do zero em 5 minutos é surreal.

Os principais aprendizamentos:
1. **Especialização > Generalização** (cada agente faz uma coisa bem)
2. **Cloud Run é subestimado** (serverless de verdade, barato, escalável)
3. **Logs salvam vidas** (90% do debugging foi via logs)
4. **Free tiers são seu amigo** (Pexels, Edge TTS, Cloud Run)

**Custo final**: ~$20/mês para 1000 vídeos (ou grátis com free tier).

Se tivesse que fazer de novo, mudaria pouca coisa. O maior erro foi não testar cross-platform desde o início (aquele bug de Windows path custou 3 deploys).

---

**Repo**: [privado por enquanto]
**Demo**: https://oma-video-generator-v2ecvhlyza-rj.a.run.app
**Stack**: Python, Multi-LLM, Cloud Run, FFmpeg

**Time de desenvolvimento**: 1 dev + Claude Code
**Deploys até funcionar**: 6 (trial and error pays off)
**Linhas de código**: ~3000 (sem contar deps)
**Commits no último deploy**: 3 fixes críticos

---

## Para Devs que Querem Replicar

Criei um guia completo de deployment: `DEPLOYMENT_GUIDE.md`

Inclui:
- Setup completo do GCP (passo a passo)
- Todas as API keys necessárias
- Problemas comuns + soluções (aquele bug de path está documentado)
- Comparação de custos (GCP vs AWS vs Azure)
- Otimizações de performance
- Troubleshooting

**Tempo estimado**: 2-3 horas do zero ao deploy (se seguir o guia)

---

**TL;DR**: Construí sistema com 5 IAs especializadas que geram vídeos automaticamente em 5min. Deploy serverless no Google Cloud Run por ~$20/mês (1000 vídeos). Maior perrengue: Windows paths não funcionam em Linux (óbvio em retrospectiva, mas custou 3 deploys pra descobrir). Multi-agent architecture é o futuro.

#AI #MultiAgent #CloudRun #Python #VideoGeneration #BuildInPublic
