# 🚀 Guia Rápido - Segunda-feira

**Data:** 2024-03-07
**Objetivo:** Começar a usar OMA.AI para criar vídeos de afiliados

---

## ✅ CHECKLIST PRÉ-SEGUNDA

### 1. APIs Configuradas (30 min)

Siga: `SETUP_APIS_RUNWAY.md`

- [ ] RunwayML Gen-3 ($28/mês) - https://runwayml.com/
- [ ] ElevenLabs ($22/mês) - https://elevenlabs.io/
- [ ] OpenRouter ($10-20) - https://openrouter.ai/

### 2. Arquivo .env Criado (5 min)

```bash
cd C:\Users\paulo\OneDrive\Desktop\OMA.AI
cp .env.example .env
```

Edite `.env` com suas chaves (veja SETUP_APIS_RUNWAY.md)

### 3. Dependências Instaladas (10 min)

```bash
cd C:\Users\paulo\OneDrive\Desktop\OMA.AI
pip install tenacity httpx
```

---

## 🎬 USAR VIA WHATSAPP (Leão)

### Método 1: Enviar imagem do produto

1. Tire foto do produto
2. Envie para Leão no WhatsApp
3. Escreva: "Leão, cria anúncio desse produto"
4. Aguarde ~2-3 minutos
5. Receba vídeo pronto! ✅

### Método 2: Só com nome do produto

```
Você: Leão, cria anúncio do perfume Chanel N°5

Leão: 🎬 Criando anúncio profissional...
      ⏳ Analisando produto...
      ✍️ Escrevendo script persuasivo...
      🎥 Gerando 4 clips de vídeo...
      🎤 Criando narração...
      ✅ Pronto! [vídeo.mp4]

      💰 Custo: $1.11
      ⏱️ Tempo: 2min 34s
```

---

## 💻 USAR VIA PYTHON (Direto)

### Opção A: Script Simples

Crie arquivo `criar_video.py`:

```python
import asyncio
from agents.video_generator_runway import VideoGeneratorRunway

async def main():
    generator = VideoGeneratorRunway()

    # Informações básicas
    product_info = {
        'name': 'Perfume Chanel N°5',
        'price': 'R$ 899'
    }

    # OMA.AI gera script automaticamente
    # Você só precisa fornecer prompts de vídeo
    video_prompts = [
        "Elegant perfume bottle on marble, luxury lighting",
        "Close-up perfume cap, premium details",
        "Woman spraying perfume, slow motion",
        "Product with gift box, CTA setup"
    ]

    script = "Script será gerado automaticamente pelo ProductAdAgent"

    # Gerar vídeo
    result = await generator.create_affiliate_video(
        product_info=product_info,
        script=script,
        video_prompts=video_prompts
    )

    print(f"✅ Vídeo: {result['video_path']}")
    print(f"💰 Custo: ${result['cost']:.2f}")

    await generator.close()

if __name__ == "__main__":
    asyncio.run(main())
```

Execute:
```bash
python criar_video.py
```

### Opção B: Automação Completa (Recomendado)

O ProductAdAgent faz TUDO automaticamente:

```python
import asyncio
from agents.product_ad_agent import ProductAdAgent

async def main():
    agent = ProductAdAgent()

    # Só isso!
    result = await agent.create_product_ad(
        product_info={
            'name': 'Perfume Chanel N°5',
            'description': 'Perfume feminino clássico',
            'price': 'R$ 899,00'
        },
        product_image_path='chanel_n5.jpg'
    )

    # ProductAdAgent faz:
    # 1. Análise visual do produto (Claude Vision)
    # 2. Pesquisa de mercado
    # 3. Estratégia de marketing
    # 4. Script persuasivo
    # 5. Geração de vídeo
    # 6. Tudo pronto!

    print(f"✅ Anúncio: {result['ad_video_path']}")
    print(f"💰 Custo: ${result['cost']:.2f}")

    await agent.close()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📊 MONITORAR CUSTOS

### Ver créditos RunwayML:

```python
from core.runwayml_client import RunwayMLClient

async def check_credits():
    async with RunwayMLClient() as client:
        info = await client.get_account_info()
        print(f"Créditos restantes: {info.get('credits', 'N/A')}")
```

### Ver uso OpenRouter:

Acesse: https://openrouter.ai/activity

### Ver uso ElevenLabs:

Acesse: https://elevenlabs.io/subscription

---

## 🎯 FLUXO COMPLETO - EXEMPLO REAL

### Cenário: Criar 10 anúncios de produtos Amazon

```python
import asyncio
from agents.product_ad_agent import ProductAdAgent

