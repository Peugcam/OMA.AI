@echo off
echo.
echo ========================================
echo   OMA.AI - DIAGNOSTICO RAPIDO
echo ========================================
echo.

echo [1/5] Verificando Docker Desktop...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Docker Desktop NAO esta rodando!
    echo.
    echo SOLUCAO:
    echo 1. Abra o Menu Iniciar
    echo 2. Digite "Docker Desktop"
    echo 3. Clique para abrir
    echo 4. Aguarde 1-2 minutos
    echo 5. Execute este script novamente
    echo.
    pause
    exit /b 1
)
echo [OK] Docker Desktop esta rodando!
echo.

echo [2/5] Verificando arquivo .env...
if not exist .env (
    echo [X] Arquivo .env NAO encontrado!
    echo.
    echo SOLUCAO:
    echo Criando .env...
    copy .env.example .env
    echo.
    echo Edite o .env e adicione suas API keys:
    notepad .env
    echo.
    pause
)
echo [OK] Arquivo .env existe!
echo.

echo [3/5] Verificando imagens Docker...
docker images | findstr oma-dashboard >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Imagens NAO foram buildadas!
    echo.
    echo SOLUCAO:
    echo Execute: START_HERE.bat
    echo (Vai levar 8-10 minutos para buildar)
    echo.
    pause
    exit /b 1
)
echo [OK] Imagens Docker existem!
echo.

echo [4/5] Verificando containers...
docker ps | findstr oma >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Containers NAO estao rodando!
    echo.
    echo SOLUCAO:
    echo Iniciando containers...
    docker-compose -f docker-compose.dev.yml up -d
    echo.
    echo Aguardando 30 segundos...
    timeout /t 30 /nobreak
)
echo [OK] Containers estao rodando!
echo.

echo [5/5] Testando acesso ao Dashboard...
curl -s http://localhost:7860/health >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Dashboard NAO esta acessivel!
    echo.
    echo Verificando logs...
    docker-compose -f docker-compose.dev.yml logs --tail=20 dashboard
    echo.
    echo SOLUCAO:
    echo Ver arquivo: TROUBLESHOOTING.md
    echo.
    pause
    exit /b 1
)
echo [OK] Dashboard esta acessivel!
echo.

echo ========================================
echo   TUDO FUNCIONANDO!
echo ========================================
echo.
echo Dashboard: http://localhost:7860
echo.
echo Abrindo no navegador...
start http://localhost:7860
echo.
pause
