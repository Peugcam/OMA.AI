# 🎬 Modern Video & Image APIs Guide (2024/2025)

## TL;DR - Melhores Opções

### Para Vídeos:
1. **Leonardo.ai** - Melhor custo-benefício ($0.08/30s)
2. **HeyGen** - Melhor para avatares ($0.05/30s)
3. **Luma AI** - Melhor qualidade intermediária ($0.60/30s)
4. **Runway** - Melhor qualidade premium ($3.00/30s)

### Para Imagens:
1. **Flux.1** - Melhor custo-benefício ($0.03/img)
2. **DALL-E 3** - Melhor overall ($0.04-0.12/img)
3. **Ideogram** - Melhor para texto em imagens ($0.08/img)

---

## 📊 Comparação Completa

### APIs de Vídeo

| API | Preço/30s | Qualidade | Velocidade | Ideal Para |
|-----|-----------|-----------|------------|------------|
| **Leonardo.ai** | $0.08 | ⭐⭐⭐⭐ | Rápida | Custo-benefício |
| **Pika Labs** | $0.80 | ⭐⭐⭐⭐⭐ | Média | Vídeos criativos |
| **Luma AI** | $0.60 | ⭐⭐⭐⭐⭐ | Lenta | Qualidade premium |
| **Runway Gen-3** | $3.00 | ⭐⭐⭐⭐⭐ | Lenta | Elite/Cinema |
| **HeyGen** | $0.05 | ⭐⭐⭐⭐⭐ | Rápida | Avatares/Explicativos |
| **D-ID** | $0.03 | ⭐⭐⭐⭐ | Rápida | Avatares budget |

### APIs de Imagem

| API | Preço/img | Qualidade | Velocidade | Ideal Para |
|-----|-----------|-----------|------------|------------|
| **Flux.1 Pro** | $0.03 | ⭐⭐⭐⭐⭐ | Rápida | Custo-benefício |
| **DALL-E 3** | $0.04-0.12 | ⭐⭐⭐⭐⭐ | Média | Overall melhor |
| **Ideogram** | $0.08 | ⭐⭐⭐⭐⭐ | Rápida | Texto em imagens |
| **Midjourney** | $0.04* | ⭐⭐⭐⭐⭐ | Média | Arte/Criativo |

*Via API não oficial (Discord bot ou intermediários)

---

## 🎯 Casos de Uso Recomendados

### 1. Vídeos Educacionais / Explicativos
**Stack Recomendado:**
- **Avatar**: HeyGen ($0.05/30s)
- **Backgrounds**: Flux.1 ($0.03/img × 3 = $0.09)
- **Total**: ~$0.14 por vídeo de 30s

**Exemplo:**
```python
# Usar HeyGen para apresentador
avatar = await agent.generate_avatar_video(
    script="Bem-vindo ao curso de Python!",
    voice_id="pt-BR-FranciscaNeural"
)

# Gerar backgrounds com Flux
background = await agent.generate_image(
    "Modern programming workspace with code on screens"
)
```

### 2. Vídeos de Marketing / Social Media
**Stack Recomendado:**
- **Vídeo**: Leonardo.ai Motion ($0.08/30s)
- **Imagens**: Flux.1 ($0.03/img × 5 = $0.15)
- **Total**: ~$0.23 por vídeo de 30s

**Exemplo:**
```python
# Gerar clips dinâmicos
clip = await agent.generate_video_clip(
    prompt="Product showcase with dynamic camera movement",
    quality=MediaQuality.ECONOMY
)
```

### 3. Vídeos Premium / Comerciais
**Stack Recomendado:**
- **Vídeo**: Runway Gen-3 ($3.00/30s)
- **Imagens**: DALL-E 3 HD ($0.08/img × 5 = $0.40)
- **Total**: ~$3.40 por vídeo de 30s

**Exemplo:**
```python
# Qualidade cinematográfica
clip = await agent.generate_video_clip(
    prompt="Cinematic product reveal with dramatic lighting",
    quality=MediaQuality.PREMIUM
)
```

### 4. Vídeos Curtos (TikTok/Reels)
**Stack Recomendado:**
- **Vídeo**: Pika Labs ($0.80/30s) - suporta vertical
- **Imagens**: Flux.1 ($0.03/img × 3 = $0.09)
- **Total**: ~$0.89 por vídeo de 30s vertical

---

## 💰 Análise de Custos (1000 vídeos de 30s)

