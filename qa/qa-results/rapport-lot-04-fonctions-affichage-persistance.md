# Rapport QA — lot-04-fonctions-affichage-persistance

**Date :** 2026-04-10 (re-QA après correctif extension .bas)
**Lot :** lot-04-fonctions-affichage-persistance
**Verdict :** ✅ VALIDÉ

## Résumé

- Tests unitaires (dev) : 724/724 passés
- Scénarios QA : 50/50 passés
  - 🔴 Bloquants : 34/34 passés
  - 🟠 Majeurs : 13/13 passés
  - 🟡 Mineurs : 1/1 passé
- Revue de code : 3 constats (0 🔴, 1 🟠, 1 🟡) — corrections appliquées
- Itérations de développement : 1

## Corrections appliquées pendant la QA

| # | Constat | Correction | Fichier |
|---|---------|-----------|---------|
| R01 | `LEFT$("HI",-1)` ne levait pas d'erreur | Ajout `if n < 0: raise BasicError(53)` | interpreter.py:957 |
| R02 | `MID$("HELLO",2,-1)` ne levait pas d'erreur | Ajout `if length < 0: raise BasicError(53)` | interpreter.py:972 |

## Re-QA 2026-04-10 — correctif extension .bas (CA-UC-004-01, CA-UC-005-01)

4 scénarios ajoutés pour valider l'ajout automatique de l'extension `.bas` sur SAVE/LOAD :

| # | Scénario | Sévérité | Résultat |
|---|----------|----------|---------|
| T05-03 | SAVE "TEST" → TEST.bas | 🔴 | ✅ |
| T05-04 | SAVE "PROG.BAS" → pas de double extension | 🟠 | ✅ |
| T06-05 | LOAD "TEST" → charge TEST.bas | 🔴 | ✅ |
| T06-06 | SAVE "DEMO" + LOAD "DEMO" → roundtrip | 🔴 | ✅ |

## Scénarios en échec

Aucun — tous les scénarios passent après corrections.

## Points d'attention (🟡 mineurs)

- `LEFT$` et `RIGHT$` ne vérifient pas `n > 255`. Sans impact fonctionnel (chaînes max 255 chars) mais asymétrie avec `CHR$` qui valide ses bornes.

## Références

- Plan de test : `qa/plan-test/lot-04-fonctions-affichage-persistance.md`
- Revue de code : `qa/code-review/lot-04-fonctions-affichage-persistance-review.md`
- Plan du lot : `plan/lot-04-fonctions-affichage-persistance.md`
