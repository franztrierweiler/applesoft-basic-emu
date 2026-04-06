# Lot 2 — Interpréteur cœur : variables, expressions, affichage

## Objectif

Rendre l'émulateur capable d'exécuter des programmes BASIC simples. L'Interpreter parcourt l'AST et exécute les instructions. L'Environment gère les variables et les tableaux. PRINT affiche des résultats. RUN lance un programme, CONT reprend après STOP/END. Après ce lot : `10 X=5 : PRINT X*2` fonctionne.

## UC couverts

| UC | Intitulé | Priorité |
|---|---|---|
| UC-003 | Exécuter un programme | Critique |
| UC-006 | Afficher des données | Critique |
| UC-010 | Assigner et manipuler des variables | Critique |
| UC-011 | Évaluer des expressions | Critique |

## Composants impactés

| Composant | Rôle dans ce lot |
|---|---|
| Interpreter (`interpreter.py`) | Création : parcours de l'AST, exécution des instructions (PRINT, LET, DIM, END, STOP, REM), évaluation des expressions (9 niveaux de précédence), compteur d'instructions (suspendabilité). |
| Environment (`environment.py`) | Création : variables (get/set avec règle 2 chars — RG-0003), tableaux (DIM, auto-dimensionnement), types numériques (RG-0006) et chaîne (RG-0007), état CONT. |
| NumberFormatter (`formatter.py`) | Utilisé par PRINT pour le formatage des nombres (RG-0006). |
| REPL (`repl.py`) | Extension : commandes RUN et CONT, exécution mode direct via l'Interpreter. |

## Dépendances

- Lot 1 (Lexer, Parser, Program, ErrorHandler, IOBridge, REPL de base)

## Fonctionnalités

### F1 — Environment (état d'exécution)

Gestion de l'état d'exécution :
- Variables : stockage par nom normalisé (2 chars + suffixe), valeurs par défaut (0 pour numériques, "" pour chaînes)
- Tableaux : DIM avec dimensions multiples, indices base 0, auto-dimensionnement à 10
- Types : flottant (IEEE 754 double), entier 16 bits (suffixe %), chaîne (suffixe $, max 255 chars)
- État CONT : sauvegarde du point de reprise après STOP/END

### F2 — Interpreter (exécution)

Parcours de l'AST et exécution :
- Instructions : LET (implicite), DIM, PRINT, END, STOP, REM (no-op)
- Multi-commandes via `:` (RG-0008)
- REM ignore tout jusqu'en fin de ligne (RG-0009)
- Compteur d'instructions pour la suspendabilité (ADR-003)
- Gestion des erreurs : traduction des exceptions Python en erreurs Applesoft (RG-0010)

### F3 — Évaluation des expressions (UC-011)

9 niveaux de précédence implémentés dans l'Interpreter :
- Unaire +/- (précédence la plus forte)
- Exponentiation ^ (associativité droite)
- Multiplication / Division
- Addition / Soustraction
- Comparaisons (=, <>, <, >, <=, >=, et variantes)
- NOT (unaire)
- AND (bit à bit sur entiers)
- OR (bit à bit sur entiers)
- Parenthèses
- Conventions : 0^0=1, -2^2=4 (unaire plus prioritaire que ^)

### F4 — PRINT (UC-006)

Affichage complet :
- Séparateur `;` (concaténation)
- Séparateur `,` (tabulation 16 colonnes)
- `;` en fin = pas de retour à la ligne
- PRINT seul = ligne vide
- `?` alias de PRINT
- SPC(n) et TAB(n)
- POS(0) retourne la colonne courante
- Formatage des nombres via NumberFormatter (RG-0006)

### F5 — RUN et CONT (UC-003)

- RUN : réinitialise l'Environment, exécute depuis la première ligne (ou ligne spécifiée)
- RUN sans programme : retour prompt
- STOP : affiche `BREAK IN linenum`, sauve l'état CONT
- END : terminaison, sauve l'état CONT
- CONT : reprend à l'instruction suivant le point d'arrêt
- CONT sans arrêt : `?CAN'T CONTINUE ERROR`
- CONT après modification du programme : `?CAN'T CONTINUE ERROR`

## Critères d'acceptation

