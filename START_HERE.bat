@echo off
REM ============================================================================
REM OMA.AI - QUICK START SCRIPT
REM Execute este script DEPOIS de iniciar o Docker Desktop
REM ============================================================================

echo.
echo ========================================
echo   OMA.AI - Quick Start
echo ========================================
echo.

REM Verificar se Docker est� rodando
echo [1/6] Verificando Docker Desktop...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Docker Desktop n�o est� rodando!
    echo.
    echo Por favor:
    echo 1. Abra o Docker Desktop do menu Iniciar
    echo 2. Aguarde at� ver "Docker Desktop is running" na bandeja
    echo 3. Execute este script novamente
    echo.
    pause
    exit /b 1
)
echo [OK] Docker Desktop est� rodando!
echo.

REM Verificar .env
echo [2/6] Verificando configura��o...
if not exist .env (
    echo [AVISO] Arquivo .env n�o encontrado!
    echo Copiando de .env.example...
    copy .env.example .env
    echo.
    echo [A��O NECESS�RIA] Edite o arquivo .env e adicione suas API keys:
    echo   - OPENROUTER_API_KEY=sk-or-v1-...
    echo   - PEXELS_API_KEY=...
    echo.
    notepad .env
    echo.
    echo Ap�s salvar o .env, pressione qualquer tecla...
    pause >nul
)
echo [OK] Arquivo .env configurado!
echo.

REM Build Dashboard
echo [3/6] Building Dashboard otimizado (pode levar 3-5 minutos)...
echo Iniciando build...
docker build -f Dockerfile.dashboard.optimized -t oma-dashboard:latest . >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Build do Dashboard falhou!
    echo Tentando build com output...
    docker build -f Dockerfile.dashboard.optimized -t oma-dashboard:latest .
    pause
    exit /b 1
)
echo [OK] Dashboard build completo!
echo.

REM Build Media Agent
echo [4/6] Building Media Agent otimizado (pode levar 5-8 minutos)...
echo Iniciando build...
docker build -f Dockerfile.media.optimized -t oma-media-agent:latest . >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Build do Media Agent falhou!
    echo Tentando build com output...
    docker build -f Dockerfile.media.optimized -t oma-media-agent:latest .
    pause
    exit /b 1
)
echo [OK] Media Agent build completo!
echo.

REM Iniciar stack
echo [5/6] Iniciando stack de desenvolvimento...
docker-compose -f docker-compose.dev.yml up -d

if %errorlevel% neq 0 (
    echo [ERRO] Falha ao iniciar servi�os!
    pause
    exit /b 1
)
echo.

REM Aguardar servi�os
echo [6/6] Aguardando servi�os iniciarem (30 segundos)...
timeout /t 30 /nobreak >nul

echo.
echo ========================================
echo   Servi�os Iniciados!
echo ========================================
echo.

REM Verificar status
docker-compose -f docker-compose.dev.yml ps

echo.
echo ========================================
echo   Acesse o Dashboard
echo ========================================
echo.
echo Dashboard OMA.AI: http://localhost:7860
echo.
echo Pressione qualquer tecla para abrir no navegador...
pause >nul

start http://localhost:7860

echo.
echo ========================================
echo   Comandos �teis
echo ========================================
echo.
echo Ver logs do Dashboard:
echo   docker-compose -f docker-compose.dev.yml logs -f dashboard
echo.
echo Ver logs do Media Agent:
echo   docker-compose -f docker-compose.dev.yml logs -f media-agent
echo.
echo Parar todos os servi�os:
echo   docker-compose -f docker-compose.dev.yml down
echo.
echo Reiniciar um servi�o:
echo   docker-compose -f docker-compose.dev.yml restart dashboard
echo.
pause
