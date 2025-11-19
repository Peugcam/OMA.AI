"""
OMA Video Dashboard - Interface para Geração de Vídeos
Integrado com quick_generate.py
"""

import gradio as gr
import asyncio
import json
from datetime import datetime
from pathlib import Path

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


def generate_video_ui(title, description, duration, audience, style, tone, cta):
    """
    Gera vídeo a partir dos inputs do usuário
    """

    # Validações
    if not title or not description:
        return "❌ Erro: Título e descrição são obrigatórios", None, ""

    try:
        duration_int = int(duration)
    except:
        return "❌ Erro: Duração deve ser um número", None, ""

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

    # Status inicial
    status_msg = f"""
## 🎬 Gerando Vídeo...

**Título:** {title}
**Duração:** {duration}s

### Pipeline:
- ⏳ Fase 1: Análise do briefing...
- ⏳ Fase 2: Criação do roteiro...
- ⏳ Fase 3: Busca/geração de mídia...
- ⏳ Fase 4: Geração de áudio...
- ⏳ Fase 5: Montagem final...

**Tempo estimado:** 1-2 minutos
"""

    yield status_msg, None, ""

    # Gerar vídeo
    result = run_async(generate_video(briefing))

    # Processar resultado
    if result["success"]:
        video_path = result["video_path"]
        cost = result.get("cost", 0)
        scenes = result.get("scenes", 0)

        success_msg = f"""
## ✅ VÍDEO GERADO COM SUCESSO!

**Arquivo:** `{Path(video_path).name}`
**Cenas:** {scenes}
**Custo:** ${cost:.4f}

### Detalhes:
- 📹 **Resolução:** {result.get('metadata', {}).get('resolution', 'N/A')}
- ⏱️ **Duração:** {result.get('metadata', {}).get('duration_seconds', 'N/A')}s
- 💾 **Tamanho:** {result.get('metadata', {}).get('file_size_mb', 'N/A')} MB

### Localizações:
1. `{video_path}`
2. `D:/OMA_Videos/{Path(video_path).name}`
3. `outputs/videos/{Path(video_path).name}`

---
**Timestamp:** {result.get('timestamp', 'N/A')}
"""

        # Metadados formatados
        metadata_json = json.dumps(result, indent=2, ensure_ascii=False)

        return success_msg, video_path, metadata_json

    else:
        error_msg = f"""
## ❌ ERRO NA GERAÇÃO

**Erro:** {result.get('error', 'Erro desconhecido')}

**Timestamp:** {result.get('timestamp', 'N/A')}

Por favor, verifique os logs e tente novamente.
"""
        return error_msg, None, json.dumps(result, indent=2, ensure_ascii=False)


def list_generated_videos():
    """Lista vídeos já gerados"""
    video_dir = Path("C:/Users/paulo/OneDrive/Desktop/OMA_Videos")

    if not video_dir.exists():
        return "Nenhum vídeo encontrado"

    videos = list(video_dir.glob("video_*.mp4"))

    if not videos:
        return "Nenhum vídeo encontrado"

    # Ordenar por data (mais recente primeiro)
    videos.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    result = "## 📹 Vídeos Gerados\n\n"

    for i, video in enumerate(videos[:10], 1):  # Mostrar últimos 10
        stat = video.stat()
        size_mb = stat.st_size / (1024 * 1024)
        modified = datetime.fromtimestamp(stat.st_mtime)

        result += f"""
### {i}. {video.name}
- **Tamanho:** {size_mb:.2f} MB
- **Data:** {modified.strftime('%d/%m/%Y %H:%M:%S')}
- **Path:** `{video}`

---
"""

    return result