async def criar_campanha():
    agent = ProductAdAgent()

    produtos = [
        {'name': 'Sérum Vitamina C', 'price': 'R$ 89', 'image': 'serum.jpg'},
        {'name': 'Perfume Importado', 'price': 'R$ 199', 'image': 'perfume.jpg'},
        {'name': 'Fone Bluetooth', 'price': 'R$ 149', 'image': 'fone.jpg'},
        # ... mais 7 produtos
    ]

    videos = []

    for produto in produtos:
        print(f"\n🎬 Criando anúncio: {produto['name']}")

        result = await agent.create_product_ad(
            product_info=produto,
            product_image_path=produto['image']
        )

        videos.append(result)

        print(f"✅ Pronto: {result['ad_video_path']}")
        print(f"💰 Custo: ${result['cost']:.2f}")

    # Relatório final
    total_cost = sum(v['cost'] for v in videos)
    total_time = sum(v['generation_time'] for v in videos)

    print(f"\n📊 CAMPANHA COMPLETA")
    print(f"Vídeos criados: {len(videos)}")
    print(f"Custo total: ${total_cost:.2f}")
    print(f"Tempo total: {total_time/60:.1f} minutos")
    print(f"Custo médio/vídeo: ${total_cost/len(videos):.2f}")

    await agent.close()

if __name__ == "__main__":
    asyncio.run(criar_campanha())
```

**Output esperado:**
```
📊 CAMPANHA COMPLETA
Vídeos criados: 10
Custo total: $11.10
Tempo total: 25.3 minutos
Custo médio/vídeo: $1.11
```

---

## ⚡ DICAS PRO

### 1. Gerar vídeos em lote (mais rápido)

```python
# Em vez de um por vez (25 minutos para 10 vídeos)
for produto in produtos:
    await agent.create_product_ad(produto)

# Faça em lotes paralelos (10 minutos para 10 vídeos)
tasks = [agent.create_product_ad(p) for p in produtos]
results = await asyncio.gather(*tasks)
```

### 2. Reutilizar clips genéricos

Clips de fundo podem ser reutilizados:
- "Lifestyle feminino elegante"
- "Produto em mesa moderna"
- "Close-up genérico de qualidade"

Economiza ~30% de custo!

### 3. Testar A/B com variações

```python
# Mesmo produto, 3 estratégias diferentes
estrategias = ['urgência', 'luxo', 'desconto']

for estrategia in estrategias:
    video = await agent.create_product_ad(
        produto,
        strategy_override=estrategia
    )
```

Depois veja qual converte melhor!

---

## 🐛 TROUBLESHOOTING

### Erro: "RUNWAYML_API_KEY not found"

**Solução:** Verifique se o `.env` foi criado e contém a chave.

```bash
cat .env | grep RUNWAYML
```

### Erro: "FFmpeg not found"

**Solução:** Instale FFmpeg:

**Windows:**
```bash
winget install FFmpeg
```

**Ou baixe:** https://ffmpeg.org/download.html

### Erro: "Insufficient credits"

**Solução:**
1. Verifique créditos: https://app.runwayml.com/billing
2. Upgrade plano ou aguarde reset mensal

### Vídeo gerado mas sem áudio

**Solução:** Verifique `ELEVENLABS_API_KEY` e `ELEVENLABS_VOICE_ID` no `.env`

---

## 📈 PRÓXIMOS PASSOS

### Segunda-feira - Manhã:
1. ✅ Configurar APIs (30 min)
2. ✅ Testar 1 vídeo manualmente (10 min)
3. ✅ Validar qualidade (5 min)

### Segunda-feira - Tarde:
1. ✅ Criar 5 anúncios reais (1 hora)
2. ✅ Postar em Instagram/TikTok (30 min)
3. ✅ Configurar tracking de links (30 min)

### Terça-feira:
1. ✅ Analisar métricas primeiros posts
2. ✅ Escalar para 10 anúncios/dia
3. ✅ Otimizar baseado em dados

---

## 💬 COMANDOS VIA LEÃO (WhatsApp)

```
"Leão, cria anúncio do [produto]"
"Leão, analisa esse produto [foto]"
"Leão, faz 5 vídeos de perfumes"
"Leão, quanto gastei hoje?"
"Leão, mostra meus últimos vídeos"
```

Leão encaminha para ProductAdAgent que faz tudo automaticamente!

---

## ✅ CHECKLIST FINAL

Antes de começar segunda, confirme:

- [ ] RunwayML configurado e com créditos
- [ ] ElevenLabs configurado e voz selecionada
- [ ] OpenRouter com $10+ de créditos
- [ ] Arquivo .env criado e validado
- [ ] FFmpeg instalado
- [ ] Testou 1 vídeo de exemplo
- [ ] OpenClaw/Leão conectado no WhatsApp (opcional)

---

**Pronto para segunda-feira!** 🚀

**Custo esperado:** $60-70/mês
**Produção esperada:** 40-60 vídeos/mês
**ROI esperado:** Break-even com 5-6 vendas/mês

**Dúvidas?** Veja `SETUP_APIS_RUNWAY.md` ou `EXEMPLO_ANALISE_PRODUTO.md`
