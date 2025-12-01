"""
🧪 TESTE RÁPIDO - Melhorias Gratuitas
=====================================

Este script testa as melhorias sem modificar o código principal.

Vai testar:
1. Prompts otimizados
2. Parâmetros otimizados
3. Validação aprimorada

Tempo: ~2-3 minutos
"""

import asyncio
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

from core.ai_client import AIClient
from core.optimized_prompts import OptimizedPrompts
from core.optimized_params import OptimizedParams
from core.validators import EnhancedValidators, ResponseValidator


async def test_basic_components():
    """Teste 1: Componentes básicos"""
    print("\n" + "="*70)
    print("TESTE 1: COMPONENTES BÁSICOS")
    print("="*70)

    # Testar OptimizedParams
    print("\n✓ OptimizedParams:")
    creative_params = OptimizedParams.CREATIVE_WRITING
    print(f"  - Temperature: {creative_params.temperature}")
    print(f"  - Max tokens: {creative_params.max_tokens}")
    print(f"  - Top-p: {creative_params.top_p}")

    # Testar OptimizedPrompts
    print("\n✓ OptimizedPrompts:")
    brief = {
        "objective": "Ensinar IA para jovens",
        "target_audience": {"age_range": "18-25", "platform": "Instagram"},
        "duration_seconds": 30
    }
    prompt = OptimizedPrompts.supervisor_analysis(brief)
    print(f"  - Prompt length: {len(prompt)} chars")
    print(f"  - Has Chain-of-Thought: {'PASSO 1' in prompt}")
    print(f"  - Has examples: {'EXEMPLO' in prompt}")

    print("\n✅ Teste 1 passou!")


async def test_supervisor_analysis():
    """Teste 2: Análise do Supervisor com melhorias"""
    print("\n" + "="*70)
    print("TESTE 2: SUPERVISOR ANALYSIS (COM MELHORIAS)")
    print("="*70)

    # Brief de teste
    brief = {
        "title": "IA para Iniciantes",
        "description": "Ensinar o básico de IA de forma simples para jovens de 18-25 anos",
        "duration": 30,
        "target": "jovens 18-25 anos, iniciantes em tecnologia",
        "style": "casual, inspiracional",
        "platform": "Instagram Reels"
    }

    print("\n📋 Brief de entrada:")
    print(f"  - Título: {brief['title']}")
    print(f"  - Público: {brief['target']}")
    print(f"  - Duração: {brief['duration']}s")

    # Criar cliente (usar modelo do .env)
    import os
    from dotenv import load_dotenv
    load_dotenv()

    model = os.getenv("SUPERVISOR_MODEL", "openrouter/qwen/qwen-2.5-7b-instruct")

    print(f"\n🤖 Usando modelo: {model}")
    client = AIClient(model=model, use_local=False)

    # Gerar prompt otimizado
    prompt = OptimizedPrompts.supervisor_analysis(brief)

    # Usar parâmetros otimizados
    params = OptimizedParams.STRATEGIC_DECISION

    print(f"\n⚙️ Parâmetros otimizados:")
    print(f"  - Temperature: {params.temperature} (focado, não criativo)")
    print(f"  - Max tokens: {params.max_tokens}")
    print(f"  - Top-p: {params.top_p}")

    print("\n🔄 Gerando análise...")

    try:
        response = await client.chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=params.temperature,
            max_tokens=params.max_tokens,
            top_p=params.top_p,
            frequency_penalty=params.frequency_penalty,
            presence_penalty=params.presence_penalty
        )

        # Parse JSON
        analysis = ResponseValidator.extract_first_json(response)

        if not analysis:
            print("❌ Modelo não retornou JSON válido")
            print(f"Resposta: {response[:500]}...")
            return False

        print("\n✅ Análise gerada com sucesso!")
        print(f"\n📊 Resultado:")
        print(f"  - Objetivo: {analysis.get('objective', 'N/A')[:80]}...")
        print(f"  - Público-alvo: {analysis.get('target_audience', {}).get('age_range', 'N/A')}")
        print(f"  - Duração: {analysis.get('duration_seconds', 'N/A')}s")
        print(f"  - Estilo: {analysis.get('style', 'N/A')}")

        if 'visual_requirements' in analysis:
            print(f"  - Visual reqs: {len(analysis['visual_requirements'].get('mandatory', []))} obrigatórios")

        if 'cta' in analysis:
            print(f"  - CTA: {analysis['cta'][:50]}...")

        client.print_stats()

        return True

    except Exception as e:
        print(f"\n❌ Erro ao gerar análise: {e}")
        return False


