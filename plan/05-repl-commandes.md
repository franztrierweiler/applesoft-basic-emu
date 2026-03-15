# EPIC 05 — REPL + Commandes système

**Statut :** ⏳ Non démarré
**Priorité :** Critique
**Dépendances :** EPIC 04 (Interpreter noyau)
**Référence :** ARCHITECTURE.md § 4.1 (REPL, IOBridgeCLI) — SPEC.md EXG-001 à EXG-010

## Objectif

Implémenter la boucle interactive REPL (prompt `]`, mode direct/différé) et les commandes système (RUN, LIST, NEW, DEL, SAVE, LOAD, CONT). Implémenter l'IOBridgeCLI pour les E/S terminal. À la fin de cet EPIC, on peut saisir un programme ligne par ligne, le lister, l'exécuter, le sauvegarder et le recharger.

## Tâches

| # | Tâche | Statut |
|---|-------|--------|
| 5.1 | Implémenter `REPL` : boucle principale, affichage prompt `]`, lecture ligne | ⏳ |
| 5.2 | Implémenter le dispatch mode direct (pas de numéro) / mode différé (numéro de ligne) | ⏳ |
| 5.3 | Implémenter le stockage du programme en mémoire (`Program` : dict trié par numéro de ligne, insertion, remplacement, suppression) | ⏳ |
| 5.4 | Implémenter la commande `RUN` (reset environment, collecte DATA, lancement run-loop step) | ⏳ |
| 5.5 | Implémenter la commande `LIST` (LIST, LIST n, LIST n-m, LIST -m, LIST n-) | ⏳ |
| 5.6 | Implémenter la commande `NEW` (effacement programme + variables) | ⏳ |
| 5.7 | Implémenter la commande `DEL start,end` | ⏳ |
| 5.8 | Implémenter la commande `SAVE "filename"` (écriture fichier texte format LIST) | ⏳ |
| 5.9 | Implémenter la commande `LOAD "filename"` (lecture fichier, remplacement programme) | ⏳ |
| 5.10 | Implémenter la commande `CONT` (reprise après STOP/END/Ctrl+C) | ⏳ |
| 5.11 | Implémenter `IOBridgeCLI` : output (stdout), input (stdin), fichiers (SAVE/LOAD) | ⏳ |
| 5.12 | Implémenter `main.py` : point d'entrée, argument parsing (mode REPL ou fichier .bas) | ⏳ |
| 5.13 | Implémenter la troncature des lignes à 239 caractères (CL-002-03) | ⏳ |
| 5.14 | Tests unitaires et d'intégration pour toutes les exigences couvertes | ⏳ |

## Exigences couvertes

| Exigence | Description | Statut tests |
|----------|-------------|-------------|
| EXG-001 | Boucle interactive REPL | ⏳ |
| EXG-002 | Stockage et gestion des lignes de programme | ⏳ |
| EXG-003 | Commande RUN | ⏳ |
| EXG-004 | Commande LIST | ⏳ |
| EXG-005 | Commande NEW | ⏳ |
| EXG-006 | Commande DEL | ⏳ |
| EXG-007 | Commande SAVE | ⏳ |
| EXG-008 | Commande LOAD | ⏳ |
| EXG-009 | Commande CONT | ⏳ |
| EXG-010 | Instructions multi-commandes (séparateur `:`) | ⏳ |

## Critères d'acceptation (extraits SPEC.md)

| CA | Description | Statut |
|----|-------------|--------|
| CA-001-01 | Démarrage → prompt `]` affiché | ⏳ |
| CA-001-02 | `PRINT "HELLO"` en mode direct → `HELLO` affiché + prompt | ⏳ |
| CA-001-03 | `10 PRINT "HELLO"` → stocké sans exécution + prompt | ⏳ |
| CA-002-01 | Lignes stockées dans l'ordre croissant des numéros | ⏳ |
| CA-002-02 | Remplacement de ligne existante | ⏳ |
| CA-002-03 | Numéro seul → suppression de la ligne | ⏳ |
| CA-003-01 | `RUN` exécute dans l'ordre des numéros de ligne | ⏳ |
| CA-003-02 | `RUN 20` commence à la ligne 20 | ⏳ |
| CA-003-03 | `RUN` réinitialise les variables | ⏳ |
| CA-004-01 | `LIST` affiche tout le programme | ⏳ |
| CA-004-02 | `LIST 20` affiche une seule ligne | ⏳ |
| CA-005-01 | `NEW` efface programme et variables | ⏳ |
| CA-006-01 | `DEL 10,20` supprime les lignes 10 à 20 | ⏳ |
| CA-007-01 | `SAVE "TEST.BAS"` crée un fichier texte | ⏳ |
| CA-008-01 | `LOAD "TEST.BAS"` charge le programme | ⏳ |
| CA-009-01 | `CONT` reprend après STOP | ⏳ |
| CA-010-01 | `PRINT "A" : PRINT "B"` → A puis B | ⏳ |

## Cas limites à tester

| CL | Description | Statut |
|----|-------------|--------|
| CL-001-01 | Ligne vide → prompt réaffiché | ⏳ |
| CL-001-02 | Erreur de syntaxe en mode direct → `?SYNTAX ERROR` + prompt | ⏳ |
| CL-002-01 | Numéro > 63999 → `?SYNTAX ERROR` | ⏳ |
| CL-002-03 | Ligne > 239 caractères → tronquée | ⏳ |
| CL-003-01 | `RUN` sans programme → prompt sans erreur | ⏳ |
| CL-003-02 | `RUN 99` ligne inexistante → `?UNDEF'D STATEMENT ERROR` | ⏳ |
| CL-004-01 | `LIST` sans programme → rien affiché | ⏳ |
| CL-008-01 | `LOAD "INEXISTANT"` → `?FILE NOT FOUND` | ⏳ |
| CL-009-01 | `CONT` sans programme interrompu → `?CAN'T CONTINUE ERROR` | ⏳ |
| CL-009-02 | `CONT` après modification programme → `?CAN'T CONTINUE ERROR` | ⏳ |

## Livrables

- `src/repl.py` — boucle REPL
- `src/io_bridge_cli.py` — IOBridge CLI
- `src/main.py` — point d'entrée
- `tests/unit/test_repl.py`
- `tests/integration/test_programs.py` (premiers tests de bout en bout)
