# EPIC 04 — Interpreter noyau

**Statut :** ⏳ Non démarré
**Priorité :** Critique
**Dépendances :** EPIC 03 (Parser + AST)
**Référence :** ARCHITECTURE.md § 4.1 (Interpreter, Environment) — SPEC.md EXG-027 à EXG-033

## Objectif

Implémenter le cœur de l'Interpreter step-by-step : machine à états, évaluation des expressions (arithmétiques, comparaison, logiques), gestion des variables et tableaux, assignation. À la fin de cet EPIC, on peut exécuter `A = 2 + 3 * 4 : PRINT A` en mode direct.

## Tâches

| # | Tâche | Statut |
|---|-------|--------|
| 4.1 | Implémenter `Environment` : stockage variables (normalisées 2 chars + suffixe), reset, valeurs par défaut (0 / "") | ⏳ |
| 4.2 | Implémenter `Environment` : tableaux (DIM, accès, auto-dimension à 10) | ⏳ |
| 4.3 | Implémenter `ErrorTable` : mapping code → message, format `?XXX ERROR [IN linenum]` | ⏳ |
| 4.4 | Implémenter `NumberFormatter` : affichage Applesoft (9 chiffres, espace signe+, notation scientifique) | ⏳ |
| 4.5 | Implémenter `Interpreter` : squelette step-by-step (machine à états IDLE/RUNNING/WAITING/BREAK/DONE, méthode `step()`) | ⏳ |
| 4.6 | Implémenter l'évaluation des expressions arithmétiques (+, -, *, /, ^, unaire) avec précédence correcte | ⏳ |
| 4.7 | Implémenter l'évaluation des opérateurs de comparaison (=, <>, <, >, <=, >=, variantes) sur nombres et chaînes | ⏳ |
| 4.8 | Implémenter l'évaluation des opérateurs logiques (AND, OR, NOT) en mode bit-à-bit sur entiers 16 bits | ⏳ |
| 4.9 | Implémenter l'assignation (LET optionnel) pour variables scalaires et éléments de tableaux | ⏳ |
| 4.10 | Implémenter la concaténation de chaînes (+) et le type checking (TYPE MISMATCH) | ⏳ |
| 4.11 | Implémenter la conversion float → int16 pour les opérateurs logiques et les variables % | ⏳ |
| 4.12 | Implémenter `io_bridge.py` (interface abstraite) et un IOBridge minimal pour les tests (capture output) | ⏳ |
| 4.13 | Implémenter PRINT basique (sans formatage complet, juste output d'expressions) pour permettre les tests | ⏳ |
| 4.14 | Tests unitaires pour toutes les exigences couvertes | ⏳ |

## Exigences couvertes

| Exigence | Description | Statut tests |
|----------|-------------|-------------|
| EXG-027 | Types numériques (float, int16, affichage) | ⏳ |
| EXG-028 | Type chaîne (concaténation, limite 255, type mismatch) | ⏳ |
| EXG-029 | Assignation (LET optionnel) | ⏳ |
| EXG-030 | Tableaux (DIM, indices base 0, auto-dimension) | ⏳ |
| EXG-031 | Opérateurs arithmétiques et précédence | ⏳ |
| EXG-032 | Opérateurs de comparaison | ⏳ |
| EXG-033 | Opérateurs logiques (bit-à-bit) | ⏳ |

## Critères d'acceptation (extraits SPEC.md)

| CA | Description | Statut |
|----|-------------|--------|
| CA-027-01 | `PRINT 3.14` → ` 3.14` (espace signe+) | ⏳ |
| CA-027-02 | `X% = 7 : PRINT X%` → ` 7` | ⏳ |
| CA-027-03 | `PRINT 1000000000` → ` 1E+09` | ⏳ |
| CA-027-04 | `PRINT -5` → `-5` (pas d'espace) | ⏳ |
| CA-028-01 | `"HELLO" + " WORLD"` → `HELLO WORLD` | ⏳ |
| CA-029-01 | `LET A = 5 : PRINT A` → ` 5` | ⏳ |
| CA-029-02 | `A = 5 : PRINT A` → ` 5` (LET implicite) | ⏳ |
| CA-029-03 | `PRINT X` (non initialisé) → ` 0` | ⏳ |
| CA-030-01 | `DIM A(5) : A(3) = 42 : PRINT A(3)` → ` 42` | ⏳ |
| CA-030-02 | `DIM B(2,3) : B(1,2) = 7 : PRINT B(1,2)` → ` 7` | ⏳ |
| CA-031-01 | `PRINT 2 + 3 * 4` → ` 14` | ⏳ |
| CA-031-02 | `PRINT (2 + 3) * 4` → ` 20` | ⏳ |
| CA-031-03 | `PRINT 2 ^ 3 ^ 2` → ` 512` (associativité droite) | ⏳ |
| CA-031-04 | `PRINT 10 - 3 - 2` → ` 5` (associativité gauche) | ⏳ |
| CA-032-01 | `PRINT 5 > 3` → ` 1` | ⏳ |
| CA-032-03 | `PRINT "B" > "A"` → ` 1` | ⏳ |
| CA-033-01 | `PRINT 1 AND 0` → ` 0` | ⏳ |
| CA-033-05 | `PRINT 12 AND 10` → ` 8` (bit-à-bit) | ⏳ |

## Cas limites à tester

| CL | Description | Statut |
|----|-------------|--------|
| CL-027-01 | `X% = 32768` → `?ILLEGAL QUANTITY ERROR` | ⏳ |
| CL-027-02 | `X% = 3.7` → tronqué à 3 | ⏳ |
| CL-028-01 | Chaîne > 255 chars → `?STRING TOO LONG ERROR` | ⏳ |
| CL-028-02 | `A$ = 5` → `?TYPE MISMATCH ERROR` | ⏳ |
| CL-030-01 | `A(11)` sans DIM → `?BAD SUBSCRIPT ERROR` | ⏳ |
| CL-030-02 | DIM deux fois → `?REDIM'D ARRAY ERROR` | ⏳ |
| CL-031-01 | `1/0` → `?DIVISION BY ZERO ERROR` | ⏳ |
| CL-031-02 | `0^0` → `1` | ⏳ |
| CL-031-03 | `-2^2` → `4` (unaire prioritaire) | ⏳ |
| CL-032-02 | `5 > "A"` → `?TYPE MISMATCH ERROR` | ⏳ |
| CL-033-02 | `3.7 AND 2.1` → `2` (conversion int avant bit-à-bit) | ⏳ |

## Livrables

- `src/environment.py` — état d'exécution
- `src/interpreter.py` — interpreter step-by-step (noyau)
- `src/number_formatter.py` — formatage nombres Applesoft
- `src/error_table.py` — table d'erreurs
- `src/io_bridge.py` — interface abstraite IOBridge
- `tests/unit/test_interpreter.py`, `test_environment.py`, `test_number_formatter.py`, `test_error_table.py`
