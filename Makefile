SHELL := /bin/bash

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
	@logfile=$$(mktemp); \
	python3 -m pytest tests/ -v 2>&1 | tee "$$logfile"; \
	rc=$${PIPESTATUS[0]}; \
	echo ""; \
	echo "════════════════════════════════════════════════════════════════"; \
	echo "  BILAN GLOBAL DES TESTS"; \
	echo "════════════════════════════════════════════════════════════════"; \
	for cat in unit qa integration; do \
	  if [ -d "tests/$$cat" ]; then \
	    pass=$$(grep -E "^tests/$$cat/.*\bPASSED\b" "$$logfile" 2>/dev/null | wc -l); \
	    fail=$$(grep -E "^tests/$$cat/.*\bFAILED\b" "$$logfile" 2>/dev/null | wc -l); \
	    skip=$$(grep -E "^tests/$$cat/.*\bSKIPPED\b" "$$logfile" 2>/dev/null | wc -l); \
	    total=$$((pass + fail + skip)); \
	    if [ $$total -gt 0 ]; then \
	      printf "  %-13s : %4d ✓ réussis · %3d ✗ échoués · %3d ⊘ ignorés · %4d total\n" "$$cat" $$pass $$fail $$skip $$total; \
	    fi; \
	  fi; \
	done; \
	tp=$$(grep -E "^tests/.*\bPASSED\b" "$$logfile" 2>/dev/null | wc -l); \
	tf=$$(grep -E "^tests/.*\bFAILED\b" "$$logfile" 2>/dev/null | wc -l); \
	ts=$$(grep -E "^tests/.*\bSKIPPED\b" "$$logfile" 2>/dev/null | wc -l); \
	tt=$$((tp + tf + ts)); \
	echo "────────────────────────────────────────────────────────────────"; \
	printf "  %-13s : %4d ✓ réussis · %3d ✗ échoués · %3d ⊘ ignorés · %4d total\n" "Total" $$tp $$tf $$ts $$tt; \
	echo "════════════════════════════════════════════════════════════════"; \
	if [ $$rc -eq 0 ]; then \
	  echo "  ✅ Tous les tests passent"; \
	else \
	  echo "  ❌ Échec : $$tf test(s) en erreur (code $$rc)"; \
	fi; \
	echo "════════════════════════════════════════════════════════════════"; \
	rm -f "$$logfile"; \
	exit $$rc

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
