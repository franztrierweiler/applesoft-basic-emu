# Plan de test — lot-02-interpreteur-coeur

**Date :** 2026-04-06
**UC couverts :** UC-003, UC-006, UC-010, UC-011
**RG couvertes :** RG-0006, RG-0007, RG-0008, RG-0009
**Nombre de scénarios :** 58

## Scénarios

### UC-003 — Exécuter un programme

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T01-01 | Exécution séquentielle 10/20 → A puis B | Nominal | CA-UC-003-01 | 🔴 Bloquant | test_t01_01_sequential_run |
| T01-02 | RUN 20 → seul B affiché | Nominal | CA-UC-003-02 | 🔴 Bloquant | test_t01_02_run_from_line |
| T01-03 | Variable assignée puis affichée | Nominal | CA-UC-003-03 | 🔴 Bloquant | test_t01_03_variable_print |
| T01-04 | END arrête l'exécution | Nominal | CA-UC-003-04 | 🔴 Bloquant | test_t01_04_end_stops |
| T01-05 | STOP + CONT → reprend | Nominal | CA-UC-003-05 | 🔴 Bloquant | test_t01_05_stop_cont |
| T01-06 | STOP + modif variable + CONT → conservée | Nominal | CA-UC-003-06 | 🔴 Bloquant | test_t01_06_stop_modify_cont |
| T01-07 | RUN sans programme → pas d'erreur | Erreur | UC-003 exc. 1b | 🟠 Majeur | test_t01_07_run_empty |
| T01-08 | RUN 99 (inexistante) → UNDEF'D STATEMENT | Erreur | UC-003 exc. 1b | 🔴 Bloquant | test_t01_08_run_undef_line |
| T01-09 | CONT sans arrêt → CAN'T CONTINUE | Erreur | UC-003 exc. 2b | 🔴 Bloquant | test_t01_09_cont_without_stop |
| T01-10 | CONT après modif programme → CAN'T CONTINUE | Erreur | UC-003 exc. 2b | 🟠 Majeur | test_t01_10_cont_after_modify |
| T01-11 | Fin de programme sans END → terminaison implicite | Limite | UC-003 exc. 2b | 🟠 Majeur | test_t01_11_implicit_end |

### UC-006 — Afficher des données

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T02-01 | PRINT "HELLO" → HELLO + retour ligne | Nominal | CA-UC-006-01 | 🔴 Bloquant | test_t02_01_print_string |
| T02-02 | PRINT "A";"B" → AB | Nominal | CA-UC-006-02 | 🔴 Bloquant | test_t02_02_semicolon |
| T02-03 | PRINT "A","B" → tabulation 16 colonnes | Nominal | CA-UC-006-03 | 🔴 Bloquant | test_t02_03_comma_tab |
| T02-04 | PRINT "A"; + PRINT "B" → AB sur une ligne | Nominal | CA-UC-006-04 | 🔴 Bloquant | test_t02_04_trailing_semicolon |
| T02-05 | PRINT seul → ligne vide | Nominal | CA-UC-006-05 | 🟠 Majeur | test_t02_05_print_empty |
| T02-06 | ? "HELLO" → HELLO | Nominal | CA-UC-006-06 | 🟠 Majeur | test_t02_06_question_mark |
| T02-07 | PRINT SPC(5);"X" → 5 espaces + X | Nominal | CA-UC-006-07 | 🟠 Majeur | test_t02_07_spc |
| T02-08 | PRINT TAB(10);"X" → X en colonne 10 | Nominal | CA-UC-006-08 | 🟠 Majeur | test_t02_08_tab |
| T02-09 | TAB au-delà du curseur → nouvelle ligne | Limite | CA-UC-006-09 | 🟠 Majeur | test_t02_09_tab_beyond |
| T02-10 | POS(0) retourne la colonne courante | Nominal | CA-UC-006-10 | 🟠 Majeur | test_t02_10_pos |
| T02-11 | PRINT 1/0 → DIVISION BY ZERO ERROR | Erreur | UC-006 exc. 1b | 🔴 Bloquant | test_t02_11_division_by_zero |
| T02-12 | PRINT nombre positif → espace avant | Nominal | RG-0006 | 🔴 Bloquant | test_t02_12_positive_space |
| T02-13 | PRINT nombre négatif → pas d'espace | Nominal | RG-0006 | 🔴 Bloquant | test_t02_13_negative_no_space |

### UC-010 — Variables

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T03-01 | LET A = 5 : PRINT A → 5 | Nominal | CA-UC-010-01 | 🔴 Bloquant | test_t03_01_let_explicit |
| T03-02 | A = 5 : PRINT A → 5 (LET implicite) | Nominal | CA-UC-010-02 | 🔴 Bloquant | test_t03_02_let_implicit |
| T03-03 | PRINT X (non init) → 0 | Nominal | CA-UC-010-03 | 🔴 Bloquant | test_t03_03_uninitialized |
| T03-04 | DIM A(5) / A(3)=42 → 42 | Nominal | CA-UC-010-04 | 🔴 Bloquant | test_t03_04_dim_array |
| T03-05 | DIM B(2,3) / B(1,2)=7 → 7 | Nominal | CA-UC-010-05 | 🔴 Bloquant | test_t03_05_dim_2d |
| T03-06 | A(3)=5 sans DIM → auto-dim | Nominal | CA-UC-010-06 | 🔴 Bloquant | test_t03_06_auto_dim |
| T03-07 | A(11) sans DIM → BAD SUBSCRIPT | Erreur | UC-010 exc. 1b | 🔴 Bloquant | test_t03_07_bad_subscript |
| T03-08 | DIM A(5) deux fois → REDIM'D ARRAY | Erreur | UC-010 exc. 1b | 🟠 Majeur | test_t03_08_redim |

