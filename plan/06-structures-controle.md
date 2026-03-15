# EPIC 06 — Structures de contrôle

**Statut :** ⏳ Non démarré
**Priorité :** Critique
**Dépendances :** EPIC 05 (REPL + Commandes)
**Référence :** ARCHITECTURE.md § 4.1 (Interpreter) — SPEC.md EXG-038 à EXG-044

## Objectif

Implémenter toutes les structures de contrôle de flux : GOTO, GOSUB/RETURN, FOR/NEXT, IF/THEN/ELSE, ON GOTO/GOSUB, END, STOP, POP. À la fin de cet EPIC, les programmes Applesoft avec boucles, branchements et sous-routines fonctionnent.

## Tâches

| # | Tâche | Statut |
|---|-------|--------|
| 6.1 | Implémenter GOTO (saut à une ligne) | ⏳ |
| 6.2 | Implémenter GOSUB/RETURN (pile GOSUB dans Environment) | ⏳ |
| 6.3 | Implémenter FOR/NEXT (pile FOR, STEP, test post-exécution, NEXT sans variable, NEXT multi-variable) | ⏳ |
| 6.4 | Implémenter IF/THEN/ELSE (GOTO implicite, multi-instructions, ELSE sur IF le plus récent) | ⏳ |
| 6.5 | Implémenter ON...GOTO et ON...GOSUB | ⏳ |
| 6.6 | Implémenter END (terminaison silencieuse) et STOP (BREAK IN linenum, CONT possible) | ⏳ |
| 6.7 | Implémenter POP (suppression adresse retour pile GOSUB) | ⏳ |
| 6.8 | Tests unitaires pour toutes les exigences couvertes | ⏳ |

## Exigences couvertes

| Exigence | Description | Statut tests |
|----------|-------------|-------------|
| EXG-038 | GOTO | ⏳ |
| EXG-039 | GOSUB / RETURN | ⏳ |
| EXG-040 | FOR / NEXT | ⏳ |
| EXG-041 | IF / THEN / ELSE | ⏳ |
| EXG-042 | ON...GOTO / ON...GOSUB | ⏳ |
| EXG-043 | END / STOP | ⏳ |
| EXG-044 | POP | ⏳ |

## Critères d'acceptation (extraits SPEC.md)

| CA | Description | Statut |
|----|-------------|--------|
| CA-038-01 | `GOTO 30` saute la ligne 20 | ⏳ |
| CA-039-01 | GOSUB/RETURN : `SUB` puis `BACK` | ⏳ |
| CA-039-02 | GOSUB imbriqué fonctionne | ⏳ |
| CA-040-01 | `FOR I=1 TO 3` → 1, 2, 3 | ⏳ |
| CA-040-02 | `FOR I=1 TO 10 STEP 3` → 1, 4, 7, 10 | ⏳ |
| CA-040-03 | `FOR I=5 TO 1 STEP -1` → 5, 4, 3, 2, 1 | ⏳ |
| CA-040-04 | NEXT multi-variable `NEXT J,I` | ⏳ |
| CA-041-01 | `IF X>3 THEN PRINT "YES"` | ⏳ |
| CA-041-02 | IF faux → bloc THEN complet sauté | ⏳ |
| CA-041-03 | IF/ELSE fonctionne | ⏳ |
| CA-041-04 | `IF X>3 THEN 100` (GOTO implicite) | ⏳ |
| CA-042-01 | `ON X GOTO 100,200,300` | ⏳ |
| CA-042-02 | `ON X GOSUB 100,200` | ⏳ |
| CA-043-01 | END termine silencieusement | ⏳ |
| CA-043-02 | STOP affiche BREAK + CONT fonctionne | ⏳ |
| CA-044-01 | POP + GOTO au lieu de RETURN | ⏳ |

## Cas limites à tester

| CL | Description | Statut |
|----|-------------|--------|
| CL-038-01 | `GOTO 999` inexistant → `?UNDEF'D STATEMENT ERROR` | ⏳ |
| CL-039-01 | `RETURN` sans GOSUB → `?RETURN WITHOUT GOSUB ERROR` | ⏳ |
| CL-040-01 | `FOR I=1 TO 0` → corps exécuté une fois (test post) | ⏳ |
| CL-040-02 | `NEXT J` pour boucle FOR I → `?NEXT WITHOUT FOR ERROR` | ⏳ |
| CL-040-03 | `FOR I=1 TO 3 STEP 0` → boucle infinie | ⏳ |
| CL-041-01 | `IF "HELLO" THEN...` → `?TYPE MISMATCH ERROR` | ⏳ |
| CL-041-02 | IF imbriqués sur une seule ligne | ⏳ |
| CL-042-01 | `ON 0 GOTO 100` → continue à l'instruction suivante | ⏳ |
| CL-042-03 | `ON -1 GOTO 100` → `?ILLEGAL QUANTITY ERROR` | ⏳ |
| CL-043-01 | END en mode direct → prompt sans erreur | ⏳ |
| CL-044-01 | POP pile vide → `?RETURN WITHOUT GOSUB ERROR` | ⏳ |

## Livrables

- `src/interpreter.py` — enrichi avec les structures de contrôle
- `src/environment.py` — enrichi avec les piles GOSUB et FOR
- `tests/unit/test_interpreter.py` — enrichi
- `tests/integration/test_programs.py` — programmes avec boucles et branchements
