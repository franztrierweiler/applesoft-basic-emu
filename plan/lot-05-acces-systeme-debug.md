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
| Environment (`environment.py`) | Extension : état d'erreur (code, ligne, handler ONERR actif), protection anti-boucle infinie dans le handler |
| IOBridgeCLI (`io_cli.py`) | Extension : gestion SIGINT → flag d'interruption |
| DebugTracer (`debug.py`) | Création : trace d'exécution activable par `--debug` ou `DEBUG ON/OFF` |
| REPL (`repl.py`) | Extension : argument `--debug`, commandes `DEBUG ON` / `DEBUG OFF` |
| `__main__.py` | Extension : parsing argument `--debug` |

## Dépendances

- Lot 3 (structures de contrôle, pour tester ONERR/RESUME avec des programmes complets)

## Fonctionnalités

### F1 — MemoryMap (UC-022)

Carte mémoire émulée :
- Bytearray 64 Ko (65 536 octets), initialisé à 0
- PEEK(addr) → valeur 0-255, `?ILLEGAL QUANTITY ERROR` si addr hors 0-65535
- POKE addr, val → écriture, `?ILLEGAL QUANTITY ERROR` si val hors 0-255
- Soft-switches (RG-0011) :
  - PEEK(222) → code dernière erreur
  - PEEK(218-219) → numéro de ligne dernière erreur
  - PEEK(49152) → dernière touche (bit 7 = nouvelle)
  - POKE 49168,0 → reset strobe clavier
  - POKE 49200,0 → clic speaker (no-op)
  - PEEK(48) → mode texte/graphique
  - PEEK(103-104) → adresse début programme (émulée)
- CALL avec routines émulées :
  - CALL -936 → HOME
  - CALL -958 → CLREOL
  - CALL -868 → CLREOP
  - CALL 62450 → SETINV (INVERSE)
  - CALL 62454 → SETNORM (NORMAL)
- CALL adresse non émulée : avertissement configurable (SEC-SPE-02)

### F2 — ONERR GOTO / RESUME (UC-023)

- ONERR GOTO linenum : installe le handler
- Sur erreur → stocke code dans PEEK(222), ligne dans PEEK(218-219), saute au handler
- ONERR GOTO 0 : désactive le handler
- RESUME : reprend à l'instruction fautive
- Protection anti-boucle : si erreur dans le handler, affiche l'erreur et revient au prompt
- RESUME sans ONERR actif : `?SYNTAX ERROR`

### F3 — Interruption Ctrl+C (UC-024)

- SIGINT (Ctrl+C) → IOBridgeCLI positionne un flag
- L'Interpreter vérifie le flag à chaque instruction (via le compteur d'instructions, ADR-003)
- Si flag levé : affiche `BREAK IN linenum`, retour prompt
- État CONT sauvegardé (continuable)
- Ctrl+C pendant INPUT/GET : annule la saisie, `BREAK` affiché
- Temps de réaction < 500ms (ENF-002)

### F4 — DebugTracer (mode debug)

- Activable par `--debug` (CLI) ou `DEBUG ON` / `DEBUG OFF` (REPL)
- Affiche pour chaque instruction : numéro de ligne, instruction, et optionnellement l'état des variables
- Sortie sur stderr pour ne pas interférer avec la sortie BASIC
- Overhead négligeable (test d'un booléen par instruction)

## Critères d'acceptation

| AC | Description | Statut | Justification | Date |
|---|---|---|---|---|
| CA-UC-022-01 | ONERR + division par zéro + PEEK(222) → `133` | ⏳ | | |
| CA-UC-022-02 | `POKE 768,42 : PRINT PEEK(768)` → `42` | ⏳ | | |
| CA-UC-022-03 | `CALL -936` → écran effacé (= HOME) | ⏳ | | |
| CA-UC-022-04 | GET + PEEK(49152) → code touche avec bit 7 | ⏳ | | |
| CA-UC-022-05 | POKE 49168,0 → reset strobe clavier | ⏳ | | |
| CA-UC-023-01 | ONERR GOTO + erreur → handler exécuté, PEEK(222) correct | ⏳ | | |
| CA-UC-023-02 | ONERR GOTO 0 → handler désactivé, erreur affichée | ⏳ | | |
| CA-UC-023-03 | ONERR + RESUME → reprend à l'instruction fautive | ⏳ | | |
| CA-UC-024-01 | Boucle infinie + Ctrl+C → `BREAK IN linenum` | ⏳ | | |
| CA-UC-024-02 | Après Ctrl+C, CONT → reprend l'exécution | ⏳ | | |

## Prochaines actions

A implémenter via /sdd-dev-workflow lot-05-acces-systeme-debug
