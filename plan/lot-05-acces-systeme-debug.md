# Lot 5 — Accès système, gestion d'erreurs et debug

## Objectif

Implémenter la carte mémoire émulée (MemoryMap 64 Ko), les instructions PEEK/POKE/CALL avec soft-switches, le gestionnaire d'erreurs ONERR GOTO / RESUME, l'interruption Ctrl+C, et le mode debug (DebugTracer). Ce lot est prérequis pour le graphisme (lot 6) car les shape tables sont chargées via POKE dans la MemoryMap.

## UC couverts

| UC | Intitulé | Priorité |
|---|---|---|
| UC-022 | Lire/écrire la mémoire | Important |
| UC-023 | Gérer les erreurs d'exécution | Important |
| UC-024 | Interrompre l'exécution | Important |

## Composants impactés

| Composant | Rôle dans ce lot |
|---|---|
| MemoryMap (`memory.py`) | Création : bytearray 64 Ko, handlers de soft-switches (RG-0011), intercept PEEK/POKE/CALL sur adresses documentées |
| Interpreter (`interpreter.py`) | Extension : PEEK, POKE, CALL, ONERR GOTO, RESUME, vérification flag interruption |
| Environment (`environment.py`) | Extension : état d'erreur (code, ligne, handler ONERR actif), protection anti-boucle dans le handler |
| IOBridgeCLI (`io_cli.py`) | Extension : gestion SIGINT → flag d'interruption, last_key pour $C000 |
| DebugTracer (`debug.py`) | Création : trace d'exécution activable par `--debug` ou `DEBUG ON/OFF` |
| REPL (`repl.py`) | Extension : argument `--debug`, commandes `DEBUG ON` / `DEBUG OFF` |
| `__main__.py` | Extension : parsing argument `--debug` |

## Dépendances

- Lot 3 (structures de contrôle, pour tester ONERR/RESUME avec des programmes complets)

## Fonctionnalités

### F1 — MemoryMap (UC-022) ✅

Carte mémoire émulée :
- Bytearray 64 Ko (65 536 octets), initialisé à 0
- PEEK(addr) → valeur 0-255, `?ILLEGAL QUANTITY ERROR` si addr hors 0-65535
- POKE addr, val → écriture, `?ILLEGAL QUANTITY ERROR` si val hors 0-255
- Soft-switches (RG-0011) : PEEK(222), PEEK(218-219), PEEK(49152), POKE 49168, POKE 49200, PEEK(48), PEEK(103-104)
- CALL avec routines émulées : -936 (HOME), -958 (CLREOL), -868 (CLREOP), 62450 (SETINV), 62454 (SETNORM)
- CALL adresse non émulée : avertissement sur stderr (SEC-SPE-02)

### F2 — ONERR GOTO / RESUME (UC-023) ✅

- ONERR GOTO linenum : installe le handler
- Sur erreur → stocke code dans PEEK(222), ligne dans PEEK(218-219), saute au handler
- ONERR GOTO 0 : désactive le handler
- RESUME : reprend à l'instruction fautive
- Protection anti-boucle : erreur dans le handler OU RESUME vers la même erreur → affiche l'erreur et remonte

### F3 — Interruption Ctrl+C (UC-024) ✅

- SIGINT (Ctrl+C) → IOBridgeCLI positionne un flag via signal handler
- L'Interpreter vérifie le flag à chaque instruction (via le compteur d'instructions, ADR-003)
- Si flag levé : affiche `BREAK IN linenum`, retour prompt
- État CONT sauvegardé (continuable)

### F4 — DebugTracer (mode debug) ✅

- Activable par `--debug` (CLI) ou `DEBUG ON` / `DEBUG OFF` (REPL)
- Affiche pour chaque instruction : numéro de ligne et type d'instruction
- Sortie sur stderr pour ne pas interférer avec la sortie BASIC
- Overhead négligeable (test d'un booléen par instruction)

## Statut des critères d'acceptation

| AC | Description | Statut | Justification | Date |
|---|---|---|---|---|
| CA-UC-022-01 | ONERR + division par zéro + PEEK(222) → `133` | ✅ | test_ca_uc_022_01_onerr_division_by_zero_peek222 passe | 2026-04-06 |
| CA-UC-022-02 | `POKE 768,42 : PRINT PEEK(768)` → `42` | ✅ | test_ca_uc_022_02_poke_peek_roundtrip passe | 2026-04-06 |
| CA-UC-022-03 | `CALL -936` → écran effacé (= HOME) | ✅ | test_ca_uc_022_03_call_minus_936_home passe | 2026-04-06 |
| CA-UC-022-04 | GET + PEEK(49152) → code touche avec bit 7 | ✅ | test_ca_uc_022_04_peek_49152_keyboard passe | 2026-04-06 |
| CA-UC-022-05 | POKE 49168,0 → reset strobe clavier | ✅ | test_ca_uc_022_05_poke_49168_reset_strobe passe | 2026-04-06 |
| CA-UC-023-01 | ONERR GOTO + erreur → handler exécuté, PEEK(222) correct | ✅ | test_ca_uc_023_01_onerr_handler_executed passe | 2026-04-06 |
| CA-UC-023-02 | ONERR GOTO 0 → handler désactivé, erreur affichée | ✅ | test_ca_uc_023_02_onerr_goto_0_disables passe | 2026-04-06 |
| CA-UC-023-03 | ONERR + RESUME → reprend à l'instruction fautive | ✅ | test_ca_uc_023_03_resume_retries_faulting_instruction passe | 2026-04-06 |
| CA-UC-024-01 | Boucle infinie + Ctrl+C → `BREAK IN linenum` | ✅ | test_ca_uc_024_01_break_in_linenum passe | 2026-04-06 |
| CA-UC-024-02 | Après Ctrl+C, CONT → reprend l'exécution | ✅ | test_ca_uc_024_02_cont_after_break passe | 2026-04-06 |

## Prochaines actions

Lot terminé — prêt pour QA