def get_templates():
    """Retorna templates pré-definidos"""
    templates = {
        "OMA App Produtividade": {
            "title": "OMA - Produtividade com IA",
            "description": """Anúncio moderno do OMA App mostrando:
1. Pessoa frustrada com tarefas (problema)
2. Logo OMA aparecendo (solução)
3. Pessoa feliz usando o app (transformação)
4. Benefícios e resultados
5. Call-to-action""",
            "duration": "30",
            "audience": "Profissionais 25-40 anos",
            "style": "modern, tech, motivational",
            "tone": "inspirational",
            "cta": "Baixe grátis e transforme sua produtividade!"
        },
        "Produto E-commerce": {
            "title": "Lançamento Produto",
            "description": "Vídeo promocional destacando características, benefícios e oferta especial",
            "duration": "30",
            "audience": "Consumidores online",
            "style": "commercial, dynamic",
            "tone": "exciting",
            "cta": "Compre agora com desconto!"
        },
        "Serviço Profissional": {
            "title": "Apresentação de Serviço",
            "description": "Vídeo corporativo apresentando serviço, expertise e diferenciais",
            "duration": "45",
            "audience": "Empresários e gestores",
            "style": "professional, trustworthy",
            "tone": "confident",
            "cta": "Agende uma consulta gratuita!"
        },
        "Educacional": {
            "title": "Dica Rápida",
            "description": "Tutorial curto ensinando algo útil de forma clara e objetiva",
            "duration": "30",
            "audience": "Estudantes e profissionais",
            "style": "educational, clear",
            "tone": "informative",
            "cta": "Aprenda mais no nosso canal!"
        }
    }
    return templates


def load_template(template_name):
    """Carrega valores do template selecionado"""
    templates = get_templates()

    if template_name and template_name in templates:
        t = templates[template_name]
        return (
            t["title"],
            t["description"],
            t["duration"],
            t["audience"],
            t["style"],
            t["tone"],
            t["cta"]
        )
    else:
        return "", "", "30", "", "", "", ""


# ============================================================================
# GRADIO UI
# ============================================================================

