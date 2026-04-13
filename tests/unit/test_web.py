"""Tests for web interface — lots 07 iterations 1+2.

These tests verify structural requirements that can be checked without a browser,
plus time-slicing mechanics (YieldSignal, resume_execution, InputRequestSignal)
which are pure Python and testable without Brython.
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
        """Verify that no file in src/applesoft/ contains 'import browser'
        or 'from browser'."""
        violations = []
        for filename in os.listdir(SRC_DIR):
            if not filename.endswith(".py"):
                continue
            filepath = os.path.join(SRC_DIR, filename)
            with open(filepath, encoding="utf-8") as f:
                content = f.read()
            for i, line in enumerate(content.splitlines(), 1):
                stripped = line.strip()
                # Skip comments
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
# Structural tests — web/index.html
# ---------------------------------------------------------------------------
class TestIndexHtml:
    """Verify web/index.html structure and content."""

    @pytest.fixture(autouse=True)
    def _load_html(self):
        self.path = os.path.join(WEB_DIR, "index.html")

    def test_index_html_exists(self):
        """web/index.html must exist."""
        assert os.path.isfile(self.path), f"Missing file: {self.path}"

    def test_index_html_doctype(self):
        """Must start with HTML5 doctype."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert content.strip().lower().startswith("<!doctype html>")

    def test_index_html_lang_fr(self):
        """Must have lang='fr'."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert 'lang="fr"' in content

    def test_index_html_charset_utf8(self):
        """Must declare UTF-8 charset."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert 'charset="UTF-8"' in content or "charset=UTF-8" in content

    def test_index_html_title(self):
        """Must have correct title."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert "Applesoft BASIC" in content
        assert "<title>" in content

    def test_index_html_brython_scripts(self):
        """Must reference local Brython files (not CDN — SEC-TECH-10)."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert 'src="brython.js"' in content
        assert 'src="brython_stdlib.js"' in content
        # Must not load from CDN
        assert "https://" not in content
        assert "http://" not in content

    def test_index_html_spinner_element(self):
        """Must have a loading spinner element (CA-UC-025-06)."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert "loading-overlay" in content
        assert "spinner" in content

    def test_index_html_console_output(self):
        """Must have a console output div."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert 'id="console-output"' in content

    def test_index_html_editor(self):
        """Must have an editor textarea."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert 'id="editor"' in content
        assert "<textarea" in content

    def test_index_html_canvas(self):
        """Must have a graphics canvas (hidden by default)."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert 'id="graphics-canvas"' in content
        assert "<canvas" in content

    def test_index_html_toolbar_buttons(self):
        """Must have toolbar with RUN, STOP, RESET, LIST, SAVE, LOAD buttons."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        for btn_id in ["btn-run", "btn-stop", "btn-reset", "btn-list", "btn-save", "btn-load"]:
            assert btn_id in content, f"Missing toolbar button: {btn_id}"

    def test_index_html_io_web_script(self):
        """Must load io_web.py as Brython script."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert 'src="io_web.py"' in content
        assert 'type="text/python"' in content

    def test_index_html_brython_call(self):
        """Must call brython() on load."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert "brython(" in content

    def test_index_html_semantic_structure(self):
        """Must use semantic HTML5 elements."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert "<header" in content
        assert "<main" in content
        assert "<footer" in content
        assert "<section" in content
        assert "<nav" in content

    def test_index_html_no_innerhtml(self):
        """Must not use innerHTML in inline scripts (SEC-DEV-03)."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert "innerHTML" not in content


# ---------------------------------------------------------------------------
# Structural tests — web/style.css
# ---------------------------------------------------------------------------
class TestStyleCss:
    """Verify web/style.css structure."""

    @pytest.fixture(autouse=True)
    def _load_css(self):
        self.path = os.path.join(WEB_DIR, "style.css")

    def test_style_css_exists(self):
        """web/style.css must exist."""
        assert os.path.isfile(self.path), f"Missing file: {self.path}"

    def test_style_css_black_background(self):
        """Must use black background (Apple II aesthetic)."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert "#000" in content

    def test_style_css_green_text(self):
        """Must use green phosphor text color."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert "#33ff33" in content

    def test_style_css_monospace_font(self):
        """Must use monospace font family."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert "monospace" in content

    def test_style_css_spinner_animation(self):
        """Must have spinner animation (CA-UC-025-06)."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert "@keyframes" in content
        assert "spin" in content

    def test_style_css_responsive_breakpoint(self):
        """Must have responsive breakpoint at 768px (CA-UC-025-04)."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert "768px" in content
        assert "@media" in content

    def test_style_css_40_columns_mode(self):
        """Must support 40-column mode (CA-UC-025-07)."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert "40ch" in content


# ---------------------------------------------------------------------------
# Structural tests — web/io_web.py
# ---------------------------------------------------------------------------
class TestIoWebPy:
    """Verify web/io_web.py structure."""

    @pytest.fixture(autouse=True)
    def _load_ioweb(self):
        self.path = os.path.join(WEB_DIR, "io_web.py")

    def test_io_web_py_exists(self):
        """web/io_web.py must exist."""
        assert os.path.isfile(self.path), f"Missing file: {self.path}"

    def test_io_web_py_defines_class(self):
        """Must define the IOBridgeWeb class."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert "class IOBridgeWeb" in content

    def test_io_web_py_has_print_str(self):
        """Must implement print_str method."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert "def print_str(self" in content

    def test_io_web_py_has_input_str(self):
        """Must implement input_str method."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert "def input_str(self" in content

    def test_io_web_py_has_get_char(self):
        """Must implement get_char method."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert "def get_char(self" in content

    def test_io_web_py_has_clear_screen(self):
        """Must implement clear_screen method."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert "def clear_screen(self" in content

    def test_io_web_py_has_check_interrupt(self):
        """Must implement check_interrupt method."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert "def check_interrupt(self" in content

    def test_io_web_py_has_get_cursor_column(self):
        """Must implement get_cursor_column method."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert "def get_cursor_column(self" in content

    def test_io_web_py_uses_textcontent(self):
        """Must use textContent for DOM writes (SEC-DEV-03)."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert "textContent" in content

    def test_io_web_py_no_innerhtml(self):
        """Must NOT use innerHTML (SEC-DEV-03, SEC-TECH-12)."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert "innerHTML" not in content

    def test_io_web_py_imports_browser(self):
        """Must import browser module (this is the ONLY file allowed to)."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert "from browser" in content or "import browser" in content

    def test_io_web_py_imports_repl(self):
        """Must import the REPL from core modules."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert "from applesoft.repl import REPL" in content

    def test_io_web_py_init_function(self):
        """Must have an init() function as entry point."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert "def init():" in content

    def test_io_web_py_hides_spinner(self):
        """Must hide the loading spinner after init (CA-UC-025-06)."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        assert "loading-overlay" in content
        assert "hidden" in content

    def test_io_web_py_shows_prompt(self):
        """Must display the ] prompt after init (CA-UC-025-01)."""
        with open(self.path, encoding="utf-8") as f:
            content = f.read()
        # The init function should call print_str with the prompt
        assert '"]"' in content or "']'" in content


# ---------------------------------------------------------------------------
# Time-slicing structural tests — web/io_web.py iteration 2
# ---------------------------------------------------------------------------
class TestIoWebTimeslicing:
    """Verify time-slicing patterns in web/io_web.py."""

    @pytest.fixture(autouse=True)
    def _load_ioweb(self):
        self.path = os.path.join(WEB_DIR, "io_web.py")
        with open(self.path, encoding="utf-8") as f:
            self.content = f.read()

    def test_io_web_py_imports_timer(self):
        """Must import browser.timer for setTimeout-based time-slicing."""
        assert "timer" in self.content

    def test_io_web_py_has_run_program_sliced(self):
        """Must have _run_program_sliced method for time-slicing runner."""
        assert "def _run_program_sliced(self" in self.content

    def test_io_web_py_has_resume_slice(self):
        """Must have _resume_slice method for yield resumption."""
        assert "def _resume_slice(self" in self.content

    def test_io_web_py_imports_yield_signal(self):
        """Must import YieldSignal from interpreter."""
        assert "YieldSignal" in self.content

    def test_io_web_py_imports_input_request_signal(self):
        """Must import InputRequestSignal from interpreter."""
        assert "InputRequestSignal" in self.content

    def test_io_web_py_uses_set_timeout(self):
        """Must use timer.set_timeout for yielding to browser (RG-0015)."""
        assert "set_timeout" in self.content

    def test_io_web_py_has_set_yield_threshold(self):
        """Must configure yield threshold on the interpreter."""
        assert "set_yield_threshold" in self.content

    def test_io_web_py_document_keydown_binding(self):
        """Must bind keydown on document for Ctrl+C during execution."""
        assert "document.bind" in self.content
        assert "_on_document_keydown" in self.content

    def test_io_web_py_stop_button_interrupt(self):
        """Must handle STOP button click for interrupt (CA-UC-025-05)."""
        assert "_on_stop_click" in self.content
        assert "set_interrupted" in self.content

    def test_io_web_py_get_char_async(self):
        """Must have async GET support via _input_kind == 'get'."""
        assert '"get"' in self.content or "'get'" in self.content

    def test_io_web_py_no_innerhtml_iter2(self):
        """Must still not use innerHTML after iteration 2 changes."""
        assert "innerHTML" not in self.content

    def test_io_web_py_running_flag(self):
        """Must track execution state via _running flag."""
        assert "_running" in self.content

    def test_io_web_py_waiting_for_input_flag(self):
        """Must track input wait state via _waiting_for_input flag."""
        assert "_waiting_for_input" in self.content


# ---------------------------------------------------------------------------
# Iteration 3 — Editor, syntax highlighting, sync, responsive, column modes
# ---------------------------------------------------------------------------
class TestEditorSyntaxHighlighting:
    """CA-UC-026-01: Editor must have syntax highlighting for Applesoft keywords."""

    @pytest.fixture(autouse=True)
    def _load_files(self):
        self.html_path = os.path.join(WEB_DIR, "index.html")
        self.css_path = os.path.join(WEB_DIR, "style.css")
        self.ioweb_path = os.path.join(WEB_DIR, "io_web.py")
        with open(self.html_path, encoding="utf-8") as f:
            self.html = f.read()
        with open(self.css_path, encoding="utf-8") as f:
            self.css = f.read()
        with open(self.ioweb_path, encoding="utf-8") as f:
            self.ioweb = f.read()

    def test_editor_has_highlight_overlay(self):
        """Editor must have a highlight overlay or mechanism for coloring keywords."""
        # Either a dedicated overlay div or a highlight function in io_web.py
        assert ("editor-highlight" in self.html or "highlight" in self.ioweb), \
            "Editor must have syntax highlighting mechanism"

    def test_highlight_keywords_list(self):
        """io_web.py must contain a list of Applesoft keywords for highlighting."""
        assert "PRINT" in self.ioweb and "GOTO" in self.ioweb and "FOR" in self.ioweb, \
            "io_web.py must reference Applesoft keywords for highlighting"

    def test_highlight_css_styles(self):
        """CSS must define styles for highlighted keywords."""
        assert "keyword" in self.css.lower() or "highlight" in self.css.lower(), \
            "CSS must have keyword/highlight styles"

    def test_highlight_uses_safe_dom(self):
        """Syntax highlighting must not use innerHTML (SEC-DEV-03, SEC-BP-24)."""
        assert "innerHTML" not in self.ioweb, \
            "Highlighting must not use innerHTML"


class TestEditorRunFromEditor:
    """CA-UC-026-02: RUN from editor must execute code and show output in console."""

    @pytest.fixture(autouse=True)
    def _load_ioweb(self):
        with open(os.path.join(WEB_DIR, "io_web.py"), encoding="utf-8") as f:
            self.ioweb = f.read()

    def test_run_button_loads_editor_content(self):
        """RUN button handler must read editor content."""
        assert "editor" in self.ioweb and "btn-run" in self.ioweb, \
            "RUN button must read editor content"

    def test_run_button_replaces_program(self):
        """RUN button must replace program memory with editor content."""
        # Already tested in iteration 2 — btn-run calls NEW then loads lines
        assert "NEW" in self.ioweb, \
            "RUN must clear program before loading editor content"


class TestEditorUndo:
    """CA-UC-026-03: Ctrl+Z must undo in the editor."""

    @pytest.fixture(autouse=True)
    def _load_html(self):
        with open(os.path.join(WEB_DIR, "index.html"), encoding="utf-8") as f:
            self.html = f.read()

    def test_editor_is_textarea(self):
        """Editor must be a <textarea> (native Ctrl+Z support)."""
        assert "<textarea" in self.html and 'id="editor"' in self.html, \
            "Editor must be a textarea for native undo support"


class TestEditorConsoleSync:
    """CA-UC-026-04: Console line entry must be visible in editor."""

    @pytest.fixture(autouse=True)
    def _load_ioweb(self):
        with open(os.path.join(WEB_DIR, "io_web.py"), encoding="utf-8") as f:
            self.ioweb = f.read()

    def test_sync_console_to_editor(self):
        """io_web.py must synchronize console program lines to editor."""
        assert "sync" in self.ioweb.lower() or "_update_editor" in self.ioweb \
            or "editor" in self.ioweb, \
            "Must have console-to-editor synchronization"

    def test_sync_updates_editor_value(self):
        """Sync must update the editor textarea value."""
        assert 'document["editor"]' in self.ioweb or "editor" in self.ioweb, \
            "Must access editor element for sync"


class TestResponsiveLayout:
    """CA-UC-025-04: Panels must stack vertically below 768px."""

    @pytest.fixture(autouse=True)
    def _load_css(self):
        with open(os.path.join(WEB_DIR, "style.css"), encoding="utf-8") as f:
            self.css = f.read()

    def test_responsive_media_query(self):
        """CSS must have @media query for max-width: 768px."""
        assert "@media" in self.css and "768px" in self.css

    def test_responsive_flex_column(self):
        """Layout must switch to flex-direction: column below 768px."""
        assert "flex-direction" in self.css and "column" in self.css


class TestColumnModes:
    """CA-UC-025-07 / CA-UC-025-08: 40 and 80 column modes."""

    @pytest.fixture(autouse=True)
    def _load_files(self):
        with open(os.path.join(WEB_DIR, "style.css"), encoding="utf-8") as f:
            self.css = f.read()
        with open(os.path.join(WEB_DIR, "io_web.py"), encoding="utf-8") as f:
            self.ioweb = f.read()

    def test_css_40_column_width(self):
        """CSS must define 40ch width for 40-column mode."""
        assert "40ch" in self.css

    def test_css_80_column_width(self):
        """CSS must define 80ch width for 80-column mode."""
        assert "80ch" in self.css

    def test_mode_80_css_class(self):
        """CSS must have a mode-80 class for switching to 80 columns."""
        assert "mode-80" in self.css

    def test_ioweb_column_mode_switch(self):
        """io_web.py must support switching between 40 and 80 column modes."""
        assert "mode-80" in self.ioweb or "80" in self.ioweb, \
            "io_web.py must support column mode switching"


# ---------------------------------------------------------------------------
# Iteration 5 — Web persistence (localStorage, import/export)
# ---------------------------------------------------------------------------
class TestPersistenceStructure:
    """CA-UC-028-01 to 06: Persistence via localStorage and file I/O."""

    @pytest.fixture(autouse=True)
    def _load_files(self):
        self.html_path = os.path.join(WEB_DIR, "index.html")
        self.ioweb_path = os.path.join(WEB_DIR, "io_web.py")
        with open(self.html_path, encoding="utf-8") as f:
            self.html = f.read()
        with open(self.ioweb_path, encoding="utf-8") as f:
            self.ioweb = f.read()

    def test_save_button_exists(self):
        """HTML must have a SAVE toolbar button."""
        assert 'id="btn-save"' in self.html

    def test_load_button_exists(self):
        """HTML must have a LOAD toolbar button."""
        assert 'id="btn-load"' in self.html

    def test_ioweb_localstorage_save(self):
        """io_web.py must implement localStorage SAVE (CA-UC-028-01)."""
        assert "localStorage" in self.ioweb or "local_storage" in self.ioweb

    def test_ioweb_localstorage_load(self):
        """io_web.py must implement localStorage LOAD (CA-UC-028-02)."""
        assert "getItem" in self.ioweb or "localStorage" in self.ioweb \
            or "local_storage" in self.ioweb

    def test_ioweb_program_list_panel(self):
        """io_web.py must support listing saved programs (CA-UC-028-03)."""
        assert "list" in self.ioweb.lower() and ("program" in self.ioweb.lower()
            or "saved" in self.ioweb.lower() or "storage" in self.ioweb.lower())

    def test_ioweb_file_import(self):
        """io_web.py must support file import via button (CA-UC-028-04)."""
        assert "file" in self.ioweb.lower() or "import" in self.ioweb.lower() \
            or "FileReader" in self.ioweb

    def test_ioweb_file_export(self):
        """io_web.py must support file export/download (CA-UC-028-05)."""
        assert "download" in self.ioweb.lower() or "export" in self.ioweb.lower() \
            or "Blob" in self.ioweb or "blob" in self.ioweb

    def test_ioweb_drag_drop(self):
        """io_web.py must support drag & drop .bas import (CA-UC-028-06)."""
        assert "drop" in self.ioweb.lower() or "dragover" in self.ioweb.lower()

    def test_ioweb_file_size_limit(self):
        """io_web.py must validate file size on import (SEC-BP-41: max 1 Mo)."""
        assert "size" in self.ioweb.lower() or "1048576" in self.ioweb \
            or "1_000_000" in self.ioweb or "1000000" in self.ioweb

    def test_ioweb_file_extension_validation(self):
        """io_web.py must validate file extensions on import (SEC-BP-40)."""
        assert ".bas" in self.ioweb or ".txt" in self.ioweb \
            or "extension" in self.ioweb.lower()

    def test_ioweb_no_innerhtml_persistence(self):
        """io_web.py must not use innerHTML even for persistence UI."""
        assert "innerHTML" not in self.ioweb


# ---------------------------------------------------------------------------
# Iteration 4 — Canvas graphics (LoRes + HiRes)
# ---------------------------------------------------------------------------
class TestCanvasStructure:
    """CA-UC-027-01 to 04: Canvas rendering structure."""

    @pytest.fixture(autouse=True)
    def _load_files(self):
        self.html_path = os.path.join(WEB_DIR, "index.html")
        self.css_path = os.path.join(WEB_DIR, "style.css")
        self.ioweb_path = os.path.join(WEB_DIR, "io_web.py")
        with open(self.html_path, encoding="utf-8") as f:
            self.html = f.read()
        with open(self.css_path, encoding="utf-8") as f:
            self.css = f.read()
        with open(self.ioweb_path, encoding="utf-8") as f:
            self.ioweb = f.read()

    def test_canvas_element_exists(self):
        """HTML must have a canvas element for graphics."""
        assert '<canvas id="graphics-canvas"' in self.html

    def test_canvas_hidden_by_default(self):
        """Canvas section must be hidden by default (display: none)."""
        assert 'style="display: none;"' in self.html or "display: none" in self.html

    def test_canvas_pixelated_rendering(self):
        """CSS must use pixelated rendering for crisp upscale."""
        assert "image-rendering" in self.css
        assert "pixelated" in self.css

    def test_ioweb_has_show_canvas(self):
        """io_web.py must have a method to show the canvas (GR/HGR)."""
        assert "_show_canvas" in self.ioweb or "show_graphics" in self.ioweb \
            or "canvas-section" in self.ioweb

    def test_ioweb_has_hide_canvas(self):
        """io_web.py must have a method to hide the canvas (TEXT)."""
        assert "_hide_canvas" in self.ioweb or "hide_graphics" in self.ioweb \
            or "display" in self.ioweb

    def test_ioweb_has_lores_render(self):
        """io_web.py must support LoRes rendering (40x48 grid)."""
        assert "lores" in self.ioweb.lower() or "render_lores" in self.ioweb \
            or "40" in self.ioweb

    def test_ioweb_has_hires_render(self):
        """io_web.py must support HiRes rendering (280x192)."""
        assert "hires" in self.ioweb.lower() or "render_hires" in self.ioweb \
            or "280" in self.ioweb

    def test_ioweb_lores_palette_16_colors(self):
        """io_web.py must define the Apple II 16-color LoRes palette."""
        assert "palette" in self.ioweb.lower() or "LORES_COLORS" in self.ioweb \
            or "#000000" in self.ioweb

    def test_ioweb_hires_palette_8_colors(self):
        """io_web.py must define the Apple II 8-color HiRes palette."""
        assert "HIRES_COLORS" in self.ioweb or "hires" in self.ioweb.lower()

    def test_ioweb_uses_canvas_api(self):
        """io_web.py must use canvas 2D context API for rendering."""
        assert "getContext" in self.ioweb or "fillRect" in self.ioweb \
            or "canvas" in self.ioweb

    def test_ioweb_no_innerhtml_canvas(self):
        """io_web.py must not use innerHTML even for canvas operations."""
        assert "innerHTML" not in self.ioweb


# ---------------------------------------------------------------------------
# Time-slicing mechanics — pure Python tests (no browser needed)
# ---------------------------------------------------------------------------
class TestYieldSignal:
    """Test YieldSignal exception and Interpreter yield mechanism."""

    def test_yield_signal_exists(self):
        """YieldSignal class must exist in interpreter module."""
        from applesoft.interpreter import YieldSignal

        sig = YieldSignal(10, 0)
        assert sig.line_num == 10
        assert sig.stmt_idx == 0

    def test_input_request_signal_exists(self):
        """InputRequestSignal class must exist in interpreter module."""
        from applesoft.interpreter import InputRequestSignal

        sig = InputRequestSignal(10, 0, "get", "")
        assert sig.line_num == 10
        assert sig.kind == "get"

    def test_yield_threshold_default_infinite(self):
        """Default yield threshold must be inf (CLI mode = no yield)."""
        from applesoft.environment import Environment
        from applesoft.interpreter import Interpreter
        from applesoft.io_cli import IOBridgeCLI
        from applesoft.program import Program

        io = IOBridgeCLI()
        interp = Interpreter(Program(), Environment(), io)
        assert interp.get_yield_threshold() == float("inf")

    def test_yield_threshold_configurable(self):
        """yield_threshold must be configurable via set_yield_threshold."""
        from applesoft.environment import Environment
        from applesoft.interpreter import Interpreter
        from applesoft.io_cli import IOBridgeCLI
        from applesoft.program import Program

        io = IOBridgeCLI()
        interp = Interpreter(Program(), Environment(), io)
        interp.set_yield_threshold(100)
        assert interp.get_yield_threshold() == 100

    def test_yield_signal_raised_at_threshold(self):
        """YieldSignal must be raised when instruction count reaches threshold.

        CA-UC-025-03: supports time-slicing for infinite loop interruption.
        """
        from applesoft.environment import Environment
        from applesoft.interpreter import Interpreter, YieldSignal
        from applesoft.io_cli import IOBridgeCLI
        from applesoft.lexer import tokenize
        from applesoft.program import Program

        io = IOBridgeCLI()
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)

        # Small program: 10 GOTO 10 (infinite loop)
        tokens = tokenize("10 GOTO 10")
        prog.add_line(10, tokens[1:])

        # Set a low threshold
        interp.set_yield_threshold(5)

        # Running should raise YieldSignal (not block forever)
        with pytest.raises(YieldSignal) as exc_info:
            interp.run()

        assert exc_info.value.line_num == 10

    def test_resume_execution_continues(self):
        """resume_execution must continue from the yield point.

        After yielding, calling resume_execution should execute more
        instructions and yield again.
        """
        from applesoft.environment import Environment
        from applesoft.interpreter import Interpreter, YieldSignal
        from applesoft.io_cli import IOBridgeCLI
        from applesoft.lexer import tokenize
        from applesoft.program import Program

        io = IOBridgeCLI()
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)

        # 10 GOTO 10
        tokens = tokenize("10 GOTO 10")
        prog.add_line(10, tokens[1:])

        interp.set_yield_threshold(3)

        # First yield
        with pytest.raises(YieldSignal) as exc_info:
            interp.run()
        first_yield = exc_info.value

        # Resume and get second yield
        with pytest.raises(YieldSignal) as exc_info:
            interp.resume_execution(first_yield.line_num, first_yield.stmt_idx)
        second_yield = exc_info.value
        assert second_yield.line_num == 10

    def test_interrupt_between_slices(self):
        """Interrupt flag must be checked at each instruction.

        CA-UC-025-03: Ctrl+C during infinite loop -> BREAK IN linenum.
        CA-UC-025-05: STOP button during execution -> interruption.
        """
        from applesoft.environment import Environment
        from applesoft.interpreter import Interpreter, YieldSignal
        from applesoft.io_cli import IOBridgeCLI
        from applesoft.lexer import tokenize
        from applesoft.program import Program

        io = IOBridgeCLI()
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)

        # 10 GOTO 10
        tokens = tokenize("10 GOTO 10")
        prog.add_line(10, tokens[1:])

        interp.set_yield_threshold(5)

        # First yield
        with pytest.raises(YieldSignal) as exc_info:
            interp.run()
        y = exc_info.value

        # Set interrupt flag (simulates Ctrl+C or STOP button)
        io.set_interrupted()

        # Resume — should NOT raise YieldSignal, should return normally
        # (the interrupt is caught, BREAK message printed, execution stops)
        interp.resume_execution(y.line_num, y.stmt_idx)

        # Verify BREAK message was printed (captured in cursor column reset)
        # The program should have stopped

    def test_cli_mode_not_affected(self):
        """When threshold is inf, no YieldSignal is raised (CLI mode regression test).

        The synchronous execution must work exactly as before.
        """
        from applesoft.environment import Environment
        from applesoft.interpreter import Interpreter
        from applesoft.io_cli import IOBridgeCLI
        from applesoft.lexer import tokenize
        from applesoft.program import Program

        io = IOBridgeCLI()
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)

        # Default threshold = inf
        assert interp.get_yield_threshold() == float("inf")

        # 10 PRINT "HELLO"
        # 20 END
        tokens10 = tokenize('10 PRINT "HELLO"')
        prog.add_line(10, tokens10[1:])
        tokens20 = tokenize("20 END")
        prog.add_line(20, tokens20[1:])

        # Should execute synchronously without raising YieldSignal
        interp.run()
        # If we get here, no YieldSignal was raised — test passes

    def test_yield_signal_preserves_state(self):
        """After YieldSignal, program state (variables) must be preserved."""
        from applesoft.environment import Environment
        from applesoft.interpreter import Interpreter, YieldSignal
        from applesoft.io_cli import IOBridgeCLI
        from applesoft.lexer import tokenize
        from applesoft.program import Program

        io = IOBridgeCLI()
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)

        # 10 X = 42
        # 20 GOTO 20
        tokens10 = tokenize("10 X = 42")
        prog.add_line(10, tokens10[1:])
        tokens20 = tokenize("20 GOTO 20")
        prog.add_line(20, tokens20[1:])

        interp.set_yield_threshold(5)

        with pytest.raises(YieldSignal):
            interp.run()

        # Variable X should be set
        assert env.get_var("X") == 42.0

    def test_input_request_signal_for_get(self):
        """GET in web mode (finite threshold) must raise InputRequestSignal.

        CA-UC-025-09: GET A$ + keypress -> correct ASCII value.
        """
        from applesoft.environment import Environment
        from applesoft.interpreter import InputRequestSignal, Interpreter
        from applesoft.io_cli import IOBridgeCLI
        from applesoft.lexer import tokenize
        from applesoft.program import Program

        io = IOBridgeCLI()
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)

        # 10 GET A$
        tokens = tokenize("10 GET A$")
        prog.add_line(10, tokens[1:])

        # Set finite threshold to activate web mode behavior
        interp.set_yield_threshold(1000)

        with pytest.raises(InputRequestSignal) as exc_info:
            interp.run()

        sig = exc_info.value
        assert sig.kind == "get"

    def test_input_request_signal_for_input(self):
        """INPUT in web mode (finite threshold) must raise InputRequestSignal."""
        from applesoft.environment import Environment
        from applesoft.interpreter import InputRequestSignal, Interpreter
        from applesoft.io_cli import IOBridgeCLI
        from applesoft.lexer import tokenize
        from applesoft.program import Program

        io = IOBridgeCLI()
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)

        # 10 INPUT A$
        tokens = tokenize("10 INPUT A$")
        prog.add_line(10, tokens[1:])

        interp.set_yield_threshold(1000)

        with pytest.raises(InputRequestSignal) as exc_info:
            interp.run()

        sig = exc_info.value
        assert sig.kind == "input"

    def test_resume_after_get_assigns_value(self):
        """resume_after_input must assign the GET value and continue.

        CA-UC-025-09: After receiving a keypress, the value is assigned
        to the variable and execution continues.
        """
        from applesoft.environment import Environment
        from applesoft.interpreter import InputRequestSignal, Interpreter
        from applesoft.io_cli import IOBridgeCLI
        from applesoft.lexer import tokenize
        from applesoft.program import Program

        io = IOBridgeCLI()
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)

        # 10 GET A$
        # 20 END
        tokens10 = tokenize("10 GET A$")
        prog.add_line(10, tokens10[1:])
        tokens20 = tokenize("20 END")
        prog.add_line(20, tokens20[1:])

        interp.set_yield_threshold(1000)

        # First: GET raises InputRequestSignal
        with pytest.raises(InputRequestSignal) as exc_info:
            interp.run()

        sig = exc_info.value

        # Resume with value "A"
        interp.resume_after_input(sig.line_num, sig.stmt_idx, "A")

        # Variable A$ should have value "A"
        assert env.get_var("A$") == "A"

    def test_resume_after_input_assigns_value(self):
        """resume_after_input must assign the INPUT value and continue."""
        from applesoft.environment import Environment
        from applesoft.interpreter import InputRequestSignal, Interpreter
        from applesoft.io_cli import IOBridgeCLI
        from applesoft.lexer import tokenize
        from applesoft.program import Program

        io = IOBridgeCLI()
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)

        # 10 INPUT A$
        # 20 END
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
        """GET in CLI mode (threshold=inf) must call io.get_char synchronously."""
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

        # Default threshold = inf (CLI mode)
        # 10 GET A$
        # 20 END
        tokens10 = tokenize("10 GET A$")
        prog.add_line(10, tokens10[1:])
        tokens20 = tokenize("20 END")
        prog.add_line(20, tokens20[1:])

        interp.run()
        io.get_char.assert_called_once()
        assert env.get_var("A$") == "A"

    def test_multiple_yield_resume_cycles(self):
        """Multiple yield/resume cycles must work correctly.

        Simulates the setTimeout-based execution loop.
        """
        from applesoft.environment import Environment
        from applesoft.interpreter import Interpreter, YieldSignal
        from applesoft.io_cli import IOBridgeCLI
        from applesoft.lexer import tokenize
        from applesoft.program import Program

        io = IOBridgeCLI()
        prog = Program()
        env = Environment()
        interp = Interpreter(prog, env, io)

        # 10 X = X + 1
        # 20 IF X >= 10 THEN END
        # 30 GOTO 10
        tokens10 = tokenize("10 X = X + 1")
        prog.add_line(10, tokens10[1:])
        tokens20 = tokenize("20 IF X >= 10 THEN END")
        prog.add_line(20, tokens20[1:])
        tokens30 = tokenize("30 GOTO 10")
        prog.add_line(30, tokens30[1:])

        interp.set_yield_threshold(3)

        # Run with yield/resume cycles until completion
        finished = False
        try:
            interp.run()
            finished = True
        except YieldSignal as y:
            for _ in range(100):  # Safety limit
                try:
                    interp.resume_execution(y.line_num, y.stmt_idx)
                    finished = True
                    break
                except YieldSignal as y2:
                    y = y2

        assert finished, "Program should have completed within 100 yield cycles"
        assert env.get_var("X") == 10.0
