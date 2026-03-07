# 🎙️ Solução de Sincronização Áudio-Vídeo

## Problema Original

Sistema anterior tentava:
1. Criar segmentos de vídeo com durações fixas (3s, 15s, 10s, 2s)
2. Gerar avatar separadamente
3. Concatenar tudo

**Resultado:** Áudio cortado, silêncios, dessincronia ❌

---

## Solução: Audio-First Architecture

### Princípio

> **"O áudio dita o vídeo, não o contrário"**

1. Gerar áudio COMPLETO primeiro
2. Analisar duração exata + timecodes
3. Criar visual sincronizado com áudio
4. Composição final em uma única passada

---

## Pipeline Correto

### ETAPA 1: Geração do Áudio Completo

```python
# 1.1: Gerar script otimizado para 30s
script = await generate_script(
    max_words=75,  # ~150 palavras/min = 75 palavras em 30s
    sections={
        "hook": 10,      # 10 palavras
        "presentation": 45,  # 45 palavras
        "benefits": 15,  # 15 palavras
        "cta": 5         # 5 palavras
    }
)

# Exemplo de script otimizado:
{
    "hook": "Cansada de manchas que não saem?",  # 6 palavras
    "presentation": "Este sérum com vitamina C já transformou mais de 10 mil mulheres. Resultados reais em 7 dias, dermatologicamente testado.",  # 20 palavras
    "benefits": "Reduz manchas, uniformiza tom, previne rugas.",  # 6 palavras
    "cta": "Garanta com desconto. Link abaixo!",  # 5 palavras
    "full_script": "Cansada de manchas que não saem? Este sérum..."
}

# 1.2: Gerar áudio com timing preciso
audio_result = await generate_audio_with_timestamps(
    script=script["full_script"],
    voice="pt-BR-FranciscaNeural",
    speed=1.1  # Ligeiramente mais rápido para caber em 30s
)

# Resultado:
{
    "audio_path": "narration.mp3",
    "duration": 29.5,  # segundos
    "timestamps": {
        "hook_start": 0.0,
        "hook_end": 3.2,
        "presentation_start": 3.2,
        "presentation_end": 15.8,
        "benefits_start": 15.8,
        "benefits_end": 25.1,
        "cta_start": 25.1,
        "cta_end": 29.5
    },
    "word_timecodes": [
        {"word": "Cansada", "start": 0.0, "end": 0.5},
        {"word": "de", "start": 0.5, "end": 0.6},
        {"word": "manchas", "start": 0.6, "end": 1.1},
        ...
    ]
}
```

**Tecnologias para timecodes:**

**Opção A: Azure Speech SDK (Recomendado)**
```python
import azure.cognitiveservices.speech as speechsdk

speech_config = speechsdk.SpeechConfig(
    subscription=AZURE_KEY,
    region="brazilsouth"
)

# Configurar para retornar word boundaries
speech_config.set_property(
    speechsdk.PropertyId.SpeechServiceResponse_RequestWordLevelTimestamps,
    "true"
)

synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

# Gerar com eventos de palavra
result = synthesizer.speak_text_async(script).get()

# Eventos contêm timecodes exatos de cada palavra!
word_boundaries = result.word_boundary_events
```

**Opção B: Edge TTS (Grátis)**
```python
import edge_tts

communicate = edge_tts.Communicate(
    script,
    "pt-BR-FranciscaNeural"
)

# Salva áudio + gera arquivo WebVTT com timecodes
await communicate.save(
    "narration.mp3",
    metadata_path="timecodes.vtt"
)

# timecodes.vtt contém:
# 00:00:00.000 --> 00:00:03.200
# Cansada de manchas que não saem?
```

**Opção C: ElevenLabs + Gentle Forced Aligner**
```python
# 1. Gera áudio com ElevenLabs (qualidade superior)
audio = elevenlabs.generate(
    text=script,
    voice="Bella",  # Voz feminina BR
    model="eleven_multilingual_v2"
)

# 2. Usa Gentle para alinhar palavras (open source)
import gentle
aligner = gentle.ForcedAligner()
alignment = aligner.align(
    audio_path="narration.mp3",
    transcript=script
)

# Retorna timecodes palavra por palavra
```