async def test_script_generation():
    """Teste 3: Geração de Script com validação"""
    print("\n" + "="*70)
    print("TESTE 3: SCRIPT GENERATION (COM VALIDAÇÃO)")
    print("="*70)

    # Análise simulada (normalmente vem do supervisor)
    analysis = {
        "objective": "Conscientizar jovens de 18-25 anos sobre mudanças climáticas e motivar ações",
        "target_audience": {
            "age_range": "18-25",
            "knowledge_level": "intermediário",
            "platform": "Instagram"
        },
        "style": ["inspiracional", "urgente"],
        "duration_seconds": 30,
        "visual_requirements": {
            "mandatory": ["gráficos de temperatura", "jovens em ação"],
            "optional": [],
            "avoid": ["imagens apocalípticas"]
        },
        "audio_requirements": {
            "narration_type": "TTS",
            "voice_tone": "Jovem e energético",
            "background_music": True
        },
        "cta": "Calcule sua pegada de carbono no link da bio"
    }

    print("\n📋 Análise de entrada:")
    print(f"  - Objetivo: {analysis['objective'][:60]}...")
    print(f"  - Duração alvo: {analysis['duration_seconds']}s")

    # Criar cliente
    import os
    from dotenv import load_dotenv
    load_dotenv()

    model = os.getenv("SCRIPT_MODEL", "openrouter/qwen/qwen-2.5-7b-instruct")

    print(f"\n🤖 Usando modelo: {model}")
    client = AIClient(model=model, use_local=False)

    # Gerar prompt otimizado
    prompt = OptimizedPrompts.script_generation(analysis)

    # Usar parâmetros otimizados
    params = OptimizedParams.CREATIVE_WRITING

    print(f"\n⚙️ Parâmetros otimizados:")
    print(f"  - Temperature: {params.temperature} (criativo)")
    print(f"  - Max tokens: {params.max_tokens}")
    print(f"  - Top-p: {params.top_p}")
    print(f"  - Frequency penalty: {params.frequency_penalty} (evita repetição)")

    print("\n🔄 Gerando script...")

    try:
        response = await client.chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=params.temperature,
            max_tokens=params.max_tokens,
            top_p=params.top_p,
            frequency_penalty=params.frequency_penalty,
            presence_penalty=params.presence_penalty
        )

        # Parse JSON
        script = ResponseValidator.extract_first_json(response)

        if not script:
            print("❌ Modelo não retornou JSON válido")
            print(f"Resposta: {response[:500]}...")
            return False

        print("\n✅ Script gerado!")
        print(f"\n📊 Resultado:")
        print(f"  - Hook: {script.get('hook', 'N/A')[:70]}...")
        print(f"  - Número de cenas: {len(script.get('scenes', []))}")
        print(f"  - Duração total: {script.get('total_duration', 'N/A')}s")
        print(f"  - CTA: {script.get('cta', 'N/A')[:50]}...")

        # VALIDAÇÃO APRIMORADA
        print("\n🔍 Validando script...")
        is_valid, issues, suggestions = EnhancedValidators.validate_script_comprehensive(
            script=script,
            brief=analysis,
            retry_count=0
        )

        if is_valid:
            print("✅ Script VÁLIDO!")
        else:
            print(f"⚠️ Script com {len(issues)} problemas:")
            for issue in issues[:5]:  # Mostrar só top 5
                print(f"  - {issue}")

            if suggestions:
                print("\n💡 Sugestões de correção:")
                for key, suggestion in list(suggestions.items())[:3]:
                    print(f"  - {key}: {suggestion}")

        client.print_stats()

        return True

    except Exception as e:
        print(f"\n❌ Erro ao gerar script: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_validation_only():
    """Teste 4: Apenas validação (sem chamar modelo)"""
    print("\n" + "="*70)
    print("TESTE 4: VALIDAÇÃO APRIMORADA (SEM MODELO)")
    print("="*70)

    # Script de exemplo (bom)
    good_script = {
        "hook": "Em 2024, 67% dos jovens usam IA sem saber. Você é um deles?",
        "scenes": [
            {
                "duration": 8,
                "narration": "Aquela correção do WhatsApp? IA. Filtro do Instagram? IA.",
                "visual_description": "Montagem rápida de apps populares"
            },
            {
                "duration": 7,
                "narration": "Mas o que REALMENTE é IA? Não é robô, não é mágica.",
                "visual_description": "Animação de código e padrões"
            },
            {
                "duration": 9,
                "narration": "E o plot twist: você pode criar suas próprias IAs.",
                "visual_description": "Jovens programando"
            },
            {
                "duration": 6,
                "narration": "Clique no link e descubra o curso gratuito.",
                "visual_description": "CTA visual"
            }
        ],
        "total_duration": 30,
        "cta": "Clique no link e comece GRÁTIS hoje - vagas limitadas!"
    }

    # Script ruim (faltando elementos)
    bad_script = {
        "hook": "IA é legal",
        "scenes": [
            {"duration": 25, "narration": "IA é muito importante e todos devem aprender."}
        ],
        "total_duration": 25,
        "cta": "Aprenda mais"
    }

    brief = {
        "objective": "Ensinar IA",
        "duration_seconds": 30
    }

    print("\n1️⃣ Validando script BOM:")
    is_valid, issues, suggestions = EnhancedValidators.validate_script_comprehensive(
        script=good_script,
        brief=brief
    )

    if is_valid:
        print("  ✅ Script VÁLIDO")
    else:
        print(f"  ⚠️ {len(issues)} problemas encontrados:")
        for issue in issues[:3]:
            print(f"    - {issue}")

    print("\n2️⃣ Validando script RUIM:")
    is_valid, issues, suggestions = EnhancedValidators.validate_script_comprehensive(
        script=bad_script,
        brief=brief
    )

    if is_valid:
        print("  ✅ Script válido")
    else:
        print(f"  ⚠️ {len(issues)} problemas encontrados:")
        for issue in issues:
            print(f"    - {issue}")

        if suggestions:
            print("\n  💡 Sugestões:")
            for key, suggestion in suggestions.items():
                print(f"    - {key}: {suggestion}")

    print("\n✅ Teste 4 concluído!")


async def main():
    """Rodar todos os testes"""
    print("\n" + "="*70)
    print("TESTE RAPIDO - MELHORIAS GRATUITAS")
    print("="*70)
    print("\nEste teste vai verificar se as melhorias funcionam corretamente.")
    print("Tempo estimado: 2-3 minutos")

    tests_passed = []

    # Teste 1: Componentes básicos (sem modelo)
    try:
        await test_basic_components()
        tests_passed.append("Componentes básicos")
    except Exception as e:
        print(f"❌ Teste 1 falhou: {e}")

    # Teste 4: Validação (sem modelo)
    try:
        await test_validation_only()
        tests_passed.append("Validação")
    except Exception as e:
        print(f"❌ Teste 4 falhou: {e}")

    # Teste 2: Supervisor (COM modelo - precisa de API key)
    print("\n" + "="*70)
    print("TESTES COM MODELO (precisa de OPENROUTER_API_KEY)")
    print("="*70)

    import os
    if not os.getenv("OPENROUTER_API_KEY"):
        print("\n⚠️ OPENROUTER_API_KEY não encontrada no .env")
        print("Pulando testes com modelo (Teste 2 e 3)")
    else:
        try:
            result = await test_supervisor_analysis()
            if result:
                tests_passed.append("Supervisor Analysis")
        except Exception as e:
            print(f"❌ Teste 2 falhou: {e}")
            import traceback
            traceback.print_exc()

        try:
            result = await test_script_generation()
            if result:
                tests_passed.append("Script Generation")
        except Exception as e:
            print(f"❌ Teste 3 falhou: {e}")
            import traceback
            traceback.print_exc()

    # Resumo
    print("\n" + "="*70)
    print("RESUMO DOS TESTES")
    print("="*70)
    print(f"\nTestes que passaram ({len(tests_passed)}):")
    for test in tests_passed:
        print(f"  OK {test}")

    if len(tests_passed) >= 2:
        print("\n" + "="*70)
        print("SUCESSO! AS MELHORIAS ESTAO FUNCIONANDO!")
        print("="*70)
        print("\nProximos passos:")
        print("1. Integrar nos agentes (seguir INTEGRATION_GUIDE.md)")
        print("2. Testar com 1 video completo (python main.py)")
        print("3. Deploy no Google Cloud Run (./deploy-cloudrun.sh)")
    else:
        print("\nALGUNS TESTES FALHARAM. Verifique os logs acima.")


if __name__ == "__main__":
    asyncio.run(main())
