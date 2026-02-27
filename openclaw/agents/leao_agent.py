"""
🦁 Agente Leão - Assistente WhatsApp para OpenClaw

Número configurado: 5511956612953
"""

import os
from typing import Dict, Any, Optional
from framework.agents import BaseAgent, AgentResponse, AgentCapability
from core import AIClient
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LeaoAgent(BaseAgent):
    """
    Agente Leão - Assistente WhatsApp integrado com OpenClaw

    Número: 5511956612953
    """

    def __init__(
        self,
        model: str = "openrouter/qwen/qwen-2.5-7b-instruct",
        temperature: float = 0.7,
        **kwargs
    ):
        super().__init__(
            name="leao",
            description="🦁 Assistente WhatsApp (Agente Leão) - Número: 5511956612953",
            model=model,
            temperature=temperature,
            **kwargs
        )

        self.metadata.capabilities = [
            AgentCapability.CHAT,
            AgentCapability.PLANNING
        ]

        # WhatsApp config
        self.whatsapp_number = os.getenv("WHATSAPP_NUMBER", "5511956612953")
        self.evolution_url = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
        self.evolution_key = os.getenv("EVOLUTION_API_KEY")
        self.instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "leao")

        # AI client
        self.llm = AIClient(model=model, temperature=temperature)

        self.system_prompt = """Você é o Agente Leão 🦁, assistente virtual brasileiro via WhatsApp.

Características:
- Amigável e prestativo
- Respostas claras e objetivas
- Linguagem natural em português do Brasil
- Pode usar emojis quando apropriado

Você ajuda com:
- Responder perguntas
- Executar comandos
- Fornecer informações
- Tarefas automatizadas

Seja sempre útil, educado e eficiente!"""

    async def execute(
        self,
        task: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Executar tarefa

        Args:
            task: {
                "type": "send" | "reply" | "status",
                "to": "número destinatário",
                "message": "mensagem"
            }
        """
        task_type = task.get("type", "status")

        self.logger.info(f"🦁 [Leão] Executando: {task_type}")

        if task_type == "send":
            return await self._send_message(task)
        elif task_type == "reply":
            return await self._generate_reply(task, context)
        elif task_type == "status":
            return self._get_status()
        else:
            return AgentResponse(
                success=False,
                error=f"Tipo desconhecido: {task_type}"
            )

    async def _send_message(self, task: Dict[str, Any]) -> AgentResponse:
        """Enviar mensagem via WhatsApp"""
        to = task.get("to")
        message = task.get("message")

        if not to or not message:
            return AgentResponse(
                success=False,
                error="Parâmetros 'to' e 'message' obrigatórios"
            )

        if not self.evolution_key:
            return AgentResponse(
                success=False,
                error="Evolution API key não configurada. Configure EVOLUTION_API_KEY no .env"
            )

        try:
            url = f"{self.evolution_url}/message/sendText/{self.instance_name}"
            headers = {
                "Content-Type": "application/json",
                "apikey": self.evolution_key
            }

            payload = {
                "number": to,
                "text": message
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    result = await response.json()

                    if response.status == 200:
                        self.logger.info(f"✅ Mensagem enviada para {to}")
                        return AgentResponse(
                            success=True,
                            result={
                                "status": "sent",
                                "to": to,
                                "message": message,
                                "api_response": result
                            }
                        )
                    else:
                        return AgentResponse(
                            success=False,
                            error=f"API retornou {response.status}: {result}"
                        )

        except Exception as e:
            self.logger.error(f"❌ Erro ao enviar: {e}")
            return AgentResponse(
                success=False,
                error=f"Erro: {str(e)}"
            )

    async def _generate_reply(
        self,
        task: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> AgentResponse:
        """Gerar resposta inteligente para mensagem recebida"""
        message = task.get("message", "")
        from_number = task.get("from", "")

        if not message:
            return AgentResponse(
                success=False,
                error="Mensagem vazia"
            )

        self.logger.info(f"📨 Processando de {from_number}: {message}")

        prompt = f"""Mensagem de {from_number}:
"{message}"

{f"Contexto: {context}" if context else ""}

Gere uma resposta apropriada, útil e amigável."""

        try:
            response = await self.llm.chat(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.metadata.temperature,
                max_tokens=500
            )

            return AgentResponse(
                success=True,
                result={
                    "original_message": message,
                    "from": from_number,
                    "reply": response
                }
            )

        except Exception as e:
            self.logger.error(f"❌ Erro ao gerar resposta: {e}")
            return AgentResponse(
                success=False,
                error=f"Erro: {str(e)}"
            )

    def _get_status(self) -> AgentResponse:
        """Obter status do agente"""
        status = {
            "nome": "Agente Leão 🦁",
            "numero": self.whatsapp_number,
            "evolution_api": "✅ Configurada" if self.evolution_key else "❌ Não configurada",
            "modelo_ia": self.metadata.model,
            "instance": self.instance_name
        }

        return AgentResponse(
            success=True,
            result=status
        )
