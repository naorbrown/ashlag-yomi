# =============================================================================
# Ashlag Yomi Makefile
# =============================================================================
# Usage: make <target>
# Run 'make help' to see all available commands
# =============================================================================

.PHONY: help install install-dev test lint format type-check run send-daily clean pre-commit audit all

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
BLACK := $(PYTHON) -m black
RUFF := $(PYTHON) -m ruff
MYPY := $(PYTHON) -m mypy

# Colors for terminal output
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# =============================================================================
# Help
# =============================================================================

help: ## Show this help message
	@echo "$(BLUE)Ashlag Yomi - Available Commands$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'

# =============================================================================
# Installation
# =============================================================================

install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(RESET)"
	$(PIP) install -e .
	@echo "$(GREEN)Done!$(RESET)"

install-dev: ## Install all dependencies including dev tools
	@echo "$(BLUE)Installing all dependencies (including dev)...$(RESET)"
	$(PIP) install -e ".[dev]"
	$(PYTHON) -m pre_commit install
	@echo "$(GREEN)Done! Pre-commit hooks installed.$(RESET)"

# =============================================================================
# Code Quality
# =============================================================================

test: ## Run tests with coverage
	@echo "$(BLUE)Running tests...$(RESET)"
	$(PYTEST)

test-fast: ## Run tests without coverage (faster)
	@echo "$(BLUE)Running tests (no coverage)...$(RESET)"
	$(PYTEST) --no-cov -x

lint: ## Run linter (ruff)
	@echo "$(BLUE)Running linter...$(RESET)"
	$(RUFF) check src tests scripts

lint-fix: ## Run linter and auto-fix issues
	@echo "$(BLUE)Running linter with auto-fix...$(RESET)"
	$(RUFF) check --fix src tests scripts

format: ## Format code with black and ruff
	@echo "$(BLUE)Formatting code...$(RESET)"
	$(BLACK) src tests scripts
	$(RUFF) format src tests scripts

format-check: ## Check if code is formatted correctly
	@echo "$(BLUE)Checking code formatting...$(RESET)"
	$(BLACK) --check src tests scripts
	$(RUFF) format --check src tests scripts

type-check: ## Run type checker (mypy)
	@echo "$(BLUE)Running type checker...$(RESET)"
	$(MYPY) src

# =============================================================================
# Running the Bot
# =============================================================================

run: ## Run the bot locally (interactive mode)
	@echo "$(BLUE)Starting Ashlag Yomi bot...$(RESET)"
	$(PYTHON) -m src.bot.main

send-daily: ## Send today's quotes (for testing/manual trigger)
	@echo "$(BLUE)Sending daily quotes...$(RESET)"
	$(PYTHON) scripts/send_daily.py

test-bot: ## Run bot in test mode (sends to test channel)
	@echo "$(BLUE)Running bot test...$(RESET)"
	$(PYTHON) scripts/test_bot.py

# =============================================================================
# Development Utilities
# =============================================================================

pre-commit: ## Run all pre-commit hooks
	@echo "$(BLUE)Running pre-commit hooks...$(RESET)"
	$(PYTHON) -m pre_commit run --all-files

audit: ## Audit dependencies for security vulnerabilities
	@echo "$(BLUE)Auditing dependencies...$(RESET)"
	$(PYTHON) -m pip_audit

clean: ## Clean up generated files
	@echo "$(BLUE)Cleaning up...$(RESET)"
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache
	rm -rf htmlcov .coverage coverage.xml
	rm -rf dist build *.egg-info
	rm -rf .eggs
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)Cleaned!$(RESET)"

# =============================================================================
# Data Management
# =============================================================================

populate: ## Populate initial quote data
	@echo "$(BLUE)Populating quotes database...$(RESET)"
	$(PYTHON) scripts/populate_quotes.py

validate-quotes: ## Validate quote JSON files
	@echo "$(BLUE)Validating quote data...$(RESET)"
	$(PYTHON) -c "from src.data.repository import QuoteRepository; r = QuoteRepository(); r.validate_all()"

# =============================================================================
# Combined Commands
# =============================================================================

all: format lint type-check test ## Run all quality checks (format, lint, type-check, test)
	@echo "$(GREEN)All checks passed!$(RESET)"

check: lint type-check test ## Run all checks without formatting
	@echo "$(GREEN)All checks passed!$(RESET)"

ci: ## Run CI checks (same as GitHub Actions)
	@echo "$(BLUE)Running CI checks...$(RESET)"
	$(RUFF) check src tests scripts
	$(BLACK) --check src tests scripts
	$(MYPY) src
	$(PYTEST)
	@echo "$(GREEN)CI checks passed!$(RESET)"