with gr.Blocks(title="OMA Video Dashboard", theme=gr.themes.Soft()) as demo:

    gr.Markdown("""
    # 🎬 OMA VIDEO DASHBOARD
    ### Geração Automatizada de Vídeos com IA

    Sistema completo: Script + Visual (Pexels/Stability) + Audio + Edição
    """)

    with gr.Tabs():

        # TAB 1: Gerar Novo Vídeo
        with gr.Tab("🎥 Gerar Vídeo"):
            gr.Markdown("## Criar Novo Vídeo")

            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Templates Rápidos")
                    template_dropdown = gr.Dropdown(
                        choices=[""] + list(get_templates().keys()),
                        label="Escolher Template",
                        value=""
                    )
                    load_template_btn = gr.Button("Carregar Template")

            with gr.Row():
                with gr.Column(scale=2):
                    gr.Markdown("### Informações do Vídeo")

                    title_input = gr.Textbox(
                        label="Título",
                        placeholder="Ex: OMA - Produtividade com IA",
                        lines=1
                    )

                    description_input = gr.Textbox(
                        label="Descrição / Briefing",
                        placeholder="Descreva o vídeo, cenas desejadas, mensagem principal...",
                        lines=6
                    )

                    with gr.Row():
                        duration_input = gr.Textbox(
                            label="Duração (segundos)",
                            value="30",
                            scale=1
                        )

                        audience_input = gr.Textbox(
                            label="Público-Alvo",
                            placeholder="Ex: Profissionais 25-40 anos",
                            scale=2
                        )

                    with gr.Row():
                        style_input = gr.Textbox(
                            label="Estilo",
                            placeholder="Ex: modern, tech, professional",
                            scale=1
                        )

                        tone_input = gr.Textbox(
                            label="Tom",
                            placeholder="Ex: inspirational, exciting",
                            scale=1
                        )

                    cta_input = gr.Textbox(
                        label="Call-to-Action (CTA)",
                        placeholder="Ex: Baixe grátis!",
                        lines=1
                    )

                    generate_btn = gr.Button(
                        "🎬 GERAR VÍDEO",
                        variant="primary",
                        size="lg"
                    )

            gr.Markdown("---")

            status_output = gr.Markdown(label="Status")

            with gr.Row():
                with gr.Column(scale=2):
                    video_output = gr.Video(label="Vídeo Gerado")

                with gr.Column(scale=1):
                    metadata_output = gr.Code(
                        label="Metadados JSON",
                        language="json"
                    )

            # Conectar template loader
            load_template_btn.click(
                fn=load_template,
                inputs=[template_dropdown],
                outputs=[
                    title_input,
                    description_input,
                    duration_input,
                    audience_input,
                    style_input,
                    tone_input,
                    cta_input
                ]
            )

            # Conectar geração
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
                outputs=[status_output, video_output, metadata_output]
            )

        # TAB 2: Vídeos Gerados
        with gr.Tab("📹 Vídeos Gerados"):
            gr.Markdown("## Biblioteca de Vídeos")

            refresh_btn = gr.Button("🔄 Atualizar Lista")
            videos_list = gr.Markdown(value=list_generated_videos())

            refresh_btn.click(
                fn=list_generated_videos,
                outputs=[videos_list]
            )

        # TAB 3: Custos
        with gr.Tab("💰 Custos"):
            gr.Markdown("""
## 💰 Estimativa de Custos

### Por Vídeo (30 segundos):

| Item | Fonte | Custo |
|------|-------|-------|
| Vídeos Pexels | Grátis | $0.00 |
| Imagens Stability | Paga | $0.04 |
| Narração TTS | Azure Grátis | $0.00 |
| Montagem FFmpeg | Local | $0.00 |

**Custo médio:** $0.00 - $0.04 por vídeo

### Estimativa Mensal:

- 100 vídeos = $0 - $4
- 500 vídeos = $0 - $20
- 1000 vídeos = $0 - $40

**Estratégia Híbrida:**
- Pexels usado para cenas com pessoas (grátis)
- Stability AI usado apenas para logos/abstratos ($0.04)
            """)

        # TAB 4: Ajuda
        with gr.Tab("❓ Ajuda"):
            gr.Markdown("""
## 📚 Como Usar

### 1. Escolher Template (Opcional)
- Selecione um template pré-definido
- Clique em "Carregar Template"
- Personalize conforme necessário

### 2. Preencher Informações
- **Título:** Nome do vídeo
- **Descrição:** Briefing detalhado (descreva cenas, mensagem, etc)
- **Duração:** Tempo em segundos (15-60s recomendado)
- **Público-Alvo:** Para quem é o vídeo
- **Estilo:** Palavras-chave visuais (ex: modern, tech)
- **Tom:** Como deve ser a narrativa (ex: inspirational)
- **CTA:** Chamada para ação final

### 3. Gerar Vídeo
- Clique em "GERAR VÍDEO"
- Aguarde 1-2 minutos
- Vídeo aparecerá na tela quando pronto

### 4. Resultado
- Vídeo salvo em 3 locais automaticamente
- Metadados disponíveis em JSON
- Custo total exibido

---

## 🎨 Dicas de Briefing

**Bom:**
```
Crie vídeo promocional do app OMA:
1. Pessoa frustrada com tarefas
2. Logo OMA aparecendo
3. Pessoa feliz usando app
4. Resultados e benefícios
5. Call-to-action
```

**Evitar:**
```
Fazer vídeo legal
```

---

## 🔧 Troubleshooting

**Vídeo não gerou:**
- Verifique se FFmpeg está instalado
- Confirme que as APIs estão configuradas no .env

**Custo muito alto:**
- Sistema prioriza Pexels (grátis) automaticamente
- Stability só é usado quando necessário

**Qualidade ruim:**
- Use descrições mais detalhadas
- Especifique melhor as cenas desejadas

---

## 📞 Suporte

Ver documentação completa em:
- `README_PARA_DASHBOARD.md`
- `SISTEMA_FUNCIONANDO.md`
            """)

    gr.Markdown("""
    ---
    **OMA Video Dashboard** v1.0 - Geração automatizada de vídeos profissionais
    """)


if __name__ == "__main__":
    print("========================================")
    print(">> OMA VIDEO DASHBOARD")
    print("========================================")
    print("")
    print("Dashboard iniciando em: http://localhost:7860")
    print("")
    print("Sistema pronto para gerar videos!")
    print("========================================")

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
