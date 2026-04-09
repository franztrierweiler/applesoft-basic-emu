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
| CA-UC-018-01 | GR → mode LoRes activé, écran noir | ✅ | test_ca_uc_018_01_gr_active_lores | 2026-04-09 |
| CA-UC-018-02 | `GR : COLOR=1 : PLOT 5,5` → bloc magenta en (5,5) | ✅ | test_ca_uc_018_02_plot_magenta | 2026-04-09 |
| CA-UC-018-03 | `GR : COLOR=4 : HLIN 0,39 AT 20` → ligne horizontale verte | ✅ | test_ca_uc_018_03_hlin_green | 2026-04-09 |
| CA-UC-018-04 | `HLIN 30,10 AT 5` → inversion des bornes, ligne tracée | ✅ | test_ca_uc_018_04_hlin_inverted_bounds | 2026-04-09 |
| CA-UC-018-05 | `COLOR=9 : PLOT 5,5 : PRINT SCRN(5,5)` → `9` | ✅ | test_ca_uc_018_05_scrn_reads_color | 2026-04-09 |
| CA-UC-018-06 | `GR : PLOT 5,5 : TEXT : PRINT "BACK"` → mode texte restauré | ✅ | test_ca_uc_018_06_text_restores_text_mode | 2026-04-09 |
| CA-UC-019-01 | HGR → mode HiRes page 1, 4 lignes texte en bas | ✅ | test_ca_uc_019_01_hgr_activates_page1 | 2026-04-09 |
| CA-UC-019-02 | HGR2 → mode HiRes page 2, plein écran | ✅ | test_ca_uc_019_02_hgr2_activates_page2 | 2026-04-09 |
| CA-UC-019-03 | `HCOLOR=1 : HPLOT 0,0 TO 279,191` → diagonale verte | ✅ | test_ca_uc_019_03_hplot_diagonal | 2026-04-09 |
| CA-UC-019-04 | HPLOT enchaîné TO TO TO → carré tracé | ✅ | test_ca_uc_019_04_hplot_chained_square | 2026-04-09 |
| CA-UC-019-05 | `HPLOT 50,50 : HPLOT TO 100,100` → point + ligne | ✅ | test_ca_uc_019_05_hplot_point_and_line_from_last | 2026-04-09 |
| CA-UC-020-01 | Shape table chargée + DRAW → forme dessinée | ✅ | test_ca_uc_020_01_draw_shape | 2026-04-09 |
| CA-UC-020-02 | DRAW puis XDRAW même position → forme effacée | ✅ | test_ca_uc_020_02_xdraw_erases | 2026-04-09 |
| CA-UC-020-03 | ROT=16, SCALE=2, DRAW → rotation 90° et échelle 2 | ✅ | test_ca_uc_020_03_rot_and_scale | 2026-04-09 |
| CA-UC-021-01 | Programme LoRes en CLI → rendu visible en terminal ou export image | ✅ | test_ca_uc_021_01_lores_render | 2026-04-09 |
| CA-UC-021-02 | Programme HiRes en CLI → rendu visible en terminal ou export image | ✅ | test_ca_uc_021_02_hires_render | 2026-04-09 |

## Prochaines actions

Lot terminé — prêt pour QA
