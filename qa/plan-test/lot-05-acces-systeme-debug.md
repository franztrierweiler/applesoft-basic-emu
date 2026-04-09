# Plan de test — lot-05-acces-systeme-debug

**Date :** 2026-04-09
**UC couverts :** UC-022, UC-023, UC-024
**Nombre de scénarios :** 30

## Scénarios

### UC-022 — Lire/écrire la mémoire (PEEK/POKE/CALL)

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T01-01 | POKE 768,42 puis PEEK(768) → affiche 42 | Nominal | CA-UC-022-02 | 🔴 Bloquant | test_t01_01_poke_peek_roundtrip |
| T01-02 | ONERR + division par zéro + PEEK(222) → affiche 133 | Nominal | CA-UC-022-01 | 🔴 Bloquant | test_t01_02_onerr_peek222_error_code |
| T01-03 | CALL -936 → écran effacé (HOME) | Nominal | CA-UC-022-03 | 🔴 Bloquant | test_t01_03_call_minus936_home |
| T01-04 | GET + PEEK(49152) → code touche avec bit 7 | Nominal | CA-UC-022-04 | 🔴 Bloquant | test_t01_04_peek_49152_keyboard |
| T01-05 | POKE 49168,0 → reset strobe clavier (bit 7 à 0) | Nominal | CA-UC-022-05 | 🟠 Majeur | test_t01_05_poke_49168_reset_strobe |
| T01-06 | PEEK(-1) → `?ILLEGAL QUANTITY ERROR` | Erreur | UC-022 exc. 1b | 🔴 Bloquant | test_t01_06_peek_negative_error |
| T01-07 | PEEK(65536) → `?ILLEGAL QUANTITY ERROR` | Erreur | UC-022 exc. 1b | 🔴 Bloquant | test_t01_07_peek_too_large_error |
| T01-08 | POKE 768,256 → `?ILLEGAL QUANTITY ERROR` | Erreur | UC-022 exc. 1b | 🔴 Bloquant | test_t01_08_poke_value_too_large |
| T01-09 | POKE 768,-1 → `?ILLEGAL QUANTITY ERROR` | Erreur | UC-022 exc. 1b | 🔴 Bloquant | test_t01_09_poke_value_negative |
| T01-10 | POKE 65536,0 → `?ILLEGAL QUANTITY ERROR` | Erreur | UC-022 exc. 1b | 🔴 Bloquant | test_t01_10_poke_address_too_large |
| T01-11 | CALL 65536 → `?ILLEGAL QUANTITY ERROR` | Erreur | UC-022 exc. 1b | 🟠 Majeur | test_t01_11_call_address_too_large |
| T01-12 | CALL 12345 (adresse non émulée) → avertissement stderr | Erreur | UC-022 exc. 1b | 🟡 Mineur | test_t01_12_call_unknown_warning |
| T01-13 | PEEK sur adresse ROM non émulée → retourne 0 | Limite | UC-022 exc. 1b | 🟡 Mineur | test_t01_13_peek_rom_returns_zero |
| T01-14 | PEEK(218-219) → numéro de ligne d'erreur (little-endian) | Nominal | RG-0011 | 🟠 Majeur | test_t01_14_peek_218_219_error_line |
| T01-15 | PEEK(48) → mode texte/graphique | Nominal | RG-0011 | 🟡 Mineur | test_t01_15_peek_48_text_mode |
| T01-16 | PEEK(103-104) → adresse début programme (0x0801) | Nominal | RG-0011 | 🟡 Mineur | test_t01_16_peek_103_104_program_start |
| T01-17 | POKE 49200 → speaker no-op (pas d'erreur) | Nominal | RG-0011 | 🟡 Mineur | test_t01_17_poke_49200_speaker_noop |

### UC-023 — Gérer les erreurs d'exécution (ONERR GOTO / RESUME)

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T02-01 | ONERR GOTO + erreur → handler exécuté, PEEK(222) correct | Nominal | CA-UC-023-01 | 🔴 Bloquant | test_t02_01_onerr_handler_executed |
| T02-02 | ONERR GOTO 0 → handler désactivé, erreur affichée | Nominal | CA-UC-023-02 | 🔴 Bloquant | test_t02_02_onerr_goto_0_disables |
| T02-03 | ONERR + RESUME → reprend à l'instruction fautive (INPUT) | Nominal | CA-UC-023-03 | 🔴 Bloquant | test_t02_03_resume_retries_faulting |
| T02-04 | ONERR GOTO 999 (ligne inexistante) → `?UNDEF'D STATEMENT ERROR` | Erreur | UC-023 exc. 1b | 🟠 Majeur | test_t02_04_onerr_undef_statement |
| T02-05 | Erreur dans le handler → anti-boucle, erreur affichée, retour prompt | Erreur | UC-023 exc. 1b | 🔴 Bloquant | test_t02_05_error_in_handler_anti_loop |
| T02-06 | RESUME sans ONERR actif → `?SYNTAX ERROR` | Erreur | UC-023 exc. 1b | 🟠 Majeur | test_t02_06_resume_without_onerr |

### UC-024 — Interrompre l'exécution (Ctrl+C)

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T03-01 | Boucle infinie + Ctrl+C → `BREAK IN 10` + retour prompt | Nominal | CA-UC-024-01 | 🔴 Bloquant | test_t03_01_break_in_linenum |
| T03-02 | Après Ctrl+C, CONT → reprend l'exécution | Nominal | CA-UC-024-02 | 🔴 Bloquant | test_t03_02_cont_after_break |
| T03-03 | Variables conservées après interruption | Limite | UC-024 nominal | 🟠 Majeur | test_t03_03_variables_preserved |
| T03-04 | Ctrl+C pendant INPUT → entrée annulée, BREAK affiché | Erreur | UC-024 exc. 1a | 🟠 Majeur | test_t03_04_interrupt_during_input |

### ENF — Performance

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T04-01 | Boucle infinie + Ctrl+C → interruption < 500ms | Performance | CA-ENF-002-03 | 🟠 Majeur | test_t04_01_interrupt_latency |

### Transversal — DebugTracer

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T05-01 | Flag --debug → trace activée sur stderr | Nominal | ADR-006 | 🟠 Majeur | test_t05_01_debug_flag_enables_trace |
| T05-02 | DEBUG ON / DEBUG OFF dans le REPL | Nominal | ADR-006 | 🟠 Majeur | test_t05_02_debug_on_off_repl |
| T05-03 | Trace sur stderr, pas sur stdout | Limite | ADR-006 | 🟡 Mineur | test_t05_03_trace_on_stderr_only |
| T05-04 | Pas de trace quand debug désactivé | Limite | ADR-006 | 🟡 Mineur | test_t05_04_no_trace_when_disabled |

## Synthèse par sévérité

| Sévérité | Nombre |
|----------|--------|
| 🔴 Bloquant | 13 |
| 🟠 Majeur | 10 |
| 🟡 Mineur | 7 |
| **Total** | **30** |

## Tests manuels

Aucun test manuel requis — tous les scénarios sont automatisables.
