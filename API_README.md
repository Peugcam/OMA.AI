# OMA Video Generation API

**Professional REST API for automated video generation using multi-agent AI**

## Overview

A production-ready FastAPI application that provides programmatic access to the OMA video generation system. Generate professional videos through simple HTTP requests with full validation, error handling, and monitoring.

## Features

- **RESTful API** with OpenAPI documentation
- **Pydantic Validation** for all inputs/outputs
- **Rate Limiting** to prevent abuse
- **Structured Logging** with JSON format
- **Health Checks** for monitoring
- **Async Task Processing** for long-running operations
- **Error Handling** with detailed responses
- **CORS Support** for web applications
- **Test Suite** with pytest

## Quick Start

### Installation

```bash
# Install API dependencies
pip install -r requirements-api.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# REQUIRED: Set your OPENAI_API_KEY
```

### Configuration

Edit `.env` file:

```env
OPENAI_API_KEY=your_key_here
API_PORT=8000
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### Run API Server

```bash
# Development mode (auto-reload)
python run_api.py

# Or with uvicorn directly
uvicorn api.main:app --reload --port 8000
```

### Access Documentation

Once running:
- **API Docs (Swagger)**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## API Endpoints

### Health & Monitoring

#### `GET /api/v1/health`
Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 1234.56,
  "checks": {
    "api": true,
    "openai_config": true,
    "output_directory": true
  }
}
```

#### `GET /api/v1/ready`
Readiness check for K8s/orchestration.

#### `GET /api/v1/ping`
Simple ping endpoint.

### Video Generation

#### `POST /api/v1/videos/generate`
Generate a video from briefing.

**Rate Limit:** 5 requests per minute

**Request Body:**
```json
{
  "briefing": {
    "title": "Lançamento de Produto Inovador",
    "description": "Vídeo de apresentação de produto tecnológico...",
    "duration": 30,
    "target_audience": "Profissionais de tecnologia",
    "style": "modern",
    "tone": "enthusiastic",
    "cta": "Experimente grátis agora!"
  },
  "async_mode": false
}
```

**Response (202 Accepted):**
```json
{
  "success": true,
  "task_id": "video_20251120_101530",
  "timestamp": "2025-11-20T10:15:30"
}
```

#### `GET /api/v1/videos/status/{task_id}`
Get video generation task status.

**Response:**
```json
{
  "task_id": "video_20251120_101530",
  "status": "completed",
  "progress": 100,
  "current_phase": null,
  "result": {
    "success": true,
    "video_path": "outputs/videos/video_20251120_101530.mp4",
    "total_cost": 0.0234,
    "generation_time_seconds": 45.2
  }
}
```

#### `GET /api/v1/videos/tasks`
List all video generation tasks.

**Query Parameters:**
- `status_filter`: Filter by status (pending, processing, completed, failed)
- `limit`: Max tasks to return (default: 50)

#### `DELETE /api/v1/videos/tasks/{task_id}`
Delete a completed/failed task.

### Statistics

#### `GET /api/v1/stats`
Get system statistics.

**Response:**
```json
{
  "total_videos_generated": 42,
  "total_cost": 1.23,
  "average_generation_time": 45.5,
  "success_rate": 98.5,
  "uptime_seconds": 86400
}
```

## Data Models

### VideoBriefing

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Video title (3-200 chars) |
| `description` | string | Yes | Detailed description (10-5000 chars) |
| `duration` | integer | No | Duration in seconds (15-180, default: 30) |
| `target_audience` | string | No | Target audience description |
| `style` | enum | No | Visual style (professional, modern, minimalist, energetic, elegant) |
| `tone` | enum | No | Narrative tone (neutral, enthusiastic, calm, inspiring, urgent) |
| `cta` | string | No | Call-to-action message |

### Video Styles

- `professional` - Corporate, trustworthy
- `modern` - Contemporary, sleek
- `minimalist` - Clean, simple
- `energetic` - Dynamic, vibrant
- `elegant` - Refined, sophisticated

### Video Tones

- `neutral` - Balanced, informative
- `enthusiastic` - Excited, energetic
- `calm` - Soothing, peaceful
- `inspiring` - Motivational, uplifting
- `urgent` - Time-sensitive, important

## Usage Examples

### Python

```python
import requests

# Generate video
response = requests.post(
    "http://localhost:8000/api/v1/videos/generate",
    json={
        "briefing": {
            "title": "My Product Launch",
            "description": "Exciting new product announcement...",
            "duration": 30,
            "style": "modern",
            "tone": "enthusiastic"
        }
    }
)

task_id = response.json()["task_id"]

# Check status
status_response = requests.get(
    f"http://localhost:8000/api/v1/videos/status/{task_id}"
)

print(status_response.json())
```

