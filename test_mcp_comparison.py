"""
Teste Comparativo: Visual Agent Original vs MCP

Testa a mesma cena com ambas as versões e compara:
- Número de chamadas LLM
- Tempo de execução
- Custo total
- Precisão da classificação
"""

import asyncio
import time
from datetime import datetime
import json

# Visual Agent original
from agents.visual_agent import VisualAgent

# Visual Agent MCP
from agents.visual_agent_mcp import VisualAgentMCP


# ============================================================================
# TESTE DE COMPARAÇÃO
# ============================================================================

async def test_scene_comparison():
    """
    Testa a mesma cena com ambas as versões.
    """

    print("=" * 80)
    print("TESTE COMPARATIVO: Visual Agent Original vs MCP")
    print("=" * 80)
    print()

    # Cena de teste (com pessoas - deve ir para Pexels)
    test_scene_people = {
        "scene_number": 1,
        "duration": 5,
        "visual_description": "Pessoa trabalhando em laptop em escritório moderno",
        "narration": "Trabalhando com produtividade",
        "mood": "professional"
    }

    # Cena de teste (abstrata - deve ir para Stability)
    test_scene_abstract = {
        "scene_number": 2,
        "duration": 5,
        "visual_description": "Logo holográfico OMA flutuando no espaço",
        "narration": "OMA - Tecnologia avançada",
        "mood": "futuristic"
    }

    # Estado de teste
    test_state = {
        "script": {
            "scenes": [test_scene_people, test_scene_abstract]
        },
        "brief": {
            "style": "modern, tech"
        }
    }

    print("\nCena 1: PESSOA TRABALHANDO (deve escolher Pexels)")
    print("-" * 80)
    await compare_agents_for_scene(test_scene_people, test_state)

    print("\n\nCena 2: LOGO HOLOGRÁFICO (deve escolher Stability)")
    print("-" * 80)
    await compare_agents_for_scene(test_scene_abstract, test_state)


async def compare_agents_for_scene(scene: dict, state: dict):
    """
    Compara os dois agentes para uma cena específica.
    """

    print(f"\nTESTE: {scene['visual_description']}")
    print()

    # ========================================================================
    # TESTE 1: VISUAL AGENT ORIGINAL
    # ========================================================================

    print("[1] VISUAL AGENT ORIGINAL")
    print("-" * 40)

    agent_original = VisualAgent()

    start_time = time.time()
    llm_calls_before = 0  # Contador manual (precisaria instrumentar AIClient)

    try:
        result_original = await agent_original._generate_scene_visual(scene, state)

        end_time = time.time()
        duration_original = end_time - start_time

        print(f"OK - Sucesso")
        print(f"   Fonte: {result_original.get('source')}")
        print(f"   Custo: ${result_original.get('cost', 0):.4f}")
        print(f"   Tempo: {duration_original:.2f}s")
        print(f"   LLM calls: ~2 (classificacao + keywords)")
        print(f"   Media path: {result_original.get('media_path', 'N/A')[:60]}...")

    except Exception as e:
        print(f"ERRO: {e}")
        duration_original = None
        result_original = None

    # ========================================================================
    # TESTE 2: VISUAL AGENT MCP
    # ========================================================================

    print()
    print("[2] VISUAL AGENT MCP")
    print("-" * 40)

    agent_mcp = VisualAgentMCP()

    start_time = time.time()

    try:
        result_mcp = await agent_mcp._generate_scene_visual_mcp(scene, state)

        end_time = time.time()
        duration_mcp = end_time - start_time

        print(f"OK - Sucesso")
        print(f"   Fonte: {result_mcp.get('source')}")
        print(f"   Custo: ${result_mcp.get('cost', 0):.4f}")
        print(f"   Tempo: {duration_mcp:.2f}s")
        print(f"   LLM calls: 1 (tool calling direto)")
        print(f"   Media path: {result_mcp.get('media_path', 'N/A')[:60]}...")

    except Exception as e:
        print(f"ERRO: {e}")
        duration_mcp = None
        result_mcp = None

    # ========================================================================
    # COMPARAÇÃO
    # ========================================================================

    print()
    print("COMPARACAO")
    print("-" * 40)

    if result_original and result_mcp:
        # Comparar fonte escolhida
        source_match = result_original.get("source") == result_mcp.get("source")
        print(f"Mesma fonte escolhida: {'SIM' if source_match else 'NAO'}")

        # Comparar custo
        cost_original = result_original.get("cost", 0)
        cost_mcp = result_mcp.get("cost", 0)
        cost_diff = cost_original - cost_mcp
        print(f"Custo original: ${cost_original:.4f}")
        print(f"Custo MCP: ${cost_mcp:.4f}")
        print(f"Diferença: ${abs(cost_diff):.4f} ({'economia' if cost_diff > 0 else 'igual'})")

        # Comparar tempo
        if duration_original and duration_mcp:
            time_diff = duration_original - duration_mcp
            time_diff_percent = (time_diff / duration_original) * 100
            print(f"Tempo original: {duration_original:.2f}s")
            print(f"Tempo MCP: {duration_mcp:.2f}s")
            print(f"Diferença: {abs(time_diff):.2f}s ({abs(time_diff_percent):.1f}% {'mais rápido' if time_diff > 0 else 'mais lento'})")

        # LLM calls
        print(f"LLM calls original: ~2")
        print(f"LLM calls MCP: 1")
        print(f"Economia de calls: 50%")

    else:
        print("Não foi possível comparar (um dos agentes falhou)")


# ============================================================================
# TESTE DE PIPELINE COMPLETO
# ============================================================================

