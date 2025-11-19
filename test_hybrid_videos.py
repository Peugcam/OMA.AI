"""
Script de teste para validar fluxo híbrido Pexels + Stability AI

Cria 2 vídeos diferentes para testar:
1. Vídeo corporativo (mais Pexels - pessoas)
2. Vídeo tech/abstrato (mix balanceado)
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Import agents
try:
    from agents.supervisor_agent import SupervisorAgent
    from agents.script_agent import ScriptAgent
    from agents.visual_agent import VisualAgent
    logger.info("✅ Agents importados com sucesso")
except ImportError as e:
    logger.error(f"❌ Erro ao importar agents: {e}")
    logger.error("Execute: pip install -r requirements_openrouter.txt")
    exit(1)


# ============================================================================
# TESTE 1: Vídeo Corporativo (mais pessoas)
# ============================================================================

BRIEF_CORPORATIVO = {
    "title": "OMA.AI - Plataforma de Criação de Vídeos",
    "description": """
    Vídeo promocional mostrando a OMA.AI como solução para criação de vídeos com IA.

    Estrutura:
    - Abertura: Pessoa frustrada tentando criar vídeo manualmente
    - Problema: Custo alto de produção de vídeo
    - Solução: Logo OMA.AI aparecendo de forma impactante
    - Benefício: Equipe feliz usando a plataforma
    """,
    "duration": 30,
    "target_audience": "Empresas e criadores de conteúdo",
    "style": "profissional e moderno",
    "mood": "inspirador e tecnológico"
}


# ============================================================================
# TESTE 2: Vídeo Tech/Abstrato (mix balanceado)
# ============================================================================

BRIEF_TECH = {
    "title": "Futuro da IA - Inovação Tecnológica",
    "description": """
    Vídeo conceitual sobre avanços em inteligência artificial.

    Estrutura:
    - Abertura: Cientista de dados analisando código
    - Conceito: Cérebro digital com redes neurais holográficas
    - Equipe: Desenvolvedores colaborando em projeto
    - Fechamento: Visualização abstrata de algoritmos e dados
    """,
    "duration": 30,
    "target_audience": "Empresas tech e investidores",
    "style": "futurista e conceitual",
    "mood": "inovador e intelectual"
}


# ============================================================================
# Função de Teste
# ============================================================================

async def test_video(brief: dict, test_name: str):
    """
    Testa criação de vídeo com fluxo híbrido.

    Args:
        brief: Briefing do vídeo
        test_name: Nome do teste para logs
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"🎬 TESTE: {test_name}")
    logger.info(f"{'='*60}\n")

    try:
        # Estado inicial
        state = {
            "brief": brief,
            "request_id": f"test_{test_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "current_phase": 0
        }

        # PHASE 1: Supervisor analisa briefing
        logger.info("📋 PHASE 1: Supervisor analisando briefing...")
        supervisor = SupervisorAgent()
        state = await supervisor.analyze_request(state)
        logger.info(f"✅ Análise completa: {state.get('analysis', {}).get('complexity', 'unknown')}")

        # PHASE 2: Script Agent cria roteiro
        logger.info("\n📝 PHASE 2: Script Agent criando roteiro...")
        script_agent = ScriptAgent()
        state = await script_agent.generate_script(state)

        script = state.get("script", {})
        scenes = script.get("scenes", [])
        logger.info(f"✅ Roteiro criado: {len(scenes)} cenas")

        # Mostrar cenas
        for scene in scenes:
            logger.info(f"\n  Cena {scene['scene_number']}: {scene.get('visual_description', '')[:60]}...")
            logger.info(f"  Narração: {scene.get('narration', '')[:60]}...")

        # PHASE 3: Visual Agent - AQUI ESTÁ O TESTE HÍBRIDO!
        logger.info("\n🎨 PHASE 3: Visual Agent (FLUXO HÍBRIDO)...")
        logger.info("="*60)

        visual_agent = VisualAgent()
        state = await visual_agent.plan_visuals(state)

        visual_plan = state.get("visual_plan", {})
        visual_scenes = visual_plan.get("scenes", [])

        # Analisar resultados
        logger.info(f"\n✅ Plano visual criado: {len(visual_scenes)} cenas\n")

        pexels_count = 0
        stability_count = 0
        total_cost = 0.0

        logger.info("📊 BREAKDOWN POR CENA:")
        logger.info("="*60)

        for vscene in visual_scenes:
            scene_num = vscene.get("scene_number")
            source = vscene.get("source", "unknown")
            media_type = vscene.get("media_type", "unknown")
            cost = vscene.get("cost", 0.0)
            classification = vscene.get("classification", "N/A")

            total_cost += cost

            if source == "pexels":
                pexels_count += 1
                icon = "📹"
            elif source == "stability_ai":
                stability_count += 1
                icon = "🎨"
            else:
                icon = "⚠️"

            logger.info(f"\n{icon} Cena {scene_num}:")
            logger.info(f"  Source: {source}")
            logger.info(f"  Type: {media_type}")
            logger.info(f"  Classification: {classification}")
            logger.info(f"  Cost: ${cost:.4f}")

            if source == "pexels":
                logger.info(f"  Keywords: {vscene.get('keywords', 'N/A')}")
            elif source == "stability_ai":
                logger.info(f"  Prompt: {vscene.get('prompt_used', 'N/A')[:60]}...")

        # Resumo final
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 RESUMO DO TESTE: {test_name}")
        logger.info(f"{'='*60}")
        logger.info(f"Total de cenas: {len(visual_scenes)}")
        logger.info(f"📹 Pexels (grátis): {pexels_count} cenas")
        logger.info(f"🎨 Stability AI: {stability_count} cenas")
        logger.info(f"💰 Custo total: ${total_cost:.4f}")
        logger.info(f"📈 Taxa Pexels: {(pexels_count/len(visual_scenes)*100):.1f}%")
        logger.info(f"{'='*60}\n")

        # Salvar resultado
        output_dir = Path("./test_results")
        output_dir.mkdir(exist_ok=True)

        result_file = output_dir / f"{test_name.lower().replace(' ', '_')}_result.json"

        result = {
            "test_name": test_name,
            "timestamp": datetime.now().isoformat(),
            "brief": brief,
            "script": script,
            "visual_plan": visual_plan,
            "statistics": {
                "total_scenes": len(visual_scenes),
                "pexels_count": pexels_count,
                "stability_count": stability_count,
                "total_cost": total_cost,
                "pexels_rate": pexels_count/len(visual_scenes) if visual_scenes else 0
            }
        }

        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Resultado salvo em: {result_file}")

        return True

    except Exception as e:
        logger.error(f"❌ Erro no teste: {e}", exc_info=True)
        return False


