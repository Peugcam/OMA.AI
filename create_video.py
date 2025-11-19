"""
Criar Video Completo - OMA v3.0

Script para criar um video completo do inicio ao fim.
Usa todos os agentes integrados com modulos otimizados.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from agents.supervisor_agent import SupervisorAgent
from agents.script_agent import ScriptAgent
from agents.visual_agent import VisualAgent
from agents.audio_agent import AudioAgent
from agents.editor_agent import EditorAgent


async def create_video(brief: dict):
    """
    Cria video completo baseado no briefing.

    Args:
        brief: Briefing do video

    Returns:
        Estado final com video_path
    """
    print("\n" + "="*80)
    print(" CRIANDO VIDEO COMPLETO - OMA v3.0")
    print("="*80 + "\n")

    # Estado inicial
    state = {
        "task_id": f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "brief": brief,
        "current_phase": 0,
        "script": None,
        "visual_plan": None,
        "audio_files": None,
        "video_path": None
    }

    # Criar supervisor
    print("[SUPERVISOR] Inicializando...")
    supervisor = SupervisorAgent()
    print(f"             Modelo: {supervisor.llm.model}")
    print(f"             Cache: Ativado\n")

    # FASE 1: SCRIPT
    print("="*80)
    print(" FASE 1: GERACAO DE ROTEIRO")
    print("="*80 + "\n")

    next_agent = supervisor.route_next(state)
    print(f"[SUPERVISOR] Proximo agente: {next_agent}\n")

    if next_agent == "script_agent":
        print("[SCRIPT] Gerando roteiro criativo...")
        script_agent = ScriptAgent()
        print(f"         Modelo: {script_agent.llm.model}")

        # Adicionar analise ao estado
        print("[SCRIPT] Analisando briefing...")
        state["analysis"] = {
            "objective": brief.get("description", ""),
            "target_audience": brief.get("target", ""),
            "style": brief.get("style", ""),
            "duration_seconds": brief.get("duration", 30),
            "cta": brief.get("cta", "")
        }

        state = await script_agent.generate_script(state)

        script = state.get("script")
        print(f"\n[SCRIPT] OK - Roteiro gerado!")
        print(f"         Titulo: {script.get('title')}")
        print(f"         Cenas: {len(script.get('scenes', []))}")
        print(f"         Duracao: {script.get('duration_seconds')}s")
        print(f"         Modelo: {script.get('model')}\n")

    # FASE 2: VISUAL
    print("="*80)
    print(" FASE 2: GERACAO DE IMAGENS")
    print("="*80 + "\n")

    next_agent = supervisor.route_next(state)
    print(f"[SUPERVISOR] Proximo agente: {next_agent}\n")

    if next_agent == "visual_agent":
        print("[VISUAL] Gerando imagens com Stability AI...")
        visual_agent = VisualAgent()
        print(f"         Modelo: {visual_agent.llm.model}")
        print(f"         Stability AI: {'OK' if visual_agent.stability_api_key else 'Placeholder'}")

        state = await visual_agent.plan_visuals(state)

        visual_plan = state.get("visual_plan")
        print(f"\n[VISUAL] OK - Imagens geradas!")
        print(f"         Cenas visuais: {len(visual_plan.get('scenes', []))}\n")

    # FASE 3: AUDIO
    print("="*80)
    print(" FASE 3: PRODUCAO DE AUDIO")
    print("="*80 + "\n")

    next_agent = supervisor.route_next(state)
    print(f"[SUPERVISOR] Proximo agente: {next_agent}\n")

    if next_agent == "audio_agent":
        print("[AUDIO] Gerando narracao com Edge TTS...")
        audio_agent = AudioAgent()
        print(f"        Modelo: {audio_agent.llm.model}")
        print(f"        Edge TTS: {'OK' if audio_agent.tts_available else 'Placeholder'}")

        state = await audio_agent.produce_audio(state)

        audio_files = state.get("audio_files")
        print(f"\n[AUDIO] OK - Audio produzido!")
        print(f"        Narracao: {audio_files.get('narration_file')}\n")

    # FASE 4: EDICAO
    print("="*80)
    print(" FASE 4: MONTAGEM DO VIDEO")
    print("="*80 + "\n")

    next_agent = supervisor.route_next(state)
    print(f"[SUPERVISOR] Proximo agente: {next_agent}\n")

    if next_agent == "editor_agent":
        print("[EDITOR] Montando video com FFmpeg...")
        editor_agent = EditorAgent()
        print(f"         Modelo: {editor_agent.llm.model}")
        print(f"         FFmpeg: {'OK' if editor_agent.ffmpeg_available else 'Placeholder'}")

        state = await editor_agent.edit_video(state)

        video_path = state.get("video_path")
        print(f"\n[EDITOR] OK - Video renderizado!")
        print(f"         Path: {video_path}\n")

    # FINALIZACAO
    print("="*80)
    print(" FINALIZACAO")
    print("="*80 + "\n")

    next_agent = supervisor.route_next(state)
    print(f"[SUPERVISOR] Status final: {next_agent}\n")

    # Estatisticas do router
    print("-"*80)
    print("ESTATISTICAS DO SMART ROUTER")
    print("-"*80 + "\n")
    supervisor.print_routing_stats()

    # Resumo final
    print("\n" + "="*80)
    print(" VIDEO CRIADO COM SUCESSO!")
    print("="*80 + "\n")

    print("RESUMO:")
    print(f"  Task ID: {state['task_id']}")
    print(f"  Titulo: {state['script'].get('title')}")
    print(f"  Cenas: {len(state['script'].get('scenes', []))}")
    print(f"  Video: {state['video_path']}")
    print("")

    return state


async def main():
    """
    Executa criacao de video completo.
    """
    # Briefing de exemplo
    brief = {
        "title": "Cafeteria Moderna - Video Teste",
        "description": "Propaganda de cafeteria aconchegante com cafe especial artesanal",
        "target": "Jovens adultos 25-35 anos, urbanos, apreciadores de cafe",
        "style": "Clean, minimalista, moderno, acolhedor",
        "duration": 20,  # 20 segundos (mais rapido para teste)
        "cta": "Visite nossa loja e experimente nosso cafe especial!"
    }

    print("BRIEFING DO VIDEO:")
    print(f"  Titulo: {brief['title']}")
    print(f"  Descricao: {brief['description']}")
    print(f"  Publico: {brief['target']}")
    print(f"  Duracao: {brief['duration']}s")

    try:
        state = await create_video(brief)

        print("\nPRONTO! Verifique o video em:")
        print(f"  {state['video_path']}")
        print("")

        return 0

    except Exception as e:
        print(f"\nERRO ao criar video: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
