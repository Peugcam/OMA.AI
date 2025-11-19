@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo TESTE COMPLETO - 2 VIDEOS HIBRIDOS
echo ============================================================
echo.
echo Este teste vai criar 2 videos:
echo 1. Video Corporativo (OMA.AI)
echo 2. Video Tech/Abstrato (Futuro da IA)
echo.
echo Vai validar:
echo - Classificacao automatica por cena
echo - Busca no Pexels para pessoas
echo - Geracao com Stability para conceitos abstratos
echo - Custo total otimizado
echo.

pause

echo.
echo Procurando Python...
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

for %%p in (%PYTHON_PATHS%) do (
    if exist "%%p" (
        echo ENCONTRADO: %%p
        echo.
        echo ============================================================
        echo EXECUTANDO TESTES COMPLETOS...
        echo ============================================================
        echo.
        "%%p" test_hybrid_videos.py
        echo.
        echo ============================================================
        echo TESTES CONCLUIDOS!
        echo ============================================================
        echo.
        echo Resultados salvos em: .\test_results\
        echo.
        pause
        exit /b 0
    )
)

echo PYTHON NAO ENCONTRADO!
pause
exit /b 1
