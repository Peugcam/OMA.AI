"""
🌐 OpenRouter Client - SLMs via API
====================================

Cliente para usar SLMs através da OpenRouter API.
Vantagens:
- ✅ Sem download de modelos (0 GB)
- ✅ Setup em 2 minutos
- ✅ Funciona em qualquer máquina
- ✅ Acesso a dezenas de modelos

Modelos Recomendados (SLMs baratos):
- google/gemma-2-9b-it          ($0.20/$0.20 per 1M tokens)
- meta-llama/llama-3.2-3b       ($0.06/$0.06 per 1M tokens)
- qwen/qwen-2.5-7b-instruct     ($0.09/$0.09 per 1M tokens)
- mistralai/mistral-7b-instruct ($0.06/$0.06 per 1M tokens)
- microsoft/phi-3-mini          ($0.10/$0.10 per 1M tokens)
"""

import os
from typing import Optional, Dict, Any, List
import httpx
import json
import asyncio
from datetime import datetime


class OpenRouterClient:
    """Cliente para OpenRouter API"""

    BASE_URL = "https://openrouter.ai/api/v1"

    # Modelos SLM otimizados para cada agente
    MODELS = {
        "supervisor": "qwen/qwen-2.5-7b-instruct",     # Melhor reasoning
        "script": "microsoft/phi-3.5-mini-128k",       # Criativo
        "visual": "google/gemma-2-9b-it",              # Classificação
        "audio": "mistralai/mistral-7b-instruct-v0.3", # Balanceado
        "editor": "meta-llama/llama-3.2-3b-instruct"   # Rápido
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ):
        """
        Inicializa cliente OpenRouter.

        Args:
            api_key: OpenRouter API key (ou via env OPENROUTER_API_KEY)
            model: Modelo a usar (ou auto-detect por agente)
            temperature: Criatividade (0-1)
            max_tokens: Máximo de tokens na resposta
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY não encontrada. "
                "Defina em .env ou passe como parâmetro."
            )

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/Peugcam/OMA_v3",
                "X-Title": "OMA - Video Creator"
            },
            timeout=300.0  # 5 minutos timeout
        )

    @classmethod
    def for_agent(cls, agent_type: str, **kwargs) -> "OpenRouterClient":
        """
        Cria cliente otimizado para um tipo de agente.

        Args:
            agent_type: "supervisor", "script", "visual", "audio", "editor"

        Returns:
            Cliente configurado com modelo apropriado
        """
        model = cls.MODELS.get(agent_type.lower())
        if not model:
            raise ValueError(f"Tipo de agente desconhecido: {agent_type}")

        # Temperaturas recomendadas por agente
        temperatures = {
            "supervisor": 0.3,  # Decisões determinísticas
            "script": 0.8,      # Criativo
            "visual": 0.5,      # Classificação
            "audio": 0.6,       # Balanceado
            "editor": 0.2       # Preciso
        }

        return cls(
            model=model,
            temperature=temperatures.get(agent_type.lower(), 0.7),
            **kwargs
        )

    async def generate(
        self,
        prompt: str,
        system: str = "",
        **kwargs
    ) -> str:
        """
        Gera resposta do modelo.

        Args:
            prompt: Prompt do usuário
            system: System prompt (contexto)
            **kwargs: Parâmetros adicionais

        Returns:
            Resposta do modelo como string
        """
        messages = []

        if system:
            messages.append({"role": "system", "content": system})

        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "top_p": kwargs.get("top_p", 1.0),
            "frequency_penalty": kwargs.get("frequency_penalty", 0),
            "presence_penalty": kwargs.get("presence_penalty", 0)
        }

        try:
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()

            data = response.json()
            return data["choices"][0]["message"]["content"]

        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            raise Exception(f"OpenRouter API error: {error_detail}")

        except Exception as e:
            raise Exception(f"Error calling OpenRouter: {str(e)}")

    async def generate_stream(
        self,
        prompt: str,
        system: str = "",
        **kwargs
    ):
        """
        Gera resposta em streaming (útil para UI).

        Yields:
            Chunks da resposta conforme vão chegando
        """
        messages = []

        if system:
            messages.append({"role": "system", "content": system})

        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "stream": True
        }

        try:
            async with self.client.stream("POST", "/chat/completions", json=payload) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: "

                        if data_str == "[DONE]":
                            break

                        try:
                            data = json.loads(data_str)
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue

        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            raise Exception(f"OpenRouter API error: {error_detail}")

    async def get_models(self) -> List[Dict[str, Any]]:
        """
        Lista modelos disponíveis na OpenRouter.

        Returns:
            Lista de modelos com informações (nome, preço, contexto)
        """
        try:
            response = await self.client.get("/models")
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])

        except Exception as e:
            raise Exception(f"Error fetching models: {str(e)}")

    async def close(self):
        """Fecha cliente HTTP"""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

async def example_basic():
    """Exemplo básico de uso"""
    async with OpenRouterClient(model="qwen/qwen-2.5-7b-instruct") as client:
        response = await client.generate(
            prompt="Escreva um roteiro de 30s para propaganda de cafeteria",
            system="Você é um roteirista profissional"
        )
        print(response)


async def example_by_agent():
    """Exemplo usando cliente otimizado por agente"""

    # Cliente para supervisor (decisões precisas)
    supervisor = OpenRouterClient.for_agent("supervisor")

    # Cliente para script (criativo)
    script = OpenRouterClient.for_agent("script")

    # Usar
    analysis = await supervisor.generate(
        "Analise esta requisição: criar vídeo de cafeteria"
    )

    roteiro = await script.generate(
        "Escreva roteiro baseado nesta análise: " + analysis
    )

    await supervisor.close()
    await script.close()


async def example_streaming():
    """Exemplo com streaming (para UI responsiva)"""
    async with OpenRouterClient.for_agent("script") as client:
        print("Gerando roteiro...")

        async for chunk in client.generate_stream(
            prompt="Escreva um roteiro de propaganda de cafeteria",
            system="Você é um roteirista criativo"
        ):
            print(chunk, end="", flush=True)

        print("\n✅ Completo!")


if __name__ == "__main__":
    # Teste rápido
    print("🧪 Testando OpenRouter Client...")

    # Verificar API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY não configurada")
        print("Configure em .env:")
        print("OPENROUTER_API_KEY=sk-or-v1-...")
    else:
        print(f"✅ API Key encontrada: {api_key[:15]}...")

        # Rodar exemplo
        asyncio.run(example_basic())
