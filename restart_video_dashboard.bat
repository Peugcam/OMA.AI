@echo off
echo.
echo ========================================
echo   Reiniciando Video Dashboard
echo ========================================
echo.

REM Matar processo na porta 7861
echo [1/2] Parando dashboard anterior...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :7861 ^| findstr LISTENING') do (
    echo Matando processo %%a...
    taskkill /F /PID %%a 2>nul
)

timeout /t 2 /nobreak >nul

echo [2/2] Iniciando dashboard...
echo.

py -3 video_dashboard_complete.py

pause
