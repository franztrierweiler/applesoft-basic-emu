# EPIC 01 — Infrastructure

**Statut :** ⏳ Non démarré
**Priorité :** Critique (prérequis de tous les EPICs)
**Dépendances :** Aucune
**Référence :** ARCHITECTURE.md § 3, § 5 — DEPLOYMENT.md § 4, § 6

## Objectif

Mettre en place la structure du projet, l'outillage de développement et le pipeline CI/CD. À la fin de cet EPIC, un développeur (ou agent IA) peut cloner le dépôt, installer les dépendances dev, lancer les tests (vides) et le linter sans erreur.

## Tâches

| # | Tâche | Statut |
|---|-------|--------|
| 1.1 | Créer la structure de répertoires (`src/`, `tests/unit/`, `tests/integration/`, `web/`, `examples/`, `plan/`, `qa/`) | ⏳ |
| 1.2 | Créer `pyproject.toml` (métadonnées projet, dépendances dev : pytest, ruff, mypy, pytest-cov) | ⏳ |
| 1.3 | Créer `src/__init__.py` et les fichiers Python vides pour chaque module (stubs) | ⏳ |
| 1.4 | Créer le `Makefile` avec les cibles : `help`, `install`, `test`, `lint`, `run`, `docker-build`, `docker-run`, `web-build`, `web-serve`, `clean` | ⏳ |
| 1.5 | Créer le `Dockerfile` (Python slim, install dev, entrypoint REPL) | ⏳ |
| 1.6 | Créer le workflow GitHub Actions (`.github/workflows/ci.yml`) : lint + tests sur push/PR | ⏳ |
| 1.7 | Configurer ruff (`ruff.toml` ou section `pyproject.toml`) et mypy | ⏳ |
| 1.8 | Créer `tests/conftest.py` avec fixtures de base (IOBridge mock) | ⏳ |
| 1.9 | Vérifier que `make install && make lint && make test` passent sans erreur | ⏳ |

## Critères d'acceptation

| CA | Description | Statut |
|----|-------------|--------|
| CA-EPIC01-01 | `git clone` + `make install` fonctionne sur Python 3.10+ | ⏳ |
| CA-EPIC01-02 | `make test` exécute pytest sans erreur (0 tests, 0 échecs) | ⏳ |
| CA-EPIC01-03 | `make lint` exécute ruff + mypy sans erreur | ⏳ |
| CA-EPIC01-04 | `make docker-build` construit une image Docker fonctionnelle | ⏳ |
| CA-EPIC01-05 | Le workflow CI GitHub Actions passe au vert | ⏳ |

## Livrables

- Structure de répertoires conforme à ARCHITECTURE.md § 5
- `pyproject.toml`, `Makefile`, `Dockerfile`, `.github/workflows/ci.yml`
- Stubs Python pour tous les modules de `src/`
- `tests/conftest.py` avec IOBridge mock
