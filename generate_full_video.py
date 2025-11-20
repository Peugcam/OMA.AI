"""
🎬 Geração Completa de Vídeo - OMA App
=======================================

Este script executa o pipeline COMPLETO:
1. Supervisor - Análise
2. Script Agent - Roteiro
3. Visual Agent - Mídia (Pexels + Stability)
4. Audio Agent - TTS + Música
5. Editor Agent - Montagem Final

Resultado: Vídeo MP4 pronto para publicar!
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
import json

# Imports dos agentes
from agents.supervisor_agent import SupervisorAgent
from agents.script_agent import ScriptAgent
from agents.visual_agent import VisualAgent
from agents.audio_agent import AudioAgent
from agents.editor_agent import EditorAgent

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# BRIEFING - DINAMICO (pode ser customizado via argumento)
# ============================================================================

def create_briefing(theme=None):
    """Cria briefing baseado no tema fornecido"""

    if not theme:
        # Briefing padrão - OMA APP
        return {
            "title": "OMA - Produtividade com IA",
            "description": """
Anúncio moderno e impactante para o OMA App de Produtividade:

**ESTRUTURA:**
1. Pessoa frustrada com múltiplas tarefas (problema)
2. Montagem rápida: caos, desorganização (dor)
3. Logo OMA aparecendo holograficamente (solução)
4. Pessoa feliz usando o app (transformação)
5. Benefícios: produtividade aumentando (resultado)
6. Call-to-action: Baixe grátis (ação)

**MENSAGEM:** Organize sua vida. Conquiste objetivos. Seja produtivo com IA.
""",
            "duration": 30,
            "target_audience": "Profissionais 25-40 anos",
            "style": "modern, tech, motivational",
            "tone": "inspirational",
            "cta": "Baixe o OMA grátis agora!",
        }
    else:
        # Briefing customizado baseado no tema
        return {
            "title": theme,
            "description": f"""
Crie um vídeo promocional impactante sobre: {theme}

**ESTRUTURA:**
1. Apresente o problema ou necessidade
2. Mostre a dor ou frustração atual
3. Introduza a solução (produto/serviço)
4. Demonstre a transformação positiva
5. Destaque os principais benefícios
6. Call-to-action claro e direto

