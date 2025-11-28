"""
🎬 OMA Video Dashboard - Interface Completa de Geração de Vídeos
================================================================

Dashboard profissional com:
- Geração de vídeos com IA
- Histórico de gerações
- Análise de custos
- Preview e download
- Templates prontos
"""

import sys
import io
import gradio as gr
import asyncio
import json
from datetime import datetime
from pathlib import Path
import os

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Verificar se quick_generate existe
try:
    from quick_generate import generate_video
    GENERATOR_AVAILABLE = True
    print("✅ quick_generate.py loaded successfully!")
except ImportError as e:
    GENERATOR_AVAILABLE = False
    print(f"⚠️ ImportError: {e}. Modo demo ativado.")
except Exception as e:
    GENERATOR_AVAILABLE = False
    print(f"⚠️ Error loading quick_generate.py: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()


# ============================================================================
# HELPERS
# ============================================================================

def run_async(coro):
    """Helper para rodar async em Gradio"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(coro)
        loop.close()
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_video_history():
    """Retorna histórico de vídeos gerados"""
    outputs_dir = Path("outputs/videos")
    if not outputs_dir.exists():
        return []

    videos = []
    for video_file in outputs_dir.glob("*.mp4"):
        stat = video_file.stat()
        videos.append({
            "name": video_file.name,
            "path": str(video_file),
            "size_mb": stat.st_size / (1024 * 1024),
            "created": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        })

    return sorted(videos, key=lambda x: x["created"], reverse=True)


def format_history_table():
    """Formata histórico como tabela markdown"""
    videos = get_video_history()

    if not videos:
        return "Nenhum vídeo gerado ainda."

    table = "| Arquivo | Tamanho | Data/Hora |\n"
    table += "|---------|---------|----------|\n"

    for v in videos:
        table += f"| {v['name']} | {v['size_mb']:.2f} MB | {v['created']} |\n"

    return table


# ============================================================================
# TEMPLATES PRONTOS
# ============================================================================

TEMPLATES = {
    "Redes Sociais": {
        "title": "Dica Rápida: Produtividade com IA",
        "description": """Conteúdo curto e viral para redes sociais.

**ESTRUTURA:**
- Hook visual nos 2 primeiros segundos
- Dica/informação valiosa
- Exemplo prático
- CTA para engajamento

**ESTILO:** Dinâmico, vertical, legendado
**TOM:** Casual e direto""",
        "duration": "15",
        "audience": "Público de redes sociais",
        "style": "social",
        "tone": "casual",
        "cta": "Curta e compartilhe!"
    }
}


# ============================================================================
# GERAÇÃO DE VÍDEO
# ============================================================================

def generate_video_ui(title, description, duration, audience, style, tone, cta, progress=gr.Progress()):
    """
    Gera vídeo a partir dos inputs do usuário
    """

    # Validações
    if not title or not description:
        return "❌ Erro: Título e descrição são obrigatórios", None, "", ""

    try:
        duration_int = int(duration)
        if duration_int < 10 or duration_int > 120:
            return "❌ Erro: Duração deve estar entre 10 e 120 segundos", None, "", ""
    except:
        return "❌ Erro: Duração deve ser um número", None, "", ""

    # Criar briefing
    briefing = {
        "title": title,
        "description": description,
        "duration": duration_int,
        "target_audience": audience or "Público geral",
        "style": style or "professional",
        "tone": tone or "neutral",
        "cta": cta or "Saiba mais!"
    }

    # DEBUG: Print briefing
    print("\n" + "="*60)
    print("🎬 BRIEFING RECEBIDO:")
    print("="*60)
    print(json.dumps(briefing, indent=2, ensure_ascii=False))
    print("="*60 + "\n")

    # Status inicial
    status_msg = f"""
## 🎬 Iniciando Geração de Vídeo...

**Título:** {title}
**Duração:** {duration}s
**Estilo:** {style}

### Pipeline Multi-Agente:
"""

    yield status_msg, None, "", ""

    if not GENERATOR_AVAILABLE:
        # Modo demo
        import time

        steps = [
            ("Supervisor Agent", "Analisando briefing...", 10),
            ("Script Agent", "Criando roteiro criativo...", 20),
            ("Visual Agent", "Buscando mídia visual...", 40),
            ("Audio Agent", "Gerando narração e música...", 60),
            ("Editor Agent", "Montando vídeo final...", 80),
            ("Finalização", "Salvando e processando...", 95),
        ]

        for step_name, step_msg, pct in steps:
            progress(pct/100, desc=step_msg)
            status_msg += f"\n- ✅ **{step_name}:** {step_msg}"
            yield status_msg, None, "", ""
            time.sleep(1)

        progress(1.0, desc="Concluído!")

        demo_result = f"""
## ✅ VÍDEO GERADO COM SUCESSO! (MODO DEMO)

**Arquivo:** demo_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4
**Cenas:** 5
**Custo:** $0.0005

### ⚠️ Modo Demo Ativo

Para gerar vídeos reais, você precisa:
1. Configurar `quick_generate.py`
2. Configurar variáveis de ambiente (.env)
3. Ter APIs configuradas (OpenRouter, Pexels, etc.)

### Detalhes do Briefing:
- 📹 **Título:** {title}
- ⏱️ **Duração:** {duration}s
- 🎯 **Audiência:** {audience}
- 🎨 **Estilo:** {style}
- 💬 **Tom:** {tone}
- 📢 **CTA:** {cta}

---
**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        history = format_history_table()
        costs = "Total investido: $0.00 (modo demo)"

        yield demo_result, None, history, costs
        return

    # Geração real
    try:
        progress(0.1, desc="Iniciando pipeline...")
        status_msg += "\n- 🔄 **Pipeline iniciado**"
        yield status_msg, None, "", ""

        result = run_async(generate_video(briefing))

        # DEBUG: Print result
        print("\n" + "="*60)
        print("📦 RESULTADO DA GERAÇÃO:")
        print("="*60)
        print(f"Success: {result.get('success')}")
        print(f"Video Path: {result.get('video_path')}")
        print(f"Error: {result.get('error', 'N/A')}")
        print("="*60 + "\n")

        progress(1.0, desc="Concluído!")

        # Processar resultado
        if result.get("success"):
            video_path = result.get("video_path", "")
            cost = result.get("cost", 0)
            scenes = result.get("scenes", 0)
            metadata = result.get("metadata", {})

            # Garantir path absoluto
            if video_path:
                video_path = str(Path(video_path).resolve())
                print(f"📹 Video path absoluto: {video_path}")
                print(f"📹 Existe? {Path(video_path).exists()}")

            success_msg = f"""
## ✅ VÍDEO GERADO COM SUCESSO!

**Arquivo:** `{Path(video_path).name if video_path else 'N/A'}`
**Cenas:** {scenes}
**Custo:** ${cost:.4f}

### 📊 Detalhes Técnicos:
- 📹 **Resolução:** {metadata.get('resolution', 'N/A')}
- ⏱️ **Duração:** {metadata.get('duration_seconds', 'N/A')}s
- 💾 **Tamanho:** {metadata.get('file_size_mb', 'N/A')} MB
- 🎵 **Áudio:** {metadata.get('audio_tracks', 'N/A')} tracks

### 📂 Localizações:
1. `{video_path}`

### ⚡ Performance:
- **Tempo total:** {metadata.get('generation_time', 'N/A')}s
- **Agentes usados:** {metadata.get('agents_used', 'N/A')}

---
**Timestamp:** {result.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}

🎉 **Pronto para publicar!**
"""

            # Atualizar histórico e custos
            history = format_history_table()
            total_cost = sum([v.get('cost', 0) for v in get_video_history()])
            costs = f"Total investido hoje: ${total_cost:.4f}"

            # Video path para preview - SEMPRE usar path relativo para Gradio
            video_preview = None
            if video_path and Path(video_path).exists():
                # Converter para path relativo (Gradio precisa disso)
                try:
                    rel_path = Path(video_path).relative_to(Path.cwd())
                    video_preview = str(rel_path)
                    print(f"✅ Preview habilitado (relativo): {video_preview}")
                except ValueError:
                    # Se não conseguir fazer relativo, usar absoluto mesmo
                    video_preview = str(Path(video_path).resolve())
                    print(f"✅ Preview habilitado (absoluto): {video_preview}")
            else:
                # Tentar encontrar o vídeo mais recente na pasta outputs
                outputs_dir = Path("outputs/videos")
                if outputs_dir.exists():
                    videos = sorted(outputs_dir.glob("*.mp4"), key=lambda x: x.stat().st_mtime, reverse=True)
                    if videos:
                        # Path relativo
                        video_preview = str(videos[0])
                        print(f"✅ Preview via fallback (último vídeo relativo): {video_preview}")

            yield success_msg, video_preview, history, costs

        else:
            error_msg = f"""
## ❌ ERRO NA GERAÇÃO

**Erro:** {result.get('error', 'Erro desconhecido')}

### 🔍 Detalhes:
{result.get('details', 'Nenhum detalhe adicional')}

### 🛠️ Possíveis Soluções:
1. Verifique as configurações no arquivo .env
2. Confirme que todas as APIs estão configuradas
3. Verifique os logs para mais detalhes
4. Tente novamente com parâmetros diferentes

---
**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            yield error_msg, None, format_history_table(), ""

    except Exception as e:
        error_msg = f"""
## ❌ ERRO INESPERADO

**Exceção:** {str(e)}

### 🔍 Stack Trace:
```
{e}
```

Entre em contato com o suporte se o problema persistir.
"""
        yield error_msg, None, format_history_table(), ""


def load_template(template_name):
    """Carrega template selecionado"""
    if template_name in TEMPLATES:
        t = TEMPLATES[template_name]
        return (
            t["title"],
            t["description"],
            t["duration"],
            t["audience"],
            t["style"],
            t["tone"],
            t["cta"]
        )
    return "", "", "30", "", "", "", ""


# ============================================================================
# INTERFACE GRADIO
# ============================================================================

def create_video_dashboard():
    """Cria interface do dashboard de vídeos"""

    with gr.Blocks(
        title="OMA Video Generator",
        theme=gr.themes.Soft(),
        css="""
        .header { text-align: center; padding: 20px; }
        .status-box { border: 2px solid #4CAF50; border-radius: 10px; padding: 15px; }
        .error-box { border: 2px solid #f44336; border-radius: 10px; padding: 15px; }
        """
    ) as app:

        # Header
        gr.Markdown("""
        <div class="header">
            <h1>🎬 OMA Video Generator</h1>
            <p><strong>Geração Automática de Vídeos com IA Multi-Agente</strong></p>
            <p>Crie vídeos profissionais em minutos usando 5 agentes especializados</p>
        </div>
        """)

        with gr.Tabs():

            # ========================================
            # TAB 1: GERADOR
            # ========================================
            with gr.Tab("🎬 Gerar Vídeo"):

                with gr.Row():
                    with gr.Column(scale=2):
                        gr.Markdown("### 📝 Briefing do Vídeo")

                        # Templates
                        template_dropdown = gr.Dropdown(
                            choices=[""] + list(TEMPLATES.keys()),
                            label="📋 Templates Prontos (Opcional)",
                            info="Selecione um template para preencher automaticamente"
                        )

                        # Inputs
                        title_input = gr.Textbox(
                            label="🎯 Título do Vídeo",
                            placeholder="Ex: Lançamento do Produto X",
                            lines=1
                        )

                        description_input = gr.Textbox(
                            label="📄 Descrição / Brief",
                            placeholder="Descreva o vídeo, estrutura, mensagem principal...",
                            lines=8
                        )

                        with gr.Row():
                            duration_input = gr.Textbox(
                                label="⏱️ Duração (segundos)",
                                value="30",
                                info="10-120 segundos"
                            )
                            audience_input = gr.Textbox(
                                label="🎯 Público-Alvo",
                                placeholder="Ex: Profissionais de tecnologia"
                            )

                        with gr.Row():
                            style_input = gr.Dropdown(
                                choices=["modern", "corporate", "educational", "promotional", "social", "minimalist"],
                                label="🎨 Estilo Visual",
                                value="modern"
                            )
                            tone_input = gr.Dropdown(
                                choices=["professional", "casual", "enthusiastic", "urgent", "friendly", "neutral"],
                                label="💬 Tom",
                                value="professional"
                            )

                        cta_input = gr.Textbox(
                            label="📢 Call-to-Action",
                            placeholder="Ex: Saiba mais em nosso site!",
                            value="Saiba mais!"
                        )

                        # Botão
                        generate_btn = gr.Button(
                            "🚀 Gerar Vídeo",
                            variant="primary",
                            size="lg"
                        )

                    with gr.Column(scale=1):
                        gr.Markdown("### 📊 Status & Preview")

                        status_output = gr.Markdown("Aguardando inputs...")
                        video_output = gr.Video(label="🎥 Preview do Vídeo")

                # Template loading
                template_dropdown.change(
                    fn=load_template,
                    inputs=[template_dropdown],
                    outputs=[title_input, description_input, duration_input,
                            audience_input, style_input, tone_input, cta_input]
                )

            # ========================================
            # TAB 2: HISTÓRICO
            # ========================================
            with gr.Tab("📋 Histórico"):
                gr.Markdown("### 📚 Vídeos Gerados")

                history_output = gr.Markdown(format_history_table())

                refresh_history_btn = gr.Button("🔄 Atualizar Histórico")
                refresh_history_btn.click(
                    fn=lambda: format_history_table(),
                    outputs=[history_output]
                )

            # ========================================
            # TAB 3: CUSTOS
            # ========================================
            with gr.Tab("💰 Custos"):
                gr.Markdown("### 💵 Análise de Custos")

                costs_output = gr.Markdown("Carregando dados de custos...")

                gr.Markdown("""
                #### 💡 Informações de Custo

                **Custo médio por vídeo:** ~$0.0005 - $0.002

                **Breakdown:**
                - Supervisor Agent (Qwen 2.5): ~$0.0001
                - Script Agent (Phi-3.5): ~$0.0001
                - Visual Agent (Gemma 2): ~$0.0002
                - Audio Agent (Mistral): ~$0.0001
                - Editor Agent (Llama 3.2): ~$0.0001

                **Total:** ~16-45x mais barato que AWS/Azure/GCP!
                """)

            # ========================================
            # TAB 4: AJUDA
            # ========================================
            with gr.Tab("❓ Ajuda"):
                gr.Markdown("""
                ### 📖 Como Usar

                #### 1️⃣ Preencher Briefing
                - Use templates prontos ou crie do zero
                - Seja específico na descrição
                - Defina duração entre 10-120 segundos

                #### 2️⃣ Gerar Vídeo
                - Clique em "Gerar Vídeo"
                - Aguarde 1-2 minutos (processamento multi-agente)
                - Vídeo aparecerá no preview

                #### 3️⃣ Download
                - Vídeo salvo em: `outputs/videos/`
                - Também copiado para: `D:/OMA_Videos/`
                - Formato: MP4, pronto para publicar

                ### 🤖 Pipeline Multi-Agente

                1. **Supervisor Agent** - Analisa briefing e planeja execução
                2. **Script Agent** - Cria roteiro criativo e cativante
                3. **Visual Agent** - Busca/gera mídia visual (Pexels + Stability AI)
                4. **Audio Agent** - Gera narração (TTS) e música de fundo
                5. **Editor Agent** - Monta vídeo final com transições

                ### ⚙️ Configuração Necessária

                **Variáveis de Ambiente (.env):**
                ```
                OPENROUTER_API_KEY=sk-or-v1-...
                PEXELS_API_KEY=...
                STABILITY_API_KEY=... (opcional)
                ```

                **Arquivos Necessários:**
                - `quick_generate.py` - Engine de geração
                - `agents/` - Diretório com agentes
                - `core/` - Módulos core

                ### 🆘 Problemas Comuns

                **"Erro: API key não configurada"**
                - Configure `.env` com suas chaves

                **"Erro: Módulo não encontrado"**
                - Execute: `pip install -r requirements_openrouter.txt`

                **"Vídeo não gera"**
                - Verifique logs no console
                - Confirme que todas as APIs estão ativas
                - Tente template pronto primeiro

                ### 📞 Suporte

                Documentação completa em: `README.md`
                """)

        # ========================================
        # EVENTOS
        # ========================================

        generate_btn.click(
            fn=generate_video_ui,
            inputs=[
                title_input,
                description_input,
                duration_input,
                audience_input,
                style_input,
                tone_input,
                cta_input
            ],
            outputs=[status_output, video_output, history_output, costs_output]
        )

        return app


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("🎬 Starting OMA Video Dashboard...")
    print("📹 Interface completa de geração de vídeos")
    print("")

    if not GENERATOR_AVAILABLE:
        print("⚠️ AVISO: quick_generate.py não encontrado")
        print("   Rodando em MODO DEMO - sem geração real de vídeos")
        print("")

    app = create_video_dashboard()

    # Get port from environment variable (required for Railway, Render, Heroku)
    PORT = int(os.environ.get("PORT", 7860))

    print(f"🌐 Starting server on port {PORT}")

    # Launch dashboard
    app.launch(
        server_name="0.0.0.0",
        server_port=PORT,
        share=False,
        show_error=True,  # Show errors para debug
        inbrowser=False,  # Don't open browser in production
        allowed_paths=[
            str(Path("outputs/videos").absolute()),
            str(Path("outputs/temp").absolute()),
            str(Path("outputs/images").absolute()),
            str(Path(".").absolute())
        ]
    )

# Export for imports
demo = create_video_dashboard()
