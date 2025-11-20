# Docker Quick Start

**Get OMA running in Docker in 2 minutes!**

---

## Prerequisites

- Docker Desktop installed
- Git installed
- OpenAI API key

---

## Option 1: Docker Compose (Recommended)

### Step 1: Setup

```bash
# Clone repository
git clone https://github.com/Peugcam/OMA.AI.git
cd OMA_REFACTORED

# Create .env file
echo "OPENAI_API_KEY=your_key_here" > .env
```

### Step 2: Run

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### Step 3: Access

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/v1/docs
- **Dashboard**: http://localhost:7861

### Step 4: Test

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Generate video (via API docs)
# 1. Open http://localhost:8000/api/v1/docs
# 2. Try POST /api/v1/videos/generate
```

### Stop

```bash
docker-compose down
```

---

## Option 2: Docker Run

### Step 1: Build

```bash
docker build -t oma-api:latest .
```

### Step 2: Run

```bash
docker run -d \
  --name oma-api \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/outputs:/app/outputs \
  oma-api:latest
```

### Step 3: Check

```bash
# View logs
docker logs -f oma-api

# Health check
curl http://localhost:8000/api/v1/health
```

### Stop

```bash
docker stop oma-api
docker rm oma-api
```

---

## Option 3: Pull from Registry

```bash
# Pull latest image
docker pull ghcr.io/peugcam/oma.ai:latest

# Run
docker run -d \
  --name oma-api \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  ghcr.io/peugcam/oma.ai:latest
```

---

## Common Commands

```bash
# View logs
docker-compose logs -f api

# Restart
docker-compose restart api

# Rebuild
docker-compose build --no-cache
docker-compose up -d

# Stop all
docker-compose down

# Remove volumes
docker-compose down -v

# Execute command
docker-compose exec api /bin/bash
docker-compose exec api pytest
```

---

## Environment Variables

Create `.env` file:

```env
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional
API_PORT=8000
LOG_LEVEL=INFO
ENVIRONMENT=production
DEBUG=false
```

---

## Troubleshooting

### Port already in use

```bash
# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead
```

### Container won't start

```bash
# Check logs
docker logs oma-api

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

### Out of memory

```bash
# Add resource limits to docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
```

---

## Next Steps

1. **Read full guide**: `DOCKER_GUIDE.md`
2. **API documentation**: `API_README.md`
3. **Try examples**: http://localhost:8000/api/v1/docs

---

**Ready to containerize!** 🐳
