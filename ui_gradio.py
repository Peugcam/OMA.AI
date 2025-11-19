"""
🎨 OMA v3.0 - Interface Gradio
================================

Interface web simples e rápida para criar vídeos com IA.

Vantagens do Gradio:
- Setup em 5 minutos
- Componentes prontos para LLM/mídia
- Deploy gratuito no Hugging Face Spaces
- Perfeito para demos e MVPs

Instalação:
pip install gradio

Uso:
python ui_gradio.py
"""

import gradio as gr
import asyncio
from pathlib import Path
from datetime import datetime

# Import dos agentes
from agents.supervisor_agent import SupervisorAgent


# ============================================================================
# FUNÇÕES DE CALLBACK
# ============================================================================

async def create_video(
    description: str,
    target_audience: str,
    duration: int,
    style: str,
    cta: str
) -> tuple:
    """
    Cria um vídeo com base nos inputs do usuário.

    Returns:
        (video_path, status_message, metadata_json)
    """

    # Validações
    if not description or len(description) < 10:
        yield None, "❌ Descrição muito curta (mín 10 caracteres)", ""
        return

    if duration < 10 or duration > 120:
        yield None, "❌ Duração deve estar entre 10-120 segundos", ""
        return

    # Criar brief
    brief = {
        "description": description,
        "target": target_audience,
        "duration": duration,
        "style": style,
        "cta": cta,
        "timestamp": datetime.now().isoformat()
    }

    # Inicializar estado
    state = {
        "task_id": f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "brief": brief,
        "created_at": datetime.now().isoformat(),
        "current_phase": 0,
        "completed_tasks": [],
        "failed_tasks": [],
        "errors": [],
        "is_complete": False
    }

    try:
        # Inicializar supervisor
        supervisor = SupervisorAgent()

        # FASE 1: Análise
        yield None, "🔍 Analisando requisição...", ""
        analysis = await supervisor.analyze_request(brief)
        state['analysis'] = analysis

        # FASE 2: Decomposição
        yield None, "🔨 Criando plano de execução...", ""
        subtasks = await supervisor.decompose_task(analysis)

        # FASE 3: Criar plano
        plan = supervisor.create_execution_plan(subtasks)
        state['execution_plan'] = plan

        # FASE 4: Executar
        yield None, f"🚀 Executando {len(plan.subtasks)} tarefas...", ""

        success, final_state = await supervisor.execute_plan(plan, state)

        if not success:
            errors = [st.error for st in plan.subtasks if st.error]
            yield None, f"❌ Falha na execução:\n" + "\n".join(errors), ""
            return

        # FASE 5: Validar
        yield None, "✅ Validando resultado...", ""
        is_valid, issues = await supervisor.validate_output(final_state)

        if not is_valid:
            yield None, f"⚠️ Problemas encontrados:\n" + "\n".join(issues), ""
            return

        # Sucesso!
        video_path = final_state.get('video_path')
        metadata = final_state.get('metadata', {})

        success_msg = f"""
✅ **Vídeo criado com sucesso!**

📊 **Estatísticas:**
- Duração: {metadata.get('duration_seconds', 0)}s
- Resolução: {metadata.get('resolution', 'N/A')}
- Tamanho: {metadata.get('file_size_mb', 0):.1f} MB
- Tempo de renderização: {metadata.get('rendering_time_seconds', 0)}s

🎬 **Cenas:** {len(final_state.get('script', {}).get('scenes', []))}
🎨 **Mídia:** {len(final_state.get('visual_plan', {}).get('scenes', []))} clipes
🎙️ **Narração:** {len(final_state.get('audio_files', {}).get('narration', {}).get('timestamps', []))} segmentos
"""

        yield video_path, success_msg, str(metadata)

    except Exception as e:
        yield None, f"❌ Erro: {str(e)}", ""


def create_example_video(example_name: str):
    """Carrega exemplos pré-definidos"""
    examples = {
        "Cafeteria": {
            "description": "Propaganda moderna para cafeteria especializada",
            "target": "Millennials urbanos, 25-35 anos",
            "duration": 30,
            "style": "Clean e minimalista",
            "cta": "Venha nos visitar!"
        },
        "E-commerce": {
            "description": "Vídeo de produto para loja online de roupas",
            "target": "Mulheres 18-30 anos",
            "duration": 20,
            "style": "Fashion e dinâmico",
            "cta": "Compre agora com 20% OFF"
        },
        "Tech Startup": {
            "description": "Apresentação de app inovador de produtividade",
            "target": "Profissionais 25-40 anos",
            "duration": 45,
            "style": "Corporativo moderno",
            "cta": "Baixe grátis hoje"
        }
    }

    example = examples.get(example_name, examples["Cafeteria"])

    return (
        example["description"],
        example["target"],
        example["duration"],
        example["style"],
        example["cta"]
    )


# ============================================================================
# INTERFACE GRADIO
# ============================================================================

