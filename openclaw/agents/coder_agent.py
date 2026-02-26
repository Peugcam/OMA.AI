"""
💻 Coder Agent - Specialized in writing code

Capabilities:
- Implement features
- Refactor code
- Fix bugs
- Optimize performance
- Follow best practices
"""

from typing import Dict, Any, Optional
from framework.agents import BaseAgent, AgentResponse, AgentCapability
from core import AIClient
import json


class CoderAgent(BaseAgent):
    """
    Agent specialized in writing high-quality code.

    Uses Chain-of-Thought reasoning to:
    1. Understand requirements
    2. Plan implementation
    3. Write code
    4. Self-review
    """

    def __init__(
        self,
        model: str = "openrouter/qwen/qwen-2.5-7b-instruct",
        temperature: float = 0.3,
        **kwargs
    ):
        super().__init__(
            name="coder",
            description="Writes high-quality code following best practices",
            model=model,
            temperature=temperature,
            **kwargs
        )

        self.metadata.capabilities = [
            AgentCapability.CODING,
            AgentCapability.PLANNING
        ]

        self.llm = AIClient(model=model, temperature=temperature)

        self.system_prompt = """You are an expert software engineer with 10+ years of experience.

Your strengths:
- Clean, maintainable code
- Following SOLID principles
- Security best practices
- Performance optimization
- Comprehensive error handling
- Clear documentation

When writing code:
1. Think step-by-step
2. Consider edge cases
3. Add helpful comments
4. Use type hints (Python)
5. Handle errors gracefully
6. Write testable code"""

    async def execute(
        self,
        task: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Execute coding task.

        Args:
            task: {
                "description": "what to code",
                "language": "python|javascript|etc",
                "framework": "optional framework",
                "style": "functional|oop|etc"
            }
            context: Optional context (existing code, dependencies, etc.)

        Returns:
            AgentResponse with generated code
        """
        self.logger.info(f"💻 [Coder] Starting: {task.get('description')}")

        # Build prompt with Chain-of-Thought
        prompt = self._build_prompt(task, context)

        # Generate code
        response = await self.llm.chat(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=self.metadata.temperature,
            max_tokens=2000
        )

        # Parse response
        code, explanation = self._parse_response(response)

        if code:
            return AgentResponse(
                success=True,
                result={
                    "code": code,
                    "explanation": explanation,
                    "language": task.get("language", "python")
                },
                metadata={
                    "agent": "coder",
                    "task_type": "code_generation"
                }
            )
        else:
            return AgentResponse(
                success=False,
                result=None,
                error="Failed to generate code"
            )

    def _build_prompt(
        self,
        task: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Build Chain-of-Thought prompt"""
        description = task.get("description", "")
        language = task.get("language", "python")
        framework = task.get("framework", "")
        style = task.get("style", "")

        prompt = f"""Write code to: {description}

Language: {language}
{f"Framework: {framework}" if framework else ""}
{f"Style: {style}" if style else ""}

{f"CONTEXT:\n{json.dumps(context, indent=2)}" if context else ""}

Think step-by-step:

Step 1: Understanding
- What is the core requirement?
- What are the inputs/outputs?
- What edge cases exist?

Step 2: Planning
- What functions/classes are needed?
- What data structures to use?
- What error handling is needed?

Step 3: Implementation
- Write clean, readable code
- Add type hints and docstrings
- Handle errors gracefully
- Add helpful comments

Respond in this format:

## Explanation
[Brief explanation of your approach]

## Code
```{language}
[Your code here]
```

## Usage Example
```{language}
[Example of how to use the code]
```
"""
        return prompt

    def _parse_response(self, response: str) -> tuple[Optional[str], str]:
        """
        Parse LLM response to extract code and explanation.

        Returns:
            (code, explanation)
        """
        explanation = ""
        code = None

        # Extract explanation
        if "## Explanation" in response:
            start = response.index("## Explanation") + len("## Explanation")
            end = response.index("## Code") if "## Code" in response else len(response)
            explanation = response[start:end].strip()

        # Extract code block
        if "```" in response:
            # Find first code block
            start = response.index("```")
            # Skip language identifier (e.g., ```python)
            start = response.index("\n", start) + 1
            end = response.index("```", start)
            code = response[start:end].strip()

        return code, explanation

    async def refactor(
        self,
        code: str,
        goal: str = "improve readability and maintainability"
    ) -> AgentResponse:
        """
        Refactor existing code.

        Args:
            code: Code to refactor
            goal: Refactoring goal

        Returns:
            AgentResponse with refactored code
        """
        prompt = f"""Refactor this code to {goal}:

```
{code}
```

Provide:
1. Explanation of what you improved
2. Refactored code
3. List of specific changes made

Use the same format as before (## Explanation, ## Code, ## Changes)."""

        response = await self.llm.chat(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        refactored_code, explanation = self._parse_response(response)

        return AgentResponse(
            success=bool(refactored_code),
            result={
                "original": code,
                "refactored": refactored_code,
                "explanation": explanation
            }
        )

    async def explain_code(self, code: str) -> AgentResponse:
        """
        Explain what a piece of code does.

        Args:
            code: Code to explain

        Returns:
            AgentResponse with explanation
        """
        prompt = f"""Explain this code in detail:

```
{code}
```

Include:
1. High-level overview (what it does)
2. Step-by-step breakdown
3. Key concepts/patterns used
4. Potential improvements
5. Edge cases to consider"""

        response = await self.llm.chat(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )

        return AgentResponse(
            success=True,
            result={"explanation": response, "code": code}
        )
