@echo off
REM ============================================================================
REM OMA Video Generation - Deploy para Google Cloud Run (Windows)
REM ============================================================================
REM Execute este script no PowerShell ou CMD
REM ============================================================================

setlocal enabledelayedexpansion

REM ============================================
REM CONFIGURACOES (EDITE AQUI)
REM ============================================
if "%GCP_PROJECT_ID%"=="" set GCP_PROJECT_ID=seu-projeto-gcp
if "%GCP_REGION%"=="" set GCP_REGION=southamerica-east1

set SERVICE_NAME=oma-video-generator
set IMAGE_NAME=oma-api
set CPU=2
set MEMORY=4Gi
set MIN_INSTANCES=0
set MAX_INSTANCES=10
set TIMEOUT=900
set CONCURRENCY=10

echo ============================================
echo    OMA Video Generator - Cloud Run Deploy
echo ============================================
echo.

REM ============================================
REM VERIFICAR PRE-REQUISITOS
REM ============================================
echo [1/7] Verificando pre-requisitos...

where gcloud >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: gcloud CLI nao encontrado!
    echo Instale em: https://cloud.google.com/sdk/docs/install
    exit /b 1
)

where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Docker nao encontrado!
    echo Instale em: https://docs.docker.com/get-docker/
    exit /b 1
)

echo [OK] gcloud CLI instalado
echo [OK] Docker instalado

REM ============================================
REM CONFIGURAR PROJETO GCP
REM ============================================
echo.
echo [2/7] Configurando projeto GCP...

if "%GCP_PROJECT_ID%"=="seu-projeto-gcp" (
    echo ERRO: Configure GCP_PROJECT_ID!
    echo Execute: set GCP_PROJECT_ID=seu-projeto-id
    exit /b 1
)

call gcloud config set project %GCP_PROJECT_ID%
echo [OK] Projeto configurado: %GCP_PROJECT_ID%

echo Habilitando APIs necessarias...
call gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com artifactregistry.googleapis.com --quiet

echo [OK] APIs habilitadas

REM ============================================
REM CONFIGURAR ARTIFACT REGISTRY
REM ============================================
echo.
echo [3/7] Configurando Artifact Registry...

call gcloud artifacts repositories create docker-repo --repository-format=docker --location=%GCP_REGION% --description="OMA Docker images" --quiet 2>nul

call gcloud auth configure-docker %GCP_REGION%-docker.pkg.dev --quiet

echo [OK] Artifact Registry configurado

REM ============================================
REM BUILD DA IMAGEM DOCKER
REM ============================================
echo.
echo [4/7] Construindo imagem Docker...

set IMAGE_URI=%GCP_REGION%-docker.pkg.dev/%GCP_PROJECT_ID%/docker-repo/%IMAGE_NAME%:latest

docker build -f Dockerfile.cloudrun -t %IMAGE_URI% --platform linux/amd64 .

if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Falha ao construir imagem Docker!
    exit /b 1
)

echo [OK] Imagem construida: %IMAGE_URI%

REM ============================================
REM PUSH PARA ARTIFACT REGISTRY
REM ============================================
echo.
echo [5/7] Enviando imagem para Artifact Registry...

docker push %IMAGE_URI%

if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Falha ao enviar imagem!
    exit /b 1
)

echo [OK] Imagem enviada

REM ============================================
REM VERIFICAR VARIAVEIS DE AMBIENTE
REM ============================================
echo.
echo [6/7] Verificando variaveis de ambiente...

if "%OPENROUTER_API_KEY%"=="" (
    echo AVISO: OPENROUTER_API_KEY nao definida!
    echo Execute: set OPENROUTER_API_KEY=sua-chave
)

if "%PEXELS_API_KEY%"=="" (
    echo AVISO: PEXELS_API_KEY nao definida!
)

REM ============================================
REM DEPLOY NO CLOUD RUN
REM ============================================
echo.
echo [7/7] Fazendo deploy no Cloud Run...

set ENV_VARS=ENVIRONMENT=production,GRADIO_SERVER_NAME=0.0.0.0

if not "%OPENROUTER_API_KEY%"=="" set ENV_VARS=%ENV_VARS%,OPENROUTER_API_KEY=%OPENROUTER_API_KEY%
if not "%PEXELS_API_KEY%"=="" set ENV_VARS=%ENV_VARS%,PEXELS_API_KEY=%PEXELS_API_KEY%
if not "%STABILITY_API_KEY%"=="" set ENV_VARS=%ENV_VARS%,STABILITY_API_KEY=%STABILITY_API_KEY%
if not "%ELEVENLABS_API_KEY%"=="" set ENV_VARS=%ENV_VARS%,ELEVENLABS_API_KEY=%ELEVENLABS_API_KEY%

call gcloud run deploy %SERVICE_NAME% ^
    --image %IMAGE_URI% ^
    --platform managed ^
    --region %GCP_REGION% ^
    --cpu %CPU% ^
    --memory %MEMORY% ^
    --min-instances %MIN_INSTANCES% ^
    --max-instances %MAX_INSTANCES% ^
    --timeout %TIMEOUT% ^
    --concurrency %CONCURRENCY% ^
    --set-env-vars "%ENV_VARS%" ^
    --allow-unauthenticated ^
    --port 8080

if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Falha no deploy!
    exit /b 1
)

REM ============================================
REM RESULTADO
REM ============================================
echo.
echo ============================================
echo    DEPLOY CONCLUIDO COM SUCESSO!
echo ============================================
echo.

for /f "tokens=*" %%i in ('gcloud run services describe %SERVICE_NAME% --region %GCP_REGION% --format "value(status.url)"') do set SERVICE_URL=%%i

echo URL do servico: %SERVICE_URL%
echo.
echo Proximos passos:
echo 1. Acesse a URL acima para testar o dashboard
echo 2. Configure variaveis de ambiente no Console se necessario
echo.
echo Comandos uteis:
echo   Ver logs:     gcloud run logs read --service %SERVICE_NAME% --region %GCP_REGION%
echo   Ver status:   gcloud run services describe %SERVICE_NAME% --region %GCP_REGION%
echo   Deletar:      gcloud run services delete %SERVICE_NAME% --region %GCP_REGION%
echo.

endlocal
