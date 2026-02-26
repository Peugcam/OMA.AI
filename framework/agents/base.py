"""
🤖 Base Agent - Abstract base class for all agents

Inspired by:
- LangChain Agent Protocol
- AutoGPT Agent Architecture
- AWS Bedrock Agent Structure
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import asyncio
from datetime import datetime


class AgentCapability(Enum):
    """Capabilities that an agent can have"""
    RESEARCH = "research"
    WRITING = "writing"
    CODING = "coding"
    ANALYSIS = "analysis"
    PLANNING = "planning"
    EXECUTION = "execution"
    COMMUNICATION = "communication"
    CREATIVITY = "creativity"


@dataclass
class AgentMetadata:
    """Metadata about an agent"""
    name: str
    description: str
    version: str = "1.0.0"
    capabilities: List[AgentCapability] = field(default_factory=list)
    model: Optional[str] = None
    temperature: float = 0.7
    max_retries: int = 3
    timeout_seconds: int = 300
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AgentResponse:
    """Response from an agent execution"""
    success: bool
    result: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    execution_time: float = 0.0
    tokens_used: int = 0
    cost: float = 0.0


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the framework.

    Agents are autonomous entities that can:
    - Execute tasks independently
    - Use tools to accomplish goals
    - Store and retrieve memories
    - Communicate with other agents
    - Learn from feedback

    Subclass this to create custom agents.
    """

    def __init__(
        self,
        name: str,
        description: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_retries: int = 3,
        tools: Optional[List[Any]] = None,
        memory: Optional[Any] = None,
        enable_monitoring: bool = True
    ):
        """
        Initialize the base agent.

        Args:
            name: Unique name for the agent
            description: Description of what the agent does
            model: LLM model to use (if applicable)
            temperature: Temperature for LLM generation
            max_retries: Max retries on failure
            tools: List of tools the agent can use
            memory: Memory system for the agent
            enable_monitoring: Enable metrics collection
        """
        self.metadata = AgentMetadata(
            name=name,
            description=description,
            model=model,
            temperature=temperature,
            max_retries=max_retries
        )

        self.tools = tools or []
        self.memory = memory
        self.enable_monitoring = enable_monitoring

        self.logger = logging.getLogger(f"Agent.{name}")
        self._execution_count = 0
        self._success_count = 0
        self._failure_count = 0

    @abstractmethod
    async def execute(self, task: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Execute a task. Must be implemented by subclasses.

        Args:
            task: Task definition with parameters
            context: Optional context from previous agents

        Returns:
            AgentResponse with results
        """
        pass

    async def run(self, task: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Run the agent with error handling and monitoring.

        Args:
            task: Task to execute
            context: Optional context

        Returns:
            AgentResponse
        """
        self._execution_count += 1
        start_time = datetime.now()

        try:
            self.logger.info(f"🚀 Starting execution: {task.get('description', 'No description')}")

            # Execute with retries
            for attempt in range(self.metadata.max_retries):
                try:
                    response = await asyncio.wait_for(
                        self.execute(task, context),
                        timeout=self.metadata.timeout_seconds
                    )

                    if response.success:
                        self._success_count += 1
                        execution_time = (datetime.now() - start_time).total_seconds()
                        response.execution_time = execution_time

                        self.logger.info(f"✅ Success in {execution_time:.2f}s")
                        return response

                    self.logger.warning(f"⚠️ Attempt {attempt + 1} failed: {response.error}")

                except asyncio.TimeoutError:
                    self.logger.error(f"⏱️ Timeout on attempt {attempt + 1}")

                except Exception as e:
                    self.logger.error(f"❌ Error on attempt {attempt + 1}: {e}")

                if attempt < self.metadata.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff

            # All attempts failed
            self._failure_count += 1
            execution_time = (datetime.now() - start_time).total_seconds()

            return AgentResponse(
                success=False,
                result=None,
                error=f"Failed after {self.metadata.max_retries} attempts",
                execution_time=execution_time
            )

        except Exception as e:
            self._failure_count += 1
            execution_time = (datetime.now() - start_time).total_seconds()

            self.logger.error(f"❌ Fatal error: {e}")
            return AgentResponse(
                success=False,
                result=None,
                error=str(e),
                execution_time=execution_time
            )

    def get_stats(self) -> Dict[str, Any]:
        """Get agent execution statistics"""
        return {
            "name": self.metadata.name,
            "total_executions": self._execution_count,
            "successes": self._success_count,
            "failures": self._failure_count,
            "success_rate": self._success_count / max(self._execution_count, 1),
        }

    def reset_stats(self):
        """Reset execution statistics"""
        self._execution_count = 0
        self._success_count = 0
        self._failure_count = 0

    async def think(self, prompt: str) -> str:
        """
        Use LLM to think about a problem (helper method).

        Args:
            prompt: Thinking prompt

        Returns:
            LLM response
        """
        # To be implemented by subclasses that use LLMs
        raise NotImplementedError("This agent does not support thinking")

    async def use_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Use a tool by name.

        Args:
            tool_name: Name of the tool
            **kwargs: Tool arguments

        Returns:
            Tool result
        """
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")

        self.logger.info(f"🔧 Using tool: {tool_name}")
        return await tool.execute(**kwargs)

    async def remember(self, key: str, value: Any):
        """Store something in memory"""
        if not self.memory:
            self.logger.warning("Memory not configured for this agent")
            return

        await self.memory.store(key, value, agent_name=self.metadata.name)

    async def recall(self, query: str) -> List[Any]:
        """Retrieve from memory"""
        if not self.memory:
            self.logger.warning("Memory not configured for this agent")
            return []

        return await self.memory.search(query, agent_name=self.metadata.name)

    def __repr__(self) -> str:
        return f"<Agent: {self.metadata.name} ({self.metadata.description})>"
