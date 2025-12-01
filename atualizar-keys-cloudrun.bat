@echo off
REM ============================================================================
REM Script de Atualizacao de API Keys - Google Cloud Run
REM ============================================================================
REM
REM INSTRUCOES:
REM 1. Gere as novas API keys (veja GUIA_ATUALIZACAO_KEYS.md)
REM 2. Edite este arquivo e cole suas keys abaixo
REM 3. Execute: atualizar-keys-cloudrun.bat
REM
REM ============================================================================

echo.
echo ============================================================================
echo  OMA.AI - Atualizacao de API Keys no Google Cloud Run
echo ============================================================================
echo.

REM ----------------------------------------------------------------------------
REM PASSO 1: Cole suas NOVAS API keys aqui
REM ----------------------------------------------------------------------------

set NOVA_OPENROUTER_KEY=sk-or-v1-COLE_SUA_KEY_AQUI
set NOVA_PEXELS_KEY=COLE_SUA_KEY_AQUI
set NOVA_ELEVENLABS_KEY=COLE_SUA_KEY_AQUI
set NOVA_STABILITY_KEY=COLE_SUA_KEY_AQUI

REM ----------------------------------------------------------------------------
REM VALIDACAO
REM ----------------------------------------------------------------------------

echo [1/5] Validando keys...

if "%NOVA_OPENROUTER_KEY%"=="sk-or-v1-COLE_SUA_KEY_AQUI" (
    echo.
    echo ERRO: Voce precisa editar este arquivo e colar suas keys!
    echo.
    echo Abra: atualizar-keys-cloudrun.bat
    echo Edite as linhas com "COLE_SUA_KEY_AQUI"
    echo.
    pause
    exit /b 1
)

echo       OK - Keys configuradas

REM ----------------------------------------------------------------------------
REM CONFIGURACAO DO PROJETO
REM ----------------------------------------------------------------------------

echo.
echo [2/5] Configurando projeto Google Cloud...

set CLOUDSDK_PYTHON=C:/Users/paulo/AppData/Local/Programs/Python/Python313/python.exe
set PROJECT_ID=oma-video-prod
set SERVICE_NAME=oma-video-generator
set REGION=southamerica-east1

gcloud config set project %PROJECT_ID% 2>nul

if %errorlevel% neq 0 (
    echo.
    echo ERRO: Falha ao configurar projeto. Execute:
    echo   gcloud auth login
    echo.
    pause
    exit /b 1
)

echo       OK - Projeto configurado

REM ----------------------------------------------------------------------------
REM ATUALIZAR CLOUD RUN
REM ----------------------------------------------------------------------------

echo.
echo [3/5] Atualizando variaveis de ambiente no Cloud Run...
echo       (Isso pode demorar 2-5 minutos)
echo.

gcloud run services update %SERVICE_NAME% ^
  --region=%REGION% ^
  --update-env-vars=OPENROUTER_API_KEY=%NOVA_OPENROUTER_KEY% ^
  --update-env-vars=PEXELS_API_KEY=%NOVA_PEXELS_KEY% ^
  --update-env-vars=ELEVENLABS_API_KEY=%NOVA_ELEVENLABS_KEY% ^
  --update-env-vars=STABILITY_API_KEY=%NOVA_STABILITY_KEY% ^
  --quiet

if %errorlevel% neq 0 (
    echo.
    echo ERRO: Falha ao atualizar Cloud Run
    echo.
    echo Tente manualmente via Console:
    echo https://console.cloud.google.com/run?project=%PROJECT_ID%
    echo.
    pause
    exit /b 1
)

echo.
echo       OK - Cloud Run atualizado!

REM ----------------------------------------------------------------------------
REM OBTER URL DO SERVICO
REM ----------------------------------------------------------------------------

echo.
echo [4/5] Obtendo URL do servico...

for /f "delims=" %%i in ('gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="get(status.url)"') do set SERVICE_URL=%%i

echo       URL: %SERVICE_URL%

REM ----------------------------------------------------------------------------
REM TESTE BASICO
REM ----------------------------------------------------------------------------

echo.
echo [5/5] Testando servico...
echo       (Abrindo navegador...)
echo.

start %SERVICE_URL%

REM ----------------------------------------------------------------------------
REM SUCESSO
REM ----------------------------------------------------------------------------

echo.
echo ============================================================================
echo  SUCESSO! Keys atualizadas com sucesso
echo ============================================================================
echo.
echo Proximos passos:
echo   1. Teste o site no navegador que acabou de abrir
echo   2. Crie um video de teste para validar
echo   3. Se funcionar, atualize seu .env local (veja guia)
echo   4. Delete este arquivo: del atualizar-keys-cloudrun.bat
echo.
echo URL do Site: %SERVICE_URL%
echo.

pause
