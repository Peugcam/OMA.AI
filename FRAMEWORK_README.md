# 🤖 OMA.AI Framework - Multi-Agent Orchestration

> Production-ready framework for building AI agent systems - **Powers OpenClaw & OMA Video Generator**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## 🚀 What is OMA.AI Framework?

OMA.AI is a **production-ready multi-agent orchestration framework** that makes it easy to build sophisticated AI applications with multiple specialized agents working together.

Think of it as:
- **LangChain** but more opinionated and production-focused
- **AutoGPT** but with better architecture and extensibility
- **AWS Bedrock Multi-Agent** but open-source and model-agnostic

## ✨ Key Features

- 🧠 **Advanced Reasoning Patterns**: ReAct, Chain-of-Thought, Self-Reflection
- 🤝 **Multi-Agent Collaboration**: Agents work together seamlessly
- 🔧 **Extensible Tool System**: Easy-to-add custom tools
- 💾 **Persistent Memory**: Vector database for long-term context
- 📊 **Built-in Monitoring**: Track performance, costs, and success rates
- 🌐 **Model Agnostic**: Works with 200+ models via OpenRouter
- 💰 **Cost Optimized**: 16-45x cheaper than AWS/Azure/GCP alternatives

## 🎯 Use Cases

### 1. 🦀 OpenClaw - AI Coding Assistant
Open-source alternative to Claude Code.
- Multiple specialized agents (Coder, Debugger, Tester, Reviewer)
- CLI and Python API
- **Cost**: ~$0.50 per 1000 coding tasks

→ [Get Started with OpenClaw](GETTING_STARTED_OPENCLAW.md)

### 2. 🎬 OMA Video Generator
Automated video creation platform.
- Script writing, visual planning, audio production, video editing
- **Cost**: <$0.001 per video (100x cheaper than alternatives)

→ [Video Generator Docs](README.md)

### 3. 🔮 Your Custom Application
Build your own multi-agent system!

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│            Your Application                      │
│        (OpenClaw, Video Gen, etc.)               │
└───────────────────┬─────────────────────────────┘
                    │
┌───────────────────┴─────────────────────────────┐
│         OMA.AI Framework                         │
│  ┌──────────────┐  ┌──────────────┐            │
│  │   Agents     │  │ Orchestrator │            │
│  │  - ReAct     │  │  - Routing   │            │
│  │  - CoT       │  │  - Execution │            │
│  │  - Reflect   │  │  - Recovery  │            │
│  └──────────────┘  └──────────────┘            │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐            │
│  │   Memory     │  │    Tools     │            │
│  │  - Vector DB │  │  - Bash      │            │
│  │  - Cache     │  │  - File I/O  │            │
│  └──────────────┘  └──────────────┘            │
└───────────────────┬─────────────────────────────┘
                    │
        ┌───────────┼──────────┐
        │           │          │
    ┌───▼───┐  ┌───▼───┐  ┌──▼───┐
    │OpenAI │  │Claude │  │Local │
    │via OR │  │via OR │  │Models│
    └───────┘  └───────┘  └──────┘
```

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/Peugcam/OMA.AI.git
cd OMA.AI

# Install framework
pip install -r requirements_openrouter.txt

# Configure
cp .env.example .env
# Add your OPENROUTER_API_KEY
```

### Create Your First Agent

```python
from framework import BaseAgent, AgentResponse
from core import AIClient

class ResearchAgent(BaseAgent):
    """Agent that researches topics"""

    def __init__(self):
        super().__init__(
            name="researcher",
            description="Researches topics and summarizes findings",
            model="openrouter/qwen/qwen-2.5-7b-instruct",
            temperature=0.5
        )
        self.llm = AIClient(model=self.metadata.model)

    async def execute(self, task, context=None):
        """Research a topic"""
        topic = task.get("topic")

        prompt = f"Research this topic and provide a summary: {topic}"

        response = await self.llm.chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        return AgentResponse(
            success=True,
            result={"summary": response}
        )


# Use it
import asyncio

async def main():
    agent = ResearchAgent()

    result = await agent.run(task={
        "topic": "quantum computing applications"
    })

    print(result.result["summary"])

asyncio.run(main())
```

### Multi-Agent System

```python
from framework import AgentRegistry, Orchestrator

# Create agents
researcher = ResearchAgent()
writer = WriterAgent()
reviewer = ReviewerAgent()

# Register them
registry = AgentRegistry()
registry.register(researcher)
registry.register(writer)
registry.register(reviewer)

# Create orchestrator
orchestrator = Orchestrator(
    registry=registry,
    pattern="sequential"  # or "parallel", "hierarchical"
)

# Execute complex task
result = await orchestrator.execute(
    task="Write a blog post about quantum computing",
    workflow=[
        ("researcher", "Research quantum computing"),
        ("writer", "Write blog post from research"),
        ("reviewer", "Review and improve post")
    ]
)
```

## 🧠 Reasoning Patterns

