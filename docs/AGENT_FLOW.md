# 🔄 Fluxo de Agentes OMA v3.0 - Supervisor Multi-Agent System

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Fluxo Completo](#fluxo-completo)
3. [Detalhamento por Fase](#detalhamento-por-fase)
4. [Comunicação Entre Agentes](#comunicação-entre-agentes)
5. [Estado Compartilhado](#estado-compartilhado)

---

## Visão Geral

O sistema v3.0 implementa o padrão **Supervisor-Worker** onde um agente central (Supervisor) coordena múltiplos agentes especializados (Workers).

### Hierarquia de Agentes

```
                    ┌─────────────────────────┐
                    │   👤 USER REQUEST       │
                    │   "Criar vídeo de 30s   │
                    │    para cafeteria"      │
                    └───────────┬─────────────┘
                                │
                                ↓
        ╔═══════════════════════════════════════════════╗
        ║    🧠 SUPERVISOR AGENT (Qwen2.5-3B)          ║
        ║    ─────────────────────────────────────────  ║
        ║    • Analisa requisição                       ║
        ║    • Decompõe em subtarefas                   ║
        ║    • Cria plano de execução                   ║
        ║    • Roteia para workers                      ║
        ║    • Monitora progresso                       ║
        ║    • Sintetiza resultados                     ║
        ║    • Valida qualidade                         ║
        ╚═══════════════════════════════════════════════╝
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ↓               ↓               ↓
        ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
        │ 📝 SCRIPT     │ │ 🎨 VISUAL     │ │ 🎙️ AUDIO      │
        │    AGENT      │ │    AGENT      │ │    AGENT      │
        │               │ │               │ │               │
        │ Phi-3.5 3.8B  │ │ Gemma-2 2B    │ │ Mistral 7B    │
        │               │ │               │ │               │
        │ • Roteiro     │ │ • Storyboard  │ │ • Narração    │
        │ • Narrativa   │ │ • Stock video │ │ • TTS         │
        │ • Copy        │ │ • Composição  │ │ • Música      │
        └───────────────┘ └───────────────┘ └───────────────┘
                │               │               │
                └───────────────┼───────────────┘
                                ↓
                        ┌───────────────┐
                        │ ✂️ EDITOR      │
                        │    AGENT      │
                        │               │
                        │ Qwen2 1.5B    │
                        │               │
                        │ • FFmpeg      │
                        │ • Montagem    │
                        │ • Render      │
                        └───────────────┘
                                │
                                ↓
                        ┌───────────────┐
                        │ 🎬 VIDEO      │
                        │    FINAL      │
                        └───────────────┘
```

---

## Fluxo Completo

### Diagrama de Sequência Temporal

```
USER           SUPERVISOR         SCRIPT         VISUAL         AUDIO         EDITOR
 │                 │                │              │              │             │
 │ 1. Request      │                │              │              │             │
 ├────────────────>│                │              │              │             │
 │                 │                │              │              │             │
 │                 │ 2. Analyze     │              │              │             │
 │                 │────┐           │              │              │             │
 │                 │    │           │              │              │             │
 │                 │<───┘           │              │              │             │
 │                 │                │              │              │             │
 │                 │ 3. Decompose   │              │              │             │
 │                 │────┐           │              │              │             │
 │                 │    │           │              │              │             │
 │                 │<───┘           │              │              │             │
 │                 │                │              │              │             │
 │                 │ 4. Create Plan │              │              │             │
 │                 │────┐           │              │              │             │
 │                 │    │           │              │              │             │
 │                 │<───┘           │              │              │             │
 │                 │                │              │              │             │
 │                 │ ╔═══════════════════════════════════════════════════════╗ │
 │                 │ ║ PHASE 1: Script Generation (Sequential)              ║ │
 │                 │ ╚═══════════════════════════════════════════════════════╝ │
 │                 │                │              │              │             │
 │                 │ 5. Delegate    │              │              │             │
 │                 ├───────────────>│              │              │             │
 │                 │                │              │              │             │
 │                 │                │ 6. Generate  │              │             │
 │                 │                │────┐         │              │             │
 │                 │                │    │         │              │             │
 │                 │                │<───┘         │              │             │
 │                 │                │              │              │             │
 │                 │ 7. Script      │              │              │             │
 │                 │<───────────────│              │              │             │
 │                 │                │              │              │             │
 │                 │ 8. Update State│              │              │             │
 │                 │────┐           │              │              │             │
 │                 │    │           │              │              │             │
 │                 │<───┘           │              │              │             │
 │                 │                │              │              │             │
 │                 │ ╔═══════════════════════════════════════════════════════╗ │
 │                 │ ║ PHASE 2: Visual + Audio (PARALLEL)                   ║ │
 │                 │ ╚═══════════════════════════════════════════════════════╝ │
 │                 │                │              │              │             │
 │                 │ 9a. Delegate   │              │              │             │
 │                 ├────────────────┼─────────────>│              │             │
 │                 │ 9b. Delegate   │              │              │             │
 │                 ├────────────────┼──────────────┼─────────────>│             │
 │                 │                │              │              │             │
 │                 │                │              │ 10a. Plan    │             │
 │                 │                │              │────┐         │             │
 │                 │                │              │    │         │             │
 │                 │                │              │<───┘         │             │
 │                 │                │              │              │             │
 │                 │                │              │              │ 10b. Produce│
 │                 │                │              │              │────┐        │
 │                 │                │              │              │    │        │
 │                 │                │              │              │<───┘        │
 │                 │                │              │              │             │
 │                 │ 11a. Visuals   │              │              │             │
 │                 │<────────────────────────────────             │             │
 │                 │ 11b. Audio     │              │              │             │
 │                 │<─────────────────────────────────────────────              │
 │                 │                │              │              │             │
 │                 │ 12. Synthesize │              │              │             │
 │                 │────┐           │              │              │             │
 │                 │    │           │              │              │             │
 │                 │<───┘           │              │              │             │
 │                 │                │              │              │             │
 │                 │ ╔═══════════════════════════════════════════════════════╗ │
 │                 │ ║ PHASE 3: Video Editing (Sequential)                  ║ │
 │                 │ ╚═══════════════════════════════════════════════════════╝ │
 │                 │                │              │              │             │
 │                 │ 13. Delegate   │              │              │             │
 │                 ├────────────────┼──────────────┼──────────────┼────────────>│
 │                 │                │              │              │             │
 │                 │                │              │              │             │ 14. Compile
 │                 │                │              │              │             │────┐
 │                 │                │              │              │             │    │
 │                 │                │              │              │             │<───┘
 │                 │                │              │              │             │
 │                 │ 15. Video      │              │              │             │
 │                 │<────────────────────────────────────────────────────────────
 │                 │                │              │              │             │
 │                 │ 16. Validate   │              │              │             │
 │                 │────┐           │              │              │             │
 │                 │    │           │              │              │             │
 │                 │<───┘           │              │              │             │
 │                 │                │              │              │             │
 │ 17. Done ✅     │                │              │              │             │
 │<────────────────│                │              │              │             │
 │                 │                │              │              │             │
```

---

## Detalhamento por Fase

### 🔍 FASE 0: Preparação (Supervisor)

```
┌──────────────────────────────────────────────────────────┐
│ INPUT: User Brief                                        │
├──────────────────────────────────────────────────────────┤
│ {                                                        │
│   "description": "Criar propaganda para cafeteria",     │
│   "target": "millennials urbanos",                      │
│   "duration": 30,                                       │
│   "style": "moderno e minimalista",                     │
│   "cta": "Visite nossa loja"                           │
│ }                                                        │
└──────────────────────────────────────────────────────────┘
                       ↓
        ┌──────────────────────────────┐
        │ Supervisor: analyze_request  │
        └──────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────┐
│ ANALYSIS OUTPUT                                          │
├──────────────────────────────────────────────────────────┤
│ {                                                        │
│   "objective": "Atrair millennials para cafeteria",     │
│   "target_audience": "25-35 anos, urbano, classe B/C",  │
│   "style": "clean, minimalista, Instagram-ready",       │
│   "duration_seconds": 30,                               │
│   "visual_requirements": [                              │
│     "cafeteria moderna",                                │
│     "café sendo preparado",                             │
│     "pessoas jovens socializando",                      │
│     "logo da cafeteria"                                 │
│   ],                                                     │
│   "audio_requirements": [                               │
│     "narração amigável",                                │
│     "música indie/lo-fi"                                │
│   ],                                                     │
│   "cta": "Visite nossa loja na Rua X"                  │
│ }                                                        │
└──────────────────────────────────────────────────────────┘
                       ↓
        ┌──────────────────────────────┐
        │ Supervisor: decompose_task   │
        └──────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────┐
│ SUBTASKS                                                 │
├──────────────────────────────────────────────────────────┤
│ [                                                        │
│   {                                                      │
│     "id": "script_01",                                   │
│     "type": "SCRIPT_GENERATION",                         │
│     "agent": "script_agent",                             │
│     "description": "Escrever roteiro de 30s...",        │
│     "dependencies": [],                                  │
│     "priority": 1                                        │
│   },                                                     │
│   {                                                      │
│     "id": "visual_01",                                   │
│     "type": "VISUAL_PLANNING",                           │
│     "agent": "visual_agent",                             │
│     "description": "Planejar storyboard...",            │
│     "dependencies": ["script_01"],                       │
│     "priority": 2                                        │
│   },                                                     │
│   {                                                      │
│     "id": "audio_01",                                    │
│     "type": "AUDIO_PRODUCTION",                          │
│     "agent": "audio_agent",                              │
│     "description": "Gerar narração e música...",        │
│     "dependencies": ["script_01"],                       │
│     "priority": 2                                        │
│   },                                                     │
│   {                                                      │
│     "id": "edit_01",                                     │
│     "type": "VIDEO_EDITING",                             │
│     "agent": "editor_agent",                             │
│     "description": "Montar vídeo final...",             │
│     "dependencies": ["visual_01", "audio_01"],           │
│     "priority": 3                                        │
│   }                                                      │
│ ]                                                        │
└──────────────────────────────────────────────────────────┘
                       ↓
        ┌──────────────────────────────────┐
        │ Supervisor: create_execution_plan │
        └──────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────┐
│ EXECUTION PLAN                                           │
├──────────────────────────────────────────────────────────┤
│ {                                                        │
│   "task_id": "plan_3phases",                            │
│   "parallel_groups": [                                   │
│     ["script_01"],              ← PHASE 1 (sequential)  │
│     ["visual_01", "audio_01"],  ← PHASE 2 (parallel!)   │
│     ["edit_01"]                 ← PHASE 3 (sequential)  │
│   ],                                                     │
│   "total_estimated_time": 240  // 4 minutos            │
│ }                                                        │
└──────────────────────────────────────────────────────────┘
```

---

### 📝 FASE 1: Script Generation (Sequential)

```
┌──────────────────────────────────────────────────────────┐
│ 📝 SCRIPT AGENT (Phi-3.5-Mini 3.8B)                     │
│ Model: microsoft/phi-3.5-mini-instruct                   │
│ Especialização: Creative Writing, Storytelling          │
└──────────────────────────────────────────────────────────┘

INPUT (from Supervisor):
{
  "objective": "Atrair millennials para cafeteria",
  "target": "25-35 anos urbano",
  "duration": 30,
  "style": "clean minimalista"
}

                       ↓

        ┌────────────────────────────┐
        │ Script Agent: generate     │
        │                            │
        │ • Cria hook (3s)           │
        │ • Desenvolve narrativa     │
        │ • Divide em cenas          │
        │ • Escreve narração         │
        │ • Define call-to-action    │
        └────────────────────────────┘

                       ↓

OUTPUT:
{
  "script_id": "script_cafe_001",
  "title": "Seu Momento Perfeito",
  "duration_seconds": 30,
  "scenes": [
    {
      "scene_number": 1,
      "duration": 3,
      "time_range": "00:00-00:03",
      "visual_description": "Close-up de grãos de café sendo moídos em slow motion",
      "narration": "",
      "on_screen_text": "Seu Momento Perfeito",
      "keywords": ["coffee beans", "grinding", "close-up", "slow motion"],
      "mood": "contemplativo"
    },
    {
      "scene_number": 2,
      "duration": 5,
      "time_range": "00:03-00:08",
      "visual_description": "Barista preparando café com arte latte",
      "narration": "Cada xícara é feita com paixão",
      "on_screen_text": "",
      "keywords": ["barista", "latte art", "espresso", "preparation"],
      "mood": "profissional"
    },
    {
      "scene_number": 3,
      "duration": 7,
      "time_range": "00:08-00:15",
      "visual_description": "Grupo de amigos conversando e rindo na cafeteria",
      "narration": "Um lugar para se conectar com quem importa",
      "on_screen_text": "",
      "keywords": ["friends", "laughing", "cafe interior", "social"],
      "mood": "alegre, social"
    },
    {
      "scene_number": 4,
      "duration": 5,
      "time_range": "00:15-00:20",
      "visual_description": "Pessoa trabalhando no laptop com café ao lado",
      "narration": "Seu escritório favorito",
      "on_screen_text": "",
      "keywords": ["laptop", "working", "coffee", "coworking"],
      "mood": "produtivo"
    },
    {
      "scene_number": 5,
      "duration": 5,
      "time_range": "00:20-00:25",
      "visual_description": "Vista externa da cafeteria ao entardecer",
      "narration": "Venha nos visitar",
      "on_screen_text": "Café Central",
      "keywords": ["cafe exterior", "sunset", "storefront"],
      "mood": "convidativo"
    },
    {
      "scene_number": 6,
      "duration": 5,
      "time_range": "00:25-00:30",
      "visual_description": "Logo da cafeteria com endereço e horários",
      "narration": "",
      "on_screen_text": "Rua Augusta, 500\nSeg-Sex: 7h-22h",
      "keywords": ["logo", "address", "hours"],
      "mood": "informativo"
    }
  ],
  "total_scenes": 6,
  "narration_full": "Cada xícara é feita com paixão. Um lugar para se conectar com quem importa. Seu escritório favorito. Venha nos visitar.",
  "music_style": "indie lo-fi upbeat",
  "estimated_word_count": 20
}

                       ↓

        STATE UPDATED: state.script = {...}
```

---

### 🎨 FASE 2A: Visual Planning (Parallel)

```
┌──────────────────────────────────────────────────────────┐
│ 🎨 VISUAL AGENT (Gemma-2-2B)                            │
│ Model: google/gemma-2-2b-it                              │
│ Especialização: Image Search, Composition, Storyboard   │
└──────────────────────────────────────────────────────────┘

INPUT (from State):
{
  "scenes": [...],  // Do script agent
  "style": "clean minimalista"
}

                       ↓

        ┌────────────────────────────┐
        │ Visual Agent: plan_visuals │
        │                            │
        │ • Para cada cena:          │
        │   - Busca stock video      │
        │   - Seleciona melhor match │
        │   - Define composição      │
        │   - Fallback para AI gen   │
        └────────────────────────────┘

                       ↓

        ┌────────────────────────────┐
        │ Pexels API                 │
        │ Query: "coffee beans       │
        │         grinding close-up" │
        └────────────────────────────┘
                 │
                 ↓ Results (10 vídeos)
        ┌────────────────────────────┐
        │ • Rank by relevance        │
        │ • Check duration (>3s)     │
        │ • Verify quality (HD+)     │
        │ • Download best match      │
        └────────────────────────────┘

                       ↓

OUTPUT:
{
  "visual_plan_id": "visual_cafe_001",
  "scenes": [
    {
      "scene_number": 1,
      "media_type": "stock_video",
      "source": "pexels",
      "media_id": "pexels-12345678",
      "media_url": "https://...",
      "local_path": "./cache/scene_01.mp4",
      "duration": 5,  // Vídeo tem 5s, usar 3s
      "trim_start": 1,  // Começar em 1s
      "trim_end": 4,    // Terminar em 4s (= 3s total)
      "resolution": "1920x1080",
      "fps": 30,
      "effects": ["slow_motion_0.8x"],
      "composition": {
        "rule_of_thirds": true,
        "focus_point": "center"
      }
    },
    {
      "scene_number": 2,
      "media_type": "stock_video",
      "source": "pixabay",
      "media_id": "pixabay-87654321",
      "local_path": "./cache/scene_02.mp4",
      "duration": 8,
      "trim_start": 0,
      "trim_end": 5,
      // ... mais detalhes
    },
    // ... cenas 3-6
  ],
  "fallback_generated": [],  // Nenhuma precisou de AI gen
  "total_download_size_mb": 120,
  "download_time_seconds": 15
}

                       ↓

        STATE UPDATED: state.visual_plan = {...}
```

---

### 🎙️ FASE 2B: Audio Production (Parallel com Visual)

```
┌──────────────────────────────────────────────────────────┐
│ 🎙️ AUDIO AGENT (Mistral-7B-Instruct)                    │
│ Model: mistralai/Mistral-7B-Instruct-v0.3                │
│ Especialização: TTS, Music Selection, Audio Mixing      │
└──────────────────────────────────────────────────────────┘

INPUT (from State):
{
  "narration_full": "Cada xícara...",
  "scenes": [...],
  "music_style": "indie lo-fi upbeat"
}

                       ↓

        ┌────────────────────────────┐
        │ Audio Agent: produce_audio │
        │                            │
        │ Step 1: TTS Narration      │
        └────────────────────────────┘
                       ↓
        ┌────────────────────────────┐
        │ Coqui TTS (Local)          │
        │ Model: tts_models/pt/cv/vits│
        │                            │
        │ Text: "Cada xícara é..."   │
        │ Voice: Feminino neutro     │
        │ Speed: 1.0x                │
        └────────────────────────────┘
                       ↓
        narration.mp3 (10s, 192kbps)

                       ↓

        ┌────────────────────────────┐
        │ Step 2: Music Selection    │
        └────────────────────────────┘
                       ↓
        ┌────────────────────────────┐
        │ Local Music Library        │
        │ /music/royalty-free/       │
        │                            │
        │ Query: "indie lo-fi upbeat"│
        │ Filter: 30s+               │
        └────────────────────────────┘
                       ↓
        Selected: "indie_chill_01.mp3"

                       ↓

        ┌────────────────────────────┐
        │ Step 3: Audio Mixing       │
        │                            │
        │ • Trim music to 30s        │
        │ • Apply fade in (2s)       │
        │ • Apply fade out (2s)      │
        │ • Ducking during narration │
        │   (reduce music to -18dB)  │
        │ • Normalize final output   │
        └────────────────────────────┘
                       ↓
        final_audio.mp3 (30s, 320kbps)

OUTPUT:
{
  "audio_production_id": "audio_cafe_001",
  "narration": {
    "file_path": "./cache/narration.mp3",
    "duration_seconds": 10,
    "sample_rate": 44100,
    "bitrate": "192k",
    "voice": "pt-BR-female",
    "timestamps": [
      {"text": "Cada xícara é feita com paixão", "start": 3, "end": 6},
      {"text": "Um lugar para se conectar...", "start": 8, "end": 12},
      {"text": "Seu escritório favorito", "start": 15, "end": 17},
      {"text": "Venha nos visitar", "start": 20, "end": 22}
    ]
  },
  "music": {
    "file_path": "./cache/background_music.mp3",
    "original_file": "indie_chill_01.mp3",
    "duration_seconds": 30,
    "genre": "indie lo-fi",
    "tempo": 95,
    "key": "C major"
  },
  "final_mix": {
    "file_path": "./cache/final_audio.mp3",
    "duration_seconds": 30,
    "layers": [
      {"type": "music", "volume_db": -12},
      {"type": "narration", "volume_db": 0}
    ],
    "effects_applied": ["ducking", "normalization", "fade_in", "fade_out"]
  }
}

                       ↓

        STATE UPDATED: state.audio_files = {...}
```

---

### ✂️ FASE 3: Video Editing (Sequential)

```
┌──────────────────────────────────────────────────────────┐
│ ✂️ EDITOR AGENT (Qwen2-1.5B)                            │
│ Model: qwen/qwen2-1.5b-instruct                          │
│ Especialização: FFmpeg, Fast Editing, Rendering         │
└──────────────────────────────────────────────────────────┘

INPUT (from State):
{
  "visual_plan": {...},  // 6 cenas
  "audio_files": {...}   // Mix final
}

                       ↓

        ┌────────────────────────────┐
        │ Editor Agent: edit_video   │
        │                            │
        │ Step 1: Prepare Assets     │
        └────────────────────────────┘
                       ↓
        • Trim cada cena conforme visual_plan
        • Aplicar efeitos (slow motion, etc)
        • Adicionar text overlays
        • Aplicar transições

                       ↓

        ┌────────────────────────────┐
        │ Step 2: FFmpeg Pipeline    │
        └────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ FFmpeg Command Pipeline:                                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ # 1. Concatenar cenas                                  │
│ ffmpeg -f concat -safe 0 -i scenes.txt \              │
│        -c copy temp_video.mp4                          │
│                                                         │
│ # 2. Adicionar text overlays                           │
│ ffmpeg -i temp_video.mp4 \                             │
│        -vf "drawtext=text='Seu Momento Perfeito':\    │
│             fontsize=48:fontcolor=white:\              │
│             x=(w-text_w)/2:y=(h-text_h)/2:\           │
│             enable='between(t,0,3)'" \                 │
│        temp_with_text.mp4                              │
│                                                         │
│ # 3. Adicionar transições (fade)                       │
│ ffmpeg -i temp_with_text.mp4 \                         │
│        -vf "fade=t=in:st=0:d=0.5,\                    │
│             fade=t=out:st=29.5:d=0.5" \               │
│        temp_with_transitions.mp4                       │
│                                                         │
│ # 4. Mix de áudio                                      │
│ ffmpeg -i temp_with_transitions.mp4 \                  │
│        -i final_audio.mp3 \                            │
│        -c:v copy -c:a aac -b:a 192k \                 │
│        -map 0:v:0 -map 1:a:0 \                        │
│        output_final.mp4                                │
│                                                         │
│ # 5. Optimize para web                                 │
│ ffmpeg -i output_final.mp4 \                           │
│        -vcodec libx264 -preset fast \                  │
│        -crf 23 \                                       │
│        -movflags +faststart \                          │
│        OMA_Video_20251118_153045.mp4                   │
│                                                         │
└─────────────────────────────────────────────────────────┘

                       ↓

        ┌────────────────────────────┐
        │ Step 3: Generate Metadata  │
        └────────────────────────────┘

OUTPUT:
{
  "video_id": "OMA_Video_20251118_153045",
  "file_path": "./outputs/OMA_Video_20251118_153045.mp4",
  "thumbnail_path": "./outputs/OMA_Video_20251118_153045_thumb.jpg",
  "metadata": {
    "duration_seconds": 30,
    "resolution": "1920x1080",
    "fps": 30,
    "codec": "h264",
    "bitrate": "5000k",
    "file_size_mb": 12.5,
    "aspect_ratio": "16:9"
  },
  "scenes_used": 6,
  "rendering_time_seconds": 45,
  "export_settings": {
    "preset": "fast",
    "crf": 23,
    "audio_bitrate": "192k"
  }
}

                       ↓

        STATE UPDATED: state.video_path = "..."
                      state.metadata = {...}
```

---

### ✅ FASE 4: Validation (Supervisor)

```
┌──────────────────────────────────────────────────────────┐
│ 🧠 SUPERVISOR: Final Validation                         │
└──────────────────────────────────────────────────────────┘

INPUT (from State):
{
  "video_path": "./outputs/OMA_Video_20251118_153045.mp4",
  "metadata": {...},
  "script": {...},
  "visual_plan": {...},
  "audio_files": {...}
}

                       ↓

        ┌────────────────────────────┐
        │ Supervisor: validate       │
        │                            │
        │ Checks:                    │
        │ ✓ Video exists?            │
        │ ✓ Duration correct?        │
        │ ✓ All scenes present?      │
        │ ✓ Audio synced?            │
        │ ✓ Quality acceptable?      │
        └────────────────────────────┘

                       ↓

VALIDATION RESULT:
{
  "is_valid": true,
  "issues": [],
  "quality_score": 8.5,
  "checks_passed": [
    "video_file_exists",
    "duration_within_range",
    "all_scenes_rendered",
    "audio_synced",
    "resolution_correct",
    "file_size_reasonable"
  ],
  "recommendations": [
    "Qualidade boa para publicação",
    "Pronto para entrega ao cliente"
  ]
}

                       ↓

        IF valid → Return video
        IF invalid → Trigger recovery
```

---

## Comunicação Entre Agentes

### Protocolo de Mensagens

```python
# Supervisor → Worker
{
  "message_id": "msg_001",
  "from": "supervisor",
  "to": "script_agent",
  "type": "TASK_DELEGATION",
  "payload": {
    "task_id": "script_01",
    "description": "Escrever roteiro...",
    "context": {...},
    "deadline": "2025-11-18T15:35:00Z"
  },
  "timestamp": "2025-11-18T15:30:00Z"
}

# Worker → Supervisor (Acknowledgment)
{
  "message_id": "msg_002",
  "from": "script_agent",
  "to": "supervisor",
  "type": "TASK_ACCEPTED",
  "payload": {
    "task_id": "script_01",
    "estimated_time": 45,
    "status": "IN_PROGRESS"
  },
  "timestamp": "2025-11-18T15:30:02Z"
}

# Worker → Supervisor (Progress Update - opcional)
{
  "message_id": "msg_003",
  "from": "script_agent",
  "to": "supervisor",
  "type": "PROGRESS_UPDATE",
  "payload": {
    "task_id": "script_01",
    "progress_percent": 50,
    "current_step": "Escrevendo cena 3 de 6"
  },
  "timestamp": "2025-11-18T15:30:25Z"
}

# Worker → Supervisor (Result)
{
  "message_id": "msg_004",
  "from": "script_agent",
  "to": "supervisor",
  "type": "TASK_COMPLETED",
  "payload": {
    "task_id": "script_01",
    "status": "SUCCESS",
    "result": {...},  // Script completo
    "execution_time": 48
  },
  "timestamp": "2025-11-18T15:30:48Z"
}
```

---

## Estado Compartilhado (LangGraph)

### VideoState Evolution

```python
from typing import TypedDict, Optional, List, Dict

class VideoState(TypedDict):
    # Identificação
    task_id: str
    created_at: str

    # Input original
    brief: dict

    # Phase 0: Analysis
    analysis: Optional[dict]
    execution_plan: Optional[dict]

    # Phase 1: Script (COMPLETED FIRST)
    script: Optional[dict]

    # Phase 2: Visual + Audio (PARALLEL)
    visual_plan: Optional[dict]
    audio_files: Optional[dict]

    # Phase 3: Editing
    video_path: Optional[str]
    thumbnail_path: Optional[str]
    metadata: Optional[dict]

    # Tracking
    current_phase: int
    completed_tasks: List[str]
    failed_tasks: List[str]
    errors: List[dict]

    # Final
    is_complete: bool
    quality_score: Optional[float]
```

### Estado em Cada Fase

**Início:**
```python
{
  "task_id": "task_abc123",
  "created_at": "2025-11-18T15:30:00Z",
  "brief": {...},
  "current_phase": 0,
  "is_complete": False
}
```

**Após Fase 1 (Script):**
```python
{
  ...
  "current_phase": 1,
  "script": {
    "scenes": [6 cenas],
    "duration": 30,
    ...
  },
  "completed_tasks": ["script_01"]
}
```

**Após Fase 2 (Visual + Audio):**
```python
{
  ...
  "current_phase": 2,
  "visual_plan": {...},
  "audio_files": {...},
  "completed_tasks": ["script_01", "visual_01", "audio_01"]
}
```

**Final (Após Edição):**
```python
{
  ...
  "current_phase": 3,
  "video_path": "./outputs/OMA_Video_20251118_153045.mp4",
  "metadata": {...},
  "completed_tasks": ["script_01", "visual_01", "audio_01", "edit_01"],
  "is_complete": True,
  "quality_score": 8.5
}
```

---

## Resumo do Fluxo

```
┌────────────────────────────────────────────────────────────┐
│ TEMPO ESTIMADO POR FASE                                    │
├────────────────────────────────────────────────────────────┤
│ Phase 0: Analysis & Planning     →  10-15s                │
│ Phase 1: Script Generation        →  45-60s               │
│ Phase 2: Visual + Audio (PARALLEL)→  60-90s               │
│ Phase 3: Video Editing            →  45-60s               │
│ Phase 4: Validation               →  5-10s                │
├────────────────────────────────────────────────────────────┤
│ TOTAL: ~3-5 minutos                                        │
└────────────────────────────────────────────────────────────┘
```

### Paralelismo Ganhos

**v2.0 (Sequential):**
```
Script (60s) → Visual (60s) → Audio (60s) → Edit (60s) = 240s
```

**v3.0 (Parallel):**
```
Script (60s) → [Visual + Audio em paralelo] (90s) → Edit (60s) = 210s
```

**Ganho: 30s (12.5% mais rápido)** ✅

---

**Este é o fluxo completo do sistema multi-agente OMA v3.0!** 🎉
