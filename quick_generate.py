"""
🚀 Geração Rápida de Vídeo - Para Dashboard
===========================================

Script simplificado para chamar via dashboard/API.
Recebe briefing via argumentos ou JSON.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

from agents.supervisor_agent import SupervisorAgent
from agents.script_agent import ScriptAgent
from agents.visual_agent import VisualAgent
from agents.audio_agent import AudioAgent
from agents.editor_agent import EditorAgent


async def generate_video(briefing: dict) -> dict:
    """
    Gera vídeo completo a partir de briefing.

    Args:
        briefing: Dict com title, description, duration, etc

    Returns:
        Dict com video_path, metadata, cost
    """

    # DEBUG: Print briefing recebido
    print("\n" + "="*70)
    print("📥 QUICK_GENERATE - Briefing Recebido:")
    print("="*70)
    print(json.dumps(briefing, indent=2, ensure_ascii=False))
    print("="*70 + "\n")

    # Estado inicial
    state = {
        "brief": briefing,
        "task_id": f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "created_at": datetime.now().isoformat(),
        "current_phase": 0
    }

    print(f"📊 Estado inicial criado: task_id={state['task_id']}")
    print(f"📋 Briefing no state: {state['brief'].get('title', 'N/A')}\n")

    try:
        # Fase 1: Análise
        supervisor = SupervisorAgent()

        # DEBUG: Verificar briefing antes de passar
        print(f"🔍 Passando briefing para supervisor:")
        print(f"   Título: {state['brief'].get('title', 'N/A')}")
        print(f"   Descrição: {state['brief'].get('description', 'N/A')[:100]}...\n")

        # Passar apenas o brief (não o state inteiro)
        analysis = await supervisor.analyze_request(state["brief"])
        state["analysis"] = analysis

        # Fase 2: Roteiro
        script_agent = ScriptAgent()
        state = await script_agent.generate_script(state)

        # Fase 3: Visual
        visual_agent = VisualAgent()
        state = await visual_agent.plan_visuals(state)

        # Fase 4: Audio
        audio_agent = AudioAgent()
        state = await audio_agent.produce_audio(state)

        # Fase 5: Edição
        editor_agent = EditorAgent()
        state = await editor_agent.edit_video(state)

        # Calcular custo
        visual_scenes = state.get("visual_plan", {}).get("scenes", [])
        total_cost = sum(s.get("cost", 0) for s in visual_scenes)

        return {
            "success": True,
            "video_path": state.get("video_path"),
            "metadata": state.get("metadata", {}),
            "cost": total_cost,
            "scenes": len(visual_scenes),
            "script": state.get("script", {}),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def main():
    """
    Executa geração via CLI ou JSON file.

    Uso:
        python quick_generate.py briefing.json

    ou:

        python quick_generate.py --title "Meu Vídeo" --description "..."
    """

    if len(sys.argv) < 2:
        print("Erro: Forneça um arquivo JSON ou argumentos")
        print("\nUso:")
        print("  python quick_generate.py briefing.json")
        print("  python quick_generate.py --title 'Título' --description '...'")
        sys.exit(1)

    # Opção 1: Arquivo JSON
    if sys.argv[1].endswith('.json'):
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            briefing = json.load(f)

    # Opção 2: Argumentos CLI
    else:
        briefing = {
            "title": sys.argv[2] if len(sys.argv) > 2 else "Vídeo OMA",
            "description": sys.argv[3] if len(sys.argv) > 3 else "Vídeo gerado automaticamente",
            "duration": int(sys.argv[4]) if len(sys.argv) > 4 else 30,
            "target_audience": sys.argv[5] if len(sys.argv) > 5 else "Público geral",
            "style": sys.argv[6] if len(sys.argv) > 6 else "professional",
            "tone": sys.argv[7] if len(sys.argv) > 7 else "neutral",
            "cta": sys.argv[8] if len(sys.argv) > 8 else "Saiba mais!"
        }

    print(f"\n🎬 Gerando vídeo: {briefing['title']}")
    print(f"⏱️  Duração: {briefing['duration']}s")
    print(f"🎯 Público: {briefing['target_audience']}\n")

    # Gerar
    result = asyncio.run(generate_video(briefing))

    # Resultado
    if result["success"]:
        print("\n✅ SUCESSO!")
        print(f"\n📹 Vídeo: {result['video_path']}")
        print(f"💰 Custo: ${result['cost']:.4f}")
        print(f"🎬 Cenas: {result['scenes']}")

        # Salvar resultado JSON
        output_file = Path("./outputs") / f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_file.parent.mkdir(exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Metadata: {output_file}")

    else:
        print("\n❌ ERRO!")
        print(f"\n{result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
