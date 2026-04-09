# Lot 7 — Interface web (Phase 2)

## Objectif

Porter l'émulateur dans le navigateur via Brython. Créer une interface web comprenant une console REPL, un éditeur de code avec coloration syntaxique, un canvas pour le rendu graphique, et une barre d'outils. Implémenter le time-slicing pour maintenir la réactivité de l'UI, la persistance via localStorage, et l'import/export de fichiers .bas. Après ce lot, le projet est complet.

## UC couverts

| UC | Intitulé | Priorité |
|---|---|---|
| UC-025 | Utiliser le REPL dans le navigateur | Critique |
| UC-026 | Éditer un programme dans l'éditeur web | Critique |
| UC-027 | Afficher les graphiques sur canvas | Critique |
| UC-028 | Sauvegarder/charger via le navigateur | Important |

## Composants impactés

| Composant | Rôle dans ce lot |
|---|---|
| IOBridgeWeb (`web/io_web.py`) | Création : implémentation de l'IOBridge pour Brython. Console DOM (PRINT → textContent, INPUT → champ de saisie, GET → événement clavier). Canvas HTML5 (LoRes + HiRes). localStorage (SAVE/LOAD). Time-slicing (yield au navigateur). |
| `web/index.html` | Création : page principale avec layout (éditeur, console, canvas, barre d'outils). Chargement Brython embarqué. |
| `web/style.css` | Création : esthétique Apple II (fond noir, police Apple II, modes 40/80 colonnes). Layout responsive. |
| `web/fonts/` | Inclusion d'une police Apple II (RG-0012) |
| Interpreter (`interpreter.py`) | Modification mineure : activation du yield effectif (compteur d'instructions → seuil ~50ms au lieu de infini) |

## Dépendances

- Lot 6 (Phase 1 complète — tous les composants du cœur sont implémentés et testés)

## Fonctionnalités

### F1 — Interface web et layout (UC-025)

- Page HTML avec 4 zones : éditeur de code, console de sortie, canvas graphique (masqué par défaut), barre d'outils (RUN, STOP, RESET, LIST, SAVE, LOAD)
- Layout responsive : empilé en vertical sur tablette (< 768px)
- Esthétique Apple II : fond noir, police Apple II (RG-0012), modes 40 et 80 colonnes
- Brython embarqué en local (SEC-SDLC-03, SEC-TECH-10), hash SHA-256 documenté
- Spinner de chargement jusqu'à initialisation complète
- Indicateur de focus console
- Gestion navigateurs non supportés

### F2 — Console REPL web (UC-025)

- Prompt `]` dans la console DOM
- PRINT → `element.textContent` (pas innerHTML — SEC-BP-24, SEC-TECH-12)
- INPUT → champ de saisie inline
- GET → capture événement clavier (codes ASCII Apple II)
- Ctrl+C → interruption (bouton STOP + raccourci clavier)
- Bouton RUN → interrompt programme en cours si actif, puis relance
- Bouton STOP → sans effet si pas de programme en cours

### F3 — Time-slicing (RG-0015)

- L'Interpreter exécute N instructions par tranche (~50ms)
- Yield au navigateur entre les tranches (requestAnimationFrame ou setTimeout)
- INPUT/GET → état « attente I/O » + yield
- Le bouton STOP et Ctrl+C restent fonctionnels pendant l'exécution
- Pas de blocage du thread principal

### F4 — Éditeur de code (UC-026)

- `<textarea>` avec numérotation des lignes en marge
- Coloration syntaxique basique des mots-clés Applesoft
- Couper/copier/coller, Ctrl+Z (annuler)
- Synchronisation éditeur ↔ REPL :
  - RUN depuis l'éditeur → code remplace le programme en mémoire
  - Saisie dans la console → visible dans l'éditeur
  - Conflit : dernière action prévaut, avertissement visuel

### F5 — Rendu graphique canvas (UC-027)

- Basse résolution : canvas rendant la grille 40x48, palette Apple II 16 couleurs
- Haute résolution : canvas 280x192 pixels logiques, palette 8 couleurs, upscale entier sans anti-aliasing
- Canvas apparaît automatiquement à GR/HGR/HGR2, masqué à TEXT
- Mode mixte : 4 lignes de texte en bas
- Mises à jour bufferisées, rafraîchies par requestAnimationFrame (cible 60 FPS)
- Redimensionnement fenêtre → canvas mis à l'échelle

### F6 — Persistance web (UC-028)

- SAVE "name" → localStorage
- LOAD "name" → depuis localStorage
- Liste des programmes sauvegardés (panneau de gestion avec nom et date)
- Export fichier : bouton SAVE → téléchargement .bas
- Import fichier : bouton LOAD → sélection fichier, ou drag & drop sur l'éditeur
- localStorage plein : `?OUT OF MEMORY ERROR`
- localStorage désactivé : message explicite
- Validation des fichiers importés (SEC-BP-40, SEC-BP-41)

## Critères d'acceptation

| AC | Description | Statut | Justification | Date |
|---|---|---|---|---|
| CA-UC-025-01 | Page chargée + Brython init → prompt `]` | ✅ | test_io_web_py_shows_prompt, test_io_web_py_init_function | 2026-04-09 |
| CA-UC-025-02 | `PRINT "HELLO"` dans la console → `HELLO` dans le DOM | ✅ | test_io_web_py_has_print_str, test_io_web_py_uses_textcontent, test_io_web_py_no_innerhtml | 2026-04-09 |
| CA-UC-025-03 | Boucle infinie + Ctrl+C → interruption, `BREAK` | ✅ | YieldSignal + check_interrupt entre tranches, test_yield_signal_raised_at_threshold, test_interrupt_between_slices, _on_document_keydown Ctrl+C | 2026-04-09 |
| CA-UC-025-04 | Fenêtre 768px → panneaux empilés verticalement | ⏳ | | |
| CA-UC-025-05 | `FOR I=1 TO 100000 : NEXT` → bouton STOP cliquable | ✅ | Time-slicing via YieldSignal + setTimeout, _on_stop_click → set_interrupted, test_io_web_py_stop_button_interrupt, test_interrupt_between_slices | 2026-04-09 |
| CA-UC-025-06 | Chargement → spinner visible | ✅ | test_index_html_spinner_element, test_style_css_spinner_animation, test_io_web_py_hides_spinner | 2026-04-09 |
| CA-UC-025-07 | Mode 40 colonnes → 40 caractères par ligne | ⏳ | | |
| CA-UC-025-08 | Mode 80 colonnes → 80 caractères par ligne | ⏳ | | |
| CA-UC-025-09 | `GET A$ : PRINT ASC(A$)` → code ASCII correct | ✅ | InputRequestSignal pour GET async, _on_keydown capture touche et appelle _receive_input_value, test_input_request_signal_for_get, test_resume_after_get_assigns_value | 2026-04-09 |
| CA-UC-025-10 | Code Lexer/Parser/Interpreter → pas de `import browser` | ✅ | test_ca_uc_025_10_no_browser_import | 2026-04-09 |
| CA-UC-026-01 | Mots-clés colorés dans l'éditeur | ⏳ | | |
| CA-UC-026-02 | RUN depuis l'éditeur → exécution + sortie console | ⏳ | | |
| CA-UC-026-03 | Ctrl+Z → annulation | ⏳ | | |
| CA-UC-026-04 | Saisie console → visible dans l'éditeur | ⏳ | | |
| CA-UC-027-01 | `GR : COLOR=9 : HLIN 0,39 AT 20` → ligne orange sur canvas | ⏳ | | |
| CA-UC-027-02 | 16 couleurs LoRes visibles | ⏳ | | |
| CA-UC-027-03 | `HGR : HCOLOR=3 : HPLOT 0,0 TO 279,159` → diagonale blanche | ⏳ | | |
| CA-UC-027-04 | Buffer interne cohérent avec SCRN() | ⏳ | | |
| CA-UC-028-01 | SAVE → stocké dans localStorage | ⏳ | | |
| CA-UC-028-02 | LOAD → chargé depuis localStorage + visible éditeur | ⏳ | | |
| CA-UC-028-03 | Panneau liste des programmes sauvegardés | ⏳ | | |
| CA-UC-028-04 | Import fichier via bouton LOAD | ⏳ | | |
| CA-UC-028-05 | Export fichier via bouton SAVE | ⏳ | | |
| CA-UC-028-06 | Drag & drop .bas sur l'éditeur | ⏳ | | |

## Progression

| Itération | Contenu | Statut |
|---|---|---|
| 1 | Fondation : page HTML, CSS Apple II, IOBridgeWeb squelette, console REPL événementielle | ✅ 2026-04-09 |
| 2 | Time-slicing + interruption (Ctrl+C, bouton STOP, GET async) | ✅ 2026-04-09 |
| 3 | Éditeur, coloration, synchronisation éditeur/REPL | ⏳ |
| 4 | Canvas graphique (LoRes + HiRes) | ⏳ |
| 5 | Persistance web (localStorage, import/export .bas) | ⏳ |

## Prochaines actions

Itération 3 : éditeur, coloration syntaxique, synchronisation éditeur/REPL, layout responsive + modes colonnes
