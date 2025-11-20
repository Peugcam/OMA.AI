"""
Dashboard OMA - Versao Completa
Mostra videos gerados e permite gerar novos videos
"""
import gradio as gr
from pathlib import Path
import json
from datetime import datetime
import subprocess
import sys

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

    if not videos:
        return "## Estatisticas\n\nNenhum video gerado ainda."

    total_size = sum(v.stat().st_size for v in videos) / (1024 * 1024 * 1024)

    output = "## Estatisticas\n\n"
    output += f"- Total de videos: {len(videos)}\n"
    output += f"- Espaco usado: {total_size:.2f} GB\n"
    output += f"- Ultimo video: {datetime.fromtimestamp(max(v.stat().st_mtime for v in videos)).strftime('%d/%m/%Y %H:%M')}\n"

    return output

def generate_video(theme):
    """Gera um novo video com tema personalizado"""
    try:
        # Debug: mostrar o tema recebido
        print(f"[DEBUG] Tema recebido do Gradio: '{theme}'")
        print(f"[DEBUG] Tipo: {type(theme)}")

        if not theme or theme.strip() == "":
            return "Erro: Por favor, digite um tema para o video"

        # Rodar generate_full_video.py com tema
        python_path = sys.executable
        script_path = Path("generate_full_video.py")

        print(f"[DEBUG] Comando: {python_path} {script_path} {theme.strip()}")

        if not script_path.exists():
            return "Erro: generate_full_video.py nao encontrado"

        # Executar em subprocess com tema como argumento
        result = subprocess.run(
            [python_path, str(script_path), theme.strip()],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos timeout
        )

        if result.returncode == 0:
            # Sucesso - buscar ultimo video gerado
            videos_dir = Path("C:/Users/paulo/OneDrive/Desktop/OMA_Videos")
            videos = sorted(videos_dir.glob("video_*.mp4"), key=lambda x: x.stat().st_mtime, reverse=True)

            if videos:
                latest = videos[0]
                size_mb = latest.stat().st_size / (1024 * 1024)
                return f"Video gerado com sucesso!\n\nTema: {theme}\nArquivo: {latest.name}\nTamanho: {size_mb:.1f} MB\nPath: {latest}"
            else:
                return "Video gerado mas nao encontrado"
        else:
            return f"Erro ao gerar video:\n\n{result.stderr[:500]}"

    except subprocess.TimeoutExpired:
        return "Erro: Geracao de video excedeu 5 minutos (timeout)"
    except Exception as e:
        return f"Erro: {str(e)}"

# Criar interface Gradio
with gr.Blocks(title="OMA Dashboard") as demo:
    gr.Markdown("# OMA Video Dashboard")
    gr.Markdown("Visualize videos gerados, estatisticas e gere novos videos")

    with gr.Tab("Gerar Video"):
        gr.Markdown("## Gerar Novo Video")
        gr.Markdown("Digite o tema do seu video e clique no botao para gerar automaticamente")
        gr.Markdown("**Tempo estimado:** 1-2 minutos | **Custo:** ~$0.04-$0.20")

        theme_input = gr.Textbox(
            label="Tema do Video",
            placeholder="Ex: App de produtividade com IA, Plataforma de vendas online, Curso de programacao...",
            lines=2
        )
        generate_btn = gr.Button("Gerar Video OMA App", variant="primary", size="lg")
        generate_output = gr.Textbox(label="Status", lines=10)

        generate_btn.click(fn=generate_video, inputs=theme_input, outputs=generate_output)

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
    print("Iniciando dashboard OMA completo...")
    print("Acesse: http://localhost:7860")
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
