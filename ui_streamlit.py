"""
🎨 OMA v3.0 - Interface Streamlit
===================================

Interface web com dashboard avançado e analytics.

Vantagens do Streamlit:
- Customização total do UI
- Gráficos e dashboards complexos
- Estado da sessão persistente
- Widgets avançados

Instalação:
pip install streamlit plotly

Uso:
streamlit run ui_streamlit.py
"""

import streamlit as st
import asyncio
from pathlib import Path
from datetime import datetime
import json

# Import dos agentes
from agents.supervisor_agent import SupervisorAgent
from core.state_graph import VideoState


# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="OMA - Criador de Vídeos com IA",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# ESTILO CUSTOMIZADO
# ============================================================================

st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }

    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }

    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }

    .agent-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 1rem;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.2rem;
    }

    .supervisor { background: #667eea; color: white; }
    .script { background: #f093fb; color: white; }
    .visual { background: #4facfe; color: white; }
    .audio { background: #43e97b; color: white; }
    .editor { background: #fa709a; color: white; }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# ESTADO DA SESSÃO
# ============================================================================

if 'videos_created' not in st.session_state:
    st.session_state.videos_created = []

if 'current_task_id' not in st.session_state:
    st.session_state.current_task_id = None

if 'generation_history' not in st.session_state:
    st.session_state.generation_history = []


# ============================================================================
# SIDEBAR - CONFIGURAÇÕES
# ============================================================================

with st.sidebar:
    st.markdown("## ⚙️ Configurações")

    st.markdown("### 🤖 Agentes Ativos")

    agents_status = {
        "Supervisor (Qwen2.5-3B)": True,
        "Script (Phi-3.5-Mini)": True,
        "Visual (Gemma-2-2B)": True,
        "Audio (Mistral-7B)": True,
        "Editor (Qwen2-1.5B)": True
    }

    for agent, status in agents_status.items():
        st.checkbox(agent, value=status, disabled=True)

    st.markdown("---")

    st.markdown("### 📊 Estatísticas")
    st.metric("Vídeos Criados", len(st.session_state.videos_created))
    st.metric("Tempo Médio", "4.2 min")
    st.metric("Custo Total", "$0.00")

    st.markdown("---")

    st.markdown("### 🔗 Links Rápidos")
    st.markdown("[📚 Documentação](https://github.com/Peugcam/OMA_v3)")
    st.markdown("[🐛 Reportar Bug](https://github.com/Peugcam/OMA_v3/issues)")
    st.markdown("[💬 Discord](https://discord.gg/oma)")


# ============================================================================
# MAIN - HEADER
# ============================================================================

st.markdown('<h1 class="main-header">🎬 OMA v3.0</h1>', unsafe_allow_html=True)
st.markdown("### Criador de Vídeos com IA Multi-Agente")

st.markdown("""
<div class="status-box">
Sistema multi-agente que coordena 5 SLMs especializados para criar vídeos profissionais em minutos.
<br><br>
<span class="agent-badge supervisor">🧠 Supervisor</span>
<span class="agent-badge script">📝 Script</span>
<span class="agent-badge visual">🎨 Visual</span>
<span class="agent-badge audio">🎙️ Audio</span>
<span class="agent-badge editor">✂️ Editor</span>
</div>
""", unsafe_allow_html=True)


# ============================================================================
# TABS PRINCIPAIS
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "🎬 Criar Vídeo",
    "📜 Histórico",
    "📊 Analytics",
    "⚙️ Configurações Avançadas"
])


# ============================================================================
# TAB 1: CRIAR VÍDEO
# ============================================================================

with tab1:
    st.markdown("## 📝 Informações do Vídeo")

    col1, col2 = st.columns([2, 1])

    with col1:
        description = st.text_area(
            "Descrição do Vídeo",
            placeholder="Ex: Propaganda para cafeteria moderna focada em millennials...",
            height=100,
            help="Descreva o objetivo e contexto do vídeo"
        )

        target_audience = st.text_input(
            "Público-Alvo",
            placeholder="Ex: Millennials urbanos, 25-35 anos",
            help="Quem deve assistir este vídeo?"
        )

    with col2:
        duration = st.slider(
            "Duração (segundos)",
            min_value=10,
            max_value=120,
            value=30,
            step=5,
            help="Entre 10 e 120 segundos"
        )

        style = st.selectbox(
            "Estilo Visual",
            [
                "Clean e minimalista",
                "Dinâmico e energético",
                "Corporativo profissional",
                "Criativo e artístico",
                "Casual e amigável"
            ],
            help="Tom visual do vídeo"
        )

    cta = st.text_input(
        "Call-to-Action",
        placeholder="Ex: Visite nosso site em www.exemplo.com",
        help="O que o espectador deve fazer?"
    )

    st.markdown("---")

    # Botões
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])

    with col_btn1:
        create_btn = st.button(
            "🎬 Criar Vídeo",
            type="primary",
            use_container_width=True
        )

    with col_btn2:
        example = st.selectbox(
            "Carregar exemplo",
            ["", "Cafeteria", "E-commerce", "Tech Startup"]
        )

    with col_btn3:
        clear_btn = st.button("🗑️ Limpar", use_container_width=True)

    # Lógica de criação
    if create_btn:
        if not description or len(description) < 10:
            st.error("❌ Descrição muito curta (mín 10 caracteres)")
        elif duration < 10 or duration > 120:
            st.error("❌ Duração deve estar entre 10-120 segundos")
        else:
            # Criar brief
            brief = {
                "description": description,
                "target": target_audience,
                "duration": duration,
                "style": style,
                "cta": cta,
                "timestamp": datetime.now().isoformat()
            }

            # Progress bar e status
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                # Inicializar estado
                state = VideoState(
                    task_id=f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    brief=brief,
                    created_at=datetime.now().isoformat(),
                    current_phase=0,
                    completed_tasks=[],
                    failed_tasks=[],
                    errors=[],
                    is_complete=False
                )

                # Supervisor
                supervisor = SupervisorAgent()

                # FASE 1: Análise (10%)
                status_text.markdown("🔍 **Fase 1/5:** Analisando requisição...")
                progress_bar.progress(10)

                # Nota: Como streamlit não suporta async nativamente,
                # precisamos usar asyncio.run()
                analysis = asyncio.run(supervisor.analyze_request(brief))
                state['analysis'] = analysis
                progress_bar.progress(20)

                # FASE 2: Decomposição (30%)
                status_text.markdown("🔨 **Fase 2/5:** Criando plano de execução...")
                progress_bar.progress(30)

                subtasks = asyncio.run(supervisor.decompose_task(analysis))
                plan = supervisor.create_execution_plan(subtasks)
                state['execution_plan'] = plan
                progress_bar.progress(40)

                # FASE 3: Execução (40-80%)
                status_text.markdown(f"🚀 **Fase 3/5:** Executando {len(plan.subtasks)} tarefas...")

                success, final_state = asyncio.run(supervisor.execute_plan(plan, state))
                progress_bar.progress(80)

                if not success:
                    errors = [st.error for st in plan.subtasks if st.error]
                    st.error(f"❌ Falha na execução:\n" + "\n".join(errors))
                else:
                    # FASE 4: Validação (90%)
                    status_text.markdown("✅ **Fase 4/5:** Validando resultado...")
                    progress_bar.progress(90)

                    is_valid, issues = asyncio.run(supervisor.validate_output(final_state))

                    if not is_valid:
                        st.warning(f"⚠️ Problemas encontrados:\n" + "\n".join(issues))
                    else:
                        # SUCESSO!
                        progress_bar.progress(100)
                        status_text.markdown("🎉 **Vídeo criado com sucesso!**")

                        video_path = final_state.get('video_path')
                        metadata = final_state.get('metadata', {})

                        # Adicionar ao histórico
                        st.session_state.videos_created.append({
                            "task_id": state['task_id'],
                            "video_path": video_path,
                            "metadata": metadata,
                            "brief": brief,
                            "created_at": datetime.now()
                        })

                        # Mostrar vídeo
                        st.markdown("---")
                        st.markdown("## 🎥 Resultado")

                        col_video, col_meta = st.columns([2, 1])

                        with col_video:
                            st.video(video_path)

                        with col_meta:
                            st.markdown("### 📊 Estatísticas")
                            st.metric("Duração", f"{metadata.get('duration_seconds', 0)}s")
                            st.metric("Resolução", metadata.get('resolution', 'N/A'))
                            st.metric("Tamanho", f"{metadata.get('file_size_mb', 0):.1f} MB")
                            st.metric("Tempo de Render", f"{metadata.get('rendering_time_seconds', 0)}s")

                            st.markdown("### 🎬 Detalhes")
                            st.write(f"**Cenas:** {len(final_state.get('script', {}).get('scenes', []))}")
                            st.write(f"**Clipes:** {len(final_state.get('visual_plan', {}).get('scenes', []))}")

                            # Botão de download
                            with open(video_path, 'rb') as f:
                                st.download_button(
                                    "⬇️ Baixar Vídeo",
                                    f,
                                    file_name=Path(video_path).name,
                                    mime="video/mp4"
                                )

            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
                progress_bar.empty()
                status_text.empty()

    # Carregar exemplo
    if example and example != "":
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
                "style": "Dinâmico e energético",
                "cta": "Compre agora com 20% OFF"
            },
            "Tech Startup": {
                "description": "Apresentação de app inovador de produtividade",
                "target": "Profissionais 25-40 anos",
                "duration": 45,
                "style": "Corporativo profissional",
                "cta": "Baixe grátis hoje"
            }
        }

        ex = examples[example]
        st.rerun()  # Recarregar com os valores


