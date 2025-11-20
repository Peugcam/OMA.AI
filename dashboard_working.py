"""
Dashboard OMA - Versao Funcional
Mostra videos gerados e permite gerar novos
"""
import gradio as gr
from pathlib import Path
import json
from datetime import datetime

def list_videos():
    """Lista todos os videos gerados"""
    videos_dir = Path("C:/Users/paulo/OneDrive/Desktop/OMA_Videos")

    if not videos_dir.exists():
        return "Nenhum video encontrado"

    videos = sorted(videos_dir.glob("video_*.mp4"), key=lambda x: x.stat().st_mtime, reverse=True)

    if not videos:
        return "Nenhum video encontrado"

    output = "## Videos Gerados\n\n"
    for i, video in enumerate(videos[:10], 1):
        size_mb = video.stat().st_size / (1024 * 1024)
        modified = datetime.fromtimestamp(video.stat().st_mtime).strftime("%d/%m/%Y %H:%M")
        output += f"{i}. **{video.name}** - {size_mb:.1f} MB - {modified}\n"
        output += f"   Path: `{video}`\n\n"

    return output

def get_metadata():
    """Busca metadata dos videos gerados"""
    outputs_dir = Path("outputs")

    if not outputs_dir.exists():
        return "Sem metadata disponivel"

    json_files = sorted(outputs_dir.glob("oma_app_full_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)

    if not json_files:
        return "Sem metadata disponivel"

    output = "## Ultimos Videos\n\n"

    for json_file in json_files[:5]:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            output += f"### {json_file.stem}\n"
            output += f"- Cenas: {data.get('scenes_count', 'N/A')}\n"
            output += f"- Custo: ${data.get('total_cost', 0):.4f}\n"
            output += f"- Duracao: {data.get('duration', 'N/A')}s\n"
            output += f"- Video: `{data.get('video_path', 'N/A')}`\n\n"
        except:
            continue

    return output

def get_stats():
    """Estatisticas gerais"""
    videos_dir = Path("C:/Users/paulo/OneDrive/Desktop/OMA_Videos")

    if not videos_dir.exists():
        return "Sem estatisticas"

    videos = list(videos_dir.glob("video_*.mp4"))
    total_size = sum(v.stat().st_size for v in videos) / (1024 * 1024 * 1024)

    output = "## Estatisticas\n\n"
    output += f"- Total de videos: {len(videos)}\n"
    output += f"- Espaco usado: {total_size:.2f} GB\n"
    output += f"- Ultimo video: {datetime.fromtimestamp(max(v.stat().st_mtime for v in videos) if videos else 0).strftime('%d/%m/%Y %H:%M')}\n"

    return output

# Criar interface Gradio
with gr.Blocks(title="OMA Dashboard") as demo:
    gr.Markdown("# OMA Video Dashboard")
    gr.Markdown("Visualize videos gerados e estatisticas")

    with gr.Tab("Videos"):
        videos_output = gr.Markdown()
        refresh_btn = gr.Button("Atualizar Lista")
        refresh_btn.click(fn=list_videos, outputs=videos_output)

    with gr.Tab("Metadata"):
        metadata_output = gr.Markdown()
        refresh_meta_btn = gr.Button("Atualizar Metadata")
        refresh_meta_btn.click(fn=get_metadata, outputs=metadata_output)

    with gr.Tab("Estatisticas"):
        stats_output = gr.Markdown()
        refresh_stats_btn = gr.Button("Atualizar Estatisticas")
        refresh_stats_btn.click(fn=get_stats, outputs=stats_output)

    # Carregar dados iniciais
    demo.load(fn=list_videos, outputs=videos_output)
    demo.load(fn=get_metadata, outputs=metadata_output)
    demo.load(fn=get_stats, outputs=stats_output)

if __name__ == "__main__":
    print("Iniciando dashboard OMA...")
    print("Acesse: http://localhost:7860")
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
