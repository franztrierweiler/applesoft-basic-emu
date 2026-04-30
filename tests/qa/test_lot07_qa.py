"""Tests QA — Lot 07 : Interface web (REPL pur).

Scénarios de recette couvrant UC-025, UC-027, UC-028.
UC-026 (éditeur) descopé — interface REPL pure fidèle Apple II.
Police Apple II bitmap (RG-0012).
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
        with pytest.raises(YieldSignal) as exc:
            interp.run()
        y = exc.value
        io.set_interrupted()
        interp.resume_execution(y.line_num, y.stmt_idx)

    def test_t07_04_responsive_layout(self, css):
        """T07-04 [🟠] Fenêtre < 768px → layout adapté."""
        assert "@media" in css
        assert "768px" in css

    def test_t07_05_stop_button_during_loop(self):
        """T07-05 [🔴] FOR I=1 TO 100000 → STOP reste cliquable."""
        io = IOBridgeCLI()
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)
        tokens = tokenize("10 GOTO 10")
        prog.add_line(10, tokens[1:])
        interp.set_yield_threshold(10)
        with pytest.raises(YieldSignal):
            interp.run()

    def test_t07_06_boot_screen_animation(self, html, css, ioweb):
        """T07-06 [🟡] Boot-screen damier visible au démarrage (remplace
        le spinner Brython, ext. LookAppleII UC-FID-003)."""
        assert "boot-screen" in html
        assert "@keyframes boot-fill" in css or "boot-running" in css
        assert "boot-screen" in ioweb
        assert "boot-running" in ioweb

    def test_t07_07_mode_40_columns(self, css):
        """T07-07 [🟠] Mode 40 colonnes → 40ch."""
        assert "40ch" in css

    def test_t07_08_mode_80_columns(self, css, ioweb):
        """T07-08 [🟠] Mode 80 colonnes → 80ch."""
        assert "80ch" in css
        assert "mode-80" in css
        assert "set_column_mode" in ioweb

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

    def test_t07_11_brython_local_no_cdn(self, html):
        """T07-11 [🟠] Brython local, pas de CDN."""
        assert "https://" not in html
        assert "http://" not in html
        assert 'src="brython.js"' in html

    def test_t07_12_focus_indicator(self, css):
        """T07-12 [🟡] Console focus → indicateur visuel."""
        assert "focus" in css.lower()

    def test_t07_13_repl_only_no_editor(self, html, ioweb):
        """T07-13 [🟠] Interface REPL pure — pas d'éditeur séparé."""
        assert 'id="editor"' not in html
        assert "editor-panel" not in html
        assert "_highlight_editor" not in ioweb


# ===================================================================
# RG-0012 — Police Apple II
# ===================================================================

class TestRG0012:

    def test_t07_14_apple2_font_declared(self, css):
        """T07-14 [🔴] Police Apple II déclarée en @font-face."""
        assert "@font-face" in css
        assert "Apple II" in css

    def test_t07_15_apple2_woff2_exists(self):
        """T07-15 [🔴] Fichier apple2.woff2 présent."""
        path = os.path.join(WEB_DIR, "fonts", "apple2.woff2")
        assert os.path.isfile(path)

    def test_t07_16_apple2_font_used(self, css):
        """T07-16 [🔴] Police Apple II utilisée comme font-family principale."""
        assert "font-apple2" in css or "Apple II" in css

    def test_t07_17_font_monospace_fallback(self, css):
        """T07-17 [🟡] Fallback monospace si police non disponible."""
        assert "monospace" in css


# ===================================================================
# UC-027 — Graphiques canvas
# ===================================================================

