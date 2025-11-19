"""
Teste SIMPLES do fluxo híbrido
Versão mínima para debug
"""

print("="*60)
print("🧪 TESTE SIMPLES - FLUXO HÍBRIDO")
print("="*60)
print()

# Step 1: Verificar imports
print("📦 Step 1: Verificando imports...")
try:
    import os
    print("  ✅ os")
    import sys
    print("  ✅ sys")
    import asyncio
    print("  ✅ asyncio")
    print()
except ImportError as e:
    print(f"  ❌ Erro básico: {e}")
    exit(1)

# Step 2: Verificar .env
print("🔑 Step 2: Verificando .env...")
try:
    from dotenv import load_dotenv
    load_dotenv()

    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    pexels_key = os.getenv("PEXELS_API_KEY")
    stability_key = os.getenv("STABILITY_API_KEY")

    if openrouter_key and openrouter_key != "sk-or-v1-your-key-here":
        print(f"  ✅ OpenRouter: {openrouter_key[:20]}...")
    else:
        print("  ⚠️ OpenRouter: não configurada")

    if pexels_key and pexels_key != "your-pexels-key-here":
        print(f"  ✅ Pexels: {pexels_key[:20]}...")
    else:
        print("  ⚠️ Pexels: não configurada")

    if stability_key and stability_key != "your-stability-key-here":
        print(f"  ✅ Stability: {stability_key[:20]}...")
    else:
        print("  ⚠️ Stability: não configurada")

    print()

except ImportError:
    print("  ⚠️ python-dotenv não instalado")
    print("     Execute: pip install python-dotenv")
    print()

# Step 3: Verificar core modules
print("📚 Step 3: Verificando core modules...")
try:
    from core import AIClient
    print("  ✅ core.AIClient")
except ImportError as e:
    print(f"  ❌ core modules: {e}")
    print()

# Step 4: Verificar agents
print("🤖 Step 4: Verificando agents...")
try:
    from agents.visual_agent import VisualAgent
    print("  ✅ agents.visual_agent.VisualAgent")

    from agents.script_agent import ScriptAgent
    print("  ✅ agents.script_agent.ScriptAgent")

    from agents.supervisor_agent import SupervisorAgent
    print("  ✅ agents.supervisor_agent.SupervisorAgent")

    print()

except ImportError as e:
    print(f"  ❌ agents: {e}")
    print()

# Step 5: Teste básico do classificador
print("🧠 Step 5: Testando classificador...")
print()

try:
    from agents.visual_agent import VisualAgent

    visual_agent = VisualAgent()
    print("  ✅ Visual Agent inicializado")

    # Teste 1: Pessoa (deve ser Pexels)
    test1 = visual_agent._classify_scene_type(
        "Pessoa sorrindo olhando para câmera",
        "feliz"
    )
    print(f"  📹 'Pessoa sorrindo' → {test1}")
    if test1 == "pexels":
        print("     ✅ Correto! (pessoas = Pexels)")
    else:
        print("     ❌ ERRADO! (deveria ser Pexels)")

    print()

    # Teste 2: Logo (deve ser Stability)
    test2 = visual_agent._classify_scene_type(
        "Logo OMA.AI em 3D holográfico com partículas de luz",
        "tecnológico"
    )
    print(f"  🎨 'Logo holográfico' → {test2}")
    if test2 == "stability":
        print("     ✅ Correto! (logo abstrato = Stability)")
    else:
        print("     ❌ ERRADO! (deveria ser Stability)")

    print()

    # Teste 3: Reunião (deve ser Pexels)
    test3 = visual_agent._classify_scene_type(
        "Equipe em reunião colaborativa no escritório",
        "profissional"
    )
    print(f"  📹 'Reunião de equipe' → {test3}")
    if test3 == "pexels":
        print("     ✅ Correto! (equipe = pessoas = Pexels)")
    else:
        print("     ❌ ERRADO! (deveria ser Pexels)")

    print()

    # Teste 4: Cérebro digital (deve ser Stability)
    test4 = visual_agent._classify_scene_type(
        "Cérebro digital com redes neurais holográficas",
        "futurista"
    )
    print(f"  🎨 'Cérebro digital' → {test4}")
    if test4 == "stability":
        print("     ✅ Correto! (conceito abstrato = Stability)")
    else:
        print("     ❌ ERRADO! (deveria ser Stability)")

    print()

except Exception as e:
    print(f"  ❌ Erro no teste: {e}")
    import traceback
    traceback.print_exc()
    print()

# Resumo
print("="*60)
print("📊 RESUMO")
print("="*60)
print()
print("Se todos os testes passaram ✅, o fluxo híbrido está funcionando!")
print()
print("Próximos passos:")
print("1. Se tudo OK → rodar: python test_hybrid_videos.py")
print("2. Se teve erro → me envie a mensagem de erro")
print()
print("="*60)
