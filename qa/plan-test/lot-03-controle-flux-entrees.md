# Plan de test — lot-03-controle-flux-entrees

**Date :** 2026-04-06
**UC couverts :** UC-007, UC-008, UC-012, UC-013, UC-014
**Nombre de scénarios :** 37

## Scénarios

### UC-012 — Branchements

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T01-01 | GOTO 30 saute la ligne 20 | Nominal | CA-UC-012-01 | 🔴 Bloquant | test_t01_01_goto |
| T01-02 | IF X>3 THEN PRINT "YES" | Nominal | CA-UC-012-02 | 🔴 Bloquant | test_t01_02_if_then |
| T01-03 | IF faux → bloc THEN sauté | Nominal | CA-UC-012-03 | 🔴 Bloquant | test_t01_03_if_false_block |
| T01-04 | IF/ELSE → branche ELSE | Nominal | CA-UC-012-04 | 🔴 Bloquant | test_t01_04_if_else |
| T01-05 | IF THEN linenum → GOTO implicite | Nominal | CA-UC-012-05 | 🔴 Bloquant | test_t01_05_if_then_linenum |
| T01-06 | ON X GOTO → branchement indexé | Nominal | CA-UC-012-06 | 🔴 Bloquant | test_t01_06_on_goto |
| T01-07 | IF imbriqués sur une même ligne | Nominal | CA-UC-012-07 | 🟠 Majeur | test_t01_07_nested_if |
| T01-08 | GOTO ligne inexistante → UNDEF'D STATEMENT | Erreur | UC-012 exc. 1b | 🔴 Bloquant | test_t01_08_goto_undef |
| T01-09 | ON 0 GOTO → continue | Limite | UC-012 exc. 1b | 🟠 Majeur | test_t01_09_on_zero |
| T01-10 | ON -1 GOTO → ILLEGAL QUANTITY | Erreur | UC-012 exc. 1b | 🟠 Majeur | test_t01_10_on_negative |

### UC-013 — Boucles FOR/NEXT

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T02-01 | FOR I=1 TO 3 → 1,2,3 | Nominal | CA-UC-013-01 | 🔴 Bloquant | test_t02_01_for_basic |
| T02-02 | FOR STEP 3 → 1,4,7,10 | Nominal | CA-UC-013-02 | 🔴 Bloquant | test_t02_02_for_step |
| T02-03 | FOR STEP -1 → 5,4,3,2,1 | Nominal | CA-UC-013-03 | 🔴 Bloquant | test_t02_03_for_step_neg |
| T02-04 | Boucles imbriquées NEXT J,I | Nominal | CA-UC-013-04 | 🔴 Bloquant | test_t02_04_nested |
| T02-05 | FOR I=1 TO 0 → corps exécuté 1 fois | Limite | UC-013 exc. 1b | 🟠 Majeur | test_t02_05_for_one_pass |
| T02-06 | NEXT sans FOR → NEXT WITHOUT FOR | Erreur | UC-013 exc. 1b | 🔴 Bloquant | test_t02_06_next_without_for |
| T02-07 | NEXT J alors que FOR I actif → NEXT WITHOUT FOR | Erreur | UC-013 exc. 1b | 🟠 Majeur | test_t02_07_next_wrong_var |

### UC-014 — GOSUB/RETURN

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T03-01 | GOSUB + RETURN → retour correct | Nominal | CA-UC-014-01 | 🔴 Bloquant | test_t03_01_gosub_return |
| T03-02 | GOSUB imbriqués | Nominal | CA-UC-014-02 | 🔴 Bloquant | test_t03_02_gosub_nested |
| T03-03 | POP + GOTO au lieu de RETURN | Nominal | CA-UC-014-03 | 🟠 Majeur | test_t03_03_pop_goto |
| T03-04 | ON X GOSUB + RETURN | Nominal | CA-UC-014-04 | 🔴 Bloquant | test_t03_04_on_gosub |
| T03-05 | RETURN sans GOSUB → RETURN WITHOUT GOSUB | Erreur | UC-014 exc. 1b | 🔴 Bloquant | test_t03_05_return_no_gosub |
| T03-06 | GOSUB ligne inexistante → UNDEF'D STATEMENT | Erreur | UC-014 exc. 1b | 🔴 Bloquant | test_t03_06_gosub_undef |

### UC-007 — INPUT/GET

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T04-01 | INPUT A$ → saisie reflétée | Nominal | CA-UC-007-01 | 🔴 Bloquant | test_t04_01_input_str |
| T04-02 | INPUT "NAME";N$ → invite NAME? | Nominal | CA-UC-007-02 | 🔴 Bloquant | test_t04_02_input_prompt |
| T04-03 | INPUT A,B → somme | Nominal | CA-UC-007-03 | 🔴 Bloquant | test_t04_03_input_multi |
| T04-04 | GET A$ → caractère sans écho | Nominal | CA-UC-007-04 | 🔴 Bloquant | test_t04_04_get_char |

### UC-008 — DATA/READ/RESTORE

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T05-01 | DATA + READ + PRINT → 6 | Nominal | CA-UC-008-01 | 🔴 Bloquant | test_t05_01_data_read |
| T05-02 | DATA après READ → position ok | Nominal | CA-UC-008-02 | 🔴 Bloquant | test_t05_02_data_position |
| T05-03 | RESTORE → relecture | Nominal | CA-UC-008-03 | 🔴 Bloquant | test_t05_03_restore |
| T05-04 | READ au-delà → OUT OF DATA | Erreur | UC-008 exc. 1b | 🔴 Bloquant | test_t05_04_out_of_data |

### ENF — Performance

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T06-01 | FOR 10000 itérations < 2s | Performance | ENF-002 | 🟠 Majeur | test_t06_01_perf_loop |

### Sécurité — Intégrité des signaux

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T07-01 | GOSUB profond (50 niveaux) ne crash pas | Robustesse | SEC-DEV-05 | 🟠 Majeur | test_t07_01_deep_gosub |
| T07-02 | FOR profond (20 niveaux) ne crash pas | Robustesse | SEC-DEV-05 | 🟡 Mineur | test_t07_02_deep_for |

## Tests manuels

Aucun pour ce lot.
