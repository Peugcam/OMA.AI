"""
Teste do OptimizedSupervisor

Teste end-to-end do sistema de roteamento otimizado,
demonstrando uso do SmartRouter e módulos auxiliares.
"""

import os
import sys
from dotenv import load_dotenv

# Adicionar pasta raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Carregar .env
load_dotenv()

from core import SmartRouter, AIClientFactory, PromptTemplates, ResponseValidator


def test_smart_router():
    """
    Testa SmartRouter com fluxo completo de criação de vídeo.
    """
    print("\n" + "="*80)
    print(" 🧪 TESTE: SmartRouter - Fluxo Completo de Criação de Vídeo")
    print("="*80 + "\n")

    # Criar router
    router = SmartRouter(enable_cache=True, enable_fallback=True)

    # Simular fluxo completo
    print("📝 Simulando criação de vídeo...\n")

    # Estado 1: Início
    print("▶️  FASE 0: Início (nada feito)")
    state1 = {
        "task_id": "video_test_001",
        "current_phase": 0,
        "script": None,
        "visual_plan": None,
        "audio_files": None,
        "video_path": None
    }
    decision1 = router.route(state1)
    print(f"   Decisão: {decision1}\n")
    assert decision1 == "script_agent", f"❌ Erro: esperado 'script_agent', recebeu '{decision1}'"

    # Estado 2: Script concluído
    print("▶️  FASE 1: Script concluído")
    state2 = {
        "task_id": "video_test_001",
        "current_phase": 1,
        "script": {
            "script_id": "script_001",
            "scenes": [
                {"scene_number": 1, "duration": 5},
                {"scene_number": 2, "duration": 5}
            ]
        },
        "visual_plan": None,
        "audio_files": None,
        "video_path": None
    }
    decision2 = router.route(state2)
    print(f"   Decisão: {decision2}\n")
    assert decision2 in ["visual_agent", "audio_agent"], f"❌ Erro: decisão inesperada '{decision2}'"

    # Estado 3: Script + Visual concluídos
    print("▶️  FASE 2A: Script + Visual concluídos")
    state3 = {
        "task_id": "video_test_001",
        "current_phase": 2,
        "script": state2["script"],
        "visual_plan": {
            "visual_plan_id": "visual_001",
            "scenes": [{"scene_number": 1}, {"scene_number": 2}]
        },
        "audio_files": None,
        "video_path": None
    }
    decision3 = router.route(state3)
    print(f"   Decisão: {decision3}\n")
    assert decision3 == "audio_agent", f"❌ Erro: esperado 'audio_agent', recebeu '{decision3}'"

    # Estado 4: Script + Visual + Audio concluídos
    print("▶️  FASE 2B: Script + Visual + Audio concluídos")
    state4 = {
        "task_id": "video_test_001",
        "current_phase": 3,
        "script": state2["script"],
        "visual_plan": state3["visual_plan"],
        "audio_files": {
            "audio_production_id": "audio_001",
            "final_mix": {"file_path": "./cache/final_audio.mp3"}
        },
        "video_path": None
    }
    decision4 = router.route(state4)
    print(f"   Decisão: {decision4}\n")
    assert decision4 == "editor_agent", f"❌ Erro: esperado 'editor_agent', recebeu '{decision4}'"

    # Estado 5: Tudo concluído
    print("▶️  FASE 3: Vídeo finalizado")
    state5 = {
        "task_id": "video_test_001",
        "current_phase": 4,
        "script": state2["script"],
        "visual_plan": state3["visual_plan"],
        "audio_files": state4["audio_files"],
        "video_path": "./outputs/OMA_Video_20251118_test.mp4"
    }
    decision5 = router.route(state5)
    print(f"   Decisão: {decision5}\n")
    assert decision5 == "FINISH", f"❌ Erro: esperado 'FINISH', recebeu '{decision5}'"

    # Teste de cache: repetir decisão 1
    print("\n" + "-"*80)
    print(" 🎯 TESTE DE CACHE: Repetir primeira decisão")
    print("-"*80 + "\n")

    decision1_cached = router.route(state1)
    print(f"   Decisão (cached): {decision1_cached}")
    assert decision1_cached == decision1, "❌ Cache retornou decisão diferente!"

    # Estatísticas
    router.print_stats()

    # Validações finais
    cache_rate = (router.stats['cache_hits'] / router.stats['total_decisions']) * 100

    print("\n✅ RESULTADOS:")
    print(f"   • Total de decisões: {router.stats['total_decisions']}")
    print(f"   • Taxa de cache: {cache_rate:.1f}%")
    print(f"   • Tempo médio: {router.stats['total_time_ms'] / router.stats['total_decisions']:.0f}ms")

    if cache_rate >= 16:  # 1 hit de 6 decisões = ~16%
        print(f"   ✅ Cache funcionando corretamente!")
    else:
        print(f"   ⚠️  Cache abaixo do esperado ({cache_rate:.1f}% < 16%)")

    print("\n" + "="*80)
    print(" ✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("="*80 + "\n")


def test_ai_client_factory():
    """
    Testa criação de clientes através do Factory.
    """
    print("\n" + "="*80)
    print(" 🧪 TESTE: AIClientFactory - Criação de Clientes do .env")
    print("="*80 + "\n")

    try:
        # Tentar criar cliente do Supervisor
        print("▶️  Criando cliente Supervisor...")
        supervisor_client = AIClientFactory.create_for_agent("supervisor")
        print(f"   ✅ Supervisor: {supervisor_client.model} ({supervisor_client.provider})\n")

        # Criar todos os clientes
        print("▶️  Criando todos os clientes...")
        clients = AIClientFactory.create_all_agents()

        for agent, client in clients.items():
            local_cloud = "LOCAL" if client.use_local else "CLOUD"
            print(f"   ✅ {agent:10s}: {client.model:40s} [{local_cloud}]")

        print("\n" + "="*80)
        print(" ✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        print("\nVerifique se:")
        print("  1. O arquivo .env existe")
        print("  2. As variáveis *_MODEL estão configuradas")
        print("  3. Ollama está rodando (se usar modelos locais)")
        print("")
        raise


def test_prompt_templates():
    """
    Testa geração de prompts.
    """
    print("\n" + "="*80)
    print(" 🧪 TESTE: PromptTemplates - Geração de Prompts")
    print("="*80 + "\n")

    # Teste 1: Routing prompt
    print("▶️  Teste 1: Routing Decision")
    print("-" * 40)

    state = {
        "current_phase": 1,
        "script": {"scenes": []},
        "visual_plan": None,
        "audio_files": None,
        "video_path": None
    }

    prompt = PromptTemplates.routing_decision(state)
    print(prompt)
    print()

    assert "Fase: 1" in prompt
    assert "Script: ✓" in prompt
    assert "Visual: ✗" in prompt
    print("✅ Prompt routing OK\n")

    # Teste 2: Script generation
    print("▶️  Teste 2: Script Generation")
    print("-" * 40)

    prompt = PromptTemplates.script_generation(
        description="Propaganda cafeteria moderna",
        target_audience="Millennials",
        duration=30,
        style="Clean",
        cta="Visite nossa loja"
    )

    print(prompt[:200] + "...\n")

    assert "30 segundos" in prompt
    assert "Millennials" in prompt
    print("✅ Prompt script OK\n")

    print("="*80)
    print(" ✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("="*80 + "\n")


def test_response_validator():
    """
    Testa validadores de resposta.
    """
    print("\n" + "="*80)
    print(" 🧪 TESTE: ResponseValidator - Parsing e Validação")
    print("="*80 + "\n")

    # Teste 1: Parse JSON
    print("▶️  Teste 1: Parse JSON")
    print("-" * 40)

    valid_json = '{"name": "teste", "value": 123}'
    result = ResponseValidator.parse_json(valid_json)
    assert result == {"name": "teste", "value": 123}
    print(f"✅ JSON válido parseado: {result}\n")

    # Teste 2: Extrair JSON de texto
    print("▶️  Teste 2: Extrair JSON de texto misto")
    print("-" * 40)

    mixed = 'Aqui está: {"status": "ok"} fim'
    result = ResponseValidator.extract_first_json(mixed)
    assert result == {"status": "ok"}
    print(f"✅ JSON extraído: {result}\n")

    # Teste 3: Validar agente
    print("▶️  Teste 3: Validar nome de agente")
    print("-" * 40)

    assert ResponseValidator.validate_agent_name("script_agent") == True
    assert ResponseValidator.validate_agent_name("invalid") == False
    print("✅ Validação de agentes OK\n")

    # Teste 4: Limpar nome
    print("▶️  Teste 4: Limpar nome de agente")
    print("-" * 40)

    clean = ResponseValidator.clean_agent_name("  visual_agent\\n")
    assert clean == "visual_agent"
    print(f"✅ Nome limpo: '{clean}'\n")

    print("="*80)
    print(" ✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("="*80 + "\n")


def main():
    """
    Executa todos os testes.
    """
    print("\n" + "="*80)
    print(" TESTE COMPLETO - OptimizedSupervisor & Core Modules")
    print("="*80)

    try:
        # Teste 1: ResponseValidator (não precisa de Ollama)
        test_response_validator()

        # Teste 2: PromptTemplates (não precisa de Ollama)
        test_prompt_templates()

        # Teste 3: AIClientFactory (precisa de .env configurado)
        test_ai_client_factory()

        # Teste 4: SmartRouter (precisa de Ollama rodando)
        print("\n⚠️  ATENÇÃO: Próximo teste requer Ollama rodando!")
        print("   Se Ollama não estiver rodando, o teste usará fallback.\n")

        input("   Pressione ENTER para continuar...")

        test_smart_router()

        # Resumo final
        print("\n" + "="*80)
        print(" TODOS OS TESTES PASSARAM COM SUCESSO!")
        print("="*80 + "\n")

        print("RESUMO:")
        print("   OK - ResponseValidator")
        print("   OK - PromptTemplates")
        print("   OK - AIClientFactory")
        print("   OK - SmartRouter")
        print("")
        print("Sistema otimizado pronto para uso!")
        print("")

    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ ERRO: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
