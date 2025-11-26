# OMA Video Generation - Production Dockerfile
# Compatible with Railway, Render, Heroku, and other PaaS
# Gradio Dashboard with FFmpeg support

FROM python:3.11-slim

# Set metadata
LABEL maintainer="OMA Team"
LABEL version="2.0.0"
LABEL description="OMA Video Generation Dashboard"

# Set environment variables
# PORT will be set by the platform (Railway, Render, Heroku)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive \
    GRADIO_SERVER_NAME=0.0.0.0 \
    ENVIRONMENT=production

# Set working directory
WORKDIR /app

# Install system dependencies (ffmpeg for video processing)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p logs outputs/videos outputs/temp outputs/images \
    && chmod -R 755 logs outputs

# Don't expose a fixed port - let the platform assign it via $PORT env var
# EXPOSE is just documentation, the actual port binding happens at runtime

# Health check using curl (more reliable than Python import)
HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
    CMD curl -f http://localhost:${PORT:-7860}/ || exit 1

# Run the Gradio dashboard (app.py handles PORT env var)
CMD ["python", "app.py"]