# ============================================================================
# TAB 2: HISTÓRICO
# ============================================================================

with tab2:
    st.markdown("## 📜 Histórico de Vídeos")

    if not st.session_state.videos_created:
        st.info("Nenhum vídeo criado ainda. Use a aba 'Criar Vídeo' para começar!")
    else:
        for video in reversed(st.session_state.videos_created):
            with st.expander(f"🎬 {video['task_id']} - {video['created_at'].strftime('%d/%m/%Y %H:%M')}"):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.video(video['video_path'])

                with col2:
                    st.json(video['brief'])

                    with open(video['video_path'], 'rb') as f:
                        st.download_button(
                            "⬇️ Baixar",
                            f,
                            file_name=Path(video['video_path']).name,
                            key=f"download_{video['task_id']}"
                        )


# ============================================================================
# TAB 3: ANALYTICS
# ============================================================================

with tab3:
    st.markdown("## 📊 Analytics e Performance")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total de Vídeos", len(st.session_state.videos_created))
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Tempo Médio", "4.2 min")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Custo Total", "$0.00")
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Taxa de Sucesso", "100%")
        st.markdown('</div>', unsafe_allow_html=True)

    # Gráficos (placeholder - requer plotly)
    st.markdown("### 📈 Tendências")
    st.info("Gráficos de performance serão adicionados aqui com mais dados")


