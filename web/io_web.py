"""IOBridgeWeb — Brython-based IOBridge implementation for the web interface.

All DOM and browser interactions are confined to this module (RG-0014, SEC-TECH-11).
Security: uses textContent exclusively, never inner-HTML (SEC-DEV-03, SEC-TECH-12).
Time-slicing: uses YieldSignal/InputRequestSignal + setTimeout for non-blocking
execution (ADR-003, RG-0015).

Interface: REPL pur (pas d'éditeur séparé), fidèle à l'Apple II original.
"""

# -- Brython imports (confined to this module — CA-UC-025-10) --
from browser import document, html, window, timer  # noqa: F401

# -- Core emulator imports --
# These will work when Brython resolves the Python path to src/applesoft/
# The path must be set up via brython({pythonpath: [...]}) in index.html.


# ---------------------------------------------------------------------------
# IOBridgeWeb — implements the IOBridge protocol for the browser
# ---------------------------------------------------------------------------
class IOBridgeWeb:
    """IOBridge implementation that renders to the browser DOM.

    Follows the IOBridge protocol defined in src/applesoft/io_bridge.py.
    Implements time-slicing runner for non-blocking program execution (RG-0015).
    REPL-only interface — no separate editor panel.
    """

    def __init__(self):
        self._interrupted = False
        self._cursor_column = 1
        self._video_mode = "normal"
        self._speed = 0
        self._last_key = 0
        self._console_output = document["console-output"]
        self._console_input = document["console-input"]
        self._console_input_display = document["console-input-display"]
        self._console_cursor = document["console-cursor"]
        # Snapshots of the last rendered canvas state — for delta rendering.
        # 0xFF is a sentinel (no valid color) that forces a full repaint on
        # the first render after a mode change (cf. _invalidate_canvas_cache).
        self._lores_snapshot = bytearray(b"\xff" * (40 * 48))
        self._hires_snapshot = bytearray(b"\xff" * (280 * 192))
        self._running = False
        self._waiting_for_input = False
        self._input_kind = None
        self._input_resume_line = None
        self._input_resume_idx = None

        # Bind keyboard events for GET support and interrupt
        self._console_input.bind("keydown", self._on_keydown)
        self._console_input.bind("input", self._on_input_change)
        document.bind("keydown", self._on_document_keydown)
        # Click anywhere on the console refocuses the hidden input
        document["console-section"].bind("click", lambda e: self._console_input.focus())

    # -- Prompt + cursor management (Apple II look) --

    def _show_prompt(self, text):
        """Print the prompt inline in the output flow and reveal the cursor.

        On Apple II, prompts (REPL `]`, `INPUT "?…"`, etc.) appear at the
        current cursor position in the same screen — not on a separate row.
        """
        if text:
            self.print_str(text)
        self._console_cursor.classList.remove("cursor-hidden")
        self._console_input.focus()

    def _hide_prompt(self):
        """Hide the cursor (program running, no input expected)."""
        self._console_input_display.textContent = ""
        self._console_cursor.classList.add("cursor-hidden")

    def _on_input_change(self, event):
        """Mirror the captured input value into the visible display span."""
        self._console_input_display.textContent = self._console_input.value
        self._console_output.scrollTop = self._console_output.scrollHeight

    # -- IOBridge protocol methods --

    def print_str(self, text):
        """Write text to the output flow, just before the live input span.

        Keeps the input-display + cursor pinned at the visual end of the
        screen. Uses textContent only (SEC-DEV-03, SEC-TECH-12).
        """
        if not text:
            return
        span = document.createElement("span")
        span.textContent = text
        self._console_output.insertBefore(span, self._console_input_display)
        self._console_output.scrollTop = self._console_output.scrollHeight

        if "\n" in text:
            last_line = text.rsplit("\n", 1)[-1]
            self._cursor_column = len(last_line) + 1
        else:
            self._cursor_column += len(text)

    def input_str(self, prompt=""):
        """Display prompt and read a line of text from the user.

        In web mode, INPUT is handled asynchronously via InputRequestSignal.
        """
        if prompt:
            self._show_prompt(prompt)
        return ""

    def get_char(self):
        """Capture the next keyboard event.

        In web mode, GET is handled asynchronously via InputRequestSignal.
        """
        return ""

    def clear_screen(self):
        """Clear the console output, preserving the live input span + cursor."""
        # Detach display + cursor, wipe everything, re-attach at the end.
        while self._console_output.firstChild:
            self._console_output.removeChild(self._console_output.firstChild)
        self._console_input_display.textContent = ""
        self._console_input.value = ""
        self._console_output.appendChild(self._console_input_display)
        self._console_output.appendChild(self._console_cursor)
        self._cursor_column = 1

    def check_interrupt(self):
        """Check if an interrupt has been requested (STOP button or Ctrl+C)."""
        if self._interrupted:
            self._interrupted = False
            return True
        return False

    def set_interrupted(self):
        """Signal an interrupt (called by STOP button or Ctrl+C handler)."""
        self._interrupted = True

    def get_cursor_column(self):
        """Return the current cursor column (1-based)."""
        return self._cursor_column

    def set_video_mode(self, mode):
        """Set video mode: normal, inverse, flash."""
        self._video_mode = mode

    def set_speed(self, value):
        """Set character delay (0-255). Ignored in web for now."""
        self._speed = value

    def get_last_key(self):
        """Return the last key pressed (RG-0011, $C000)."""
        return self._last_key

    def set_last_key(self, key):
        """Set the last key pressed."""
        self._last_key = key

    def move_cursor_to_row(self, row):
        """Move cursor to row (no-op in web)."""
        pass

    # -- Column mode switching (CA-UC-025-07, CA-UC-025-08) --

    def set_column_mode(self, columns):
        """Switch between 40 and 80 column display modes."""
        if columns == 80:
            self._console_output.classList.add("mode-80")
        else:
            self._console_output.classList.remove("mode-80")

    # -- Persistence: localStorage + file I/O (CA-UC-028-01 to CA-UC-028-06) --

    MAX_IMPORT_SIZE = 1_000_000
    ALLOWED_EXTENSIONS = (".bas", ".txt")

    def save_to_localStorage(self, name, program_text):
        """Save a program to localStorage (CA-UC-028-01)."""
        key = "applesoft:" + name
        try:
            storage = window.localStorage
            import json
            data = json.dumps({
                "name": name,
                "code": program_text,
                "date": str(window.Date.new().toISOString()),
            })
            storage.setItem(key, data)
        except Exception:
            self.print_str("?OUT OF MEMORY ERROR\n")

    def load_from_localStorage(self, name):
        """Load a program from localStorage (CA-UC-028-02)."""
        key = "applesoft:" + name
        try:
            storage = window.localStorage
            raw = storage.getItem(key)
            if raw is None:
                return None
            import json
            data = json.loads(raw)
            return data.get("code", "")
        except Exception:
            self.print_str("?STORAGE ERROR\n")
            return None

    def list_saved_programs(self):
        """List all saved programs in localStorage (CA-UC-028-03)."""
        programs = []
        try:
            storage = window.localStorage
            import json
            for i in range(storage.length):
                key = storage.key(i)
                if key.startswith("applesoft:"):
                    name = key[len("applesoft:"):]
                    raw = storage.getItem(key)
                    data = json.loads(raw)
                    programs.append((name, data.get("date", "")))
        except Exception:
            pass
        return programs

    def export_file(self, filename, content):
        """Export a program as a downloadable .bas file (CA-UC-028-05)."""
        if not filename.endswith(".bas"):
            filename += ".bas"
        blob = window.Blob.new([content], {"type": "text/plain"})
        url = window.URL.createObjectURL(blob)
        a = document.createElement("a")
        a.href = url
        a.download = filename
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)

    def _validate_import_file(self, file):
        """Validate an imported file (SEC-BP-40, SEC-BP-41)."""
        name = file.name.lower()
        valid_ext = any(name.endswith(ext) for ext in self.ALLOWED_EXTENSIONS)
        if not valid_ext:
            self.print_str("?FILE TYPE ERROR — only .bas and .txt files accepted\n")
            return False
        if file.size > self.MAX_IMPORT_SIZE:
            self.print_str("?FILE TOO LARGE ERROR — max 1 Mo\n")
            return False
        return True

    def _import_file_content(self, content):
        """Load imported file content into program memory."""
        if hasattr(self, "_repl") and self._repl is not None:
            self._repl._process_line("NEW")
            for line in content.strip().splitlines():
                line = line.strip()
                if line:
                    self._repl._process_line(line)
            self._show_prompt("]")

    def _setup_file_import(self):
        """Set up file import via hidden <input type=file> (CA-UC-028-04)."""
        file_input = document.createElement("input")
        file_input.type = "file"
        file_input.accept = ".bas,.txt"
        file_input.style.display = "none"
        document.body.appendChild(file_input)
        self._file_input = file_input

        def on_file_selected(event):
            files = file_input.files
            if files.length == 0:
                return
            f = files[0]
            if not self._validate_import_file(f):
                return
            reader = window.FileReader.new()
            reader.onload = lambda e: self._import_file_content(e.target.result)
            reader.readAsText(f)

        file_input.bind("change", on_file_selected)

    def _setup_drag_drop(self):
        """Set up drag & drop .bas import on the console (CA-UC-028-06)."""
        def on_dragover(event):
            event.preventDefault()
            event.dataTransfer.dropEffect = "copy"

        def on_drop(event):
            event.preventDefault()
            files = event.dataTransfer.files
            if files.length == 0:
                return
            f = files[0]
            if not self._validate_import_file(f):
                return
            reader = window.FileReader.new()
            reader.onload = lambda e: self._import_file_content(e.target.result)
            reader.readAsText(f)

        self._console_output.bind("dragover", on_dragover)
        self._console_output.bind("drop", on_drop)

    # -- Canvas graphics (CA-UC-027-01 to CA-UC-027-04) --

    LORES_COLORS = [
        "#000000", "#DD0033", "#000099", "#DD22DD",
        "#007700", "#555555", "#2222FF", "#6699FF",
        "#885500", "#FF6600", "#AAAAAA", "#FF9988",
        "#11DD00", "#FFFF00", "#44FF99", "#FFFFFF",
    ]

    HIRES_COLORS = [
        "#000000", "#11DD00", "#FF6600", "#FFFFFF",
        "#000000", "#2222FF", "#FF44DD", "#FFFFFF",
    ]

    def _show_canvas(self, width, height):
        """Show the graphics canvas and set its logical size."""
        canvas_section = document["canvas-section"]
        canvas_section.style.display = "flex"
        canvas = document["graphics-canvas"]
        canvas.width = width
        canvas.height = height

    def _hide_canvas(self):
        """Hide the graphics canvas (called on TEXT command)."""
        document["canvas-section"].style.display = "none"

    def _invalidate_canvas_cache(self):
        """Force a full repaint on next render_*_delta call (mode change)."""
        for i in range(len(self._lores_snapshot)):
            self._lores_snapshot[i] = 0xFF
        for i in range(len(self._hires_snapshot)):
            self._hires_snapshot[i] = 0xFF

    def render_lores(self, buffer):
        """Render the LoRes 40x48 grid to the canvas — delta only.

        Accepts a flat bytearray of length 40*48 (as exposed by GraphicsEngine).
        Only redraws cells whose color differs from the previous snapshot.
        """
        canvas = document["graphics-canvas"]
        ctx = canvas.getContext("2d")
        cell_w = canvas.width / 40
        cell_h = canvas.height / 48
        snap = self._lores_snapshot
        for i in range(40 * 48):
            cur = buffer[i]
            if cur != snap[i]:
                y = i // 40
                x = i - y * 40
                ctx.fillStyle = self.LORES_COLORS[cur & 0x0F]
                ctx.fillRect(x * cell_w, y * cell_h, cell_w, cell_h)
                snap[i] = cur

    def render_hires(self, buffer, width=280, height=192):
        """Render the HiRes 280x192 buffer to the canvas — delta only.

        Accepts a flat bytearray of length width*height.
        """
        canvas = document["graphics-canvas"]
        ctx = canvas.getContext("2d")
        snap = self._hires_snapshot
        n = width * height
        for i in range(n):
            cur = buffer[i]
            if cur != snap[i]:
                y = i // width
                x = i - y * width
                ctx.fillStyle = self.HIRES_COLORS[cur & 0x07]
                ctx.fillRect(x, y, 1, 1)
                snap[i] = cur

    # -- Time-slicing runner (ADR-003, RG-0015) --

    def _run_program_sliced(self, command):
        """Run a BASIC command with time-slicing."""
        from applesoft.interpreter import YieldSignal, InputRequestSignal
        from applesoft.errors import BasicError

        self._running = True
        self._waiting_for_input = False

        try:
            self._repl._process_line(command)
        except YieldSignal as y:
            timer.set_timeout(lambda: self._resume_slice(y.line_num, y.stmt_idx), 0)
            return
        except InputRequestSignal as inp:
            self._wait_for_async_input(inp)
            return
        except BasicError as e:
            self.print_str(e.format() + "\n")
        except Exception as e:
            self.print_str("?ERROR: " + str(e) + "\n")

        self._finish_execution()

    def _resume_slice(self, line_num, stmt_idx):
        """Resume execution from a yield point (time-slicing)."""
        from applesoft.interpreter import YieldSignal, InputRequestSignal
        from applesoft.errors import BasicError

        # Aborted by RESET (or similar) — caller already cleaned up + showed
        # the prompt. Silent return avoids printing a duplicate `]`.
        if not self._running:
            return

        try:
            self._repl.interpreter.resume_execution(line_num, stmt_idx)
        except YieldSignal as y:
            timer.set_timeout(lambda: self._resume_slice(y.line_num, y.stmt_idx), 0)
            return
        except InputRequestSignal as inp:
            self._wait_for_async_input(inp)
            return
        except BasicError as e:
            self.print_str(e.format() + "\n")
        except Exception as e:
            self.print_str("?ERROR: " + str(e) + "\n")

        self._finish_execution()

    def _wait_for_async_input(self, inp):
        """Enter async input wait state (INPUT or GET)."""
        self._waiting_for_input = True
        self._input_kind = inp.kind
        self._input_resume_line = inp.line_num
        self._input_resume_idx = inp.stmt_idx

        self._console_cursor.classList.remove("cursor-hidden")
        if inp.kind == "input":
            self._console_input.value = ""
            self._console_input_display.textContent = ""
        self._console_input.focus()

    def _receive_input_value(self, value):
        """Process received input value and resume execution."""
        from applesoft.interpreter import YieldSignal, InputRequestSignal
        from applesoft.errors import BasicError

        self._waiting_for_input = False
        line_num = self._input_resume_line
        stmt_idx = self._input_resume_idx

        try:
            self._repl.interpreter.resume_after_input(line_num, stmt_idx, value)
        except YieldSignal as y:
            timer.set_timeout(lambda: self._resume_slice(y.line_num, y.stmt_idx), 0)
            return
        except InputRequestSignal as inp:
            self._wait_for_async_input(inp)
            return
        except BasicError as e:
            self.print_str(e.format() + "\n")
        except Exception as e:
            self.print_str("?ERROR: " + str(e) + "\n")

        self._finish_execution()

    def _finish_execution(self):
        """Clean up after program execution ends."""
        self._running = False
        self._waiting_for_input = False
        self._show_prompt("]")

    # -- Event handlers --

    def _on_document_keydown(self, event):
        """Handle keydown on the whole document (for Ctrl+C during execution)."""
        if event.key == "c" and event.ctrlKey:
            event.preventDefault()
            if self._running:
                self.set_interrupted()
                if self._waiting_for_input:
                    self._waiting_for_input = False
                    self.print_str("^C\n")
                    self._running = False
                    self._show_prompt("]")

    def _on_keydown(self, event):
        """Handle keydown events on the console input field."""
        if event.key == "c" and event.ctrlKey:
            event.preventDefault()
            self.set_interrupted()
            if self._waiting_for_input:
                self._waiting_for_input = False
                self.print_str("^C\n")
                self._running = False
                self._show_prompt("]")
            return

        if len(event.key) == 1:
            self._last_key = ord(event.key.upper()) | 0x80

        if self._waiting_for_input and self._input_kind == "get":
            if len(event.key) == 1:
                event.preventDefault()
                ch = event.key.upper()
                self.print_str(ch)
                self._receive_input_value(ch)
                return

        if event.key == "Enter":
            event.preventDefault()
            line = self._console_input.value
            self._console_input.value = ""
            self._console_input_display.textContent = ""
            # The prompt is already part of the output flow — only commit the
            # typed text + newline. Cursor follows naturally on the next line.
            self.print_str(line + "\n")
            self._hide_prompt()

            if self._waiting_for_input and self._input_kind == "input":
                self._receive_input_value(line)
                return

            if hasattr(self, "_repl") and self._repl is not None:
                self._process_repl_line(line)

    def _process_repl_line(self, line):
        """Feed a line to the REPL for processing."""
        upper = line.strip().upper()

        if upper.startswith("RUN") or upper.startswith("GOTO") or upper.startswith("GOSUB"):
            self._run_program_sliced(line)
            return

        try:
            self._repl._process_line(line)
        except Exception as e:
            self.print_str("?ERROR: " + str(e) + "\n")

        self._show_prompt("]")

    # -- STOP button handler --

    def _on_stop_click(self, event):
        """Handle STOP button click — same effect as Ctrl+C (CA-UC-025-05)."""
        self.set_interrupted()
        if self._waiting_for_input:
            self._waiting_for_input = False
            self.print_str("^C\n")
            self._running = False
            self._show_prompt("]")

    def _on_reset_click(self, event):
        """RESET button — full reboot, like Apple ][ power-cycle.

        Aborts any running program, clears program + variables (`NEW`),
        exits graphics mode, blanks the screen, and prints the iconic
        boot banner.
        """
        if not hasattr(self, "_repl") or self._repl is None:
            return
        # Cut any in-flight slice — _resume_slice will see _running=False
        # and bail silently, so we own the prompt redraw below.
        self.set_interrupted()
        self._running = False
        self._waiting_for_input = False
        try:
            self._repl._process_line("NEW")
        except Exception:
            pass
        if hasattr(self._repl, "graphics"):
            self._repl.graphics.text()
        self._hide_canvas()
        self._invalidate_canvas_cache()
        self.clear_screen()
        self._console_input.value = ""
        # Cosmetic boot banner — homage to the original power-on sequence.
        self.print_str("APPLE ][\n\n")
        self._show_prompt("]")

    # -- Initialization --

    def _bind_toolbar(self):
        """Bind LOAD / STOP / RESET toolbar buttons. Other commands
        (RUN, LIST, SAVE, NEW…) are typed at the prompt, Apple II-style."""
        self._setup_file_import()

        def on_load(event):
            self._file_input.click()

        document["btn-load"].bind("click", on_load)
        document["btn-stop"].bind("click", self._on_stop_click)
        document["btn-reset"].bind("click", self._on_reset_click)

        self._setup_drag_drop()


