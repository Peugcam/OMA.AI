"""
AI Client - Abstração Unificada para LLM/SLM (Local e Cloud)

Este módulo fornece uma interface única para interagir com modelos
de IA, seja localmente via Ollama ou na nuvem via OpenRouter.

Elimina duplicação de código e facilita troca entre modelos.
"""

from openai import OpenAI
import os
from typing import Literal, Optional
import time
from dotenv import load_dotenv

load_dotenv()


class AIClient:
    """
    Cliente abstrato para interagir com LLMs/SLMs.

    Suporta:
    - SLMs locais via Ollama (Phi3:mini, Gemma2:2b)
    - LLMs cloud via OpenRouter (GPT-4o-mini, Claude, etc)

    Exemplo:
        # SLM local
        client = AIClient(model="phi3:mini", use_local=True)
        response = client.chat([{"role": "user", "content": "Olá!"}])

        # LLM cloud
        client = AIClient(model="openai/gpt-4o-mini", use_local=False)
        response = client.chat([{"role": "user", "content": "Crie um roteiro"}])
    """

    def __init__(
        self,
        model: str,
        use_local: bool = False,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Inicializa cliente de IA.

        Args:
            model: Nome do modelo (ex: "phi3:mini", "openai/gpt-4o-mini")
            use_local: Se True, usa Ollama local. Se False, usa OpenRouter.
            base_url: URL customizada (opcional)
            api_key: API key customizada (opcional)
        """
        self.model = model
        self.use_local = use_local

        # Configurar cliente
        if use_local:
            # Ollama local
            self.client = OpenAI(
                base_url=base_url or os.getenv("OLLAMA_HOST", "http://localhost:11434/v1"),
                api_key=api_key or "ollama"  # Placeholder (Ollama não valida)
            )
            self.provider = "Ollama (Local)"
        else:
            # OpenRouter cloud
            self.client = OpenAI(
                base_url=base_url or "https://openrouter.ai/api/v1",
                api_key=api_key or os.getenv("OPENROUTER_API_KEY")
            )
            self.provider = "OpenRouter (Cloud)"

        # Estatísticas
        self.stats = {
            "total_calls": 0,
            "total_tokens_input": 0,
            "total_tokens_output": 0,
            "total_time_ms": 0,
            "errors": 0
        }

    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Realiza chat completion (async).

        Args:
            messages: Lista de mensagens no formato OpenAI
            temperature: Temperatura (0.0 = determinístico, 1.0 = criativo)
            max_tokens: Máximo de tokens na resposta
            system_prompt: Prompt de sistema opcional

        Returns:
            String com a resposta do modelo

        Raises:
            Exception: Se a chamada falhar
        """
        # Adicionar system prompt se fornecido
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        # Medir tempo
        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Atualizar estatísticas
            elapsed_ms = (time.time() - start_time) * 1000
            self.stats["total_calls"] += 1
            self.stats["total_time_ms"] += elapsed_ms

            # Tokens (se disponível)
            if hasattr(response, 'usage') and response.usage:
                self.stats["total_tokens_input"] += response.usage.prompt_tokens
                self.stats["total_tokens_output"] += response.usage.completion_tokens

            # Extrair resposta
            content = response.choices[0].message.content

            return content

        except Exception as e:
            self.stats["errors"] += 1
            raise Exception(f"[{self.provider}] Erro ao chamar modelo '{self.model}': {e}")

    def chat_json(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None
    ) -> dict:
        """
        Realiza chat completion esperando resposta em JSON.

        Automaticamente adiciona instruções para responder em JSON
        e faz parsing da resposta.

        Args:
            messages: Lista de mensagens
            temperature: Temperatura (recomendado: 0.0-0.5 para JSON)
            max_tokens: Máximo de tokens
            system_prompt: Prompt de sistema opcional

        Returns:
            Dict com o JSON parseado

        Raises:
            Exception: Se a resposta não for JSON válido
        """
        import json

        # Adicionar instrução de JSON ao system prompt
        json_instruction = "Responda APENAS com JSON válido, sem texto adicional."
        if system_prompt:
            system_prompt = f"{system_prompt}\n\n{json_instruction}"
        else:
            system_prompt = json_instruction

        # Chamar modelo
        response_text = self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt
        )

        # Parse JSON
        try:
            # Tentar extrair JSON de dentro do texto (caso modelo adicione explicação)
            from core.validators import ResponseValidator
            result = ResponseValidator.extract_first_json(response_text)

            if result is None:
                # Fallback: tentar parse direto
                result = json.loads(response_text)

            return result

        except json.JSONDecodeError as e:
            raise Exception(
                f"Modelo retornou texto inválido (esperado JSON):\n"
                f"{response_text[:200]}...\n"
                f"Erro: {e}"
            )

    def print_stats(self):
        """Imprime estatísticas de uso"""
        print("\n" + "="*60)
        print(f"📊 ESTATÍSTICAS - {self.provider}")
        print("="*60)
        print(f"Modelo: {self.model}")
        print(f"Total de chamadas: {self.stats['total_calls']}")

        if self.stats['total_calls'] > 0:
            avg_time = self.stats['total_time_ms'] / self.stats['total_calls']
            print(f"Tempo médio: {avg_time:.0f}ms")
            print(f"Tempo total: {self.stats['total_time_ms']/1000:.2f}s")

        if self.stats['total_tokens_input'] > 0:
            print(f"Tokens entrada: {self.stats['total_tokens_input']:,}")
            print(f"Tokens saída: {self.stats['total_tokens_output']:,}")
            print(f"Tokens totais: {self.stats['total_tokens_input'] + self.stats['total_tokens_output']:,}")

        if self.stats['errors'] > 0:
            print(f"⚠️  Erros: {self.stats['errors']}")

        print("="*60 + "\n")

    def reset_stats(self):
        """Reseta estatísticas"""
        self.stats = {
            "total_calls": 0,
            "total_tokens_input": 0,
            "total_tokens_output": 0,
            "total_time_ms": 0,
            "errors": 0
        }


