---
title: OMA Video Generator
emoji: 🎬
colorFrom: purple
colorTo: blue
sdk: gradio
sdk_version: 4.44.1
app_file: app.py
pinned: false
license: mit
---

# 🎬 OMA.AI - Multi-Agent Video Creation Platform

> Enterprise-grade video automation with AI agents - **16-45x cheaper** than AWS/Azure/Google Cloud!

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## 🚀 What is OMA.AI?

OMA (Orquestrador Multi-Agente) is a **production-ready** multi-agent system that creates professional videos automatically using AI. Think AWS Bedrock + Azure AI + Vertex AI, but:

- ✅ **16-45x cheaper** ($2.41 vs $40-100 per 1000 requests)
- ✅ **No vendor lock-in** (works with 200+ models via OpenRouter)
- ✅ **Runs anywhere** (local, AWS, Azure, Google Cloud, Heroku, Railway...)
- ✅ **Enterprise features** (observability, state persistence, testing, guardrails)

## 💰 Cost Comparison

| Provider | Cost/1000 req | Models | Vendor Lock-in |
|----------|---------------|--------|----------------|
| **OMA.AI** | **$2.41** | **200+** | **No** ✅ |
| AWS Bedrock | $40 | ~15 | Yes 🔒 |
| Azure AI | $60 | ~10 | Yes 🔒 |
| Vertex AI | $100 | ~8 | Yes 🔒 |

**You save 16-45x!** 🎉

## 🎯 AI Models

**All via OpenRouter API:**
- **Supervisor:** Qwen 2.5 7B Instruct ($0.09/1M tokens) - Task planning
- **Script Agent:** Phi-3.5 Mini 128k ($0.10/1M) - Creative writing
- **Visual Agent:** Gemma 2 9B IT ($0.20/1M) - Visual description
- **Audio Agent:** Mistral 7B Instruct ($0.06/1M) - Audio planning
- **Editor Agent:** Llama 3.2 3B ($0.06/1M) - Video editing

**Cost per video:** ~$0.0007 (less than 1 cent!)

**Local Model (Optional):**
- Gemma 2 9B - Only useful local model for offline testing
- All production work via OpenRouter API

**Total: 200+ models available via OpenRouter!**

See [MODELS_REFERENCE.md](MODELS_REFERENCE.md) for detailed info.

## 🚀 Quick Start

```bash
# 1. Install
git clone https://github.com/Peugcam/OMA.AI.git
cd OMA.AI
pip install -r requirements_openrouter.txt

# 2. Configure
cp .env.example .env
# Add your OPENROUTER_API_KEY

# 3. Run Dashboard
python dashboard.py
```

Open http://localhost:7860 🎉

## 🔧 Code Quality & Development

OMA.AI uses **18+ professional quality tools** for code analysis:

```bash
# Setup all quality tools
npm run setup

# Run comprehensive quality checks
npm run check:all

# Auto-fix formatting issues
npm run check:all:fix
```

**Quality Tools Installed:**
- ✅ **Black** & **isort** - Auto-formatting
- ✅ **Flake8** (6 plugins) - Advanced linting
- ✅ **Pylint** (custom checkers) - Code quality
- ✅ **MyPy** - Type checking
- ✅ **jscpd** - Duplicate detection
- ✅ **Bandit** - Security analysis
- ✅ **Radon** - Complexity analysis
- ✅ **Vulture** - Dead code detection
- ✅ **Pre-commit hooks** - Automated checks

**Documentation:**
- [**Quick Reference**](QUICK_QUALITY_REFERENCE.md) - Fast commands
- [**Complete Guide**](QUALITY_TOOLS_GUIDE.md) - Detailed usage
- [**Tools Summary**](TOOLS_SUMMARY.md) - What's installed

## 📚 Documentation

- [Architecture Comparison](ARCHITECTURE_COMPARISON.md) - vs AWS/Azure/Vertex
- [Cost Analysis](COST_ANALYSIS_API_ONLY.md) - Detailed pricing
- [Code Analysis Guide](CODE_ANALYSIS_GUIDE.md) - Quality tools
- [Vendor Lock-in Explained](VENDOR_LOCK_IN_EXPLAINED.md) - Why OMA is different

## 📄 License

MIT License

---

**OMA.AI** - Enterprise AI without enterprise costs! 🚀
