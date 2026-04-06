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
| CA-UC-007-01 | `INPUT A$ : PRINT A$` → saisie reflétée | ⏳ | | |
| CA-UC-007-02 | `INPUT "NAME";N$` → invite `NAME?` | ⏳ | | |
| CA-UC-007-03 | `INPUT A,B : PRINT A+B` → somme des deux valeurs | ⏳ | | |
| CA-UC-007-04 | `GET A$ : PRINT A$` → caractère sans écho | ⏳ | | |
| CA-UC-008-01 | `DATA 1,2,3` / `READ A,B,C` / `PRINT A+B+C` → `6` | ⏳ | | |
| CA-UC-008-02 | DATA après READ → position sans importance | ⏳ | | |
| CA-UC-008-03 | RESTORE → relecture depuis le début | ⏳ | | |
| CA-UC-012-01 | `GOTO 30` saute la ligne 20 | ⏳ | | |
| CA-UC-012-02 | `IF X>3 THEN PRINT "YES"` → conditionnel | ⏳ | | |
| CA-UC-012-03 | IF faux avec multi-commandes THEN → bloc entier sauté | ⏳ | | |
| CA-UC-012-04 | `IF X>3 THEN ... ELSE ...` → branche ELSE | ⏳ | | |
| CA-UC-012-05 | `IF X>3 THEN 100` → GOTO implicite | ⏳ | | |
| CA-UC-012-06 | `ON X GOTO 100,200,300` → branchement indexé | ⏳ | | |
| CA-UC-012-07 | IF imbriqués sur une même ligne | ⏳ | | |
| CA-UC-013-01 | `FOR I=1 TO 3 : PRINT I : NEXT` → 1, 2, 3 | ⏳ | | |
| CA-UC-013-02 | `FOR I=1 TO 10 STEP 3` → 1, 4, 7, 10 | ⏳ | | |
| CA-UC-013-03 | `FOR I=5 TO 1 STEP -1` → 5, 4, 3, 2, 1 | ⏳ | | |
| CA-UC-013-04 | Boucles imbriquées avec `NEXT J,I` | ⏳ | | |
| CA-UC-014-01 | GOSUB + RETURN → retour après GOSUB | ⏳ | | |
| CA-UC-014-02 | GOSUB imbriqués | ⏳ | | |
| CA-UC-014-03 | POP + GOTO au lieu de RETURN | ⏳ | | |
| CA-UC-014-04 | ON X GOSUB → appel indexé avec RETURN | ⏳ | | |

## Prochaines actions

A implémenter via /sdd-dev-workflow lot-03-controle-flux-entrees