# ---------------------------------------------------------------------------
# Initialization — called when Brython finishes loading
# ---------------------------------------------------------------------------
def init():
    """Initialize the web emulator.

    Creates the IOBridgeWeb, sets up the REPL, and displays the prompt.
    """
    io = IOBridgeWeb()

    try:
        from applesoft.repl import REPL
        from applesoft.debug import DebugTracer

        debug = DebugTracer()
        repl = REPL(io=io, debug=debug)
        io._repl = repl

        # Shorter slices = more frequent browser repaints between tranches.
        # 200 instructions ≈ 200-1000 ms in Brython on tight PLOT loops.
        repl.interpreter.set_yield_threshold(200)

        # Wire the graphics engine to the canvas — overrides the ANSI/stdout
        # renderer installed by REPL._setup_graphics_render (used by the CLI).
        # Strategy: while a BASIC slice runs synchronously the browser cannot
        # repaint, so calling fillRect inside on_draw is wasted CPU. Instead
        # we just mark the canvas dirty and schedule ONE render via
        # requestAnimationFrame; it fires between slices, right before the
        # browser paints. Result: at most one canvas render per displayed frame.
        gfx_state = {"dirty": False, "scheduled": False, "last_mode": None}

        def _do_render(_ts):
            gfx_state["scheduled"] = False
            if not gfx_state["dirty"]:
                return
            gfx_state["dirty"] = False
            gfx = repl.graphics
            mode = gfx.mode
            if mode != gfx_state["last_mode"]:
                io._invalidate_canvas_cache()
                gfx_state["last_mode"] = mode
            if mode == "lores":
                io._show_canvas(280, 192)
                io.render_lores(gfx.lores_buffer)
            elif mode == "hires":
                io._show_canvas(280, 192)
                io.render_hires(gfx.hires_buffer)
            elif mode == "text":
                io._hide_canvas()

        def _web_on_draw():
            gfx_state["dirty"] = True
            if not gfx_state["scheduled"]:
                gfx_state["scheduled"] = True
                window.requestAnimationFrame(_do_render)

        repl.graphics.set_on_draw(_web_on_draw)
    except Exception as e:
        io.print_str("Error initializing REPL: " + str(e) + "\n")

    io._bind_toolbar()

    loading = document["loading-overlay"]
    loading.classList.add("hidden")

    io._show_prompt("]")


init()