class AIClientFactory:
    """
    Factory para criar clientes de IA baseado em variáveis de ambiente.

    Lê configurações do .env e cria clientes apropriados para cada agente.
    """

    @staticmethod
    def create_for_agent(
        agent_name: Literal["supervisor", "script", "visual", "audio", "editor"]
    ) -> AIClient:
        """
        Cria cliente otimizado para um agente específico.

        Args:
            agent_name: Nome do agente

        Returns:
            AIClient configurado

        Exemplo:
            supervisor_client = AIClientFactory.create_for_agent("supervisor")
            response = supervisor_client.chat([...])
        """
        # Ler configuração do .env
        model_key = f"{agent_name.upper()}_MODEL"
        use_local_key = f"{agent_name.upper()}_USE_LOCAL"

        model = os.getenv(model_key)
        use_local = os.getenv(use_local_key, "false").lower() == "true"

        if not model:
            raise ValueError(
                f"Modelo não configurado para agente '{agent_name}'. "
                f"Adicione {model_key} no .env"
            )

        return AIClient(
            model=model,
            use_local=use_local
        )

    @staticmethod
    def create_all_agents() -> dict[str, AIClient]:
        """
        Cria clientes para todos os agentes.

        Returns:
            Dict com clientes para cada agente

        Exemplo:
            clients = AIClientFactory.create_all_agents()
            supervisor = clients["supervisor"]
            script = clients["script"]
        """
        agents = ["supervisor", "script", "visual", "audio", "editor"]
        return {
            agent: AIClientFactory.create_for_agent(agent)
            for agent in agents
        }


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    print("🧪 Testando AIClient...\n")

    # Teste 1: SLM Local (Phi3:mini)
    print("=" * 60)
    print("TESTE 1: SLM Local (Phi3:mini)")
    print("=" * 60)

    try:
        local_client = AIClient(model="phi3:mini", use_local=True)

        response = local_client.chat(
            messages=[{"role": "user", "content": "Responda em 5 palavras: O que é IA?"}],
            temperature=0.3,
            max_tokens=50
        )

        print(f"✅ Resposta: {response}")
        local_client.print_stats()

    except Exception as e:
        print(f"❌ Erro: {e}\n")

    # Teste 2: LLM Cloud (via OpenRouter)
    print("=" * 60)
    print("TESTE 2: Factory - Criar clientes do .env")
    print("=" * 60)

    try:
        # Criar cliente do Supervisor (configurado no .env)
        supervisor = AIClientFactory.create_for_agent("supervisor")
        print(f"✅ Supervisor criado: {supervisor.model} ({supervisor.provider})")

        # Criar todos os agentes
        clients = AIClientFactory.create_all_agents()
        print(f"✅ Todos os agentes criados:")
        for agent, client in clients.items():
            print(f"   • {agent}: {client.model} ({'Local' if client.use_local else 'Cloud'})")

    except Exception as e:
        print(f"❌ Erro: {e}\n")

    print("\n✅ Testes concluídos!")
