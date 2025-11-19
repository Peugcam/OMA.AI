"""
OMA Video Dashboard - Versao Simplificada
"""

import gradio as gr
import asyncio
import json
from datetime import datetime
from pathlib import Path
import sys

# Import video generation
from quick_generate import generate_video


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


def generate_video_simple(title, description):
    """Gera video com parametros basicos"""

    if not title or not description:
        return "Erro: Titulo e descricao obrigatorios", None

    briefing = {
        "title": title,
        "description": description,
        "duration": 30,
        "target_audience": "Publico geral",
        "style": "professional",
        "tone": "neutral",
        "cta": "Saiba mais!"
    }

    status_msg = f"Gerando video: {title}...\nAguarde 1-2 minutos..."

    result = run_async(generate_video(briefing))

    if result["success"]:
        video_path = result["video_path"]
        cost = result.get("cost", 0)
        scenes = result.get("scenes", 0)

        success_msg = f"""
SUCESSO!

Arquivo: {Path(video_path).name}
Cenas: {scenes}
Custo: ${cost:.4f}

Path: {video_path}
"""
        return success_msg, video_path
    else:
        error_msg = f"ERRO: {result.get('error', 'Erro desconhecido')}"
        return error_msg, None


# Interface Gradio
with gr.Blocks(title="OMA Video") as demo:

    gr.Markdown("# OMA VIDEO GENERATOR")
    gr.Markdown("Geracao automatizada de videos com IA")

    with gr.Row():
        title_input = gr.Textbox(label="Titulo", placeholder="Ex: OMA App")

    description_input = gr.Textbox(
        label="Descricao/Briefing",
        placeholder="Descreva o video...",
        lines=5
    )

    generate_btn = gr.Button("GERAR VIDEO", variant="primary")

    status_output = gr.Textbox(label="Status", lines=10)
    video_output = gr.Video(label="Video Gerado")

    generate_btn.click(
        fn=generate_video_simple,
        inputs=[title_input, description_input],
        outputs=[status_output, video_output]
    )

    gr.Markdown("---")
    gr.Markdown("Custo estimado: $0.00 - $0.04 por video")


if __name__ == "__main__":
    print("========================================")
    print("OMA VIDEO DASHBOARD")
    print("========================================")
    print("Iniciando em: http://localhost:7860")
    print("========================================")

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