**MENSAGEM:** Comunique o valor principal de forma clara e persuasiva.
""",
            "duration": 30,
            "target_audience": "Público geral",
            "style": "modern, engaging, professional",
            "tone": "persuasive",
            "cta": "Saiba mais agora!",
        }


# ============================================================================
# PIPELINE COMPLETO
# ============================================================================

async def generate_complete_video(theme=None):
    """
    Executa pipeline completo de geração de vídeo

    Args:
        theme: Tema customizado para o vídeo (opcional)
    """

    # Criar briefing baseado no tema
    briefing = create_briefing(theme)

    logger.info("="*70)
    logger.info(f"🎬 PIPELINE COMPLETO - {briefing['title']}")
    logger.info("="*70)
    logger.info("")

    # Criar diretórios
    output_dir = Path("./outputs")
    output_dir.mkdir(exist_ok=True)

    # Estado inicial
    state = {
        "brief": briefing,
        "task_id": f"oma_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "created_at": datetime.now().isoformat(),
        "current_phase": 0
    }

    try:
        # ================================================================
        # FASE 1: SUPERVISOR - Análise
        # ================================================================
        logger.info("📋 FASE 1/5: Supervisor analisando briefing...")

        supervisor = SupervisorAgent()
        state = await supervisor.analyze_request(state)

        logger.info("✅ Análise completa!")
        logger.info("")

        # ================================================================
        # FASE 2: SCRIPT AGENT - Roteiro
        # ================================================================
        logger.info("📝 FASE 2/5: Gerando roteiro criativo...")

        script_agent = ScriptAgent()
        state = await script_agent.generate_script(state)

        scenes = state.get("script", {}).get("scenes", [])
        logger.info(f"✅ Roteiro: {len(scenes)} cenas")
        logger.info("")

        # ================================================================
        # FASE 3: VISUAL AGENT - Mídia Híbrida
        # ================================================================
        logger.info("🎨 FASE 3/5: Buscando/gerando mídia (Pexels + Stability)...")

        visual_agent = VisualAgent()
        state = await visual_agent.plan_visuals(state)

        visual_scenes = state.get("visual_plan", {}).get("scenes", [])
        pexels_count = sum(1 for s in visual_scenes if s.get("source") == "pexels")
        stability_count = len(visual_scenes) - pexels_count
        total_cost = sum(s.get("cost", 0) for s in visual_scenes)

        logger.info(f"✅ Mídia: {len(visual_scenes)} cenas")
        logger.info(f"   📹 Pexels: {pexels_count} (grátis)")
        logger.info(f"   🎨 Stability: {stability_count} (${total_cost:.2f})")
        logger.info("")

        # ================================================================
        # FASE 4: AUDIO AGENT - TTS + Música
        # ================================================================
        logger.info("🎙️ FASE 4/5: Gerando áudio (narração + música)...")

        audio_agent = AudioAgent()
        state = await audio_agent.produce_audio(state)

        audio_files = state.get("audio_files", {})
        narration = audio_files.get("narration", {})
        music = audio_files.get("background_music")

        logger.info(f"✅ Áudio gerado:")
        logger.info(f"   🎤 Narração: {narration.get('path', 'N/A')}")
        logger.info(f"   🎵 Música: {music if music else 'N/A'}")
        logger.info("")

        # ================================================================
        # FASE 5: EDITOR AGENT - Montagem Final
        # ================================================================
        logger.info("✂️ FASE 5/5: Montando vídeo final (FFmpeg)...")

        editor_agent = EditorAgent()
        state = await editor_agent.edit_video(state)

        video_path = state.get("video_path")
        metadata = state.get("metadata", {})

        logger.info(f"✅ Vídeo montado:")
        logger.info(f"   📹 Path: {video_path}")
        logger.info(f"   ⏱️  Duração: {metadata.get('duration_seconds', 0)}s")
        logger.info(f"   📏 Resolução: {metadata.get('resolution', 'N/A')}")
        logger.info(f"   💾 Tamanho: {metadata.get('file_size_mb', 0):.1f} MB")
        logger.info("")

        # ================================================================
        # RESUMO FINAL
        # ================================================================
        logger.info("="*70)
        logger.info("🎉 VÍDEO COMPLETO GERADO COM SUCESSO!")
        logger.info("="*70)
        logger.info("")
        logger.info(f"📁 Arquivo: {video_path}")
        logger.info(f"⏱️  Duração: {metadata.get('duration_seconds', 0)}s")
        logger.info(f"🎬 Cenas: {len(scenes)}")
        logger.info(f"💰 Custo total: ${total_cost:.4f}")
        logger.info("")
        logger.info("📊 Breakdown:")
        logger.info(f"   • Script: {len(scenes)} cenas")
        logger.info(f"   • Visual: {pexels_count} Pexels + {stability_count} Stability")
        logger.info(f"   • Audio: Narração + Música")
        logger.info(f"   • Editor: Montagem FFmpeg")
        logger.info("")
        logger.info("✅ Pronto para publicar!")
        logger.info("="*70)

        # Salvar metadata completo
        result_path = output_dir / f"oma_app_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump({
                "briefing": briefing,
                "video_path": str(video_path),
                "metadata": metadata,
                "stats": {
                    "scenes": len(scenes),
                    "pexels_scenes": pexels_count,
                    "stability_scenes": stability_count,
                    "total_cost": total_cost
                },
                "timestamp": datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Metadata salvo: {result_path}")
        logger.info("")

        return True, video_path

    except Exception as e:
        logger.error(f"❌ Erro durante pipeline: {e}", exc_info=True)
        return False, None


# ============================================================================
# EXECUTAR
# ============================================================================

if __name__ == "__main__":
    import sys

    # Verificar se foi fornecido um tema
    theme = None
    if len(sys.argv) > 1:
        theme = " ".join(sys.argv[1:])

    print("\n")
    print("="*70)
    if theme:
        print(f">> GERANDO VIDEO: {theme}")
    else:
        print(">> INICIANDO GERACAO COMPLETA DO VIDEO OMA APP")
    print("="*70)
    print("\n")
    print("Tempo estimado: 2-3 minutos")
    print("Custo estimado: $0.00 - $0.10")
    print("\n")
    print("Pipeline:")
    print("   1. Supervisor -> Analise")
    print("   2. Script -> Roteiro")
    print("   3. Visual -> Midia (Pexels/Stability)")
    print("   4. Audio -> Narracao + Musica")
    print("   5. Editor -> Montagem Final")
    print("\n")
    print("="*70)
    print("\n")

    success, video_path = asyncio.run(generate_complete_video(theme))

    if success:
        print("\n")
        print("="*70)
        print(">> SUCESSO! VIDEO GERADO!")
        print("="*70)
        print(f"\nAssista: {video_path}")
        print("\n")
    else:
        print("\n")
        print("="*70)
        print(">> ERRO NA GERACAO")
        print("="*70)
        print("\nVerifique os logs acima para detalhes.")
        print("\n")
