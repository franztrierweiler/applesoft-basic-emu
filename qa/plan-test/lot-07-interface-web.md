# Plan de test — lot-07-interface-web

**Date :** 2026-04-10
**UC couverts :** UC-025, UC-026, UC-027, UC-028
**Nombre de scénarios :** 40

## Scénarios

### UC-025 — REPL navigateur

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T07-01 | Page chargée + Brython init → prompt `]` | Nominal | CA-UC-025-01 | 🔴 Bloquant | test_t07_01_prompt_after_init |
| T07-02 | PRINT "HELLO" → HELLO dans le DOM via textContent | Nominal | CA-UC-025-02 | 🔴 Bloquant | test_t07_02_print_to_dom |
| T07-03 | Boucle infinie + Ctrl+C → interruption BREAK | Nominal | CA-UC-025-03 | 🔴 Bloquant | test_t07_03_infinite_loop_interrupt |
| T07-04 | Fenêtre < 768px → panneaux empilés verticalement | Nominal | CA-UC-025-04 | 🟠 Majeur | test_t07_04_responsive_layout |
| T07-05 | FOR I=1 TO 100000 → STOP cliquable (UI non bloquée) | Nominal | CA-UC-025-05 | 🔴 Bloquant | test_t07_05_stop_button_during_loop |
| T07-06 | Chargement → spinner visible jusqu'à init | Nominal | CA-UC-025-06 | 🟡 Mineur | test_t07_06_spinner_loading |
| T07-07 | Mode 40 colonnes → 40ch largeur max | Nominal | CA-UC-025-07 | 🟠 Majeur | test_t07_07_mode_40_columns |
| T07-08 | Mode 80 colonnes → 80ch largeur max | Nominal | CA-UC-025-08 | 🟠 Majeur | test_t07_08_mode_80_columns |
| T07-09 | GET A$ → code ASCII correct après appui touche | Nominal | CA-UC-025-09 | 🔴 Bloquant | test_t07_09_get_ascii_value |
| T07-10 | Code cœur (Lexer/Parser/Interpreter) sans import browser | Conformité | CA-UC-025-10 | 🔴 Bloquant | test_t07_10_no_browser_import |
| T07-11 | Navigateur non supporté → message explicite | Erreur | UC-025 exc. 1b | 🟠 Majeur | test_t07_11_unsupported_browser_msg |
| T07-12 | Console sans focus → indicateur visuel | Erreur | UC-025 exc. 2a | 🟡 Mineur | test_t07_12_focus_indicator |
| T07-13 | Clic RUN pendant exécution → interruption + relance | Erreur | UC-025 exc. 2b | 🟠 Majeur | test_t07_13_run_during_execution |
| T07-14 | Clic STOP sans programme → aucun effet | Erreur | UC-025 exc. 2b | 🟡 Mineur | test_t07_14_stop_no_program |

### UC-026 — Éditeur web

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T07-15 | Mots-clés colorés dans l'éditeur | Nominal | CA-UC-026-01 | 🟠 Majeur | test_t07_15_syntax_highlighting |
| T07-16 | RUN depuis l'éditeur → exécution + sortie console | Nominal | CA-UC-026-02 | 🔴 Bloquant | test_t07_16_run_from_editor |
| T07-17 | Ctrl+Z → annulation (textarea natif) | Nominal | CA-UC-026-03 | 🟡 Mineur | test_t07_17_ctrl_z_undo |
| T07-18 | Saisie console → visible dans l'éditeur | Nominal | CA-UC-026-04 | 🟠 Majeur | test_t07_18_console_to_editor_sync |
| T07-19 | Coloration n'utilise pas innerHTML (SEC-DEV-03) | Sécurité | SEC-BP-24 | 🔴 Bloquant | test_t07_19_highlight_no_innerhtml |
| T07-20 | Conflit éditeur/REPL → dernière action prévaut | Erreur | UC-026 exc. 2b | 🟡 Mineur | test_t07_20_conflict_last_wins |

