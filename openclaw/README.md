# 🦀 OpenClaw - Open Source AI Coding Assistant

> The open-source alternative to Claude Code, powered by OMA.AI Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## 🚀 What is OpenClaw?

OpenClaw is an **open-source AI coding assistant** inspired by Claude Code, built on top of the OMA.AI multi-agent framework. It uses multiple specialized AI agents to help you code faster and smarter.

### Key Features

- 🤖 **Multi-Agent System**: Specialized agents for coding, debugging, testing, and documentation
- 🧠 **Advanced Reasoning**: Uses ReAct, Chain-of-Thought, and Reflection patterns
- 🔧 **Extensible Tools**: Bash, file operations, git, code analysis, and more
- 💾 **Persistent Memory**: Remembers context across sessions using vector database
- 🎯 **Cost Effective**: Uses OpenRouter API - 20x cheaper than Claude Code's API costs
- 🌐 **200+ Models**: Access to any LLM via OpenRouter (GPT-4, Claude, Gemini, Llama, etc.)
- 📊 **Real-time Monitoring**: Web dashboard to visualize agent execution
- 🐳 **Docker Ready**: Easy deployment with Docker Compose

## 🎯 Agents

OpenClaw uses specialized agents for different tasks:

| Agent | Role | Model | Use Case |
|-------|------|-------|----------|
| **CoderAgent** | Write code | GPT-4o / Qwen 2.5 | Implement features, refactor code |
| **DebuggerAgent** | Fix bugs | Claude 3.5 Sonnet | Analyze errors, suggest fixes |
| **TesterAgent** | Write tests | DeepSeek Coder | Generate unit/integration tests |
| **ReviewerAgent** | Code review | Claude 3.5 Sonnet | Review PRs, suggest improvements |
| **DocAgent** | Documentation | Gemini Pro | Write docs, comments, READMEs |
| **ArchitectAgent** | System design | GPT-4 | Design architecture, patterns |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│         OpenClaw CLI / Web UI                │
└────────────────┬────────────────────────────┘
                 │
┌────────────────┴────────────────────────────┐
│         Orchestrator (Coordinator)           │
│  - Task decomposition                        │
│  - Agent routing                             │
│  - Result synthesis                          │
└────────────────┬────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼───┐   ┌───▼───┐   ┌───▼───┐
│ Coder │   │Debug  │   │Tester │  ... (6 agents)
└───┬───┘   └───┬───┘   └───┬───┘
    │           │           │
    └───────────┼───────────┘
                │
    ┌───────────┼───────────┐
    │           │           │
┌───▼────┐  ┌──▼──┐   ┌───▼────┐
│ Tools  │  │Memory│   │Monitor │
└────────┘  └─────┘   └────────┘
```

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/Peugcam/OMA.AI.git
cd OMA.AI/openclaw

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

### Basic Usage

```bash
# Start OpenClaw CLI
python openclaw.py

# Example commands
> help                    # Show all commands
> code "add login feature"  # Generate code
> debug "NullPointerException in auth.py:42"  # Debug error
> test "auth module"      # Generate tests
> review "pull-request.diff"  # Review code
> docs "create README for this project"  # Generate docs
```

### Python API

```python
from openclaw import OpenClaw, Task

# Initialize OpenClaw
claw = OpenClaw(
    api_key="your-openrouter-key",
    enable_memory=True,
    enable_monitoring=True
)

# Execute a coding task
result = await claw.execute(Task(
    type="code",
    description="Create a FastAPI endpoint for user authentication",
    context={
        "framework": "FastAPI",
        "auth_method": "JWT",
        "database": "PostgreSQL"
    }
))

print(result.code)
print(result.explanation)
```

## 🔧 Tools Available

OpenClaw agents can use these tools:

- **BashTool**: Execute shell commands
- **FileReadTool**: Read files from filesystem
- **FileWriteTool**: Create/edit files
- **GitTool**: Git operations (commit, push, pull, etc.)
- **CodeAnalysisTool**: Analyze code quality, complexity
- **WebSearchTool**: Search the web for solutions
- **APICallTool**: Call external APIs
- **DockerTool**: Docker operations

## 💰 Cost Comparison

| Provider | Cost/1M tokens | OpenClaw Advantage |
|----------|----------------|-------------------|
| **OpenClaw (OpenRouter)** | **$0.10 - $2** | **Baseline** |
| Claude Code (API) | $3 - $15 | **3-15x more expensive** |
| GitHub Copilot | $10/month | Limited model choice |
| Cursor | $20/month | Closed source |

**Example: Generate 1000 files (~1M tokens)**
- OpenClaw: $0.50 - $2.00
- Claude Code API: $5 - $15
- **Savings: 75-90%**

## 🌟 Advanced Features

### 1. Memory System

OpenClaw remembers context across sessions:

```python
# Agents automatically remember:
# - Previous conversations
# - Code you've written
# - Bugs you've fixed
# - Patterns you use

# Example
> code "use the same auth pattern as yesterday"
# Agent recalls your JWT implementation from yesterday
```

### 2. Collaborative Agents

Agents work together on complex tasks:

```python
# Example: Full feature implementation
> feature "add payment processing with Stripe"

# Orchestrator coordinates:
# 1. ArchitectAgent: Design the payment flow
# 2. CoderAgent: Implement Stripe integration
# 3. TesterAgent: Write tests
# 4. ReviewerAgent: Review code
# 5. DocAgent: Document the API
```

### 3. Custom Agents

Extend OpenClaw with your own agents:

```python
from openclaw import BaseAgent, AgentCapability

class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="my_agent",
            description="Does something amazing",
            capabilities=[AgentCapability.CUSTOM]
        )

    async def execute(self, task, context):
        # Your logic here
        return AgentResponse(success=True, result=data)

# Register it
claw.register_agent(CustomAgent())
```

## 📊 Monitoring Dashboard

Access the web dashboard at `http://localhost:8000`

Features:
- Real-time agent execution visualization
- Token usage and cost tracking
- Success/failure rates
- Memory usage stats
- Agent collaboration graph

## 🐳 Docker Deployment

```bash
# Run with Docker Compose
docker-compose up -d

# Access CLI
docker exec -it openclaw bash
python openclaw.py

# Access Web UI
open http://localhost:8000
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md)

Areas we need help:
- New agents (DevOps, Security, Data Science)
- More tools (Kubernetes, Terraform, etc.)
- UI improvements
- Documentation
- Bug fixes

## 📄 License

MIT License - see [LICENSE](LICENSE)

## 🙏 Acknowledgments

Built with:
- [OMA.AI Framework](../) - Multi-agent orchestration
- [LangChain](https://langchain.com/) - LLM framework
- [OpenRouter](https://openrouter.ai/) - LLM API aggregator
- Inspired by [Claude Code](https://claude.com/code)

## 🌟 Star History

If you find OpenClaw useful, please star the repo!

---

**OpenClaw** - Open Source AI Coding, Powered by Community 🦀
