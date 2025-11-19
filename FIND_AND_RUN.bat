@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo LOCALIZANDO E EXECUTANDO PYTHON
echo ============================================================
echo.

REM Locais comuns onde Python pode estar
set "PYTHON_PATHS=C:\Python311\python.exe"
set "PYTHON_PATHS=%PYTHON_PATHS%;C:\Python310\python.exe"
set "PYTHON_PATHS=%PYTHON_PATHS%;C:\Python39\python.exe"
set "PYTHON_PATHS=%PYTHON_PATHS%;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe"
set "PYTHON_PATHS=%PYTHON_PATHS%;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe"
set "PYTHON_PATHS=%PYTHON_PATHS%;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39\python.exe"
set "PYTHON_PATHS=%PYTHON_PATHS%;C:\Program Files\Python311\python.exe"
set "PYTHON_PATHS=%PYTHON_PATHS%;C:\Program Files\Python310\python.exe"
set "PYTHON_PATHS=%PYTHON_PATHS%;C:\ProgramData\Anaconda3\python.exe"
set "PYTHON_PATHS=%PYTHON_PATHS%;C:\Users\%USERNAME%\Anaconda3\python.exe"

echo Procurando Python...
echo.

for %%p in (%PYTHON_PATHS%) do (
    if exist "%%p" (
        echo ENCONTRADO: %%p
        echo.
        echo Executando teste...
        echo ============================================================
        echo.
        "%%p" test_simple_hybrid.py
        echo.
        echo ============================================================
        echo TESTE CONCLUIDO!
        echo ============================================================
        pause
        exit /b 0
    )
)

REM Se chegou aqui, não encontrou
echo ============================================================
echo PYTHON NAO ENCONTRADO!
echo ============================================================
echo.
echo Procurei em:
for %%p in (%PYTHON_PATHS%) do (
    echo   - %%p
)
echo.
echo.
echo SOLUCAO:
echo 1. Instale Python de: https://www.python.org/downloads/
echo 2. Durante instalacao, marque "Add Python to PATH"
echo 3. Ou me diga onde esta instalado
echo.
pause
exit /b 1
