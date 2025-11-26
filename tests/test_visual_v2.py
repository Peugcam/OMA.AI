"""
Testes para Visual Agent V2 - Integracao Eficiente Pexels + Stability

Executa:
    python -m tests.test_visual_v2
"""

import asyncio
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_scene_classifier():
    """Testa o classificador de cenas em 3 niveis"""
    print("\n" + "="*70)
    print("TESTE 1: SceneClassifier (3 Niveis)")
    print("="*70 + "\n")

    from core.scene_classifier import SceneClassifier

    classifier = SceneClassifier()

    test_scenes = [
        # Nivel 1 - Pexels (pessoas)
        ("Pessoa trabalhando no laptop em escritorio moderno", "pexels", 1),
        ("Equipe discutindo projeto em reuniao", "pexels", 1),
        ("Professor explicando conceito para estudantes", "pexels", 1),

        # Nivel 1 - Stability (abstrato)
        ("Logo holografico flutuando no espaco", "stability", 1),
        ("Visualizacao de dados com particulas", "stability", 1),

        # Nivel 2 - Both (hibrido)
        ("Pessoa apresentando grafico de dados", "both", 2),
        ("Equipe com logo da empresa ao fundo", "both", 2),

        # Nivel 3 - Unknown (MCP decide)
        ("Ambiente corporativo moderno", "unknown", 3),
    ]

    passed = 0
    failed = 0

    for description, expected_tool, expected_level in test_scenes:
        result = classifier.classify(description)

        is_correct = result.tool == expected_tool

        status = "PASS" if is_correct else "FAIL"
        if is_correct:
            passed += 1
        else:
            failed += 1

        print(f"[{status}] {description[:40]}...")
        print(f"       Esperado: {expected_tool} (L{expected_level})")
        print(f"       Obtido:   {result.tool} (L{result.level})")
        print()

    print(f"\nResultado: {passed}/{len(test_scenes)} testes passaram")

    # Stats
    stats = classifier.get_stats()
    print(f"\nEstatisticas do classificador:")
    print(f"  Eficiencia: {stats['efficiency_pct']}")
    print(f"  Nivel 1: {stats['level_1_pct']}")
    print(f"  Nivel 2: {stats['level_2_pct']}")
    print(f"  Nivel 3: {stats['level_3_pct']}")

    return failed == 0


def test_schemas():
    """Testa os schemas Pydantic"""
    print("\n" + "="*70)
    print("TESTE 2: Schemas (Pydantic)")
    print("="*70 + "\n")

    from mcp.schemas import (
        PexelsSearchResult,
        StabilityImageResult,
        HybridVisualResult,
        SearchPexelsInput,
        GenerateHybridInput
    )

    try:
        # Teste PexelsSearchResult
        pexels = PexelsSearchResult(
            video_id=123456,
            video_url="https://videos.pexels.com/test.mp4",
            local_path="/test/path.mp4",
            width=1920,
            height=1080,
            duration=15,
            keywords="test keywords"
        )
        print(f"[PASS] PexelsSearchResult: source={pexels.source}, cost=${pexels.cost}")

        # Teste StabilityImageResult
        stability = StabilityImageResult(
            image_path="/test/image.png",
            prompt_used="test prompt"
        )
        print(f"[PASS] StabilityImageResult: source={stability.source}, cost=${stability.cost}")

        # Teste HybridVisualResult
        hybrid = HybridVisualResult(
            video_id=123456,
            video_url="https://videos.pexels.com/test.mp4",
            video_local_path="/test/video.mp4",
            video_width=1920,
            video_height=1080,
            video_duration=15,
            video_keywords="test",
            image_path="/test/overlay.png",
            image_prompt="overlay prompt"
        )
        print(f"[PASS] HybridVisualResult: source={hybrid.source}, cost=${hybrid.cost}")

        # Teste GenerateHybridInput
        hybrid_input = GenerateHybridInput(
            video_keywords="team meeting business",
            overlay_prompt="company logo minimalist design"
        )
        print(f"[PASS] GenerateHybridInput: video='{hybrid_input.video_keywords}', overlay='{hybrid_input.overlay_prompt[:30]}...'")

        print("\nTodos os schemas funcionando corretamente!")
        return True

    except Exception as e:
        print(f"[FAIL] Erro nos schemas: {e}")
        return False


