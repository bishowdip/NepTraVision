# NepTraVision — common developer entry points.
# Run `make help` to list targets.

.DEFAULT_GOAL := help
PY ?= python

.PHONY: help install install-train install-serve install-dev lint fmt typecheck test clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: ## Install core (data pipeline + CLI)
	$(PY) -m pip install -e .

install-train: ## Install training extras (GPU box: Colab/Kaggle)
	$(PY) -m pip install -e ".[train]"

install-serve: ## Install prototype dashboard extras
	$(PY) -m pip install -e ".[serve]"

install-dev: ## Install dev + analysis tooling
	$(PY) -m pip install -e ".[dev,analysis]"

lint: ## Lint with ruff
	ruff check src tests

fmt: ## Auto-format / fix with ruff
	ruff check --fix src tests
	ruff format src tests

typecheck: ## Static type check with mypy
	mypy

test: ## Run the test suite
	pytest

clean: ## Remove caches and build artifacts
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache .mypy_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
