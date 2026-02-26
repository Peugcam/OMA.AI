"""
🤖 OMA.AI Framework - Multi-Agent Orchestration Framework
==========================================================

A production-ready framework for building, orchestrating, and monitoring AI agent systems.

Core Components:
- BaseAgent: Abstract base class for all agents
- Orchestrator: Coordinates multiple agents to complete complex tasks
- Memory: Persistent memory system with vector database
- ToolRegistry: Extensible tool system for agents
- Monitor: Real-time monitoring and observability

Example:
    ```python
    from framework import Agent, Orchestrator, Tool

    # Define a custom agent
    class ResearchAgent(Agent):
        async def execute(self, task):
            # Your logic here
            return result

    # Create orchestrator
    orchestrator = Orchestrator(
        agents=[ResearchAgent(), WriterAgent()],
        pattern="sequential"
    )

    # Execute task
    result = await orchestrator.run("Write a blog post about AI")
    ```

"""

from .agents import BaseAgent, AgentRegistry
from .orchestrator import Orchestrator, ExecutionPattern
from .memory import Memory, MemoryType
from .tools import Tool, ToolRegistry
from .monitor import Monitor, MetricsCollector

__version__ = "1.0.0"
__all__ = [
    "BaseAgent",
    "AgentRegistry",
    "Orchestrator",
    "ExecutionPattern",
    "Memory",
    "MemoryType",
    "Tool",
    "ToolRegistry",
    "Monitor",
    "MetricsCollector",
]