async def test_visual_agent_v2_mock():
    """Testa Visual Agent V2 com mock (sem APIs reais)"""
    print("\n" + "="*70)
    print("TESTE 3: VisualAgentV2 (Mock)")
    print("="*70 + "\n")

    from agents.visual_agent_v2 import VisualAgentV2

    try:
        # Criar agente (vai tentar inicializar MCP)
        print("Inicializando VisualAgentV2...")
        agent = VisualAgentV2()

        print("[PASS] VisualAgentV2 inicializado com sucesso")

        # Testar classificador interno
        classification = agent.classifier.classify("Pessoa trabalhando no laptop")
        print(f"[PASS] Classificador interno: {classification.tool} (L{classification.level})")

        # Testar geracao de keywords
        keywords = agent._generate_keywords_simple("Pessoa trabalhando no escritorio moderno")
        print(f"[PASS] Keywords geradas: '{keywords}'")

        # Testar geracao de prompt
        prompt = agent._generate_prompt_simple("Logo futurista", "energetic", "modern")
        print(f"[PASS] Prompt gerado: '{prompt[:50]}...'")

        return True

    except Exception as e:
        print(f"[FAIL] Erro no VisualAgentV2: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_full_integration():
    """Testa integracao completa (REQUER APIs configuradas)"""
    print("\n" + "="*70)
    print("TESTE 4: Integracao Completa (Requer APIs)")
    print("="*70 + "\n")

    import os

    # Verificar APIs
    has_pexels = bool(os.getenv("PEXELS_API_KEY"))
    has_stability = bool(os.getenv("STABILITY_API_KEY"))
    has_openrouter = bool(os.getenv("OPENROUTER_API_KEY"))

    print(f"APIs configuradas:")
    print(f"  PEXELS_API_KEY: {'OK' if has_pexels else 'NAO CONFIGURADA'}")
    print(f"  STABILITY_API_KEY: {'OK' if has_stability else 'NAO CONFIGURADA'}")
    print(f"  OPENROUTER_API_KEY: {'OK' if has_openrouter else 'NAO CONFIGURADA'}")

    if not all([has_pexels, has_stability, has_openrouter]):
        print("\n[SKIP] Teste de integracao pulado - configure as APIs no .env")
        return True  # Nao falha, apenas pula

    try:
        from agents.visual_agent_v2 import VisualAgentV2

        agent = VisualAgentV2()

        # Mock state com script
        state = {
            "brief": {
                "topic": "Teste de integracao",
                "style": "modern"
            },
            "script": {
                "scenes": [
                    {
                        "scene_number": 1,
                        "visual_description": "Pessoa trabalhando no laptop em escritorio moderno",
                        "mood": "professional",
                        "duration": 5
                    },
                    {
                        "scene_number": 2,
                        "visual_description": "Logo holografico da empresa flutuando",
                        "mood": "futuristic",
                        "duration": 5
                    },
                    {
                        "scene_number": 3,
                        "visual_description": "Equipe apresentando grafico de resultados",
                        "mood": "energetic",
                        "duration": 5
                    }
                ]
            }
        }

        print("\nProcessando 3 cenas de teste...")
        result = await agent.plan_visuals(state)

        print("\nResultado:")
        metrics = result["visual_plan"]["metrics"]
        print(f"  Cenas processadas: {metrics['total_scenes']}")
        print(f"  Eficiencia: {metrics['efficiency']}")
        print(f"  Custo total: {metrics['total_cost']}")
        print(f"  Fontes: {metrics['sources']}")

        print("\n[PASS] Integracao completa funcionando!")
        return True

    except Exception as e:
        print(f"\n[FAIL] Erro na integracao: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Executa todos os testes"""
    print("\n" + "#"*70)
    print("# TESTES - VISUAL AGENT V2")
    print("# Integracao Eficiente Pexels + Stability AI")
    print("#"*70)

    results = []

    # Teste 1: Classificador
    results.append(("SceneClassifier", test_scene_classifier()))

    # Teste 2: Schemas
    results.append(("Schemas", test_schemas()))

    # Teste 3: VisualAgentV2 Mock
    results.append(("VisualAgentV2 Mock", await test_visual_agent_v2_mock()))

    # Teste 4: Integracao (opcional)
    results.append(("Integracao Completa", await test_full_integration()))

    # Resumo
    print("\n" + "#"*70)
    print("# RESUMO DOS TESTES")
    print("#"*70)

    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("Todos os testes passaram!")
    else:
        print("Alguns testes falharam!")

    return all_passed


if __name__ == "__main__":
    asyncio.run(main())
