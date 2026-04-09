# Plan de test — lot-06-graphisme

**Date :** 2026-04-09
**UC couverts :** UC-018, UC-019, UC-020, UC-021
**ENF couverts :** ENF-001 (portabilité), ENF-005 (testabilité)
**SEC couverts :** SEC-DEV-01, SEC-DEV-02, SEC-DEV-05
**Nombre de scénarios :** 44

## Scénarios

### UC-018 — Dessiner en basse résolution

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T01-01 | GR active le mode LoRes (40x48), écran effacé en noir, couleur initiale 0 | Nominal | CA-UC-018-01 | 🔴 Bloquant | test_t01_01_gr_active_lores |
| T01-02 | `GR : COLOR=1 : PLOT 5,5` place un bloc magenta en (5,5) | Nominal | CA-UC-018-02 | 🔴 Bloquant | test_t01_02_plot_magenta |
| T01-03 | `GR : COLOR=4 : HLIN 0,39 AT 20` trace une ligne horizontale verte complète | Nominal | CA-UC-018-03 | 🔴 Bloquant | test_t01_03_hlin_green |
| T01-04 | `HLIN 30,10 AT 5` inverse les bornes et trace la ligne de x=10 à x=30 | Nominal | CA-UC-018-04 | 🔴 Bloquant | test_t01_04_hlin_inverted |
| T01-05 | `COLOR=9 : PLOT 5,5 : PRINT SCRN(5,5)` affiche `9` | Nominal | CA-UC-018-05 | 🔴 Bloquant | test_t01_05_scrn_reads_color |
| T01-06 | `GR : PLOT 5,5 : TEXT : PRINT "BACK"` restaure le mode texte | Nominal | CA-UC-018-06 | 🔴 Bloquant | test_t01_06_text_restores |
| T01-07 | `VLIN 30,10 AT 5` inverse les bornes et trace la ligne de y=10 à y=30 | Nominal | UC-018 étape 3b | 🟠 Majeur | test_t01_07_vlin_inverted |
| T01-08 | `COLOR= -1` déclenche `?ILLEGAL QUANTITY ERROR` | Erreur | UC-018 exception 2b | 🔴 Bloquant | test_t01_08_color_negative |
| T01-09 | `COLOR= 16` déclenche `?ILLEGAL QUANTITY ERROR` | Erreur | UC-018 exception 2b | 🔴 Bloquant | test_t01_09_color_overflow |
| T01-10 | `COLOR= 5.9` est tronqué à 5 (pas d'erreur) | Limite | UC-018 exception 2b | 🟠 Majeur | test_t01_10_color_float_truncated |
| T01-11 | `PLOT 40,0` (x hors limites) déclenche `?ILLEGAL QUANTITY ERROR` | Erreur | UC-018 exception 3b | 🔴 Bloquant | test_t01_11_plot_x_oob |
| T01-12 | `PLOT 0,48` (y hors limites) déclenche `?ILLEGAL QUANTITY ERROR` | Erreur | UC-018 exception 3b | 🔴 Bloquant | test_t01_12_plot_y_oob |
| T01-13 | `HLIN 0,39 AT 48` (y hors limites) déclenche `?ILLEGAL QUANTITY ERROR` | Erreur | UC-018 exception 3b | 🔴 Bloquant | test_t01_13_hlin_y_oob |
| T01-14 | `VLIN 0,47 AT 40` (x hors limites) déclenche `?ILLEGAL QUANTITY ERROR` | Erreur | UC-018 exception 3b | 🔴 Bloquant | test_t01_14_vlin_x_oob |
| T01-15 | `SCRN(40,0)` (x hors limites) déclenche `?ILLEGAL QUANTITY ERROR` | Erreur | UC-018 exception 4b | 🔴 Bloquant | test_t01_15_scrn_x_oob |
| T01-16 | `SCRN(0,48)` (y hors limites) déclenche `?ILLEGAL QUANTITY ERROR` | Erreur | UC-018 exception 4b | 🔴 Bloquant | test_t01_16_scrn_y_oob |

### UC-019 — Dessiner en haute résolution

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T02-01 | `HGR` active la page 1, mode mixte (280x160 + 4 lignes texte), écran noir | Nominal | CA-UC-019-01 | 🔴 Bloquant | test_t02_01_hgr_page1 |
| T02-02 | `HGR2` active la page 2, plein écran (280x192), écran noir | Nominal | CA-UC-019-02 | 🔴 Bloquant | test_t02_02_hgr2_page2 |
| T02-03 | `HCOLOR=1 : HPLOT 0,0 TO 279,191` trace une diagonale verte complète | Nominal | CA-UC-019-03 | 🔴 Bloquant | test_t02_03_hplot_diagonal |
| T02-04 | `HPLOT 0,0 TO 100,0 TO 100,100 TO 0,100 TO 0,0` trace un carré (segments enchaînés) | Nominal | CA-UC-019-04 | 🔴 Bloquant | test_t02_04_hplot_chained_square |
| T02-05 | `HPLOT 50,50 : HPLOT TO 100,100` dessine un point puis une ligne depuis la dernière position | Nominal | CA-UC-019-05 | 🔴 Bloquant | test_t02_05_hplot_to_from_last |
| T02-06 | `HCOLOR= -1` déclenche `?ILLEGAL QUANTITY ERROR` | Erreur | UC-019 exception 2b | 🔴 Bloquant | test_t02_06_hcolor_negative |
| T02-07 | `HCOLOR= 8` déclenche `?ILLEGAL QUANTITY ERROR` | Erreur | UC-019 exception 2b | 🔴 Bloquant | test_t02_07_hcolor_overflow |
| T02-08 | `HPLOT 280,0` (x hors limites) déclenche `?ILLEGAL QUANTITY ERROR` | Erreur | UC-019 exception 3b | 🔴 Bloquant | test_t02_08_hplot_x_oob |
| T02-09 | `HPLOT 0,192` (y hors limites) déclenche `?ILLEGAL QUANTITY ERROR` | Erreur | UC-019 exception 3b | 🔴 Bloquant | test_t02_09_hplot_y_oob |
| T02-10 | `HPLOT TO 50,50` sans HPLOT préalable trace depuis (0,0) par défaut | Limite | UC-019 exception 3b | 🟠 Majeur | test_t02_10_hplot_to_default_origin |

### UC-020 — Utiliser les shape tables

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T03-01 | Shape table chargée + `DRAW 1 AT 140,80` dessine la forme au centre | Nominal | CA-UC-020-01 | 🔴 Bloquant | test_t03_01_draw_shape |
| T03-02 | `DRAW 1 AT 140,80` puis `XDRAW 1 AT 140,80` efface la forme (XOR) | Nominal | CA-UC-020-02 | 🔴 Bloquant | test_t03_02_xdraw_erases |
| T03-03 | `ROT=16 : SCALE=2 : DRAW 1 AT 140,80` applique rotation 90 deg et échelle 2 | Nominal | CA-UC-020-03 | 🟠 Majeur | test_t03_03_rot_and_scale |
| T03-04 | `DRAW 1 AT 140,80` sans shape table chargée déclenche `?ILLEGAL QUANTITY ERROR` | Erreur | UC-020 exception 1b | 🔴 Bloquant | test_t03_04_draw_no_table |
| T03-05 | `DRAW 0 AT 140,80` (forme 0 invalide) déclenche `?ILLEGAL QUANTITY ERROR` | Erreur | UC-020 exception 1b | 🔴 Bloquant | test_t03_05_draw_zero |
| T03-06 | `ROT= -1` déclenche `?ILLEGAL QUANTITY ERROR` | Erreur | UC-020 exception 1b | 🔴 Bloquant | test_t03_06_rot_negative |
| T03-07 | `ROT= 256` déclenche `?ILLEGAL QUANTITY ERROR` | Erreur | UC-020 exception 1b | 🔴 Bloquant | test_t03_07_rot_overflow |
| T03-08 | `SCALE= 0` rend la forme invisible (aucun pixel tracé, pas d'erreur) | Limite | UC-020 exception 1b | 🟠 Majeur | test_t03_08_scale_zero_invisible |
| T03-09 | `SCALE= 256` déclenche `?ILLEGAL QUANTITY ERROR` | Erreur | UC-020 exception 1b | 🔴 Bloquant | test_t03_09_scale_overflow |

### UC-021 — Rendre les graphiques en terminal

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T04-01 | Programme LoRes avec rectangle coloré produit un rendu ANSI contenant des codes couleur et des blocs Unicode | Nominal | CA-UC-021-01 | 🟠 Majeur | test_t04_01_lores_render_ansi |
| T04-02 | Programme HiRes avec lignes produit un rendu ANSI contenant des codes couleur et des blocs Unicode | Nominal | CA-UC-021-02 | 🟠 Majeur | test_t04_02_hires_render_ansi |
| T04-03 | Rendu LoRes d'un écran vierge (noir) ne contient que des blocs noirs | Limite | UC-021 étape 1b | 🟡 Mineur | test_t04_03_lores_render_blank |
| T04-04 | Rendu HiRes d'un écran vierge (noir) ne contient que des blocs noirs | Limite | UC-021 étape 1b | 🟡 Mineur | test_t04_04_hires_render_blank |

### Exigences non fonctionnelles et sécurité

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T05-01 | `graphics.py` n'importe aucun module interdit (ctypes, numpy, threading, multiprocessing, os.path, subprocess) | Conformité | ENF-001 / CA-ENF-001-01 | 🔴 Bloquant | test_t05_01_no_forbidden_imports |
| T05-02 | GraphicsEngine est instanciable et testable de manière isolée (sans IOBridge, sans terminal) | Conformité | ENF-005 / CA-ENF-005-01 | 🟠 Majeur | test_t05_02_graphics_engine_isolated |
| T05-03 | `graphics.py` ne contient aucun appel a `eval()`, `exec()`, `pickle`, `compile()` | Sécurité | SEC-DEV-01 | 🔴 Bloquant | test_t05_03_no_eval_exec |
| T05-04 | Toute erreur de bornes dans GraphicsEngine lève une ValueError convertie en BasicError(53) par l'Interpreter (fail securely) | Sécurité | SEC-DEV-02 | 🔴 Bloquant | test_t05_04_fail_securely |
| T05-05 | Les buffers LoRes (40x48) et HiRes (280x192) sont de taille fixe, non extensibles | Sécurité | SEC-DEV-05 | 🟠 Majeur | test_t05_05_buffers_bounded |

## Synthèse par sévérité

| Sévérité | Nombre |
|----------|--------|
| 🔴 Bloquant | 29 |
| 🟠 Majeur | 9 |
| 🟡 Mineur | 2 |
| **Total** | **44** |

## Règles de verdict

- **Verdict ❌ (échec)** si au moins 1 scénario 🔴 Bloquant est en échec
- **Verdict ❌ (échec)** si plus de 2 scénarios 🟠 Majeur sont en échec
- **Verdict ⚠️ (conditionnel)** si 1-2 scénarios 🟠 Majeur en échec, avec plan de correction
- Les scénarios 🟡 Mineur ne bloquent pas le verdict

## Tests manuels

Aucun test manuel requis. Tous les scénarios sont automatisables via les API de GraphicsEngine et de l'Interpreter.

## Correspondance tests unitaires existants / scénarios QA

Les tests unitaires dans `tests/unit/test_graphics.py` (35 tests) couvrent déjà les scénarios T01-01 a T01-16, T02-01 a T02-10, T03-01 a T03-09, T04-01, T04-02. Les scénarios T04-03, T04-04 et T05-01 a T05-05 sont de nouveaux tests QA a créer dans `tests/qa/test_lot06_qa.py`.

## Traçabilité

| Source SPEC | Scénarios couverts |
|-------------|-------------------|
| CA-UC-018-01 | T01-01 |
| CA-UC-018-02 | T01-02 |
| CA-UC-018-03 | T01-03 |
| CA-UC-018-04 | T01-04 |
| CA-UC-018-05 | T01-05 |
| CA-UC-018-06 | T01-06 |
| UC-018 exception 2b (COLOR= hors limites) | T01-08, T01-09 |
| UC-018 exception 2b (COLOR= flottant) | T01-10 |
| UC-018 exception 3b (PLOT/HLIN/VLIN hors limites) | T01-11, T01-12, T01-13, T01-14 |
| UC-018 exception 4b (SCRN hors limites) | T01-15, T01-16 |
| UC-018 étape 3b (VLIN inversion bornes) | T01-07 |
| CA-UC-019-01 | T02-01 |
| CA-UC-019-02 | T02-02 |
| CA-UC-019-03 | T02-03 |
| CA-UC-019-04 | T02-04 |
| CA-UC-019-05 | T02-05 |
| UC-019 exception 2b (HCOLOR= hors limites) | T02-06, T02-07 |
| UC-019 exception 3b (HPLOT hors limites) | T02-08, T02-09 |
| UC-019 exception 3b (HPLOT TO sans préalable) | T02-10 |
| CA-UC-020-01 | T03-01 |
| CA-UC-020-02 | T03-02 |
| CA-UC-020-03 | T03-03 |
| UC-020 exception 1b (DRAW sans table) | T03-04 |
| UC-020 exception 1b (DRAW 0) | T03-05 |
| UC-020 exception 1b (ROT= hors limites) | T03-06, T03-07 |
| UC-020 exception 1b (SCALE= 0 invisible) | T03-08 |
| UC-020 exception 1b (SCALE= 256) | T03-09 |
| CA-UC-021-01 | T04-01 |
| CA-UC-021-02 | T04-02 |
| UC-021 étape 1b (rendu écran vierge) | T04-03, T04-04 |
| ENF-001 / CA-ENF-001-01 | T05-01 |
| ENF-005 / CA-ENF-005-01 | T05-02 |
| SEC-DEV-01 | T05-03 |
| SEC-DEV-02 | T05-04 |
| SEC-DEV-05 | T05-05 |
