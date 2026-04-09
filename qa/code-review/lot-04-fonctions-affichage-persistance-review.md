# Revue de code — lot-04-fonctions-affichage-persistance

**Date :** 2026-04-09
**Fichiers revus :** 3 (interpreter.py, io_cli.py, repl.py)

## Constats

| # | Fichier | Ligne | Axe | Sévérité | Constat | Recommandation |
|---|---------|-------|-----|----------|---------|----------------|
| R01 | src/applesoft/interpreter.py | 955-958 | Sécurité | 🔴 | `LEFT$("HI",-1)` retourne `"H"` au lieu de `?ILLEGAL QUANTITY ERROR` (exception UC-016 : `LEFT$("HI",-1) → ?ILLEGAL QUANTITY ERROR`). Python `s[:-1]` interprète silencieusement l'index négatif. | Ajouter `if n < 0: raise BasicError(53)` avant le slice |
| R02 | src/applesoft/interpreter.py | 963-971 | Sécurité | 🟠 | `MID$("HELLO",2,-1)` retourne silencieusement une chaîne vide au lieu de lever une erreur. Pas explicitement dans les exceptions SPEC mais comportement Applesoft attendu. | Ajouter validation `if length < 0: raise BasicError(53)` |
| R03 | src/applesoft/interpreter.py | 955-962 | Qualité | 🟡 | `LEFT$` et `RIGHT$` ne vérifient pas `n > 255`. Pas d'impact fonctionnel (slice sur chaîne max 255 chars) mais asymétrie avec `CHR$` qui valide ses bornes. | Optionnel : ajouter validation `n > 255` |

## Synthèse

- Conformité architecturale : ✅ — Composants dans les bons modules, interfaces respectées
- Sécurité : ⚠️ — 1 validation manquante (LEFT$ négatif), path traversal OK, file limits OK, pas d'eval/exec
- Qualité du code : ✅ — Code lisible, nommage cohérent, pas de duplication
- Tests : ✅ — Chaque CA-UC a au moins un test, nommage traçable
- Performance : ✅ — Pas de boucle coûteuse, ressources bien gérées
