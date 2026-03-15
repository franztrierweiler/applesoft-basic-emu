# EPIC 08 — Fonctions

**Statut :** ⏳ Non démarré
**Priorité :** Critique
**Dépendances :** EPIC 04 (Interpreter noyau)
**Référence :** ARCHITECTURE.md § 4.1 (Interpreter) — SPEC.md EXG-034 à EXG-037

## Objectif

Implémenter toutes les fonctions intégrées (mathématiques, chaînes, conversion) et les fonctions utilisateur (DEF FN). À la fin de cet EPIC, `PRINT SIN(3.14)`, `PRINT LEFT$("HELLO",3)` et `FN DOUBLE(5)` fonctionnent.

## Tâches

| # | Tâche | Statut |
|---|-------|--------|
| 8.1 | Implémenter les fonctions mathématiques : ABS, INT, SGN, SQR, LOG, EXP, SIN, COS, TAN, ATN | ⏳ |
| 8.2 | Implémenter RND (n>0 : aléatoire, n=0 : dernier, n<0 : graine déterministe) | ⏳ |
| 8.3 | Implémenter les fonctions de chaîne : LEN, LEFT$, RIGHT$, MID$, ASC, CHR$ | ⏳ |
| 8.4 | Implémenter les fonctions de conversion : STR$, VAL | ⏳ |
| 8.5 | Implémenter DEF FN (définition de fonction utilisateur à un paramètre) | ⏳ |
| 8.6 | Implémenter FN appel (appel de fonction utilisateur, accès variables globales) | ⏳ |
| 8.7 | Tests unitaires pour toutes les exigences couvertes | ⏳ |

## Exigences couvertes

| Exigence | Description | Statut tests |
|----------|-------------|-------------|
| EXG-034 | Fonctions mathématiques | ⏳ |
| EXG-035 | Fonction RND | ⏳ |
| EXG-036 | Fonctions de chaînes et conversion | ⏳ |
| EXG-037 | DEF FN / FN appel | ⏳ |

## Critères d'acceptation (extraits SPEC.md)

| CA | Description | Statut |
|----|-------------|--------|
| CA-034-01 | `ABS(-5)` → 5 | ⏳ |
| CA-034-02 | `INT(3.7)` → 3 | ⏳ |
| CA-034-03 | `INT(-3.7)` → -4 (floor, pas troncature) | ⏳ |
| CA-034-04 | `SQR(16)` → 4 | ⏳ |
| CA-034-05 | `SGN(-42)` → -1 | ⏳ |
| CA-035-01 | `RND(1)` → valeur entre 0 et 1 | ⏳ |
| CA-035-02 | `RND(-5)` → séquence déterministe | ⏳ |
| CA-035-03 | `RND(0)` → répète dernière valeur | ⏳ |
| CA-036-01 | `LEN("HELLO")` → 5 | ⏳ |
| CA-036-02 | `LEFT$("HELLO",3)` → `HEL` | ⏳ |
| CA-036-03 | `RIGHT$("HELLO",3)` → `LLO` | ⏳ |
| CA-036-04 | `MID$("HELLO",2,3)` → `ELL` | ⏳ |
| CA-036-05 | `ASC("A")` → 65 | ⏳ |
| CA-036-06 | `CHR$(65)` → `A` | ⏳ |
| CA-036-07 | `VAL("3.14")` → 3.14 | ⏳ |
| CA-036-08 | `STR$(42)` → `" 42"` | ⏳ |
| CA-037-01 | `DEF FN DOUBLE(X) = X * 2` + `FN DOUBLE(5)` → 10 | ⏳ |
| CA-037-02 | Fonction accède aux variables globales | ⏳ |

## Cas limites à tester

| CL | Description | Statut |
|----|-------------|--------|
| CL-034-01 | `SQR(-1)` → `?ILLEGAL QUANTITY ERROR` | ⏳ |
| CL-034-02 | `LOG(0)` → `?ILLEGAL QUANTITY ERROR` | ⏳ |
| CL-036-01 | `ASC("")` → `?ILLEGAL QUANTITY ERROR` | ⏳ |
| CL-036-02 | `CHR$(256)` → `?ILLEGAL QUANTITY ERROR` | ⏳ |
| CL-036-03 | `MID$("AB",5,1)` → chaîne vide | ⏳ |
| CL-036-04 | `VAL("HELLO")` → 0 | ⏳ |
| CL-036-05 | `VAL("3ABC")` → 3 | ⏳ |
| CL-036-06 | `LEFT$("HI",-1)` → `?ILLEGAL QUANTITY ERROR` | ⏳ |
| CL-037-01 | `FN DOUBLE(5)` sans DEF → `?UNDEF'D FUNCTION ERROR` | ⏳ |

## Livrables

- `src/interpreter.py` — enrichi avec les fonctions
- `tests/unit/test_interpreter.py` — enrichi (fonctions)
