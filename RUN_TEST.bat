@echo off
echo ============================================================
echo TESTE DO FLUXO HIBRIDO - OMA.AI
echo ============================================================
echo.

REM Tentar diferentes formas de executar Python
echo Tentando executar teste...
echo.

REM Tentativa 1: py
py test_simple_hybrid.py
if %errorlevel% equ 0 goto success

REM Tentativa 2: python
python test_simple_hybrid.py
if %errorlevel% equ 0 goto success

REM Tentativa 3: python3
python3 test_simple_hybrid.py
if %errorlevel% equ 0 goto success

REM Se chegou aqui, nenhum funcionou
echo.
echo ============================================================
echo ERRO: Python nao encontrado!
echo ============================================================
echo.
echo Por favor, instale Python:
echo 1. Acesse: https://www.python.org/downloads/
echo 2. Baixe Python 3.11+
echo 3. IMPORTANTE: Marque "Add Python to PATH" durante instalacao
echo.
pause
exit /b 1

:success
echo.
echo ============================================================
echo TESTE CONCLUIDO!
echo ============================================================
echo.
pause