### cURL

```bash
# Generate video
curl -X POST "http://localhost:8000/api/v1/videos/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "briefing": {
      "title": "Test Video",
      "description": "Testing the API...",
      "duration": 30
    }
  }'

# Check status
curl "http://localhost:8000/api/v1/videos/status/video_20251120_101530"
```

### JavaScript

```javascript
// Generate video
const response = await fetch('http://localhost:8000/api/v1/videos/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    briefing: {
      title: 'My Video',
      description: 'Video description...',
      duration: 30,
      style: 'modern'
    }
  })
});

const { task_id } = await response.json();

// Poll for status
const checkStatus = async () => {
  const statusRes = await fetch(
    `http://localhost:8000/api/v1/videos/status/${task_id}`
  );
  return await statusRes.json();
};
```

## Error Handling

All errors return a structured response:

```json
{
  "error": "ValidationError",
  "message": "Invalid request data",
  "details": {
    "validation_errors": [...]
  },
  "timestamp": "2025-11-20T10:15:30",
  "request_id": "abc-123"
}
```

### HTTP Status Codes

- `200 OK` - Success
- `202 Accepted` - Task created (async)
- `400 Bad Request` - Invalid request
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service down

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=api --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v
```

## Logging

Structured JSON logs are written to `logs/api.log`:

```json
{
  "event": "api_request",
  "method": "POST",
  "path": "/api/v1/videos/generate",
  "status_code": 202,
  "duration_ms": 123.45,
  "timestamp": "2025-11-20T10:15:30"
}
```

### Log Levels

- `DEBUG` - Detailed diagnostic information
- `INFO` - General informational messages
- `WARNING` - Warning messages
- `ERROR` - Error messages
- `CRITICAL` - Critical issues

Configure in `.env`:
```env
LOG_LEVEL=INFO
LOG_FILE=./logs/api.log
LOG_FORMAT=json
```

## Rate Limiting

Default limits:
- **Video Generation**: 5 requests/minute per IP
- **Other Endpoints**: 100 requests/hour per IP

Configure in `.env`:
```env
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_PER_HOUR=100
```

## Security

### API Keys (Future)

For production, implement API key authentication:

```python
# Future implementation
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}
```

### CORS

Configure allowed origins in `.env`:
```env
CORS_ORIGINS=["http://localhost:7861", "https://yourdomain.com"]
```

## Deployment

### Docker (Future)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements-api.txt

CMD ["python", "run_api.py"]
```

### Production Checklist

- [ ] Set strong `SECRET_KEY` in `.env`
- [ ] Configure production `OPENAI_API_KEY`
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=false`
- [ ] Configure specific `CORS_ORIGINS`
- [ ] Setup PostgreSQL for task storage
- [ ] Setup Redis for caching
- [ ] Configure monitoring (Sentry, Prometheus)
- [ ] Setup SSL/TLS certificates
- [ ] Configure reverse proxy (Nginx)
- [ ] Setup automated backups

## Architecture

```
api/
├── __init__.py
├── main.py           # FastAPI app & middleware
├── config.py         # Settings & environment
├── models.py         # Pydantic models
├── exceptions.py     # Custom exceptions
├── logger.py         # Structured logging
└── routers/
    ├── health.py     # Health checks
    ├── videos.py     # Video generation
    └── stats.py      # Statistics
```

## Performance

- **Async Processing**: Background tasks don't block API
- **Rate Limiting**: Prevents abuse
- **Connection Pooling**: Efficient DB connections (future)
- **Caching**: Redis for frequently accessed data (future)

## Monitoring

### Health Checks

```bash
# Liveness probe
curl http://localhost:8000/api/v1/ping

# Readiness probe
curl http://localhost:8000/api/v1/ready
```

### Metrics (Future)

Prometheus metrics available at `:9090/metrics`:
- Request count
- Request duration
- Error rate
- Active tasks

## Troubleshooting

### API won't start

```bash
# Check if port is in use
netstat -ano | findstr :8000

# Check logs
tail -f logs/api.log
```

### OpenAI errors

Verify API key:
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_KEY"
```

### Import errors

Ensure you're in the project root:
```bash
cd OMA_REFACTORED
python run_api.py
```

## Support

- **Issues**: Report bugs on GitHub
- **Docs**: http://localhost:8000/api/v1/docs
- **Logs**: Check `logs/api.log` for errors

## License

Proprietary - All rights reserved

---

**Version**: 1.0.0
**Last Updated**: 2025-11-20
**Status**: Production Ready
