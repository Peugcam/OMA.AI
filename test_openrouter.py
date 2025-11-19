"""
Teste de Conexao com OpenRouter

Verifica se a API key esta funcionando.
"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from core import AIClient


def test_openrouter():
    """
    Testa conexao com OpenRouter usando GPT-4o-mini.
    """
    print("\n" + "="*80)
    print(" TESTE: Conexao com OpenRouter")
    print("="*80 + "\n")

    try:
        # Verificar API key
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key or api_key == "sk-or-v1-your-key-here":
            print("ERRO: API key nao configurada no .env")
            return False

        print(f"API Key: {api_key[:20]}...{api_key[-10:]}\n")

        # Criar client cloud (OpenRouter)
        print("[1/3] Criando AIClient para OpenRouter...")
        client = AIClient(
            model="openai/gpt-4o-mini",
            use_local=False  # Usar cloud (OpenRouter)
        )
        print(f"      OK - Cliente criado: {client.model}")
        print(f"      Provider: {client.provider}\n")

        # Testar chamada simples
        print("[2/3] Testando chamada ao modelo...")
        response = client.chat(
            messages=[
                {"role": "user", "content": "Responda apenas: 'OK'"}
            ],
            temperature=0.0,
            max_tokens=10
        )
        print(f"      Resposta: {response}")
        print(f"      OK - Chamada funcionou!\n")

        # Testar chamada criativa
        print("[3/3] Testando chamada criativa...")
        response = client.chat(
            messages=[
                {"role": "user", "content": "Crie um titulo criativo para um video sobre cafe em 5 palavras."}
            ],
            temperature=0.7,
            max_tokens=30
        )
        print(f"      Resposta: {response}")
        print(f"      OK - OpenRouter funcionando!\n")

        print("="*80)
        print(" TESTE CONCLUIDO COM SUCESSO!")
        print("="*80 + "\n")

        print("OpenRouter esta funcionando corretamente!")
        print("Agora podemos usar modelos cloud para criar videos.\n")

        return True

    except Exception as e:
        print(f"\nERRO: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = test_openrouter()
    sys.exit(0 if result else 1)
