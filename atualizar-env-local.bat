@echo off
REM ============================================================================
REM Script para Atualizar .env Local com Novas Keys
REM ============================================================================

echo.
echo ============================================================================
echo  Atualizacao do arquivo .env local
echo ============================================================================
echo.

echo IMPORTANTE: Este script vai atualizar seu arquivo .env local
echo com as novas API keys.
echo.

REM Verificar se .env existe
if not exist ".env" (
    echo Arquivo .env nao encontrado!
    echo Criando a partir de .env.example...
    copy .env.example .env
)

echo Backup do .env atual...
copy .env .env.backup.%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%

echo.
echo Agora vou abrir o .env no Notepad.
echo.
echo Por favor, atualize as seguintes linhas:
echo   - OPENROUTER_API_KEY=sua-nova-key
echo   - PEXELS_API_KEY=sua-nova-key
echo   - ELEVENLABS_API_KEY=sua-nova-key
echo   - STABILITY_API_KEY=sua-nova-key
echo.
echo Salve e feche o Notepad quando terminar.
echo.

pause

notepad .env

echo.
echo Arquivo .env atualizado!
echo Backup salvo em: .env.backup.*
echo.

pause
