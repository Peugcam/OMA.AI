@echo off
REM ========================================
REM  OMA Quality Checks - Windows Launcher
REM ========================================

echo.
echo ========================================
echo   OMA Code Quality Checks
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.10+ and add to PATH
    pause
    exit /b 1
)

REM Check if dependencies are installed
python -c "import black" >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Dependencies not installed!
    echo.
    choice /C YN /M "Do you want to install dependencies now"
    if errorlevel 2 goto :skipdeps
    if errorlevel 1 goto :installdeps
)
goto :skipdeps

:installdeps
echo.
echo Installing dependencies...
pip install -r requirements_analysis.txt
npm install
echo.
echo Dependencies installed!
echo.

:skipdeps

REM Parse command line arguments
set FIX_MODE=
set VERBOSE_MODE=

:parse
if "%~1"=="" goto :endparse
if /i "%~1"=="--fix" set FIX_MODE=--fix
if /i "%~1"=="-f" set FIX_MODE=--fix
if /i "%~1"=="--verbose" set VERBOSE_MODE=--verbose
if /i "%~1"=="-v" set VERBOSE_MODE=--verbose
shift
goto :parse

:endparse

REM Run quality checks
echo Running quality checks...
echo.

python run_quality_checks.py %FIX_MODE% %VERBOSE_MODE%

set EXIT_CODE=%errorlevel%

echo.
echo ========================================
if %EXIT_CODE%==0 (
    echo   All checks passed! ✓
) else (
    echo   Some checks failed! ✗
    echo   Review the output above
)
echo ========================================
echo.

pause
exit /b %EXIT_CODE%
