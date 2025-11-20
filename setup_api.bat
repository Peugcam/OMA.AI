@echo off
echo.
echo ========================================
echo   OMA API - Setup Rapido
echo ========================================
echo.

REM Instalar dependencias
echo [1/3] Instalando dependencias...
py -3 -m pip install -r requirements-api.txt --quiet

if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Falha ao instalar dependencias
    pause
    exit /b 1
)

echo OK - Dependencias instaladas
echo.

REM Criar .env se nao existir
if not exist .env (
    echo [2/3] Criando arquivo .env...
    echo OPENAI_API_KEY=your_key_here > .env
    echo API_PORT=8000 >> .env
    echo ENVIRONMENT=development >> .env
    echo DEBUG=true >> .env
    echo LOG_LEVEL=INFO >> .env
    echo.
    echo IMPORTANTE: Edite o arquivo .env e adicione sua OPENAI_API_KEY
    echo.
) else (
    echo [2/3] Arquivo .env ja existe - OK
    echo.
)

REM Criar diretorios necessarios
echo [3/3] Criando diretorios...
if not exist logs mkdir logs
if not exist outputs\videos mkdir outputs\videos
if not exist temp mkdir temp

echo OK - Diretorios criados
echo.

echo ========================================
echo   Setup Completo!
echo ========================================
echo.
echo Proximos passos:
echo.
echo 1. Edite .env e adicione sua OPENAI_API_KEY
echo 2. Execute: python run_api.py
echo 3. Acesse: http://localhost:8000/api/v1/docs
echo.
echo Para testar: pytest -v
echo.

pause
