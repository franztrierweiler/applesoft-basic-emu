# Plan de test — EPIC 01 Infrastructure

## Scénarios de test

### CA-EPIC01-01 : Installation

| # | Scénario | Type | Vérification |
|---|----------|------|-------------|
| T01-01 | `make install` installe le package et les dépendances dev | Nominal | Commande sort sans erreur, pytest/ruff/mypy disponibles |
| T01-02 | `python3 -c "import src"` fonctionne après install | Nominal | Pas d'ImportError |

### CA-EPIC01-02 : Tests

| # | Scénario | Type | Vérification |
|---|----------|------|-------------|
| T02-01 | `make test` exécute pytest et collecte au moins 1 test | Nominal | Exit code 0, "passed" dans la sortie |
| T02-02 | `make test-cov` affiche le rapport de couverture | Nominal | Exit code 0, tableau de couverture affiché |

### CA-EPIC01-03 : Lint

| # | Scénario | Type | Vérification |
|---|----------|------|-------------|
| T03-01 | `ruff check src/ tests/` passe sans erreur | Nominal | "All checks passed" |
| T03-02 | `mypy src/` passe sans erreur sur les 18 stubs | Nominal | "no issues found in 18 source files" |

### CA-EPIC01-04 : CI GitHub Actions

| # | Scénario | Type | Vérification |
|---|----------|------|-------------|
| T04-01 | Le workflow CI s'exécute au push sur main | Manuel | Onglet Actions GitHub → check vert |

### Vérifications structurelles

| # | Scénario | Type | Vérification |
|---|----------|------|-------------|
| T05-01 | Les 17 stubs Python existent dans `src/` | Structurel | 18 fichiers .py (17 modules + __init__.py) |
| T05-02 | La structure correspond à ARCHITECTURE.md § 5 | Structurel | Répertoires src/, tests/unit/, tests/integration/, web/, examples/, qa/ existent |
| T05-03 | La fixture `mock_io` est disponible dans les tests | Structurel | conftest.py contient la fixture, utilisable par pytest |
| T05-04 | Le Makefile expose les cibles documentées | Structurel | `make help` liste help, install, test, lint, run, clean |
| T05-05 | `.gitignore` exclut les artefacts de build | Structurel | __pycache__, *.egg-info, .mypy_cache présents dans .gitignore |
| T05-06 | Pas de résidu Docker dans le projet | Structurel | Pas de Dockerfile, pas de cible docker-* dans le Makefile |
