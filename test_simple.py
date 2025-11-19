"""
Teste Simplificado - Módulos Otimizados (sem emojis para Windows)
"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from core import SmartRouter, AIClientFactory, PromptTemplates, ResponseValidator


def test_validators():
    """Teste ResponseValidator"""
    print("\n" + "="*80)
    print("TESTE 1: ResponseValidator")
    print("="*80)

    # Parse JSON
    result = ResponseValidator.parse_json('{"a": 1}')
    assert result == {"a": 1}, "Parse JSON falhou"
    print("[OK] Parse JSON")

    # Extrair JSON
    result = ResponseValidator.extract_first_json('Resultado: {"b": 2}')
    assert result == {"b": 2}, "Extração JSON falhou"
    print("[OK] Extração JSON")

    # Validar agente
    assert ResponseValidator.validate_agent_name("script_agent") == True
    assert ResponseValidator.validate_agent_name("invalid") == False
    print("[OK] Validação agente")

    print("="*80)
    print("TESTE 1 CONCLUIDO COM SUCESSO!\n")


def test_prompts():
    """Teste PromptTemplates"""
    print("="*80)
    print("TESTE 2: PromptTemplates")
    print("="*80)

    state = {
        "current_phase": 1,
        "script": {"scenes": []},
        "visual_plan": None,
        "audio_files": None,
        "video_path": None
    }

    prompt = PromptTemplates.routing_decision(state)
    assert "Fase: 1" in prompt, "Routing prompt inválido"
    assert "Script:" in prompt, "Routing prompt sem Script"
    print("[OK] Routing prompt")

    prompt = PromptTemplates.script_generation(
        description="Test",
        target_audience="Test",
        duration=30,
        style="Test",
        cta="Test"
    )
    assert "30 segundos" in prompt or "30" in prompt, "Script prompt inválido"
    print("[OK] Script prompt")

    print("="*80)
    print("TESTE 2 CONCLUIDO COM SUCESSO!\n")


def test_factory():
    """Teste AIClientFactory"""
    print("="*80)
    print("TESTE 3: AIClientFactory")
    print("="*80)

    try:
        # Criar cliente supervisor
        supervisor = AIClientFactory.create_for_agent("supervisor")
        print(f"[OK] Supervisor criado: {supervisor.model}")

        # Criar todos
        clients = AIClientFactory.create_all_agents()
        print(f"[OK] Todos criados: {len(clients)} clientes")

        for agent, client in clients.items():
            local_cloud = "LOCAL" if client.use_local else "CLOUD"
            print(f"     {agent}: {local_cloud}")

        print("="*80)
        print("TESTE 3 CONCLUIDO COM SUCESSO!\n")

    except Exception as e:
        print(f"[ERRO] {e}")
        print("Verifique configuração do .env")
        raise


def test_router():
    """Teste SmartRouter"""
    print("="*80)
    print("TESTE 4: SmartRouter")
    print("="*80)
    print("[INFO] Este teste requer Ollama rodando")
    print("[INFO] Se Ollama não estiver disponível, usará fallback\n")

    router = SmartRouter(enable_cache=True, enable_fallback=True)

    # Estado 1: Início
    print("[1/5] Testando fase inicial...")
    state1 = {
        "current_phase": 0,
        "script": None,
        "visual_plan": None,
        "audio_files": None,
        "video_path": None
    }
    decision1 = router.route(state1)
    assert decision1 == "script_agent", f"Esperado script_agent, got {decision1}"
    print(f"      Decisão: {decision1} [OK]")

    # Estado 2: Script concluído
    print("[2/5] Testando com script concluído...")
    state2 = {
        "current_phase": 1,
        "script": {"scenes": []},
        "visual_plan": None,
        "audio_files": None,
        "video_path": None
    }
    decision2 = router.route(state2)
    assert decision2 in ["visual_agent", "audio_agent"]
    print(f"      Decisão: {decision2} [OK]")

    # Estado 3: Script + Visual
    print("[3/5] Testando com script + visual...")
    state3 = {
        "current_phase": 2,
        "script": {"scenes": []},
        "visual_plan": {"scenes": []},
        "audio_files": None,
        "video_path": None
    }
    decision3 = router.route(state3)
    assert decision3 == "audio_agent"
    print(f"      Decisão: {decision3} [OK]")

    # Estado 4: Pronto para editar
    print("[4/5] Testando pronto para editar...")
    state4 = {
        "current_phase": 3,
        "script": {"scenes": []},
        "visual_plan": {"scenes": []},
        "audio_files": {"final_mix": {}},
        "video_path": None
    }
    decision4 = router.route(state4)
    assert decision4 == "editor_agent"
    print(f"      Decisão: {decision4} [OK]")

    # Estado 5: Finalizado
    print("[5/5] Testando finalização...")
    state5 = {
        "current_phase": 4,
        "script": {"scenes": []},
        "visual_plan": {"scenes": []},
        "audio_files": {"final_mix": {}},
        "video_path": "./output.mp4"
    }
    decision5 = router.route(state5)
    assert decision5 == "FINISH"
    print(f"      Decisão: {decision5} [OK]")

    # Teste cache
    print("\nTestando cache...")
    decision1_cached = router.route(state1)
    assert decision1_cached == decision1
    print(f"      Cache funcionando [OK]")

    # Estatísticas
    print("\nEstatísticas do Router:")
    router.print_stats()

    cache_rate = (router.stats['cache_hits'] / router.stats['total_decisions']) * 100
    print(f"\nTaxa de cache: {cache_rate:.1f}%")

    print("="*80)
    print("TESTE 4 CONCLUIDO COM SUCESSO!\n")


def main():
    """Executa todos os testes"""
    print("\n" + "="*80)
    print(" TESTES - Módulos Otimizados OMA v3.0")
    print("="*80 + "\n")

    try:
        test_validators()
        test_prompts()
        test_factory()

        print("\n[INFO] Próximo teste requer Ollama rodando")
        print("[INFO] Pressione Ctrl+C para pular ou ENTER para continuar...")
        try:
            input()
        except KeyboardInterrupt:
            print("\n\nTeste do Router pulado.")
            print("\nPara rodar: D:\\OMA_Portable\\start_ollama.bat")
            print("Depois execute este teste novamente.\n")
            sys.exit(0)

        test_router()

        # Resumo
        print("\n" + "="*80)
        print(" TODOS OS TESTES PASSARAM!")
        print("="*80 + "\n")

        print("RESUMO:")
        print("  [OK] ResponseValidator")
        print("  [OK] PromptTemplates")
        print("  [OK] AIClientFactory")
        print("  [OK] SmartRouter")
        print("")
        print("Sistema otimizado pronto para uso!")
        print("")

    except AssertionError as e:
        print(f"\n[ERRO] Teste falhou: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERRO] {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
