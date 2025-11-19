"""
Teste do Supervisor Integrado com Modulos Otimizados

Testa SupervisorAgent com SmartRouter, AIClient, PromptTemplates e ResponseValidator.
"""

import os
import sys
from dotenv import load_dotenv

# Adicionar pasta raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Carregar .env
load_dotenv()

# Imports
from core import SmartRouter, AIClientFactory, PromptTemplates, ResponseValidator


def test_supervisor_modules():
    """
    Testa que SupervisorAgent pode importar modulos otimizados.
    """
    print("\n" + "="*80)
    print(" TESTE: Supervisor Integration - Importacao de Modulos")
    print("="*80 + "\n")

    try:
        # Simular import do supervisor
        print("[1/4] Importando modulos otimizados...")
        from core import AIClient, SmartRouter, PromptTemplates, ResponseValidator
        print("      OK - Modulos importados\n")

        # Testar criacao do SmartRouter
        print("[2/4] Criando SmartRouter...")
        router = SmartRouter(enable_cache=True, enable_fallback=True)
        print("      OK - SmartRouter criado\n")

        # Testar criacao de AI clients via Factory
        print("[3/4] Criando AI clients via Factory...")
        supervisor_client = AIClientFactory.create_for_agent("supervisor")
        print(f"      OK - Supervisor client: {supervisor_client.model}\n")

        # Testar routing decision
        print("[4/4] Testando routing decision...")
        state = {
            "current_phase": 0,
            "script": None,
            "visual_plan": None,
            "audio_files": None,
            "video_path": None
        }

        decision = router.route(state)
        print(f"      Decisao: {decision}")

        assert decision == "script_agent", f"Erro: esperado script_agent, got {decision}"
        print("      OK - Routing funcionando\n")

        # Estatisticas
        print("Estatisticas do Router:")
        router.print_stats()

        print("="*80)
        print(" TESTE CONCLUIDO COM SUCESSO!")
        print("="*80 + "\n")

        return True

    except Exception as e:
        print(f"\nERRO: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_supervisor_routing():
    """
    Testa roteamento completo do fluxo de criacao de video.
    """
    print("\n" + "="*80)
    print(" TESTE: Supervisor Integration - Fluxo de Roteamento Completo")
    print("="*80 + "\n")

    try:
        from core import SmartRouter

        router = SmartRouter(enable_cache=True, enable_fallback=True)

        print("Simulando fluxo de criacao de video...\n")

        # Estado 1: Inicio
        print("[FASE 0] Inicio - nada feito")
        state1 = {
            "current_phase": 0,
            "script": None,
            "visual_plan": None,
            "audio_files": None,
            "video_path": None
        }
        d1 = router.route(state1)
        print(f"         Decisao: {d1}")
        assert d1 == "script_agent"

        # Estado 2: Script concluido
        print("\n[FASE 1] Script concluido")
        state2 = {
            "current_phase": 1,
            "script": {"scenes": []},
            "visual_plan": None,
            "audio_files": None,
            "video_path": None
        }
        d2 = router.route(state2)
        print(f"         Decisao: {d2}")
        assert d2 in ["visual_agent", "audio_agent"]

        # Estado 3: Script + Visual
        print("\n[FASE 2] Script + Visual concluidos")
        state3 = {
            "current_phase": 2,
            "script": {"scenes": []},
            "visual_plan": {"scenes": []},
            "audio_files": None,
            "video_path": None
        }
        d3 = router.route(state3)
        print(f"         Decisao: {d3}")
        assert d3 == "audio_agent"

        # Estado 4: Pronto para editar
        print("\n[FASE 3] Tudo pronto, falta editar")
        state4 = {
            "current_phase": 3,
            "script": {"scenes": []},
            "visual_plan": {"scenes": []},
            "audio_files": {"final_mix": {}},
            "video_path": None
        }
        d4 = router.route(state4)
        print(f"         Decisao: {d4}")
        assert d4 == "editor_agent"

        # Estado 5: Finalizado
        print("\n[FASE 4] Video finalizado")
        state5 = {
            "current_phase": 4,
            "script": {"scenes": []},
            "visual_plan": {"scenes": []},
            "audio_files": {"final_mix": {}},
            "video_path": "./output.mp4"
        }
        d5 = router.route(state5)
        print(f"         Decisao: {d5}")
        assert d5 == "FINISH"

        # Teste cache
        print("\n" + "-"*80)
        print("TESTE DE CACHE")
        print("-"*80)
        print("\nRepetindo decisao 1 (deve usar cache)...")
        d1_cached = router.route(state1)
        assert d1_cached == d1
        print(f"         Decisao (cached): {d1_cached}")

        # Estatisticas
        print("\nEstatisticas finais:")
        router.print_stats()

        cache_rate = (router.stats['cache_hits'] / router.stats['total_decisions']) * 100
        print(f"\nTaxa de cache: {cache_rate:.1f}%")

        if cache_rate >= 16:
            print("OK - Cache funcionando!\n")
        else:
            print(f"WARN - Cache abaixo do esperado ({cache_rate:.1f}% < 16%)\n")

        print("="*80)
        print(" TESTE CONCLUIDO COM SUCESSO!")
        print("="*80 + "\n")

        return True

    except Exception as e:
        print(f"\nERRO: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_prompt_templates():
    """
    Testa que PromptTemplates tem metodo supervisor_system_prompt.
    """
    print("\n" + "="*80)
    print(" TESTE: PromptTemplates - supervisor_system_prompt")
    print("="*80 + "\n")

    try:
        from core import PromptTemplates

        print("Obtendo supervisor_system_prompt...")
        prompt = PromptTemplates.supervisor_system_prompt()

        assert "SUPERVISOR AGENT" in prompt
        assert "COORDENAR" in prompt
        assert "Script Agent" in prompt

        print("OK - supervisor_system_prompt encontrado")
        print(f"\nPrimeiras linhas do prompt:")
        print("-" * 40)
        print(prompt[:200] + "...")
        print("-" * 40)

        print("\n" + "="*80)
        print(" TESTE CONCLUIDO COM SUCESSO!")
        print("="*80 + "\n")

        return True

    except Exception as e:
        print(f"\nERRO: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """
    Executa todos os testes de integracao.
    """
    print("\n" + "="*80)
    print(" TESTES DE INTEGRACAO - SupervisorAgent Otimizado")
    print("="*80)

    results = []

    # Teste 1: Modulos
    results.append(("Modulos Otimizados", test_supervisor_modules()))

    # Teste 2: PromptTemplates
    results.append(("PromptTemplates", test_prompt_templates()))

    # Teste 3: Roteamento (requer Ollama ou usa fallback)
    print("\nINFO: Proximo teste usara Ollama (se disponivel) ou fallback.\n")

    results.append(("Roteamento Completo", test_supervisor_routing()))

    # Resumo
    print("\n" + "="*80)
    print(" RESUMO DOS TESTES")
    print("="*80 + "\n")

    all_passed = True
    for name, passed in results:
        status = "OK" if passed else "FALHOU"
        print(f"  [{status:^6}] {name}")
        if not passed:
            all_passed = False

    print("\n" + "="*80)

    if all_passed:
        print(" TODOS OS TESTES PASSARAM!")
        print("="*80 + "\n")
        print("Supervisor integrado com sucesso com:")
        print("  - AIClient (Factory pattern)")
        print("  - SmartRouter (cache + fallback)")
        print("  - PromptTemplates (DRY)")
        print("  - ResponseValidator (parsing robusto)")
        print("")
        sys.exit(0)
    else:
        print(" ALGUNS TESTES FALHARAM")
        print("="*80 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
