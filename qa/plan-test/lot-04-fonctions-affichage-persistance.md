# Plan de test — lot-04-fonctions-affichage-persistance

**Date :** 2026-04-07
**UC couverts :** UC-004, UC-005, UC-009, UC-015, UC-016, UC-017
**Nombre de scénarios :** 46

## Scénarios

### UC-015 — Fonctions mathématiques

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T01-01 | ABS(-5) → 5 | Nominal | CA-UC-015-01 | 🔴 Bloquant | test_t01_01_abs |
| T01-02 | INT(3.7) → 3 | Nominal | CA-UC-015-02 | 🔴 Bloquant | test_t01_02_int_positive |
| T01-03 | INT(-3.7) → -4 (arrondi vers le bas) | Nominal | CA-UC-015-03 | 🔴 Bloquant | test_t01_03_int_negative |
| T01-04 | SQR(16) → 4 | Nominal | CA-UC-015-04 | 🔴 Bloquant | test_t01_04_sqr |
| T01-05 | SGN(-42) → -1, SGN(0) → 0, SGN(5) → 1 | Nominal | CA-UC-015-05 | 🔴 Bloquant | test_t01_05_sgn |
| T01-06 | RND(1) → deux valeurs différentes ∈ [0,1) | Nominal | CA-UC-015-06 | 🔴 Bloquant | test_t01_06_rnd_different |
| T01-07 | RND(-5) puis RND(1) → graine déterministe | Nominal | CA-UC-015-07 | 🟠 Majeur | test_t01_07_rnd_seed |
| T01-08 | RND(0) → répète le dernier | Nominal | CA-UC-015-08 | 🟠 Majeur | test_t01_08_rnd_zero_repeats |
| T01-09 | SQR(-1) → ?ILLEGAL QUANTITY ERROR | Erreur | UC-015 exception 1b | 🔴 Bloquant | test_t01_09_sqr_negative |
| T01-10 | LOG(0) → ?ILLEGAL QUANTITY ERROR | Erreur | UC-015 exception 1b | 🔴 Bloquant | test_t01_10_log_zero |
| T01-11 | LOG(-1) → ?ILLEGAL QUANTITY ERROR | Erreur | UC-015 exception 1b | 🔴 Bloquant | test_t01_11_log_negative |
| T01-12 | LOG, EXP, SIN, COS, TAN, ATN — valeurs de référence | Nominal | CA-UC-015-01 (étendu) | 🟠 Majeur | test_t01_12_trig_and_log_exp |

### UC-016 — Fonctions de chaînes

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T02-01 | LEN("HELLO") → 5 | Nominal | CA-UC-016-01 | 🔴 Bloquant | test_t02_01_len |
| T02-02 | LEFT$("HELLO",3) → "HEL" | Nominal | CA-UC-016-02 | 🔴 Bloquant | test_t02_02_left |
| T02-03 | RIGHT$("HELLO",3) → "LLO" | Nominal | CA-UC-016-03 | 🔴 Bloquant | test_t02_03_right |
| T02-04 | MID$("HELLO",2,3) → "ELL" | Nominal | CA-UC-016-04 | 🔴 Bloquant | test_t02_04_mid |
| T02-05 | ASC("A") → 65 | Nominal | CA-UC-016-05 | 🔴 Bloquant | test_t02_05_asc |
| T02-06 | CHR$(65) → "A" | Nominal | CA-UC-016-06 | 🔴 Bloquant | test_t02_06_chr |
| T02-07 | VAL("3.14") → 3.14 | Nominal | CA-UC-016-07 | 🔴 Bloquant | test_t02_07_val |
| T02-08 | STR$(42) → " 42" | Nominal | CA-UC-016-08 | 🔴 Bloquant | test_t02_08_str |
| T02-09 | MID$("AB",5,1) → chaîne vide | Limite | CA-UC-016-09 | 🟠 Majeur | test_t02_09_mid_out_of_range |
| T02-10 | VAL("HELLO") → 0 | Limite | CA-UC-016-10 | 🟠 Majeur | test_t02_10_val_non_numeric |
| T02-11 | VAL("3ABC") → 3 | Limite | CA-UC-016-11 | 🟠 Majeur | test_t02_11_val_partial |
| T02-12 | ASC("") → ?ILLEGAL QUANTITY ERROR | Erreur | UC-016 exception 1b | 🔴 Bloquant | test_t02_12_asc_empty |
| T02-13 | CHR$(256) → ?ILLEGAL QUANTITY ERROR | Erreur | UC-016 exception 1b | 🔴 Bloquant | test_t02_13_chr_overflow |
| T02-14 | LEFT$("HI",-1) → ?ILLEGAL QUANTITY ERROR | Erreur | UC-016 exception 1b | 🔴 Bloquant | test_t02_14_left_negative |
| T02-15 | MID$ sans longueur → retourne jusqu'à la fin | Limite | CA-UC-016-04 (étendu) | 🟠 Majeur | test_t02_15_mid_no_length |

