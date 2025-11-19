@echo off
REM OMA Code Analysis Setup Script for Windows
REM This script installs all necessary tools for code analysis

echo.
echo 🚀 Setting up OMA Code Analysis Tools...
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Node.js is not installed. Please install Node.js first.
    echo    Download from: https://nodejs.org/
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    echo    Download from: https://www.python.org/
    exit /b 1
)

echo ✅ Node.js found
node --version
echo ✅ Python found
python --version
echo.

REM Install Node.js dependencies
echo 📦 Installing Node.js dependencies (jscpd)...
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install Node.js dependencies
    exit /b 1
)
echo.

REM Install Python analysis tools
echo 📦 Installing Python analysis tools...
python -m pip install --upgrade pip
python -m pip install -r requirements_analysis.txt
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install Python analysis tools
    exit /b 1
)
echo.

REM Install pre-commit hooks
echo 🔗 Installing pre-commit hooks...
python -m pip install pre-commit
pre-commit install
echo.

REM Create reports directory
echo 📁 Creating reports directory...
if not exist reports\jscpd mkdir reports\jscpd
echo.

REM Run initial analysis
echo 🔍 Running initial code analysis...
echo    This may take a few minutes...
echo.

REM Run jscpd
echo 📊 Running duplicate detection...
call npm run check:duplicates
echo.

REM Display summary
echo.
echo ✅ Setup complete!
echo.
echo 📋 Available commands:
echo    npm run check:duplicates          - Detect duplicate code
echo    npm run check:duplicates:watch    - Watch for duplicates during development
echo    python run_analysis.py            - Run complete analysis
echo    pre-commit run --all-files        - Run all pre-commit checks
echo.
echo 📖 Documentation:
echo    See CODE_ANALYSIS_GUIDE.md for detailed usage instructions
echo.
echo 🎯 Next steps:
echo    1. Review the duplicate code report in reports\jscpd\html\index.html
echo    2. Run: python run_analysis.py
echo    3. Check CODE_ANALYSIS_GUIDE.md for best practices
echo.

pause