| Estratégia | Custo/vídeo | Custo/1000 | Vs AWS Bedrock | Economia |
|------------|-------------|------------|----------------|----------|
| **Ultra Economy** (Leonardo + Flux) | $0.23 | $230 | $40,000 | **99.4%** 🔥 |
| **Balanced** (Luma + DALL-E) | $0.85 | $850 | $40,000 | **97.9%** |
| **Premium** (Runway + DALL-E HD) | $3.40 | $3,400 | $40,000 | **91.5%** |
| **Avatar** (HeyGen + Flux) | $0.14 | $140 | $40,000 | **99.7%** 🏆 |

---

## 🚀 Como Integrar no OMA

### Opção 1: Substituir Agentes Atuais

```python
# Antes (usando modelos de texto)
visual_agent = VisualAgent()
result = visual_agent.generate_scene_description(prompt)

# Depois (usando APIs modernas)
media_agent = MediaGenerationAgent(config)
video = await media_agent.generate_video_clip(prompt)
```

### Opção 2: Modo Híbrido (Recomendado)

```python
# Use IA de texto para planejamento
supervisor = SupervisorAgent()
plan = supervisor.create_video_plan(briefing)

# Use APIs modernas para geração
media_agent = MediaGenerationAgent(config)

for scene in plan.scenes:
    if scene.type == "avatar":
        video = await media_agent.generate_avatar_video(scene.script)
    else:
        video = await media_agent.generate_video_clip(scene.description)
```

---

## ⚙️ Configuração

### 1. Criar Contas

**Essenciais (Modo Economy):**
- Leonardo.ai: https://leonardo.ai
- fal.ai: https://fal.ai (para Flux)

**Opcionais (Melhor qualidade):**
- HeyGen: https://heygen.com
- Luma AI: https://lumalabs.ai
- Runway: https://runwayml.com
- OpenAI: https://platform.openai.com

### 2. Obter API Keys

```bash
# Leonardo.ai
LEONARDO_API_KEY=leo_...

# fal.ai (Flux)
FAL_API_KEY=fal_...

# HeyGen (avatares)
HEYGEN_API_KEY=hey_...

# Luma AI
LUMA_API_KEY=luma_...

# Runway
RUNWAY_API_KEY=runway_...

# OpenAI (DALL-E)
OPENAI_API_KEY=sk-proj-...
```

### 3. Adicionar ao .env

```bash
# Adicionar ao arquivo .env do OMA
echo "LEONARDO_API_KEY=leo_..." >> .env
echo "FAL_API_KEY=fal_..." >> .env
echo "HEYGEN_API_KEY=hey_..." >> .env
```

### 4. Instalar Dependências

```bash
pip install httpx  # Já incluído
```

---

## 📝 Exemplos de Uso

### Modo Economy (Leonardo + Flux)

```python
from agents.media_generation_agent import MediaGenerationAgent, MediaConfig, MediaQuality

# Configuração
config = MediaConfig(
    quality=MediaQuality.ECONOMY,
    leonardo_api_key=os.getenv("LEONARDO_API_KEY"),
    fal_api_key=os.getenv("FAL_API_KEY")
)

agent = MediaGenerationAgent(config)

# Gerar vídeo de 30s (8 clips de 4s)
clips = []
for i in range(8):
    clip = await agent.generate_video_clip(
        f"Scene {i+1}: Dynamic footage of technology",
        duration=4
    )
    clips.append(clip)

# Gerar imagens de background (5 imagens)
images = []
for i in range(5):
    img = await agent.generate_image(
        f"Background {i+1}: Tech workspace"
    )
    images.append(img)

# Custo total
total_cost = sum(c['cost'] for c in clips) + sum(i['cost'] for i in images)
print(f"Total cost: ${total_cost:.2f}")  # ~$0.23
```

### Modo Avatar (HeyGen + Flux)

```python
# Configuração
config = MediaConfig(
    quality=MediaQuality.ECONOMY,
    heygen_api_key=os.getenv("HEYGEN_API_KEY"),
    fal_api_key=os.getenv("FAL_API_KEY")
)

agent = MediaGenerationAgent(config)

# Script do vídeo
script = """
Olá! Bem-vindo ao nosso tutorial sobre inteligência artificial.
Hoje vamos aprender sobre redes neurais e como elas funcionam.
Prepare-se para uma jornada fascinante pelo mundo da IA!
"""

# Gerar vídeo com avatar
avatar_video = await agent.generate_avatar_video(
    script=script,
    voice_id="pt-BR-FranciscaNeural"  # Voz feminina PT-BR
)

# Gerar backgrounds
backgrounds = []
for desc in ["AI neural network visualization",
             "Modern tech laboratory",
             "Data flowing through circuits"]:
    bg = await agent.generate_image(desc)
    backgrounds.append(bg)

# Custo total
total_cost = avatar_video['cost'] + sum(bg['cost'] for bg in backgrounds)
print(f"Total cost: ${total_cost:.2f}")  # ~$0.14
```

