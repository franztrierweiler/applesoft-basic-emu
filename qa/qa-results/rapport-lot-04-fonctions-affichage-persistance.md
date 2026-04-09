# Rapport QA — lot-04-fonctions-affichage-persistance

**Date :** 2026-04-09
**Lot :** lot-04-fonctions-affichage-persistance
**Verdict :** ✅ VALIDÉ

## Résumé

- Tests unitaires (dev) : 500/500 passés
- Scénarios QA : 46/46 passés
  - 🔴 Bloquants : 30/30 passés
  - 🟠 Majeurs : 12/12 passés
  - 🟡 Mineurs : 1/1 passé
- Revue de code : 3 constats (0 🔴, 1 🟠, 1 🟡) — corrections appliquées
- Itérations de développement : 1

## Corrections appliquées pendant la QA

| # | Constat | Correction | Fichier |
|---|---------|-----------|---------|
| R01 | `LEFT$("HI",-1)` ne levait pas d'erreur | Ajout `if n < 0: raise BasicError(53)` | interpreter.py:957 |
| R02 | `MID$("HELLO",2,-1)` ne levait pas d'erreur | Ajout `if length < 0: raise BasicError(53)` | interpreter.py:972 |

## Scénarios en échec

Aucun — tous les scénarios passent après corrections.

## Points d'attention (🟡 mineurs)

- `LEFT$` et `RIGHT$` ne vérifient pas `n > 255`. Sans impact fonctionnel (chaînes max 255 chars) mais asymétrie avec `CHR$` qui valide ses bornes.

## Références

- Plan de test : `qa/plan-test/lot-04-fonctions-affichage-persistance.md`
- Revue de code : `qa/code-review/lot-04-fonctions-affichage-persistance-review.md`
- Plan du lot : `plan/lot-04-fonctions-affichage-persistance.md`