### UC-011 — Expressions

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T04-01 | 2+3*4 → 14 (précédence) | Nominal | CA-UC-011-01 | 🔴 Bloquant | test_t04_01_precedence |
| T04-02 | (2+3)*4 → 20 (parenthèses) | Nominal | CA-UC-011-02 | 🔴 Bloquant | test_t04_02_parens |
| T04-03 | 2^3^2 → 512 (droite) | Nominal | CA-UC-011-03 | 🔴 Bloquant | test_t04_03_power_right |
| T04-04 | 10-3-2 → 5 (gauche) | Nominal | CA-UC-011-04 | 🔴 Bloquant | test_t04_04_sub_left |
| T04-05 | 5>3 → 1 | Nominal | CA-UC-011-05 | 🔴 Bloquant | test_t04_05_gt |
| T04-06 | 5=3 → 0 | Nominal | CA-UC-011-06 | 🔴 Bloquant | test_t04_06_eq |
| T04-07 | "B">"A" → 1 (lexicographique) | Nominal | CA-UC-011-07 | 🔴 Bloquant | test_t04_07_string_cmp |
| T04-08 | 1 AND 0 → 0 | Nominal | CA-UC-011-08 | 🔴 Bloquant | test_t04_08_and |
| T04-09 | 1 OR 0 → 1 | Nominal | CA-UC-011-09 | 🔴 Bloquant | test_t04_09_or |
| T04-10 | NOT 0 → 1 | Nominal | CA-UC-011-10 | 🔴 Bloquant | test_t04_10_not |
| T04-11 | 5>3 AND 2<4 → 1 | Nominal | CA-UC-011-11 | 🟠 Majeur | test_t04_11_compound |
| T04-12 | 12 AND 10 → 8 (bit à bit) | Nominal | CA-UC-011-12 | 🟠 Majeur | test_t04_12_bitwise_and |
| T04-13 | 0^0 → 1 | Limite | CA-UC-011-13 | 🟠 Majeur | test_t04_13_zero_power_zero |
| T04-14 | -2^2 → 4 (unaire prioritaire) | Nominal | CA-UC-011-14 | 🔴 Bloquant | test_t04_14_unary_precedence |
| T04-15 | 5 =< 5 → 1 | Nominal | CA-UC-011-15 | 🟠 Majeur | test_t04_15_equal_less |
| T04-16 | 5>"A" → TYPE MISMATCH | Erreur | UC-011 exc. 1b | 🔴 Bloquant | test_t04_16_type_mismatch_cmp |

### RG-0006 — Types numériques

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T05-01 | X%=32768 → ILLEGAL QUANTITY | Erreur | CA-RG-0006-04 | 🔴 Bloquant | test_t05_01_int_overflow |
| T05-02 | X%=3.7 → tronqué à 3 | Nominal | CA-RG-0006-05 | 🟠 Majeur | test_t05_02_int_truncation |
| T05-03 | EXP(1000) → OVERFLOW | Erreur | CA-RG-0006-06 | 🟠 Majeur | test_t05_03_overflow |

### RG-0007 — Chaînes

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T06-01 | A$+"HELLO" + " WORLD" → HELLO WORLD | Nominal | CA-RG-0007-01 | 🔴 Bloquant | test_t06_01_concat |
| T06-02 | Concaténation > 255 → STRING TOO LONG | Erreur | CA-RG-0007-02 | 🔴 Bloquant | test_t06_02_string_too_long |
| T06-03 | A$=5 → TYPE MISMATCH | Erreur | CA-RG-0007-03 | 🔴 Bloquant | test_t06_03_type_mismatch_str |
| T06-04 | A="TEXT" → TYPE MISMATCH | Erreur | CA-RG-0007-04 | 🔴 Bloquant | test_t06_04_type_mismatch_num |

### RG-0008/0009 — Multi-commandes et REM

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T07-01 | PRINT "A" : PRINT "B" → A puis B | Nominal | CA-RG-0008-01 | 🔴 Bloquant | test_t07_01_multi_stmt |
| T07-02 | REM → ignoré | Nominal | CA-RG-0009-01 | 🔴 Bloquant | test_t07_02_rem_ignored |
| T07-03 | REM : PRINT → rien | Nominal | CA-RG-0009-02 | 🔴 Bloquant | test_t07_03_rem_eats_colon |

### ENF — Sécurité

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T08-01 | Pas d'eval/exec dans interpreter.py | Sécurité | SEC-DEV-01 | 🔴 Bloquant | test_t08_01_no_eval_exec |

## Tests manuels

Aucun pour ce lot.
