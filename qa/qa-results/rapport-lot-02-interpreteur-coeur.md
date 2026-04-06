# Rapport QA — lot-02-interpreteur-coeur

**Date :** 2026-04-06
**Lot :** lot-02-interpreteur-coeur
**Verdict :** ✅ VALIDÉ

## Résumé

- Tests unitaires (dev) : 178/178 passés
- Scénarios QA : 59/59 passés
  - 🔴 Bloquants : 35/35 passés
  - 🟠 Majeurs : 15/15 passés
  - 🟡 Mineurs : 0/0
- Revue de code : 5 constats (0 🔴, 1 🟠, 4 🟡)
- Itérations de développement : 2

## Scénarios en échec

Aucun.

## Constats de revue de code à corriger

| # | Fichier:ligne | Axe | Sévérité | Constat |
|---|--------------|-----|----------|---------|
| R01 | interpreter.py | Architecture | 🟠 | Module de 693 lignes (seuil : 500). À refactorer dans un lot futur. |

## Points d'attention (🟡 mineurs)

- R02 : Indices tableau convertis avec `int()` au lieu de `math.floor()` — impact uniquement sur flottants négatifs (cas extrême)
- R03 : GOSUB/RETURN incomplets — déféré au lot 3
- R04 : FOR/NEXT incomplets — déféré au lot 3
- R05 : READ/INPUT silencieux sur erreurs numériques — conforme Applesoft, documenter

## Références

- Plan de test : `qa/plan-test/lot-02-interpreteur-coeur.md`
- Revue de code : `qa/code-review/lot-02-interpreteur-coeur-review.md`
- Plan du lot : `plan/lot-02-interpreteur-coeur.md`
