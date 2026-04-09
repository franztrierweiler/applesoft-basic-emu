# Revue de code — lot-03-controle-flux-entrees

**Date :** 2026-04-06
**Fichiers revus :** 3 (interpreter.py, lexer.py, parser.py — deltas lot 3)

## Constats

| # | Fichier | Ligne | Axe | Sévérité | Constat | Recommandation |
|---|---------|-------|-----|----------|---------|----------------|
| R01 | interpreter.py | — | Architecture | 🟠 Majeur | Module à ~750 lignes (seuil 500). L'ajout des signaux GosubSignal/ReturnSignal/NextLoopSignal et des méthodes FOR/NEXT/GOSUB augmente encore la taille. | Extraire les signaux et l'évaluateur dans des modules séparés. |
| R02 | lexer.py | 68 | Qualité | 🟡 Mineur | Ajout de ELSE aux keywords — correction justifiée, documentée dans GRAMMAR.md. | Rien à changer. |
| R03 | parser.py | 231-235 | Qualité | 🟡 Mineur | Condition d'arrêt PRINT ajoutant `ELSE` — fonctionne mais pourrait bénéficier d'une liste extensible de stop-keywords. | Acceptable en l'état. |

## Synthèse

- Conformité architecturale : ⚠️ (interpreter.py > 500 lignes — R01, déjà noté lot 2)
- Sécurité : ✅ (pas d'eval/exec, signaux via exceptions typées, pas de désérialisation)
- Qualité du code : ✅ (signaux bien typés, pile FOR/GOSUB propre, séparation claire)
- Tests : ✅ (22 AC + 34 scénarios QA, nommage traçable)
- Performance : ✅ (boucle 10000 en < 2s, pas de récursion Python pour les boucles BASIC)
