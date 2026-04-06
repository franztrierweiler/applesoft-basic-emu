# Lot 4 — Fonctions intégrées, affichage avancé et persistance

## Objectif

Compléter le langage BASIC hors graphisme : fonctions mathématiques et de chaînes, fonctions utilisateur (DEF FN), contrôle de l'affichage (HTAB, VTAB, HOME, INVERSE, FLASH, SPEED=), et persistance fichier (SAVE/LOAD). Après ce lot, l'émulateur est pleinement fonctionnel pour tout programme texte Applesoft BASIC.

## UC couverts

| UC | Intitulé | Priorité |
|---|---|---|
| UC-009 | Contrôler l'affichage | Important |
| UC-015 | Utiliser les fonctions mathématiques | Critique |
| UC-016 | Utiliser les fonctions de chaînes | Critique |
| UC-017 | Définir une fonction utilisateur | Important |
| UC-004 | Sauvegarder un programme | Important |
| UC-005 | Charger un programme | Important |

## Composants impactés

| Composant | Rôle dans ce lot |
|---|---|
| Interpreter (`interpreter.py`) | Extension : fonctions intégrées (math, chaînes, conversion), DEF FN / FN, HTAB, VTAB, HOME, NORMAL, INVERSE, FLASH, SPEED= |
| Environment (`environment.py`) | Extension : définitions FN, état affichage (curseur, mode vidéo, vitesse) |
| REPL (`repl.py`) | Extension : commandes SAVE et LOAD |
| IOBridgeCLI (`io_cli.py`) | Extension : SAVE/LOAD fichier, INVERSE/FLASH en ANSI, HOME (clear screen), restriction de chemin (SEC-BP-22) |

## Dépendances

- Lot 3 (structures de contrôle complètes)

## Fonctionnalités

### F1 — Fonctions mathématiques (UC-015)

ABS, INT (arrondi vers le bas), SGN, SQR, LOG, EXP, SIN, COS, TAN, ATN (radians).
RND : n>0 → nouveau [0,1), n=0 → répète le dernier, n<0 → réinitialise la graine.

### F2 — Fonctions de chaînes (UC-016)

LEN, LEFT$, RIGHT$, MID$ (base 1), ASC, CHR$, STR$, VAL.
VAL("HELLO") → 0, VAL("3ABC") → 3. ASC("") → `?ILLEGAL QUANTITY ERROR`.

### F3 — Fonctions utilisateur DEF FN (UC-017)

- DEF FN name(param) = expression
- FN name(value) → évalue l'expression avec la valeur
- Un seul paramètre
- L'expression peut référencer les variables globales
- FN sans DEF : `?UNDEF'D FUNCTION ERROR`
- Erreur dans l'expression détectée à l'appel, pas à la définition

### F4 — Contrôle de l'affichage (UC-009)

- HTAB n (colonne 1-40) : `?ILLEGAL QUANTITY ERROR` si hors bornes
- VTAB n (ligne 1-24) : idem
- HOME : efface l'écran, curseur en (1,1)
- NORMAL : mode texte normal
- INVERSE : mode texte inversé (ANSI reverse video)
- FLASH : mode texte clignotant (ANSI blink)
- SPEED= n (0-255) : délai entre caractères

### F5 — Persistance fichier SAVE/LOAD (UC-004, UC-005)

- SAVE "filename" : détokenise le programme, écrit en fichier texte
- LOAD "filename" : lit le fichier, tokenise chaque ligne, remplace le programme
- SAVE sans nom : `?SYNTAX ERROR`
- LOAD sans nom : `?SYNTAX ERROR`
- Fichier inexistant : `?FILE NOT FOUND`
- Fichier existant écrasé sans avertissement (fidèle Apple II)
- LOAD réinitialise les variables
- Restriction de chemin au répertoire projet (SEC-BP-22)
- Validation du contenu des fichiers (SEC-BP-23)
- Limite taille 1 Mo (SEC-BP-25)

## Critères d'acceptation

| AC | Description | Statut | Justification | Date |
|---|---|---|---|---|
| CA-UC-009-01 | `HTAB 10 : PRINT "X"` → X en colonne 10 | ⏳ | | |
| CA-UC-009-02 | `VTAB 12 : HTAB 20 : PRINT "X"` → position (12,20) | ⏳ | | |
| CA-UC-009-03 | HOME → écran vidé, curseur en (1,1) | ⏳ | | |
| CA-UC-009-04 | INVERSE + PRINT → mode inversé | ⏳ | | |
| CA-UC-009-05 | FLASH + PRINT → attribut clignotant | ⏳ | | |
| CA-UC-009-06 | `SPEED=100 : PRINT "SLOW"` → délai visible | ⏳ | | |
| CA-UC-015-01 | `PRINT ABS(-5)` → `5` | ⏳ | | |
| CA-UC-015-02 | `PRINT INT(3.7)` → `3` | ⏳ | | |
| CA-UC-015-03 | `PRINT INT(-3.7)` → `-4` (arrondi vers le bas) | ⏳ | | |
| CA-UC-015-04 | `PRINT SQR(16)` → `4` | ⏳ | | |
| CA-UC-015-05 | `PRINT SGN(-42)` → `-1` | ⏳ | | |
| CA-UC-015-06 | RND(1) → deux valeurs différentes | ⏳ | | |
| CA-UC-015-07 | RND(-5) + RND(1) → graine déterministe | ⏳ | | |
| CA-UC-015-08 | RND(0) → répète le dernier | ⏳ | | |
| CA-UC-016-01 | `PRINT LEN("HELLO")` → `5` | ⏳ | | |
| CA-UC-016-02 | `PRINT LEFT$("HELLO",3)` → `HEL` | ⏳ | | |
| CA-UC-016-03 | `PRINT RIGHT$("HELLO",3)` → `LLO` | ⏳ | | |
| CA-UC-016-04 | `PRINT MID$("HELLO",2,3)` → `ELL` | ⏳ | | |
| CA-UC-016-05 | `PRINT ASC("A")` → `65` | ⏳ | | |
| CA-UC-016-06 | `PRINT CHR$(65)` → `A` | ⏳ | | |
| CA-UC-016-07 | `PRINT VAL("3.14")` → `3.14` | ⏳ | | |
| CA-UC-016-08 | `PRINT STR$(42)` → `" 42"` | ⏳ | | |
| CA-UC-016-09 | `MID$("AB",5,1)` → chaîne vide | ⏳ | | |
| CA-UC-016-10 | `VAL("HELLO")` → `0` | ⏳ | | |
| CA-UC-016-11 | `VAL("3ABC")` → `3` | ⏳ | | |
| CA-UC-017-01 | `DEF FN DOUBLE(X)=X*2 : PRINT FN DOUBLE(5)` → `10` | ⏳ | | |
| CA-UC-017-02 | DEF FN avec variable globale → correctement évaluée | ⏳ | | |
| CA-UC-004-01 | SAVE → fichier créé au format texte | ⏳ | | |
| CA-UC-005-01 | LOAD → programme chargé, variables effacées | ⏳ | | |
| CA-UC-005-02 | LOAD → ancien programme intégralement remplacé | ⏳ | | |

## Prochaines actions

A implémenter via /sdd-dev-workflow lot-04-fonctions-affichage-persistance
