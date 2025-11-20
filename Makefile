# Makefile for OMA_REFACTORED Quality Checks
# Cross-platform commands for code quality

.PHONY: help setup clean test check check-fix format lint security complexity duplicates reports all

# Default target
.DEFAULT_GOAL := help

# Colors for output (works on Unix-like systems)
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)OMA_REFACTORED - Quality Tools$(NC)"
	@echo ""
	@echo "$(GREEN)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

setup: ## Install all dependencies and configure hooks
	@echo "$(GREEN)Installing dependencies...$(NC)"
	pip install -r requirements_analysis.txt
	npm install
	pre-commit install
	@echo "$(GREEN)Setup complete!$(NC)"

clean: ## Clean cache files and reports
	@echo "$(GREEN)Cleaning cache and reports...$(NC)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf reports/ 2>/dev/null || true
	@echo "$(GREEN)Clean complete!$(NC)"

format: ## Format code with Black and isort
	@echo "$(GREEN)Formatting code...$(NC)"
	black .
	isort .
	@echo "$(GREEN)Formatting complete!$(NC)"

format-check: ## Check code formatting without changes
	@echo "$(GREEN)Checking formatting...$(NC)"
	black --check --diff .
	isort --check-only --diff .

lint: ## Run linting (Pylint + Flake8)
	@echo "$(GREEN)Running linters...$(NC)"
	-pylint --rcfile=.pylintrc --load-plugins=pylint_custom_checkers agents/ core/ mcp/
	-flake8 .

types: ## Run type checking with MyPy
	@echo "$(GREEN)Running type checks...$(NC)"
	mypy agents/ core/ mcp/ --config-file=pyproject.toml

security: ## Run security analysis with Bandit
	@echo "$(GREEN)Running security analysis...$(NC)"
	bandit -c .bandit.yaml -r agents/ core/ mcp/

complexity: ## Analyze code complexity with Radon
	@echo "$(GREEN)Analyzing complexity...$(NC)"
	radon cc . --min B --show-complexity
	@echo ""
	radon mi . --min B --show

duplicates: ## Check for duplicate code with jscpd
	@echo "$(GREEN)Checking for duplicates...$(NC)"
	npm run check:duplicates

deadcode: ## Find dead code with Vulture
	@echo "$(GREEN)Finding dead code...$(NC)"
	vulture . --min-confidence 80

test: ## Run tests with pytest
	@echo "$(GREEN)Running tests...$(NC)"
	pytest -v

test-cov: ## Run tests with coverage report
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	pytest --cov=. --cov-report=term-missing --cov-report=html:reports/coverage

check: ## Run all quality checks (read-only)
	@echo "$(GREEN)Running all quality checks...$(NC)"
	python run_quality_checks.py --verbose

check-fix: ## Run all quality checks and auto-fix issues
	@echo "$(GREEN)Running quality checks with auto-fix...$(NC)"
	python run_quality_checks.py --fix --verbose

pre-commit: ## Run pre-commit hooks manually
	@echo "$(GREEN)Running pre-commit hooks...$(NC)"
	pre-commit run --all-files

pre-commit-update: ## Update pre-commit hook versions
	@echo "$(GREEN)Updating pre-commit hooks...$(NC)"
	pre-commit autoupdate

reports: ## Generate all reports (duplicates + coverage)
	@echo "$(GREEN)Generating reports...$(NC)"
	npm run check:duplicates || true
	pytest --cov=. --cov-report=html:reports/coverage || true
	@echo ""
	@echo "$(GREEN)Reports generated:$(NC)"
	@echo "  - Duplicates: reports/jscpd/html/index.html"
	@echo "  - Coverage:   reports/coverage/index.html"

all: format lint types security complexity duplicates deadcode test ## Run everything (format + all checks + tests)
	@echo ""
	@echo "$(GREEN)All checks complete!$(NC)"

quick: format-check lint types ## Quick checks (no formatting, no heavy analysis)
	@echo "$(GREEN)Quick checks complete!$(NC)"

ci: ## CI/CD pipeline checks
	@echo "$(GREEN)Running CI/CD checks...$(NC)"
	black --check .
	isort --check-only .
	flake8 .
	mypy agents/ core/ mcp/ --config-file=pyproject.toml
	bandit -c .bandit.yaml -r agents/ core/ mcp/
	pytest --cov=. --cov-report=term-missing
	npm run check:duplicates:ci

# Aliases for common commands
install: setup ## Alias for setup
fmt: format ## Alias for format
lint-fix: ## Fix linting issues automatically
	@echo "$(GREEN)Auto-fixing linting issues...$(NC)"
	autopep8 --in-place --aggressive --aggressive -r .
	black .
	isort .
