# -*- coding: utf-8 -*-
"""
TESTE DAS SKILLS DE PRODUCAO DE VIDEO
Valida que as skills funcionam corretamente antes do commit
"""

import sys
import os
from pathlib import Path

# Fix encoding for Windows
if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Adicionar path do projeto
sys.path.insert(0, str(Path(__file__).parent))

from skills_system.skill_manager import SkillManager
from skills_library.video_scripting_skill import VideoScriptingSkill
from skills_library.tech_explanation_skill import TechExplanationSkill
from skills_library.visual_design_skill import VisualDesignSkill


def test_video_scripting_skill():
    """Teste da VideoScriptingSkill"""
    print("=" * 80)
    print("[TEST] TESTE 1: VideoScriptingSkill")
    print("=" * 80)

    try:
        # Criar skill
        skill = VideoScriptingSkill()

        # Tarefa de teste
        task = """
        Criar roteiro de 60 segundos sobre:
        "Como aprender Python em 30 dias"

        Público: Desenvolvedores iniciantes (18-25 anos)
        Tom: Encorajador mas direto
        Formato: TikTok/Shorts vertical
        """

        # Aplicar skill
        prompt = skill.apply(task)

        # Validações
        assert skill.metadata.name == "VideoScriptingSkill"
        assert skill.metadata.version == "1.0.0"
        assert len(skill.get_procedure().steps) == 5  # 5 fases do roteiro
        assert len(skill.get_best_practices()) > 0
        assert len(skill.get_examples()) > 0

        # Verificar que tem estrutura de roteiro viral
        procedure = skill.get_procedure()
        steps_text = ' '.join(procedure.steps).lower()
        assert 'hook' in steps_text
        assert 'problema' in steps_text
        assert 'solução' in steps_text or 'solucao' in steps_text
        assert 'cta' in steps_text

        print("[OK] VideoScriptingSkill carregada com sucesso!")
        print(f"   - Nome: {skill.metadata.name}")
        print(f"   - Versao: {skill.metadata.version}")
        print(f"   - Passos: {len(skill.get_procedure().steps)}")
        print(f"   - Best Practices: {len(skill.get_best_practices())}")
        print(f"   - Exemplos: {len(skill.get_examples())}")
        print(f"   - Prompt gerado: {len(prompt)} caracteres")
        print(f"   - Estrutura viral: Hook, Problema, Solucao, CTA [OK]")

        # Salvar skill
        filepath = skill.save("./skills_library")
        print(f"   - Salva em: {filepath}")

        return True

    except Exception as e:
        print(f"[FAIL] ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tech_explanation_skill():
    """Teste da TechExplanationSkill"""
    print("\n")
    print("=" * 80)
    print("[TEST] TESTE 2: TechExplanationSkill")
    print("=" * 80)

    try:
        # Criar skill
        skill = TechExplanationSkill()

        # Tarefa de teste
        task = """
        Explicar "Docker e Containers" para:
        - Público: Devs iniciantes que só conhecem HTML/CSS/JS
        - Contexto: Vão usar Docker no primeiro projeto backend
        - Objetivo: Entender o suficiente para usar docker-compose
        """

        # Aplicar skill
        prompt = skill.apply(task)

        # Validações
        assert skill.metadata.name == "TechExplanationSkill"
        assert skill.metadata.version == "1.0.0"
        assert len(skill.get_procedure().steps) > 0
        assert len(skill.get_best_practices()) > 0
        assert len(skill.get_examples()) > 0

        # Verificar que usa Técnica Feynman
        procedure = skill.get_procedure()
        steps_text = ' '.join(procedure.steps).lower()
        assert 'analogia' in steps_text or 'analoga' in steps_text
        assert 'exemplo' in steps_text

        print("[OK] TechExplanationSkill carregada com sucesso!")
        print(f"   - Nome: {skill.metadata.name}")
        print(f"   - Versao: {skill.metadata.version}")
        print(f"   - Passos: {len(skill.get_procedure().steps)}")
        print(f"   - Best Practices: {len(skill.get_best_practices())}")
        print(f"   - Exemplos: {len(skill.get_examples())}")
        print(f"   - Prompt gerado: {len(prompt)} caracteres")
        print(f"   - Tecnica Feynman: Analogias + Exemplos [OK]")

        # Salvar skill
        filepath = skill.save("./skills_library")
        print(f"   - Salva em: {filepath}")

        return True

    except Exception as e:
        print(f"[FAIL] ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_visual_design_skill():
    """Teste da VisualDesignSkill"""
    print("\n")
    print("=" * 80)
    print("[TEST] TESTE 3: VisualDesignSkill")
    print("=" * 80)

    try:
        # Criar skill
        skill = VisualDesignSkill()

        # Tarefa de teste
        task = """
        Criar storyboard visual para vídeo de 90 segundos:
        "Como criar seu primeiro projeto Python do zero"

        Público: Iniciantes absolutos em programação
        Objetivo: Vídeo educacional calmo e encorajador
        Formato: 9:16 vertical (TikTok/Shorts)
        """

        # Aplicar skill
        prompt = skill.apply(task)

        # Validações
        assert skill.metadata.name == "VisualDesignSkill"
        assert skill.metadata.version == "1.0.0"
        assert len(skill.get_procedure().steps) > 0
        assert len(skill.get_best_practices()) > 0
        assert len(skill.get_examples()) > 0

        # Verificar que trata design visual
        procedure = skill.get_procedure()
        steps_text = ' '.join(procedure.steps).lower()
        assert 'cor' in steps_text or 'visual' in steps_text or 'paleta' in steps_text
        assert 'storyboard' in steps_text or 'frame' in steps_text

        print("[OK] VisualDesignSkill carregada com sucesso!")
        print(f"   - Nome: {skill.metadata.name}")
        print(f"   - Versao: {skill.metadata.version}")
        print(f"   - Passos: {len(skill.get_procedure().steps)}")
        print(f"   - Best Practices: {len(skill.get_best_practices())}")
        print(f"   - Exemplos: {len(skill.get_examples())}")
        print(f"   - Prompt gerado: {len(prompt)} caracteres")
        print(f"   - Design Visual: Paleta, Storyboard, Animacoes [OK]")

        # Salvar skill
        filepath = skill.save("./skills_library")
        print(f"   - Salva em: {filepath}")

        return True

    except Exception as e:
        print(f"[FAIL] ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_skill_manager():
    """Teste do SkillManager"""
    print("\n")
    print("=" * 80)
    print("[TEST] TESTE 4: SkillManager (Integracao)")
    print("=" * 80)

    try:
        # Criar manager
        manager = SkillManager(skills_dir="./skills_library")

        # Registrar skills
        manager.register_skill(VideoScriptingSkill())
        manager.register_skill(TechExplanationSkill())
        manager.register_skill(VisualDesignSkill())

        # Validar registro
        assert "VideoScriptingSkill_1.0.0" in manager.skills
        assert "TechExplanationSkill_1.0.0" in manager.skills
        assert "VisualDesignSkill_1.0.0" in manager.skills

        print("[OK] SkillManager funcionando!")
        print(f"   - Skills registradas: {len(manager.skills)}")

        # Testar recomendação
        recommendations = manager.recommend_skills(
            "Criar video viral sobre programacao Python"
        )

        print(f"   - Recomendacoes: {len(recommendations)}")
        if recommendations:
            top = recommendations[0]
            print(f"   - Top skill: {top[0]} (score: {top[1]:.2f})")

        # Testar execução
        prompt, metadata = manager.execute_with_rag(
            skill_id="VideoScriptingSkill_1.0.0",
            task="Criar roteiro viral sobre IA"
        )

        assert len(prompt) > 0
        assert "skill_id" in metadata

        print(f"   - Prompt gerado: {len(prompt)} caracteres")
        print(f"   - Skill usada: {metadata['skill_id']}")

        # Testar estatísticas
        stats = manager.get_stats()
        print(f"   - Total skills: {stats['total_skills']}")

        return True

    except Exception as e:
        print(f"[FAIL] ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multi_skill_video_creation():
    """Teste de integração completa - Criação de vídeo com múltiplas skills"""
    print("\n")
    print("=" * 80)
    print("[TEST] TESTE 5: Criacao de Video Completa (Multi-Skill)")
    print("=" * 80)

    try:
        manager = SkillManager()
        manager.register_skill(VideoScriptingSkill())
        manager.register_skill(TechExplanationSkill())
        manager.register_skill(VisualDesignSkill())

        # Caso real: Criar vídeo educacional técnico
        task = """
        Criar vídeo completo de 90 segundos sobre:
        "O que é Machine Learning e como começar"

        Público: Iniciantes em programação, 18-25 anos
        Objetivo: Educar + inspirar a aprender ML
        Formato: YouTube Shorts (9:16)
        """

        # Usar múltiplas skills
        prompt, metadata = manager.execute_multi_skill(
            skill_ids=[
                "TechExplanationSkill_1.0.0",  # Explica ML simplesmente
                "VideoScriptingSkill_1.0.0",   # Estrutura viral
                "VisualDesignSkill_1.0.0"      # Planeja visual
            ],
            task=task
        )

        # Validações de conteúdo
        prompt_lower = prompt.lower()
        assert 'hook' in prompt_lower or 'estrutura' in prompt_lower
        assert 'analogia' in prompt_lower or 'exemplo' in prompt_lower
        assert 'visual' in prompt_lower or 'cor' in prompt_lower or 'paleta' in prompt_lower

        print("[OK] Criacao de video completa funcionando!")
        print(f"   - Prompt gerado: {len(prompt)} caracteres")
        print(f"   - Skills combinadas: {len(metadata.get('skills_used', []))}")
        print(f"   - Contem explicacao tecnica: [OK]")
        print(f"   - Contem estrutura viral: [OK]")
        print(f"   - Contem planejamento visual: [OK]")
        print(f"   - Pronto para gerar video profissional!")

        return True

    except Exception as e:
        print(f"[FAIL] ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executa todos os testes"""
    print("\n")
    print("=" * 80)
    print("      TESTE DAS SKILLS DE PRODUCAO DE VIDEO - OMA.AI")
    print("=" * 80)
    print("\n")

    results = []

    # Executar testes
    results.append(("VideoScriptingSkill", test_video_scripting_skill()))
    results.append(("TechExplanationSkill", test_tech_explanation_skill()))
    results.append(("VisualDesignSkill", test_visual_design_skill()))
    results.append(("SkillManager", test_skill_manager()))
    results.append(("Multi-Skill Video Creation", test_multi_skill_video_creation()))

    # Resumo
    print("\n")
    print("=" * 80)
    print("[STATS] RESUMO DOS TESTES")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[OK] PASSOU" if result else "[FAIL] FALHOU"
        print(f"{status} - {name}")

    print("\n" + "-" * 80)
    print(f"RESULTADO FINAL: {passed}/{total} testes passaram")
    print("-" * 80)

    if passed == total:
        print("\n[SUCCESS] TODOS OS TESTES PASSARAM!")
        print("[OK] Sistema de Skills pronto para commit no GitHub!")
        return 0
    else:
        print(f"\n[FAIL] {total - passed} teste(s) falharam!")
        print("[WARN] Corrija os erros antes do commit!")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
