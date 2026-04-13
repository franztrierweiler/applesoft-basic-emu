# Rapport QA — lot-07-interface-web

**Date :** 2026-04-10
**Lot :** lot-07-interface-web
**Verdict :** ✅ VALIDÉ

## Résumé

- Tests unitaires (dev) : 719/719 passés
- Scénarios QA : 40/40 passés
  - 🔴 Bloquants : 19/19 passés
  - 🟠 Majeurs : 13/13 passés
  - 🟡 Mineurs : 8/8 passés
- Revue de code : 5 constats (0 🔴, 1 🟠, 4 🟡)
- Itérations de développement : 5

## Scénarios en échec

Aucun.

## Constats de revue de code à corriger

| # | Fichier:ligne | Axe | Sévérité | Constat |
|---|--------------|-----|----------|---------|
| R01 | web/io_web.py:1-837 | Qualité | 🟠 | Fichier de 837 lignes — dépasse le seuil de 500 lignes recommandé. Bien structuré mais à découper dans une itération future. |

## Points d'attention (🟡 mineurs)

- R02 : `_match_keyword` itère sur tous les mots-clés — optimisation possible avec un trie
- R03 : `import json` répété dans chaque méthode de persistance — déplacer en tête
- R04 : `__init__` avec 13 attributs — surveiller la croissance
- R05 : `_bind_toolbar` à 60 lignes — extraire les handlers en méthodes

## Références

- Plan de test : `qa/plan-test/lot-07-interface-web.md`
- Revue de code : `qa/code-review/lot-07-interface-web-review.md`
- Plan du lot : `plan/lot-07-interface-web.md`