### 1. ReAct (Reasoning + Acting)

```python
from framework.agents import ReActAgent

agent = ReActAgent(
    name="problem_solver",
    description="Solves problems step-by-step",
    tools=[WebSearchTool(), CalculatorTool()]
)

result = await agent.run(task={
    "description": "How many days until Christmas 2025?"
})

# Agent will:
# 1. Think about what information is needed
# 2. Use tools (date calculator)
# 3. Observe results
# 4. Provide final answer
```

### 2. Chain-of-Thought

```python
from framework.agents import ChainOfThoughtAgent

agent = ChainOfThoughtAgent(
    name="logical_reasoner",
    description="Breaks down complex problems"
)

result = await agent.run(task={
    "description": "Explain why the sky is blue"
})

# Agent will think step-by-step and explain reasoning
```

### 3. Self-Reflection

```python
from framework.agents import ReflectionAgent

agent = ReflectionAgent(
    name="perfectionist",
    description="Improves output through reflection",
    max_reflections=3
)

result = await agent.run(task={
    "description": "Write a professional email"
})

# Agent will:
# 1. Generate initial response
# 2. Reflect on quality
# 3. Improve based on reflection
# 4. Repeat until satisfied
```

## 🔧 Tools System

Create custom tools for your agents:

```python
from framework.tools import Tool, ToolParameter, ToolResult, ToolParameterType

class WeatherTool(Tool):
    """Get weather information"""

    def __init__(self):
        super().__init__(
            name="get_weather",
            description="Get current weather for a location",
            parameters=[
                ToolParameter(
                    name="location",
                    type=ToolParameterType.STRING,
                    description="City name",
                    required=True
                )
            ]
        )

    async def execute(self, location: str) -> ToolResult:
        # Call weather API
        weather_data = await fetch_weather(location)

        return ToolResult(
            success=True,
            output=weather_data
        )


# Give it to an agent
agent = ReActAgent(
    name="weather_assistant",
    tools=[WeatherTool()]
)
```

## 💾 Memory System

```python
from framework import Memory, MemoryType

# Create memory
memory = Memory(
    type=MemoryType.VECTOR,
    provider="chromadb",  # or "pinecone", "weaviate"
)

# Create agent with memory
agent = ResearchAgent(memory=memory)

# Agent will automatically:
# - Store important information
# - Retrieve relevant context
# - Remember across sessions
```

## 📊 Monitoring

```python
# Get agent stats
stats = agent.get_stats()
print(f"Success rate: {stats['success_rate']:.1%}")
print(f"Total executions: {stats['total_executions']}")

# Get registry stats
registry_stats = registry.get_stats()
print(f"Total agents: {registry_stats['total_agents']}")
```

## 💰 Cost Comparison

| Solution | Cost/1M tokens | Vendor Lock-in | Models Available |
|----------|---------------|----------------|------------------|
| **OMA.AI Framework** | **$0.06 - $3** | **No** ✅ | **200+** |
| AWS Bedrock | $3 - $15 | Yes 🔒 | ~15 |
| Azure AI | $3 - $20 | Yes 🔒 | ~10 |
| Vertex AI | $3 - $30 | Yes 🔒 | ~8 |

**Save 10-100x on costs!**

## 📚 Examples & Documentation

- [OpenClaw (AI Coding Assistant)](openclaw/README.md)
- [Video Generator](README.md)
- [Framework API Docs](docs/API.md) (coming soon)
- [Creating Custom Agents](docs/CUSTOM_AGENTS.md) (coming soon)

## 🤝 Contributing

We welcome contributions!

**Areas we need help:**
- More reasoning patterns (Tree-of-Thoughts, Self-Ask, etc.)
- Additional tools (Kubernetes, Terraform, Slack, etc.)
- More agent templates
- Documentation improvements
- Bug fixes

See [CONTRIBUTING.md](CONTRIBUTING.md) (coming soon)

## 📄 License

MIT License - see [LICENSE](LICENSE)

## 🙏 Acknowledgments

Built with:
- [LangChain](https://langchain.com/) - LLM framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent graphs
- [OpenRouter](https://openrouter.ai/) - LLM API aggregator
- [ChromaDB](https://www.trychroma.com/) - Vector database

Inspired by:
- AWS Bedrock Multi-Agent Collaboration
- Azure AI Multi-Agent Orchestrator
- Google Vertex AI Agent Builder
- AutoGPT architecture

## 🌟 Projects Using OMA.AI

- **OpenClaw** - AI Coding Assistant
- **OMA Video Generator** - Automated video creation
- Your project here? Submit a PR!

---

**OMA.AI Framework** - Build powerful AI agents in minutes, not months! 🚀

**Ready to build?**
- [Try OpenClaw](GETTING_STARTED_OPENCLAW.md) - AI coding in 5 minutes
- [Build Custom Agents](docs/QUICKSTART.md) - Your first agent
- [Join Discord](#) - Community support
