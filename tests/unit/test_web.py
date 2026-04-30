"""Tests for web interface — lot 07.

These tests verify structural requirements that can be checked without a browser,
plus time-slicing mechanics (YieldSignal, resume_execution, InputRequestSignal)
which are pure Python and testable without Brython.

Interface: REPL pur (UC-026 descopé), police Apple II (RG-0012).
"""

from __future__ import annotations

import os
import re

import pytest

# Base paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WEB_DIR = os.path.join(PROJECT_ROOT, "web")
SRC_DIR = os.path.join(PROJECT_ROOT, "src", "applesoft")


# ---------------------------------------------------------------------------
# CA-UC-025-10 — No browser import in core modules
# ---------------------------------------------------------------------------
class TestNoBrowserImport:
    """CA-UC-025-10: Lexer, Parser, Interpreter must not import browser."""

    def test_ca_uc_025_10_no_browser_import(self):
        violations = []
        for filename in os.listdir(SRC_DIR):
            if not filename.endswith(".py"):
                continue
            filepath = os.path.join(SRC_DIR, filename)
            with open(filepath, encoding="utf-8") as f:
                content = f.read()
            for i, line in enumerate(content.splitlines(), 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if re.search(r"\bimport\s+browser\b", stripped) or re.search(
                    r"\bfrom\s+browser\b", stripped
                ):
                    violations.append(f"{filename}:{i}: {stripped}")
        assert violations == [], (
            "CA-UC-025-10 violation — browser import found in core:\n" + "\n".join(violations)
        )


# ---------------------------------------------------------------------------
# Structural tests — web/index.html (REPL-only layout)
# ---------------------------------------------------------------------------
class TestIndexHtml:

    @pytest.fixture(autouse=True)
    def _load_html(self):
        self.path = os.path.join(WEB_DIR, "index.html")
        with open(self.path, encoding="utf-8") as f:
            self.content = f.read()

    def test_index_html_exists(self):
        assert os.path.isfile(self.path)

    def test_index_html_doctype(self):
        assert self.content.strip().lower().startswith("<!doctype html>")

    def test_index_html_lang_fr(self):
        assert 'lang="fr"' in self.content

    def test_index_html_charset_utf8(self):
        assert 'charset="UTF-8"' in self.content

    def test_index_html_brython_scripts(self):
        assert 'src="brython.js"' in self.content
        assert 'src="brython_stdlib.js"' in self.content
        assert "https://" not in self.content
        assert "http://" not in self.content

    def test_index_html_boot_screen_element(self):
        # Spinner retiré au profit du boot-screen damier Apple II.
        assert "boot-screen" in self.content

    def test_index_html_console_output(self):
        assert 'id="console-output"' in self.content

    def test_index_html_no_editor_panel(self):
        """REPL pur — pas de panneau éditeur séparé."""
        assert 'id="editor"' not in self.content
        assert "editor-panel" not in self.content

    def test_index_html_canvas(self):
        assert 'id="graphics-canvas"' in self.content
        assert "<canvas" in self.content

    def test_index_html_toolbar_buttons(self):
        # Apple II look: LOAD + STOP + RESET (the three keys that have no
        # equivalent typed BASIC command). RUN/LIST/SAVE/NEW are typed.
        for btn_id in ("btn-load", "btn-stop", "btn-reset"):
            assert f'id="{btn_id}"' in self.content, f"Missing toolbar button: {btn_id}"

    def test_index_html_blinking_cursor_elements(self):
        # Apple II single-screen model: input display + blinking block cursor
        # live inside console-output (no separate input-line row).
        assert 'id="console-input-display"' in self.content
        assert 'id="console-cursor"' in self.content

    def test_index_html_io_web_script(self):
        assert 'src="io_web.py"' in self.content
        assert 'type="text/python"' in self.content

    def test_index_html_brython_call(self):
        assert "brython(" in self.content

    def test_index_html_no_innerhtml(self):
        assert "innerHTML" not in self.content


# ---------------------------------------------------------------------------
# Structural tests — web/style.css (Apple II font)
# ---------------------------------------------------------------------------
class TestStyleCss:

    @pytest.fixture(autouse=True)
    def _load_css(self):
        self.path = os.path.join(WEB_DIR, "style.css")
        with open(self.path, encoding="utf-8") as f:
            self.content = f.read()

    def test_style_css_exists(self):
        assert os.path.isfile(self.path)

    def test_style_css_apple2_font_face(self):
        """Must declare @font-face for Apple II font (RG-0012)."""
        assert "@font-face" in self.content
        assert "Apple II" in self.content

    def test_style_css_apple2_woff2(self):
        """Must reference local apple2.woff2 font file."""
        assert "apple2.woff2" in self.content

    def test_style_css_black_background(self):
        assert "#000" in self.content

    def test_style_css_green_text(self):
        assert "#33ff33" in self.content

    def test_style_css_monospace_fallback(self):
        assert "monospace" in self.content

    def test_style_css_spinner_animation(self):
        assert "@keyframes" in self.content
        assert "spin" in self.content

    def test_style_css_responsive_breakpoint(self):
        assert "@media" in self.content and "768px" in self.content

    def test_style_css_40_columns_mode(self):
        assert "40ch" in self.content

    def test_style_css_80_columns_mode(self):
        assert "80ch" in self.content


# ---------------------------------------------------------------------------
# Apple II font file
# ---------------------------------------------------------------------------
class TestApple2Font:
    """Verify Apple II font files exist (RG-0012)."""

    def test_apple2_woff2_exists(self):
        path = os.path.join(WEB_DIR, "fonts", "apple2.woff2")
        assert os.path.isfile(path), f"Missing: {path}"

    def test_apple2_ttf_exists(self):
        path = os.path.join(WEB_DIR, "fonts", "apple2.ttf")
        assert os.path.isfile(path), f"Missing: {path}"

    def test_apple2_woff2_reasonable_size(self):
        """Font file should be < 50 Ko (bitmap font is small)."""
        path = os.path.join(WEB_DIR, "fonts", "apple2.woff2")
        size = os.path.getsize(path)
        assert size < 50_000, f"Font too large: {size} bytes"
        assert size > 100, f"Font too small: {size} bytes"


# ---------------------------------------------------------------------------
# Structural tests — web/io_web.py (REPL-only)
# ---------------------------------------------------------------------------
class TestIoWebPy:

    @pytest.fixture(autouse=True)
    def _load_ioweb(self):
        self.path = os.path.join(WEB_DIR, "io_web.py")
        with open(self.path, encoding="utf-8") as f:
            self.content = f.read()

    def test_io_web_py_exists(self):
        assert os.path.isfile(self.path)

    def test_io_web_py_defines_class(self):
        assert "class IOBridgeWeb" in self.content

    def test_io_web_py_has_print_str(self):
        assert "def print_str(self" in self.content

    def test_io_web_py_has_input_str(self):
        assert "def input_str(self" in self.content

    def test_io_web_py_has_get_char(self):
        assert "def get_char(self" in self.content

    def test_io_web_py_has_clear_screen(self):
        assert "def clear_screen(self" in self.content

    def test_io_web_py_has_check_interrupt(self):
        assert "def check_interrupt(self" in self.content

    def test_io_web_py_uses_textcontent(self):
        assert "textContent" in self.content

    def test_io_web_py_no_innerhtml(self):
        assert "innerHTML" not in self.content

    def test_io_web_py_imports_browser(self):
        assert "from browser" in self.content or "import browser" in self.content

    def test_io_web_py_imports_repl(self):
        assert "from applesoft.repl import REPL" in self.content

    def test_io_web_py_init_function(self):
        assert "def init():" in self.content

    def test_io_web_py_boot_screen_animation(self):
        # Le spinner Brython a été retiré au profit d'un boot-screen damier
        # qui se révèle ligne par ligne (UC-FID-003 ext. LookAppleII).
        assert "boot-screen" in self.content
        assert "boot-running" in self.content

    def test_io_web_py_shows_prompt(self):
        assert '"]"' in self.content or "']'" in self.content

    def test_io_web_py_no_editor_references(self):
        """REPL pur — pas de code éditeur dans io_web.py."""
        assert "editor-highlight" not in self.content
        assert "_highlight_editor" not in self.content
        assert "APPLESOFT_KEYWORDS" not in self.content


# ---------------------------------------------------------------------------
# Time-slicing structural tests
# ---------------------------------------------------------------------------
class TestIoWebTimeslicing:

    @pytest.fixture(autouse=True)
    def _load_ioweb(self):
        with open(os.path.join(WEB_DIR, "io_web.py"), encoding="utf-8") as f:
            self.content = f.read()

    def test_io_web_py_imports_timer(self):
        assert "timer" in self.content

    def test_io_web_py_has_run_program_sliced(self):
        assert "def _run_program_sliced(self" in self.content

    def test_io_web_py_has_resume_slice(self):
        assert "def _resume_slice(self" in self.content

    def test_io_web_py_imports_yield_signal(self):
        assert "YieldSignal" in self.content

    def test_io_web_py_imports_input_request_signal(self):
        assert "InputRequestSignal" in self.content

    def test_io_web_py_uses_set_timeout(self):
        assert "set_timeout" in self.content

    def test_io_web_py_has_set_yield_threshold(self):
        assert "set_yield_threshold" in self.content

    def test_io_web_py_stop_button_interrupt(self):
        assert "_on_stop_click" in self.content
        assert "set_interrupted" in self.content

    def test_io_web_py_get_char_async(self):
        assert '"get"' in self.content or "'get'" in self.content

    def test_io_web_py_no_innerhtml_timeslicing(self):
        assert "innerHTML" not in self.content

    def test_io_web_py_running_flag(self):
        assert "_running" in self.content

    def test_io_web_py_waiting_for_input_flag(self):
        assert "_waiting_for_input" in self.content


# ---------------------------------------------------------------------------
# Persistence structural tests
# ---------------------------------------------------------------------------
class TestPersistenceStructure:

    @pytest.fixture(autouse=True)
    def _load_files(self):
        with open(os.path.join(WEB_DIR, "index.html"), encoding="utf-8") as f:
            self.html = f.read()
        with open(os.path.join(WEB_DIR, "io_web.py"), encoding="utf-8") as f:
            self.ioweb = f.read()

    def test_load_button_exists(self):
        assert 'id="btn-load"' in self.html

    def test_save_command_available(self):
        # SAVE is no longer a toolbar button; it's a typed BASIC command
        # exposed via the file-export helper used by the interpreter.
        assert "export_file" in self.ioweb

    def test_ioweb_localstorage_save(self):
        assert "localStorage" in self.ioweb

    def test_ioweb_localstorage_load(self):
        assert "getItem" in self.ioweb or "localStorage" in self.ioweb

    def test_ioweb_file_export(self):
        assert "Blob" in self.ioweb or "blob" in self.ioweb

    def test_ioweb_drag_drop(self):
        assert "drop" in self.ioweb.lower()

    def test_ioweb_file_size_limit(self):
        assert "1_000_000" in self.ioweb or "1000000" in self.ioweb

    def test_ioweb_file_extension_validation(self):
        assert ".bas" in self.ioweb or ".txt" in self.ioweb

    def test_ioweb_no_innerhtml_persistence(self):
        assert "innerHTML" not in self.ioweb


# ---------------------------------------------------------------------------
# Canvas structural tests
# ---------------------------------------------------------------------------
class TestCanvasStructure:

    @pytest.fixture(autouse=True)
    def _load_files(self):
        with open(os.path.join(WEB_DIR, "index.html"), encoding="utf-8") as f:
            self.html = f.read()
        with open(os.path.join(WEB_DIR, "style.css"), encoding="utf-8") as f:
            self.css = f.read()
        with open(os.path.join(WEB_DIR, "io_web.py"), encoding="utf-8") as f:
            self.ioweb = f.read()

    def test_canvas_element_exists(self):
        assert '<canvas id="graphics-canvas"' in self.html

    def test_canvas_pixelated_rendering(self):
        assert "pixelated" in self.css

    def test_ioweb_has_show_canvas(self):
        assert "_show_canvas" in self.ioweb

    def test_ioweb_has_hide_canvas(self):
        assert "_hide_canvas" in self.ioweb

    def test_ioweb_lores_palette_16_colors(self):
        assert "LORES_COLORS" in self.ioweb
        match = re.search(r"LORES_COLORS\s*=\s*\[(.*?)\]", self.ioweb, re.DOTALL)
        assert match is not None
        colors = re.findall(r'"#[0-9A-Fa-f]{6}"', match.group(1))
        assert len(colors) == 16

    def test_ioweb_hires_palette(self):
        assert "HIRES_COLORS" in self.ioweb

    def test_ioweb_uses_canvas_api(self):
        assert "fillRect" in self.ioweb or "getContext" in self.ioweb

    def test_ioweb_no_innerhtml_canvas(self):
        assert "innerHTML" not in self.ioweb


# ---------------------------------------------------------------------------
# Time-slicing mechanics — pure Python tests (no browser needed)
# ---------------------------------------------------------------------------
class TestYieldSignal:

    def test_yield_signal_exists(self):
        from applesoft.interpreter import YieldSignal
        sig = YieldSignal(10, 0)
        assert sig.line_num == 10

    def test_input_request_signal_exists(self):
        from applesoft.interpreter import InputRequestSignal
        sig = InputRequestSignal(10, 0, "get", "")
        assert sig.kind == "get"

    def test_yield_threshold_default_infinite(self):
        from applesoft.environment import Environment
        from applesoft.interpreter import Interpreter
        from applesoft.io_cli import IOBridgeCLI
        from applesoft.program import Program
        io = IOBridgeCLI()
        interp = Interpreter(Program(), Environment(), io)
        assert interp.get_yield_threshold() == float("inf")

    def test_yield_threshold_configurable(self):
        from applesoft.environment import Environment
        from applesoft.interpreter import Interpreter
        from applesoft.io_cli import IOBridgeCLI
        from applesoft.program import Program
        io = IOBridgeCLI()
        interp = Interpreter(Program(), Environment(), io)
        interp.set_yield_threshold(100)
        assert interp.get_yield_threshold() == 100

    def test_yield_signal_raised_at_threshold(self):
        from applesoft.environment import Environment
        from applesoft.interpreter import Interpreter, YieldSignal
        from applesoft.io_cli import IOBridgeCLI
        from applesoft.lexer import tokenize
        from applesoft.program import Program
        io = IOBridgeCLI()
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)
        tokens = tokenize("10 GOTO 10")
        prog.add_line(10, tokens[1:])
        interp.set_yield_threshold(5)
        with pytest.raises(YieldSignal) as exc_info:
            interp.run()
        assert exc_info.value.line_num == 10

    def test_resume_execution_continues(self):
        from applesoft.environment import Environment
        from applesoft.interpreter import Interpreter, YieldSignal
        from applesoft.io_cli import IOBridgeCLI
        from applesoft.lexer import tokenize
        from applesoft.program import Program
        io = IOBridgeCLI()
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)
        tokens = tokenize("10 GOTO 10")
        prog.add_line(10, tokens[1:])
        interp.set_yield_threshold(3)
        with pytest.raises(YieldSignal) as exc_info:
            interp.run()
        first_yield = exc_info.value
        with pytest.raises(YieldSignal):
            interp.resume_execution(first_yield.line_num, first_yield.stmt_idx)

    def test_interrupt_between_slices(self):
        from applesoft.environment import Environment
        from applesoft.interpreter import Interpreter, YieldSignal
        from applesoft.io_cli import IOBridgeCLI
        from applesoft.lexer import tokenize
        from applesoft.program import Program
        io = IOBridgeCLI()
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)
        tokens = tokenize("10 GOTO 10")
        prog.add_line(10, tokens[1:])
        interp.set_yield_threshold(5)
        with pytest.raises(YieldSignal) as exc_info:
            interp.run()
        y = exc_info.value
        io.set_interrupted()
        interp.resume_execution(y.line_num, y.stmt_idx)

    def test_cli_mode_not_affected(self):
        from applesoft.environment import Environment
        from applesoft.interpreter import Interpreter
        from applesoft.io_cli import IOBridgeCLI
        from applesoft.lexer import tokenize
        from applesoft.program import Program
        io = IOBridgeCLI()
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)
        tokens10 = tokenize('10 PRINT "HELLO"')
        prog.add_line(10, tokens10[1:])
        tokens20 = tokenize("20 END")
        prog.add_line(20, tokens20[1:])
        interp.run()

    def test_yield_signal_preserves_state(self):
        from applesoft.environment import Environment
        from applesoft.interpreter import Interpreter, YieldSignal
        from applesoft.io_cli import IOBridgeCLI
        from applesoft.lexer import tokenize
        from applesoft.program import Program
        io = IOBridgeCLI()
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)
        tokens10 = tokenize("10 X = 42")
        prog.add_line(10, tokens10[1:])
        tokens20 = tokenize("20 GOTO 20")
        prog.add_line(20, tokens20[1:])
        interp.set_yield_threshold(5)
        with pytest.raises(YieldSignal):
            interp.run()
        assert env.get_var("X") == 42.0

    def test_input_request_signal_for_get(self):
        from applesoft.environment import Environment
        from applesoft.interpreter import InputRequestSignal, Interpreter
        from applesoft.io_cli import IOBridgeCLI
        from applesoft.lexer import tokenize
        from applesoft.program import Program
        io = IOBridgeCLI()
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)
        tokens = tokenize("10 GET A$")
        prog.add_line(10, tokens[1:])
        interp.set_yield_threshold(1000)
        with pytest.raises(InputRequestSignal) as exc_info:
            interp.run()
        assert exc_info.value.kind == "get"

    def test_input_request_signal_for_input(self):
        from applesoft.environment import Environment
        from applesoft.interpreter import InputRequestSignal, Interpreter
        from applesoft.io_cli import IOBridgeCLI
        from applesoft.lexer import tokenize
        from applesoft.program import Program
        io = IOBridgeCLI()
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)
        tokens = tokenize("10 INPUT A$")
        prog.add_line(10, tokens[1:])
        interp.set_yield_threshold(1000)
        with pytest.raises(InputRequestSignal) as exc_info:
            interp.run()
        assert exc_info.value.kind == "input"

    def test_resume_after_get_assigns_value(self):
        from applesoft.environment import Environment
        from applesoft.interpreter import InputRequestSignal, Interpreter
        from applesoft.io_cli import IOBridgeCLI
        from applesoft.lexer import tokenize
        from applesoft.program import Program
        io = IOBridgeCLI()
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)
        tokens10 = tokenize("10 GET A$")
        prog.add_line(10, tokens10[1:])
        tokens20 = tokenize("20 END")
        prog.add_line(20, tokens20[1:])
        interp.set_yield_threshold(1000)
        with pytest.raises(InputRequestSignal) as exc_info:
            interp.run()
        sig = exc_info.value
        interp.resume_after_input(sig.line_num, sig.stmt_idx, "A")
        assert env.get_var("A$") == "A"

    def test_resume_after_input_assigns_value(self):
        from applesoft.environment import Environment
        from applesoft.interpreter import InputRequestSignal, Interpreter
        from applesoft.io_cli import IOBridgeCLI
        from applesoft.lexer import tokenize
        from applesoft.program import Program
        io = IOBridgeCLI()
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)
        tokens10 = tokenize("10 INPUT A$")
        prog.add_line(10, tokens10[1:])
        tokens20 = tokenize("20 END")
        prog.add_line(20, tokens20[1:])
        interp.set_yield_threshold(1000)
        with pytest.raises(InputRequestSignal) as exc_info:
            interp.run()
        sig = exc_info.value
        interp.resume_after_input(sig.line_num, sig.stmt_idx, "HELLO")
        assert env.get_var("A$") == "HELLO"

    def test_get_cli_mode_synchronous(self):
        from unittest.mock import MagicMock
        from applesoft.environment import Environment
        from applesoft.interpreter import Interpreter
        from applesoft.lexer import tokenize
        from applesoft.program import Program
        io = MagicMock()
        io.check_interrupt.return_value = False
        io.get_char.return_value = "A"
        io.get_cursor_column.return_value = 1
        io.get_last_key.return_value = 0
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)
        tokens10 = tokenize("10 GET A$")
        prog.add_line(10, tokens10[1:])
        tokens20 = tokenize("20 END")
        prog.add_line(20, tokens20[1:])
        interp.run()
        io.get_char.assert_called_once()
        assert env.get_var("A$") == "A"

    def test_multiple_yield_resume_cycles(self):
        from applesoft.environment import Environment
        from applesoft.interpreter import Interpreter, YieldSignal
        from applesoft.io_cli import IOBridgeCLI
        from applesoft.lexer import tokenize
        from applesoft.program import Program
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
            for _ in range(100):
                try:
                    interp.resume_execution(y.line_num, y.stmt_idx)
                    finished = True
                    break
                except YieldSignal as y2:
                    y = y2
        assert finished
        assert env.get_var("X") == 10.0
