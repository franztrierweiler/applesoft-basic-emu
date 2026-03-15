# EPIC 09 — Gestion d'erreurs

**Statut :** ⏳ Non démarré
**Priorité :** Important
**Dépendances :** EPIC 06 (Structures de contrôle)
**Référence :** ARCHITECTURE.md § 4.1 (Interpreter) — SPEC.md EXG-045, EXG-046, EXG-047, EXG-065

## Objectif

Implémenter la gestion complète des erreurs : messages d'erreur Applesoft fidèles, ONERR GOTO / RESUME, interruption Ctrl+C. À la fin de cet EPIC, les programmes utilisant des gestionnaires d'erreurs fonctionnent et Ctrl+C interrompt proprement l'exécution.

## Tâches

| # | Tâche | Statut |
|---|-------|--------|
| 9.1 | Compléter `ErrorTable` avec tous les codes et messages (table EXG-065) | ⏳ |
| 9.2 | Implémenter le format d'affichage `?XXX ERROR IN linenum` (mode programme) et `?XXX ERROR` (mode direct) | ⏳ |
| 9.3 | Implémenter ONERR GOTO linenum (installation du handler dans Environment) | ⏳ |
| 9.4 | Implémenter ONERR GOTO 0 (désactivation du handler) | ⏳ |
| 9.5 | Implémenter le routage des erreurs runtime vers le handler ONERR (sauvegarde code dans PEEK(222), ligne dans PEEK(218-219)) | ⏳ |
| 9.6 | Implémenter RESUME (reprise à l'instruction fautive) | ⏳ |
| 9.7 | Implémenter la protection contre boucle infinie dans le handler d'erreur | ⏳ |
| 9.8 | Implémenter Ctrl+C : flag d'interruption vérifié à chaque `step()`, message BREAK IN linenum, CONT possible | ⏳ |
| 9.9 | Implémenter Ctrl+C pendant INPUT/GET (annulation de l'entrée) | ⏳ |
| 9.10 | Tests unitaires pour toutes les exigences couvertes | ⏳ |

## Exigences couvertes

| Exigence | Description | Statut tests |
|----------|-------------|-------------|
| EXG-045 | Interruption Ctrl+C | ⏳ |
| EXG-046 | ONERR GOTO | ⏳ |
| EXG-047 | RESUME | ⏳ |
| EXG-065 | Messages d'erreur Applesoft | ⏳ |

## Critères d'acceptation (extraits SPEC.md)

| CA | Description | Statut |
|----|-------------|--------|
| CA-045-01 | Boucle infinie + Ctrl+C → `BREAK IN 10` + prompt | ⏳ |
| CA-045-02 | Ctrl+C + CONT → reprise | ⏳ |
| CA-046-01 | `ONERR GOTO 100` + `1/0` → handler exécuté, `PEEK(222)` = 133 | ⏳ |
| CA-046-02 | `ONERR GOTO 0` désactive le handler | ⏳ |
| CA-047-01 | RESUME reprend à l'instruction fautive | ⏳ |
| CA-065-01 | `10 X=1/0` + RUN → `?DIVISION BY ZERO ERROR IN 10` | ⏳ |
| CA-065-02 | `X=1/0` en mode direct → `?DIVISION BY ZERO ERROR` (sans numéro) | ⏳ |
| CA-065-03 | ONERR + PEEK(222) → code correspondant au message | ⏳ |

## Cas limites à tester

| CL | Description | Statut |
|----|-------------|--------|
| CL-045-01 | Ctrl+C pendant INPUT/GET → annulation + BREAK | ⏳ |
| CL-046-01 | `ONERR GOTO 999` (ligne inexistante) → erreur au moment du routage | ⏳ |
| CL-046-02 | Erreur dans le handler lui-même → pas de boucle infinie, affichage erreur + prompt | ⏳ |
| CL-047-01 | RESUME sans ONERR actif → `?SYNTAX ERROR` + prompt | ⏳ |
| CL-065-01 | Erreur dans multi-commande → numéro de la ligne entière | ⏳ |

## Livrables

- `src/error_table.py` — complété
- `src/interpreter.py` — enrichi (ONERR, RESUME, Ctrl+C)
- `src/environment.py` — enrichi (error state)
- `tests/unit/test_interpreter.py` — enrichi (erreurs)
