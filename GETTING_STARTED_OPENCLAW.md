# 🚀 Getting Started with OpenClaw

This guide will help you start using OpenClaw in 5 minutes!

## Prerequisites

- Python 3.11+
- OpenRouter API key (get one at https://openrouter.ai/)

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/Peugcam/OMA.AI.git
cd OMA.AI

# 2. Install dependencies
pip install -r requirements_openrouter.txt
pip install -r openclaw/requirements.txt

# 3. Configure API key
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

## Quick Start - Interactive Mode

```bash
# Start OpenClaw CLI
python openclaw/openclaw.py
```

You'll see:
```
🦀 OpenClaw - Open Source AI Coding Assistant
Registered agents: coder

Type 'help' for available commands or 'exit' to quit

openclaw>
```

### Try These Commands:

```bash
# Generate a function
openclaw> code create a function that validates email addresses

# Get help
openclaw> help

# List agents
openclaw> list

# Show statistics
openclaw> stats

# Exit
openclaw> exit
```

## Quick Start - Single Command

```bash
# Run a single command
python openclaw/openclaw.py code "create a REST API endpoint for user authentication"
```

## Quick Start - Python API

```python
# example.py
import asyncio
from openclaw.openclaw import OpenClaw

async def main():
    # Initialize
    claw = OpenClaw()

    # Get coder agent
    coder = claw.registry.get("coder")

    # Generate code
    result = await coder.run(task={
        "description": "Create a function to merge two sorted lists",
        "language": "python"
    })

    if result.success:
        print("Code:")
        print(result.result["code"])
        print("\nExplanation:")
        print(result.result["explanation"])

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:
```bash
python example.py
```

## Examples

See [`openclaw/examples/`](openclaw/examples/) for more examples:

- `simple_example.py` - Basic usage
- `advanced_example.py` - Multi-agent collaboration (coming soon)
- `memory_example.py` - Using persistent memory (coming soon)

## What's Next?

1. **Try the examples**: `cd openclaw/examples && python simple_example.py`
2. **Read the docs**: Check out [openclaw/README.md](openclaw/README.md)
3. **Customize agents**: Create your own agents (see Framework docs)
4. **Join the community**: Share your agents and use cases!

## Cost Optimization

OpenClaw uses OpenRouter, giving you access to 200+ models. Choose based on your needs:

| Use Case | Recommended Model | Cost/1M tokens |
|----------|------------------|----------------|
| **Quick coding** | Qwen 2.5 7B | $0.09 |
| **Complex logic** | GPT-4o | $2.50 |
| **Best quality** | Claude 3.5 Sonnet | $3.00 |
| **Local (free)** | Gemma 2 9B | Free (local) |

Configure in your agent:
```python
coder = CoderAgent(
    model="openrouter/qwen/qwen-2.5-7b-instruct",  # Cheap & fast
    # model="openrouter/anthropic/claude-3.5-sonnet",  # Best quality
    temperature=0.3
)
```

## Troubleshooting

### "OpenRouter API key required"
Make sure you set `OPENROUTER_API_KEY` in your `.env` file.

### "Module not found"
Make sure you installed both requirement files:
```bash
pip install -r requirements_openrouter.txt
pip install -r openclaw/requirements.txt
```

### Rate limits
OpenRouter has rate limits. If you hit them, wait a minute or upgrade your plan.

## Get Help

- **Issues**: https://github.com/Peugcam/OMA.AI/issues
- **Discussions**: https://github.com/Peugcam/OMA.AI/discussions
- **Documentation**: [openclaw/README.md](openclaw/README.md)

## What You Just Built

You now have:
- ✅ A working AI coding assistant (OpenClaw)
- ✅ Multi-agent framework (OMA.AI Framework)
- ✅ ReAct, Chain-of-Thought reasoning patterns
- ✅ Extensible agent system
- ✅ CLI interface
- ✅ Python API

**Next**: Add more agents (Debugger, Tester), create custom tools, build a web UI!

---

**Happy coding with OpenClaw! 🦀**