# ============================================================================
# TAB 4: CONFIGURAÇÕES AVANÇADAS
# ============================================================================

with tab4:
    st.markdown("## ⚙️ Configurações Avançadas")

    st.markdown("### 🤖 Modelos SLM")

    models_config = {
        "Supervisor": {"model": "qwen2.5:3b-instruct", "temp": 0.3},
        "Script": {"model": "phi3.5:3.8b-mini", "temp": 0.7},
        "Visual": {"model": "gemma2:2b", "temp": 0.5},
        "Audio": {"model": "mistral:7b-instruct", "temp": 0.6},
        "Editor": {"model": "qwen2:1.5b", "temp": 0.2}
    }

    for agent, config in models_config.items():
        with st.expander(f"{agent} Agent"):
            st.text_input("Modelo", config["model"], disabled=True)
            st.slider("Temperature", 0.0, 1.0, config["temp"], 0.1, disabled=True)

    st.markdown("### 🔧 Performance")

    col1, col2 = st.columns(2)

    with col1:
        st.number_input("Max Concurrent Jobs", value=3, min_value=1, max_value=10)
        st.number_input("Request Timeout (s)", value=300, min_value=60, max_value=600)

    with col2:
        st.number_input("Max Retries", value=3, min_value=1, max_value=5)
        st.checkbox("Enable Cost Tracking", value=True)


# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p><strong>OMA v3.0</strong> - Sistema Multi-Agente com SLMs Locais</p>
    <p>Desenvolvido com ❤️ | 🌟 <a href="https://github.com/Peugcam/OMA_v3">GitHub</a> | 📚 <a href="#">Documentação</a></p>
</div>
""", unsafe_allow_html=True)
