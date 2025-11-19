"""
🎬 Teste Real - Anúncio do OMA App de Produtividade
===================================================

Este script testa o fluxo completo de criação de vídeo
com um briefing real do OMA App.
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

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# BRIEFING REAL - OMA APP
# ============================================================================

BRIEFING_OMA_APP = {
    "title": "OMA - Produtividade com IA",
    "description": """
Crie um anúncio moderno e impactante para o OMA App:

**ESTRUTURA SUGERIDA:**

1. **ABERTURA (5s)**: Pessoa frustrada com múltiplas tarefas, papéis espalhados,
   caos na mesa de trabalho. Expressão de stress.

2. **PROBLEMA (5s)**: Montagem rápida mostrando: calendários confusos,
   post-its perdidos, notificações em excesso, pessoa perdida.

3. **SOLUÇÃO - Logo OMA (3s)**: Logo do OMA aparecendo de forma holográfica
   e futurista, com efeito de partículas de IA.

4. **DEMONSTRAÇÃO (8s)**: Pessoa sorrindo usando o app no celular,
   organizando tarefas com facilidade. Interface limpa e moderna.

5. **BENEFÍCIOS (6s)**: Visualização abstrata de produtividade:
   gráficos crescentes, cérebro digital conectando ideias, fluxo otimizado.

6. **CALL-TO-ACTION (3s)**: Logo OMA + texto "Baixe Grátis" com
   botão de download destacado.

**MENSAGEM PRINCIPAL:**
"Organize sua vida. Conquiste seus objetivos. Seja mais produtivo com IA."

**TOM:** Motivacional, moderno, tecnológico, inspirador

