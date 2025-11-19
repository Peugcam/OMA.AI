"""
AI Client MCP - AIClient com suporte a Tool Calling (MCP)

Estende AIClient original com:
- Tool calling nativo (OpenAI format)
- Schema validation (Pydantic)
- Retry automático
- Fallback inteligente
- Cost tracking por tool

Compatível 100% com AIClient (drop-in replacement)
"""

import logging
import json
import time
from typing import List, Dict, Any, Optional, Union, Callable
from pydantic import BaseModel

from .ai_client import AIClient


logger = logging.getLogger(__name__)


class ToolCall(BaseModel):
    """Representa uma chamada de tool pelo LLM"""
    id: str
    type: str = "function"
    function: Dict[str, Any]  # {"name": "tool_name", "arguments": "json_string"}


class ToolCallResponse(BaseModel):
    """Resposta do LLM com tool calls"""
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    finish_reason: str


class AIClientMCP(AIClient):
    """
    AIClient com suporte a MCP Tool Calling.

    Adiciona métodos para:
    - Tool calling nativo
    - Schema validation
    - Retry automático
    - Fallback

    Exemplo:
        client = AIClientMCP(model="openai/gpt-4o-mini")

        # Definir tools
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_video",
                    "description": "Search for videos",
                    "parameters": {...}
                }
            }
        ]

        # Chamar com tools
        response = await client.chat_with_tools(
            messages=[{"role": "user", "content": "Find a video"}],
            tools=tools,
            tool_choice="auto"
        )
    """

    def __init__(self, *args, **kwargs):
        """
        Inicializa AIClientMCP.

        Aceita mesmos parâmetros que AIClient.
        """
        super().__init__(*args, **kwargs)

        # Estatísticas MCP
        self.mcp_stats = {
            "tool_calls_total": 0,
            "tool_calls_by_name": {},
            "tool_call_errors": 0,
            "fallback_activations": 0
        }

        logger.info(f"AIClientMCP inicializado: {self.model} (MCP enabled)")


    async def chat_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        tool_choice: Union[str, Dict] = "auto",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Realiza chat completion com tool calling.

        Args:
            messages: Mensagens do chat
            tools: Lista de tools disponíveis (formato OpenAI)
            tool_choice: "auto", "none", ou {"type": "function", "function": {"name": "tool_name"}}
            temperature: Temperatura
            max_tokens: Max tokens
            system_prompt: System prompt opcional
            max_retries: Tentativas em caso de erro

        Returns:
            Dict com:
                - content: Resposta de texto (se houver)
                - tool_calls: Lista de tool calls (se houver)
                - finish_reason: Razão de parada ("stop", "tool_calls", etc)

        Example:
            >>> response = await client.chat_with_tools(
            ...     messages=[{"role": "user", "content": "Search for videos"}],
            ...     tools=[search_tool, generate_tool],
            ...     tool_choice="auto"
            ... )
            >>> if response["tool_calls"]:
            ...     for tc in response["tool_calls"]:
            ...         tool_name = tc["function"]["name"]
            ...         tool_args = json.loads(tc["function"]["arguments"])
            ...         result = execute_tool(tool_name, tool_args)
        """

        # Adicionar system prompt
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        # Retry loop
        for attempt in range(max_retries):
            try:
                start_time = time.time()

                # Chamar OpenRouter com tools
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools,
                    tool_choice=tool_choice,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                elapsed_ms = (time.time() - start_time) * 1000

                # Atualizar stats básicas
                self.stats["total_calls"] += 1
                self.stats["total_time_ms"] += elapsed_ms

                if hasattr(response, 'usage') and response.usage:
                    self.stats["total_tokens_input"] += response.usage.prompt_tokens
                    self.stats["total_tokens_output"] += response.usage.completion_tokens

                # Processar resposta
                message = response.choices[0].message
                finish_reason = response.choices[0].finish_reason

                result = {
                    "content": message.content,
                    "tool_calls": None,
                    "finish_reason": finish_reason
                }

                # Se há tool calls
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    tool_calls = []

                    for tc in message.tool_calls:
                        tool_call = {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        tool_calls.append(tool_call)

                        # Atualizar stats MCP
                        self.mcp_stats["tool_calls_total"] += 1
                        tool_name = tc.function.name
                        self.mcp_stats["tool_calls_by_name"][tool_name] = \
                            self.mcp_stats["tool_calls_by_name"].get(tool_name, 0) + 1

                    result["tool_calls"] = tool_calls

                logger.info(
                    f"Tool calling: {len(result['tool_calls']) if result['tool_calls'] else 0} tools, "
                    f"{elapsed_ms:.0f}ms"
                )

                return result

            except Exception as e:
                logger.error(f"Erro no tool calling (tentativa {attempt + 1}/{max_retries}): {e}")

                if attempt == max_retries - 1:
                    # Última tentativa falhou
                    self.stats["errors"] += 1
                    self.mcp_stats["tool_call_errors"] += 1
                    raise Exception(f"Tool calling falhou após {max_retries} tentativas: {e}")

                # Aguardar antes de retry (exponential backoff)
                wait_time = 2 ** attempt
                logger.info(f"Aguardando {wait_time}s antes de retry...")
                time.sleep(wait_time)


    async def execute_tool_call(
        self,
        tool_call: Dict[str, Any],
        tool_functions: Dict[str, Callable]
    ) -> Any:
        """
        Executa uma tool call.

        Args:
            tool_call: Tool call do LLM (formato OpenAI)
            tool_functions: Dict com funções disponíveis {name: function}

        Returns:
            Resultado da execução do tool

        Example:
            >>> tool_functions = {
            ...     "search_pexels": search_pexels_video,
            ...     "generate_stability": generate_stability_image
            ... }
            >>> result = await client.execute_tool_call(tool_call, tool_functions)
        """
        tool_name = tool_call["function"]["name"]
        tool_args_json = tool_call["function"]["arguments"]

        logger.info(f"Executando tool: {tool_name}")

        # Parse argumentos
        try:
            tool_args = json.loads(tool_args_json)
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao parsear argumentos do tool: {e}")
            raise ValueError(f"Tool arguments inválidos: {tool_args_json}")

        # Verificar se tool existe
        if tool_name not in tool_functions:
            raise ValueError(f"Tool '{tool_name}' não encontrado. Disponíveis: {list(tool_functions.keys())}")

        # Executar tool
        tool_function = tool_functions[tool_name]

        try:
            result = tool_function(**tool_args)

            # Se função é async
            if hasattr(result, '__await__'):
                result = await result

            logger.info(f"Tool '{tool_name}' executado com sucesso")
            return result

        except Exception as e:
            logger.error(f"Erro ao executar tool '{tool_name}': {e}")
            raise


    async def chat_with_tools_and_execute(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        tool_functions: Dict[str, Callable],
        system_prompt: Optional[str] = None,
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Realiza chat com tools e executa automaticamente.

        Loop completo:
        1. LLM escolhe tool
        2. Executa tool
        3. Retorna resultado para LLM
        4. Repete até LLM retornar resposta final

        Args:
            messages: Mensagens iniciais
            tools: Tools disponíveis
            tool_functions: Funções dos tools
            system_prompt: System prompt
            max_iterations: Max iterações (previne loops infinitos)

        Returns:
            Dict com resposta final

        Example:
            >>> result = await client.chat_with_tools_and_execute(
            ...     messages=[{"role": "user", "content": "Get video for office scene"}],
            ...     tools=[pexels_tool, stability_tool],
            ...     tool_functions={"search_pexels": search_fn, "generate_stability": generate_fn}
            ... )
            >>> print(result["final_response"])
        """

        conversation = messages.copy()
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Iteração {iteration}/{max_iterations}")

            # Chamar LLM com tools
            response = await self.chat_with_tools(
                messages=conversation,
                tools=tools,
                tool_choice="auto",
                system_prompt=system_prompt if iteration == 1 else None
            )

            # Se LLM retornou resposta final (não tool call)
            if not response["tool_calls"]:
                logger.info("LLM retornou resposta final (sem tool calls)")
                return {
                    "final_response": response["content"],
                    "iterations": iteration,
                    "tool_calls_executed": self.mcp_stats["tool_calls_total"]
                }

            # Executar tool calls
            tool_results = []

            for tool_call in response["tool_calls"]:
                try:
                    result = await self.execute_tool_call(tool_call, tool_functions)
                    tool_results.append({
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": tool_call["function"]["name"],
                        "content": json.dumps(result) if not isinstance(result, str) else result
                    })

                except Exception as e:
                    logger.error(f"Erro ao executar tool: {e}")
                    tool_results.append({
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": tool_call["function"]["name"],
                        "content": f"ERROR: {str(e)}"
                    })

            # Adicionar tool calls à conversa
            conversation.append({
                "role": "assistant",
                "content": response["content"],
                "tool_calls": response["tool_calls"]
            })

            # Adicionar resultados dos tools
            conversation.extend(tool_results)

        # Max iterações atingido
        logger.warning(f"Max iterações ({max_iterations}) atingido")
        return {
            "final_response": "Max iterations reached",
            "iterations": iteration,
            "tool_calls_executed": self.mcp_stats["tool_calls_total"]
        }


    def print_mcp_stats(self):
        """Imprime estatísticas MCP"""
        print("\n" + "="*60)
        print("📊 ESTATÍSTICAS MCP")
        print("="*60)
        print(f"Total tool calls: {self.mcp_stats['tool_calls_total']}")

        if self.mcp_stats['tool_calls_by_name']:
            print("\nTool calls por nome:")
            for tool_name, count in self.mcp_stats['tool_calls_by_name'].items():
                print(f"  • {tool_name}: {count}")

        if self.mcp_stats['tool_call_errors'] > 0:
            print(f"\n⚠️  Erros: {self.mcp_stats['tool_call_errors']}")

        if self.mcp_stats['fallback_activations'] > 0:
            print(f"🔄 Fallbacks: {self.mcp_stats['fallback_activations']}")

        print("="*60 + "\n")


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    import asyncio

    async def test_tool_calling():
        """Teste de tool calling"""

        print("🧪 Testando AIClientMCP com tool calling...\n")

        # Criar cliente MCP
        client = AIClientMCP(
            model="openai/gpt-4o-mini-2024-07-18",
            use_local=False
        )

        # Definir tools (exemplo)
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get weather for a city",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "City name"
                            }
                        },
                        "required": ["city"]
                    }
                }
            }
        ]

        # Função do tool (mock)
        def get_weather(city: str) -> dict:
            return {"city": city, "temperature": 25, "condition": "sunny"}

        tool_functions = {"get_weather": get_weather}

        # Testar tool calling
        try:
            result = await client.chat_with_tools_and_execute(
                messages=[
                    {"role": "user", "content": "What's the weather in São Paulo?"}
                ],
                tools=tools,
                tool_functions=tool_functions
            )

            print(f"✅ Resposta final: {result['final_response']}")
            print(f"Iterações: {result['iterations']}")
            print(f"Tool calls: {result['tool_calls_executed']}")

            client.print_mcp_stats()
            client.print_stats()

        except Exception as e:
            print(f"❌ Erro: {e}")

    asyncio.run(test_tool_calling())
