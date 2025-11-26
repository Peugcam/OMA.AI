#!/bin/bash
# ============================================================================
# OMA.AI Docker Setup and Testing Script
# Builds images, runs tests, and starts the stack
# ============================================================================

set -e  # Exit on error

echo ""
echo "========================================"
echo "OMA.AI Docker Setup"
echo "========================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "[ERROR] Docker is not running!"
    echo "Please start Docker and try again."
    exit 1
fi

echo "[OK] Docker is running"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "[WARNING] .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "[ACTION REQUIRED] Please edit .env and add your API keys:"
    echo "  - OPENROUTER_API_KEY"
    echo "  - PEXELS_API_KEY"
    echo ""
    read -p "Press Enter to continue after editing .env..."
fi

echo "========================================"
echo "Step 1: Building Docker Images"
echo "========================================"
echo ""

echo "Building Dashboard image..."
docker build -f Dockerfile.dashboard -t oma-dashboard:latest .
echo "[OK] Dashboard image built successfully"
echo ""

echo "Building Media Agent image..."
docker build -f Dockerfile.media -t oma-media-agent:latest .
echo "[OK] Media Agent image built successfully"
echo ""

echo "========================================"
echo "Step 2: Testing Images"
echo "========================================"
echo ""

echo "Testing Dashboard image..."
docker run --rm oma-dashboard:latest python -c "import gradio; print('Gradio version:', gradio.__version__)"
echo "[OK] Dashboard image is working"
echo ""

echo "Testing Media Agent image (FFmpeg)..."
docker run --rm oma-media-agent:latest ffmpeg -version | head -n 1
echo "[OK] FFmpeg is working in Media Agent"
echo ""

echo "========================================"
echo "Step 3: Starting Docker Compose Stack"
echo "========================================"
echo ""

echo "Starting services..."
docker-compose -f docker-compose.dev.yml up -d

echo ""
echo "[OK] All services started successfully!"
echo ""

echo "========================================"
echo "Access Points"
echo "========================================"
echo ""
echo "Dashboard:        http://localhost:7860"
echo "Redis Commander:  http://localhost:8081 (with --profile debug)"
echo "Prometheus:       http://localhost:9090 (with --profile monitoring)"
echo "Grafana:          http://localhost:3000 (with --profile monitoring)"
echo ""

echo "========================================"
echo "Checking Container Status"
echo "========================================"
echo ""

docker-compose -f docker-compose.dev.yml ps

echo ""
echo "========================================"
echo "View Logs"
echo "========================================"
echo ""
echo "To view logs, run:"
echo "  docker-compose -f docker-compose.dev.yml logs -f [service-name]"
echo ""
echo "Services: dashboard, media-agent, redis"
echo ""

echo "========================================"
echo "Stop Services"
echo "========================================"
echo ""
echo "To stop all services, run:"
echo "  docker-compose -f docker-compose.dev.yml down"
echo ""