**ESTILO VISUAL:**
- Cenas com pessoas: realistas (Pexels)
- Logo/conceitos abstratos: futurista (Stability AI)
""",
    "duration": 30,
    "target_audience": "Profissionais ocupados, empreendedores, estudantes universitários (25-40 anos)",
    "style": "modern, tech, motivational",
    "tone": "inspirational",
    "cta": "Baixe o OMA grátis e transforme sua produtividade hoje!",
    "keywords": ["produtividade", "organização", "IA", "tarefas", "objetivos", "eficiência"]
}


# ============================================================================
# FUNÇÃO DE TESTE
# ============================================================================

async def test_oma_app_ad():
    """
    Testa criação de anúncio do OMA App com fluxo híbrido completo
    """

    logger.info("="*60)
    logger.info("🎬 CRIANDO ANÚNCIO - OMA APP DE PRODUTIVIDADE")
    logger.info("="*60)
    logger.info("")

    # Criar diretório de output
    output_dir = Path("./test_results")
    output_dir.mkdir(exist_ok=True)

    # Inicializar estado
    state = {
        "brief": BRIEFING_OMA_APP,
        "task_id": f"oma_app_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "created_at": datetime.now().isoformat(),
        "current_phase": 0
    }

    try:
        # ====================================================================
        # FASE 1: SUPERVISOR - Análise
        # ====================================================================
        logger.info("📋 FASE 1: Supervisor analisando briefing...")
        logger.info("")

        supervisor = SupervisorAgent()
        state = await supervisor.analyze_request(state)

        logger.info(f"✅ Análise completa!")
        logger.info("")

        # ====================================================================
        # FASE 2: SCRIPT AGENT - Roteiro
        # ====================================================================
        logger.info("📝 FASE 2: Script Agent criando roteiro...")
        logger.info("")

        script_agent = ScriptAgent()
        state = await script_agent.generate_script(state)

        script = state.get("script", {})
        scenes = script.get("scenes", [])

        logger.info(f"✅ Roteiro criado: {len(scenes)} cenas")
        logger.info("")

        # Mostrar cenas
        for i, scene in enumerate(scenes, 1):
            logger.info(f"  Cena {i}: {scene.get('visual_description', '')[:60]}...")
            logger.info(f"  Narração: {scene.get('narration', '')[:60]}...")
            logger.info("")

        # ====================================================================
        # FASE 3: VISUAL AGENT - Mídia Híbrida
        # ====================================================================
        logger.info("🎨 FASE 3: Visual Agent (FLUXO HÍBRIDO PEXELS + STABILITY)...")
        logger.info("="*60)
        logger.info("")

        visual_agent = VisualAgent()
        state = await visual_agent.plan_visuals(state)

        visual_plan = state.get("visual_plan", {})
        visual_scenes = visual_plan.get("scenes", [])

        logger.info(f"✅ Plano visual criado: {len(visual_scenes)} cenas")
        logger.info("")

        # ====================================================================
        # ANÁLISE DE RESULTADOS
        # ====================================================================
        logger.info("📊 BREAKDOWN POR CENA:")
        logger.info("="*60)

        total_cost = 0.0
        pexels_count = 0
        stability_count = 0

        for i, scene in enumerate(visual_scenes, 1):
            source = scene.get("source", "unknown")
            media_type = scene.get("media_type", "unknown")
            cost = scene.get("cost", 0.0)
            classification = scene.get("classification", "N/A")

            total_cost += cost

            if source == "pexels":
                pexels_count += 1
                icon = "📹"
            else:
                stability_count += 1
                icon = "🎨"

            logger.info(f"{icon} Cena {i}:")
            logger.info(f"   Source: {source}")
            logger.info(f"   Type: {media_type}")
            logger.info(f"   Classification: {classification}")
            logger.info(f"   Cost: ${cost:.4f}")

            if source == "pexels":
                logger.info(f"   Keywords: {scene.get('keywords', 'N/A')}")
            else:
                prompt = scene.get('prompt_used', '')
                logger.info(f"   Prompt: {prompt[:60]}...")

            logger.info("")

        # Resumo final
        logger.info("="*60)
        logger.info("📊 RESUMO DO ANÚNCIO OMA APP")
        logger.info("="*60)
        logger.info(f"Total de cenas: {len(visual_scenes)}")
        logger.info(f"📹 Pexels (grátis): {pexels_count} cenas")
        logger.info(f"🎨 Stability AI: {stability_count} cenas")
        logger.info(f"💰 Custo total: ${total_cost:.4f}")

        if len(visual_scenes) > 0:
            pexels_rate = (pexels_count / len(visual_scenes)) * 100
            logger.info(f"📈 Taxa Pexels: {pexels_rate:.1f}%")

        logger.info("="*60)
        logger.info("")

        # Salvar resultado
        result = {
            "briefing": BRIEFING_OMA_APP,
            "script": script,
            "visual_plan": visual_plan,
            "stats": {
                "total_scenes": len(visual_scenes),
                "pexels_scenes": pexels_count,
                "stability_scenes": stability_count,
                "total_cost": total_cost,
                "pexels_percentage": (pexels_count / len(visual_scenes) * 100) if len(visual_scenes) > 0 else 0
            },
            "timestamp": datetime.now().isoformat()
        }

        result_path = output_dir / "oma_app_ad_result.json"
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Resultado salvo em: {result_path}")
        logger.info("")

        # ====================================================================
        # ANÁLISE DE QUALIDADE
        # ====================================================================
        logger.info("🔍 ANÁLISE DE QUALIDADE:")
        logger.info("="*60)

        # Verificar se logo foi para Stability (esperado)
        logo_scenes = [s for s in visual_scenes if 'logo' in str(s.get('visual_description', '')).lower()]
        if logo_scenes:
            logo_source = logo_scenes[0].get('source')
            if logo_source == 'stability_ai':
                logger.info("✅ Logo corretamente gerado com Stability AI (evita Pexels)")
            else:
                logger.info("⚠️  Logo foi para Pexels (pode não ter logo OMA específico)")

        # Verificar se pessoas foram para Pexels (esperado)
        people_scenes = [s for s in visual_scenes if any(word in str(s.get('visual_description', '')).lower()
                                                          for word in ['pessoa', 'pessoas', 'profissional'])]
        if people_scenes:
            people_pexels = sum(1 for s in people_scenes if s.get('source') == 'pexels')
            logger.info(f"✅ {people_pexels}/{len(people_scenes)} cenas com pessoas usaram Pexels (evita rostos deformados)")

        # Verificar mix
        if pexels_count > 0 and stability_count > 0:
            logger.info("✅ Mix híbrido funcionando (Pexels + Stability)")
        elif pexels_count == len(visual_scenes):
            logger.info("ℹ️  100% Pexels (todas cenas eram filméveis)")
        else:
            logger.info("ℹ️  100% Stability (todas cenas eram abstratas/específicas)")

        # Verificar custo
        if total_cost <= 0.10:
            logger.info(f"✅ Custo excelente: ${total_cost:.4f} (dentro do target)")
        else:
            logger.info(f"⚠️  Custo acima do esperado: ${total_cost:.4f}")

        logger.info("="*60)
        logger.info("")

        logger.info("✅ TESTE CONCLUÍDO COM SUCESSO!")
        logger.info("")
        logger.info("📁 Próximos passos:")
        logger.info("1. Analise o JSON gerado em ./test_results/")
        logger.info("2. Verifique se as cenas fazem sentido")
        logger.info("3. Valide se a classificação Pexels/Stability está correta")
        logger.info("4. Para gerar o vídeo completo, use o pipeline completo!")

        return True

    except Exception as e:
        logger.error(f"❌ Erro durante teste: {e}", exc_info=True)
        return False


# ============================================================================
# EXECUTAR TESTE
# ============================================================================

if __name__ == "__main__":
    print("\n")
    print(">> Iniciando teste do anuncio OMA App...")
    print("\n")

    success = asyncio.run(test_oma_app_ad())

    if success:
        print("\n>> Teste concluido com sucesso!")
    else:
        print("\n>> Teste falhou!")