### UC-017 — Fonctions utilisateur DEF FN

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T03-01 | DEF FN DOUBLE(X)=X*2 : PRINT FN DOUBLE(5) → 10 | Nominal | CA-UC-017-01 | 🔴 Bloquant | test_t03_01_def_fn_double |
| T03-02 | DEF FN avec variable globale → évaluée correctement | Nominal | CA-UC-017-02 | 🔴 Bloquant | test_t03_02_def_fn_global_var |
| T03-03 | FN sans DEF → ?UNDEF'D FUNCTION ERROR | Erreur | UC-017 exception 1b | 🔴 Bloquant | test_t03_03_undef_fn_error |
| T03-04 | DEF FN avec erreur dans l'expression → erreur à l'appel | Erreur | UC-017 exception 1b | 🟠 Majeur | test_t03_04_fn_error_at_call |

### UC-009 — Contrôle de l'affichage

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T04-01 | HTAB 10 : PRINT "X" → colonne 10 | Nominal | CA-UC-009-01 | 🔴 Bloquant | test_t04_01_htab |
| T04-02 | VTAB 12 : HTAB 20 : PRINT "X" → position (12,20) | Nominal | CA-UC-009-02 | 🔴 Bloquant | test_t04_02_vtab_htab |
| T04-03 | HOME → écran vidé, curseur en (1,1) | Nominal | CA-UC-009-03 | 🔴 Bloquant | test_t04_03_home |
| T04-04 | INVERSE + PRINT → mode inversé | Nominal | CA-UC-009-04 | 🟠 Majeur | test_t04_04_inverse |
| T04-05 | FLASH + PRINT → attribut clignotant | Nominal | CA-UC-009-05 | 🟠 Majeur | test_t04_05_flash |
| T04-06 | SPEED=100 : PRINT "SLOW" → délai visible | Nominal | CA-UC-009-06 | 🟡 Mineur | test_t04_06_speed |
| T04-07 | HTAB 0 / HTAB 41 → ?ILLEGAL QUANTITY ERROR | Erreur | UC-009 exception 1b | 🔴 Bloquant | test_t04_07_htab_out_of_range |
| T04-08 | VTAB 0 / VTAB 25 → ?ILLEGAL QUANTITY ERROR | Erreur | UC-009 exception 1b | 🔴 Bloquant | test_t04_08_vtab_out_of_range |
| T04-09 | SPEED=-1 / SPEED=256 → ?ILLEGAL QUANTITY ERROR | Erreur | UC-009 exception 1b | 🟠 Majeur | test_t04_09_speed_out_of_range |

### UC-004 — Sauvegarder un programme (SAVE)

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T05-01 | SAVE "TEST.BAS" → fichier texte créé | Nominal | CA-UC-004-01 | 🔴 Bloquant | test_t05_01_save_creates_file |
| T05-02 | SAVE sans nom → ?SYNTAX ERROR | Erreur | UC-004 exception 1a | 🔴 Bloquant | test_t05_02_save_no_filename |
| T05-03 | SAVE "TEST" → fichier TEST.bas créé (extension auto) | Nominal | CA-UC-004-01 | 🔴 Bloquant | test_t05_03_save_auto_bas_extension |
| T05-04 | SAVE "PROG.BAS" → pas de double extension | Limite | CA-UC-004-01 | 🟠 Majeur | test_t05_04_save_no_double_extension |

### UC-005 — Charger un programme (LOAD)

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T06-01 | LOAD → programme chargé, variables effacées | Nominal | CA-UC-005-01 | 🔴 Bloquant | test_t06_01_load_replaces_and_clears |
| T06-02 | LOAD → ancien programme intégralement remplacé | Nominal | CA-UC-005-02 | 🔴 Bloquant | test_t06_02_load_replaces_entirely |
| T06-03 | LOAD fichier inexistant → ?FILE NOT FOUND | Erreur | UC-005 exception 1b | 🔴 Bloquant | test_t06_03_load_file_not_found |
| T06-04 | LOAD avec path traversal → bloqué (SEC-BP-22) | Sécurité | SEC-BP-22 | 🔴 Bloquant | test_t06_04_load_path_traversal |
| T06-05 | LOAD "TEST" → charge TEST.bas (extension auto) | Nominal | CA-UC-005-01 | 🔴 Bloquant | test_t06_05_load_auto_bas_extension |
| T06-06 | SAVE "DEMO" + LOAD "DEMO" → roundtrip sans extension | Nominal | CA-UC-004-01/005-01 | 🔴 Bloquant | test_t06_06_save_load_roundtrip_no_ext |

## Tests manuels

Aucun — tous les scénarios sont automatisables.