| AC | Description | Statut | Justification | Date |
|---|---|---|---|---|
| CA-UC-003-01 | `10 PRINT "A"` / `20 PRINT "B"` + RUN → `A` puis `B` | ✅ | test_ca_uc_003_01_sequential | 2026-04-06 |
| CA-UC-003-02 | `RUN 20` → seul `B` affiché | ✅ | test_ca_uc_003_02_run_from_line | 2026-04-06 |
| CA-UC-003-03 | `10 X=5` / `20 PRINT X` + RUN → `5` | ✅ | test_ca_uc_003_03_variable | 2026-04-06 |
| CA-UC-003-04 | `10 PRINT "A" : END : PRINT "B"` + RUN → seul `A` | ✅ | test_ca_uc_003_04_end | 2026-04-06 |
| CA-UC-003-05 | STOP + CONT → reprend après STOP | ✅ | test_ca_uc_003_05_stop_cont | 2026-04-06 |
| CA-UC-003-06 | STOP + modification variable en direct + CONT → variable modifiée conservée | ✅ | test_ca_uc_003_06_stop_modify_cont | 2026-04-06 |
| CA-UC-006-01 | `PRINT "HELLO"` → `HELLO` + retour ligne | ✅ | test_ca_uc_006_01_print_string | 2026-04-06 |
| CA-UC-006-02 | `PRINT "A";"B"` → `AB` | ✅ | test_ca_uc_006_02_semicolon | 2026-04-06 |
| CA-UC-006-03 | `PRINT "A","B"` → `A` + espaces jusqu'à colonne 16 + `B` | ✅ | test_ca_uc_006_03_comma | 2026-04-06 |
| CA-UC-006-04 | `PRINT "A";` / `PRINT "B"` → `AB` sur une ligne | ✅ | test_ca_uc_006_04_trailing_semicolon | 2026-04-06 |
| CA-UC-006-05 | `PRINT` seul → ligne vide | ✅ | test_ca_uc_006_05_print_empty | 2026-04-06 |
| CA-UC-006-06 | `? "HELLO"` → `HELLO` | ✅ | test_ca_uc_006_06_question_mark | 2026-04-06 |
| CA-UC-006-07 | `PRINT SPC(5);"X"` → 5 espaces + `X` | ✅ | test_ca_uc_006_07_spc | 2026-04-06 |
| CA-UC-006-08 | `PRINT TAB(10);"X"` → `X` en colonne 10 | ✅ | test_ca_uc_006_08_tab | 2026-04-06 |
| CA-UC-006-09 | TAB avec curseur au-delà → passe à la ligne suivante | ✅ | test_ca_uc_006_09_tab_beyond_cursor | 2026-04-06 |
| CA-UC-006-10 | POS(0) retourne la colonne courante | ✅ | test_ca_uc_006_10_pos | 2026-04-06 |
| CA-UC-010-01 | `LET A = 5 : PRINT A` → `5` | ✅ | test_ca_uc_010_01_let_explicit | 2026-04-06 |
| CA-UC-010-02 | `A = 5 : PRINT A` → `5` (LET implicite) | ✅ | test_ca_uc_010_02_let_implicit | 2026-04-06 |
| CA-UC-010-03 | `PRINT X` (non initialisée) → `0` | ✅ | test_ca_uc_010_03_uninitialized | 2026-04-06 |
| CA-UC-010-04 | `DIM A(5)` / `A(3)=42` / `PRINT A(3)` → `42` | ✅ | test_ca_uc_010_04_dim_array | 2026-04-06 |
| CA-UC-010-05 | `DIM B(2,3)` / `B(1,2)=7` / `PRINT B(1,2)` → `7` | ✅ | test_ca_uc_010_05_dim_2d | 2026-04-06 |
| CA-UC-010-06 | `A(3)=5` sans DIM → auto-dimensionnement à 10, `5` affiché | ✅ | test_ca_uc_010_06_auto_dim | 2026-04-06 |
| CA-UC-011-01 | `PRINT 2+3*4` → `14` | ✅ | test_ca_uc_011_01_precedence | 2026-04-06 |
| CA-UC-011-02 | `PRINT (2+3)*4` → `20` | ✅ | test_ca_uc_011_02_parentheses | 2026-04-06 |
| CA-UC-011-03 | `PRINT 2^3^2` → `512` (associativité droite) | ✅ | test_ca_uc_011_03_power_right_assoc | 2026-04-06 |
| CA-UC-011-04 | `PRINT 10-3-2` → `5` (associativité gauche) | ✅ | test_ca_uc_011_04_subtraction_left_assoc | 2026-04-06 |
| CA-UC-011-05 | `PRINT 5>3` → `1` | ✅ | test_ca_uc_011_05_greater_than | 2026-04-06 |
| CA-UC-011-06 | `PRINT 5=3` → `0` | ✅ | test_ca_uc_011_06_equal | 2026-04-06 |
| CA-UC-011-07 | `PRINT "B">"A"` → `1` (comparaison lexicographique) | ✅ | test_ca_uc_011_07_string_comparison | 2026-04-06 |
| CA-UC-011-08 | `PRINT 1 AND 0` → `0` | ✅ | test_ca_uc_011_08_and | 2026-04-06 |
| CA-UC-011-09 | `PRINT 1 OR 0` → `1` | ✅ | test_ca_uc_011_09_or | 2026-04-06 |
| CA-UC-011-10 | `PRINT NOT 0` → `1` | ✅ | test_ca_uc_011_10_not | 2026-04-06 |
| CA-UC-011-11 | `PRINT 5>3 AND 2<4` → `1` | ✅ | test_ca_uc_011_11_compound_logical | 2026-04-06 |
| CA-UC-011-12 | `PRINT 12 AND 10` → `8` (bit à bit) | ✅ | test_ca_uc_011_12_bitwise_and | 2026-04-06 |
| CA-UC-011-13 | `PRINT 0^0` → `1` | ✅ | test_ca_uc_011_13_zero_power_zero | 2026-04-06 |
| CA-UC-011-14 | `PRINT -2^2` → `4` (unaire prioritaire) | ✅ | test_ca_uc_011_14_unary_precedence | 2026-04-06 |
| CA-UC-011-15 | `PRINT 5 =< 5` → `1` (synonyme <=) | ✅ | test_ca_uc_011_15_equal_less | 2026-04-06 |
| CA-RG-0006-04 | `X%=32768` → `?ILLEGAL QUANTITY ERROR` | ✅ | test_ca_rg_0006_04_integer_overflow | 2026-04-06 |
| CA-RG-0006-05 | `X%=3.7` → tronqué à 3 | ✅ | test_ca_rg_0006_05_integer_truncation | 2026-04-06 |
| CA-RG-0006-06 | `X=1E39` → `?OVERFLOW ERROR` | ✅ | test_ca_rg_0006_06_overflow | 2026-04-06 |
| CA-RG-0007-01 | `A$="HELLO" : B$=" WORLD" : PRINT A$+B$` → `HELLO WORLD` | ✅ | test_ca_rg_0007_01_concatenation | 2026-04-06 |
| CA-RG-0007-02 | Concaténation > 255 chars → `?STRING TOO LONG ERROR` | ✅ | test_ca_rg_0007_02_string_too_long | 2026-04-06 |
| CA-RG-0007-03 | `A$=5` → `?TYPE MISMATCH ERROR` | ✅ | test_ca_rg_0007_03_type_mismatch_to_string | 2026-04-06 |
| CA-RG-0007-04 | `A="TEXT"` → `?TYPE MISMATCH ERROR` | ✅ | test_ca_rg_0007_04_type_mismatch_to_numeric | 2026-04-06 |
| CA-RG-0008-01 | `PRINT "A" : PRINT "B"` → `A` puis `B` (multi-commandes) | ✅ | test_ca_rg_0008_01_multi_print | 2026-04-06 |
| CA-RG-0009-01 | `REM COMMENTAIRE` → ignoré | ✅ | test_ca_rg_0009_01_rem_ignored | 2026-04-06 |
| CA-RG-0009-02 | `REM TEXTE : PRINT "CACHÉ"` → rien affiché | ✅ | test_ca_rg_0009_02_rem_eats_colon | 2026-04-06 |

## Prochaines actions

Lot terminé — prêt pour QA
