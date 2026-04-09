# Lot 3 — Contrôle de flux et entrées utilisateur

## Objectif

Implémenter toutes les structures de contrôle (GOTO, IF/THEN/ELSE, ON...GOTO/GOSUB, FOR/NEXT, GOSUB/RETURN, POP) et les entrées utilisateur (INPUT, GET, DATA/READ/RESTORE). Après ce lot, tout programme BASIC non graphique sans fonctions intégrées peut s'exécuter.

## UC couverts

| UC | Intitulé | Priorité |
|---|---|---|
| UC-007 | Saisir des données | Critique |
| UC-008 | Utiliser DATA / READ / RESTORE | Critique |
| UC-012 | Brancher l'exécution | Critique |
| UC-013 | Boucler | Critique |
| UC-014 | Appeler des sous-programmes | Critique |

## Composants impactés

| Composant | Rôle dans ce lot |
|---|---|
| Interpreter (`interpreter.py`) | Extension : GOTO, IF/THEN/ELSE, ON...GOTO/GOSUB, FOR/NEXT, GOSUB/RETURN, POP, INPUT, GET, DATA, READ, RESTORE |
| Environment (`environment.py`) | Extension : pile GOSUB, pile FOR, pointeur DATA global, collecte des DATA à travers le programme |
| IOBridgeCLI (`io_cli.py`) | Extension : lecture d'entrée pour INPUT (avec invite), GET (un caractère sans écho) |

## Dépendances

- Lot 2 (Interpreter de base, Environment, PRINT)

## Fonctionnalités

### F1 — Branchements (UC-012)

- GOTO linenum : transfert à la ligne cible
- IF expr THEN action [ELSE action] : branchement conditionnel
  - action = numéro de ligne (GOTO implicite) ou instruction(s)
  - ELSE appartient au IF le plus récent sur la même ligne
  - IF imbriqués sur une même ligne
- ON expr GOTO line1,line2,... : branchement indexé (base 1)
- ON expr GOSUB line1,line2,... : appel indexé (base 1)
- Valeur hors plage pour ON : continue à l'instruction suivante
- Valeur négative pour ON : `?ILLEGAL QUANTITY ERROR`

### F2 — Boucles FOR/NEXT (UC-013)