### Modo Premium (Runway + DALL-E HD)

```python
# Configuração
config = MediaConfig(
    quality=MediaQuality.PREMIUM,
    runway_api_key=os.getenv("RUNWAY_API_KEY"),
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

agent = MediaGenerationAgent(config)

# Gerar clips cinematográficos
clips = []
for scene in ["Opening shot: Sunrise over city",
              "Mid shot: Product reveal",
              "Close up: Details and features",
              "Wide shot: Lifestyle integration",
              "Closing: Call to action"]:
    clip = await agent.generate_video_clip(scene, duration=6)
    clips.append(clip)

# Gerar imagens premium
images = []
for desc in ["Hero product shot",
             "Lifestyle scene",
             "Detail macro shot"]:
    img = await agent.generate_image(desc)
    images.append(img)

# Custo total
total_cost = sum(c['cost'] for c in clips) + sum(i['cost'] for i in images)
print(f"Total cost: ${total_cost:.2f}")  # ~$3.40
```

---

## 🎨 Vozes Disponíveis (HeyGen)

### Português (Brasil)

```python
voices_pt_br = {
    "FranciscaNeural": "Feminina, jovem, amigável",
    "AntonioNeural": "Masculina, profissional",
    "BrendaNeural": "Feminina, energética",
    "DonatoNeural": "Masculina, madura",
    "ElzaNeural": "Feminina, calma",
    "FabioNeural": "Masculina, casual",
    "GiovannaNeural": "Feminina, moderna",
    "HumbertoNeural": "Masculina, autoritária",
    "JulioNeural": "Masculina, jovem",
    "LeilaNeural": "Feminina, suave",
    "LeticiaNeural": "Feminina, clara",
    "ManuelaNeural": "Feminina, educada",
    "NicolauNeural": "Masculina, formal",
    "ValerioNeural": "Masculina, dinâmica",
    "YaraNeural": "Feminina, versátil"
}
```

---

## 🔧 Troubleshooting

### Leonardo API Errors

```python
# Erro: Rate limit
# Solução: Adicionar delay entre requests
await asyncio.sleep(1)

# Erro: Image not ready
# Solução: Aumentar tempo de espera
await asyncio.sleep(15)  # Ao invés de 10
```

### HeyGen Timeout

```python
# Erro: Timeout ao gerar avatar
# Solução: Aumentar timeout do httpx
self.client = httpx.AsyncClient(timeout=300.0)  # 5 minutos
```

### Flux.1 Quality Issues

```python
# Melhorar qualidade Flux
response = await self.client.post(
    "https://fal.run/fal-ai/flux-pro",
    json={
        "prompt": prompt,
        "num_inference_steps": 50,  # Aumentar de 28
        "guidance_scale": 5.0  # Aumentar de 3.5
    }
)
```

---

## 📈 Roadmap de Migração

### Fase 1: Testes (1-2 dias)
1. Criar conta Leonardo + fal.ai
2. Testar `media_generation_agent.py`
3. Gerar 10 vídeos de teste
4. Comparar qualidade vs custo

### Fase 2: Integração (3-5 dias)
1. Integrar `MediaGenerationAgent` no Supervisor
2. Adaptar pipeline de vídeo
3. Testar fluxo completo WhatsApp → Vídeo
4. Otimizar tempos de geração

### Fase 3: Produção (1 semana)
1. Deploy em produção
2. Monitorar custos reais
3. Ajustar qualidade conforme feedback
4. Escalar conforme demanda

---

## 💡 Dicas Finais

1. **Comece com Leonardo + Flux** - Melhor custo-benefício
2. **Use HeyGen para explicativos** - Avatares são muito eficientes
3. **Reserve Runway para casos especiais** - Qualidade premium custa
4. **Cache resultados** - Evite gerar mesma coisa 2x
5. **Monitore custos** - Configure alertas de budget

---

**Documentação criada em:** 2024-03-07
**Última atualização:** 2024-03-07
**Próxima revisão:** Mensal (novos APIs surgem rápido!)
