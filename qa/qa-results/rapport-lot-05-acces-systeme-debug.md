# Rapport QA -- lot-05-acces-systeme-debug

**Date :** 2026-04-09
**Lot :** lot-05-acces-systeme-debug
**Verdict :** ✅ VALIDE

## Resume
- Tests unitaires (dev) : 42/42 passes
- Scenarios QA : 32/32 passes
  - 🔴 Bloquants : 13/13 passes
  - 🟠 Majeurs : 12/12 passes
  - 🟡 Mineurs : 7/7 passes
- Revue de code : 7 constats (0 🔴, 1 🟠, 6 🟡)

## Scenarios en echec

Aucun.

## Detail des scenarios QA

### UC-022 -- Lire/ecrire la memoire (PEEK/POKE/CALL)

| # | Severite | Description | Resultat |
|---|----------|-------------|----------|
| T01-01 | 🔴 | POKE 768,42 puis PEEK(768) -> 42 | ✅ |
| T01-02 | 🔴 | ONERR + div/0 + PEEK(222) -> 133 | ✅ |
| T01-03 | 🔴 | CALL -936 -> HOME | ✅ |
| T01-04 | 🔴 | PEEK(49152) -> code touche bit 7 | ✅ |
| T01-05 | 🟠 | POKE 49168 -> reset strobe | ✅ |
| T01-06 | 🔴 | PEEK(-1) -> ILLEGAL QUANTITY | ✅ |
| T01-07 | 🔴 | PEEK(65536) -> ILLEGAL QUANTITY | ✅ |
| T01-08 | 🔴 | POKE 768,256 -> ILLEGAL QUANTITY | ✅ |
| T01-09 | 🔴 | POKE 768,-1 -> ILLEGAL QUANTITY | ✅ |
| T01-10 | 🔴 | POKE 65536,0 -> ILLEGAL QUANTITY | ✅ |
| T01-11 | 🟠 | CALL 65536 -> ILLEGAL QUANTITY | ✅ |
| T01-12 | 🟡 | CALL 12345 -> avertissement stderr | ✅ |
| T01-13 | 🟡 | PEEK ROM non emulee -> 0 | ✅ |
| T01-14 | 🟠 | PEEK(218-219) -> ligne erreur | ✅ |
| T01-15 | 🟡 | PEEK(48) -> mode texte | ✅ |
| T01-16 | 🟡 | PEEK(103-104) -> 0x0801 | ✅ |
| T01-17 | 🟡 | POKE 49200 speaker no-op | ✅ |

### UC-023 -- Gerer les erreurs (ONERR GOTO / RESUME)

| # | Severite | Description | Resultat |
|---|----------|-------------|----------|
| T02-01 | 🔴 | ONERR handler execute + PEEK(222) | ✅ |
| T02-02 | 🔴 | ONERR GOTO 0 desactive handler | ✅ |
| T02-03 | 🔴 | RESUME re-execute instruction fautive | ✅ |
| T02-04 | 🟠 | ONERR GOTO 999 -> UNDEF'D STATEMENT | ✅ |
| T02-05 | 🔴 | Erreur dans handler -> anti-boucle | ✅ |
| T02-06 | 🟠 | RESUME sans ONERR -> SYNTAX ERROR | ✅ |

### UC-024 -- Interrompre l'execution (Ctrl+C)

| # | Severite | Description | Resultat |
|---|----------|-------------|----------|
| T03-01 | 🔴 | BREAK IN linenum | ✅ |
| T03-02 | 🔴 | CONT apres BREAK | ✅ |
| T03-03 | 🟠 | Variables preservees | ✅ |
| T03-04 | 🟠 | Ctrl+C pendant INPUT | ✅ |

### ENF-002 -- Performance

| # | Severite | Description | Resultat |
|---|----------|-------------|----------|
| T04-01 | 🟠 | Latence interruption < 500ms | ✅ |

### DebugTracer (ADR-006)

| # | Severite | Description | Resultat |
|---|----------|-------------|----------|
| T05-01 | 🟠 | --debug active trace stderr | ✅ |
| T05-02 | 🟠 | DEBUG ON/OFF dans REPL | ✅ |
| T05-03 | 🟡 | Trace sur stderr uniquement | ✅ |
| T05-04 | 🟡 | Pas de trace si desactive | ✅ |

## Constats de revue a corriger

| # | Severite | Constat | Impact |
|---|----------|---------|--------|
| R01 | 🟠 | interpreter.py fait 1045 lignes (limite 500) | Non bloquant mais a traiter dans un lot de refactoring |

## Points d'attention (🟡 mineurs)

- R02 : Avertissement CALL non emule pourrait utiliser DebugTracer
- R03 : `_exec_stmt` pourrait utiliser un dictionnaire de dispatch
- R04 : `get_char()` ne met pas a jour `_last_key` pour fidelite Apple II
- R05 : `_execute_from` est complexe (130 lignes, imbrication profonde)
- R06 : Methodes d'etat d'erreur manquent de tests unitaires dedies
- R07 : Overhead debug check a chaque instruction (negligeable)

## References
- Plan de test : qa/plan-test/lot-05-acces-systeme-debug.md
- Revue de code : qa/code-review/lot-05-acces-systeme-debug-review.md
- Plan du lot : plan/lot-05-acces-systeme-debug.md
