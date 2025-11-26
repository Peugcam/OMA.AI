@echo off
REM ============================================================================
REM OMA.AI Docker Setup and Testing Script
REM Builds images, runs tests, and starts the stack
REM ============================================================================

echo.
echo ========================================
echo OMA.AI Docker Setup
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.

REM Check if .env file exists
if not exist .env (
    echo [WARNING] .env file not found!
    echo Creating .env from .env.example...
    copy .env.example .env
    echo.
    echo [ACTION REQUIRED] Please edit .env and add your API keys:
    echo   - OPENROUTER_API_KEY
    echo   - PEXELS_API_KEY
    echo.
    pause
)

echo ========================================
echo Step 1: Building Docker Images
echo ========================================
echo.

echo Building Dashboard image...
docker build -f Dockerfile.dashboard -t oma-dashboard:latest .
if %errorlevel% neq 0 (
    echo [ERROR] Dashboard build failed!
    pause
    exit /b 1
)
echo [OK] Dashboard image built successfully
echo.

echo Building Media Agent image...
docker build -f Dockerfile.media -t oma-media-agent:latest .
if %errorlevel% neq 0 (
    echo [ERROR] Media Agent build failed!
    pause
    exit /b 1
)
echo [OK] Media Agent image built successfully
echo.

echo ========================================
echo Step 2: Testing Images
echo ========================================
echo.

echo Testing Dashboard image...
docker run --rm oma-dashboard:latest python -c "import gradio; print('Gradio version:', gradio.__version__)"
if %errorlevel% neq 0 (
    echo [ERROR] Dashboard image test failed!
    pause
    exit /b 1
)
echo [OK] Dashboard image is working
echo.

echo Testing Media Agent image (FFmpeg)...
docker run --rm oma-media-agent:latest ffmpeg -version
if %errorlevel% neq 0 (
    echo [ERROR] FFmpeg not found in Media Agent!
    pause
    exit /b 1
)
echo [OK] FFmpeg is working in Media Agent
echo.

echo ========================================
echo Step 3: Starting Docker Compose Stack
echo ========================================
echo.

echo Starting services...
docker-compose -f docker-compose.dev.yml up -d

if %errorlevel% neq 0 (
    echo [ERROR] Failed to start services!
    pause
    exit /b 1
)

echo.
echo [OK] All services started successfully!
echo.

echo ========================================
echo Access Points
echo ========================================
echo.
echo Dashboard:        http://localhost:7860
echo Redis Commander:  http://localhost:8081 (with --profile debug)
echo Prometheus:       http://localhost:9090 (with --profile monitoring)
echo Grafana:          http://localhost:3000 (with --profile monitoring)
echo.

echo ========================================
echo Checking Container Status
echo ========================================
echo.

docker-compose -f docker-compose.dev.yml ps

echo.
echo ========================================
echo View Logs
echo ========================================
echo.
echo To view logs, run:
echo   docker-compose -f docker-compose.dev.yml logs -f [service-name]
echo.
echo Services: dashboard, media-agent, redis
echo.

echo ========================================
echo Stop Services
echo ========================================
echo.
echo To stop all services, run:
echo   docker-compose -f docker-compose.dev.yml down
echo.

pause
