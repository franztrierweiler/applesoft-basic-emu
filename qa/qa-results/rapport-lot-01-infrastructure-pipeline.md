# Rapport QA — lot-01-infrastructure-pipeline

**Date :** 2026-04-06
**Lot :** lot-01-infrastructure-pipeline
**Verdict :** ✅ VALIDÉ

## Résumé

- Tests unitaires (dev) : 114/114 passés
- Scénarios QA : 47/47 passés
  - 🔴 Bloquants : 27/27 passés
  - 🟠 Majeurs : 12/12 passés
  - 🟡 Mineurs : 6/6 passés
  - TM-01 (manuel) : ✅ démarrage en 0.113s (seuil : 1s)
- Revue de code : 5 constats (0 🔴, 1 🟠, 4 🟡)
- Itérations de développement : 2

## Scénarios en échec

Aucun.

## Constats de revue de code à corriger

| # | Fichier:ligne | Axe | Sévérité | Constat |
|---|--------------|-----|----------|---------|
| R01 | src/applesoft/parser.py | Architecture | 🟠 | Module de 803 lignes (seuil : 500). À refactorer dans un lot futur. |

## Points d'attention (🟡 mineurs)

- R02 : `repl.py` utilise le type concret `IOBridgeCLI` au lieu du Protocol `IOBridge`
- R03 : `repl.py` utilise `except Exception` trop large
- R04 : Import lazy dans `program.py:collect_data()` — acceptable, à documenter
- R05 : Docstring `errors.py` indique « 17 codes » au lieu de 16

## Références

- Plan de test : `qa/plan-test/lot-01-infrastructure-pipeline.md`
- Revue de code : `qa/code-review/lot-01-infrastructure-pipeline-review.md`
- Plan du lot : `plan/lot-01-infrastructure-pipeline.md`
