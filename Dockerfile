# OMA Video Generation API - Production Dockerfile
# Multi-stage build for optimized image size

# ============================================
# Stage 1: Builder
# ============================================
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt requirements-api.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt && \
    pip install --no-cache-dir --user -r requirements-api.txt


# ============================================
# Stage 2: Runtime
# ============================================
FROM python:3.11-slim

# Set metadata
LABEL maintainer="OMA Team"
LABEL version="1.0.0"
LABEL description="OMA Video Generation API"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# Create non-root user
RUN useradd -m -u 1000 oma && \
    mkdir -p /app /app/logs /app/outputs /app/temp && \
    chown -R oma:oma /app

# Set working directory
WORKDIR /app

# Install runtime dependencies (ffmpeg for video processing)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /home/oma/.local

# Copy application code
COPY --chown=oma:oma . .

# Update PATH
ENV PATH=/home/oma/.local/bin:$PATH

# Switch to non-root user
USER oma

# Create necessary directories
RUN mkdir -p logs outputs/videos temp

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/ping')" || exit 1

# Run the application
CMD ["python", "run_api.py"]
