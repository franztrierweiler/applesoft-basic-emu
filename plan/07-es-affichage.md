# EPIC 07 — E/S et affichage

**Statut :** ⏳ Non démarré
**Priorité :** Critique
**Dépendances :** EPIC 05 (REPL + Commandes)
**Référence :** ARCHITECTURE.md § 4.1 (Interpreter, IOBridge) — SPEC.md EXG-011 à EXG-021

## Objectif

Implémenter les instructions d'entrées/sorties texte (PRINT complet, INPUT, GET, DATA/READ/RESTORE) et les instructions d'affichage (HTAB, VTAB, HOME, NORMAL/INVERSE/FLASH, SPEED=, POS, REM, TEXT). Implémenter le DataCollector pour le scan pré-exécution des DATA.

## Tâches

| # | Tâche | Statut |
|---|-------|--------|
| 7.1 | Compléter PRINT : séparateurs `;` et `,` (tabulation 16 colonnes), `;` final supprime retour ligne, `?` alias | ⏳ |
| 7.2 | Implémenter SPC(n) et TAB(n) dans PRINT | ⏳ |
| 7.3 | Implémenter INPUT (prompt optionnel, multi-variables, REENTER, EXTRA IGNORED) | ⏳ |
| 7.4 | Implémenter GET (lecture un caractère sans RETURN, sans écho) dans IOBridgeCLI (mode raw terminal) | ⏳ |
| 7.5 | Implémenter `DataCollector` : scan pré-exécution de l'AST, collecte DATA dans l'ordre des numéros de ligne | ⏳ |
| 7.6 | Implémenter DATA, READ, RESTORE dans l'Interpreter | ⏳ |
| 7.7 | Implémenter HTAB et VTAB (positionnement curseur) | ⏳ |
| 7.8 | Implémenter HOME (effacement écran, curseur en 1,1) | ⏳ |
| 7.9 | Implémenter NORMAL, INVERSE, FLASH (modes d'affichage dans Environment + IOBridge) | ⏳ |
| 7.10 | Implémenter SPEED= (délai par caractère) | ⏳ |
| 7.11 | Implémenter POS(n) (position curseur horizontale, argument ignoré) | ⏳ |
| 7.12 | Implémenter REM (commentaire, `:` fait partie du commentaire) | ⏳ |
| 7.13 | Implémenter TEXT (retour mode texte plein écran) | ⏳ |
| 7.14 | Enrichir IOBridgeCLI : codes ANSI pour INVERSE/FLASH, positionnement curseur, HOME | ⏳ |
| 7.15 | Tests unitaires pour toutes les exigences couvertes | ⏳ |

## Exigences couvertes

| Exigence | Description | Statut tests |
|----------|-------------|-------------|
| EXG-011 | PRINT (séparateurs, alias ?) | ⏳ |
| EXG-012 | INPUT | ⏳ |
| EXG-013 | GET | ⏳ |
| EXG-014 | DATA / READ / RESTORE | ⏳ |
| EXG-015 | SPC et TAB dans PRINT | ⏳ |
| EXG-016 | HTAB / VTAB | ⏳ |
| EXG-017 | HOME | ⏳ |
| EXG-018 | NORMAL / INVERSE / FLASH | ⏳ |
| EXG-019 | REM | ⏳ |
| EXG-020 | SPEED= | ⏳ |
| EXG-021 | POS | ⏳ |
| EXG-053 | TEXT | ⏳ |

## Critères d'acceptation (extraits SPEC.md)

| CA | Description | Statut |
|----|-------------|--------|
| CA-011-01 | `PRINT "HELLO"` → `HELLO` + retour ligne | ⏳ |
| CA-011-02 | `PRINT "A";"B"` → `AB` | ⏳ |
| CA-011-03 | `PRINT "A","B"` → tabulation 16 colonnes | ⏳ |
| CA-011-04 | `;` final supprime retour ligne | ⏳ |
| CA-011-05 | `PRINT` seul → ligne vide | ⏳ |
| CA-012-01 | `INPUT A$` → prompt `?`, lecture valeur | ⏳ |
| CA-012-02 | `INPUT "NAME";N$` → prompt `NAME?` | ⏳ |
| CA-013-01 | `GET A$` → lecture un caractère sans écho | ⏳ |
| CA-014-01 | `DATA 1,2,3` + `READ A,B,C` → 6 | ⏳ |
| CA-014-02 | DATA après READ dans le code → fonctionne (global) | ⏳ |
| CA-014-03 | RESTORE remet le pointeur au début | ⏳ |
| CA-015-01 | `SPC(5);"X"` → 5 espaces + X | ⏳ |
| CA-015-02 | `TAB(10);"X"` → X en colonne 10 | ⏳ |
| CA-016-01 | HTAB 10 positionne en colonne 10 | ⏳ |
| CA-017-01 | HOME efface l'écran | ⏳ |
| CA-018-01 | INVERSE + NORMAL fonctionnent | ⏳ |
| CA-019-01 | REM ignoré à l'exécution | ⏳ |
| CA-019-02 | `REM TEXTE : PRINT "CACHÉ"` → rien affiché | ⏳ |
| CA-021-01 | `POS(0)` retourne la position curseur | ⏳ |

## Livrables

- `src/data_collector.py` — collecteur DATA pré-exécution
- `src/interpreter.py` — enrichi avec E/S et affichage
- `src/io_bridge_cli.py` — enrichi (raw terminal, ANSI)
- `tests/unit/test_data_collector.py`
- `tests/unit/test_interpreter.py` — enrichi
