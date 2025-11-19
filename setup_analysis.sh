#!/bin/bash

# OMA Code Analysis Setup Script
# This script installs all necessary tools for code analysis

set -e  # Exit on error

echo "🚀 Setting up OMA Code Analysis Tools..."
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    echo "   Download from: https://nodejs.org/"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ first."
    echo "   Download from: https://www.python.org/"
    exit 1
fi

# Determine Python command
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "✅ Node.js $(node --version) found"
echo "✅ Python $($PYTHON_CMD --version 2>&1) found"
echo ""

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies (jscpd)..."
npm install
echo ""

# Install Python analysis tools
echo "📦 Installing Python analysis tools..."
$PYTHON_CMD -m pip install --upgrade pip
$PYTHON_CMD -m pip install -r requirements_analysis.txt
echo ""

# Install pre-commit hooks
echo "🔗 Installing pre-commit hooks..."
$PYTHON_CMD -m pip install pre-commit
pre-commit install
echo ""

# Create reports directory
echo "📁 Creating reports directory..."
mkdir -p reports/jscpd
echo ""

# Run initial analysis
echo "🔍 Running initial code analysis..."
echo "   This may take a few minutes..."
echo ""

# Run jscpd
echo "📊 Running duplicate detection..."
npm run check:duplicates || true
echo ""

# Display summary
echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Available commands:"
echo "   npm run check:duplicates          - Detect duplicate code"
echo "   npm run check:duplicates:watch    - Watch for duplicates during development"
echo "   python run_analysis.py            - Run complete analysis"
echo "   pre-commit run --all-files        - Run all pre-commit checks"
echo ""
echo "📖 Documentation:"
echo "   See CODE_ANALYSIS_GUIDE.md for detailed usage instructions"
echo ""
echo "🎯 Next steps:"
echo "   1. Review the duplicate code report in reports/jscpd/html/index.html"
echo "   2. Run: python run_analysis.py"
echo "   3. Check CODE_ANALYSIS_GUIDE.md for best practices"
echo ""
