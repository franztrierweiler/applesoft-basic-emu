.PHONY: help install test lint format run web clean

help:
	@echo "Commandes disponibles :"
	@echo ""
	@echo "  Développement :"
	@echo "    make install   Installe le projet et les dépendances dev (pip install -e \".[dev,png]\")"
	@echo "    make test      Lance les tests unitaires (pytest tests/ -v)"
	@echo "    make lint      Vérifie le code (ruff check + ruff format --check)"
	@echo "    make format    Formate le code (ruff format + ruff check --fix)"
	@echo ""
	@echo "  Exécution :"
	@echo "    make run       Lance l'émulateur en mode CLI (python3 -m applesoft)"
	@echo "    make web       Lance l'émulateur web sur http://localhost:8000"
	@echo ""
	@echo "  Maintenance :"
	@echo "    make help      Affiche cette aide"
	@echo "    make clean     Nettoie les caches (__pycache__, .pytest_cache, *.pyc)"

install:
	pip install -e ".[dev,png]"

test:
	python3 -m pytest tests/ -v

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

format:
	ruff format src/ tests/
	ruff check --fix src/ tests/

run:
	python3 -m applesoft

web:
	@test -L web/applesoft || ln -sf ../src/applesoft web/applesoft
	python3 -m http.server 8000 --directory web/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
