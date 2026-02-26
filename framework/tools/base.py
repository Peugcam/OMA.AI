"""
🔧 Base Tool - Abstract base class for all tools
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging


class ToolParameterType(Enum):
    """Types of tool parameters"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


@dataclass
class ToolParameter:
    """Definition of a tool parameter"""
    name: str
    type: ToolParameterType
    description: str
    required: bool = True
    default: Optional[Any] = None


@dataclass
class ToolResult:
    """Result from tool execution"""
    success: bool
    output: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class Tool(ABC):
    """
    Abstract base class for tools that agents can use.

    Tools are functions/capabilities that agents can invoke to:
    - Search the web
    - Execute code
    - Read/write files
    - Call APIs
    - Perform calculations
    - etc.
    """

    def __init__(
        self,
        name: str,
        description: str,
        parameters: Optional[List[ToolParameter]] = None
    ):
        """
        Initialize the tool.

        Args:
            name: Unique name for the tool
            description: What the tool does
            parameters: List of parameters the tool accepts
        """
        self.name = name
        self.description = description
        self.parameters = parameters or []
        self.logger = logging.getLogger(f"Tool.{name}")
        self._execution_count = 0

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool. Must be implemented by subclasses.

        Args:
            **kwargs: Tool parameters

        Returns:
            ToolResult with output
        """
        pass

    async def run(self, **kwargs) -> ToolResult:
        """
        Run the tool with validation.

        Args:
            **kwargs: Tool parameters

        Returns:
            ToolResult
        """
        self._execution_count += 1

        try:
            # Validate parameters
            validation_error = self._validate_parameters(kwargs)
            if validation_error:
                return ToolResult(
                    success=False,
                    output=None,
                    error=validation_error
                )

            # Execute
            self.logger.info(f"🔧 Executing tool: {self.name}")
            result = await self.execute(**kwargs)
            self.logger.info(f"✅ Tool completed: {self.name}")
            return result

        except Exception as e:
            self.logger.error(f"❌ Tool error: {e}")
            return ToolResult(
                success=False,
                output=None,
                error=str(e)
            )

    def _validate_parameters(self, kwargs: Dict[str, Any]) -> Optional[str]:
        """Validate provided parameters"""
        # Check required parameters
        required = [p.name for p in self.parameters if p.required]
        missing = [name for name in required if name not in kwargs]

        if missing:
            return f"Missing required parameters: {', '.join(missing)}"

        # Type validation (basic)
        for param in self.parameters:
            if param.name in kwargs:
                value = kwargs[param.name]

                if param.type == ToolParameterType.STRING and not isinstance(value, str):
                    return f"Parameter '{param.name}' must be a string"
                elif param.type == ToolParameterType.INTEGER and not isinstance(value, int):
                    return f"Parameter '{param.name}' must be an integer"
                elif param.type == ToolParameterType.BOOLEAN and not isinstance(value, bool):
                    return f"Parameter '{param.name}' must be a boolean"

        return None

    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema in OpenAI function calling format"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    p.name: {
                        "type": p.type.value,
                        "description": p.description
                    }
                    for p in self.parameters
                },
                "required": [p.name for p in self.parameters if p.required]
            }
        }

    def __repr__(self) -> str:
        return f"<Tool: {self.name}>"
