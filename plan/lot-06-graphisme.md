# Lot 6 — Graphisme

## Objectif

Implémenter le moteur graphique complet : basse résolution (40x48, 16 couleurs), haute résolution (280x192, 8 couleurs), shape tables (DRAW/XDRAW avec ROT= et SCALE=), et le rendu CLI (caractères Unicode + couleurs ANSI en temps réel, export PNG via Pillow). Après ce lot, la Phase 1 est complète.

## UC couverts

| UC | Intitulé | Priorité |
|---|---|---|
| UC-018 | Dessiner en basse résolution | Critique |
| UC-019 | Dessiner en haute résolution | Critique |
| UC-020 | Utiliser les shape tables | Souhaité |
| UC-021 | Rendre les graphiques en terminal | Important |

## Composants impactés

| Composant | Rôle dans ce lot |
|---|---|
| GraphicsEngine (`graphics.py`) | Création : buffers LoRes (40x48) et HiRes (280x192 x 2 pages), état graphique (mode, couleur, position, ROT, SCALE), logique de dessin (PLOT, HPLOT, HLIN, VLIN, DRAW/XDRAW, SCRN), palettes Apple II, algorithme de tracé de ligne (Bresenham), décodage shape tables |
| Interpreter (`interpreter.py`) | Extension : GR, HGR, HGR2, COLOR=, HCOLOR=, PLOT, HPLOT, HLIN, VLIN, DRAW, XDRAW, ROT=, SCALE=, SCRN(), TEXT |
| IOBridgeCLI (`io_cli.py`) | Extension : rendu graphique temps réel en terminal (ANSI + Unicode blocs ▀▄█), throttle 30 FPS (ADR-004), export PNG via Pillow (import conditionnel — SEC-TECH-20), restriction chemin export (SEC-TECH-21) |
| MemoryMap (`memory.py`) | Utilisé pour le stockage des shape tables (chargées via POKE — ADR-005) |

## Dépendances

- Lot 5 (MemoryMap pour les shape tables)

## Fonctionnalités

### F1 — Basse résolution (UC-018)

- GR : active le mode LoRes (40x48, mode mixte 40x40 + 4 lignes texte), écran effacé en noir
- COLOR= n (0-15) : définit la couleur de dessin, palette Apple II 16 couleurs
- PLOT x,y : dessine un bloc
- HLIN x1,x2 AT y : ligne horizontale (inversion des bornes si x1>x2)
- VLIN y1,y2 AT x : ligne verticale (inversion des bornes si y1>y2)
- SCRN(x,y) : retourne le code couleur (0-15) du bloc
- TEXT : retour au mode texte plein écran
- Validation des bornes : x 0-39, y 0-47, `?ILLEGAL QUANTITY ERROR`
- COLOR= avec flottant → tronqué

### F2 — Haute résolution (UC-019)

- HGR : page 1, mode mixte (280x160 + 4 lignes texte), écran noir
- HGR2 : page 2, plein écran (280x192), écran noir
- HCOLOR= n (0-7) : palette 8 couleurs Apple II
- HPLOT x,y : point
- HPLOT x1,y1 TO x2,y2 : ligne (algorithme de Bresenham)
- HPLOT TO x,y : depuis la dernière position
- Segments enchaînables : HPLOT x1,y1 TO x2,y2 TO x3,y3
- Dernière position par défaut (0,0)
- Validation : x 0-279, y 0-191

### F3 — Shape tables (UC-020)

- ROT= n (0-255) : rotation (0=0°, 16=90°, 32=180°, 48=270°)
- SCALE= n (0-255) : échelle (0=invisible, 1=originale)
- DRAW n AT x,y : dessine la forme n depuis la shape table
- XDRAW n AT x,y : dessine en XOR (effacement par re-dessin)
- Shape tables chargées via POKE dans la MemoryMap (ADR-005)
- Décodage du format binaire Apple II shape table
- Sans shape table chargée : `?ILLEGAL QUANTITY ERROR`

### F4 — Rendu CLI (UC-021)

- Basse résolution : caractères blocs Unicode (▀▄█) + codes ANSI 256 couleurs
- Haute résolution : demi-blocs Unicode pour approximer 280x192
- Rendu temps réel : chaque opération graphique déclenche un rafraîchissement (throttle 30 FPS — ADR-004)
- Export PNG via Pillow : rendu pixel-perfect des buffers graphiques
- Pillow optionnel (import conditionnel, SEC-TECH-20)
- Terminal ne supportant pas ANSI : rendu dégradé ou export image comme alternative

## Critères d'acceptation

| AC | Description | Statut | Justification | Date |
|---|---|---|---|---|
| CA-UC-018-01 | GR → mode LoRes activé, écran noir | ⏳ | | |
| CA-UC-018-02 | `GR : COLOR=1 : PLOT 5,5` → bloc magenta en (5,5) | ⏳ | | |
| CA-UC-018-03 | `GR : COLOR=4 : HLIN 0,39 AT 20` → ligne horizontale verte | ⏳ | | |
| CA-UC-018-04 | `HLIN 30,10 AT 5` → inversion des bornes, ligne tracée | ⏳ | | |
| CA-UC-018-05 | `COLOR=9 : PLOT 5,5 : PRINT SCRN(5,5)` → `9` | ⏳ | | |
| CA-UC-018-06 | `GR : PLOT 5,5 : TEXT : PRINT "BACK"` → mode texte restauré | ⏳ | | |
| CA-UC-019-01 | HGR → mode HiRes page 1, 4 lignes texte en bas | ⏳ | | |
| CA-UC-019-02 | HGR2 → mode HiRes page 2, plein écran | ⏳ | | |
| CA-UC-019-03 | `HCOLOR=1 : HPLOT 0,0 TO 279,191` → diagonale verte | ⏳ | | |
| CA-UC-019-04 | HPLOT enchaîné TO TO TO → carré tracé | ⏳ | | |
| CA-UC-019-05 | `HPLOT 50,50 : HPLOT TO 100,100` → point + ligne | ⏳ | | |
| CA-UC-020-01 | Shape table chargée + DRAW → forme dessinée | ⏳ | | |
| CA-UC-020-02 | DRAW puis XDRAW même position → forme effacée | ⏳ | | |
| CA-UC-020-03 | ROT=16, SCALE=2, DRAW → rotation 90° et échelle 2 | ⏳ | | |
| CA-UC-021-01 | Programme LoRes en CLI → rendu visible en terminal ou export image | ⏳ | | |
| CA-UC-021-02 | Programme HiRes en CLI → rendu visible en terminal ou export image | ⏳ | | |

## Prochaines actions

A implémenter via /sdd-dev-workflow lot-06-graphisme
