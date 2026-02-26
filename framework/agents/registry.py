"""
📋 Agent Registry - Central registry for discovering and managing agents
"""

from typing import Dict, List, Optional, Type
from .base import BaseAgent, AgentCapability
import logging


class AgentRegistry:
    """
    Central registry for managing agents.

    Features:
    - Register/unregister agents
    - Discover agents by capability
    - Get agent by name
    - List all agents
    """

    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        self._agent_classes: Dict[str, Type[BaseAgent]] = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    def register(self, agent: BaseAgent) -> None:
        """
        Register an agent instance.

        Args:
            agent: Agent instance to register
        """
        name = agent.metadata.name
        if name in self._agents:
            self.logger.warning(f"Agent '{name}' already registered, overwriting")

        self._agents[name] = agent
        self.logger.info(f"✅ Registered agent: {name}")

    def register_class(self, name: str, agent_class: Type[BaseAgent]) -> None:
        """
        Register an agent class for lazy instantiation.

        Args:
            name: Name for the agent class
            agent_class: Agent class
        """
        self._agent_classes[name] = agent_class
        self.logger.info(f"✅ Registered agent class: {name}")

    def unregister(self, name: str) -> None:
        """
        Unregister an agent.

        Args:
            name: Agent name
        """
        if name in self._agents:
            del self._agents[name]
            self.logger.info(f"🗑️ Unregistered agent: {name}")
        else:
            self.logger.warning(f"Agent '{name}' not found")

    def get(self, name: str) -> Optional[BaseAgent]:
        """
        Get an agent by name.

        Args:
            name: Agent name

        Returns:
            Agent instance or None
        """
        return self._agents.get(name)

    def get_or_create(self, name: str, **kwargs) -> Optional[BaseAgent]:
        """
        Get agent or create from registered class.

        Args:
            name: Agent name
            **kwargs: Arguments for agent creation

        Returns:
            Agent instance or None
        """
        # Try to get existing
        agent = self.get(name)
        if agent:
            return agent

        # Try to create from class
        agent_class = self._agent_classes.get(name)
        if agent_class:
            agent = agent_class(**kwargs)
            self.register(agent)
            return agent

        self.logger.warning(f"Agent or agent class '{name}' not found")
        return None

    def list_agents(self) -> List[str]:
        """
        List all registered agent names.

        Returns:
            List of agent names
        """
        return list(self._agents.keys())

    def find_by_capability(self, capability: AgentCapability) -> List[BaseAgent]:
        """
        Find agents with a specific capability.

        Args:
            capability: Capability to search for

        Returns:
            List of agents with that capability
        """
        return [
            agent for agent in self._agents.values()
            if capability in agent.metadata.capabilities
        ]

    def get_stats(self) -> Dict[str, any]:
        """Get registry statistics"""
        return {
            "total_agents": len(self._agents),
            "total_agent_classes": len(self._agent_classes),
            "agents": [
                {
                    "name": agent.metadata.name,
                    "capabilities": [c.value for c in agent.metadata.capabilities],
                    "stats": agent.get_stats()
                }
                for agent in self._agents.values()
            ]
        }

    def clear(self):
        """Clear all registered agents"""
        self._agents.clear()
        self._agent_classes.clear()
        self.logger.info("🗑️ Cleared all agents from registry")

    def __len__(self) -> int:
        return len(self._agents)

    def __contains__(self, name: str) -> bool:
        return name in self._agents

    def __repr__(self) -> str:
        return f"<AgentRegistry: {len(self._agents)} agents>"
