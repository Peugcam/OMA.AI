@echo off
echo Abrindo ultimo video gerado...
cd /d "%~dp0"
for /f "delims=" %%i in ('dir /b /o-d outputs\videos\*.mp4 2^>nul') do (
    start "" "outputs\videos\%%i"
    echo Abrindo: %%i
    goto :end
)
echo Nenhum video encontrado!
:end
pause
