# Revue de code — lot-02-interpreteur-coeur

**Date :** 2026-04-06
**Fichiers revus :** 2 (interpreter.py, environment.py)

## Constats

| # | Fichier | Ligne | Axe | Sévérité | Constat | Recommandation |
|---|---------|-------|-----|----------|---------|----------------|
| R01 | interpreter.py | — | Architecture | 🟠 Majeur | Module de 693 lignes (seuil : 500). Combiné avec parser.py (803), deux modules dépassent le seuil. | Extraire les méthodes `_eval_*` dans un `evaluator.py`. À planifier pour un lot futur. |
| R02 | interpreter.py | 247, 298 | Qualité | 🟡 Mineur | Indices tableau convertis avec `int()` au lieu de `math.floor()`. Différence uniquement pour les flottants négatifs (cas rare). | Utiliser `math.floor()` pour les indices de tableau. |
| R03 | interpreter.py | 301-310 | Qualité | 🟡 Mineur | GOSUB/RETURN incomplets (commenté « lot 3 »). `push_gosub()` non appelé avant le saut. | Sera complété au lot 3. Acceptable en l'état. |
| R04 | interpreter.py | 312-324 | Qualité | 🟡 Mineur | FOR/NEXT incomplets (commenté « lot 3 »). Variables initialisées mais boucle non implémentée. | Sera complété au lot 3. Acceptable en l'état. |
| R05 | interpreter.py | 357-360 | Qualité | 🟡 Mineur | READ/INPUT convertissent silencieusement les erreurs numériques en 0. | Comportement conforme Applesoft, mais ajouter un commentaire expliquant ce choix. |

## Synthèse

- Conformité architecturale : ⚠️ (interpreter.py dépasse 500 lignes — R01)
- Sécurité : ✅ (pas d'eval/exec, IOBridge pour tout I/O, pas d'accès filesystem)
- Qualité du code : ✅ (dispatch visitor propre, séparation Environment/Interpreter, gestion d'erreurs Applesoft)
- Tests : ✅ (47 AC couverts + 59 scénarios QA, nommage traçable)
- Performance : ✅ (pas de boucle coûteuse, cache AST réutilisé)
