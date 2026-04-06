# Revue de code — lot-01-infrastructure-pipeline

**Date :** 2026-04-06
**Fichiers revus :** 9

## Constats

| # | Fichier | Ligne | Axe | Sévérité | Constat | Recommandation |
|---|---------|-------|-----|----------|---------|----------------|
| R01 | src/applesoft/parser.py | — | Architecture | 🟠 Majeur | Module de 803 lignes (seuil ARCHITECTURE.md : 500) | Extraire les méthodes de parsing d'expressions ou de commandes dans un module dédié. À planifier pour un lot futur. |
| R02 | src/applesoft/repl.py | 22 | Architecture | 🟡 Mineur | Le type hint `IOBridgeCLI` est concret au lieu du Protocol `IOBridge` | Changer en `IOBridge | None` pour respecter le principe d'inversion de dépendance |
| R03 | src/applesoft/repl.py | 48 | Qualité | 🟡 Mineur | `except Exception:` trop large dans `_process_line` | Attraper les exceptions spécifiques du Lexer |
| R04 | src/applesoft/program.py | 120-121 | Qualité | 🟡 Mineur | Import lazy de `parser` et `ast_nodes` dans `collect_data()` | Acceptable pour éviter les imports circulaires — documenter la raison |
| R05 | src/applesoft/errors.py | 3 | Qualité | 🟡 Mineur | Docstring dit « 17 codes » mais 16 sont définis | Corriger le commentaire en « 16 codes » |

## Synthèse

- Conformité architecturale : ⚠️ (parser.py dépasse 500 lignes — R01)
- Sécurité : ✅ (pas d'eval/exec, pas d'import interdit, pas d'accès filesystem dans le cœur)
- Qualité du code : ✅ (modules bien structurés, nommage clair, duplication minimale)
- Tests : ✅ (chaque CA-UC a un test traçable, nommage conforme)
- Performance : ✅ (démarrage en 0.113s, pas de boucle coûteuse)