### UC-027 — Graphiques canvas

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T07-21 | GR COLOR=9 HLIN → ligne orange sur canvas | Nominal | CA-UC-027-01 | 🔴 Bloquant | test_t07_21_lores_hlin_orange |
| T07-22 | 16 couleurs LoRes visibles (palette) | Nominal | CA-UC-027-02 | 🔴 Bloquant | test_t07_22_lores_16_colors |
| T07-23 | HGR HCOLOR=3 HPLOT → diagonale blanche | Nominal | CA-UC-027-03 | 🔴 Bloquant | test_t07_23_hires_diagonal |
| T07-24 | SCRN() cohérent avec buffer interne | Nominal | CA-UC-027-04 | 🔴 Bloquant | test_t07_24_scrn_buffer_coherent |
| T07-25 | Canvas hidden par défaut, visible à GR/HGR | Erreur | UC-027 exc. 1b | 🟠 Majeur | test_t07_25_canvas_show_hide |
| T07-26 | TEXT après HGR → canvas masqué | Erreur | UC-027 exc. 1b | 🟠 Majeur | test_t07_26_text_hides_canvas |
| T07-27 | Canvas rendu pixelated (pas d'anti-aliasing) | Performance | ENF-003 | 🟡 Mineur | test_t07_27_pixelated_rendering |

### UC-028 — Persistance web

| # | Scénario | Type | Source | Sévérité | Test auto |
|---|----------|------|--------|----------|-----------|
| T07-28 | SAVE "DEMO" → stocké dans localStorage | Nominal | CA-UC-028-01 | 🔴 Bloquant | test_t07_28_save_localstorage |
| T07-29 | LOAD "DEMO" → chargé + visible éditeur | Nominal | CA-UC-028-02 | 🔴 Bloquant | test_t07_29_load_localstorage |
| T07-30 | Panneau liste des programmes sauvegardés | Nominal | CA-UC-028-03 | 🟠 Majeur | test_t07_30_list_saved_programs |
| T07-31 | Import fichier .bas via bouton LOAD | Nominal | CA-UC-028-04 | 🔴 Bloquant | test_t07_31_import_file |
| T07-32 | Export fichier .bas via bouton SAVE | Nominal | CA-UC-028-05 | 🔴 Bloquant | test_t07_32_export_file |
| T07-33 | Drag & drop .bas sur l'éditeur | Nominal | CA-UC-028-06 | 🟠 Majeur | test_t07_33_drag_drop |
| T07-34 | localStorage plein → OUT OF MEMORY ERROR | Erreur | UC-028 exc. 1b | 🟠 Majeur | test_t07_34_storage_full_error |
| T07-35 | localStorage désactivé → message explicite | Erreur | UC-028 exc. 1b | 🟠 Majeur | test_t07_35_storage_disabled_msg |
| T07-36 | Fichier importé > 1 Mo → rejet (SEC-BP-41) | Sécurité | SEC-BP-41 | 🔴 Bloquant | test_t07_36_file_size_limit |
| T07-37 | Fichier importé non .bas/.txt → rejet (SEC-BP-40) | Sécurité | SEC-BP-40 | 🔴 Bloquant | test_t07_37_file_extension_check |
| T07-38 | Chaîne malicieuse PRINT "<script>" → pas de XSS | Sécurité | SEC-BP-24 | 🔴 Bloquant | test_t07_38_xss_prevention |
| T07-39 | Brython embarqué en local (pas de CDN) | Sécurité | SEC-SDLC-03 | 🔴 Bloquant | test_t07_39_brython_local_no_cdn |
| T07-40 | Time-slicing : yield/resume cycles fonctionnels | Performance | RG-0015 | 🔴 Bloquant | test_t07_40_timeslicing_cycles |

## Tests manuels

| # | Scénario | Procédure | Critère de réussite |
|---|----------|-----------|-------------------|
| TM-01 | Rendu visuel Apple II | Ouvrir index.html dans un navigateur | Fond noir, texte vert, police monospace |
| TM-02 | Coloration syntaxique visible | Saisir `10 PRINT "HELLO"` dans l'éditeur | PRINT coloré différemment de "HELLO" |
| TM-03 | Boutons toolbar cliquables | Cliquer sur chaque bouton | Pas de gel, actions cohérentes |
