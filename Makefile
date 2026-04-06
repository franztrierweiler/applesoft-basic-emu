.PHONY: help install test lint run clean

help: ## Afficher cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Installer le projet et les dépendances de développement
	pip install -e ".[dev,png]"

test: ## Lancer les tests unitaires
	python3 -m pytest tests/ -v

lint: ## Vérifier le code avec ruff
	ruff check src/ tests/
	ruff format --check src/ tests/

format: ## Formater le code avec ruff
	ruff format src/ tests/
	ruff check --fix src/ tests/

run: ## Lancer l'émulateur
	python3 -m applesoft

clean: ## Nettoyer les fichiers générés
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
