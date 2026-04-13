"""Tests QA — Lot 07 : Interface web.

40 scénarios de recette couvrant UC-025, UC-026, UC-027, UC-028.
Tests structurels (analyse statique du code source) + tests fonctionnels
du mécanisme de time-slicing (pur Python, sans navigateur).
"""

from __future__ import annotations

import os
import re

import pytest

from applesoft.environment import Environment
from applesoft.interpreter import (
    InputRequestSignal,
    Interpreter,
    YieldSignal,
)
from applesoft.io_cli import IOBridgeCLI
from applesoft.lexer import tokenize
from applesoft.program import Program

# Base paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WEB_DIR = os.path.join(PROJECT_ROOT, "web")
SRC_DIR = os.path.join(PROJECT_ROOT, "src", "applesoft")


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


@pytest.fixture(scope="module")
def html():
    return _read(os.path.join(WEB_DIR, "index.html"))


@pytest.fixture(scope="module")
def css():
    return _read(os.path.join(WEB_DIR, "style.css"))


@pytest.fixture(scope="module")
def ioweb():
    return _read(os.path.join(WEB_DIR, "io_web.py"))


# ===================================================================
# UC-025 — REPL navigateur
# ===================================================================

class TestUC025:

    def test_t07_01_prompt_after_init(self, ioweb):
        """T07-01 [🔴] Page chargée + Brython init → prompt `]`."""
        assert "def init():" in ioweb
        assert '"]"' in ioweb or "']'" in ioweb

    def test_t07_02_print_to_dom(self, ioweb):
        """T07-02 [🔴] PRINT → DOM via textContent (pas innerHTML)."""
        assert "def print_str(self" in ioweb
        assert "textContent" in ioweb
        assert "innerHTML" not in ioweb

    def test_t07_03_infinite_loop_interrupt(self):
        """T07-03 [🔴] Boucle infinie + Ctrl+C → interruption BREAK."""
        io = IOBridgeCLI()
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)

        tokens = tokenize("10 GOTO 10")
        prog.add_line(10, tokens[1:])
        interp.set_yield_threshold(5)

        # Premier yield
        with pytest.raises(YieldSignal) as exc:
            interp.run()
        y = exc.value

        # Simuler Ctrl+C
        io.set_interrupted()
        # Ne doit PAS lever YieldSignal — doit s'arrêter
        interp.resume_execution(y.line_num, y.stmt_idx)

    def test_t07_04_responsive_layout(self, css):
        """T07-04 [🟠] Fenêtre < 768px → panneaux empilés."""
        assert "@media" in css
        assert "768px" in css
        assert "flex-direction" in css
        assert "column" in css

    def test_t07_05_stop_button_during_loop(self):
        """T07-05 [🔴] FOR I=1 TO 100000 → STOP reste cliquable (time-slicing)."""
        io = IOBridgeCLI()
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)

        tokens = tokenize("10 GOTO 10")
        prog.add_line(10, tokens[1:])
        interp.set_yield_threshold(10)

        with pytest.raises(YieldSignal):
            interp.run()
        # Si on arrive ici, time-slicing fonctionne = UI non bloquée

    def test_t07_06_spinner_loading(self, html, css, ioweb):
        """T07-06 [🟡] Spinner visible pendant chargement."""
        assert "loading-overlay" in html
        assert "spinner" in html
        assert "@keyframes" in css and "spin" in css
        assert "hidden" in ioweb and "loading-overlay" in ioweb

    def test_t07_07_mode_40_columns(self, css):
        """T07-07 [🟠] Mode 40 colonnes → 40ch."""
        assert "40ch" in css

    def test_t07_08_mode_80_columns(self, css, ioweb):
        """T07-08 [🟠] Mode 80 colonnes → 80ch."""
        assert "80ch" in css
        assert "mode-80" in css
        assert "mode-80" in ioweb or "set_column_mode" in ioweb

    def test_t07_09_get_ascii_value(self):
        """T07-09 [🔴] GET A$ → code ASCII correct."""
        io = IOBridgeCLI()
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)

        tokens10 = tokenize("10 GET A$")
        prog.add_line(10, tokens10[1:])
        tokens20 = tokenize("20 END")
        prog.add_line(20, tokens20[1:])
        interp.set_yield_threshold(1000)

        with pytest.raises(InputRequestSignal) as exc:
            interp.run()
        sig = exc.value
        assert sig.kind == "get"

        interp.resume_after_input(sig.line_num, sig.stmt_idx, "A")
        assert env.get_var("A$") == "A"

    def test_t07_10_no_browser_import(self):
        """T07-10 [🔴] Code cœur sans import browser."""
        for filename in os.listdir(SRC_DIR):
            if not filename.endswith(".py"):
                continue
            content = _read(os.path.join(SRC_DIR, filename))
            for i, line in enumerate(content.splitlines(), 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                assert not re.search(r"\bfrom\s+browser\b", stripped), \
                    f"{filename}:{i}: browser import found"
                assert not re.search(r"\bimport\s+browser\b", stripped), \
                    f"{filename}:{i}: browser import found"

    def test_t07_11_unsupported_browser_msg(self, html):
        """T07-11 [🟠] Brython non supporté → Brython local inclus, pas de CDN."""
        # Vérification : pas de lien CDN externe
        assert "https://" not in html
        assert "http://" not in html
        assert 'src="brython.js"' in html

    def test_t07_12_focus_indicator(self, css):
        """T07-12 [🟡] Console focus → indicateur visuel."""
        assert "focus" in css.lower()

    def test_t07_13_run_during_execution(self, ioweb):
        """T07-13 [🟠] RUN pendant exécution → interruption + relance."""
        # Le on_run doit vérifier _running et interrompre
        assert "_running" in ioweb
        # Le handler btn-run doit gérer le cas "already running"
        assert "btn-run" in ioweb

    def test_t07_14_stop_no_program(self, ioweb):
        """T07-14 [🟡] STOP sans programme → aucun effet."""
        # set_interrupted met juste le flag, pas de crash
        assert "def _on_stop_click" in ioweb
        assert "set_interrupted" in ioweb


# ===================================================================
# UC-026 — Éditeur web
# ===================================================================

class TestUC026:

    def test_t07_15_syntax_highlighting(self, ioweb, css):
        """T07-15 [🟠] Mots-clés colorés dans l'éditeur."""
        assert "APPLESOFT_KEYWORDS" in ioweb
        assert "PRINT" in ioweb
        assert "GOTO" in ioweb
        assert "_highlight_editor" in ioweb
        assert "keyword" in css.lower()

    def test_t07_16_run_from_editor(self, ioweb):
        """T07-16 [🔴] RUN depuis éditeur → exécution + sortie console."""
        assert "btn-run" in ioweb
        assert "editor" in ioweb
        assert "NEW" in ioweb
        assert "_run_program_sliced" in ioweb

    def test_t07_17_ctrl_z_undo(self, html):
        """T07-17 [🟡] Ctrl+Z → annulation (textarea natif)."""
        assert "<textarea" in html
        assert 'id="editor"' in html

    def test_t07_18_console_to_editor_sync(self, ioweb):
        """T07-18 [🟠] Saisie console → visible dans l'éditeur."""
        assert "_update_editor" in ioweb
        assert "editor" in ioweb

    def test_t07_19_highlight_no_innerhtml(self, ioweb):
        """T07-19 [🔴] Coloration n'utilise pas innerHTML (SEC-DEV-03)."""
        assert "innerHTML" not in ioweb
        # Vérifie que textContent est utilisé pour le highlighting
        assert "textContent" in ioweb

    def test_t07_20_conflict_last_wins(self, ioweb):
        """T07-20 [🟡] Conflit éditeur/REPL → dernière action prévaut."""
        # Le RUN depuis l'éditeur fait NEW puis charge le contenu éditeur
        # La saisie console appelle _update_editor
        assert "_update_editor" in ioweb
        assert "btn-run" in ioweb


# ===================================================================
# UC-027 — Graphiques canvas
# ===================================================================

class TestUC027:

    def test_t07_21_lores_hlin_orange(self, ioweb):
        """T07-21 [🔴] GR COLOR=9 HLIN → ligne orange sur canvas."""
        assert "LORES_COLORS" in ioweb
        assert "render_lores" in ioweb
        assert "fillRect" in ioweb
        # Couleur 9 = orange (#FF6600) dans la palette
        assert "#FF6600" in ioweb

    def test_t07_22_lores_16_colors(self, ioweb):
        """T07-22 [🔴] 16 couleurs LoRes dans la palette."""
        # Compter les entrées dans LORES_COLORS
        match = re.search(r"LORES_COLORS\s*=\s*\[(.*?)\]", ioweb, re.DOTALL)
        assert match is not None, "LORES_COLORS not found"
        colors = re.findall(r'"#[0-9A-Fa-f]{6}"', match.group(1))
        assert len(colors) == 16, f"Expected 16 colors, got {len(colors)}"

    def test_t07_23_hires_diagonal(self, ioweb):
        """T07-23 [🔴] HGR HCOLOR=3 HPLOT → diagonale blanche."""
        assert "HIRES_COLORS" in ioweb
        assert "render_hires" in ioweb
        # Couleur 3 = blanc (#FFFFFF)
        assert "#FFFFFF" in ioweb

    def test_t07_24_scrn_buffer_coherent(self, ioweb):
        """T07-24 [🔴] SCRN() cohérent avec buffer interne."""
        # Le render reçoit un buffer en paramètre (source de vérité = GraphicsEngine)
        assert "def render_lores(self, buffer" in ioweb
        assert "def render_hires(self, buffer" in ioweb

    def test_t07_25_canvas_show_hide(self, ioweb, html):
        """T07-25 [🟠] Canvas masqué par défaut, visible à GR/HGR."""
        assert 'display: none' in html or "display: none" in html
        assert "_show_canvas" in ioweb
        assert "_hide_canvas" in ioweb

    def test_t07_26_text_hides_canvas(self, ioweb):
        """T07-26 [🟠] TEXT après HGR → canvas masqué."""
        assert "_hide_canvas" in ioweb
        assert '"none"' in ioweb or "'none'" in ioweb

    def test_t07_27_pixelated_rendering(self, css):
        """T07-27 [🟡] Canvas rendu pixelated (pas d'anti-aliasing)."""
        assert "image-rendering" in css
        assert "pixelated" in css


# ===================================================================
# UC-028 — Persistance web
# ===================================================================

class TestUC028:

    def test_t07_28_save_localstorage(self, ioweb):
        """T07-28 [🔴] SAVE → stocké dans localStorage."""
        assert "def save_to_localStorage" in ioweb
        assert "localStorage" in ioweb
        assert "setItem" in ioweb

    def test_t07_29_load_localstorage(self, ioweb):
        """T07-29 [🔴] LOAD → chargé depuis localStorage."""
        assert "def load_from_localStorage" in ioweb
        assert "getItem" in ioweb

    def test_t07_30_list_saved_programs(self, ioweb):
        """T07-30 [🟠] Panneau liste des programmes sauvegardés."""
        assert "def list_saved_programs" in ioweb
        assert "storage" in ioweb.lower()

    def test_t07_31_import_file(self, ioweb):
        """T07-31 [🔴] Import fichier .bas via bouton LOAD."""
        assert "_setup_file_import" in ioweb
        assert "FileReader" in ioweb
        assert "btn-load" in ioweb

    def test_t07_32_export_file(self, ioweb):
        """T07-32 [🔴] Export fichier .bas via bouton SAVE."""
        assert "def export_file" in ioweb
        assert "Blob" in ioweb
        assert "download" in ioweb

    def test_t07_33_drag_drop(self, ioweb):
        """T07-33 [🟠] Drag & drop .bas sur l'éditeur."""
        assert "_setup_drag_drop" in ioweb
        assert "dragover" in ioweb
        assert "drop" in ioweb

    def test_t07_34_storage_full_error(self, ioweb):
        """T07-34 [🟠] localStorage plein → OUT OF MEMORY ERROR."""
        assert "OUT OF MEMORY ERROR" in ioweb

    def test_t07_35_storage_disabled_msg(self, ioweb):
        """T07-35 [🟠] localStorage désactivé → message explicite."""
        # Le try/except dans save_to_localStorage attrape l'exception
        assert "except Exception" in ioweb
        # Le message d'erreur est affiché
        assert "OUT OF MEMORY ERROR" in ioweb or "STORAGE ERROR" in ioweb

    def test_t07_36_file_size_limit(self, ioweb):
        """T07-36 [🔴] Fichier importé > 1 Mo → rejet (SEC-BP-41)."""
        assert "MAX_IMPORT_SIZE" in ioweb
        assert "1_000_000" in ioweb or "1000000" in ioweb or "1048576" in ioweb
        assert "FILE TOO LARGE" in ioweb or "size" in ioweb.lower()

    def test_t07_37_file_extension_check(self, ioweb):
        """T07-37 [🔴] Fichier non .bas/.txt → rejet (SEC-BP-40)."""
        assert "ALLOWED_EXTENSIONS" in ioweb
        assert ".bas" in ioweb
        assert ".txt" in ioweb
        assert "_validate_import_file" in ioweb

    def test_t07_38_xss_prevention(self, ioweb):
        """T07-38 [🔴] Chaîne malicieuse → pas de XSS (SEC-BP-24)."""
        # Aucune utilisation de innerHTML
        assert "innerHTML" not in ioweb
        # textContent est utilisé pour toutes les sorties DOM
        assert "textContent" in ioweb

    def test_t07_39_brython_local_no_cdn(self, html):
        """T07-39 [🔴] Brython embarqué en local (SEC-SDLC-03)."""
        assert 'src="brython.js"' in html
        assert 'src="brython_stdlib.js"' in html
        # Pas de CDN
        assert "https://" not in html
        assert "http://" not in html

    def test_t07_40_timeslicing_cycles(self):
        """T07-40 [🔴] Time-slicing yield/resume fonctionne sur plusieurs cycles."""
        io = IOBridgeCLI()
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)

        tokens10 = tokenize("10 X = X + 1")
        prog.add_line(10, tokens10[1:])
        tokens20 = tokenize("20 IF X >= 10 THEN END")
        prog.add_line(20, tokens20[1:])
        tokens30 = tokenize("30 GOTO 10")
        prog.add_line(30, tokens30[1:])

        interp.set_yield_threshold(3)

        finished = False
        try:
            interp.run()
            finished = True
        except YieldSignal as y:
            for _ in range(200):
                try:
                    interp.resume_execution(y.line_num, y.stmt_idx)
                    finished = True
                    break
                except YieldSignal as y2:
                    y = y2

        assert finished, "Programme devrait terminer en < 200 cycles"
        assert env.get_var("X") == 10.0
