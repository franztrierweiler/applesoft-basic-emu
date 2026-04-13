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
        self._console_prompt = document["console-prompt"]
        self._running = False
        self._waiting_for_input = False
        self._input_kind = None
        self._input_resume_line = None
        self._input_resume_idx = None

        # Bind keyboard events for GET support and interrupt
        self._console_input.bind("keydown", self._on_keydown)
        document.bind("keydown", self._on_document_keydown)

    # -- IOBridge protocol methods --

    def print_str(self, text):
        """Write text to the console DOM element.

        Uses textContent via createElement + textContent (SEC-DEV-03, SEC-TECH-12).
        """
        if not text:
            return
        span = document.createElement("span")
        span.textContent = text
        self._console_output.appendChild(span)
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
            self.print_str(prompt)
        return ""

    def get_char(self):
        """Capture the next keyboard event.

        In web mode, GET is handled asynchronously via InputRequestSignal.
        """
        return ""

    def clear_screen(self):
        """Clear the console output."""
        while self._console_output.firstChild:
            self._console_output.removeChild(self._console_output.firstChild)
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

    def render_lores(self, buffer):
        """Render the LoRes 40x48 grid to the canvas."""
        canvas = document["graphics-canvas"]
        ctx = canvas.getContext("2d")
        cell_w = canvas.width / 40
        cell_h = canvas.height / 48
        for y in range(48):
            for x in range(40):
                color_idx = buffer[y][x] if y < len(buffer) and x < len(buffer[y]) else 0
                ctx.fillStyle = self.LORES_COLORS[color_idx % 16]
                ctx.fillRect(x * cell_w, y * cell_h, cell_w, cell_h)

    def render_hires(self, buffer, width=280, height=192):
        """Render the HiRes 280x192 buffer to the canvas."""
        canvas = document["graphics-canvas"]
        ctx = canvas.getContext("2d")
        for y in range(min(height, len(buffer))):
            for x in range(min(width, len(buffer[y]))):
                color_idx = buffer[y][x]
                ctx.fillStyle = self.HIRES_COLORS[color_idx % 8]
                ctx.fillRect(x, y, 1, 1)

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

        if not self._running:
            self._finish_execution()
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

        if inp.kind == "input":
            self._console_input.value = ""
            self._console_input.focus()
        elif inp.kind == "get":
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
        self.print_str("]")

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
                    self.print_str("]")

    def _on_keydown(self, event):
        """Handle keydown events on the console input field."""
        if event.key == "c" and event.ctrlKey:
            event.preventDefault()
            self.set_interrupted()
            if self._waiting_for_input:
                self._waiting_for_input = False
                self.print_str("^C\n")
                self._running = False
                self.print_str("]")
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
            self.print_str(line + "\n")

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

        self.print_str("]")

    # -- STOP button handler --

    def _on_stop_click(self, event):
        """Handle STOP button click (CA-UC-025-05)."""
        self.set_interrupted()
        if self._waiting_for_input:
            self._waiting_for_input = False
            self.print_str("^C\n")
            self._running = False
            self.print_str("]")

    # -- Initialization --

    def _bind_toolbar(self):
        """Bind toolbar buttons to actions."""
        document["btn-stop"].bind("click", self._on_stop_click)

        def on_run(event):
            if hasattr(self, "_repl") and self._repl is not None:
                if self._running:
                    self._running = False
                    self._waiting_for_input = False
                self._run_program_sliced("RUN")

        document["btn-run"].bind("click", on_run)

        def on_reset(event):
            if hasattr(self, "_repl") and self._repl is not None:
                if self._running:
                    self._running = False
                    self._waiting_for_input = False
                self._repl._process_line("NEW")
                self.clear_screen()
                self.print_str("]")

        document["btn-reset"].bind("click", on_reset)

        def on_list(event):
            if hasattr(self, "_repl") and self._repl is not None:
                self._repl._process_line("LIST")
                self.print_str("]")

        document["btn-list"].bind("click", on_list)

        def on_save(event):
            if hasattr(self, "_repl") and self._repl is not None:
                content = self._repl.interpreter.program.detokenize_all()
                self.export_file("program", content)

        document["btn-save"].bind("click", on_save)

        self._setup_file_import()

        def on_load(event):
            self._file_input.click()

        document["btn-load"].bind("click", on_load)

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

        repl.interpreter.set_yield_threshold(1000)
    except Exception as e:
        io.print_str("Error initializing REPL: " + str(e) + "\n")

    io._bind_toolbar()

    loading = document["loading-overlay"]
    loading.classList.add("hidden")

    io.print_str("]")
    io._console_input.focus()


init()
