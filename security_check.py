#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔒 Security Check Script - OMA Video Generator
===============================================

Verifica questões de segurança antes do deploy.
"""

import os
import sys
import re
from pathlib import Path


def check_env_file():
    """Verifica se .env está seguro"""
    print("\n🔍 Verificando arquivo .env...")

    env_path = Path(".env")
    if not env_path.exists():
        print("  ⚠️  .env não encontrado (OK para produção)")
        return True

    # Verificar se tem keys expostas
    with open(env_path, 'r') as f:
        content = f.read()

    # Patterns de keys reais (não examples)
    key_patterns = [
        (r'OPENROUTER_API_KEY=sk-or-v1-[a-f0-9]{64}', 'OpenRouter API Key'),
        (r'PEXELS_API_KEY=[a-zA-Z0-9]{56}', 'Pexels API Key'),
        (r'STABILITY_API_KEY=sk-[a-zA-Z0-9]{48}', 'Stability AI Key'),
        (r'ELEVENLABS_API_KEY=[a-f0-9]{32}', 'ElevenLabs Key'),
    ]

    found_keys = []
    for pattern, name in key_patterns:
        if re.search(pattern, content):
            found_keys.append(name)

    if found_keys:
        print(f"  ❌ Keys encontradas em .env: {', '.join(found_keys)}")
        print("     ATENÇÃO: Não commitar este arquivo!")
        return False
    else:
        print("  ✅ .env parece seguro (sem keys detectadas)")
        return True


def check_gitignore():
    """Verifica se .env está no .gitignore"""
    print("\n🔍 Verificando .gitignore...")

    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        print("  ❌ .gitignore não encontrado!")
        return False

    with open(gitignore_path, 'r') as f:
        content = f.read()

    if '.env' in content or '*.env' in content:
        print("  ✅ .env está no .gitignore")
        return True
    else:
        print("  ❌ .env NÃO está no .gitignore!")
        print("     Adicione: echo '.env' >> .gitignore")
        return False


def check_hardcoded_secrets():
    """Verifica se há secrets hardcoded no código"""
    print("\n🔍 Verificando secrets hardcoded no código...")

    # Pastas para verificar
    dirs_to_check = ['agents', 'api', 'core']

    key_patterns = [
        r'api[_-]?key\s*=\s*["\'][a-zA-Z0-9_-]{20,}["\']',
        r'password\s*=\s*["\'].+["\']',
        r'secret\s*=\s*["\'].+["\']',
        r'token\s*=\s*["\'][a-zA-Z0-9_-]{20,}["\']',
    ]

    issues = []
    for dir_name in dirs_to_check:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            continue

        for py_file in dir_path.rglob('*.py'):
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            for pattern in key_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    # Filtrar false positives (examples, comments)
                    for match in matches:
                        if 'example' not in match.lower() and 'your-' not in match.lower():
                            issues.append((py_file, match[:50]))

    if issues:
        print(f"  ❌ Possíveis secrets hardcoded encontrados:")
        for file, snippet in issues:
            print(f"     {file}: {snippet}...")
        return False
    else:
        print("  ✅ Nenhum secret hardcoded detectado")
        return True


def check_rate_limiting():
    """Verifica se rate limiting está implementado"""
    print("\n🔍 Verificando rate limiting...")

    # Procurar por limiter no código
    api_main = Path("api/main.py")
    if not api_main.exists():
        print("  ⚠️  api/main.py não encontrado")
        return None

    with open(api_main, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'limiter' in content.lower() or '@limit' in content:
        print("  ✅ Rate limiting implementado")
        return True
    else:
        print("  ⚠️  Rate limiting NÃO detectado")
        print("     Recomendado: implementar slowapi ou similar")
        return False


def check_input_validation():
    """Verifica se input validation está implementado"""
    print("\n🔍 Verificando input validation...")

    models_file = Path("api/models.py")
    if not models_file.exists():
        print("  ⚠️  api/models.py não encontrado")
        return None

    with open(models_file, 'r', encoding='utf-8') as f:
        content = f.read()

    has_validation = 'Field' in content or 'validator' in content or 'ge=' in content
    if has_validation:
        print("  ✅ Input validation implementado (Pydantic)")
        return True
    else:
        print("  ⚠️  Input validation não detectado")
        print("     Recomendado: usar Pydantic Field com validações")
        return False


def check_subprocess_safety():
    """Verifica uso seguro de subprocess"""
    print("\n🔍 Verificando segurança de subprocess...")

    editor_file = Path("agents/editor_agent.py")
    if not editor_file.exists():
        print("  ⚠️  agents/editor_agent.py não encontrado")
        return None

    with open(editor_file, 'r', encoding='utf-8') as f:
        content = f.read()

    has_shell_true = 'shell=True' in content
    has_shlex = 'shlex.quote' in content or 'shlex.split' in content

    if has_shell_true and not has_shlex:
        print("  ❌ subprocess com shell=True SEM shlex.quote!")
        print("     RISCO: Command injection")
        return False
    elif has_shlex:
        print("  ✅ subprocess usando shlex.quote (seguro)")
        return True
    else:
        print("  ✅ subprocess sem shell=True (seguro)")
        return True


def check_dependencies_vulnerabilities():
    """Verifica vulnerabilidades conhecidas em dependências"""
    print("\n🔍 Verificando vulnerabilidades em dependências...")

    requirements = Path("requirements.txt")
    if not requirements.exists():
        print("  ⚠️  requirements.txt não encontrado")
        return None

    # Dependências conhecidas com vulnerabilidades (exemplos)
    vulnerable = {
        'urllib3<1.26.5': 'CVE-2021-33503',
        'requests<2.25.0': 'CVE-2018-18074',
        'pillow<8.3.2': 'CVE-2021-34552',
    }

    with open(requirements, 'r') as f:
        deps = f.read()

    issues = []
    for vuln_dep, cve in vulnerable.items():
        pkg, version = vuln_dep.split('<')
        if pkg in deps:
            issues.append((pkg, cve))

    if issues:
        print(f"  ⚠️  Possíveis vulnerabilidades:")
        for pkg, cve in issues:
            print(f"     {pkg}: {cve}")
        print("     Rode: pip-audit ou safety check")
        return False
    else:
        print("  ✅ Nenhuma vulnerabilidade óbvia detectada")
        print("     (Recomendado: rodar 'pip-audit' periodicamente)")
        return True


def main():
    """Roda todos os checks"""
    import sys
    import os
    # Fix Windows encoding
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("[SECURITY] OMA Video Generator - Security Check")
    print("=" * 70)

    checks = [
        check_gitignore,
        check_env_file,
        check_hardcoded_secrets,
        check_rate_limiting,
        check_input_validation,
        check_subprocess_safety,
        check_dependencies_vulnerabilities,
    ]

    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"  ❌ Erro ao executar check: {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 70)
    print("📊 RESUMO")
    print("=" * 70)

    passed = sum(1 for r in results if r is True)
    failed = sum(1 for r in results if r is False)
    warnings = sum(1 for r in results if r is None)

    print(f"✅ Passou: {passed}")
    print(f"❌ Falhou: {failed}")
    print(f"⚠️  Avisos: {warnings}")

    if failed > 0:
        print("\n⚠️  ATENÇÃO: Corrigir issues antes do deploy!")
        print("   Veja: SECURITY_DEPLOY_CHECKLIST.md")
        return 1
    elif warnings > 0:
        print("\n⚠️  AVISO: Revisar warnings antes do deploy")
        return 0
    else:
        print("\n✅ Tudo OK! Pronto para deploy seguro.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