---

### ETAPA 2: Criar Vídeo Sincronizado

Agora que temos áudio + timecodes, criamos vídeo que casa perfeitamente:

```python
# 2.1: Extrair durações dos timecodes
hook_duration = timestamps["hook_end"] - timestamps["hook_start"]  # 3.2s
presentation_duration = timestamps["presentation_end"] - timestamps["presentation_start"]  # 12.6s
benefits_duration = timestamps["benefits_end"] - timestamps["benefits_start"]  # 9.3s
cta_duration = timestamps["cta_end"] - timestamps["cta_start"]  # 4.4s

# 2.2: Criar segmentos com duração EXATA
segments = []

# HOOK (duração dinâmica baseada em áudio)
hook_video = create_hook_segment(
    image=product_image,
    text=script["hook"],
    duration=hook_duration  # 3.2s (não 3s fixo!)
)
segments.append(hook_video)

# APRESENTAÇÃO
# Opção 1: Avatar (HeyGen/D-ID)
presentation_video = create_avatar_segment(
    script=script["presentation"],
    duration=presentation_duration  # 12.6s
)

# Opção 2: Produto animado (sem avatar)
presentation_video = create_product_showcase(
    image=product_image,
    backgrounds=backgrounds,
    duration=presentation_duration,
    animation="smooth_pan_zoom"
)
segments.append(presentation_video)

# BENEFÍCIOS
benefits_video = create_benefits_segment(
    image=product_image,
    benefits=benefits_list,
    duration=benefits_duration,  # 9.3s
    word_timecodes=word_timecodes  # Animar cada benefício no momento certo!
)
segments.append(benefits_video)

# CTA
cta_video = create_cta_segment(
    image=product_image,
    cta_text=script["cta"],
    price_text=price,
    duration=cta_duration  # 4.4s
)
segments.append(cta_video)
```

---

### ETAPA 3: Composição Final com FFmpeg

```python
# 3.1: Concatenar vídeos
concat_list = "\n".join([f"file '{seg}'" for seg in segments])
with open("segments.txt", "w") as f:
    f.write(concat_list)

# 3.2: Concatenar sem re-encoding (rápido!)
subprocess.run([
    'ffmpeg', '-y',
    '-f', 'concat',
    '-safe', '0',
    '-i', 'segments.txt',
    '-c', 'copy',  # Copy, não re-encode
    'video_silent.mp4'
])

# 3.3: Adicionar áudio COMPLETO de uma vez
subprocess.run([
    'ffmpeg', '-y',
    '-i', 'video_silent.mp4',
    '-i', 'narration.mp3',
    '-c:v', 'copy',  # Mantém vídeo
    '-c:a', 'aac',
    '-b:a', '128k',
    '-shortest',  # Corta no menor (garante sync)
    'final_ad.mp4'
])
```

**Resultado:**
✅ Áudio e vídeo perfeitamente sincronizados
✅ Duração exata (não 30s fixo, mas 29.5s ou 31.2s conforme narração)
✅ Sem cortes ou silêncios

---

## Exemplo Prático: Benefícios Animados

Usando word-level timecodes para animar cada benefício EXATAMENTE quando mencionado:

