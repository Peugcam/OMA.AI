"""
Teste do Script Agent
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from agents.script_agent import ScriptAgent


async def test():
    """Testa ScriptAgent com OpenRouter"""
    print("\n" + "="*80)
    print(" TESTE: Script Agent - Geracao de Roteiro")
    print("="*80 + "\n")

    try:
        print("[1/3] Criando ScriptAgent...")
        agent = ScriptAgent()
        print(f"      OK - Agent criado: {agent.llm.model}\n")

        print("[2/3] Criando briefing...")
        state = {
            "brief": {
                "title": "Cafeteria Moderna",
                "description": "Propaganda de cafeteria aconchegante com cafe especial",
                "target": "Jovens adultos 25-35 anos",
                "style": "Clean e minimalista",
                "duration": 30,
                "cta": "Visite nossa loja!"
            },
            "analysis": {
                "objective": "Atrair clientes para nova cafeteria",
                "target_audience": "Millennials urbanos",
                "style": "moderno",
                "duration_seconds": 30,
                "cta": "Visite nossa loja hoje!"
            }
        }
        print("      OK - Briefing criado\n")

        print("[3/3] Gerando roteiro...")
        result = await agent.generate_script(state)

        script = result.get("script")
        print(f"      OK - Roteiro gerado!")
        print(f"\n      Script ID: {script.get('script_id')}")
        print(f"      Titulo: {script.get('title')}")
        print(f"      Cenas: {len(script.get('scenes', []))}")
        print(f"      Modelo: {script.get('model')}")
        print(f"      Duracao: {script.get('duration_seconds')}s")

        print(f"\n      Primeira cena:")
        scene1 = script['scenes'][0]
        print(f"        Cena {scene1['scene_number']}: {scene1['time_range']}")
        print(f"        Visual: {scene1['visual_description'][:60]}...")
        print(f"        Narracao: {scene1['narration'][:60]}...")

        print("\n" + "="*80)
        print(" TESTE CONCLUIDO COM SUCESSO!")
        print("="*80 + "\n")

        print("Script Agent esta funcionando!")
        print("Proximo passo: Criar Visual, Audio e Editor agents.\n")

        return True

    except Exception as e:
        print(f"\nERRO: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test())
    sys.exit(0 if result else 1)
