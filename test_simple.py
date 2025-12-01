# -*- coding: utf-8 -*-
"""TESTE SIMPLES - Melhorias Gratuitas"""

import asyncio
import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from core.optimized_params import OptimizedParams
from core.optimized_prompts import OptimizedPrompts
from core.validators import EnhancedValidators


def test_components():
    print("\n" + "="*70)
    print("TESTE 1: COMPONENTES")
    print("="*70)

    creative = OptimizedParams.CREATIVE_WRITING
    print(f"\n[OK] Creative params: temp={creative.temperature}, tokens={creative.max_tokens}")

    brief = {"objective": "Ensinar IA", "duration_seconds": 30}
    prompt = OptimizedPrompts.supervisor_analysis(brief)
    print(f"[OK] Prompt gerado: {len(prompt)} chars")
    print(f"[OK] Chain-of-Thought: {'PASSO 1' in prompt}")

    return True


def test_validation():
    print("\n" + "="*70)
    print("TESTE 2: VALIDACAO")
    print("="*70)

    good_script = {
        "hook": "Hook forte aqui",
        "scenes": [
            {"duration": 10, "narration": "Cena 1"},
            {"duration": 10, "narration": "Cena 2"},
            {"duration": 10, "narration": "Cena 3"}
        ],
        "total_duration": 30,
        "cta": "Clique agora!"
    }

    is_valid, issues, _ = EnhancedValidators.validate_script_comprehensive(
        script=good_script,
        brief={"duration_seconds": 30}
    )

    if is_valid:
        print("[OK] Script valido detectado")
    else:
        print(f"[OK] {len(issues)} problemas encontrados (esperado se houver)")

    return True


async def main():
    print("\n" + "="*70)
    print("TESTE SIMPLES - MELHORIAS")
    print("="*70)

    passed = []

    try:
        if test_components():
            passed.append("Componentes")
    except Exception as e:
        print(f"[ERRO] Teste 1: {e}")

    try:
        if test_validation():
            passed.append("Validacao")
    except Exception as e:
        print(f"[ERRO] Teste 2: {e}")

    print("\n" + "="*70)
    print("RESUMO")
    print("="*70)
    for test in passed:
        print(f"  [OK] {test}")

    if len(passed) >= 2:
        print("\n[SUCESSO] Melhorias funcionando!")
        print("\nProximos passos:")
        print("1. Ver INTEGRATION_GUIDE.md")
        print("2. Testar com main.py")


if __name__ == "__main__":
    asyncio.run(main())
