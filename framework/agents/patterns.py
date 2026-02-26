"""
🧠 Agent Reasoning Patterns - ReAct, Chain-of-Thought, Reflection

Implementations of advanced reasoning patterns for agents.
"""

from typing import Dict, List, Optional, Any
import json
import re
from .base import BaseAgent, AgentResponse
from core import AIClient


class ReActAgent(BaseAgent):
    """
    Agent that uses ReAct pattern (Reasoning + Acting).

    Pattern:
    1. Thought: Think about what to do next
    2. Action: Execute a tool/action
    3. Observation: Observe the result
    4. Repeat until task is complete
    5. Answer: Final response

    Reference: https://arxiv.org/abs/2210.03629
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = AIClient(
            model=self.metadata.model or "openrouter/qwen/qwen-2.5-7b-instruct",
            temperature=self.metadata.temperature
        )

    async def execute(self, task: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Execute task using ReAct pattern.

        Args:
            task: Task with 'description' and optional 'parameters'
            context: Optional context from previous steps

        Returns:
            AgentResponse with result
        """
        self.logger.info(f"🧠 [ReAct] Starting: {task.get('description')}")

        # Build tools description
        tools_desc = self._build_tools_description()

        # Create ReAct prompt
        prompt = f"""You are an AI agent using the ReAct pattern (Reasoning + Acting).

TASK: {task.get('description')}

{f"CONTEXT: {json.dumps(context, indent=2)}" if context else ""}

AVAILABLE TOOLS:
{tools_desc}

INSTRUCTIONS:
Use this exact format:

Thought: [your reasoning about what to do next]
Action: [tool_name(arguments)]
Observation: [wait for result]

... (repeat Thought-Action-Observation as needed)

Answer: [final answer when task is complete]

IMPORTANT:
- Think step-by-step
- Use tools to gather information
- Make 2-5 iterations before answering
- Be concise but thorough

Start with Thought:"""

        # ReAct loop
        messages = [{"role": "user", "content": prompt}]
        max_iterations = 10
        result_data = None

        for iteration in range(max_iterations):
            self.logger.info(f"🔄 [ReAct] Iteration {iteration + 1}/{max_iterations}")

            # Get LLM response
            response = await self.llm.chat(messages=messages, temperature=0.3)

            # Parse response
            if "Thought:" in response:
                thought = self._extract_section(response, "Thought:")
                self.logger.info(f"💭 Thought: {thought[:100]}...")

            if "Action:" in response:
                action_str = self._extract_section(response, "Action:")
                self.logger.info(f"⚡ Action: {action_str}")

                # Execute action
                try:
                    observation = await self._execute_action(action_str)
                    self.logger.info(f"👁️ Observation: {str(observation)[:100]}...")

                    # Add to conversation
                    messages.append({"role": "assistant", "content": response})
                    messages.append({
                        "role": "user",
                        "content": f"Observation: {observation}\n\nContinue with Thought: or finalize with Answer:"
                    })
                    continue

                except Exception as e:
                    observation = f"Error: {str(e)}"
                    self.logger.error(f"❌ Action failed: {e}")
                    messages.append({"role": "assistant", "content": response})
                    messages.append({
                        "role": "user",
                        "content": f"Observation: {observation}\n\nTry a different approach with Thought:"
                    })
                    continue

            if "Answer:" in response:
                answer = self._extract_section(response, "Answer:")
                self.logger.info(f"✅ [ReAct] Answer: {answer[:100]}...")

                return AgentResponse(
                    success=True,
                    result={"answer": answer, "iterations": iteration + 1},
                    metadata={"pattern": "react", "iterations": iteration + 1}
                )

            # If no clear pattern, prompt for continuation
            if "Thought:" not in response and "Action:" not in response:
                messages.append({"role": "assistant", "content": response})
                messages.append({
                    "role": "user",
                    "content": "Please continue with Thought: or Answer:"
                })

        # Max iterations reached
        self.logger.warning("⚠️ [ReAct] Max iterations reached without Answer")
        return AgentResponse(
            success=False,
            result=None,
            error="ReAct loop did not converge"
        )

    def _build_tools_description(self) -> str:
        """Build description of available tools"""
        if not self.tools:
            return "No tools available"

        descriptions = []
        for tool in self.tools:
            descriptions.append(f"- {tool.name}: {tool.description}")

        return "\n".join(descriptions)

    def _extract_section(self, text: str, section: str) -> str:
        """Extract a section from ReAct response"""
        if section not in text:
            return ""

        start = text.index(section) + len(section)
        end_markers = ["Thought:", "Action:", "Observation:", "Answer:"]
        end = len(text)

        for marker in end_markers:
            if marker == section:
                continue
            if marker in text[start:]:
                potential_end = start + text[start:].index(marker)
                if potential_end < end:
                    end = potential_end

        return text[start:end].strip()

    async def _execute_action(self, action_str: str) -> Any:
        """Parse and execute an action"""
        # Parse action string like "tool_name(arg1, arg2)"
        match = re.match(r'(\w+)\((.*)\)', action_str.strip())
        if not match:
            raise ValueError(f"Invalid action format: {action_str}")

        tool_name = match.group(1)
        args_str = match.group(2)

        # Find tool
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")

        # Parse arguments (simple parsing, can be improved)
        if args_str:
            # Try to parse as JSON for structured args
            try:
                args = json.loads(f"{{{args_str}}}")
                return await tool.execute(**args)
            except:
                # Fallback to positional args
                args = [arg.strip().strip('"\'') for arg in args_str.split(',')]
                return await tool.execute(*args)
        else:
            return await tool.execute()