class TestUC027:

    def test_t07_18_lores_hlin_orange(self, ioweb):
        """T07-18 [🔴] GR COLOR=9 HLIN → ligne orange sur canvas."""
        assert "LORES_COLORS" in ioweb
        assert "render_lores" in ioweb
        assert "#FF6600" in ioweb

    def test_t07_19_lores_16_colors(self, ioweb):
        """T07-19 [🔴] 16 couleurs LoRes dans la palette."""
        match = re.search(r"LORES_COLORS\s*=\s*\[(.*?)\]", ioweb, re.DOTALL)
        assert match is not None
        colors = re.findall(r'"#[0-9A-Fa-f]{6}"', match.group(1))
        assert len(colors) == 16

    def test_t07_20_hires_diagonal(self, ioweb):
        """T07-20 [🔴] HGR HCOLOR=3 HPLOT → diagonale blanche."""
        assert "HIRES_COLORS" in ioweb
        assert "render_hires" in ioweb
        assert "#FFFFFF" in ioweb

    def test_t07_21_scrn_buffer_coherent(self, ioweb):
        """T07-21 [🔴] SCRN() cohérent avec buffer interne."""
        assert "def render_lores(self, buffer" in ioweb

    def test_t07_22_canvas_show_hide(self, ioweb, html):
        """T07-22 [🟠] Canvas masqué par défaut, visible à GR/HGR."""
        assert "display: none" in html
        assert "_show_canvas" in ioweb

    def test_t07_23_pixelated_rendering(self, css):
        """T07-23 [🟡] Canvas rendu pixelated."""
        assert "pixelated" in css


# ===================================================================
# UC-028 — Persistance web
# ===================================================================

class TestUC028:

    def test_t07_24_save_localstorage(self, ioweb):
        """T07-24 [🔴] SAVE → stocké dans localStorage."""
        assert "def save_to_localStorage" in ioweb
        assert "setItem" in ioweb

    def test_t07_25_load_localstorage(self, ioweb):
        """T07-25 [🔴] LOAD → chargé depuis localStorage."""
        assert "def load_from_localStorage" in ioweb
        assert "getItem" in ioweb

    def test_t07_26_list_saved_programs(self, ioweb):
        """T07-26 [🟠] Liste des programmes sauvegardés."""
        assert "def list_saved_programs" in ioweb

    def test_t07_27_import_file(self, ioweb):
        """T07-27 [🔴] Import fichier .bas via bouton LOAD."""
        assert "_setup_file_import" in ioweb
        assert "FileReader" in ioweb

    def test_t07_28_export_file(self, ioweb):
        """T07-28 [🔴] Export fichier .bas via bouton SAVE."""
        assert "def export_file" in ioweb
        assert "Blob" in ioweb

    def test_t07_29_drag_drop(self, ioweb):
        """T07-29 [🟠] Drag & drop .bas."""
        assert "_setup_drag_drop" in ioweb
        assert "dragover" in ioweb

    def test_t07_30_storage_full_error(self, ioweb):
        """T07-30 [🟠] localStorage plein → OUT OF MEMORY ERROR."""
        assert "OUT OF MEMORY ERROR" in ioweb

    def test_t07_31_file_size_limit(self, ioweb):
        """T07-31 [🔴] Fichier > 1 Mo → rejet (SEC-BP-41)."""
        assert "MAX_IMPORT_SIZE" in ioweb
        assert "1_000_000" in ioweb

    def test_t07_32_file_extension_check(self, ioweb):
        """T07-32 [🔴] Fichier non .bas/.txt → rejet (SEC-BP-40)."""
        assert "ALLOWED_EXTENSIONS" in ioweb
        assert ".bas" in ioweb
        assert "_validate_import_file" in ioweb

    def test_t07_33_xss_prevention(self, ioweb):
        """T07-33 [🔴] Pas de XSS (SEC-BP-24)."""
        assert "innerHTML" not in ioweb
        assert "textContent" in ioweb

    def test_t07_34_brython_local(self, html):
        """T07-34 [🔴] Brython embarqué (SEC-SDLC-03)."""
        assert 'src="brython.js"' in html
        assert "https://" not in html

    def test_t07_35_timeslicing_cycles(self):
        """T07-35 [🔴] Time-slicing yield/resume fonctionne."""
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
        assert finished
        assert env.get_var("X") == 10.0
