# Plan de test — lot-01-infrastructure-pipeline

**Date :** 2026-04-06
**UC couverts :** UC-001, UC-002
**RG couvertes :** RG-0001 à RG-0006, RG-0010
**Nombre de scénarios :** 45

## Scénarios

### Lexer (RG-0001 à RG-0005)

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T01-01 | Tokenisation `10 PRINT "HELLO"` → séquence correcte | Nominal | CA-RG-0001-01 | 🔴 Bloquant | test_t01_01_tokenize_print_hello |
| T01-02 | Tokenisation `A = 3.14 + B` → séquence correcte | Nominal | CA-RG-0001-02 | 🔴 Bloquant | test_t01_02_tokenize_expression |
| T01-03 | Espaces optionnels entre keyword et chaîne | Nominal | CA-RG-0001-03 | 🟠 Majeur | test_t01_03_no_space_keyword_string |
| T01-04 | Ligne vide → séquence vide | Limite | CA-RG-0001-04 | 🟡 Mineur | test_t01_04_empty_line |
| T01-05 | Chaîne non fermée → terminée en fin de ligne | Limite | CA-RG-0001-05 | 🟠 Majeur | test_t01_05_unclosed_string |
| T01-06 | Correspondance gloutonne `FORI=1TO10` | Nominal | CA-RG-0002-01 | 🔴 Bloquant | test_t01_06_greedy_for |
| T01-07 | Correspondance gloutonne `IFATHENPRINT` | Nominal | CA-RG-0002-02 | 🔴 Bloquant | test_t01_07_greedy_if_at |
| T01-08 | `GOTO100` sans séparateur | Nominal | CA-RG-0002-03 | 🔴 Bloquant | test_t01_08_goto_no_space |
| T01-09 | `SCORE` → `SC` + `OR` + `E` | Nominal | CA-RG-0002-04 | 🔴 Bloquant | test_t01_09_score_keyword_in_ident |
| T01-10 | `NOTATION` → `NOT` + `AT` + `I` + `ON` | Nominal | CA-RG-0002-05 | 🔴 Bloquant | test_t01_10_notation_multi_keyword |
| T01-11 | 2 chars significatifs pour identifiants | Nominal | CA-RG-0003-01 | 🔴 Bloquant | test_t01_11_two_char_ident |
| T01-12 | A, A$, A% sont distincts | Nominal | CA-RG-0003-02 | 🔴 Bloquant | test_t01_12_suffix_distinct |
| T01-13 | Littéral flottant 3.14 | Nominal | CA-RG-0004-01 | 🔴 Bloquant | test_t01_13_float_literal |
| T01-14 | Notation scientifique 1E3 | Nominal | CA-RG-0004-02 | 🟠 Majeur | test_t01_14_scientific_notation |
| T01-15 | Nombre commençant par `.` (.5) | Limite | CA-RG-0004-03 | 🟠 Majeur | test_t01_15_dot_prefix_number |
| T01-16 | Chaîne "HELLO WORLD" | Nominal | CA-RG-0005-01 | 🔴 Bloquant | test_t01_16_string_literal |
| T01-17 | Chaîne non fermée "HELLO | Limite | CA-RG-0005-02 | 🟠 Majeur | test_t01_17_unclosed_string_literal |
| T01-18 | Chaîne vide "" | Limite | CA-RG-0005-03 | 🟡 Mineur | test_t01_18_empty_string |
| T01-19 | Troncature à 239 caractères | Limite | UC-001 exc. 2b | 🟠 Majeur | test_t01_19_line_truncation_239 |
| T01-20 | `?` reconnu comme alias de PRINT | Nominal | GRAMMAR.md | 🟠 Majeur | test_t01_20_question_mark_print |

### NumberFormatter (RG-0006)

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T02-01 | Espace avant nombre positif | Nominal | CA-RG-0006-01 | 🔴 Bloquant | test_t02_01_positive_space |
| T02-02 | Pas d'espace avant nombre négatif | Nominal | CA-RG-0006-02 | 🔴 Bloquant | test_t02_02_negative_no_space |
| T02-03 | Notation scientifique >= 1E9 | Nominal | CA-RG-0006-03 | 🟠 Majeur | test_t02_03_scientific_large |

