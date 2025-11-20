@echo off
REM ========================================
REM  Setup Quality Tools - Windows
REM ========================================

echo.
echo ========================================
echo   OMA Quality Tools Setup
echo ========================================
echo.

REM Check Python
echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)
python --version
echo.

REM Check Node.js
echo [2/5] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)
node --version
npm --version
echo.

REM Install Python dependencies
echo [3/5] Installing Python dependencies...
echo This may take a few minutes...
python -m pip install --upgrade pip
pip install -r requirements_analysis.txt
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install Python dependencies!
    pause
    exit /b 1
)
echo Python dependencies installed successfully!
echo.

REM Install Node.js dependencies
echo [4/5] Installing Node.js dependencies...
call npm install
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install Node.js dependencies!
    pause
    exit /b 1
)
echo Node.js dependencies installed successfully!
echo.

REM Setup pre-commit hooks
echo [5/5] Setting up pre-commit hooks...
pre-commit install
if errorlevel 1 (
    echo WARNING: Failed to setup pre-commit hooks
    echo You can setup manually later with: pre-commit install
) else (
    echo Pre-commit hooks installed successfully!
)
echo.

REM Verify installation
echo ========================================
echo   Verifying Installation
echo ========================================
echo.

echo Checking installed tools:
echo.

REM Check each tool
set ALL_OK=1

python -c "import black; print('✓ Black:', black.__version__)" 2>nul
if errorlevel 1 (
    echo ✗ Black: NOT FOUND
    set ALL_OK=0
)

python -c "import isort; print('✓ isort:', isort.__version__)" 2>nul
if errorlevel 1 (
    echo ✗ isort: NOT FOUND
    set ALL_OK=0
)

python -c "import pylint; print('✓ Pylint:', pylint.__version__)" 2>nul
if errorlevel 1 (
    echo ✗ Pylint: NOT FOUND
    set ALL_OK=0
)

python -c "import flake8; print('✓ Flake8: OK')" 2>nul
if errorlevel 1 (
    echo ✗ Flake8: NOT FOUND
    set ALL_OK=0
)

python -c "import mypy; print('✓ MyPy:', mypy.__version__)" 2>nul
if errorlevel 1 (
    echo ✗ MyPy: NOT FOUND
    set ALL_OK=0
)

python -c "import bandit; print('✓ Bandit: OK')" 2>nul
if errorlevel 1 (
    echo ✗ Bandit: NOT FOUND
    set ALL_OK=0
)

python -c "import radon; print('✓ Radon:', radon.VERSION)" 2>nul
if errorlevel 1 (
    echo ✗ Radon: NOT FOUND
    set ALL_OK=0
)

python -c "import vulture; print('✓ Vulture: OK')" 2>nul
if errorlevel 1 (
    echo ✗ Vulture: NOT FOUND
    set ALL_OK=0
)

call jscpd --version >nul 2>&1
if errorlevel 1 (
    echo ✗ jscpd: NOT FOUND
    set ALL_OK=0
) else (
    echo ✓ jscpd: OK
)

echo.

if %ALL_OK%==1 (
    echo ========================================
    echo   ✓ Setup Complete!
    echo ========================================
    echo.
    echo All tools installed successfully!
    echo.
    echo Next steps:
    echo   1. Run quality checks:  npm run check:all
    echo   2. Auto-fix issues:     npm run check:all:fix
    echo   3. Read documentation:  QUICK_QUALITY_REFERENCE.md
    echo.
    echo To run a quick test:
    echo   RUN_QUALITY_CHECKS.bat
    echo.
) else (
    echo ========================================
    echo   ⚠ Setup Complete with Warnings
    echo ========================================
    echo.
    echo Some tools failed to install.
    echo Please check the errors above and try:
    echo   pip install -r requirements_analysis.txt
    echo   npm install
    echo.
)

pause