- FOR var = start TO end [STEP step]
- NEXT [var] : incrémente et boucle
- NEXT I,J = NEXT I : NEXT J
- NEXT sans variable = boucle la plus récente
- STEP positif : continue tant que var <= end
- STEP négatif : continue tant que var >= end
- FOR I=1 TO 0 : corps exécuté une fois (test après exécution, fidèle Apple II)
- STEP 0 : boucle infinie (pas d'erreur)
- Pile FOR dans l'Environment

### F3 — Sous-programmes GOSUB/RETURN (UC-014)

- GOSUB linenum : empile adresse de retour, saute
- RETURN : dépile, reprend après le GOSUB
- POP : supprime l'adresse de retour sans revenir
- Appels imbriqués
- Pile GOSUB dans l'Environment

### F4 — Entrées INPUT et GET (UC-007)

- INPUT var : affiche `?`, lit une ligne, assigne
- INPUT "prompt";var : affiche le prompt personnalisé
- INPUT A,B : lecture de plusieurs valeurs séparées par virgule
- Valeurs insuffisantes : `??` pour redemander
- Trop de valeurs : `?EXTRA IGNORED`
- Type incorrect (numérique attendu, texte saisi) : `?REENTER`
- GET var$ : lit un caractère sans écho ni RETURN
- GET var (numérique) et touche non numérique : `?TYPE MISMATCH ERROR`

### F5 — DATA / READ / RESTORE (UC-008)

- DATA val1,val2,... : déclare des valeurs littérales
- READ var1,var2,... : lit les valeurs depuis le pointeur DATA global
- RESTORE : remet le pointeur au début
- Les DATA sont parcourues dans l'ordre des numéros de ligne
- Collecte de tous les DATA au moment du RUN
- READ au-delà des données : `?OUT OF DATA ERROR`
- Type mismatch : `?TYPE MISMATCH ERROR`

## Critères d'acceptation

| AC | Description | Statut | Justification | Date |
|---|---|---|---|---|
| CA-UC-007-01 | `INPUT A$ : PRINT A$` → saisie reflétée | ✅ | test_ca_uc_007_01_input_string | 2026-04-06 |
| CA-UC-007-02 | `INPUT "NAME";N$` → invite `NAME?` | ✅ | test_ca_uc_007_02_input_prompt | 2026-04-06 |
| CA-UC-007-03 | `INPUT A,B : PRINT A+B` → somme des deux valeurs | ✅ | test_ca_uc_007_03_input_multi | 2026-04-06 |
| CA-UC-007-04 | `GET A$ : PRINT A$` → caractère sans écho | ✅ | test_ca_uc_007_04_get_char | 2026-04-06 |
| CA-UC-008-01 | `DATA 1,2,3` / `READ A,B,C` / `PRINT A+B+C` → `6` | ✅ | test_ca_uc_008_01_data_read | 2026-04-06 |
| CA-UC-008-02 | DATA après READ → position sans importance | ✅ | test_ca_uc_008_02_data_position | 2026-04-06 |
| CA-UC-008-03 | RESTORE → relecture depuis le début | ✅ | test_ca_uc_008_03_restore | 2026-04-06 |
| CA-UC-012-01 | `GOTO 30` saute la ligne 20 | ✅ | test_ca_uc_012_01_goto_skips | 2026-04-06 |
| CA-UC-012-02 | `IF X>3 THEN PRINT "YES"` → conditionnel | ✅ | test_ca_uc_012_02_if_then_true | 2026-04-06 |
| CA-UC-012-03 | IF faux avec multi-commandes THEN → bloc entier sauté | ✅ | test_ca_uc_012_03_if_false_skips_block | 2026-04-06 |
| CA-UC-012-04 | `IF X>3 THEN ... ELSE ...` → branche ELSE | ✅ | test_ca_uc_012_04_if_else | 2026-04-06 |
| CA-UC-012-05 | `IF X>3 THEN 100` → GOTO implicite | ✅ | test_ca_uc_012_05_if_then_linenum | 2026-04-06 |
| CA-UC-012-06 | `ON X GOTO 100,200,300` → branchement indexé | ✅ | test_ca_uc_012_06_on_goto | 2026-04-06 |
| CA-UC-012-07 | IF imbriqués sur une même ligne | ✅ | test_ca_uc_012_07_if_nested | 2026-04-06 |
| CA-UC-013-01 | `FOR I=1 TO 3 : PRINT I : NEXT` → 1, 2, 3 | ✅ | test_ca_uc_013_01_for_next_basic | 2026-04-06 |
| CA-UC-013-02 | `FOR I=1 TO 10 STEP 3` → 1, 4, 7, 10 | ✅ | test_ca_uc_013_02_for_step | 2026-04-06 |
| CA-UC-013-03 | `FOR I=5 TO 1 STEP -1` → 5, 4, 3, 2, 1 | ✅ | test_ca_uc_013_03_for_step_negative | 2026-04-06 |
| CA-UC-013-04 | Boucles imbriquées avec `NEXT J,I` | ✅ | test_ca_uc_013_04_nested_next_ji | 2026-04-06 |
| CA-UC-014-01 | GOSUB + RETURN → retour après GOSUB | ✅ | test_ca_uc_014_01_gosub_return | 2026-04-06 |
| CA-UC-014-02 | GOSUB imbriqués | ✅ | test_ca_uc_014_02_gosub_nested | 2026-04-06 |
| CA-UC-014-03 | POP + GOTO au lieu de RETURN | ✅ | test_ca_uc_014_03_pop_goto | 2026-04-06 |
| CA-UC-014-04 | ON X GOSUB → appel indexé avec RETURN | ✅ | test_ca_uc_014_04_on_gosub | 2026-04-06 |

## Prochaines actions

Lot terminé — prêt pour QA