### ErrorHandler (RG-0010)

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T03-01 | `?DIVISION BY ZERO ERROR IN 10` avec n° ligne | Nominal | CA-RG-0010-01 | 🔴 Bloquant | test_t03_01_error_with_linenum |
| T03-02 | `?DIVISION BY ZERO ERROR` sans n° en mode direct | Nominal | CA-RG-0010-02 | 🔴 Bloquant | test_t03_02_error_no_linenum |
| T03-03 | Les 16 codes d'erreur sont définis | Nominal | RG-0010 | 🔴 Bloquant | test_t03_03_all_error_codes |

### Parser (GRAMMAR.md)

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T04-01 | Parse PRINT "HELLO" → PrintStmt | Nominal | GRAMMAR.md | 🔴 Bloquant | test_t04_01_parse_print |
| T04-02 | Parse LET A = 5 → LetStmt | Nominal | GRAMMAR.md | 🔴 Bloquant | test_t04_02_parse_let |
| T04-03 | Précédence * sur + correcte | Nominal | GRAMMAR.md § 4.1 | 🔴 Bloquant | test_t04_03_precedence |
| T04-04 | Associativité droite de ^ | Nominal | GRAMMAR.md § 4.1 | 🟠 Majeur | test_t04_04_power_right_assoc |
| T04-05 | REM absorbe tout y compris `:` | Nominal | RG-0009 | 🔴 Bloquant | test_t04_05_rem_eats_colon |
| T04-06 | `?SYNTAX ERROR` sur entrée invalide | Erreur | RG-0010 | 🔴 Bloquant | test_t04_06_syntax_error |

### REPL — UC-001

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T05-01 | Prompt `]` affiché au démarrage | Nominal | CA-UC-001-01 | 🔴 Bloquant | test_t05_01_prompt_at_start |
| T05-02 | Ligne numérotée stockée sans exécution | Nominal | CA-UC-001-03 | 🔴 Bloquant | test_t05_02_deferred_store |
| T05-03 | Lignes triées par numéro | Nominal | CA-UC-001-04 | 🔴 Bloquant | test_t05_03_sorted_lines |
| T05-04 | Remplacement de ligne existante | Nominal | CA-UC-001-05 | 🔴 Bloquant | test_t05_04_replace_line |
| T05-05 | Numéro seul → suppression | Nominal | CA-UC-001-06 | 🔴 Bloquant | test_t05_05_delete_by_number |
| T05-06 | Ligne vide → prompt réaffiché | Erreur | UC-001 exc. 2a | 🟡 Mineur | test_t05_06_empty_line |
| T05-07 | Numéro > 63999 → ?SYNTAX ERROR | Erreur | UC-001 exc. 2b | 🟠 Majeur | test_t05_07_linenum_too_large |
| T05-08 | Suppression d'une ligne inexistante → pas d'erreur | Erreur | UC-001 exc. 2b | 🟡 Mineur | test_t05_08_delete_nonexistent |

### REPL — UC-002

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T06-01 | LIST affiche toutes les lignes dans l'ordre | Nominal | CA-UC-002-01 | 🔴 Bloquant | test_t06_01_list_all |
| T06-02 | LIST 20 → uniquement ligne 20 | Nominal | CA-UC-002-02 | 🔴 Bloquant | test_t06_02_list_single |
| T06-03 | LIST 10,20 → plage | Nominal | CA-UC-002-03 | 🔴 Bloquant | test_t06_03_list_range |
| T06-04 | NEW → programme effacé | Nominal | CA-UC-002-04 | 🔴 Bloquant | test_t06_04_new_clears |
| T06-05 | DEL 10,20 → supprime plage | Nominal | CA-UC-002-05 | 🔴 Bloquant | test_t06_05_del_range |
| T06-06 | DEL 20,20 → supprime une seule ligne | Nominal | CA-UC-002-06 | 🟠 Majeur | test_t06_06_del_single |

### ENF — Performance et portabilité

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T07-01 | Pas d'import interdit dans le cœur | Performance | ENF-001 | 🟠 Majeur | test_t07_01_no_forbidden_imports |
| T07-02 | Démarrage < 1s | Performance | ENF-002 | 🟠 Majeur | TM-01 (manuel) |

## Tests manuels

| # | Scénario | Procédure | Critère de réussite |
|---|----------|-----------|-------------------|
| TM-01 | Temps de démarrage < 1s | `time python3 -m applesoft <<< ""` | real < 1.0s |