```python
def create_benefits_segment(image, benefits, duration, word_timecodes):
    # Encontrar quando cada benefício é mencionado
    benefit_timings = []

    for benefit in benefits:
        # Exemplo: "Reduz manchas em 7 dias"
        first_word = benefit.split()[0].lower()  # "reduz"

        # Buscar no word_timecodes
        for tc in word_timecodes:
            if tc["word"].lower() == first_word:
                benefit_timings.append({
                    "text": benefit,
                    "start": tc["start"],
                    "duration": 2.5  # Mostrar por 2.5s
                })
                break

    # Criar vídeo com textos aparecendo nos momentos certos
    filter_complex = f"[0:v]scale=1920:1080[bg];"

    for i, bt in enumerate(benefit_timings):
        # Cada benefício aparece no timecode exato
        filter_complex += f"[bg]drawtext=text='{bt['text']}':"
        filter_complex += f"fontsize=50:fontcolor=white:"
        filter_complex += f"x=100:y={200 + i*80}:"
        filter_complex += f"enable='between(t,{bt['start']},{bt['start'] + bt['duration']})'[bg];"

    cmd = [
        'ffmpeg', '-y',
        '-loop', '1', '-i', image,
        '-filter_complex', filter_complex,
        '-t', str(duration),
        '-c:v', 'libx264',
        'benefits.mp4'
    ]

    subprocess.run(cmd)
    return 'benefits.mp4'
```

**Resultado:**
- Benefício 1 aparece aos 15.8s (quando narração diz "Reduz")
- Benefício 2 aparece aos 18.2s (quando narração diz "Uniformiza")
- Benefício 3 aparece aos 20.5s (quando narração diz "Previne")
- **Perfeitamente sincronizado!** ✅

---

## Alternativas ao Avatar

Já que avatar tem custo e complexidade, aqui estão opções melhores para afiliados:

### Opção 1: Produto Hero + Narração (Recomendado)

```
┌─────────────────────────┐
│  HOOK (0-3s)           │
│  - Produto zoom in     │
│  - Texto: "Manchas?"   │
├─────────────────────────┤
│  APRESENTAÇÃO (3-16s)  │
│  - Produto rotação 3D  │
│  - Textos key points   │
│  - Background elegante │
├─────────────────────────┤
│  BENEFÍCIOS (16-26s)   │
│  - Split screen:       │
│    - Produto (esq)     │
│    - Lista (dir)       │
├─────────────────────────┤
│  CTA (26-30s)          │
│  - Produto + preço     │
│  - Botão animado       │
└─────────────────────────┘
```

**Vantagens:**
- ✅ Custo: $0.10 total
- ✅ Foco no produto
- ✅ Sem "uncanny valley" do avatar
- ✅ Sincronização 100% controlada

### Opção 2: B-Roll Stock + Produto

```python
# Usa Pexels API (grátis) para pegar vídeos relacionados
videos = pexels.search_videos(
    query="woman applying skincare cream",
    orientation="landscape"
)

# Composição:
# 0-3s: Hook com produto
# 3-16s: B-roll de mulher usando produto + produto em corner
# 16-26s: Benefícios com produto
# 26-30s: CTA
```

**Vantagens:**
- ✅ Grátis (Pexels)
- ✅ Footage real de pessoas
- ✅ Mais convincente que avatar sintético

### Opção 3: Kinetic Typography (Texto Animado)

Estilo "anúncio moderno" com textos dinâmicos:

```
┌─────────────────────────┐
│  Palavras aparecem      │
│  sincronizadas com voz: │
│                         │
│  "CANSADA"             │
│    "de MANCHAS?"       │
│                         │
│  [Produto aparece]     │
│                         │
│  "10.000 MULHERES"     │
│    "JÁ USAM"           │
└─────────────────────────┘
```

**Implementação:**
```python
# Anima cada palavra no momento exato
for word_tc in word_timecodes:
    animate_word(
        text=word_tc["word"],
        start=word_tc["start"],
        duration=word_tc["end"] - word_tc["start"],
        style="fade_in_scale"
    )
```

---

## Recomendação Final

**Para afiliados, melhor stack:**

1. **Áudio:** Edge TTS (grátis) ou Azure TTS ($0.001)
2. **Visual:** Produto + Kinetic Typography + B-roll
3. **Composição:** FFmpeg audio-first

**Custo:** $0.10-0.12 por anúncio
**Qualidade:** 9/10
**Sincronização:** 100% ✅

---

**Quer que eu implemente essa versão audio-first?**
