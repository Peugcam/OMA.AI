# 🚀 Getting Started with OMA

**Welcome to the OMA Video Generation Platform!**

---

## 📋 Quick Navigation

### For Users

- 🎬 **[Generate Videos via Dashboard](#option-1-gradio-dashboard)** - Visual web interface
- 🔌 **[Generate Videos via API](#option-2-rest-api)** - Programmatic access
- 🐳 **[Run with Docker](#option-3-docker)** - Containerized deployment

### For Developers

- 📚 **[API Documentation](API_README.md)** - Complete API reference
- 🐳 **[Docker Guide](DOCKER_GUIDE.md)** - Containerization & deployment
- 🧪 **[Run Tests](#testing)** - Automated testing
- 🔧 **[Development Setup](#development-setup)** - Local development

---

## ⚡ Quick Start (Choose One)

### Option 1: Gradio Dashboard

**Best for:** Visual interface, testing, demos

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set OpenAI key
# Add to .env: OPENAI_API_KEY=your_key

# 3. Start dashboard
python video_dashboard_complete.py

# 4. Open browser
# http://localhost:7861
```

**Features:**
- 5 professional templates
- Visual briefing builder
- Real-time generation monitoring
- Video preview

---

### Option 2: REST API

**Best for:** Automation, integration, web/mobile apps

```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install -r requirements-api.txt

# 2. Set OpenAI key
echo "OPENAI_API_KEY=your_key" > .env

# 3. Start API
python run_api.py

# 4. Access API docs
# http://localhost:8000/api/v1/docs
```

**Try it:**
```bash
curl -X POST "http://localhost:8000/api/v1/videos/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "briefing": {
      "title": "My First Video",
      "description": "Test video generation",
      "duration": 30
    }
  }'
```

**Features:**
- 9 professional endpoints
- OpenAPI/Swagger docs
- Rate limiting
- Request validation

---

### Option 3: Docker

**Best for:** Production, deployment, consistency

```bash
# 1. Create .env
echo "OPENAI_API_KEY=your_key" > .env

# 2. Run with Docker Compose
docker-compose up -d

# 3. Access services
# API: http://localhost:8000
# Dashboard: http://localhost:7861
```

**Features:**
- Isolated environment
- Easy deployment
- Production-ready
- Auto-restart

---

## 📖 Documentation Map

### Getting Started
- **[GETTING_STARTED.md](GETTING_STARTED.md)** ← You are here
- **[API_QUICKSTART.md](API_QUICKSTART.md)** - API in 5 minutes
- **[DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)** - Docker in 2 minutes

### Complete Guides
- **[API_README.md](API_README.md)** - Full API documentation
- **[DOCKER_GUIDE.md](DOCKER_GUIDE.md)** - Complete Docker & CI/CD guide

### Technical Details
- **[PRODUCTION_FOUNDATION_SUMMARY.md](PRODUCTION_FOUNDATION_SUMMARY.md)** - API implementation
- **[DOCKER_CI_CD_SUMMARY.md](DOCKER_CI_CD_SUMMARY.md)** - Docker & CI/CD details
- **[COMPLETE_IMPLEMENTATION_SUMMARY.md](COMPLETE_IMPLEMENTATION_SUMMARY.md)** - Everything combined

---

## 🎯 Use Cases

### 1. Marketing Videos

```python
import requests

briefing = {
    "title": "Product Launch 2025",
    "description": "Exciting new product reveal",
    "duration": 30,
    "style": "modern",
    "tone": "enthusiastic",
    "cta": "Pre-order now!"
}

response = requests.post(
    "http://localhost:8000/api/v1/videos/generate",
    json={"briefing": briefing}
)
```

### 2. Social Media Content

```python
briefing = {
    "title": "Quick Tip Tuesday",
    "description": "Weekly productivity tips",
    "duration": 15,
    "style": "energetic",
    "target_audience": "Young professionals"
}
```

### 3. Educational Content

```python
briefing = {
    "title": "How AI Works",
    "description": "Explaining AI to beginners",
    "duration": 60,
    "style": "professional",
    "tone": "calm"
}
```

### 4. Corporate Announcements

```python
briefing = {
    "title": "Q4 Results",
    "description": "Financial results presentation",
    "duration": 45,
    "style": "professional",
    "tone": "neutral"
}
```

---

## 🔧 Development Setup

### Prerequisites

- Python 3.10+
- OpenAI API key
- Git
- (Optional) Docker Desktop

### Installation

```bash
# 1. Clone repository
git clone https://github.com/Peugcam/OMA.AI.git
cd OMA_REFACTORED

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-api.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 5. Run tests
pytest -v

# 6. Start development server
python run_api.py
```

---

## 🧪 Testing

### Run All Tests

```bash
pytest -v
```

### Run Specific Tests

```bash
# API tests only
pytest tests/test_api.py -v

# Health checks only
pytest tests/test_api.py::TestHealthEndpoints -v

# With coverage
pytest --cov=api --cov-report=html
```

### Test Coverage

```bash
# Generate coverage report
pytest --cov=api --cov-report=html

# Open report
# Open htmlcov/index.html in browser
```

---

## 🐳 Docker Usage

### Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Restart
docker-compose restart

# Stop
docker-compose down
```

### Production

```bash
# Build image
docker build -t oma-api:v1.0.0 .

# Run container
docker run -d \
  --name oma-api \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  oma-api:v1.0.0
```

---

## 🔐 Environment Variables

### Required

```env
OPENAI_API_KEY=sk-your-key-here
```

### Optional

```env
# API Configuration
API_PORT=8000
API_HOST=0.0.0.0
DEBUG=false
ENVIRONMENT=production

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/api.log

# Rate Limiting
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_PER_HOUR=100
```

---

## 📊 Architecture

### System Overview

```
┌─────────────────────────────────────┐
│         User Interface              │
│  (Dashboard / API / Mobile App)     │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│          FastAPI Server             │
│   (Validation, Auth, Rate Limit)    │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│        Video Generation             │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  1. Supervisor Agent         │  │
│  │     (Analyze request)        │  │
│  └──────────┬───────────────────┘  │
│             ↓                       │
│  ┌──────────────────────────────┐  │
│  │  2. Script Agent             │  │
│  │     (Generate script)        │  │
│  └──────────┬───────────────────┘  │
│             ↓                       │
│  ┌──────────────────────────────┐  │
│  │  3. Visual Agent             │  │
│  │     (Create images)          │  │
│  └──────────┬───────────────────┘  │
│             ↓                       │
│  ┌──────────────────────────────┐  │
│  │  4. Audio Agent              │  │
│  │     (Generate audio)         │  │
│  └──────────┬───────────────────┘  │
│             ↓                       │
│  ┌──────────────────────────────┐  │
│  │  5. Editor Agent             │  │
│  │     (Combine & export)       │  │
│  └──────────┬───────────────────┘  │
│             ↓                       │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│        Generated Video              │
│       (outputs/videos/)             │
└─────────────────────────────────────┘
```

### Tech Stack

**Backend:**
- FastAPI (API framework)
- Pydantic (validation)
- OpenAI API (AI generation)
- FFmpeg (video processing)

**Frontend:**
- Gradio (dashboard)
- React/Vue/Angular (custom apps)

**Infrastructure:**
- Docker (containerization)
- GitHub Actions (CI/CD)
- Railway/Render (deployment)

---

## 🚀 Deployment

### Deploy to Railway

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Deploy
railway up
```

### Deploy to Render

```bash
# 1. Connect GitHub repo
# 2. Create new Web Service
# 3. Select Dockerfile
# 4. Add OPENAI_API_KEY secret
# 5. Deploy
```

### Deploy to AWS

```bash
# Use GitHub Actions workflow
git tag v1.0.0
git push origin v1.0.0
# Auto-deploys to AWS ECS
```

---

## 🔍 Monitoring

### Health Checks

```bash
# API health
curl http://localhost:8000/api/v1/health

# Readiness
curl http://localhost:8000/api/v1/ready

# Ping
curl http://localhost:8000/api/v1/ping
```

### Logs

```bash
# API logs
tail -f logs/api.log

# Docker logs
docker-compose logs -f api

# View last 100 lines
docker-compose logs --tail=100 api
```

### Metrics

```bash
# System stats
curl http://localhost:8000/api/v1/stats

# Container stats
docker stats oma-api
```

---

## 🆘 Troubleshooting

### API won't start

```bash
# Check if port is in use
netstat -ano | findstr :8000

# Check logs
python run_api.py
# or
docker logs oma-api
```

### OpenAI errors

```bash
# Verify API key
echo $OPENAI_API_KEY

# Test directly
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Import errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
pip install -r requirements-api.txt --force-reinstall
```

### Docker issues

```bash
# Rebuild
docker-compose build --no-cache

# Check logs
docker-compose logs -f

# Restart
docker-compose restart
```

---

## 📞 Support

### Documentation

- **Full API Docs**: http://localhost:8000/api/v1/docs
- **Docker Guide**: [DOCKER_GUIDE.md](DOCKER_GUIDE.md)
- **API Guide**: [API_README.md](API_README.md)

### Logs

```bash
# API logs
tail -f logs/api.log

# Docker logs
docker-compose logs -f
```

### GitHub

- **Issues**: https://github.com/Peugcam/OMA.AI/issues
- **Discussions**: https://github.com/Peugcam/OMA.AI/discussions

---

## 🎯 Next Steps

### For First-Time Users

1. ✅ Choose deployment method (Dashboard/API/Docker)
2. ✅ Follow quick start above
3. ✅ Generate first video
4. ✅ Explore API docs

### For Developers

1. ✅ Read [API_README.md](API_README.md)
2. ✅ Setup development environment
3. ✅ Run tests
4. ✅ Make changes
5. ✅ Submit PR

### For DevOps

1. ✅ Read [DOCKER_GUIDE.md](DOCKER_GUIDE.md)
2. ✅ Setup Docker
3. ✅ Configure CI/CD
4. ✅ Deploy to production

---

## 📄 License

Proprietary - All rights reserved

---

**Ready to generate amazing videos!** 🎬✨

*Last updated: 2025-11-20*
