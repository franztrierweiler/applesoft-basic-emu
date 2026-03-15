# EPIC 12 — Accès mémoire

**Statut :** ⏳ Non démarré
**Priorité :** Important
**Dépendances :** EPIC 05 (REPL + Commandes)
**Référence :** ARCHITECTURE.md § 4.1 (MemoryMap) — SPEC.md EXG-061 à EXG-064

## Objectif

Implémenter l'espace mémoire émulé Apple II : PEEK, POKE, CALL et la table des adresses à effets de bord (soft-switches). À la fin de cet EPIC, `PEEK(222)` retourne le code d'erreur, `POKE 768,42 : PRINT PEEK(768)` fonctionne, et `CALL -936` efface l'écran.

## Tâches

| # | Tâche | Statut |
|---|-------|--------|
| 12.1 | Implémenter `MemoryMap` : espace 64K sparse (dict), lecture/écriture générique | ⏳ |
| 12.2 | Implémenter la dispatch table PEEK : adresses à effet de bord (222, 218-219, 49152, 49168, 48, 103-104) | ⏳ |
| 12.3 | Implémenter la dispatch table POKE : adresses à effet de bord (49168, 49200) | ⏳ |
| 12.4 | Implémenter la dispatch table CALL : adresses émulées (-936/HOME, -958/CLREOL, -868/CLREOP, 62450/SETINV, 62454/SETNORM) | ⏳ |
| 12.5 | Implémenter PEEK dans l'Interpreter (validation adresse 0-65535) | ⏳ |
| 12.6 | Implémenter POKE dans l'Interpreter (validation adresse 0-65535, valeur 0-255) | ⏳ |
| 12.7 | Implémenter CALL dans l'Interpreter (validation adresse, dispatch ou avertissement) | ⏳ |
| 12.8 | Connecter MemoryMap à Environment (error state pour PEEK(222), clavier pour PEEK(49152)) | ⏳ |
| 12.9 | Implémenter le comportement par défaut : PEEK sur adresse non émulée → 0, POKE non émulé → no-op | ⏳ |
| 12.10 | Tests unitaires pour toutes les exigences couvertes | ⏳ |

## Exigences couvertes

| Exigence | Description | Statut tests |
|----------|-------------|-------------|
| EXG-061 | PEEK | ⏳ |
| EXG-062 | POKE | ⏳ |
| EXG-063 | CALL | ⏳ |
| EXG-064 | Table des adresses mémoire émulées | ⏳ |

## Critères d'acceptation (extraits SPEC.md)

| CA | Description | Statut |
|----|-------------|--------|
| CA-061-01 | `ONERR GOTO 100` + `1/0` + `PEEK(222)` → 133 | ⏳ |
| CA-061-02 | `POKE 768,42 : PRINT PEEK(768)` → 42 | ⏳ |
| CA-062-01 | `POKE 768,255 : PRINT PEEK(768)` → 255 | ⏳ |
| CA-062-02 | `POKE 49168,0` → strobe clavier réinitialisé | ⏳ |
| CA-063-01 | `CALL -936` → écran effacé (HOME) | ⏳ |
| CA-064-01 | `GET A$ : PRINT PEEK(49152)` → code touche + bit 7 | ⏳ |
| CA-064-02 | `POKE 49168,0 : PRINT PEEK(49152)` → bit 7 à 0 | ⏳ |

## Cas limites à tester

| CL | Description | Statut |
|----|-------------|--------|
| CL-061-01 | `PEEK(65536)` → `?ILLEGAL QUANTITY ERROR` | ⏳ |
| CL-061-02 | `PEEK(-1)` → `?ILLEGAL QUANTITY ERROR` | ⏳ |
| CL-061-03 | PEEK sur adresse non émulée → 0 | ⏳ |
| CL-062-01 | `POKE 768,256` → `?ILLEGAL QUANTITY ERROR` | ⏳ |
| CL-062-02 | `POKE 768,-1` → `?ILLEGAL QUANTITY ERROR` | ⏳ |
| CL-063-01 | `CALL 65536` → `?ILLEGAL QUANTITY ERROR` | ⏳ |
| CL-064-01 | PEEK/POKE sur adresse non documentée → défaut silencieux | ⏳ |

## Livrables

- `src/memory_map.py` — espace mémoire émulé
- `src/interpreter.py` — enrichi (PEEK, POKE, CALL)
- `tests/unit/test_memory_map.py`