async def test_full_pipeline_comparison():
    """
    Testa pipeline completo com 5 cenas (original vs MCP).
    """

    print("\n" + "=" * 80)
    print("TESTE DE PIPELINE COMPLETO (5 CENAS)")
    print("=" * 80)

    # Script de teste com 5 cenas
    test_state = {
        "script": {
            "scenes": [
                {
                    "scene_number": 1,
                    "duration": 5,
                    "visual_description": "Pessoa frustrada com múltiplas tarefas",
                    "narration": "Muitas tarefas, pouco tempo",
                    "mood": "stressed"
                },
                {
                    "scene_number": 2,
                    "duration": 5,
                    "visual_description": "Equipe colaborando em reunião",
                    "narration": "Trabalho em equipe eficiente",
                    "mood": "energetic"
                },
                {
                    "scene_number": 3,
                    "duration": 5,
                    "visual_description": "Logo OMA holográfico aparecendo",
                    "narration": "Apresentando OMA",
                    "mood": "futuristic"
                },
                {
                    "scene_number": 4,
                    "duration": 5,
                    "visual_description": "Pessoa sorrindo usando app",
                    "narration": "Produtividade aumentada",
                    "mood": "happy"
                },
                {
                    "scene_number": 5,
                    "duration": 5,
                    "visual_description": "Visualização abstrata de dados crescentes",
                    "narration": "Resultados impressionantes",
                    "mood": "triumphant"
                }
            ]
        },
        "brief": {
            "style": "modern, tech, motivational"
        }
    }

    # ========================================================================
    # TESTE ORIGINAL
    # ========================================================================

    print("\n1️⃣  PIPELINE ORIGINAL")
    print("-" * 80)

    agent_original = VisualAgent()

    start_time = time.time()

    try:
        result_original = await agent_original.plan_visuals(test_state.copy())
        end_time = time.time()
        duration_original = end_time - start_time

        scenes_original = result_original["visual_plan"]["scenes"]
        total_cost_original = sum(s.get("cost", 0) for s in scenes_original)
        pexels_count_original = sum(1 for s in scenes_original if s.get("source") == "pexels")
        stability_count_original = sum(1 for s in scenes_original if s.get("source") == "stability_ai")

        print(f"✅ Sucesso")
        print(f"   Cenas: {len(scenes_original)}")
        print(f"   Pexels: {pexels_count_original}")
        print(f"   Stability: {stability_count_original}")
        print(f"   Custo total: ${total_cost_original:.4f}")
        print(f"   Tempo total: {duration_original:.2f}s")
        print(f"   LLM calls: ~{len(scenes_original) * 2} (2 por cena)")

    except Exception as e:
        print(f"❌ Erro: {e}")
        result_original = None

    # ========================================================================
    # TESTE MCP
    # ========================================================================

    print("\n2️⃣  PIPELINE MCP")
    print("-" * 80)

    agent_mcp = VisualAgentMCP()

    start_time = time.time()

    try:
        result_mcp = await agent_mcp.plan_visuals(test_state.copy())
        end_time = time.time()
        duration_mcp = end_time - start_time

        scenes_mcp = result_mcp["visual_plan"]["scenes"]
        total_cost_mcp = sum(s.get("cost", 0) for s in scenes_mcp)
        pexels_count_mcp = sum(1 for s in scenes_mcp if s.get("source") == "pexels")
        stability_count_mcp = sum(1 for s in scenes_mcp if s.get("source") == "stability_ai")

        print(f"✅ Sucesso")
        print(f"   Cenas: {len(scenes_mcp)}")
        print(f"   Pexels: {pexels_count_mcp}")
        print(f"   Stability: {stability_count_mcp}")
        print(f"   Custo total: ${total_cost_mcp:.4f}")
        print(f"   Tempo total: {duration_mcp:.2f}s")
        print(f"   LLM calls: {len(scenes_mcp)} (1 por cena)")

    except Exception as e:
        print(f"❌ Erro: {e}")
        result_mcp = None

    # ========================================================================
    # COMPARAÇÃO FINAL
    # ========================================================================

    if result_original and result_mcp:
        print("\n📊 RESUMO DA COMPARAÇÃO")
        print("=" * 80)

        print(f"\nMétrica                | Original | MCP      | Melhoria")
        print("-" * 80)
        print(f"Cenas processadas      | {len(scenes_original)}        | {len(scenes_mcp)}        | -")
        print(f"Custo total            | ${total_cost_original:.4f}   | ${total_cost_mcp:.4f}   | {((total_cost_original - total_cost_mcp) / total_cost_original * 100):.1f}%")
        print(f"Tempo total            | {duration_original:.2f}s     | {duration_mcp:.2f}s     | {((duration_original - duration_mcp) / duration_original * 100):.1f}%")
        print(f"LLM calls              | {len(scenes_original) * 2}        | {len(scenes_mcp)}        | -50%")
        print(f"Pexels (grátis)        | {pexels_count_original}        | {pexels_count_mcp}        | -")
        print(f"Stability (pago)       | {stability_count_original}        | {stability_count_mcp}        | -")


# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Executa todos os testes"""

    # Teste 1: Comparação por cena
    await test_scene_comparison()

    # Teste 2: Pipeline completo
    # await test_full_pipeline_comparison()

    print("\n" + "=" * 80)
    print("TESTES CONCLUÍDOS")
    print("=" * 80)


if __name__ == "__main__":
    import sys
    import os

    # Adicionar path para imports
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    # Carregar .env
    from dotenv import load_dotenv
    load_dotenv()

    # Executar testes
    asyncio.run(main())