class ChainOfThoughtAgent(BaseAgent):
    """
    Agent that uses Chain-of-Thought reasoning.

    Breaks down complex problems into step-by-step reasoning.

    Reference: https://arxiv.org/abs/2201.11903
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = AIClient(
            model=self.metadata.model or "openrouter/qwen/qwen-2.5-7b-instruct",
            temperature=self.metadata.temperature
        )

    async def execute(self, task: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Execute task using Chain-of-Thought reasoning"""
        self.logger.info(f"🧠 [CoT] Starting: {task.get('description')}")

        prompt = f"""Think step-by-step to solve this task.

TASK: {task.get('description')}

{f"CONTEXT: {json.dumps(context, indent=2)}" if context else ""}

Please think through this step-by-step:
1. Understand what is being asked
2. Break down into smaller steps
3. Solve each step
4. Combine into final answer

Format your response as:

Step 1: [reasoning]
Step 2: [reasoning]
...
Final Answer: [your answer]
"""

        response = await self.llm.chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.metadata.temperature
        )

        # Extract final answer
        if "Final Answer:" in response:
            answer_start = response.index("Final Answer:") + len("Final Answer:")
            answer = response[answer_start:].strip()

            return AgentResponse(
                success=True,
                result={"answer": answer, "reasoning": response},
                metadata={"pattern": "chain_of_thought"}
            )
        else:
            return AgentResponse(
                success=False,
                result=None,
                error="Could not extract final answer from Chain-of-Thought reasoning"
            )


class ReflectionAgent(BaseAgent):
    """
    Agent that reflects on its own output and improves it.

    Pattern:
    1. Generate initial response
    2. Reflect on quality
    3. Identify improvements
    4. Generate improved response

    Reference: https://arxiv.org/abs/2303.11366
    """

    def __init__(self, *args, max_reflections: int = 3, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_reflections = max_reflections
        self.llm = AIClient(
            model=self.metadata.model or "openrouter/qwen/qwen-2.5-7b-instruct",
            temperature=self.metadata.temperature
        )

    async def execute(self, task: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Execute task with reflection"""
        self.logger.info(f"🧠 [Reflection] Starting: {task.get('description')}")

        current_output = ""
        reflections = []

        for reflection_idx in range(self.max_reflections):
            self.logger.info(f"🔄 Reflection iteration {reflection_idx + 1}/{self.max_reflections}")

            # Generate or improve output
            if reflection_idx == 0:
                # Initial generation
                prompt = f"""Complete this task:

TASK: {task.get('description')}

{f"CONTEXT: {json.dumps(context, indent=2)}" if context else ""}

Provide your best response:"""
            else:
                # Improve based on reflection
                prompt = f"""Your previous response:
{current_output}

Reflection on what could be improved:
{reflections[-1]}

Please provide an improved response:"""

            current_output = await self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=self.metadata.temperature
            )

            # Reflect on output (except on last iteration)
            if reflection_idx < self.max_reflections - 1:
                reflection_prompt = f"""Reflect on this response:

{current_output}

TASK was: {task.get('description')}

What could be improved? Consider:
- Accuracy
- Completeness
- Clarity
- Relevance

Be specific and concise (2-3 sentences):"""

                reflection = await self.llm.chat(
                    messages=[{"role": "user", "content": reflection_prompt}],
                    temperature=0.4
                )

                reflections.append(reflection)
                self.logger.info(f"💭 Reflection: {reflection[:100]}...")

                # Check if reflection indicates no improvements needed
                if "no improvement" in reflection.lower() or "looks good" in reflection.lower():
                    self.logger.info("✅ Reflection indicates output is satisfactory")
                    break

        return AgentResponse(
            success=True,
            result={"answer": current_output, "reflections": reflections},
            metadata={
                "pattern": "reflection",
                "num_reflections": len(reflections)
            }
        )
