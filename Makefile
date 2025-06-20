.PHONY: help install lint format type-check security-check test clean all-checks

help:
	@echo "Available commands:"
	@echo "  install          Install all dependencies including dev tools"
	@echo "  lint             Run flake8 linter (check only)"
	@echo "  lint-fix         Auto-fix lint issues with autopep8"
	@echo "  format           Run black and isort formatters"
	@echo "  format-all       Auto-fix everything (lint + format)"
	@echo "  all-checks       Run all linting and formatting tools (check only)"
	@echo "  pre-commit       Install and run pre-commit hooks"
	@echo "  clean            Clean up cache files"

install:
	pip install -r requirements.txt

lint:
	flake8 .

lint-fix:
	autopep8 --in-place --aggressive --aggressive --recursive .
	@echo "Auto-fixed lint issues with autopep8!"

format:
	black .
	isort .

format-all: lint-fix format
	@echo "All auto-fixes applied!"

all-checks: lint type-check
	@echo "All checks completed!"

pre-commit:
	pre-commit install
	pre-commit run --all-files

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".mypy_cache" -delete
	find . -type d -name ".pytest_cache" -delete