# ============================================================================
# Main
# ============================================================================

async def main():
    """Executa os 2 testes"""

    logger.info("\n" + "="*60)
    logger.info("🚀 TESTE DO FLUXO HÍBRIDO PEXELS + STABILITY AI")
    logger.info("="*60 + "\n")

    logger.info("Este teste vai validar:")
    logger.info("✅ Classificação automática por cena")
    logger.info("✅ Busca no Pexels para cenas com pessoas")
    logger.info("✅ Geração com Stability para conceitos abstratos")
    logger.info("✅ Custo otimizado (mix inteligente)")
    logger.info("✅ Qualidade da narrativa\n")

    # input("Pressione ENTER para começar os testes...")  # Comentado para CI/CD

    # Teste 1: Corporativo (espera-se mais Pexels)
    success1 = await test_video(BRIEF_CORPORATIVO, "Vídeo Corporativo")

    if success1:
        logger.info("\n✅ Teste 1 concluído com sucesso!\n")
        # input("Pressione ENTER para o próximo teste...")  # Comentado para CI/CD

    # Teste 2: Tech/Abstrato (espera-se mix balanceado)
    success2 = await test_video(BRIEF_TECH, "Vídeo Tech")

    if success2:
        logger.info("\n✅ Teste 2 concluído com sucesso!\n")

    # Resumo geral
    logger.info("\n" + "="*60)
    logger.info("🎉 TESTES CONCLUÍDOS")
    logger.info("="*60)

    if success1 and success2:
        logger.info("✅ Ambos os testes passaram!")
        logger.info("\n📁 Verifique os resultados em: ./test_results/")
        logger.info("\nPróximos passos:")
        logger.info("1. Analise os JSONs gerados")
        logger.info("2. Verifique se classificações fazem sentido")
        logger.info("3. Valide custos por vídeo")
        logger.info("4. Teste com seus próprios briefings!")
    else:
        logger.warning("⚠️ Alguns testes falharam. Verifique os logs acima.")


if __name__ == "__main__":
    asyncio.run(main())
