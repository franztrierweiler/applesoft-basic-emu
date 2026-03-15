# EPIC 03 — Parser + AST

**Statut :** ⏳ Non démarré
**Priorité :** Critique
**Dépendances :** EPIC 02 (Lexer)
**Référence :** ARCHITECTURE.md § 4.1 (Parser) — GRAMMAR.md (toutes les productions)

## Objectif

Implémenter le parser par descente récursive qui transforme la liste de tokens en AST. Couvre toutes les productions de GRAMMAR.md : instructions, expressions avec précédence, structures de contrôle, fonctions.

## Tâches

| # | Tâche | Statut |
|---|-------|--------|
| 3.1 | Définir tous les nœuds AST dans `ast_nodes.py` (dataclasses) : Program, Line, Statement, Expression et sous-types | ⏳ |
| 3.2 | Implémenter le squelette du Parser (consommation de tokens, gestion d'erreurs syntaxiques) | ⏳ |
| 3.3 | Implémenter le parsing des expressions avec précédence (or → and → not → compare → add → mul → power → unary → primary) | ⏳ |
| 3.4 | Implémenter le parsing des expressions primaires (littéraux, variables, accès tableaux, appels de fonctions, parenthèses) | ⏳ |
| 3.5 | Implémenter le parsing des commandes système (RUN, LIST, NEW, DEL, SAVE, LOAD, CONT) | ⏳ |
| 3.6 | Implémenter le parsing des instructions d'E/S (PRINT, INPUT, GET, DATA, READ, RESTORE) | ⏳ |
| 3.7 | Implémenter le parsing des structures de contrôle (GOTO, GOSUB, RETURN, FOR/NEXT, IF/THEN/ELSE, ON GOTO/GOSUB, END, STOP, POP) | ⏳ |
| 3.8 | Implémenter le parsing des instructions d'affichage (HTAB, VTAB, HOME, NORMAL, INVERSE, FLASH, SPEED=, TEXT, REM) | ⏳ |
| 3.9 | Implémenter le parsing des instructions graphiques (GR, COLOR=, PLOT, HLIN, VLIN, HGR, HGR2, HCOLOR=, HPLOT, DRAW, XDRAW, ROT=, SCALE=) | ⏳ |
| 3.10 | Implémenter le parsing des instructions mémoire (PEEK, POKE, CALL) et fonctions spéciales (SCRN, POS, SPC, TAB) | ⏳ |
| 3.11 | Implémenter le parsing de l'assignation (LET optionnel) et de DIM | ⏳ |
| 3.12 | Implémenter le parsing de DEF FN et FN appel | ⏳ |
| 3.13 | Implémenter le parsing de ONERR GOTO et RESUME | ⏳ |
| 3.14 | Implémenter le parsing du séparateur `:` (multi-commandes) avec exception REM | ⏳ |
| 3.15 | Tests unitaires : un test par production de GRAMMAR.md + cas d'erreur syntaxique | ⏳ |

## Exigences couvertes

Le Parser couvre indirectement toutes les exigences fonctionnelles car il valide la syntaxe de chaque instruction. Les tests vérifient que le Parser produit l'AST correct pour chaque construction syntaxique définie dans GRAMMAR.md.

## Critères d'acceptation

| CA | Description | Statut |
|----|-------------|--------|
| CA-EPIC03-01 | Chaque production de GRAMMAR.md a un test qui vérifie l'AST produit | ⏳ |
| CA-EPIC03-02 | La précédence des opérateurs est correcte (tests ARCHITECTURE.md étape A.2) | ⏳ |
| CA-EPIC03-03 | Les erreurs de syntaxe produisent un message `?SYNTAX ERROR` (pas un crash Python) | ⏳ |
| CA-EPIC03-04 | Le séparateur `:` découpe correctement les multi-commandes, sauf après REM | ⏳ |
| CA-EPIC03-05 | `IF...THEN...ELSE` avec GOTO implicite et instructions multiples est correctement parsé | ⏳ |

## Livrables

- `src/ast_nodes.py` — tous les nœuds AST
- `src/parser.py` — parser descente récursive
- `tests/unit/test_parser.py` — tests exhaustifs
