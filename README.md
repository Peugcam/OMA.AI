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
- Script Agent: GPT-4o-mini
- Visual Agent: GPT-4o-mini
- Audio Agent: Llama 3.2 3B
- Editor Agent: Claude 3 Haiku
- Supervisor: Qwen 2.5 7B

**Local Models (Optional - Pendrive):**
- Only 2 models for testing/development
- Can use API for everything instead
- Not required for production

**Total: 200+ models available via OpenRouter!**

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

## 📚 Documentation

- [Architecture Comparison](ARCHITECTURE_COMPARISON.md) - vs AWS/Azure/Vertex
- [Cost Analysis](COST_ANALYSIS_API_ONLY.md) - Detailed pricing
- [Code Analysis Guide](CODE_ANALYSIS_GUIDE.md) - Quality tools
- [Vendor Lock-in Explained](VENDOR_LOCK_IN_EXPLAINED.md) - Why OMA is different

## 📄 License

MIT License

---

**OMA.AI** - Enterprise AI without enterprise costs! 🚀
