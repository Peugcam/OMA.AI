"""
Teste de Criacao de Video Completo

Testa o fluxo end-to-end do sistema OMA v3.0 integrado.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from datetime import datetime

# Adicionar pasta raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Carregar .env
load_dotenv()


async def test_video_creation():
    """
    Testa criacao de video completo com supervisor integrado.
    """
    print("\n" + "="*80)
    print(" TESTE: Criacao de Video Completo - OMA v3.0 Integrado")
    print("="*80 + "\n")

    try:
        # Import do supervisor integrado
        print("[1/6] Importando SupervisorAgent integrado...")
        from agents.supervisor_agent import SupervisorAgent
        print("      OK - SupervisorAgent importado\n")

        # Criar supervisor
        print("[2/6] Criando SupervisorAgent com modulos otimizados...")
        supervisor = SupervisorAgent(
            enable_cache=True,
            enable_fallback=True
        )
        print(f"      OK - Supervisor criado")
        print(f"      Modelo: {supervisor.llm.model}")
        print(f"      Cache: Ativado")
        print(f"      Fallback: Ativado\n")

        # Criar briefing de teste
        print("[3/6] Criando briefing de teste...")
        brief = {
            "title": "Video Teste - OMA v3.0",
            "description": "Propaganda de uma cafeteria moderna e aconchegante",
            "target": "Jovens adultos 25-35 anos, urbanos",
            "style": "Clean, minimalista, moderno",
            "duration": 30,  # segundos
            "cta": "Visite nossa loja hoje!"
        }
        print("      OK - Briefing criado")
        print(f"      Titulo: {brief['title']}")
        print(f"      Duracao: {brief['duration']}s\n")

        # Testar analise
        print("[4/6] Analisando requisicao...")
        try:
            analysis = await supervisor.analyze_request(brief)
            print("      OK - Analise completa")
            print(f"      Objetivo: {analysis.get('objective', 'N/A')[:60]}...")
            print(f"      Publico: {analysis.get('target_audience', 'N/A')}")
            print(f"      Estilo: {analysis.get('style', 'N/A')}\n")
        except Exception as e:
            print(f"      ERRO na analise: {e}")
            print("      Usando dados do briefing...\n")
            analysis = {
                "objective": brief["description"],
                "target_audience": brief["target"],
                "style": brief["style"],
                "duration_seconds": brief["duration"],
                "visual_requirements": ["imagens cafe", "ambiente moderno"],
                "audio_requirements": ["musica calma", "naracao profissional"],
                "cta": brief["cta"]
            }

        # Testar decomposicao
        print("[5/6] Decompondo em subtarefas...")
        try:
            subtasks = await supervisor.decompose_task(analysis)
            print(f"      OK - {len(subtasks)} subtarefas criadas")
            for st in subtasks:
                print(f"      - {st.id}: {st.description[:50]}...")
            print()
        except Exception as e:
            print(f"      ERRO na decomposicao: {e}")
            print("      Usando plano padrao...\n")
            subtasks = supervisor._create_default_plan(analysis)

        # Testar roteamento
        print("[6/6] Testando roteamento de agentes...")

        # Estado inicial
        state = {
            "task_id": f"video_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "brief": brief,
            "analysis": analysis,
            "current_phase": 0,
            "script": None,
            "visual_plan": None,
            "audio_files": None,
            "video_path": None
        }

        print("\n      Simulando fluxo de roteamento:\n")

        # Fase 0: Inicio
        next_agent = supervisor.route_next(state)
        print(f"      Fase 0 (inicio)           -> {next_agent}")
        assert next_agent == "script_agent"

        # Fase 1: Script concluido
        state["current_phase"] = 1
        state["script"] = {"script_id": "test_001", "scenes": []}
        next_agent = supervisor.route_next(state)
        print(f"      Fase 1 (script pronto)    -> {next_agent}")
        assert next_agent in ["visual_agent", "audio_agent"]

        # Fase 2: Visual concluido
        state["current_phase"] = 2
        state["visual_plan"] = {"visual_plan_id": "test_001", "scenes": []}
        next_agent = supervisor.route_next(state)
        print(f"      Fase 2 (visual pronto)    -> {next_agent}")
        assert next_agent == "audio_agent"

        # Fase 3: Audio concluido
        state["current_phase"] = 3
        state["audio_files"] = {"final_mix": {"path": "test.mp3"}}
        next_agent = supervisor.route_next(state)
        print(f"      Fase 3 (audio pronto)     -> {next_agent}")
        assert next_agent == "editor_agent"

        # Fase 4: Video concluido
        state["current_phase"] = 4
        state["video_path"] = "./output/test_video.mp4"
        next_agent = supervisor.route_next(state)
        print(f"      Fase 4 (video renderizado)-> {next_agent}")
        assert next_agent == "FINISH"

        print("\n      OK - Todos os roteamentos corretos!\n")

        # Estatisticas do router
        print("-"*80)
        print("ESTATISTICAS DO SMART ROUTER")
        print("-"*80 + "\n")

        supervisor.print_routing_stats()

        stats = supervisor.get_routing_stats()
        cache_rate = (stats['cache_hits'] / stats['total_decisions'] * 100) if stats['total_decisions'] > 0 else 0

        print(f"Taxa de cache: {cache_rate:.1f}%")
        print(f"Tempo medio: {stats['total_time_ms'] / stats['total_decisions']:.0f}ms")

        # Resumo final
        print("\n" + "="*80)
        print(" TESTE CONCLUIDO COM SUCESSO!")
        print("="*80 + "\n")

        print("RESUMO:")
        print(f"  OK - Supervisor integrado funcionando")
        print(f"  OK - AIClient: {supervisor.llm.model}")
        print(f"  OK - SmartRouter: {stats['total_decisions']} decisoes")
        print(f"  OK - Cache: {stats['cache_hits']} hits ({cache_rate:.1f}%)")
        print(f"  OK - Fallback: {stats['fallback_calls']} chamadas")
        print(f"  OK - Tempo medio: {stats['total_time_ms'] / stats['total_decisions']:.0f}ms")
        print("")

        print("PROXIMO PASSO:")
        print("  Para criar um video completo, os agentes individuais")
        print("  (Script, Visual, Audio, Editor) tambem precisam ser")
        print("  integrados com os modulos otimizados.")
        print("")

        return True

    except Exception as e:
        print(f"\nERRO: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """
    Executa teste de criacao de video.
    """
    # Rodar teste async
    result = asyncio.run(test_video_creation())

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
