# API Quick Start Guide

**Get the OMA API running in 5 minutes!**

## Prerequisites

- Python 3.10+
- OpenAI API key
- OMA project installed

## Step 1: Install Dependencies

```bash
pip install -r requirements-api.txt
```

This installs:
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Pydantic (validation)
- Loguru (logging)
- SlowAPI (rate limiting)
- pytest (testing)

## Step 2: Configure Environment

Create `.env` file (copy from `.env.example`):

```env
# Minimum required config
OPENAI_API_KEY=sk-your-key-here
API_PORT=8000
ENVIRONMENT=development
DEBUG=true
```

Generate a secure SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Step 3: Start the API

```bash
python run_api.py
```

You should see:
```
🚀 Starting OMA Video Generation API
📊 Version: 1.0.0
🌍 Environment: development
🔗 URL: http://0.0.0.0:8000/api/v1
📚 Docs: http://0.0.0.0:8000/api/v1/docs
```

## Step 4: Test the API

### Option 1: Swagger UI (Easiest)

1. Open http://localhost:8000/api/v1/docs
2. Expand `POST /api/v1/videos/generate`
3. Click "Try it out"
4. Use this example:

```json
{
  "briefing": {
    "title": "Test Video",
    "description": "My first API-generated video!",
    "duration": 30,
    "style": "modern",
    "tone": "enthusiastic"
  }
}
```

5. Click "Execute"
6. Copy the `task_id` from the response
7. Check status at `GET /api/v1/videos/status/{task_id}`

### Option 2: cURL

```bash
# Generate video
curl -X POST "http://localhost:8000/api/v1/videos/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "briefing": {
      "title": "Test Video",
      "description": "Testing the API",
      "duration": 30
    }
  }'

# Response:
# {"success": true, "task_id": "video_20251120_123456", ...}

# Check status
curl "http://localhost:8000/api/v1/videos/status/video_20251120_123456"
```

### Option 3: Python

```python
import requests

# Generate
resp = requests.post(
    "http://localhost:8000/api/v1/videos/generate",
    json={
        "briefing": {
            "title": "Test Video",
            "description": "API test",
            "duration": 30
        }
    }
)

task_id = resp.json()["task_id"]
print(f"Task created: {task_id}")

# Check status
status = requests.get(
    f"http://localhost:8000/api/v1/videos/status/{task_id}"
)

print(status.json())
```

## Step 5: Monitor

### Check Health

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 123.45,
  "checks": {
    "api": true,
    "openai_config": true,
    "output_directory": true
  }
}
```

### View Logs

```bash
# Windows
type logs\api.log

# Linux/Mac
tail -f logs/api.log
```

## What's Next?

### Run Tests

```bash
pytest -v
```

### Explore API Docs

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

### Try Different Styles

Available styles:
- `professional` - Corporate
- `modern` - Contemporary
- `minimalist` - Clean
- `energetic` - Dynamic
- `elegant` - Refined

Available tones:
- `neutral` - Balanced
- `enthusiastic` - Excited
- `calm` - Soothing
- `inspiring` - Motivational
- `urgent` - Time-sensitive

### Check Statistics

```bash
curl http://localhost:8000/api/v1/stats
```

## Troubleshooting

### Port already in use

Change port in `.env`:
```env
API_PORT=8001
```

### OpenAI errors

Check your API key:
```bash
echo $OPENAI_API_KEY  # Linux/Mac
echo %OPENAI_API_KEY%  # Windows
```

### Import errors

Make sure you're in the project root:
```bash
cd OMA_REFACTORED
python run_api.py
```

### Can't access from other machines

Change host in `.env`:
```env
API_HOST=0.0.0.0  # Listen on all interfaces
```

## Common Tasks

### List All Tasks

```bash
curl http://localhost:8000/api/v1/videos/tasks
```

### Filter by Status

```bash
curl "http://localhost:8000/api/v1/videos/tasks?status_filter=completed&limit=10"
```

### Delete Task

```bash
curl -X DELETE "http://localhost:8000/api/v1/videos/tasks/{task_id}"
```

## Production Deployment

See `API_README.md` for full production deployment guide.

Quick checklist:
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=false`
- [ ] Generate secure `SECRET_KEY`
- [ ] Configure production `OPENAI_API_KEY`
- [ ] Setup reverse proxy (Nginx)
- [ ] Enable HTTPS

## Need Help?

- **Full API docs**: See `API_README.md`
- **Interactive docs**: http://localhost:8000/api/v1/docs
- **Logs**: Check `logs/api.log`

---

**Ready to generate videos!** 🎬