def build_interface():
    """Constrói a interface Gradio"""

    with gr.Blocks(
        title="OMA - Criador de Vídeos com IA",
        theme=gr.themes.Soft(),
        css="""
            .gradio-container {
                max-width: 1200px;
                margin: auto;
            }
            .output-video {
                max-height: 600px;
            }
        """
    ) as demo:

        # Header
        gr.Markdown("""
        # 🎬 OMA v3.0 - Criador de Vídeos com IA

        Sistema multi-agente que cria vídeos profissionais em minutos usando SLMs locais.

        **Powered by:**
        - 🧠 Supervisor Agent (Qwen2.5-3B)
        - 📝 Script Agent (Phi-3.5-Mini)
        - 🎨 Visual Agent (Gemma-2-2B)
        - 🎙️ Audio Agent (Mistral-7B)
        - ✂️ Editor Agent (Qwen2-1.5B)
        """)

        with gr.Row():
            with gr.Column(scale=1):
                # Inputs
                gr.Markdown("## 📝 Informações do Vídeo")

                description = gr.Textbox(
                    label="Descrição do Vídeo",
                    placeholder="Ex: Propaganda para cafeteria moderna focada em millennials...",
                    lines=3,
                    info="Descreva o objetivo e contexto do vídeo"
                )

                target_audience = gr.Textbox(
                    label="Público-Alvo",
                    placeholder="Ex: Millennials urbanos, 25-35 anos",
                    info="Quem deve assistir este vídeo?"
                )

                with gr.Row():
                    duration = gr.Slider(
                        label="Duração (segundos)",
                        minimum=10,
                        maximum=120,
                        value=30,
                        step=5,
                        info="Entre 10 e 120 segundos"
                    )

                    style = gr.Dropdown(
                        label="Estilo Visual",
                        choices=[
                            "Clean e minimalista",
                            "Dinâmico e energético",
                            "Corporativo profissional",
                            "Criativo e artístico",
                            "Casual e amigável"
                        ],
                        value="Clean e minimalista",
                        info="Tom visual do vídeo"
                    )

                cta = gr.Textbox(
                    label="Call-to-Action",
                    placeholder="Ex: Visite nosso site em www.exemplo.com",
                    info="O que o espectador deve fazer?"
                )

                # Botões
                with gr.Row():
                    create_btn = gr.Button(
                        "🎬 Criar Vídeo",
                        variant="primary",
                        size="lg"
                    )
                    clear_btn = gr.ClearButton(
                        [description, target_audience, duration, style, cta],
                        value="🗑️ Limpar"
                    )

                # Exemplos
                gr.Markdown("### 💡 Exemplos Rápidos")
                example_btns = gr.Radio(
                    choices=["Cafeteria", "E-commerce", "Tech Startup"],
                    label="Carregar exemplo:",
                    value=None
                )

            with gr.Column(scale=1):
                # Outputs
                gr.Markdown("## 🎥 Resultado")

                status_output = gr.Markdown(
                    "Aguardando inputs...",
                    label="Status"
                )

                video_output = gr.Video(
                    label="Vídeo Gerado",
                    autoplay=True,
                    show_label=True,
                    elem_classes=["output-video"]
                )

                metadata_output = gr.JSON(
                    label="Metadados",
                    visible=False
                )

                # Actions pós-geração
                with gr.Row():
                    download_btn = gr.DownloadButton(
                        "⬇️ Baixar Vídeo",
                        visible=False
                    )
                    share_btn = gr.Button(
                        "🔗 Compartilhar",
                        visible=False
                    )

        # Event handlers
        create_btn.click(
            fn=create_video,
            inputs=[description, target_audience, duration, style, cta],
            outputs=[video_output, status_output, metadata_output],
            api_name="create_video"
        )

        example_btns.change(
            fn=create_example_video,
            inputs=[example_btns],
            outputs=[description, target_audience, duration, style, cta]
        )

        # Footer
        gr.Markdown("""
        ---
        ### 📊 Sobre o Sistema

        **OMA v3.0** usa 5 agentes especializados coordenados por um Supervisor:
        1. **Análise** (~10s): Supervisor entende a requisição
        2. **Roteiro** (~60s): Script Agent cria narrativa engajante
        3. **Visual + Áudio** (~90s): Agents trabalham em paralelo
        4. **Edição** (~60s): Editor Agent monta o vídeo final
        5. **Validação** (~10s): Supervisor verifica qualidade

        ⏱️ **Tempo total:** ~4-5 minutos | 💰 **Custo:** $0 (100% local)

        ---
        **Desenvolvido com ❤️ usando SLMs locais**
        """)

    return demo


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Criar interface
    demo = build_interface()

    # Lançar
    demo.launch(
        server_name="0.0.0.0",  # Acessível na rede local
        server_port=7860,
        share=False,  # True = gera URL pública temporária
        show_error=True,
        show_api=True  # API REST automática
    )

    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║                 OMA v3.0 - Interface Gradio                ║
    ╚════════════════════════════════════════════════════════════╝

    🌐 Interface disponível em:
       • Local:   http://localhost:7860
       • Rede:    http://0.0.0.0:7860

    📡 API REST disponível em:
       • Endpoint: http://localhost:7860/api/create_video
       • Docs:     http://localhost:7860/docs

    🛑 Pressione Ctrl+C para parar
    """)
