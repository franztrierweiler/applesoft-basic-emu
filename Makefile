PYTHON ?= python3

.PHONY: help install test lint run web-build web-serve clean

help: ## Afficher cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Installer le projet en mode développeur
	pip install -e ".[dev]"

test: ## Lancer les tests (pytest)
	$(PYTHON) -m pytest tests/ -v

test-cov: ## Lancer les tests avec couverture
	$(PYTHON) -m pytest tests/ -v --cov=src --cov-report=term-missing

lint: ## Vérifier le code (ruff + mypy)
	ruff check src/ tests/
	mypy src/

format: ## Formater le code (ruff)
	ruff format src/ tests/
	ruff check --fix src/ tests/

run: ## Lancer le REPL Applesoft BASIC
	$(PYTHON) -m src.main $(FILE)

web-build: ## Construire le site web statique (Phase 2)
	@echo "Phase 2 — non implémenté"

web-serve: ## Prévisualiser le site web en local (Phase 2)
	@echo "Phase 2 — non implémenté"

clean: ## Nettoyer les fichiers générés
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
