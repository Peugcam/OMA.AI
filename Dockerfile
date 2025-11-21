# OMA Video Generation - Production Dockerfile for Render
# Gradio Dashboard with FFmpeg support

FROM python:3.11-slim

# Set metadata
LABEL maintainer="OMA Team"
LABEL version="2.0.0"
LABEL description="OMA Video Generation Dashboard"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive \
    GRADIO_SERVER_NAME=0.0.0.0

# Set working directory
WORKDIR /app

# Install system dependencies (ffmpeg for video processing)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs outputs/videos outputs/temp

# Expose Gradio port (Render uses PORT env var)
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:7860/')" || exit 1

# Run the Gradio dashboard
CMD ["python", "video_dashboard_complete.py"]
